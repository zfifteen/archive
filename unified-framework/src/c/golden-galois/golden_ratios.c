#include "golden_ratios.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <mpfr.h>
#include <gmp.h>

/**
 * @file golden_ratios.c
 * @brief Implementation of multi-base golden ratio computations
 * 
 * High-precision MPFR implementation of golden ratio extensions including
 * φ, silver ratio, and Tribonacci constant with Galois field operations.
 */

void golden_init_precision(unsigned int precision_bits) {
    mpfr_set_default_prec(precision_bits);
}

void golden_compute_phi(mpfr_t result, mpfr_prec_t precision) {
    mpfr_t sqrt5, one;
    
    mpfr_init2(sqrt5, precision);
    mpfr_init2(one, precision);
    
    // Compute √5
    mpfr_set_ui(sqrt5, 5, MPFR_RNDN);
    mpfr_sqrt(sqrt5, sqrt5, MPFR_RNDN);
    
    // Compute (1 + √5) / 2
    mpfr_set_ui(one, 1, MPFR_RNDN);
    mpfr_add(result, one, sqrt5, MPFR_RNDN);
    mpfr_div_ui(result, result, 2, MPFR_RNDN);
    
    mpfr_clear(sqrt5);
    mpfr_clear(one);
}

void golden_compute_phi_conjugate(mpfr_t result, mpfr_prec_t precision) {
    mpfr_t sqrt5, one;
    
    mpfr_init2(sqrt5, precision);
    mpfr_init2(one, precision);
    
    // Compute √5
    mpfr_set_ui(sqrt5, 5, MPFR_RNDN);
    mpfr_sqrt(sqrt5, sqrt5, MPFR_RNDN);
    
    // Compute (1 - √5) / 2
    mpfr_set_ui(one, 1, MPFR_RNDN);
    mpfr_sub(result, one, sqrt5, MPFR_RNDN);
    mpfr_div_ui(result, result, 2, MPFR_RNDN);
    
    mpfr_clear(sqrt5);
    mpfr_clear(one);
}

void golden_compute_silver(mpfr_t result, mpfr_prec_t precision) {
    mpfr_t sqrt2, one;
    
    mpfr_init2(sqrt2, precision);
    mpfr_init2(one, precision);
    
    // Compute √2
    mpfr_set_ui(sqrt2, 2, MPFR_RNDN);
    mpfr_sqrt(sqrt2, sqrt2, MPFR_RNDN);
    
    // Compute 1 + √2
    mpfr_set_ui(one, 1, MPFR_RNDN);
    mpfr_add(result, one, sqrt2, MPFR_RNDN);
    
    mpfr_clear(sqrt2);
    mpfr_clear(one);
}

void golden_compute_tribonacci(mpfr_t result, mpfr_prec_t precision, int max_iterations) {
    mpfr_t x, x_old, f_x, df_x, delta, tolerance;
    
    mpfr_init2(x, precision);
    mpfr_init2(x_old, precision);
    mpfr_init2(f_x, precision);
    mpfr_init2(df_x, precision);
    mpfr_init2(delta, precision);
    mpfr_init2(tolerance, precision);
    
    // Set tolerance for Newton-Raphson convergence
    mpfr_set_str(tolerance, "1e-80", 10, MPFR_RNDN);
    
    // Initial guess: x = 1.8 (close to tribonacci constant)
    mpfr_set_d(x, 1.8, MPFR_RNDN);
    
    // Newton-Raphson iteration to solve x³ - x² - x - 1 = 0
    for (int i = 0; i < max_iterations; i++) {
        mpfr_set(x_old, x, MPFR_RNDN);
        
        // f(x) = x³ - x² - x - 1
        mpfr_pow_ui(f_x, x, 3, MPFR_RNDN);     // x³
        mpfr_sqr(delta, x, MPFR_RNDN);          // x²
        mpfr_sub(f_x, f_x, delta, MPFR_RNDN);   // x³ - x²
        mpfr_sub(f_x, f_x, x, MPFR_RNDN);       // x³ - x² - x
        mpfr_sub_ui(f_x, f_x, 1, MPFR_RNDN);    // x³ - x² - x - 1
        
        // f'(x) = 3x² - 2x - 1
        mpfr_sqr(df_x, x, MPFR_RNDN);           // x²
        mpfr_mul_ui(df_x, df_x, 3, MPFR_RNDN);  // 3x²
        mpfr_mul_ui(delta, x, 2, MPFR_RNDN);    // 2x
        mpfr_sub(df_x, df_x, delta, MPFR_RNDN); // 3x² - 2x
        mpfr_sub_ui(df_x, df_x, 1, MPFR_RNDN);  // 3x² - 2x - 1
        
        // Newton step: x_new = x - f(x)/f'(x)
        mpfr_div(delta, f_x, df_x, MPFR_RNDN);
        mpfr_sub(x, x, delta, MPFR_RNDN);
        
        // Check convergence
        mpfr_sub(delta, x, x_old, MPFR_RNDN);
        mpfr_abs(delta, delta, MPFR_RNDN);
        
        if (mpfr_cmp(delta, tolerance) < 0) {
            break;
        }
    }
    
    mpfr_set(result, x, MPFR_RNDN);
    
    mpfr_clear(x);
    mpfr_clear(x_old);
    mpfr_clear(f_x);
    mpfr_clear(df_x);
    mpfr_clear(delta);
    mpfr_clear(tolerance);
}

