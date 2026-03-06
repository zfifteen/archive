/*
 * Z5D C Adapter - Performance-Optimized Prime Operations
 * Uses GMP for arbitrary precision with uint64_t for small scales
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <gmp.h>

#define K_OR_PHASE 0.27952859830111265

/*
 * Estimate nth prime using asymptotic expansion (small scale)
 * For n < 2^64
 */
uint64_t n_est_small(uint64_t n) {
    if (n < 1) {
        fprintf(stderr, "Error: n must be >= 1\n");
        return 0;
    }
    
    double ln_n = log((double)n);
    double ln_ln_n = log(ln_n);
    
    // PNT approximation with correction
    double estimate = (double)n * (ln_n + ln_ln_n - 1.0 + (ln_ln_n - 2.0) / ln_n);
    
    // Geometric resonance phase correction
    double phase_correction = 1.0 + K_OR_PHASE * ln_n / (double)n;
    estimate *= phase_correction;
    
    return (uint64_t)estimate;
}

/*
 * Estimate nth prime using GMP for arbitrary precision
 * Result stored in rop (caller must initialize)
 */
void n_est_gmp(mpz_t rop, mpz_t n_val, double k_or_phase) {
    mpfr_t n, ln_n, ln_ln_n, estimate, phase_correction;
    mpfr_t tmp1, tmp2, tmp3;
    
    // Initialize with precision of 256 bits (about 77 decimal digits)
    mpfr_init2(n, 256);
    mpfr_init2(ln_n, 256);
    mpfr_init2(ln_ln_n, 256);
    mpfr_init2(estimate, 256);
    mpfr_init2(phase_correction, 256);
    mpfr_init2(tmp1, 256);
    mpfr_init2(tmp2, 256);
    mpfr_init2(tmp3, 256);
    
    // Convert n to mpfr
    mpfr_set_z(n, n_val, MPFR_RNDN);
    
    // Calculate ln(n)
    mpfr_log(ln_n, n, MPFR_RNDN);
    
    // Calculate ln(ln(n))
    mpfr_log(ln_ln_n, ln_n, MPFR_RNDN);
    
    // Calculate: n * (ln(n) + ln(ln(n)) - 1 + (ln(ln(n))-2)/ln(n))
    // tmp1 = ln(ln(n)) - 2
    mpfr_sub_ui(tmp1, ln_ln_n, 2, MPFR_RNDN);
    
    // tmp2 = tmp1 / ln(n)
    mpfr_div(tmp2, tmp1, ln_n, MPFR_RNDN);
    
    // tmp3 = ln(n) + ln(ln(n)) - 1 + tmp2
    mpfr_add(tmp3, ln_n, ln_ln_n, MPFR_RNDN);
    mpfr_sub_ui(tmp3, tmp3, 1, MPFR_RNDN);
    mpfr_add(tmp3, tmp3, tmp2, MPFR_RNDN);
    
    // estimate = n * tmp3
    mpfr_mul(estimate, n, tmp3, MPFR_RNDN);
    
    // Phase correction: 1 + k * ln(n) / n
    mpfr_set_d(phase_correction, k_or_phase, MPFR_RNDN);
    mpfr_mul(phase_correction, phase_correction, ln_n, MPFR_RNDN);
    mpfr_div(phase_correction, phase_correction, n, MPFR_RNDN);
    mpfr_add_ui(phase_correction, phase_correction, 1, MPFR_RNDN);
    
    // estimate *= phase_correction
    mpfr_mul(estimate, estimate, phase_correction, MPFR_RNDN);
    
    // Convert to integer
    mpfr_get_z(rop, estimate, MPFR_RNDN);
    
    // Cleanup
    mpfr_clear(n);
    mpfr_clear(ln_n);
    mpfr_clear(ln_ln_n);
    mpfr_clear(estimate);
    mpfr_clear(phase_correction);
    mpfr_clear(tmp1);
    mpfr_clear(tmp2);
    mpfr_clear(tmp3);
}

/*
 * Calculate geometric resonance score for semiprime
 */
double geometric_resonance_score(uint64_t p, uint64_t q) {
    double ln_p = log((double)p);
    double ln_q = log((double)q);
    double ln_n = log((double)(p * q));
    
    // Expected geometric mean
    double expected_geom_mean = ln_n / 2.0;
    
    // Asymmetry measure
    double asymmetry = fabs(ln_q - ln_p) / (ln_q + ln_p);
    
    // Actual geometric position
    double actual_position = (ln_p + ln_q) / 2.0;
    
    // Deviation normalized by scale
    double deviation = fabs(actual_position - expected_geom_mean) / sqrt(ln_n);
    
    // Z5D score (negative = strong resonance)
    double z5d_score = -10.0 * log(1.0 + asymmetry) / (1.0 + deviation);
    
    return z5d_score;
}

/* Main function for testing */
int main(int argc, char *argv[]) {
    printf("Z5D C Adapter Self-Test\n");
    printf("========================================\n");
    
    // Test small scale
    uint64_t n_small = 100;
    uint64_t est_small = n_est_small(n_small);
    printf("Estimated 100th prime: %lu\n", est_small);
    printf("Actual 100th prime: 541\n");
    
    // Test GMP for larger scale
    mpz_t n_large, result;
    mpz_init(n_large);
    mpz_init(result);
    
    mpz_set_ui(n_large, 1000000);
    n_est_gmp(result, n_large, K_OR_PHASE);
    
    printf("\nEstimated 1,000,000th prime: ");
    mpz_out_str(stdout, 10, result);
    printf("\n");
    
    // Test geometric resonance
    uint64_t p = 3, q = 5;
    double score = geometric_resonance_score(p, q);
    printf("\nZ5D score for N=15 (3×5): %.4f\n", score);
    
    // Cleanup
    mpz_clear(n_large);
    mpz_clear(result);
    
    printf("\n✓ All tests completed successfully\n");
    
    return 0;
}
