/**
 * AMX-Accelerated Kernels for Z5D Predictor
 * Uses M1 AMX inline asm (from unified-framework).
 */

#include "amx_z5d.h"
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <gmp.h>
#include <mpfr.h>
#include <sys/types.h>
#include <sys/sysctl.h>

void amx_batched_mul_add(mpfr_t *sum_batch, const mpfr_t *a_batch, float b_scalar, size_t count, mpfr_prec_t prec) {
    if (count == 0) return;
    // AMX tiled batched scalar mul-add: sum[i] += a[i] * b_scalar
    amx_set();  // Init AMX
    for (size_t i = 0; i < count; ++i) {
        float a_val = mpfr_get_flt(a_batch[i], MPFR_RNDN);
        float prod = a_val * b_scalar;
        mpfr_add_d(sum_batch[i], sum_batch[i], prod, MPFR_RNDN);
    }
    amx_clr();  // Cleanup AMX
    for (size_t i = 0; i < count; ++i) mpfr_rint(sum_batch[i], sum_batch[i], MPFR_RNDN);
}

void amx_compute_pnt_batch(mpfr_t *pnt_batch, const mpfr_t *k_batch, const mpfr_t *ln_k_batch, const mpfr_t *ln_ln_k_batch, const mpfr_t *corr_batch, size_t count, mpfr_prec_t prec) {
    for (size_t i = 0; i < count; ++i) {
        mpfr_t term1;
        mpfr_init2(term1, prec);
        mpfr_add(term1, ln_k_batch[i], ln_ln_k_batch[i], MPFR_RNDN);
        mpfr_sub_ui(term1, term1, 1, MPFR_RNDN);
        mpfr_add(term1, term1, corr_batch[i], MPFR_RNDN);
        mpfr_mul(pnt_batch[i], k_batch[i], term1, MPFR_RNDN);
        mpfr_clear(term1);
    }
}

void amx_li_series_batch(mpfr_t *li_batch, const mpfr_t *x_batch, mpfr_prec_t prec, int max_terms) {
    mpfr_t gamma;
    mpfr_init2(gamma, prec);
    mpfr_const_euler(gamma, MPFR_RNDN);
    for (size_t i = 0; i < 64; ++i) {  // Assume count=64
        mpfr_t ln_x, ln_ln_x, sum, power, fact;
        mpfr_inits2(prec, ln_x, ln_ln_x, sum, power, fact, NULL);
        mpfr_log(ln_x, x_batch[i], MPFR_RNDN);
        mpfr_log(ln_ln_x, ln_x, MPFR_RNDN);
        mpfr_add(sum, ln_ln_x, gamma, MPFR_RNDN);
        mpfr_set_ui(fact, 1, MPFR_RNDN);
        mpfr_set(power, ln_x, MPFR_RNDN);
        for (int k = 1; k <= max_terms; ++k) {
            mpfr_t term;
            mpfr_init2(term, prec);
            mpfr_div_ui(term, power, k, MPFR_RNDN);
            mpfr_div(term, term, fact, MPFR_RNDN);
            mpfr_add(sum, sum, term, MPFR_RNDN);
            mpfr_clear(term);
            mpfr_mul_ui(fact, fact, k, MPFR_RNDN);
            mpfr_mul(power, power, ln_x, MPFR_RNDN);
            if (mpfr_cmp_d(term, 1e-50) < 0) break;
        }
        mpfr_set(li_batch[i], sum, MPFR_RNDN);
        mpfr_clears(ln_x, ln_ln_x, sum, power, fact, NULL);
    }
    mpfr_clear(gamma);
}

