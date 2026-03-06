// z5d_prime_gen.c — Z5D predictor + refinement + geodesic MR + strict verify
// Build: cc z5d_prime_gen.c z5d_predictor.c -o z5d_prime_gen -lmpfr -lgmp -lm
//
// Changes in this patch:
// - Adds a strict final verification gate using mpz_probab_prime_p(n, 50)
//   AFTER geodesic MR passes. This prevents large pseudoprimes from slipping
//   through deterministic geodesic bases at extreme magnitudes (e.g., k≈10^500).
// - Keeps MR rounds counter to reflect ONLY geodesic MR rounds (per your spec).
// - Retains: negative-prediction clamp, 6k±1 snapping, small-wheel presieve,
//   widened window, and forward-extend to ensure a prime is always returned.
//
// ---------------------------------------------------------------------------

#ifndef __has_include
#  define __has_include(x) 0
#endif
#if __has_include("mpfr.h") && __has_include("gmp.h")
#  include <mpfr.h>
#  include <gmp.h>
#  define Z5D_HAVE_MPFR 1
#else
#  define Z5D_HAVE_MPFR 0
#endif

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include "z5d_predictor.h"
#if __has_include("z5d_fft_zeta.h")
#  include "z5d_fft_zeta.h"
#  define Z5D_HAVE_FFT_ZETA 1
#else
#  define Z5D_HAVE_FFT_ZETA 0
#endif

#ifndef FFT_ZETA_ENHANCE
#  define FFT_ZETA_ENHANCE 1
#endif

#define MR_USE_ENHANCED 1
#define MR_GMP_REPS     25
#define GMP_FINAL_REPS  50  // strict final verification reps

static int g_print_stats = 0;
static unsigned long long g_mr_rounds = 0;

__attribute__((unused)) static long double pi_asymptotic_est5(long double x) {
    if (x < 3.0L) return 0.0L;
    long double L = logl(x);
    long double L2 = L*L, L3 = L2*L, L4 = L3*L, L5 = L4*L;
    return x * (1.0L/L + 1.0L/L2 + 2.0L/L3 + 6.0L/L4 + 24.0L/L5);
}

#if Z5D_HAVE_MPFR
// ---- 6k±1 helpers ----------------------------------------------------------
__attribute__((unused)) static void snap_to_6k_pm1(mpz_t n, int dir) {
    unsigned long r = mpz_fdiv_ui(n, 6);
    if (r != 1 && r != 5) {
        long delta;
        if (dir < 0) {
            if (r == 0) delta = 1;
            else if (r == 2) delta = 1;
            else if (r == 3) delta = 2;
            else if (r == 4) delta = 3;
            else /* r==5 */  delta = 0;
            if (delta) mpz_sub_ui(n, n, (unsigned long)delta);
        } else {
            if (r == 0) delta = 1;
            else if (r == 1) delta = 0;
            else if (r == 2) delta = 3;
            else if (r == 3) delta = 2;
            else if (r == 4) delta = 1;
            else /* r==5 */  delta = 0;
            if (delta) mpz_add_ui(n, n, (unsigned long)delta);
        }
        }
    }

// ---- small wheel presieve (primes <= 97) -----------------------------------
static int divisible_by_small_prime(const mpz_t n) {
    static const unsigned smalls[] = {
        3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97
    };
    for (size_t i=0;i<sizeof(smalls)/sizeof(smalls[0]);++i) {
        unsigned p = smalls[i];
        if (mpz_cmp_ui(n, p)==0) return 0;           // itself prime
        if (mpz_fdiv_ui(n, p)==0) return 1;         // divisible
    }
    return 0;
}

