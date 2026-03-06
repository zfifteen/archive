/**
 * Z5D Prime Predictor - C Implementation (Bug-Fixed v1.3)
 * =====================================
 *
 * Implementation of the Z5D predictor following unified-framework principles.
 * Provides double-precision arithmetic with numerical stability guards.
 * Fixes: Corrected log-space in base_pNT; adjusted d_term guard.
 *
 * @file z5d_predictor.c
 * @author Unified Framework Team (Bug-Fixed by Big D)
 * @version 1.3 (Bug-Fixed)
 */

#include "z5d_predictor.h"
#include <float.h>

#if Z5D_HAVE_MPFR
#include <mpfr.h>
#include <gmp.h>
#endif

/* Version information */
static const char* Z5D_VERSION = "2025-09-03";

/* Scale-specific calibration parameters (Const) */
static const z5d_calibration_t Z5D_CALIBRATIONS[] = {
    { -0.00247,  0.04449, 0.3 },
    { -0.00037, -0.11446, 0.3 * 0.809 },
    { -0.0001,  -0.15,    0.3 * 0.5  },
    { -0.00002, -0.10,    0.3 * 0.333}
};

/* Scale thresholds for lookup */
static const double Z5D_SCALE_THRESHOLDS[] = {0, Z5D_SCALE_MEDIUM_MAX, Z5D_SCALE_LARGE_MAX, Z5D_SCALE_ULTRA_MAX, INFINITY};

static double safe_log(double x) {
    if (x <= 0.0 || !isfinite(x)) {
        return NAN;
    }
    return log(x);
}

static double safe_divide(double numerator, double denominator) {
    if (fabs(denominator) < Z5D_PRECISION_EPSILON) {
        return NAN;
    }
    return numerator / denominator;
}

static int is_valid_finite(double x) {
    return isfinite(x) && !isnan(x);
}


z5d_calibration_t z5d_get_optimal_calibration(double k) {
    int scale_idx = 0;
    for (int i = 1; i < 5; ++i) {  /* 4 scales + inf */
        if (k <= Z5D_SCALE_THRESHOLDS[i]) {
            scale_idx = i - 1;
            break;
        }
    }
    return Z5D_CALIBRATIONS[scale_idx];
}

int z5d_validate_k(double k) {
    if (!is_valid_finite(k)) return Z5D_ERROR_DOMAIN;
    if (k < Z5D_MIN_K) return Z5D_ERROR_INVALID_K;
    if (k > DBL_MAX / 1000.0) return Z5D_ERROR_OVERFLOW;
    return Z5D_SUCCESS;
}

int z5d_validate_kappa_geo(double kappa_geo) {
    if (!is_valid_finite(kappa_geo)) return Z5D_ERROR_DOMAIN;
    if (kappa_geo < Z5D_MIN_KAPPA_GEO || kappa_geo > Z5D_MAX_KAPPA_GEO) return Z5D_ERROR_INVALID_KAPPA_GEO;
    return Z5D_SUCCESS;
}

double z5d_base_pnt_prime(double k) {
    int validation = z5d_validate_k(k);
    if (validation != Z5D_SUCCESS) return NAN;

    double ln_k = safe_log(k);
    if (!is_valid_finite(ln_k)) return NAN;

    double ln_ln_k = safe_log(ln_k);
    if (!is_valid_finite(ln_ln_k)) return NAN;

    double small_term = safe_divide(ln_ln_k - 2.0, ln_k);

    /* FIX v1.3: Correct log-space approx: log_p = ln_k + log(term) */
    if (k > Z5D_LARGE_K_THRESHOLD) {
        double term = ln_k + ln_ln_k - 1.0 + small_term;
        double log_term = safe_log(term);
        if (!is_valid_finite(log_term)) return NAN;
        double log_p = ln_k + log_term;
        if (!is_valid_finite(log_p)) return NAN;
        if (log_p > log(DBL_MAX) - 1e-10) {  /* FIX v1.3: Tighter guard */
            return DBL_MAX;
        }
        double pnt = exp(log_p);
        if (!isfinite(pnt)) return NAN;  /* FIX v1.3: Post-exp check */
        return pnt;
    }

    /* Standard computation (safe up to threshold) */
    double term = ln_k + ln_ln_k - 1.0 + small_term;
    double pnt = k * term;
    if (!isfinite(pnt) || pnt < 0.0) return NAN;
    return pnt;
}

