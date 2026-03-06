#ifndef CRYPTO_ANALYSIS_H
#define CRYPTO_ANALYSIS_H

#include <mpfr.h>
#include <gmp.h>
#include <stdbool.h>
#include <stdint.h>
#include "modular_progressions.h"

/**
 * @file crypto_analysis.h
 * @brief Cryptographic analysis using modular geometric progressions
 * 
 * Implements cryptographic analysis applications including:
 * - Scalar analogy for Dual_EC_DRBG
 * - Modular geometric bounds for SHA-256 constants
 * - Z Framework applications to cryptographic primitives
 */

// SHA-256 constants (first 32 bits of fractional parts of cube roots of first 64 primes)
extern const uint32_t SHA256_K[64];

/**
 * Structure for cryptographic analysis parameters
 */
typedef struct {
    mod_geom_prog_t progression;  // Base modular geometric progression
    mpfr_t kappa_crypto;         // Cryptographic strength parameter
    mpz_t security_bound;        // Security parameter bound
    unsigned long rounds;        // Number of analysis rounds
} crypto_analysis_t;

/**
 * Initialize cryptographic analysis structure
 * @param analysis Pointer to analysis structure
 */
void crypto_analysis_init(crypto_analysis_t *analysis);

/**
 * Clear cryptographic analysis structure
 * @param analysis Pointer to analysis structure
 */
void crypto_analysis_clear(crypto_analysis_t *analysis);

/**
 * Analyze modular geometric progression for cryptographic strength
 * Uses Z Framework principles to evaluate security properties
 * @param analysis Analysis parameters
 * @param security_estimate Output security estimate
 * @return true if analysis successful, false otherwise
 */
bool crypto_analyze_strength(const crypto_analysis_t *analysis, mpfr_t security_estimate);

/**
 * Compute scalar analogy for Dual_EC_DRBG using modular geometric progressions
 * @param result Output scalar value
 * @param base_point Base elliptic curve point (simplified to mpz_t)
 * @param multiplier Scalar multiplier
 * @param modulus Field modulus
 */
void crypto_dual_ec_scalar_analogy(mpz_t result, const mpz_t base_point, 
                                   const mpz_t multiplier, const mpz_t modulus);

/**
 * Analyze SHA-256 round constants using modular geometric progression bounds
 * @param bounds Output array for computed bounds
 * @param round_index SHA-256 round index (0-63)
 * @param progression Modular geometric progression for analysis
 * @return true if bounds computed successfully
 */
bool crypto_sha256_bounds_analysis(mpfr_t *bounds, int round_index, 
                                   const mod_geom_prog_t *progression);

/**
 * Compute cryptographic period analysis using Z Framework
 * @param period_estimate Output period estimate
 * @param progression Progression to analyze
 * @param security_level Required security level in bits
 * @return true if period suitable for given security level
 */
bool crypto_period_analysis(mpfr_t period_estimate, const mod_geom_prog_t *progression,
                           unsigned int security_level);

/**
 * Generate cryptographically strong parameters using modular geometric progressions
 * @param base Output base parameter
 * @param ratio Output ratio parameter
 * @param modulus Output modulus parameter
 * @param security_bits Target security level in bits
 * @return true if strong parameters generated
 */
bool crypto_generate_strong_params(mpz_t base, mpz_t ratio, mpz_t modulus,
                                  unsigned int security_bits);

/**
 * Validate cryptographic parameters against known attacks
 * @param progression Progression to validate
 * @param security_level Required security level
 * @return true if parameters resist known attacks
 */
bool crypto_validate_security(const mod_geom_prog_t *progression, 
                              unsigned int security_level);

/**
 * Compute geodesic-enhanced cryptographic bounds
 * Applies Z Framework geodesic mapping to cryptographic analysis
 * @param lower_bound Output lower security bound
 * @param upper_bound Output upper security bound
 * @param progression Progression parameters
 * @param kappa_geo Geodesic exponent
 */
void crypto_geodesic_bounds(mpfr_t lower_bound, mpfr_t upper_bound,
                           const mod_geom_prog_t *progression, double kappa_geo);

#endif /* CRYPTO_ANALYSIS_H */