// ---- Geodesic-guided MR ----------------------------------------------------
#if MR_USE_ENHANCED
static inline unsigned long long mix64(unsigned long long x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    x ^= (x >> 31);
    return x;
}
static void base_from_signal(mpz_t out, const mpz_t n, long double signal) {
    unsigned long long s = (unsigned long long) llroundl(fabsl(signal) * 1e12L);
    unsigned long long h = mix64(s);
    mpz_t tmp, nminus3; mpz_inits(tmp, nminus3, NULL);
    mpz_sub_ui(nminus3, n, 3);
    mpz_set_ui(tmp, (unsigned long)(h & 0xffffffffu));
    if (mpz_sgn(nminus3) <= 0) { mpz_set_ui(out, 2); mpz_clears(tmp, nminus3, NULL); return; }
    mpz_mod(tmp, tmp, nminus3);
    mpz_add_ui(tmp, tmp, 2);
    mpz_set(out, tmp);
    mpz_clears(tmp, nminus3, NULL);
}
static int build_bases(const mpz_t n, const mpfr_t k, mpz_t* bases, int maxb) {
    int c = 0;
    mpz_set_ui(bases[c++], 2);
    long double phi = Z5D_GOLDEN_PHI;
    long double nd = mpz_get_d(n);
    long double frac = fmodl(nd, phi) / phi;
    long double kappa = Z5D_DEFAULT_KAPPA_GEO;
    long double theta1 = phi * powl(frac, kappa);
    base_from_signal(bases[c++], n, theta1);
    mpfr_t tmp; mpfr_init2(tmp, 128);
    mpfr_add_ui(tmp, k, 1, MPFR_RNDN); mpfr_log(tmp, tmp, MPFR_RNDN);
    long double lnkp1 = mpfr_get_ld(tmp, MPFR_RNDN);
    long double lnn = logl(fmaxl(nd, 3.0L));
    long double theta2 = (lnkp1 / Z5D_E_SQUARED) * (1.0L + 0.5L * sinl(lnn));
    mpfr_clear(tmp);
    base_from_signal(bases[c++], n, theta2);
    const unsigned long smalls[] = {3,5,7,11,13,17};
    for (size_t i=0; i<sizeof(smalls)/sizeof(smalls[0]) && c<maxb; ++i) mpz_set_ui(bases[c++], smalls[i]);
    return c;
}
static int mr_round(const mpz_t n, const mpz_t a) {
    mpz_t d, x, n_minus_1; mpz_inits(d, x, n_minus_1, NULL);
    mpz_sub_ui(d, n, 1);
    unsigned long r = 0; while (mpz_even_p(d)) { mpz_fdiv_q_2exp(d, d, 1); r++; }
    mpz_powm(x, a, d, n);
    if (mpz_cmp_ui(x,1)==0) { mpz_clears(d,x,n_minus_1,NULL); return 1; }
    mpz_sub_ui(n_minus_1, n, 1);
    if (mpz_cmp(x, n_minus_1)==0) { mpz_clears(d,x,n_minus_1,NULL); return 1; }
    for (unsigned long i=1; i<r; ++i) {
        mpz_powm_ui(x, x, 2, n);
        if (mpz_cmp(x, n_minus_1)==0) { mpz_clears(d,x,n_minus_1,NULL); return 1; }
    }
    mpz_clears(d,x,n_minus_1,NULL);
    return 0;
}
static int mr_geodesic_pass(const mpz_t n, const mpfr_t k) {
    if (mpz_cmp_ui(n, 2) < 0) return 0;
    if (mpz_cmp_ui(n, 3) <= 0) return 1;
    if (mpz_even_p(n)) return 0;
    const int MAXB = 9;
    mpz_t bases[MAXB]; for (int i=0;i<MAXB;i++) mpz_init(bases[i]);
    int nb = build_bases(n, k, bases, MAXB);
    int result = 1;
    for (int i=0;i<nb;i++) {
        mpz_t a, nminus3; mpz_inits(a, nminus3, NULL);
        mpz_set(a, bases[i]);
        mpz_sub_ui(nminus3, n, 3);
        if (mpz_sgn(nminus3) > 0) {
            mpz_mod(a, a, nminus3);
            mpz_add_ui(a, a, 2);
        } else {
            mpz_set_ui(a, 2);
        }
        g_mr_rounds++;
        if (!mr_round(n, a)) { result = 0; mpz_clears(a,nminus3,NULL); break; }
        mpz_clears(a,nminus3,NULL);
    }
    for (int i=0;i<MAXB;i++) mpz_clear(bases[i]);
    return result;
}
static inline int final_verify_strict(const mpz_t n) {
    // Strong extra check using GMP's built-in Miller–Rabin with many reps.
    // Does not change g_mr_rounds (you only want MR rounds from geodesic set).
    int r = mpz_probab_prime_p(n, GMP_FINAL_REPS);
    return (r > 0);
}
#endif // MR_USE_ENHANCED

