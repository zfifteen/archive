#include "sha256_bounds.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

/**
 * @file sha256_bounds.c
 * @brief SHA-256 bounds analysis implementation
 */

// SHA-256 round constants (same as in crypto_analysis.c for consistency)
const uint32_t SHA256_ROUND_CONSTANTS[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

void sha256_bounds_init(sha256_bounds_t *bounds) {
    mod_geom_prog_init(&bounds->base_progression);
    mpfr_init2(bounds->analysis_precision, MP_DPS);
    mpz_init(bounds->constant_bound);
    bounds->round_count = 64;
    
    // Set default analysis precision
    mpfr_set_d(bounds->analysis_precision, 1e-10, MPFR_RNDN);
}

void sha256_bounds_clear(sha256_bounds_t *bounds) {
    mod_geom_prog_clear(&bounds->base_progression);
    mpfr_clear(bounds->analysis_precision);
    mpz_clear(bounds->constant_bound);
    bounds->round_count = 0;
}

bool sha256_analyze_round_constant(mpfr_t lower_bound, mpfr_t upper_bound,
                                   unsigned int round_index,
                                   const mod_geom_prog_t *progression) {
    if (round_index >= 64) {
        return false;
    }
    
    mpfr_t constant, prog_term, deviation;
    mpfr_init2(constant, MP_DPS);
    mpfr_init2(prog_term, MP_DPS);
    mpfr_init2(deviation, MP_DPS);
    
    // Get SHA-256 constant
    mpfr_set_ui(constant, SHA256_ROUND_CONSTANTS[round_index], MPFR_RNDN);
    
    // Get corresponding geometric progression term with geodesic enhancement
    mod_geom_prog_geodesic_term(prog_term, progression, round_index, KAPPA_GEO_DEFAULT);
    
    // Compute relative deviation as bound width
    mpfr_sub(deviation, constant, prog_term, MPFR_RNDN);
    mpfr_abs(deviation, deviation, MPFR_RNDN);
    
    // If progression term is zero, use the constant itself for bounds
    if (mpfr_zero_p(prog_term)) {
        mpfr_mul_d(lower_bound, constant, 0.5, MPFR_RNDN);
        mpfr_mul_d(upper_bound, constant, 1.5, MPFR_RNDN);
    } else {
        // Use progression term ± deviation as bounds
        mpfr_sub(lower_bound, prog_term, deviation, MPFR_RNDN);
        mpfr_add(upper_bound, prog_term, deviation, MPFR_RNDN);
    }
    
    mpfr_clear(constant);
    mpfr_clear(prog_term);
    mpfr_clear(deviation);
    
    return true;
}

int sha256_compute_all_bounds(mpfr_t bounds_array[][2], 
                              const mod_geom_prog_t *progression) {
    int successful_bounds = 0;
    
    for (int i = 0; i < 64; i++) {
        if (sha256_analyze_round_constant(bounds_array[i][0], bounds_array[i][1], 
                                          i, progression)) {
            successful_bounds++;
        }
    }
    
    return successful_bounds;
}

int sha256_test_constant_bounds(const mod_geom_prog_t *progression, double tolerance) {
    int constants_within_bounds = 0;
    
    for (int i = 0; i < 64; i++) {
        mpfr_t lower, upper, constant, prog_term;
        mpfr_init2(lower, MP_DPS);
        mpfr_init2(upper, MP_DPS);
        mpfr_init2(constant, MP_DPS);
        mpfr_init2(prog_term, MP_DPS);
        
        mpfr_set_ui(constant, SHA256_ROUND_CONSTANTS[i], MPFR_RNDN);
        mod_geom_prog_geodesic_term(prog_term, progression, i, KAPPA_GEO_DEFAULT);
        
        // Create bounds with tolerance
        mpfr_mul_d(lower, prog_term, 1.0 - tolerance, MPFR_RNDN);
        mpfr_mul_d(upper, prog_term, 1.0 + tolerance, MPFR_RNDN);
        
        // Check if constant is within bounds
        if (mpfr_cmp(constant, lower) >= 0 && mpfr_cmp(constant, upper) <= 0) {
            constants_within_bounds++;
        }
        
        mpfr_clear(lower);
        mpfr_clear(upper);
        mpfr_clear(constant);
        mpfr_clear(prog_term);
    }
    
    return constants_within_bounds;
}

bool sha256_analyze_geometric_structure(mpfr_t structure_score,
                                        const mod_geom_prog_t *progression,
                                        double kappa_geo) {
    mpfr_t total_deviation, avg_deviation, constant, prog_term, diff;
    mpfr_init2(total_deviation, MP_DPS);
    mpfr_init2(avg_deviation, MP_DPS);
    mpfr_init2(constant, MP_DPS);
    mpfr_init2(prog_term, MP_DPS);
    mpfr_init2(diff, MP_DPS);
    
    mpfr_set_ui(total_deviation, 0, MPFR_RNDN);
    
    // Compute average relative deviation from geometric progression
    for (int i = 0; i < 64; i++) {
        mpfr_set_ui(constant, SHA256_ROUND_CONSTANTS[i], MPFR_RNDN);
        mod_geom_prog_geodesic_term(prog_term, progression, i, kappa_geo);
        
        if (!mpfr_zero_p(prog_term)) {
            mpfr_sub(diff, constant, prog_term, MPFR_RNDN);
            mpfr_abs(diff, diff, MPFR_RNDN);
            mpfr_div(diff, diff, prog_term, MPFR_RNDN); // Relative deviation
            mpfr_add(total_deviation, total_deviation, diff, MPFR_RNDN);
        }
    }
    
    // Average deviation (lower is better structure)
    mpfr_div_ui(avg_deviation, total_deviation, 64, MPFR_RNDN);
    
    // Structure score = 1 - avg_deviation (higher is better structure)
    mpfr_ui_sub(structure_score, 1, avg_deviation, MPFR_RNDN);
    
    mpfr_clear(total_deviation);
    mpfr_clear(avg_deviation);
    mpfr_clear(constant);
    mpfr_clear(prog_term);
    mpfr_clear(diff);
    
    return true;
}

bool sha256_crypto_strength_bounds(mpfr_t min_strength, mpfr_t max_strength,
                                   const mod_geom_prog_t *progression) {
    // Analyze cryptographic strength based on geometric progression properties
    
    mpfr_t period_strength, modulus_strength, ratio_strength;
    mpfr_init2(period_strength, MP_DPS);
    mpfr_init2(modulus_strength, MP_DPS);
    mpfr_init2(ratio_strength, MP_DPS);
    
    // Period-based strength
    unsigned long period = mod_geom_prog_period(progression);
    if (period == 0) {
        mpfr_set_ui(period_strength, 256, MPFR_RNDN); // Very strong
    } else {
        mpfr_set_ui(period_strength, period, MPFR_RNDN);
        mpfr_log2(period_strength, period_strength, MPFR_RNDN);
    }
    
    // Modulus-based strength
    mpfr_set_z(modulus_strength, progression->modulus, MPFR_RNDN);
    mpfr_log2(modulus_strength, modulus_strength, MPFR_RNDN);
    
    // Ratio-based strength (entropy measure)
    mpfr_set_z(ratio_strength, progression->ratio, MPFR_RNDN);
    mpfr_log2(ratio_strength, ratio_strength, MPFR_RNDN);
    
    // Minimum strength (weakest component)
    mpfr_min(min_strength, period_strength, modulus_strength, MPFR_RNDN);
    mpfr_min(min_strength, min_strength, ratio_strength, MPFR_RNDN);
    
    // Maximum strength (combined components)
    mpfr_add(max_strength, period_strength, modulus_strength, MPFR_RNDN);
    mpfr_add(max_strength, max_strength, ratio_strength, MPFR_RNDN);
    mpfr_div_ui(max_strength, max_strength, 3, MPFR_RNDN); // Average
    
    mpfr_clear(period_strength);
    mpfr_clear(modulus_strength);
    mpfr_clear(ratio_strength);
    
    return true;
}

int sha256_generate_alternative_constants(uint32_t *alt_constants,
                                         unsigned int count,
                                         const mod_geom_prog_t *progression,
                                         unsigned int security_target) {
    int generated = 0;
    
    for (unsigned int i = 0; i < count && i < 64; i++) {
        mpz_t term;
        mpz_init(term);
        
        // Generate term from geometric progression
        mod_geom_prog_term(term, progression, i);
        
        // Apply Z Framework enhancement
        mpfr_t enhanced_term;
        mpfr_init2(enhanced_term, MP_DPS);
        mod_geom_prog_geodesic_term(enhanced_term, progression, i, KAPPA_GEO_DEFAULT);
        
        // Convert to 32-bit constant
        double term_d = mpfr_get_d(enhanced_term, MPFR_RNDN);
        uint32_t constant = (uint32_t)(fmod(term_d, 4294967296.0)); // mod 2^32
        
        alt_constants[i] = constant;
        generated++;
        
        mpz_clear(term);
        mpfr_clear(enhanced_term);
    }
    
    return generated;
}

bool sha256_validate_against_progression(mpfr_t validation_score,
                                        const mod_geom_prog_t *progression,
                                        bool strict_mode) {
    double tolerance = strict_mode ? 0.05 : 0.2; // 5% or 20% tolerance
    
    int constants_within_bounds = sha256_test_constant_bounds(progression, tolerance);
    
    // Validation score = fraction of constants within bounds
    mpfr_set_d(validation_score, (double)constants_within_bounds / 64.0, MPFR_RNDN);
    
    return mpfr_get_d(validation_score, MPFR_RNDN) > (strict_mode ? 0.8 : 0.5);
}

int sha256_geodesic_enhanced_bounds(mpfr_t geodesic_bounds[][2],
                                   const mod_geom_prog_t *progression,
                                   double kappa_geo) {
    int computed_bounds = 0;
    
    for (int i = 0; i < 64; i++) {
        mpfr_t prog_term, enhanced_lower, enhanced_upper;
        mpfr_init2(prog_term, MP_DPS);
        mpfr_init2(enhanced_lower, MP_DPS);
        mpfr_init2(enhanced_upper, MP_DPS);
        
        // Compute geodesic-enhanced progression term
        mod_geom_prog_geodesic_term(prog_term, progression, i, kappa_geo);
        
        // Apply Z Framework enhancement to bounds
        mpfr_t enhancement_factor;
        mpfr_init2(enhancement_factor, MP_DPS);
        
        // Enhancement based on Z Framework principles
        mpfr_set_d(enhancement_factor, KAPPA_STAR_DEFAULT, MPFR_RNDN);
        mpfr_pow_ui(enhancement_factor, enhancement_factor, i + 1, MPFR_RNDN);
        
        // Enhanced bounds
        mpfr_mul(enhanced_lower, prog_term, enhancement_factor, MPFR_RNDN);
        mpfr_mul_d(enhanced_lower, enhanced_lower, 0.9, MPFR_RNDN);
        
        mpfr_mul(enhanced_upper, prog_term, enhancement_factor, MPFR_RNDN);
        mpfr_mul_d(enhanced_upper, enhanced_upper, 1.1, MPFR_RNDN);
        
        mpfr_set(geodesic_bounds[i][0], enhanced_lower, MPFR_RNDN);
        mpfr_set(geodesic_bounds[i][1], enhanced_upper, MPFR_RNDN);
        
        computed_bounds++;
        
        mpfr_clear(prog_term);
        mpfr_clear(enhanced_lower);
        mpfr_clear(enhanced_upper);
        mpfr_clear(enhancement_factor);
    }
    
    return computed_bounds;
}