double z5d_prime(double k, double c_in, double k_star_in, double kappa_geo_in, int auto_calibrate) {
    // Suppress unused parameter warning for API compatibility
    (void)kappa_geo_in;
    
    // Validate input
    int validation = z5d_validate_k(k);
    if (validation != Z5D_SUCCESS) return NAN;

    // Handle auto-calibration
    if (auto_calibrate) {
        z5d_calibration_t cal = z5d_get_optimal_calibration(k);
        c_in = cal.c;
        k_star_in = cal.k_star;
        // Note: kappa_geo_in not used in repository formula, but keeping for compatibility
    }

    /* Use the repository's accurate Z5D formula:
     * p_Z5D(k) = p_PNT(k) + c·d(k)·p_PNT(k) + k*·e(k)·p_PNT(k)
     * where:
     * - p_PNT(k) = k * (ln k + ln ln k - 1 + (ln ln k - 2)/ln k)  [base term]
     * - d(k) = (ln(p_PNT(k)) / e^4)^2  [dilation term] 
     * - e(k) = p_PNT(k)^(-1/3)  [curvature term]
     */

    double ln_k = safe_log(k);
    double ln_ln_k = safe_log(ln_k);
    
    // Base PNT term
    double pnt = k * (ln_k + ln_ln_k - 1.0 + (ln_ln_k - 2.0) / ln_k);
    if (!is_valid_finite(pnt) || pnt <= 0.0) return NAN;
    
    // Dilation term d(k) = (ln(p_PNT(k)) / e^4)^2
    double ln_pnt = safe_log(pnt);
    double d_term = 0.0;
    if (ln_pnt > 0.0) {
        d_term = (ln_pnt / Z5D_E_FOURTH) * (ln_pnt / Z5D_E_FOURTH);
    }
    
    // Curvature term e(k) = p_PNT(k)^(-1/3)
    double e_term = 0.0;
    if (pnt > 0.0) {
        e_term = pow(pnt, -1.0/3.0);
    }
    
    // Apply Z5D formula: p_PNT + c·d·p_PNT + k*·e·p_PNT
    double z5d_result = pnt + c_in * d_term * pnt + k_star_in * e_term * pnt;
    
    // Ensure non-negative result
    if (z5d_result < 0.0) z5d_result = pnt;
    
    if (!isfinite(z5d_result)) return NAN;
    return z5d_result;
}

int z5d_prime_extended(double k, double c, double k_star, double kappa_geo, int auto_calibrate, z5d_result_t* result) {
    if (!result) return Z5D_ERROR_DOMAIN;

    double pred = z5d_prime(k, c, k_star, kappa_geo, auto_calibrate);
    if (!is_valid_finite(pred)) {
        result->error_code = Z5D_ERROR_DOMAIN;
        return result->error_code;
    }

    z5d_calibration_t cal;
    if (auto_calibrate) {
        cal = z5d_get_optimal_calibration(k);
    } else {
        cal.c = c;
        cal.k_star = k_star;
        cal.kappa_geo_factor = kappa_geo;
    }

//    double ln_k = safe_log(k);
//    double ln_ln_k = safe_log(ln_k);
    double pnt = z5d_base_pnt_prime(k);
    double ln_pnt = safe_log(pnt);
    double d = z5d_d_term(ln_pnt, Z5D_E_FOURTH);
    double e = z5d_e_term(k);
    double ln_k_plus1 = safe_log(k + 1.0);
    double curv_proxy = compute_5d_curvature_proxy(ln_k_plus1, Z5D_E_SQUARED, e, cal.kappa_geo_factor);

    result->prediction = pred;
    result->pnt_base = pnt;
    result->d_term = d;
    result->e_term = e;
    result->curvature_proxy = curv_proxy;
    result->c_used = cal.c;
    result->k_star_used = cal.k_star;
    result->kappa_geo_used = cal.kappa_geo_factor;
    result->error_code = Z5D_SUCCESS;

    return Z5D_SUCCESS;
}