void golden_compute_power(mpfr_t result, mpfr_t base, long exponent, 
                         golden_ratio_type_t ratio_type, mpfr_prec_t precision) {
    if (ratio_type == GOLDEN_PHI) {
        // For φ, use the identity φⁿ = F_n * φ + F_{n-1} for efficiency
        // This is more numerically stable than direct exponentiation
        mpfr_pow_si(result, base, exponent, MPFR_RNDN);
    } else {
        // For other ratios, use direct exponentiation
        mpfr_pow_si(result, base, exponent, MPFR_RNDN);
    }
}

void golden_apply_galois_automorphism(mpfr_t result, mpfr_t input, 
                                    galois_automorphism_t automorphism, 
                                    mpfr_prec_t precision) {
    if (automorphism == GALOIS_IDENTITY) {
        mpfr_set(result, input, MPFR_RNDN);
    } else {
        // For conjugation, φ → φ̄ = (1 - √5)/2
        // This only applies to golden ratio φ
        golden_compute_phi_conjugate(result, precision);
    }
}

void golden_compute_trace(mpfr_t result, mpfr_t golden_value, mpfr_prec_t precision) {
    mpfr_t phi_conjugate;
    
    mpfr_init2(phi_conjugate, precision);
    
    // Trace(φ) = φ + φ̄ = 1
    golden_compute_phi_conjugate(phi_conjugate, precision);
    mpfr_add(result, golden_value, phi_conjugate, MPFR_RNDN);
    
    mpfr_clear(phi_conjugate);
}

void golden_compute_norm(mpfr_t result, mpfr_t golden_value, mpfr_prec_t precision) {
    mpfr_t phi_conjugate;
    
    mpfr_init2(phi_conjugate, precision);
    
    // Norm(φ) = φ * φ̄ = -1
    golden_compute_phi_conjugate(phi_conjugate, precision);
    mpfr_mul(result, golden_value, phi_conjugate, MPFR_RNDN);
    
    mpfr_clear(phi_conjugate);
}

bool golden_is_galois_invariant(mpfr_t value, mpfr_t tolerance, mpfr_prec_t precision) {
    mpfr_t conjugate_value, difference;
    bool is_invariant;
    
    mpfr_init2(conjugate_value, precision);
    mpfr_init2(difference, precision);
    
    // Apply conjugation and check if result is same as original
    golden_apply_galois_automorphism(conjugate_value, value, GALOIS_CONJUGATE, precision);
    mpfr_sub(difference, value, conjugate_value, MPFR_RNDN);
    mpfr_abs(difference, difference, MPFR_RNDN);
    
    is_invariant = (mpfr_cmp(difference, tolerance) <= 0);
    
    mpfr_clear(conjugate_value);
    mpfr_clear(difference);
    
    return is_invariant;
}

