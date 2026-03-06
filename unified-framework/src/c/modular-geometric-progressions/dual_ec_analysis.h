#ifndef DUAL_EC_ANALYSIS_H
#define DUAL_EC_ANALYSIS_H

#include <mpfr.h>
#include <gmp.h>
#include <stdbool.h>
#include "modular_progressions.h"

/**
 * @file dual_ec_analysis.h
 * @brief Dual_EC_DRBG scalar analogy using modular geometric progressions
 * 
 * Implements scalar analysis analogous to Dual_EC_DRBG elliptic curve operations
 * using modular geometric progressions and Z Framework principles.
 */

/**
 * Structure representing Dual EC scalar state
 */
typedef struct {
    mpz_t state;           // Current state
    mpz_t generator;       // Generator point (scalar analogy)
    mpz_t multiplier;      // Secret multiplier
    mpz_t field_mod;       // Field modulus
    mod_geom_prog_t prog;  // Underlying geometric progression
} dual_ec_state_t;

/**
 * Initialize Dual EC scalar state
 * @param state Pointer to state structure
 */
void dual_ec_init(dual_ec_state_t *state);

/**
 * Clear Dual EC scalar state
 * @param state Pointer to state structure
 */
void dual_ec_clear(dual_ec_state_t *state);

/**
 * Set up Dual EC parameters with modular geometric progression base
 * @param state State structure
 * @param generator Generator value
 * @param multiplier Secret multiplier
 * @param field_mod Field modulus
 * @param prog_base Base for geometric progression
 * @param prog_ratio Ratio for geometric progression
 */
void dual_ec_setup(dual_ec_state_t *state, unsigned long generator,
                   unsigned long multiplier, unsigned long field_mod,
                   unsigned long prog_base, unsigned long prog_ratio);

/**
 * Perform one step of Dual EC scalar generation
 * Simulates: s_{i+1} = s_i * generator (mod field_mod)
 * With geometric progression enhancement
 * @param state State structure (modified)
 * @param output Output random value
 * @return true if generation successful
 */
bool dual_ec_generate(dual_ec_state_t *state, mpz_t output);

/**
 * Analyze predictability of Dual EC scalar sequence
 * Uses Z Framework geodesic analysis to detect patterns
 * @param state State structure
 * @param num_samples Number of samples to analyze
 * @param predictability_score Output predictability measure
 * @return true if analysis completed
 */
bool dual_ec_analyze_predictability(const dual_ec_state_t *state, 
                                    unsigned long num_samples,
                                    mpfr_t predictability_score);

/**
 * Compute correlation between Dual EC output and geometric progression
 * @param correlation Output correlation coefficient
 * @param state State structure
 * @param sequence_length Length of sequence to analyze
 * @return true if correlation computed successfully
 */
bool dual_ec_geometric_correlation(mpfr_t correlation, const dual_ec_state_t *state,
                                   unsigned long sequence_length);

/**
 * Test for backdoor vulnerabilities in Dual EC scalar analogy
 * @param state State structure
 * @param backdoor_detected Output backdoor detection flag
 * @param confidence Output confidence level
 * @return true if test completed
 */
bool dual_ec_backdoor_test(const dual_ec_state_t *state, bool *backdoor_detected,
                          mpfr_t confidence);

/**
 * Generate secure Dual EC parameters using Z Framework optimization
 * @param generator Output secure generator
 * @param multiplier Output secure multiplier  
 * @param field_mod Output field modulus
 * @param security_bits Target security level
 * @return true if secure parameters generated
 */
bool dual_ec_generate_secure_params(mpz_t generator, mpz_t multiplier,
                                    mpz_t field_mod, unsigned int security_bits);

/**
 * Validate Dual EC parameters against known vulnerabilities
 * @param generator Generator to validate
 * @param multiplier Multiplier to validate
 * @param field_mod Field modulus to validate
 * @return true if parameters are secure
 */
bool dual_ec_validate_params(const mpz_t generator, const mpz_t multiplier,
                            const mpz_t field_mod);

#endif /* DUAL_EC_ANALYSIS_H */