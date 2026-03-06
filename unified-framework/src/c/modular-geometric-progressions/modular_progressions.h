#ifndef MODULAR_PROGRESSIONS_H
#define MODULAR_PROGRESSIONS_H

#include <mpfr.h>
#include <gmp.h>
#include <stdbool.h>

/**
 * @file modular_progressions.h
 * @brief Core modular geometric progression functions
 * 
 * Implements modular geometric progressions following Z Framework principles.
 * Uses GMP and MPFR for high-precision calculations with 256-bit precision.
 */

// Precision settings following Z Framework standards
#define MP_DPS 256
#define KAPPA_GEO_DEFAULT 0.3
#define KAPPA_STAR_DEFAULT 0.04449

/**
 * Structure representing a modular geometric progression
 */
typedef struct {
    mpz_t base;         // Base value a
    mpz_t ratio;        // Common ratio r  
    mpz_t modulus;      // Modulus m
    unsigned long terms; // Number of terms
} mod_geom_prog_t;

/**
 * Initialize a modular geometric progression structure
 * @param prog Pointer to progression structure
 */
void mod_geom_prog_init(mod_geom_prog_t *prog);

/**
 * Clear and free a modular geometric progression structure
 * @param prog Pointer to progression structure
 */
void mod_geom_prog_clear(mod_geom_prog_t *prog);

/**
 * Set parameters for modular geometric progression
 * @param prog Progression structure
 * @param base Base value a
 * @param ratio Common ratio r
 * @param modulus Modulus m
 * @param terms Number of terms
 */
void mod_geom_prog_set(mod_geom_prog_t *prog, unsigned long base, 
                       unsigned long ratio, unsigned long modulus, 
                       unsigned long terms);

/**
 * Compute the nth term of a modular geometric progression
 * Result: a * r^n (mod m)
 * @param result Output for nth term
 * @param prog Progression parameters
 * @param n Term index (0-based)
 */
void mod_geom_prog_term(mpz_t result, const mod_geom_prog_t *prog, unsigned long n);

/**
 * Compute sum of first n terms of modular geometric progression
 * Uses Z Framework geodesic principles for optimization
 * @param result Output for sum
 * @param prog Progression parameters  
 * @param n Number of terms to sum
 */
void mod_geom_prog_sum(mpz_t result, const mod_geom_prog_t *prog, unsigned long n);

/**
 * Find period of modular geometric progression
 * @param prog Progression parameters
 * @return Period length, or 0 if no period found within reasonable bounds
 */
unsigned long mod_geom_prog_period(const mod_geom_prog_t *prog);

/**
 * Check if a value appears in the modular geometric progression
 * @param prog Progression parameters
 * @param value Value to search for
 * @param max_terms Maximum terms to check
 * @return Index where value appears, or -1 if not found
 */
long mod_geom_prog_contains(const mod_geom_prog_t *prog, const mpz_t value, 
                           unsigned long max_terms);

/**
 * Compute geodesic-enhanced modular geometric progression term
 * Applies Z Framework geodesic mapping with kappa parameter
 * @param result Output for enhanced term
 * @param prog Progression parameters
 * @param n Term index
 * @param kappa_geo Geodesic exponent (default: 0.3)
 */
void mod_geom_prog_geodesic_term(mpfr_t result, const mod_geom_prog_t *prog, 
                                 unsigned long n, double kappa_geo);

/**
 * Generate terms of modular geometric progression with Z Framework optimization
 * @param terms Array to store computed terms
 * @param prog Progression parameters
 * @param count Number of terms to generate
 */
void mod_geom_prog_generate_terms(mpz_t *terms, const mod_geom_prog_t *prog, 
                                  unsigned long count);

#endif /* MODULAR_PROGRESSIONS_H */