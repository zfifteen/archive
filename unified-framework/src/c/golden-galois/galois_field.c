#include "galois_field.h"
#include <stdio.h>
#include <stdlib.h>
#include <mpfr.h>
#include <gmp.h>

/**
 * @file galois_field.c
 * @brief Implementation of Galois field operations for ℚ(√5)
 * 
 * Operations for the field extension ℚ(√5) with Galois group of order 2.
 * Elements represented as a + b√5 with high-precision MPFR arithmetic.
 */

void galois_field_init(galois_field_element_t *element, mpfr_prec_t precision) {
    mpfr_init2(element->rational_part, precision);
    mpfr_init2(element->sqrt5_part, precision);
    element->precision = precision;
    
    // Initialize to zero
    mpfr_set_ui(element->rational_part, 0, MPFR_RNDN);
    mpfr_set_ui(element->sqrt5_part, 0, MPFR_RNDN);
}

void galois_field_clear(galois_field_element_t *element) {
    mpfr_clear(element->rational_part);
    mpfr_clear(element->sqrt5_part);
}

void galois_field_set(galois_field_element_t *element, mpfr_t a, mpfr_t b) {
    mpfr_set(element->rational_part, a, MPFR_RNDN);
    mpfr_set(element->sqrt5_part, b, MPFR_RNDN);
}

void galois_field_set_phi(galois_field_element_t *element, mpfr_prec_t precision) {
    mpfr_t half;
    
    mpfr_init2(half, precision);
    mpfr_set_d(half, 0.5, MPFR_RNDN);
    
    // φ = (1 + √5)/2 = 1/2 + (1/2)√5
    mpfr_set(element->rational_part, half, MPFR_RNDN);  // a = 1/2
    mpfr_set(element->sqrt5_part, half, MPFR_RNDN);     // b = 1/2
    
    mpfr_clear(half);
}

void galois_field_set_phi_conjugate(galois_field_element_t *element, mpfr_prec_t precision) {
    mpfr_t half, neg_half;
    
    mpfr_init2(half, precision);
    mpfr_init2(neg_half, precision);
    
    mpfr_set_d(half, 0.5, MPFR_RNDN);
    mpfr_set_d(neg_half, -0.5, MPFR_RNDN);
    
    // φ̄ = (1 - √5)/2 = 1/2 + (-1/2)√5
    mpfr_set(element->rational_part, half, MPFR_RNDN);     // a = 1/2
    mpfr_set(element->sqrt5_part, neg_half, MPFR_RNDN);    // b = -1/2
    
    mpfr_clear(half);
    mpfr_clear(neg_half);
}

void galois_field_add(galois_field_element_t *result, 
                     const galois_field_element_t *op1, 
                     const galois_field_element_t *op2) {
    // (a₁ + b₁√5) + (a₂ + b₂√5) = (a₁ + a₂) + (b₁ + b₂)√5
    mpfr_add(result->rational_part, op1->rational_part, op2->rational_part, MPFR_RNDN);
    mpfr_add(result->sqrt5_part, op1->sqrt5_part, op2->sqrt5_part, MPFR_RNDN);
}

