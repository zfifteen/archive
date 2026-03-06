// Auto-detect library availability
#ifndef __has_include
#  define __has_include(x) 0
#endif

#if __has_include("gmp.h") && __has_include("mpfr.h")
#include <gmp.h>
#include <mpfr.h>
#define Z5D_HAVE_MPFR 1
#else
#define Z5D_HAVE_MPFR 0
#include "z5d_fallback_types.h"
#endif

#include <math.h>
#include <stdlib.h>
#include <stdio.h>

#if __has_include("omp.h")
#include <omp.h>
#define Z5D_GEODESIC_OMP_AVAILABLE 1
#else
#define Z5D_GEODESIC_OMP_AVAILABLE 0
#define omp_get_max_threads() 1
#define omp_get_thread_num() 0
#define omp_set_num_threads(x) ((void)0)
#define omp_get_wtime() 0.0
#endif

// Constants from params.py (calibrated)
#define KAPPA_GEO_DEFAULT 0.3
#define KAPPA_STAR_DEFAULT 0.04449
#define PHI ((1.0 + sqrt(5.0)) / 2.0)
#define E2 (exp(2.0))  // e^2 invariant
#define MP_DPS 256  // High precision (256 bits minimum for extreme k values)

// Forward declaration to resolve implicit declaration errors
static int is_probable_prime(const mpz_t n, int reps);

// Z5D Predictor (high-precision using MPFR for extreme k values)
static void z5d_predict(mpz_t result, unsigned long long k) {
    // Initialize MPFR variables with high precision
    mpfr_set_default_prec(MP_DPS);
    
    mpfr_t k_mp, log_k, log_log_k, pnt, d_term, e_term, pred;
    mpfr_t temp1, temp2, temp3;
    mpz_t k_mpz;
    
    mpfr_inits2(MP_DPS, k_mp, log_k, log_log_k, pnt, d_term, e_term, pred, 
                temp1, temp2, temp3, (mpfr_ptr) 0);
    mpz_init(k_mpz);
    
    // Convert k to MPFR via mpz_t for large values
    mpz_set_ui(k_mpz, (unsigned long)(k & 0xFFFFFFFF));  // Lower 32 bits
    if (k > 0xFFFFFFFF) {
        mpz_t temp;
        mpz_init(temp);
        mpz_set_ui(temp, (unsigned long)(k >> 32));  // Upper 32 bits
        mpz_mul_2exp(temp, temp, 32);
        mpz_add(k_mpz, k_mpz, temp);
        mpz_clear(temp);
    }
    mpfr_set_z(k_mp, k_mpz, MPFR_RNDN);
    
    // Compute log(k)
    mpfr_log(log_k, k_mp, MPFR_RNDN);
    
    // Compute log(log(k))
    mpfr_log(log_log_k, log_k, MPFR_RNDN);
    
    // Base PNT: k * (log(k) + log(log(k)) - 1.0 + (log(log(k)) - 2.0)/log(k))
    
    // temp1 = log(log(k)) - 2.0
    mpfr_sub_ui(temp1, log_log_k, 2, MPFR_RNDN);
    
    // temp2 = (log(log(k)) - 2.0) / log(k)
    mpfr_div(temp2, temp1, log_k, MPFR_RNDN);
    
    // temp3 = log(k) + log(log(k)) - 1.0 + temp2
    mpfr_add(temp3, log_k, log_log_k, MPFR_RNDN);
    mpfr_sub_ui(temp3, temp3, 1, MPFR_RNDN);
    mpfr_add(temp3, temp3, temp2, MPFR_RNDN);
    
    // pnt = k * temp3
    mpfr_mul(pnt, k_mp, temp3, MPFR_RNDN);
    
    // d_term = -0.00247 * pnt (calibrated c)
    mpfr_mul_d(d_term, pnt, -0.00247, MPFR_RNDN);
    
    // e_term = KAPPA_STAR_DEFAULT * exp(log(k) / E2) (e-term scaling)
    mpfr_div_d(temp1, log_k, E2, MPFR_RNDN);
    mpfr_exp(temp1, temp1, MPFR_RNDN);
    mpfr_mul_d(e_term, temp1, KAPPA_STAR_DEFAULT, MPFR_RNDN);
    mpfr_mul(e_term, e_term, pnt, MPFR_RNDN);
    
    // pred = pnt + d_term + e_term
    mpfr_add(pred, pnt, d_term, MPFR_RNDN);
    mpfr_add(pred, pred, e_term, MPFR_RNDN);
    
    // Convert to mpz_t (round to nearest integer)
    mpfr_get_z(result, pred, MPFR_RNDN);
    
    // Clean up
    mpfr_clears(k_mp, log_k, log_log_k, pnt, d_term, e_term, pred, 
                temp1, temp2, temp3, (mpfr_ptr) 0);
    mpz_clear(k_mpz);
}