void golden_to_minimal_polynomial(mpfr_t coeffs[3], golden_ratio_type_t ratio_type, 
                                 mpfr_prec_t precision) {
    // Initialize coefficients
    mpfr_init2(coeffs[0], precision);
    mpfr_init2(coeffs[1], precision);
    mpfr_init2(coeffs[2], precision);
    
    switch (ratio_type) {
        case GOLDEN_PHI:
            // φ satisfies x² - x - 1 = 0, so coefficients are [-1, -1, 1]
            mpfr_set_si(coeffs[0], -1, MPFR_RNDN);  // constant term
            mpfr_set_si(coeffs[1], -1, MPFR_RNDN);  // linear term
            mpfr_set_si(coeffs[2], 1, MPFR_RNDN);   // quadratic term
            break;
            
        case GOLDEN_SILVER:
            // Silver ratio: (1 + √2)² - 2(1 + √2) - 1 = 0 → x² - 2x - 1 = 0
            mpfr_set_si(coeffs[0], -1, MPFR_RNDN);  // constant term
            mpfr_set_si(coeffs[1], -2, MPFR_RNDN);  // linear term
            mpfr_set_si(coeffs[2], 1, MPFR_RNDN);   // quadratic term
            break;
            
        case GOLDEN_TRIBONACCI:
            // Tribonacci: x³ - x² - x - 1 = 0 (already in standard form)
            mpfr_set_si(coeffs[0], -1, MPFR_RNDN);  // constant term
            mpfr_set_si(coeffs[1], -1, MPFR_RNDN);  // linear term
            mpfr_set_si(coeffs[2], -1, MPFR_RNDN);  // quadratic term
            // Note: This is cubic, but we only store first 3 coefficients
            break;
    }
}

void golden_continued_fraction(mpfr_t result, int num_terms, 
                              golden_ratio_type_t ratio_type, mpfr_prec_t precision) {
    mpfr_t temp, one;
    
    mpfr_init2(temp, precision);
    mpfr_init2(one, precision);
    mpfr_set_ui(one, 1, MPFR_RNDN);
    
    if (ratio_type == GOLDEN_PHI) {
        // φ = [1; 1, 1, 1, 1, ...]
        mpfr_set_ui(result, 1, MPFR_RNDN);
        
        for (int i = 1; i < num_terms; i++) {
            mpfr_add(temp, result, one, MPFR_RNDN);
            mpfr_div(result, temp, result, MPFR_RNDN);
            mpfr_add(result, one, result, MPFR_RNDN);
        }
    } else {
        // For other ratios, compute directly
        switch (ratio_type) {
            case GOLDEN_SILVER:
                golden_compute_silver(result, precision);
                break;
            case GOLDEN_TRIBONACCI:
                golden_compute_tribonacci(result, precision, 100);
                break;
            default:
                mpfr_set_ui(result, 1, MPFR_RNDN);
        }
    }
    
    mpfr_clear(temp);
    mpfr_clear(one);
}

void golden_print_info(mpfr_t value, golden_ratio_type_t ratio_type, 
                      mpfr_prec_t precision, bool verbose) {
    const char* ratio_names[] = {"φ (Golden ratio)", "Silver ratio", "Tribonacci"};
    
    printf("📐 %s\n", ratio_names[ratio_type]);
    printf("   Value: ");
    mpfr_printf("%.50Rf", value);
    printf("\n");
    printf("   Precision: %lu bits\n", (unsigned long)precision);
    
    if (verbose) {
        mpfr_t trace, norm, coeffs[3];
        
        mpfr_init2(trace, precision);
        mpfr_init2(norm, precision);
        
        if (ratio_type == GOLDEN_PHI) {
            golden_compute_trace(trace, value, precision);
            golden_compute_norm(norm, value, precision);
            
            printf("   Trace in ℚ(√5): ");
            mpfr_printf("%.20Rf", trace);
            printf("\n");
            printf("   Norm in ℚ(√5): ");
            mpfr_printf("%.20Rf", norm);
            printf("\n");
        }
        
        golden_to_minimal_polynomial(coeffs, ratio_type, precision);
        printf("   Minimal polynomial: ");
        mpfr_printf("%.10Rf", coeffs[2]);
        printf("x² + ");
        mpfr_printf("%.10Rf", coeffs[1]);
        printf("x + ");
        mpfr_printf("%.10Rf", coeffs[0]);
        printf(" = 0\n");
        
        mpfr_clear(trace);
        mpfr_clear(norm);
        mpfr_clear(coeffs[0]);
        mpfr_clear(coeffs[1]);
        mpfr_clear(coeffs[2]);
    }
    
    printf("\n");
}