void galois_field_multiply(galois_field_element_t *result, 
                          const galois_field_element_t *op1, 
                          const galois_field_element_t *op2) {
    mpfr_t temp1, temp2, temp3, temp4;
    mpfr_prec_t precision = op1->precision;
    
    mpfr_init2(temp1, precision);
    mpfr_init2(temp2, precision);
    mpfr_init2(temp3, precision);
    mpfr_init2(temp4, precision);
    
    // (a₁ + b₁√5)(a₂ + b₂√5) = (a₁a₂ + 5b₁b₂) + (a₁b₂ + a₂b₁)√5
    
    // Rational part: a₁a₂ + 5b₁b₂
    mpfr_mul(temp1, op1->rational_part, op2->rational_part, MPFR_RNDN);  // a₁a₂
    mpfr_mul(temp2, op1->sqrt5_part, op2->sqrt5_part, MPFR_RNDN);        // b₁b₂
    mpfr_mul_ui(temp2, temp2, 5, MPFR_RNDN);                             // 5b₁b₂
    mpfr_add(result->rational_part, temp1, temp2, MPFR_RNDN);
    
    // √5 coefficient: a₁b₂ + a₂b₁
    mpfr_mul(temp3, op1->rational_part, op2->sqrt5_part, MPFR_RNDN);     // a₁b₂
    mpfr_mul(temp4, op2->rational_part, op1->sqrt5_part, MPFR_RNDN);     // a₂b₁
    mpfr_add(result->sqrt5_part, temp3, temp4, MPFR_RNDN);
    
    mpfr_clear(temp1);
    mpfr_clear(temp2);
    mpfr_clear(temp3);
    mpfr_clear(temp4);
}

void galois_field_apply_automorphism(galois_field_element_t *result, 
                                    const galois_field_element_t *input, 
                                    galois_auto_type_t auto_type) {
    if (auto_type == GALOIS_AUTO_IDENTITY) {
        // Identity: a + b√5 → a + b√5
        mpfr_set(result->rational_part, input->rational_part, MPFR_RNDN);
        mpfr_set(result->sqrt5_part, input->sqrt5_part, MPFR_RNDN);
    } else {
        // Conjugation: a + b√5 → a - b√5
        mpfr_set(result->rational_part, input->rational_part, MPFR_RNDN);
        mpfr_neg(result->sqrt5_part, input->sqrt5_part, MPFR_RNDN);
    }
}

void galois_field_trace(mpfr_t result, const galois_field_element_t *element) {
    galois_field_element_t conjugate;
    mpfr_t sum;
    
    galois_field_init(&conjugate, element->precision);
    mpfr_init2(sum, element->precision);
    
    // Tr(a + b√5) = (a + b√5) + (a - b√5) = 2a
    galois_field_apply_automorphism(&conjugate, element, GALOIS_AUTO_CONJUGATE);
    mpfr_add(result, element->rational_part, conjugate.rational_part, MPFR_RNDN);
    
    galois_field_clear(&conjugate);
    mpfr_clear(sum);
}

void galois_field_norm(mpfr_t result, const galois_field_element_t *element) {
    galois_field_element_t conjugate, product;
    
    galois_field_init(&conjugate, element->precision);
    galois_field_init(&product, element->precision);
    
    // N(a + b√5) = (a + b√5)(a - b√5) = a² - 5b²
    galois_field_apply_automorphism(&conjugate, element, GALOIS_AUTO_CONJUGATE);
    galois_field_multiply(&product, element, &conjugate);
    
    // Result is rational, so take the rational part
    mpfr_set(result, product.rational_part, MPFR_RNDN);
    
    galois_field_clear(&conjugate);
    galois_field_clear(&product);
}

bool galois_field_is_invariant(const galois_field_element_t *element, mpfr_t tolerance) {
    galois_field_element_t conjugate;
    mpfr_t diff;
    bool is_invariant;
    
    galois_field_init(&conjugate, element->precision);
    mpfr_init2(diff, element->precision);
    
    // Element is invariant iff σ(element) = element
    // This happens iff the √5 coefficient is 0
    galois_field_apply_automorphism(&conjugate, element, GALOIS_AUTO_CONJUGATE);
    
    // Check if √5 coefficients are equal (which means both are 0 for invariance)
    mpfr_sub(diff, element->sqrt5_part, conjugate.sqrt5_part, MPFR_RNDN);
    mpfr_abs(diff, diff, MPFR_RNDN);
    
    // Simple check: element is invariant if sqrt5_part is near zero
    mpfr_abs(diff, element->sqrt5_part, MPFR_RNDN);
    is_invariant = (mpfr_cmp(diff, tolerance) <= 0);
    
    galois_field_clear(&conjugate);
    mpfr_clear(diff);
    
    return is_invariant;
}

