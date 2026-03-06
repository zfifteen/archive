#ifndef GALOIS_FIELD_H
#define GALOIS_FIELD_H

#include <mpfr.h>
#include <stdbool.h>

/**
 * @file galois_field.h
 * @brief Galois field operations for ℚ(√5) extension
 * 
 * This module provides operations for the Galois field extension ℚ(√5)
 * with automorphism group {id, σ} where σ(√5) = -√5. Used for analyzing
 * Mersenne prime invariance under Galois automorphisms.
 */

// Field element structure for ℚ(√5)
// Represents a + b√5 where a, b ∈ ℚ
typedef struct {
    mpfr_t rational_part;  // a (rational part)
    mpfr_t sqrt5_part;     // b (coefficient of √5)
    mpfr_prec_t precision; // MPFR precision
} galois_field_element_t;

// Galois automorphism types
typedef enum {
    GALOIS_AUTO_IDENTITY,   // id: √5 → √5
    GALOIS_AUTO_CONJUGATE   // σ: √5 → -√5
} galois_auto_type_t;

/**
 * Initialize a Galois field element
 * @param element Field element to initialize
 * @param precision MPFR precision
 */
void galois_field_init(galois_field_element_t *element, mpfr_prec_t precision);

/**
 * Clear a Galois field element
 * @param element Field element to clear
 */
void galois_field_clear(galois_field_element_t *element);

/**
 * Set field element to a + b√5
 * @param element Field element to set
 * @param a Rational part
 * @param b Coefficient of √5
 */
void galois_field_set(galois_field_element_t *element, mpfr_t a, mpfr_t b);

/**
 * Set field element from golden ratio φ = (1 + √5)/2
 * @param element Field element to set
 * @param precision MPFR precision
 */
void galois_field_set_phi(galois_field_element_t *element, mpfr_prec_t precision);

/**
 * Set field element from φ̄ = (1 - √5)/2 (Galois conjugate)
 * @param element Field element to set
 * @param precision MPFR precision
 */
void galois_field_set_phi_conjugate(galois_field_element_t *element, mpfr_prec_t precision);

/**
 * Add two field elements: (a₁ + b₁√5) + (a₂ + b₂√5) = (a₁+a₂) + (b₁+b₂)√5
 * @param result Output field element
 * @param op1 First operand
 * @param op2 Second operand
 */
void galois_field_add(galois_field_element_t *result, 
                     const galois_field_element_t *op1, 
                     const galois_field_element_t *op2);

/**
 * Multiply two field elements using (a₁+b₁√5)(a₂+b₂√5) = (a₁a₂+5b₁b₂) + (a₁b₂+a₂b₁)√5
 * @param result Output field element
 * @param op1 First operand
 * @param op2 Second operand
 */
void galois_field_multiply(galois_field_element_t *result, 
                          const galois_field_element_t *op1, 
                          const galois_field_element_t *op2);

/**
 * Apply Galois automorphism to field element
 * @param result Output field element
 * @param input Input field element
 * @param auto_type Type of automorphism
 */
void galois_field_apply_automorphism(galois_field_element_t *result, 
                                    const galois_field_element_t *input, 
                                    galois_auto_type_t auto_type);

/**
 * Compute trace of field element: Tr(a + b√5) = (a + b√5) + (a - b√5) = 2a
 * @param result Output MPFR variable for trace
 * @param element Input field element
 */
void galois_field_trace(mpfr_t result, const galois_field_element_t *element);

/**
 * Compute norm of field element: N(a + b√5) = (a + b√5)(a - b√5) = a² - 5b²
 * @param result Output MPFR variable for norm
 * @param element Input field element
 */
void galois_field_norm(mpfr_t result, const galois_field_element_t *element);

/**
 * Test if field element is invariant under all Galois automorphisms
 * An element is invariant iff it's in the base field ℚ (i.e., √5 coefficient is 0)
 * @param element Field element to test
 * @param tolerance Numerical tolerance for zero checking
 * @return true if invariant, false otherwise
 */
bool galois_field_is_invariant(const galois_field_element_t *element, mpfr_t tolerance);

/**
 * Convert field element to MPFR value (for rational elements only)
 * @param result Output MPFR variable
 * @param element Input field element (must be rational)
 * @return true if conversion successful, false if element is not rational
 */
bool galois_field_to_mpfr(mpfr_t result, const galois_field_element_t *element);

/**
 * Test if two field elements are equal within tolerance
 * @param op1 First field element
 * @param op2 Second field element
 * @param tolerance Numerical tolerance
 * @return true if equal, false otherwise
 */
bool galois_field_equal(const galois_field_element_t *op1, 
                       const galois_field_element_t *op2, 
                       mpfr_t tolerance);

/**
 * Compute minimal polynomial of field element over ℚ
 * For φ, this gives x² - x - 1 = 0
 * @param coeffs Array to store polynomial coefficients [a₀, a₁, a₂] for a₀ + a₁x + a₂x²
 * @param element Input field element
 */
void galois_field_minimal_polynomial(mpfr_t coeffs[3], const galois_field_element_t *element);

/**
 * Generate orbit of field element under Galois group
 * For ℚ(√5), orbit has at most 2 elements: {α, σ(α)}
 * @param orbit Array to store orbit elements (size 2)
 * @param element Input field element
 * @return Number of distinct elements in orbit (1 if invariant, 2 otherwise)
 */
int galois_field_orbit(galois_field_element_t orbit[2], const galois_field_element_t *element);

/**
 * Print field element in standard form a + b√5
 * @param element Field element to print
 * @param precision Display precision
 * @param verbose Enable verbose output
 */
void galois_field_print(const galois_field_element_t *element, int precision, bool verbose);

/**
 * Check if field element satisfies specific polynomial equation
 * Useful for verifying φ² - φ - 1 = 0
 * @param element Field element to test
 * @param coeffs Polynomial coefficients [a₀, a₁, a₂] for a₀ + a₁x + a₂x²
 * @param tolerance Numerical tolerance
 * @return true if element is a root, false otherwise
 */
bool galois_field_is_polynomial_root(const galois_field_element_t *element, 
                                    mpfr_t coeffs[3], mpfr_t tolerance);

#endif // GALOIS_FIELD_H