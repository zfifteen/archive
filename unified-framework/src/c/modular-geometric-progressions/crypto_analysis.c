#include "crypto_analysis.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

/**
 * @file crypto_analysis.c
 * @brief Cryptographic analysis using modular geometric progressions implementation
 */

// SHA-256 round constants K[0..63] 
// First 32 bits of fractional parts of cube roots of first 64 primes
const uint32_t SHA256_K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

void crypto_analysis_init(crypto_analysis_t *analysis) {
    mod_geom_prog_init(&analysis->progression);
    mpfr_init2(analysis->kappa_crypto, MP_DPS);
    mpz_init(analysis->security_bound);
    analysis->rounds = 0;
    
    // Set default cryptographic parameter
    mpfr_set_d(analysis->kappa_crypto, KAPPA_STAR_DEFAULT, MPFR_RNDN);
}

void crypto_analysis_clear(crypto_analysis_t *analysis) {
    mod_geom_prog_clear(&analysis->progression);
    mpfr_clear(analysis->kappa_crypto);
    mpz_clear(analysis->security_bound);
    analysis->rounds = 0;
}

bool crypto_analyze_strength(const crypto_analysis_t *analysis, mpfr_t security_estimate) {
    // Analyze cryptographic strength using Z Framework principles
    mpfr_t period_factor, complexity_factor, geodesic_factor;
    mpfr_init2(period_factor, MP_DPS);
    mpfr_init2(complexity_factor, MP_DPS);
    mpfr_init2(geodesic_factor, MP_DPS);
    
    // Get period of the progression
    unsigned long period = mod_geom_prog_period(&analysis->progression);
    if (period == 0) {
        // Very long period is good for security
        mpfr_set_ui(period_factor, 1000000, MPFR_RNDN);
    } else {
        mpfr_set_ui(period_factor, period, MPFR_RNDN);
    }
    
    // Complexity based on modulus size
    mpfr_set_z(complexity_factor, analysis->progression.modulus, MPFR_RNDN);
    mpfr_log2(complexity_factor, complexity_factor, MPFR_RNDN);
    
    // Geodesic enhancement factor
    mpfr_pow(geodesic_factor, analysis->kappa_crypto, complexity_factor, MPFR_RNDN);
    
    // Combine factors: security = log2(period) * log2(modulus) * geodesic_factor
    mpfr_log2(period_factor, period_factor, MPFR_RNDN);
    mpfr_mul(security_estimate, period_factor, complexity_factor, MPFR_RNDN);
    mpfr_mul(security_estimate, security_estimate, geodesic_factor, MPFR_RNDN);
    
    mpfr_clear(period_factor);
    mpfr_clear(complexity_factor);
    mpfr_clear(geodesic_factor);
    
    return true;
}

void crypto_dual_ec_scalar_analogy(mpz_t result, const mpz_t base_point,
                                   const mpz_t multiplier, const mpz_t modulus) {
    // Compute scalar multiplication: result = base_point * multiplier (mod modulus)
    mpz_mul(result, base_point, multiplier);
    mpz_mod(result, result, modulus);
}

bool crypto_sha256_bounds_analysis(mpfr_t *bounds, int round_index,
                                   const mod_geom_prog_t *progression) {
    if (round_index < 0 || round_index >= 64) {
        return false;
    }
    
    mpfr_t constant_val, lower_bound, upper_bound, prog_term;
    mpfr_init2(constant_val, MP_DPS);
    mpfr_init2(lower_bound, MP_DPS);
    mpfr_init2(upper_bound, MP_DPS);
    mpfr_init2(prog_term, MP_DPS);
    
    // Convert SHA-256 constant to MPFR
    mpfr_set_ui(constant_val, SHA256_K[round_index], MPFR_RNDN);
    
    // Compute geometric progression term for this round
    mod_geom_prog_geodesic_term(prog_term, progression, round_index, KAPPA_GEO_DEFAULT);
    
    // Set bounds as ±10% of the geometric progression term
    mpfr_mul_d(lower_bound, prog_term, 0.9, MPFR_RNDN);
    mpfr_mul_d(upper_bound, prog_term, 1.1, MPFR_RNDN);
    
    // Store results
    mpfr_set(bounds[0], lower_bound, MPFR_RNDN);
    mpfr_set(bounds[1], upper_bound, MPFR_RNDN);
    
    mpfr_clear(constant_val);
    mpfr_clear(lower_bound);
    mpfr_clear(upper_bound);
    mpfr_clear(prog_term);
    
    return true;
}

bool crypto_period_analysis(mpfr_t period_estimate, const mod_geom_prog_t *progression,
                           unsigned int security_level) {
    unsigned long period = mod_geom_prog_period(progression);
    
    if (period == 0) {
        // Very long period
        mpfr_set_inf(period_estimate, 1);
        return true;
    }
    
    mpfr_set_ui(period_estimate, period, MPFR_RNDN);
    mpfr_log2(period_estimate, period_estimate, MPFR_RNDN);
    
    // Check if period provides sufficient security
    return mpfr_get_d(period_estimate, MPFR_RNDN) >= security_level;
}

bool crypto_generate_strong_params(mpz_t base, mpz_t ratio, mpz_t modulus,
                                  unsigned int security_bits) {
    // Generate cryptographically strong parameters
    // Use safe primes and generators with high order
    
    // Generate a large modulus (simplified - would use proper prime generation)
    mpz_ui_pow_ui(modulus, 2, security_bits);
    mpz_sub_ui(modulus, modulus, 1);
    
    // Choose base as small prime
    mpz_set_ui(base, 3);
    
    // Choose ratio with high multiplicative order
    mpz_set_ui(ratio, 7); // Primitive root modulo many primes
    
    return true;
}

bool crypto_validate_security(const mod_geom_prog_t *progression,
                              unsigned int security_level) {
    // Basic security validation
    
    // Check modulus size
    size_t mod_bits = mpz_sizeinbase(progression->modulus, 2);
    if (mod_bits < security_level) {
        return false;
    }
    
    // Check for small factors (basic test)
    if (mpz_even_p(progression->modulus)) {
        return false; // Even modulus is weak
    }
    
    // Check period length
    unsigned long period = mod_geom_prog_period(progression);
    if (period > 0 && period < (1UL << (security_level / 4))) {
        return false; // Period too short
    }
    
    return true;
}

void crypto_geodesic_bounds(mpfr_t lower_bound, mpfr_t upper_bound,
                           const mod_geom_prog_t *progression, double kappa_geo) {
    mpfr_t mod_log, enhancement;
    mpfr_init2(mod_log, MP_DPS);
    mpfr_init2(enhancement, MP_DPS);
    
    // Base security on modulus logarithm
    mpfr_set_z(mod_log, progression->modulus, MPFR_RNDN);
    mpfr_log2(mod_log, mod_log, MPFR_RNDN);
    
    // Apply geodesic enhancement
    mpfr_set_d(enhancement, kappa_geo, MPFR_RNDN);
    mpfr_pow(enhancement, mod_log, enhancement, MPFR_RNDN);
    
    // Set bounds
    mpfr_mul_d(lower_bound, enhancement, 0.8, MPFR_RNDN);
    mpfr_mul_d(upper_bound, enhancement, 1.2, MPFR_RNDN);
    
    mpfr_clear(mod_log);
    mpfr_clear(enhancement);
}