bool galois_field_to_mpfr(mpfr_t result, const galois_field_element_t *element) {
    mpfr_t tolerance;
    bool is_rational;
    
    mpfr_init2(tolerance, element->precision);
    mpfr_set_str(tolerance, "1e-80", 10, MPFR_RNDN);
    
    // Check if √5 coefficient is essentially zero
    mpfr_abs(tolerance, element->sqrt5_part, MPFR_RNDN);
    mpfr_t small_threshold;
    mpfr_init2(small_threshold, element->precision);
    mpfr_set_str(small_threshold, "1e-80", 10, MPFR_RNDN);
    is_rational = (mpfr_cmp(tolerance, small_threshold) <= 0);
    mpfr_clear(small_threshold);
    
    if (is_rational) {
        mpfr_set(result, element->rational_part, MPFR_RNDN);
    }
    
    mpfr_clear(tolerance);
    return is_rational;
}

bool galois_field_equal(const galois_field_element_t *op1, 
                       const galois_field_element_t *op2, 
                       mpfr_t tolerance) {
    mpfr_t diff1, diff2;
    bool are_equal;
    
    mpfr_init2(diff1, op1->precision);
    mpfr_init2(diff2, op1->precision);
    
    // Check if both rational and √5 parts are equal within tolerance
    mpfr_sub(diff1, op1->rational_part, op2->rational_part, MPFR_RNDN);
    mpfr_abs(diff1, diff1, MPFR_RNDN);
    
    mpfr_sub(diff2, op1->sqrt5_part, op2->sqrt5_part, MPFR_RNDN);
    mpfr_abs(diff2, diff2, MPFR_RNDN);
    
    are_equal = (mpfr_cmp(diff1, tolerance) <= 0) && (mpfr_cmp(diff2, tolerance) <= 0);
    
    mpfr_clear(diff1);
    mpfr_clear(diff2);
    
    return are_equal;
}

void galois_field_minimal_polynomial(mpfr_t coeffs[3], const galois_field_element_t *element) {
    galois_field_element_t conjugate;
    mpfr_t trace, norm;
    
    galois_field_init(&conjugate, element->precision);
    mpfr_init2(trace, element->precision);
    mpfr_init2(norm, element->precision);
    
    // For element α, minimal polynomial is (x - α)(x - σ(α)) = x² - Tr(α)x + N(α)
    galois_field_trace(trace, element);
    galois_field_norm(norm, element);
    
    // Coefficients for x² - Tr(α)x + N(α)
    mpfr_set(coeffs[0], norm, MPFR_RNDN);      // constant term: N(α)
    mpfr_neg(coeffs[1], trace, MPFR_RNDN);     // linear term: -Tr(α)
    mpfr_set_ui(coeffs[2], 1, MPFR_RNDN);      // quadratic term: 1
    
    galois_field_clear(&conjugate);
    mpfr_clear(trace);
    mpfr_clear(norm);
}

int galois_field_orbit(galois_field_element_t orbit[2], const galois_field_element_t *element) {
    mpfr_t tolerance;
    
    mpfr_init2(tolerance, element->precision);
    mpfr_set_str(tolerance, "1e-80", 10, MPFR_RNDN);
    
    // First orbit element is the element itself
    galois_field_init(&orbit[0], element->precision);
    mpfr_set(orbit[0].rational_part, element->rational_part, MPFR_RNDN);
    mpfr_set(orbit[0].sqrt5_part, element->sqrt5_part, MPFR_RNDN);
    
    // Second orbit element is the conjugate
    galois_field_init(&orbit[1], element->precision);
    galois_field_apply_automorphism(&orbit[1], element, GALOIS_AUTO_CONJUGATE);
    
    // Check if element is invariant (orbit size 1)
    if (galois_field_equal(&orbit[0], &orbit[1], tolerance)) {
        galois_field_clear(&orbit[1]);
        mpfr_clear(tolerance);
        return 1;
    }
    
    mpfr_clear(tolerance);
    return 2;
}

