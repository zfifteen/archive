#include "modular_progressions.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

/**
 * @file modular_progressions.c
 * @brief Core modular geometric progression functions implementation
 * 
 * Implements modular geometric progressions following Z Framework principles.
 * Uses GMP and MPFR for high-precision calculations with 256-bit precision.
 */

void mod_geom_prog_init(mod_geom_prog_t *prog) {
    mpz_init(prog->base);
    mpz_init(prog->ratio);
    mpz_init(prog->modulus);
    prog->terms = 0;
}

void mod_geom_prog_clear(mod_geom_prog_t *prog) {
    mpz_clear(prog->base);
    mpz_clear(prog->ratio);
    mpz_clear(prog->modulus);
    prog->terms = 0;
}

void mod_geom_prog_set(mod_geom_prog_t *prog, unsigned long base,
                       unsigned long ratio, unsigned long modulus,
                       unsigned long terms) {
    mpz_set_ui(prog->base, base);
    mpz_set_ui(prog->ratio, ratio);
    mpz_set_ui(prog->modulus, modulus);
    prog->terms = terms;
}

void mod_geom_prog_term(mpz_t result, const mod_geom_prog_t *prog, unsigned long n) {
    // Compute a * r^n (mod m)
    mpz_t ratio_power;
    mpz_init(ratio_power);
    
    // Compute r^n mod m using fast exponentiation
    mpz_powm_ui(ratio_power, prog->ratio, n, prog->modulus);
    
    // Multiply by base: a * r^n mod m
    mpz_mul(result, prog->base, ratio_power);
    mpz_mod(result, result, prog->modulus);
    
    mpz_clear(ratio_power);
}

void mod_geom_prog_sum(mpz_t result, const mod_geom_prog_t *prog, unsigned long n) {
    if (n == 0) {
        mpz_set_ui(result, 0);
        return;
    }
    
    if (n == 1) {
        mpz_mod(result, prog->base, prog->modulus);
        return;
    }
    
    // Check if ratio = 1 (mod m)
    mpz_t temp;
    mpz_init(temp);
    mpz_sub_ui(temp, prog->ratio, 1);
    
    if (mpz_divisible_p(temp, prog->modulus)) {
        // r ≡ 1 (mod m), sum = n * a (mod m)
        mpz_mul_ui(result, prog->base, n);
        mpz_mod(result, result, prog->modulus);
    } else {
        // General case: sum = a * (r^n - 1) / (r - 1) (mod m)
        mpz_t r_power_n, numerator, denominator, inv_denom;
        mpz_init(r_power_n);
        mpz_init(numerator);
        mpz_init(denominator);
        mpz_init(inv_denom);
        
        // r^n mod m
        mpz_powm_ui(r_power_n, prog->ratio, n, prog->modulus);
        
        // r^n - 1
        mpz_sub_ui(numerator, r_power_n, 1);
        
        // a * (r^n - 1)
        mpz_mul(numerator, prog->base, numerator);
        
        // r - 1
        mpz_sub_ui(denominator, prog->ratio, 1);
        
        // Find modular inverse of (r - 1) mod m
        if (mpz_invert(inv_denom, denominator, prog->modulus)) {
            mpz_mul(result, numerator, inv_denom);
            mpz_mod(result, result, prog->modulus);
        } else {
            // No inverse exists, use approximation
            mpz_mod(result, numerator, prog->modulus);
        }
        
        mpz_clear(r_power_n);
        mpz_clear(numerator);
        mpz_clear(denominator);
        mpz_clear(inv_denom);
    }
    
    mpz_clear(temp);
}

unsigned long mod_geom_prog_period(const mod_geom_prog_t *prog) {
    // Find the period of the sequence a * r^n (mod m)
    // This is the order of r modulo m
    
    mpz_t current, initial;
    mpz_init(current);
    mpz_init(initial);
    
    // Start with r mod m
    mpz_mod(current, prog->ratio, prog->modulus);
    mpz_set(initial, current);
    
    unsigned long period = 1;
    const unsigned long max_period = 10000; // Reasonable upper bound
    
    while (period < max_period) {
        mpz_mul(current, current, prog->ratio);
        mpz_mod(current, current, prog->modulus);
        
        if (mpz_cmp(current, initial) == 0) {
            mpz_clear(current);
            mpz_clear(initial);
            return period;
        }
        period++;
    }
    
    mpz_clear(current);
    mpz_clear(initial);
    return 0; // No period found within bounds
}

long mod_geom_prog_contains(const mod_geom_prog_t *prog, const mpz_t value,
                           unsigned long max_terms) {
    mpz_t term;
    mpz_init(term);
    
    for (unsigned long i = 0; i < max_terms; i++) {
        mod_geom_prog_term(term, prog, i);
        if (mpz_cmp(term, value) == 0) {
            mpz_clear(term);
            return (long)i;
        }
    }
    
    mpz_clear(term);
    return -1; // Not found
}

void mod_geom_prog_geodesic_term(mpfr_t result, const mod_geom_prog_t *prog,
                                 unsigned long n, double kappa_geo) {
    // Apply Z Framework geodesic mapping: enhanced = term * (n/φ)^kappa
    mpz_t term;
    mpfr_t term_f, n_f, phi, phi_ratio, enhancement;
    
    mpz_init(term);
    mpfr_init2(term_f, MP_DPS);
    mpfr_init2(n_f, MP_DPS);
    mpfr_init2(phi, MP_DPS);
    mpfr_init2(phi_ratio, MP_DPS);
    mpfr_init2(enhancement, MP_DPS);
    
    // Get the regular term
    mod_geom_prog_term(term, prog, n);
    mpfr_set_z(term_f, term, MPFR_RNDN);
    
    // Golden ratio φ = (1 + √5)/2
    mpfr_sqrt_ui(phi, 5, MPFR_RNDN);
    mpfr_add_ui(phi, phi, 1, MPFR_RNDN);
    mpfr_div_ui(phi, phi, 2, MPFR_RNDN);
    
    // Compute (n/φ)^kappa_geo
    mpfr_set_ui(n_f, n, MPFR_RNDN);
    mpfr_div(phi_ratio, n_f, phi, MPFR_RNDN);
    
    // Convert kappa_geo to MPFR and compute power
    mpfr_t kappa_f;
    mpfr_init2(kappa_f, MP_DPS);
    mpfr_set_d(kappa_f, kappa_geo, MPFR_RNDN);
    mpfr_pow(enhancement, phi_ratio, kappa_f, MPFR_RNDN);
    mpfr_clear(kappa_f);
    
    // Apply geodesic enhancement
    mpfr_mul(result, term_f, enhancement, MPFR_RNDN);
    
    // Cleanup
    mpz_clear(term);
    mpfr_clear(term_f);
    mpfr_clear(n_f);
    mpfr_clear(phi);
    mpfr_clear(phi_ratio);
    mpfr_clear(enhancement);
}

void mod_geom_prog_generate_terms(mpz_t *terms, const mod_geom_prog_t *prog,
                                  unsigned long count) {
    for (unsigned long i = 0; i < count; i++) {
        mod_geom_prog_term(terms[i], prog, i);
    }
}