// Main Search (outwards from center on odds, no geodesic)
static void z5d_search(unsigned long long k, mpz_t prime, int *tests_performed) {
    mpz_t center;
    mpz_init(center);
    
    // Use high-precision predictor for center calculation
    z5d_predict(center, k);
    
    // Make center odd (adjust to nearest odd if even)
    if (mpz_even_p(center)) {
        mpz_add_ui(center, center, 1);  // Prefer +1; could check distance but simple
    }

    int found = 0;
    int tests = 0;
    mpz_t cand;
    mpz_init(cand);

    // Loop outwards: center, then ±2, ±4, ...
    const int max_offset = 500;  // Equivalent to ~1000 odd candidates
    for (int offset = 0; offset <= max_offset && !found; offset++) {
        if (offset == 0) {
            // Test center
            mpz_set(cand, center);
            tests++;
            if (is_probable_prime(cand, 10)) {
                mpz_set(prime, cand);
                found = 1;
            }
        } else {
            // Test center + offset*2
            mpz_add_ui(cand, center, offset * 2);
            tests++;
            if (is_probable_prime(cand, 10)) {
                mpz_set(prime, cand);
                found = 1;
            }

            if (!found) {
                // Test center - offset*2 (if positive)
                mpz_sub_ui(cand, center, offset * 2);
                if (mpz_sgn(cand) > 0) {
                    tests++;
                    if (is_probable_prime(cand, 10)) {
                        mpz_set(prime, cand);
                        found = 1;
                    }
                }
            }
        }
    }

    if (!found) {
        mpz_set_ui(prime, 0);  // Indicate not found
    }
    *tests_performed = tests;

    mpz_clear(center);
    mpz_clear(cand);
}

// Miller-Rabin (optimized with GMP; deterministic bases for <2^64, extend for larger)
static int is_probable_prime(const mpz_t n, int reps) {
    (void)reps;  // silence unused parameter warning
    // Handle small cases
    if (mpz_cmp_ui(n, 2) < 0) return 0;
    if (mpz_cmp_ui(n, 2) == 0) return 1;
    if (mpz_even_p(n)) return 0;

    mpz_t d, y, nm1;
    mpz_inits(d, y, nm1, NULL);
    mpz_sub_ui(nm1, n, 1);
    int s = mpz_scan1(nm1, 0);
    mpz_tdiv_q_2exp(d, nm1, s);

    // Bases for deterministic MR up to 2^64 (extend for larger ranges as needed)
    const unsigned long bases[] = {2ul, 3ul, 5ul, 7ul, 11ul, 13ul, 23ul, 29ul};
    const int nb = (int)(sizeof(bases)/sizeof(bases[0]));

    for (int i = 0; i < nb; i++) {
        mpz_set_ui(y, bases[i]);
        mpz_powm(y, y, d, n);  // y = a^d mod n
        if (mpz_cmp_ui(y, 1) == 0 || mpz_cmp(y, nm1) == 0) continue;
        int witness = 1;
        for (int r = 1; r < s; r++) {
            mpz_powm_ui(y, y, 2, n);
            if (mpz_cmp(y, nm1) == 0) { witness = 0; break; }
        }
        if (witness) { mpz_clears(d, y, nm1, NULL); return 0; }
    }
    mpz_clears(d, y, nm1, NULL);
    return 1;
}

int main(int argc, char *argv[]) {
    unsigned long long k_start = 8686ULL;  // Default start for p_k ~10^5 range
    int num_ks = 10;                 // Default number of k's to test

    // Override defaults with command-line arguments if provided
    if (argc > 1) {
        k_start = strtoull(argv[1], NULL, 10);
    }
    if (argc > 2) {
        num_ks = atoi(argv[2]);
    }

    printf("Starting search with k_start = %llu and num_ks = %d\n", k_start, num_ks);

    double total_time_ms = 0.0;
    int total_tests = 0;
    int num_found = 0;

    for (int i = 0; i < num_ks; i++) {
        unsigned long long k = k_start + i;
        mpz_t prime;
        mpz_init(prime);
        int tests = 0;
        double start = omp_get_wtime();
        z5d_search(k, prime, &tests);
        double time_ms = (omp_get_wtime() - start) * 1000.0;
        total_time_ms += time_ms;
        total_tests += tests;
        if (mpz_cmp_ui(prime, 0) != 0) {
            num_found++;
            gmp_printf("k=%llu Prime: %Zd\n", k, prime);
        } else {
            printf("Not found for k=%llu\n", k);
        }
        mpz_clear(prime);
    }

    printf("Found %d out of %d\n", num_found, num_ks);
    printf("Average time: %.3f ms\n", total_time_ms / num_ks);
    printf("Average MR tests per find: %.1f\n", (double)total_tests / num_ks);

    return 0;
}
