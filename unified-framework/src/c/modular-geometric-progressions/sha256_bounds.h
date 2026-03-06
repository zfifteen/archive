#ifndef SHA256_BOUNDS_H
#define SHA256_BOUNDS_H

#include <mpfr.h>
#include <gmp.h>
#include <stdbool.h>
#include <stdint.h>
#include "modular_progressions.h"

/**
 * @file sha256_bounds.h
 * @brief SHA-256 constant bounds analysis using modular geometric progressions
 * 
 * Analyzes SHA-256 round constants using modular geometric progression bounds
 * and Z Framework geodesic principles for cryptographic strength assessment.
 */

// SHA-256 round constants K[0..63]
// First 32 bits of fractional parts of cube roots of first 64 primes
extern const uint32_t SHA256_ROUND_CONSTANTS[64];

/**
 * Structure for SHA-256 bounds analysis
 */
typedef struct {
    mod_geom_prog_t base_progression;   // Base modular geometric progression
    mpfr_t analysis_precision;          // Analysis precision parameter
    mpz_t constant_bound;               // Upper bound for constants
    unsigned int round_count;           // Number of rounds to analyze
} sha256_bounds_t;

/**
 * Initialize SHA-256 bounds analysis structure
 * @param bounds Pointer to bounds structure
 */
void sha256_bounds_init(sha256_bounds_t *bounds);

/**
 * Clear SHA-256 bounds analysis structure  
 * @param bounds Pointer to bounds structure
 */
void sha256_bounds_clear(sha256_bounds_t *bounds);

/**
 * Analyze SHA-256 round constant using modular geometric progression
 * @param lower_bound Output lower bound
 * @param upper_bound Output upper bound
 * @param round_index Round index (0-63)
 * @param progression Geometric progression for analysis
 * @return true if bounds computed successfully
 */
bool sha256_analyze_round_constant(mpfr_t lower_bound, mpfr_t upper_bound,
                                   unsigned int round_index,
                                   const mod_geom_prog_t *progression);

/**
 * Compute modular geometric bounds for all SHA-256 constants
 * @param bounds_array Output array of bound pairs (lower, upper)
 * @param progression Progression parameters
 * @return Number of constants successfully analyzed
 */
int sha256_compute_all_bounds(mpfr_t bounds_array[][2], 
                              const mod_geom_prog_t *progression);

/**
 * Test if SHA-256 constants fit within geometric progression bounds
 * @param progression Progression to test against
 * @param tolerance Tolerance for bound checking
 * @return Number of constants within bounds
 */
int sha256_test_constant_bounds(const mod_geom_prog_t *progression, 
                               double tolerance);

/**
 * Analyze geometric structure of SHA-256 constants
 * Uses Z Framework principles to identify patterns
 * @param structure_score Output structural analysis score
 * @param progression Base progression for analysis
 * @param kappa_geo Geodesic exponent parameter
 * @return true if structure analysis completed
 */
bool sha256_analyze_geometric_structure(mpfr_t structure_score,
                                        const mod_geom_prog_t *progression,
                                        double kappa_geo);

/**
 * Compute cryptographic strength bounds for SHA-256 using geometric analysis
 * @param min_strength Output minimum strength estimate
 * @param max_strength Output maximum strength estimate  
 * @param progression Progression parameters
 * @return true if strength bounds computed
 */
bool sha256_crypto_strength_bounds(mpfr_t min_strength, mpfr_t max_strength,
                                   const mod_geom_prog_t *progression);

/**
 * Generate alternative SHA-256-like constants using geometric progressions
 * @param alt_constants Output array for alternative constants
 * @param count Number of constants to generate
 * @param progression Base progression
 * @param security_target Target security level
 * @return Number of constants generated
 */
int sha256_generate_alternative_constants(uint32_t *alt_constants,
                                         unsigned int count,
                                         const mod_geom_prog_t *progression,
                                         unsigned int security_target);

/**
 * Validate SHA-256 constants against geometric progression criteria
 * @param validation_score Output validation score
 * @param progression Progression for validation
 * @param strict_mode Use strict validation criteria
 * @return true if validation completed
 */
bool sha256_validate_against_progression(mpfr_t validation_score,
                                        const mod_geom_prog_t *progression,
                                        bool strict_mode);

/**
 * Compute geodesic-enhanced bounds for SHA-256 analysis
 * Applies Z Framework geodesic mapping to constant analysis
 * @param geodesic_bounds Output enhanced bounds array
 * @param progression Base progression
 * @param kappa_geo Geodesic exponent
 * @return Number of enhanced bounds computed
 */
int sha256_geodesic_enhanced_bounds(mpfr_t geodesic_bounds[][2],
                                   const mod_geom_prog_t *progression,
                                   double kappa_geo);

#endif /* SHA256_BOUNDS_H */