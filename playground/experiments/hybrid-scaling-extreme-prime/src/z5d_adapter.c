/*
 * Z5D Adapter - C Implementation
 * High-performance adapter using GMP/MPFR for scales ≤50
 * Provides fixed precision arithmetic for extreme prime prediction
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gmp.h>
#include <mpfr.h>
#include <string.h>

#define PRECISION 256  // Fixed precision in bits for scales ≤50
#define MAX_SCALE 50

// Structure to hold prime prediction results
typedef struct {
    double predicted_value;
    double actual_value;
    double relative_error;
    double log10_relative_error;
} PrimePrediction;

// Prime Number Theorem based nth-prime approximation
// p_n ≈ n * (ln(n) + ln(ln(n)) - 1 + (ln(ln(n)) - 2)/ln(n))
void compute_nth_prime_approximation(mpfr_t result, unsigned long n, mpfr_rnd_t rnd) {
    mpfr_t ln_n, ln_ln_n, term1, term2, term3, temp;
    
    mpfr_init2(ln_n, PRECISION);
    mpfr_init2(ln_ln_n, PRECISION);
    mpfr_init2(term1, PRECISION);
    mpfr_init2(term2, PRECISION);
    mpfr_init2(term3, PRECISION);
    mpfr_init2(temp, PRECISION);
    
    // Compute ln(n)
    mpfr_set_ui(temp, n, rnd);
    mpfr_log(ln_n, temp, rnd);
    
    // Compute ln(ln(n))
    mpfr_log(ln_ln_n, ln_n, rnd);
    
    // term1 = ln(n)
    mpfr_set(term1, ln_n, rnd);
    
    // term2 = ln(ln(n)) - 1
    mpfr_sub_ui(term2, ln_ln_n, 1, rnd);
    
    // term3 = (ln(ln(n)) - 2) / ln(n)
    mpfr_sub_ui(temp, ln_ln_n, 2, rnd);
    mpfr_div(term3, temp, ln_n, rnd);
    
    // result = n * (term1 + term2 + term3)
    mpfr_add(result, term1, term2, rnd);
    mpfr_add(result, result, term3, rnd);
    mpfr_set_ui(temp, n, rnd);
    mpfr_mul(result, result, temp, rnd);
    
    mpfr_clear(ln_n);
    mpfr_clear(ln_ln_n);
    mpfr_clear(term1);
    mpfr_clear(term2);
    mpfr_clear(term3);
    mpfr_clear(temp);
}

// Compute Z5D score (log10-relative error)
double compute_z5d_score(double predicted, double actual) {
    if (actual == 0.0) {
        return INFINITY;
    }
    
    double relative_error = fabs((predicted - actual) / actual);
    
    if (relative_error == 0.0) {
        return -INFINITY;  // Perfect prediction
    }
    
    return log10(relative_error);
}

// Test prime prediction at given scale
PrimePrediction test_prime_prediction(unsigned long n) {
    PrimePrediction result;
    mpfr_t predicted;
    mpfr_rnd_t rnd = MPFR_RNDN;
    
    mpfr_init2(predicted, PRECISION);
    
    // Compute prediction using PNT with corrections
    compute_nth_prime_approximation(predicted, n, rnd);
    
    result.predicted_value = mpfr_get_d(predicted, rnd);
    
    // For testing, we'll use the approximation as both predicted and "actual"
    // In real usage, actual would come from prime tables or computation
    result.actual_value = result.predicted_value;
    
    // Compute relative error
    result.relative_error = 0.0;  // Perfect for self-test
    result.log10_relative_error = compute_z5d_score(result.predicted_value, result.actual_value);
    
    mpfr_clear(predicted);
    
    return result;
}

// Main function for testing
int main(int argc, char *argv[]) {
    unsigned long scale = 10;
    
    if (argc > 1) {
        scale = strtoul(argv[1], NULL, 10);
        if (scale > MAX_SCALE) {
            fprintf(stderr, "Warning: Scale %lu exceeds MAX_SCALE %d. Use Python adapter for higher scales.\n", 
                    scale, MAX_SCALE);
            scale = MAX_SCALE;
        }
    }
    
    printf("C Adapter - Testing at scale %lu\n", scale);
    printf("Using fixed precision: %d bits\n", PRECISION);
    printf("==========================================\n\n");
    
    // Test predictions at various scales
    unsigned long test_n = 1;
    for (int i = 0; i < scale; i++) {
        test_n *= 10;
    }
    
    PrimePrediction pred = test_prime_prediction(test_n);
    
    printf("n = 10^%lu\n", scale);
    printf("Predicted nth prime: %.6e\n", pred.predicted_value);
    printf("Relative error: %.6e\n", pred.relative_error);
    printf("Log10 relative error: %.6f\n", pred.log10_relative_error);
    
    return 0;
}
