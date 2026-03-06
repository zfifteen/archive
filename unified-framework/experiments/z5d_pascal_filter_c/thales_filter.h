// Attribution: Created by Dionisio Alberto Lopez III (D.A.L. III), Z Framework
// Thales Gate: Header definitions for monotone-pruning filter

#ifndef THALES_FILTER_H
#define THALES_FILTER_H

#include <mpfr.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Counter types for metrics tracking
typedef enum {
    THALES_PASS = 0,
    THALES_DROP,
    MR_SAVED,
    TD_SAVED,
    COUNTER_COUNT
} thales_counter_t;

// Function declarations

/**
 * Initialize known primes storage for error envelope validation
 */
void thales_init_known_primes(void);

/**
 * Cleanup known primes storage
 */
void thales_cleanup_known_primes(void);

/**
 * Core Thales filter function implementing monotone-pruning gate
 * 
 * @param n Input candidate number
 * @param Delta_n Delta value for geodesic calculation  
 * @param counters Array of counters for metrics tracking
 * @param k_in Prime index k for Z5D prediction
 * @return 1 if passes filter, 0 if filtered out, -1 on error
 */
int thales_filter(mpfr_t n, mpfr_t Delta_n, unsigned long* counters, mpfr_t k_in);

/**
 * Compute bootstrap confidence intervals for metrics
 * 
 * @param values Array of metric values
 * @param n_values Number of values in array
 * @param ci_low Output parameter for lower CI bound
 * @param ci_high Output parameter for upper CI bound
 * @param alpha Significance level (e.g., 0.05 for 95% CI)
 */
void compute_bootstrap_ci(double* values, size_t n_values, double* ci_low, double* ci_high, 
                         double alpha);

/**
 * Generate comprehensive Thales metrics report
 * 
 * @param counters Array of counter values
 * @param total_tests Total number of tests performed
 * @param commit_sha Git commit SHA for reproducibility
 * @param seed Random seed used for testing
 */
void generate_thales_report(unsigned long* counters, size_t total_tests, 
                           const char* commit_sha, unsigned int seed);

// Constants from Z Framework parameters
#define THALES_MPFR_PREC 200         // dps=50 equivalent
#define THALES_KAPPA_GEO 0.3
#define THALES_K_STAR 0.04449
#define THALES_Z5D_C -0.00247
#define THALES_ERROR_ENVELOPE 0.0002  // 200 ppm
#define THALES_PHI ((1.0 + sqrt(5.0)) / 2.0)
#define THALES_TOL 1e-10
#define THALES_DELTA_MAX_GUARD 1e-50

#ifdef __cplusplus
}
#endif

#endif // THALES_FILTER_H