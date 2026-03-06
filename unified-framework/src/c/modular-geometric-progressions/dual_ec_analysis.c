#include "dual_ec_analysis.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

/**
 * @file dual_ec_analysis.c
 * @brief Dual_EC_DRBG scalar analogy implementation
 */

void dual_ec_init(dual_ec_state_t *state) {
    mpz_init(state->state);
    mpz_init(state->generator);
    mpz_init(state->multiplier);
    mpz_init(state->field_mod);
    mod_geom_prog_init(&state->prog);
}

void dual_ec_clear(dual_ec_state_t *state) {
    mpz_clear(state->state);
    mpz_clear(state->generator);
    mpz_clear(state->multiplier);
    mpz_clear(state->field_mod);
    mod_geom_prog_clear(&state->prog);
}

void dual_ec_setup(dual_ec_state_t *state, unsigned long generator,
                   unsigned long multiplier, unsigned long field_mod,
                   unsigned long prog_base, unsigned long prog_ratio) {
    mpz_set_ui(state->generator, generator);
    mpz_set_ui(state->multiplier, multiplier);
    mpz_set_ui(state->field_mod, field_mod);
    
    // Initialize geometric progression
    mod_geom_prog_set(&state->prog, prog_base, prog_ratio, field_mod, 100);
    
    // Set initial state
    mpz_set_ui(state->state, 1);
}

bool dual_ec_generate(dual_ec_state_t *state, mpz_t output) {
    // Simulate Dual EC generation: s_{i+1} = s_i * generator (mod field_mod)
    mpz_mul(state->state, state->state, state->generator);
    mpz_mod(state->state, state->state, state->field_mod);
    
    // Apply geometric progression enhancement
    mpz_t prog_enhancement;
    mpz_init(prog_enhancement);
    
    // Get current geometric progression term (using state value as index)
    unsigned long index = mpz_get_ui(state->state) % 1000; // Limit index
    mod_geom_prog_term(prog_enhancement, &state->prog, index);
    
    // Combine with state: output = state + prog_enhancement (mod field_mod)
    mpz_add(output, state->state, prog_enhancement);
    mpz_mod(output, output, state->field_mod);
    
    mpz_clear(prog_enhancement);
    return true;
}

bool dual_ec_analyze_predictability(const dual_ec_state_t *state,
                                    unsigned long num_samples,
                                    mpfr_t predictability_score) {
    // Analyze predictability by examining correlation with geometric progression
    mpfr_t correlation_sum, sample_count;
    mpfr_init2(correlation_sum, MP_DPS);
    mpfr_init2(sample_count, MP_DPS);
    
    // Simulate samples and check correlation
    dual_ec_state_t test_state = *state;
    mpz_t sample, expected;
    mpz_init(sample);
    mpz_init(expected);
    
    double total_correlation = 0.0;
    
    for (unsigned long i = 0; i < num_samples && i < 1000; i++) {
        dual_ec_generate(&test_state, sample);
        mod_geom_prog_term(expected, &state->prog, i);
        
        // Simple correlation measure
        double sample_d = mpz_get_d(sample);
        double expected_d = mpz_get_d(expected);
        
        if (expected_d > 0) {
            total_correlation += fabs(sample_d - expected_d) / expected_d;
        }
    }
    
    // Average correlation (lower means more predictable)
    mpfr_set_d(predictability_score, total_correlation / num_samples, MPFR_RNDN);
    
    mpfr_clear(correlation_sum);
    mpfr_clear(sample_count);
    mpz_clear(sample);
    mpz_clear(expected);
    
    return true;
}

