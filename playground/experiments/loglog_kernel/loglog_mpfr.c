/**
 * @file loglog_mpfr.c
 * @brief Implementation of arbitrary-precision log(log(x)) computation
 */

#include "loglog_mpfr.h"

#define LOGLOG_VERSION "1.0.0"

int loglog_mpfr_real(mpfr_t result, const mpfr_t x, mpfr_prec_t prec, mpfr_rnd_t rnd) {
    mpfr_t temp;
    int ret;
    
    /* Initialize temporary variable with specified precision */
    mpfr_init2(temp, prec);
    
    /* Compute log(x) */
    mpfr_log(temp, x, rnd);
    
    /* Compute log(log(x)) */
    ret = mpfr_log(result, temp, rnd);
    
    /* Clean up */
    mpfr_clear(temp);
    
    /* Return the ternary value from the final operation */
    return ret;
}

int loglog_mpfr_int(mpfr_t result, const mpz_t n, mpfr_prec_t prec, mpfr_rnd_t rnd) {
    mpfr_t x;
    int ret;
    
    /* Initialize temporary MPFR variable */
    mpfr_init2(x, prec);
    
    /* Convert integer to MPFR */
    mpfr_set_z(x, n, rnd);
    
    /* Compute log(log(x)) */
    ret = loglog_mpfr_real(result, x, prec, rnd);
    
    /* Clean up */
    mpfr_clear(x);
    
    return ret;
}

void loglog_mpfr_init(mpfr_t var, mpfr_prec_t prec) {
    mpfr_init2(var, prec);
}

void loglog_mpfr_clear(mpfr_t var) {
    mpfr_clear(var);
}

const char* loglog_mpfr_version(void) {
    return LOGLOG_VERSION;
}