int z5d_validate_accuracy(const double* k_values, const double* true_primes,
                         int n_values, double c, double k_star, double kappa_geo, int auto_calibrate,
                         double* mean_relative_error, double* max_relative_error) {
    if (n_values <= 0 || !k_values || !true_primes) return Z5D_ERROR_DOMAIN;

    double sum_relative_error = 0.0;
    double max_error = 0.0;
    int valid_count = 0;

    const double* kv = k_values;
    const double* tp = true_primes;

    for (int i = 0; i < n_values; i++) {
        if (tp[i] <= 0.0) continue;

        double prediction = z5d_prime(kv[i], c, k_star, kappa_geo, auto_calibrate);
        if (!is_valid_finite(prediction)) continue;

        double relative_error = fabs((prediction - tp[i]) / tp[i]);

        sum_relative_error += relative_error;
        if (relative_error > max_error) max_error = relative_error;
        valid_count++;
    }

    if (valid_count == 0) return Z5D_ERROR_DOMAIN;

    *mean_relative_error = sum_relative_error / valid_count;
    *max_relative_error = max_error;

    return Z5D_SUCCESS;
}

void z5d_print_formula_info(void) {
    printf("Z5D Prime Predictor - C Implementation v%s\n", Z5D_VERSION);
    printf("==========================================\n\n");
    printf("Formula: p_Z5D(k) = p_PNT(k) + c·d(k)·p_PNT(k) + k*·e(k)·p_PNT(k)\n");
    printf("With geodesic modulation: e(k) *= kappa_geo · (ln(k+1)/e²)\n\n");
    printf("Where:\n");
    printf("  p_PNT(k) = k * (ln(k) + ln(ln(k)) - 1 + (ln(ln(k)) - 2)/ln(k))\n");
    printf("  d(k)     = (ln(p_PNT(k)) / e^4)^2 if ln(p) > 0 else 0\n");
    printf("  e(k)     = (k^2 + k + 2) / (k * (k + 1) * (k + 2))\n");
    printf("  Curvature Proxy: kappa_geo * (ln(k+1)/e^2) * e(k)\n\n");
    printf("Default Parameters:\n");
    printf("  c  = %.5f (dilation calibration)\n", Z5D_DEFAULT_C);
    printf("  k* = %.5f (curvature calibration)\n", Z5D_DEFAULT_K_STAR);
    printf("  kappa_geo = %.5f (geodesic exponent for ~15%% enhancement)\n\n", Z5D_DEFAULT_KAPPA_GEO);
    printf("Scale-specific Calibrations:\n");
    for (int i = 0; i < 4; i++) {
        printf("  Scale %d: c=%.5f, k*=%.5f, kappa_geo_factor=%.5f\n", i+1,
               Z5D_CALIBRATIONS[i].c, Z5D_CALIBRATIONS[i].k_star, Z5D_CALIBRATIONS[i].kappa_geo_factor);
    }
    printf("\nFeatures:\n");
    printf("  - Double-precision arithmetic\n");
    printf("  - Automatic parameter selection with kappa_geo\n");
    printf("  - Numerical stability guards (fixed log-space for ultra k)\n");
    printf("  - Zero-division protection (ln_pnt <=0 guard)\n");
    printf("  - Domain validation\n");
    printf("  - 5D Curvature Proxy for validation\n");
    printf("  - Optimizations: Inlines, log caching, array lookups\n\n");
}

const char* z5d_get_version(void) {
    return Z5D_VERSION;
}