bool dual_ec_geometric_correlation(mpfr_t correlation, const dual_ec_state_t *state,
                                   unsigned long sequence_length) {
    // Compute correlation coefficient between Dual EC output and geometric progression
    
    mpfr_t sum_xy, sum_x, sum_y, sum_x2, sum_y2, n_f;
    mpfr_init2(sum_xy, MP_DPS);
    mpfr_init2(sum_x, MP_DPS);
    mpfr_init2(sum_y, MP_DPS);
    mpfr_init2(sum_x2, MP_DPS);
    mpfr_init2(sum_y2, MP_DPS);
    mpfr_init2(n_f, MP_DPS);
    
    mpfr_set_ui(n_f, sequence_length, MPFR_RNDN);
    
    dual_ec_state_t test_state = *state;
    mpz_t dual_output, prog_term;
    mpz_init(dual_output);
    mpz_init(prog_term);
    
    // Compute correlation statistics
    for (unsigned long i = 0; i < sequence_length && i < 500; i++) {
        dual_ec_generate(&test_state, dual_output);
        mod_geom_prog_term(prog_term, &state->prog, i);
        
        mpfr_t x, y, x2, y2, xy;
        mpfr_init2(x, MP_DPS);
        mpfr_init2(y, MP_DPS);
        mpfr_init2(x2, MP_DPS);
        mpfr_init2(y2, MP_DPS);
        mpfr_init2(xy, MP_DPS);
        
        mpfr_set_z(x, dual_output, MPFR_RNDN);
        mpfr_set_z(y, prog_term, MPFR_RNDN);
        
        mpfr_mul(x2, x, x, MPFR_RNDN);
        mpfr_mul(y2, y, y, MPFR_RNDN);
        mpfr_mul(xy, x, y, MPFR_RNDN);
        
        mpfr_add(sum_x, sum_x, x, MPFR_RNDN);
        mpfr_add(sum_y, sum_y, y, MPFR_RNDN);
        mpfr_add(sum_x2, sum_x2, x2, MPFR_RNDN);
        mpfr_add(sum_y2, sum_y2, y2, MPFR_RNDN);
        mpfr_add(sum_xy, sum_xy, xy, MPFR_RNDN);
        
        mpfr_clear(x);
        mpfr_clear(y);
        mpfr_clear(x2);
        mpfr_clear(y2);
        mpfr_clear(xy);
    }
    
    // Compute Pearson correlation coefficient
    mpfr_t numerator, denom1, denom2, denominator;
    mpfr_init2(numerator, MP_DPS);
    mpfr_init2(denom1, MP_DPS);
    mpfr_init2(denom2, MP_DPS);
    mpfr_init2(denominator, MP_DPS);
    
    // numerator = n*sum_xy - sum_x*sum_y
    mpfr_mul(numerator, n_f, sum_xy, MPFR_RNDN);
    mpfr_mul(denom1, sum_x, sum_y, MPFR_RNDN);
    mpfr_sub(numerator, numerator, denom1, MPFR_RNDN);
    
    // denom1 = n*sum_x2 - sum_x^2
    mpfr_mul(denom1, n_f, sum_x2, MPFR_RNDN);
    mpfr_mul(denom2, sum_x, sum_x, MPFR_RNDN);
    mpfr_sub(denom1, denom1, denom2, MPFR_RNDN);
    
    // denom2 = n*sum_y2 - sum_y^2  
    mpfr_mul(denom2, n_f, sum_y2, MPFR_RNDN);
    mpfr_mul(denominator, sum_y, sum_y, MPFR_RNDN);
    mpfr_sub(denom2, denom2, denominator, MPFR_RNDN);
    
    // denominator = sqrt(denom1 * denom2)
    mpfr_mul(denominator, denom1, denom2, MPFR_RNDN);
    mpfr_sqrt(denominator, denominator, MPFR_RNDN);
    
    // correlation = numerator / denominator
    if (mpfr_cmp_ui(denominator, 0) != 0) {
        mpfr_div(correlation, numerator, denominator, MPFR_RNDN);
    } else {
        mpfr_set_ui(correlation, 0, MPFR_RNDN);
    }
    
    // Cleanup
    mpfr_clear(sum_xy);
    mpfr_clear(sum_x);
    mpfr_clear(sum_y);
    mpfr_clear(sum_x2);
    mpfr_clear(sum_y2);
    mpfr_clear(n_f);
    mpfr_clear(numerator);
    mpfr_clear(denom1);
    mpfr_clear(denom2);
    mpfr_clear(denominator);
    mpz_clear(dual_output);
    mpz_clear(prog_term);
    
    return true;
}

bool dual_ec_backdoor_test(const dual_ec_state_t *state, bool *backdoor_detected,
                          mpfr_t confidence) {
    // Test for potential backdoors by analyzing predictability patterns
    
    mpfr_t predictability;
    mpfr_init2(predictability, MP_DPS);
    
    // Analyze predictability over short sequence
    dual_ec_analyze_predictability(state, 100, predictability);
    
    // High predictability suggests potential backdoor
    double pred_value = mpfr_get_d(predictability, MPFR_RNDN);
    
    if (pred_value < 0.1) { // Very predictable
        *backdoor_detected = true;
        mpfr_set_d(confidence, 0.9, MPFR_RNDN);
    } else if (pred_value < 0.3) { // Somewhat predictable
        *backdoor_detected = true;
        mpfr_set_d(confidence, 0.6, MPFR_RNDN);
    } else {
        *backdoor_detected = false;
        mpfr_set_d(confidence, 0.8, MPFR_RNDN);
    }
    
    mpfr_clear(predictability);
    return true;
}

bool dual_ec_generate_secure_params(mpz_t generator, mpz_t multiplier,
                                    mpz_t field_mod, unsigned int security_bits) {
    // Generate secure parameters for Dual EC scalar analogy
    
    // Use a large prime modulus
    mpz_ui_pow_ui(field_mod, 2, security_bits);
    mpz_sub_ui(field_mod, field_mod, 1);
    
    // Choose generator with high multiplicative order
    mpz_set_ui(generator, 5); // Often a primitive root
    
    // Choose multiplier coprime to modulus
    mpz_set_ui(multiplier, 7);
    
    return true;
}

bool dual_ec_validate_params(const mpz_t generator, const mpz_t multiplier,
                            const mpz_t field_mod) {
    // Basic parameter validation
    
    // Check for small values that could be weak
    if (mpz_cmp_ui(generator, 2) < 0 || mpz_cmp_ui(multiplier, 2) < 0) {
        return false;
    }
    
    // Check that parameters are less than modulus
    if (mpz_cmp(generator, field_mod) >= 0 || mpz_cmp(multiplier, field_mod) >= 0) {
        return false;
    }
    
    // Check that modulus is odd (basic primality indication)
    if (mpz_even_p(field_mod)) {
        return false;
    }
    
    return true;
}