void galois_field_print(const galois_field_element_t *element, int precision, bool verbose) {
    printf("(");
    mpfr_printf("%.Rf", element->rational_part);
    
    // Handle sign of √5 coefficient
    if (mpfr_sgn(element->sqrt5_part) >= 0) {
        printf(" + ");
    } else {
        printf(" - ");
    }
    
    mpfr_t abs_sqrt5;
    mpfr_init2(abs_sqrt5, element->precision);
    mpfr_abs(abs_sqrt5, element->sqrt5_part, MPFR_RNDN);
    mpfr_printf("%.Rf", abs_sqrt5);
    printf("√5)");
    
    if (verbose) {
        mpfr_t trace, norm;
        mpfr_init2(trace, element->precision);
        mpfr_init2(norm, element->precision);
        
        galois_field_trace(trace, element);
        galois_field_norm(norm, element);
        
        printf("\n   Trace: ");
        mpfr_printf("%.Rf", trace);
        printf("\n   Norm: ");
        mpfr_printf("%.Rf", norm);
        
        mpfr_clear(trace);
        mpfr_clear(norm);
    }
    
    mpfr_clear(abs_sqrt5);
}

bool galois_field_is_polynomial_root(const galois_field_element_t *element, 
                                    mpfr_t coeffs[3], mpfr_t tolerance) {
    galois_field_element_t x, x_squared, result;
    mpfr_t temp;
    bool is_root;
    
    galois_field_init(&x, element->precision);
    galois_field_init(&x_squared, element->precision);
    galois_field_init(&result, element->precision);
    mpfr_init2(temp, element->precision);
    
    // Copy element to x
    mpfr_set(x.rational_part, element->rational_part, MPFR_RNDN);
    mpfr_set(x.sqrt5_part, element->sqrt5_part, MPFR_RNDN);
    
    // Compute x²
    galois_field_multiply(&x_squared, &x, &x);
    
    // Evaluate polynomial: a₂x² + a₁x + a₀
    // Start with constant term
    mpfr_set(result.rational_part, coeffs[0], MPFR_RNDN);
    mpfr_set_ui(result.sqrt5_part, 0, MPFR_RNDN);
    
    // Add a₁x term
    galois_field_element_t linear_term;
    galois_field_init(&linear_term, element->precision);
    mpfr_mul(linear_term.rational_part, coeffs[1], x.rational_part, MPFR_RNDN);
    mpfr_mul(linear_term.sqrt5_part, coeffs[1], x.sqrt5_part, MPFR_RNDN);
    galois_field_add(&result, &result, &linear_term);
    
    // Add a₂x² term
    galois_field_element_t quadratic_term;
    galois_field_init(&quadratic_term, element->precision);
    mpfr_mul(quadratic_term.rational_part, coeffs[2], x_squared.rational_part, MPFR_RNDN);
    mpfr_mul(quadratic_term.sqrt5_part, coeffs[2], x_squared.sqrt5_part, MPFR_RNDN);
    galois_field_add(&result, &result, &quadratic_term);
    
    // Check if result is close to zero
    mpfr_abs(temp, result.rational_part, MPFR_RNDN);
    is_root = (mpfr_cmp(temp, tolerance) <= 0);
    
    mpfr_abs(temp, result.sqrt5_part, MPFR_RNDN);
    is_root = is_root && (mpfr_cmp(temp, tolerance) <= 0);
    
    galois_field_clear(&x);
    galois_field_clear(&x_squared);
    galois_field_clear(&result);
    galois_field_clear(&linear_term);
    galois_field_clear(&quadratic_term);
    mpfr_clear(temp);
    
    return is_root;
}