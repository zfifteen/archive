/**
 * Golden Lucas Predictor - Header File
 * ==================================
 * 
 * Header file for Mersenne prime prediction using golden space ℚ(√5) 
 * invariance and Lucas predictor with ℚ(√3) roots.
 * 
 * @file z_golden_lucas.h
 * @author D.A.L. III (Dionisio Alberto Lopez III)
 * @version 1.0
 */

#ifndef Z_GOLDEN_LUCAS_H
#define Z_GOLDEN_LUCAS_H

#include <mpfr.h>
#include <gmp.h>

/**
 * Structure to hold golden ratio constants with high precision
 */
typedef struct {
    mpfr_t phi;         // Golden ratio φ = (1 + √5)/2
    mpfr_t phi_inv;     // φ^(-1) = (√5 - 1)/2  
    mpfr_t sqrt5;       // √5
    mpfr_t sqrt3;       // √3 for Lucas sequences
} golden_constants_t;

/**
 * Structure to hold prediction results
 */
typedef struct {
    int is_prime;               // Predicted primality (1 = prime, 0 = composite)
    double confidence;          // Prediction confidence [0.0, 1.0]
    double galois_invariant;    // Galois invariance measure in ℚ(√5)
    double geometric_point;     // Geometric point analysis
    double cross_correlation;   // Cross-correlation with golden spiral
    double lucas_convergence;   // Lucas-Lehmer convergence approximation
} golden_prediction_t;

/**
 * Main prediction function using golden-Lucas hybrid approach
 * 
 * @param exp Mersenne exponent to test
 * @param is_prime Output: predicted primality (1 = prime, 0 = composite)
 * @param confidence Output: prediction confidence [0.0, 1.0]
 * @param verbose Enable verbose output
 */
void golden_lucas_predict(mpz_t exp, int *is_prime, double *confidence, int verbose);

/**
 * Extended prediction function with detailed results
 * 
 * @param exp Mersenne exponent to test
 * @param result Output: detailed prediction results
 * @param verbose Enable verbose output
 */
void golden_lucas_predict_detailed(mpz_t exp, golden_prediction_t *result, int verbose);

/**
 * Test the golden lucas predictor with known Mersenne exponents
 */
void test_golden_lucas_predictor(void);

/**
 * Calculate Galois invariance in golden space ℚ(√5)
 * 
 * @param exp Input exponent
 * @param invariant Output: invariance measure
 * @param constants Pre-initialized golden constants
 */
void calculate_galois_invariance(mpz_t exp, mpfr_t invariant, const golden_constants_t *constants);

/**
 * Calculate geometric point analysis for golden spiral
 * 
 * @param exp Input exponent  
 * @param geometric_point Output: geometric point measure
 * @param constants Pre-initialized golden constants
 */
void calculate_geometric_point(mpz_t exp, mpfr_t geometric_point, const golden_constants_t *constants);

/**
 * Calculate cross-correlation with golden spiral pattern
 * 
 * @param exp Input exponent
 * @param correlation Output: correlation measure
 * @param constants Pre-initialized golden constants
 */
void calculate_cross_correlation(mpz_t exp, mpfr_t correlation, const golden_constants_t *constants);

/**
 * Approximate Lucas-Lehmer sequence convergence using ℚ(√3) roots
 * 
 * @param exp Input exponent
 * @param convergence Output: convergence approximation
 * @param constants Pre-initialized golden constants
 */
void lucas_lehmer_convergence(mpz_t exp, mpfr_t convergence, const golden_constants_t *constants);

#endif // Z_GOLDEN_LUCAS_H