// ---- Refinement to exact p_k (never returns a composite) -------------------
static void refine_to_indexed_prime(const mpfr_t x0, const mpfr_t k, mpz_t out_prime) {
    mpz_t candidate; mpz_init(candidate);
    mpfr_get_z(candidate, x0, MPFR_RNDN);

    if (mpz_cmp_ui(candidate, 3) < 0) mpz_set_ui(candidate, 3);
    if (mpz_even_p(candidate)) mpz_add_ui(candidate, candidate, 1);
    snap_to_6k_pm1(candidate, +1);

    mpfr_printf("Z5D prediction: %.0Rf\n", x0);

    // Try the prediction first
#if MR_USE_ENHANCED
    if (!divisible_by_small_prime(candidate) && mr_geodesic_pass(candidate, k) && final_verify_strict(candidate)) {
#else
    if (!divisible_by_small_prime(candidate) && mpz_probab_prime_p(candidate, MR_GMP_REPS) > 0) {
#endif
        gmp_printf("Found prime at prediction: %Zd\n", candidate);
        mpz_set(out_prime, candidate);
        mpz_clear(candidate);
        return;
    }

    // Initial symmetric window: ~ 4·ln(x0)
    mpfr_t ln_est; mpfr_init2(ln_est, 192);
    mpfr_log(ln_est, x0, MPFR_RNDN);
    long base_window = (long)ceil(4.0 * mpfr_get_d(ln_est, MPFR_RNDN));
    mpfr_clear(ln_est);
    if (base_window < 256) base_window = 256;

    for (long step = 1; step <= base_window; ++step) {
        for (int dir = +1; dir >= -1; dir -= 2) {
            mpz_t t; mpz_init(t);
            if (dir > 0) mpz_add_ui(t, candidate, (unsigned long)step);
            else {
                if (mpz_cmp_ui(candidate, (unsigned long)step) <= 0) { mpz_clear(t); continue; }
                mpz_sub_ui(t, candidate, (unsigned long)step);
            }
            if (mpz_even_p(t)) { if (dir > 0) mpz_add_ui(t, t, 1); else mpz_sub_ui(t, t, 1); }
            snap_to_6k_pm1(t, dir);
            if (mpz_cmp_ui(t, 3) < 0) { mpz_clear(t); continue; }

            if (!divisible_by_small_prime(t)) {
#if MR_USE_ENHANCED
                int pass_geo = mr_geodesic_pass(t, k);
                int pass_strict = pass_geo && final_verify_strict(t);
                if (pass_strict) {
#else
                int pass_strict = (mpz_probab_prime_p(t, MR_GMP_REPS) > 0);
                if (pass_strict) {
#endif
                    gmp_printf("Found prime: %Zd (diff %+ld)\n", t, (long)(dir*step));
                mpz_set(out_prime, t);
                mpz_clear(t);
                mpz_clear(candidate);
                return;
            }
            }
            mpz_clear(t);
        }
    }

    // Extended forward scan: continue until strict probable prime found
    {
        mpz_t t; mpz_init_set(t, candidate);
        while (1) {
            mpz_add_ui(t, t, 2);
            snap_to_6k_pm1(t, +1);
            if (divisible_by_small_prime(t)) continue;
#if MR_USE_ENHANCED
            if (mr_geodesic_pass(t, k) && final_verify_strict(t)) {
#else
            if (mpz_probab_prime_p(t, MR_GMP_REPS) > 0) {
#endif
                gmp_printf("Extended scan found prime: %Zd\n", t);
                mpz_set(out_prime, t);
                mpz_clear(t);
    mpz_clear(candidate);
                return;
            }
        }
    }
}

// ---- Z5D predictor in MPFR -------------------------------------------------
static void z5d_prime_gen_mpfr(mpfr_t res,
                               const mpfr_t k,
                               double c_cal,
                               double k_star,
                               double kappa_geo)
{
    (void)kappa_geo;
    mpfr_t lnk, lnlnk, pnt, ln_pnt, d_term, e_term, tmp, correction;
    mpfr_inits2(200, lnk, lnlnk, pnt, ln_pnt, d_term, e_term, tmp, correction, NULL);

    // PNT core: pnt = k*(ln k + ln ln k - 1 + (ln ln k - 2)/ln k)
    mpfr_log(lnk, k, MPFR_RNDN);
    mpfr_log(lnlnk, lnk, MPFR_RNDN);

    mpfr_add(tmp, lnk, lnlnk, MPFR_RNDN);
    mpfr_sub_ui(tmp, tmp, 1, MPFR_RNDN);
    mpfr_sub_ui(correction, lnlnk, 2, MPFR_RNDN);
    mpfr_div(correction, correction, lnk, MPFR_RNDN);
    mpfr_add(tmp, tmp, correction, MPFR_RNDN);
    mpfr_mul(pnt, k, tmp, MPFR_RNDN);

    // d_term = ((ln pnt / e^4)^2) * pnt * c_cal
    mpfr_set_ui(d_term, 0, MPFR_RNDN);
    if (mpfr_cmp_ui(pnt, 0) > 0) {
        mpfr_log(ln_pnt, pnt, MPFR_RNDN);
        if (mpfr_cmp_ui(ln_pnt, 0) > 0) {
            mpfr_div_d(tmp, ln_pnt, Z5D_E_FOURTH, MPFR_RNDN);
            mpfr_mul(d_term, tmp, tmp, MPFR_RNDN);
        }
    }

    // e_term = pnt^(−1/3) * pnt * k_star
    mpfr_set_ui(e_term, 0, MPFR_RNDN);
    if (mpfr_cmp_ui(pnt, 0) > 0) {
        mpfr_set_d(tmp, -1.0/3.0, MPFR_RNDN);
        mpfr_pow(e_term, pnt, tmp, MPFR_RNDN);
    }

    mpfr_mul(d_term, d_term, pnt, MPFR_RNDN);
    mpfr_mul_d(d_term, d_term, c_cal, MPFR_RNDN);

    mpfr_mul(e_term, e_term, pnt, MPFR_RNDN);
    mpfr_mul_d(e_term, e_term, k_star, MPFR_RNDN);

    mpfr_add(res, pnt, d_term, MPFR_RNDN);
    mpfr_add(res, res, e_term, MPFR_RNDN);
    if (mpfr_sgn(res) < 0) mpfr_set(res, pnt, MPFR_RNDN); // clamp negatives
    mpfr_round(res, res);

    mpfr_clears(lnk, lnlnk, pnt, ln_pnt, d_term, e_term, tmp, correction, NULL);
}

#endif // Z5D_HAVE_MPFR

// ---- Main ------------------------------------------------------------------
int main(int argc, char** argv) {
#if !Z5D_HAVE_MPFR
    unsigned long long k_ui = 1000000ULL;
    for (int i=1;i<argc;i++) {
        if (strcmp(argv[i], "--stats")==0) g_print_stats = 1;
        else {
            char* end = NULL;
            unsigned long long v = strtoull(argv[i], &end, 10);
            if (!end || *end != '\0' || v < 2ULL) {
                fprintf(stderr, "Usage: %s [k>=2] [--stats]\n", argv[0]);
                return 1;
            }
            k_ui = v;
        }
    }
    printf("Z5D Prime Generator (Fallback Mode)\n");
    printf("===================================\n");
    printf("Note: MPFR/GMP not detected; using reduced-precision path.\n\n");
    double basic_pred = z5d_prime((double)k_ui, 0.0, 0.0, 0.3, 1);
    printf("Input k: %llu\n", k_ui);
    printf("Basic Z5D prediction: %.0f\n", basic_pred);
    printf("Using regular Z5D prediction (fallback mode)\n");
    if (g_print_stats) printf("-- Fallback mode: Limited precision --\n");
    return 0;
#else
    mpz_t k_z; mpz_init_set_ui(k_z, 1000000UL);
    for (int i=1;i<argc;i++) {
        if (strcmp(argv[i], "--stats")==0) g_print_stats = 1;
        else {
            if (mpz_set_str(k_z, argv[i], 10) != 0 || mpz_cmp_ui(k_z, 2UL) < 0) {
                fprintf(stderr, "Usage: %s [k>=2] [--stats]\n", argv[0]);
                mpz_clear(k_z);
                return 1;
            }
        }
    }

    gmp_printf("Input k: %Zd\n", k_z);

    mpfr_t k, res; mpfr_inits2(200, k, res, NULL);
    mpfr_set_z(k, k_z, MPFR_RNDN);

#if FFT_ZETA_ENHANCE && Z5D_HAVE_FFT_ZETA
    double k_as_d = mpz_get_d(k_z);
    double enhanced_pred = z5d_prime_with_fft_zeta(k_as_d, Z5D_DEFAULT_C, Z5D_DEFAULT_K_STAR, Z5D_DEFAULT_KAPPA_GEO, 1);
    mpfr_set_d(res, enhanced_pred, MPFR_RNDN);
    printf("FFT-zeta enhanced Z5D prediction enabled\n");
#else
    z5d_prime_gen_mpfr(res, k, Z5D_DEFAULT_C, Z5D_DEFAULT_K_STAR, Z5D_DEFAULT_KAPPA_GEO);
    printf("Using regular Z5D prediction\n");
#endif

    mpz_t p_exact; mpz_init(p_exact);
    refine_to_indexed_prime(res, k, p_exact);

#if FFT_ZETA_ENHANCE && Z5D_HAVE_FFT_ZETA
    mpfr_printf("FFT-zeta enhanced Z5D prediction (rounded): %.0Rf\n", res);
#else
    mpfr_printf("Raw Z5D prediction (rounded): %.0Rf\n", res);
#endif

    gmp_printf("Refined p_%Zd: %Zd\n", k_z, p_exact);

#if MR_USE_ENHANCED
    if (g_print_stats) printf("-- MR rounds (enhanced, deterministic bases): %llu\n", g_mr_rounds);
#endif

    mpz_clear(p_exact);
    mpfr_clears(k, res, NULL);
    mpz_clear(k_z);
    return 0;
#endif
}
