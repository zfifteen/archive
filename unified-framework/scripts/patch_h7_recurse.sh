#!/bin/bash
# Add params
sed -i '' 's/double k = 0.45;/double k_star = 0.04449; double width = 0.4; double h7_thresh = 0.252; # e^2 approx
#define E_SQ (2.718281828459045 * 2.718281828459045)
#define RECURSE_DEPTH 5
#define ZF_GOLDEN_PHI ((1 + sqrt(5)) / 2)/' z5d_factorization_shortcut.c

# Add kappa_n fn (before main loop)
sed -i '' '/static double theta_prime_from_bn/i\\
static double kappa_n(const mpz_t n) {\\
    // d(n) stub: 2 for prime; full trial div\\
    int d = 2;\\
    mpfr_t ln_np1; mpfr_init2(ln_np1, 512); mpfr_log_ui(ln_np1, mpz_get_ui(n) + 1, MPFR_RNDN);\\
    double res = d * mpfr_get_d(ln_np1, MPFR_RNDN) / E_SQ;\\
    mpfr_clear(ln_np1); return res;\\
}\\
static int recurse_h7(mpz_t cand, double theta_n, int depth, const mpz_t N_mpz) {\\
    if (depth > RECURSE_DEPTH) return 0;\\
    mpz_t h7_n; mpz_init_set_ui(h7_n, 3 * mpz_get_ui(cand) * mpz_get_ui(cand) + mpz_get_ui(cand));  // H7 approx\\
    double theta_prime = theta_prime_from_mpz(cand, k_star);  // Assume helper\\
    double theta_adj = theta_prime + width * fmod(mpz_get_d(h7_n), ZF_GOLDEN_PHI);\\
    double dist = circular_distance(theta_adj, theta_n);\\
    if (dist >= h7_thresh) { mpz_clear(h7_n); return 0; }\\
    // Z-Red\\
    mpz_t prev; mpz_init_set(prev, cand); mpz_sub_ui(prev, prev, 1);\\
    double delta_n = kappa_n(cand) - kappa_n(prev);\\
    double delta_max = log(mpz_get_d(N_mpz));\\
    double z_red = mpz_get_d(cand) * (delta_n / delta_max);\\
    mpz_t cand_red; mpz_init_set_d(cand_red, z_red); if (mpz_even_p(cand_red)) mpz_add_ui(cand_red, cand_red, 1);\\
    mpz_divexact(cand, cand, cand_red);\\
    int is_prime = mpz_probab_prime_p(cand, 10);\\
    if (is_prime) { mpz_clear(h7_n); mpz_clear(prev); mpz_clear(cand_red); return 1; }\\
    int rec = recurse_h7(cand, theta_adj, depth + 1, N_mpz);\\
    mpz_clear(h7_n); mpz_clear(prev); mpz_clear(cand_red); return rec;\\
}' z5d_factorization_shortcut.c

# Int in loop (before if (dist > epsilon))
sed -i '' '/double dist = circular_distance(theta_p, theta_N);/a\\
    mpz_t mp_cand, N_mpz;\\
    mpz_init_set_str(mp_cand, BN_bn2dec(candidate), 10);\\
    mpz_init_set_str(N_mpz, modulus_decimal, 10);\\
    if (!recurse_h7(mp_cand, theta_N, 0, N_mpz)) {\\
        mpz_clear(mp_cand); mpz_clear(N_mpz); continue;\\
    }\\
    mpz_clear(mp_cand); mpz_clear(N_mpz);\\
    // Update candidate from reduced mp_cand if needed\\
    BN_dec2bn(&candidate, mpz_get_str(NULL, 10, mp_cand));' z5d_factorization_shortcut.c

# Add theta_prime_from_mpz stub
sed -i '' '/static double theta_prime_from_bn/a\\
static double theta_prime_from_mpz(const mpz_t z, double k) {\\
    mpfr_t mp_z; mpfr_init2(mp_z, 512); mpfr_set_z(mp_z, z, MPFR_RNDN);\\
    double res = theta_prime_from_mpfr(mp_z, k);\\
    mpfr_clear(mp_z); return res;\\
}' z5d_factorization_shortcut.c
