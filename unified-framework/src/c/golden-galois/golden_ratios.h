#ifndef GOLDEN_RATIOS_H
#define GOLDEN_RATIOS_H

#include <mpfr.h>
#include <stdbool.h>

/**
 * @file golden_ratios.h
 * @brief Multi-base golden ratio computations with high precision
 * 
 * This module provides high-precision computations for various golden ratio
 * extensions including φ, φ² (silver ratio), and Tribonacci constant.
 * All computations use MPFR for numerical stability.
 */

// Default precision for MPFR computations (256 bits)
#define GOLDEN_PRECISION_BITS 256

// Golden ratio types
typedef enum {
    GOLDEN_PHI,        // φ = (1 + √5)/2 ≈ 1.618033988749
    GOLDEN_SILVER,     // 1 + √2 ≈ 2.414213562373
    GOLDEN_TRIBONACCI  // ψ ≈ 1.839286755214 (real root of x³-x²-x-1=0)
} golden_ratio_type_t;

// Galois conjugate type
typedef enum {
    GALOIS_IDENTITY,   // Identity automorphism
    GALOIS_CONJUGATE   // Conjugation automorphism (√5 → -√5)
} galois_automorphism_t;

/**
 * Initialize MPFR precision for golden ratio computations
 * @param precision_bits MPFR precision in bits
 */
void golden_init_precision(unsigned int precision_bits);

/**
 * Compute golden ratio φ = (1 + √5)/2
 * @param result Output MPFR variable
 * @param precision MPFR precision
 */
void golden_compute_phi(mpfr_t result, mpfr_prec_t precision);

/**
 * Compute Galois conjugate φ̄ = (1 - √5)/2
 * @param result Output MPFR variable
 * @param precision MPFR precision
 */
void golden_compute_phi_conjugate(mpfr_t result, mpfr_prec_t precision);

/**
 * Compute silver ratio 1 + √2
 * @param result Output MPFR variable
 * @param precision MPFR precision
 */
void golden_compute_silver(mpfr_t result, mpfr_prec_t precision);

/**
 * Compute Tribonacci constant (real root of x³ - x² - x - 1 = 0)
 * Uses Newton-Raphson iteration for high precision
 * @param result Output MPFR variable
 * @param precision MPFR precision
 * @param max_iterations Maximum Newton-Raphson iterations
 */
void golden_compute_tribonacci(mpfr_t result, mpfr_prec_t precision, int max_iterations);

/**
 * Compute powers of golden ratios with high precision
 * @param result Output MPFR variable
 * @param base Golden ratio base
 * @param exponent Integer exponent
 * @param ratio_type Type of golden ratio
 * @param precision MPFR precision
 */
void golden_compute_power(mpfr_t result, mpfr_t base, long exponent, 
                         golden_ratio_type_t ratio_type, mpfr_prec_t precision);

/**
 * Apply Galois automorphism to golden ratio expression
 * @param result Output MPFR variable
 * @param input Input golden ratio value
 * @param automorphism Type of Galois automorphism
 * @param precision MPFR precision
 */
void golden_apply_galois_automorphism(mpfr_t result, mpfr_t input, 
                                    galois_automorphism_t automorphism, 
                                    mpfr_prec_t precision);

/**
 * Compute trace of golden ratio in field extension ℚ(√5)
 * Trace(φ) = φ + φ̄ = 1
 * @param result Output MPFR variable
 * @param golden_value Input golden ratio
 * @param precision MPFR precision
 */
void golden_compute_trace(mpfr_t result, mpfr_t golden_value, mpfr_prec_t precision);

/**
 * Compute norm of golden ratio in field extension ℚ(√5)
 * Norm(φ) = φ * φ̄ = -1
 * @param result Output MPFR variable
 * @param golden_value Input golden ratio
 * @param precision MPFR precision
 */
void golden_compute_norm(mpfr_t result, mpfr_t golden_value, mpfr_prec_t precision);

/**
 * Test if value is invariant under Galois automorphism φ ↔ φ̄
 * @param value Input value to test
 * @param tolerance Numerical tolerance for comparison
 * @param precision MPFR precision
 * @return true if invariant, false otherwise
 */
bool golden_is_galois_invariant(mpfr_t value, mpfr_t tolerance, mpfr_prec_t precision);

/**
 * Convert golden ratio to minimal polynomial representation
 * φ satisfies x² - x - 1 = 0
 * @param coeffs Array to store polynomial coefficients [a₀, a₁, a₂]
 * @param ratio_type Type of golden ratio
 * @param precision MPFR precision
 */
void golden_to_minimal_polynomial(mpfr_t coeffs[3], golden_ratio_type_t ratio_type, 
                                 mpfr_prec_t precision);

/**
 * Evaluate continued fraction representation of golden ratio
 * φ = [1; 1, 1, 1, 1, ...]
 * @param result Output MPFR variable
 * @param num_terms Number of continued fraction terms
 * @param ratio_type Type of golden ratio
 * @param precision MPFR precision
 */
void golden_continued_fraction(mpfr_t result, int num_terms, 
                              golden_ratio_type_t ratio_type, mpfr_prec_t precision);

/**
 * Print golden ratio information with specified precision
 * @param value Golden ratio value
 * @param ratio_type Type of golden ratio
 * @param precision MPFR precision
 * @param verbose Enable verbose output
 */
void golden_print_info(mpfr_t value, golden_ratio_type_t ratio_type, 
                      mpfr_prec_t precision, bool verbose);

#endif // GOLDEN_RATIOS_H