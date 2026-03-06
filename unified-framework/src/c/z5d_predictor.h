/**
 * Z5D Prime Predictor - C Implementation (Compilation-Fixed v1.4)
 * =====================================
 *
 * Advanced Z Framework with 5D curvature proxy for superior prime prediction.
 * Implements the unified-framework's normalization principles Z = A(B/c).
 *
 * Fixes (v1.4):
 * - Removed Python mpmath artifact ('mpf_to_double'); fixed d_term guard to ln_pnt <=0.0
 * - Ensured pure double precision; added explicit math.h include
 *
 * @file z5d_predictor.h
 * @author Unified Framework Team (Compilation-Fixed by Big D)
 * @version 1.4 (Compilation-Fixed)
 */

#ifndef Z5D_PREDICTOR_H
#define Z5D_PREDICTOR_H

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <float.h>  /* FIX v1.4: For DBL_MAX, isfinite */
#include "z_framework_params.h"  /* Standardized parameters from Z Framework */

#ifdef __cplusplus
extern "C" {
#endif

/* Mathematical constants - now using Z Framework standardized values */
#define Z5D_E_SQUARED   ZF_E_SQUARED       /* e^2 */
#define Z5D_E_FOURTH    ZF_E_FOURTH        /* e^4 */
#define Z5D_GOLDEN_PHI  ZF_GOLDEN_PHI      /* Golden ratio φ */
#define Z5D_PI          ZF_PI              /* π */
#define Z5D_BOOTSTRAP_RESAMPLES ZF_BOOTSTRAP_RESAMPLES_DEFAULT  /* From params.py */

/* Default calibration parameters - synchronized with src/core/params.py */
#define Z5D_DEFAULT_C           ZF_Z5D_C_CALIBRATED     /* -0.00247 */
#define Z5D_DEFAULT_K_STAR      ZF_KAPPA_STAR_DEFAULT   /* 0.04449 - KEY PARAMETER */
#define Z5D_DEFAULT_KAPPA_GEO   ZF_KAPPA_GEO_DEFAULT    /* 0.3 */

/* Bounds from params.py */
#define Z5D_MIN_KAPPA_GEO  ZF_MIN_KAPPA_GEO    /* 0.05 */
#define Z5D_MAX_KAPPA_GEO  ZF_MAX_KAPPA_GEO    /* 10.0 */

/* Scale-specific calibration thresholds - synchronized with params.py */
#define Z5D_SCALE_MEDIUM_MAX     1e7
#define Z5D_SCALE_LARGE_MAX      ZF_K_SCALE_THRESHOLD_HIGH   /* 1e10 from params.py */
#define Z5D_SCALE_ULTRA_MAX      ZF_K_SCALE_THRESHOLD_ULTRA  /* 1e12 from params.py */

/* Precision thresholds - using framework standards */
#define Z5D_MIN_K               ZF_MIN_K_NTH                 /* 2.0 from params.py */
#define Z5D_PRECISION_EPSILON   ZF_PRECISION_SCALE_THRESHOLD_HIGH  /* 1e-15 from params.py */
#define Z5D_LARGE_K_THRESHOLD   ZF_K_SCALE_THRESHOLD_HIGH    /* 1e10 from params.py */

/* Error codes */
#define Z5D_SUCCESS            0
#define Z5D_ERROR_INVALID_K   -1
#define Z5D_ERROR_OVERFLOW    -2
#define Z5D_ERROR_UNDERFLOW   -3
#define Z5D_ERROR_DOMAIN      -4
#define Z5D_ERROR_INVALID_KAPPA_GEO -5

typedef struct {
    double c;
    double k_star;
    double kappa_geo_factor;
} z5d_calibration_t;

typedef struct {
    double prediction;
    double pnt_base;
    double d_term;
    double e_term;
    double curvature_proxy;
    double c_used;
    double k_star_used;
    double kappa_geo_used;
    int error_code;
} z5d_result_t;

/* Function prototypes */

/**
 * Get optimal calibration based on scale
 */
z5d_calibration_t z5d_get_optimal_calibration(double k);

/**
 * Validate k value
 */
int z5d_validate_k(double k);

/**
 * Validate kappa_geo
 */
int z5d_validate_kappa_geo(double kappa_geo);

/**
 * Compute base PNT prime estimate
 */
double z5d_base_pnt_prime(double k);

/**
 * Compute dilation term d(k) (FIX v1.4: Pure double, ln_pnt <=0 guard)
 */
static inline double z5d_d_term(double ln_pnt, double e_fourth) {
    if (ln_pnt <= 0.0) return 0.0;  /* FIX v1.4: No exp; direct guard for p <=1 */
    return pow(ln_pnt / e_fourth, 2.0);
}

/**
 * Compute curvature term e(k) (Inline)
 */
static inline double z5d_e_term(double k) {
    if (k < Z5D_MIN_K) return 0.0;
    double k2 = k * k;
    double denom = k * (k + 1.0) * (k + 2.0);
    return (k2 + k + 2.0) / denom;
}

/**
 * Compute 5D curvature proxy (Inline)
 */
static inline double compute_5d_curvature_proxy(double ln_k_plus1, double e_sq, double e_term, double kappa_geo) {
    return kappa_geo * (ln_k_plus1 / e_sq) * e_term;
}

/**
 * Main Z5D prime predictor function
 */
double z5d_prime(double k, double c, double k_star, double kappa_geo, int auto_calibrate);

/**
 * Extended Z5D prediction with detailed results
 */
int z5d_prime_extended(double k, double c, double k_star, double kappa_geo, int auto_calibrate, z5d_result_t* result);

/**
 * Validate Z5D accuracy against true prime values
 */
int z5d_validate_accuracy(const double* k_values, const double* true_primes,
                         int n_values, double c, double k_star, double kappa_geo, int auto_calibrate,
                         double* mean_relative_error, double* max_relative_error);

/**
 * Print Z5D formula and parameters information
 */
void z5d_print_formula_info(void);

/**
 * Get version string
 */
const char* z5d_get_version(void);

#ifdef __cplusplus
}
#endif

#endif /* Z5D_PREDICTOR_H */
