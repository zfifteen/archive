/**
 * @file loglog_mpfr.h
 * @brief Arbitrary-precision log(log(x)) computation using GMP/MPFR
 *
 * This library provides a clean, self-contained implementation of the
 * double-logarithm function log(log(x)) for arbitrary-precision inputs.
 *
 * Requirements:
 * - C99 standard
 * - GMP library for arbitrary-precision integers
 * - MPFR library for arbitrary-precision floating-point
 *
 * Non-goals:
 * - No double, long double, or hardware floats
 * - No alternate backends or runtime fallbacks
 */

#ifndef LOGLOG_MPFR_H
#define LOGLOG_MPFR_H

#include <gmp.h>
#include <mpfr.h>

/**
 * @brief Compute log(log(x)) for an arbitrary-precision real input
 *
 * @param result Output parameter for log(log(x))
 * @param x Input value (must be > 1 for real result)
 * @param prec Precision in bits for intermediate and final computation
 * @param rnd Rounding mode for MPFR operations
 *
 * @return MPFR ternary value indicating rounding direction:
 *         - negative if result < exact value
 *         - zero if result == exact value
 *         - positive if result > exact value
 *
 * @note Behavior for x <= 1:
 *       - For 0 < x < 1: log(x) < 0, so log(log(x)) is undefined (NaN)
 *       - For x == 1: log(1) == 0, so log(log(1)) = log(0) = -inf
 *       - For x <= 0: log(x) is undefined (NaN)
 */
int loglog_mpfr_real(mpfr_t result, const mpfr_t x, mpfr_prec_t prec, mpfr_rnd_t rnd);

/**
 * @brief Compute log(log(n)) for an arbitrary-precision integer input
 *
 * This function converts the integer to MPFR format and computes log(log(n)).
 *
 * @param result Output parameter for log(log(n))
 * @param n Input integer value (must be >= 2 for real result)
 * @param prec Precision in bits for computation
 * @param rnd Rounding mode for MPFR operations
 *
 * @return MPFR ternary value (see loglog_mpfr_real)
 *
 * @note For n < 2, the result will be NaN or -inf as described above
 */
int loglog_mpfr_int(mpfr_t result, const mpz_t n, mpfr_prec_t prec, mpfr_rnd_t rnd);

/**
 * @brief Initialize an MPFR variable with specified precision
 *
 * Helper function to initialize and allocate memory for an MPFR variable.
 *
 * @param var The MPFR variable to initialize
 * @param prec Precision in bits
 */
void loglog_mpfr_init(mpfr_t var, mpfr_prec_t prec);

/**
 * @brief Clear and free memory for an MPFR variable
 *
 * @param var The MPFR variable to clear
 */
void loglog_mpfr_clear(mpfr_t var);

/**
 * @brief Get version information for the library
 *
 * @return Version string in format "major.minor.patch"
 */
const char* loglog_mpfr_version(void);

#endif /* LOGLOG_MPFR_H */
