/**
 * Specialized Test Exclusion Header (Issue #610)
 * 
 * Header file for the specialized test exclusion functionality
 * that enables 40% compute savings for RSA-like factorization candidates.
 */

#ifndef SPECIALIZED_EXCLUSION_H
#define SPECIALIZED_EXCLUSION_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Check if a number appears to be RSA-like (non-special form) based on size and characteristics
 * 
 * RSA numbers are specifically chosen to avoid special forms for security.
 * This function implements the detection logic mentioned in issue #610 for
 * RSA-260 analysis where factors are confirmed to be non-special forms.
 * 
 * @param n The candidate number to check
 * @param k The k-th prime index (indicates scale)
 * @return true if the candidate appears to be RSA-like (non-special form)
 */
bool is_rsa_like_candidate(uint64_t n, uint64_t k);

/**
 * Configuration structure for prime generation with specialized test exclusion
 */
typedef struct {
    uint64_t batch_size;
    uint64_t k_max;
    int threads;
    bool use_simd;
    bool verify_primes;
    bool detect_mersenne;
    bool exclude_specialized_tests;  ///< NEW: Skip special form tests for RSA-like candidates
    bool verbose;
} prime_gen_config_t;

/**
 * Batch generation result with exclusion statistics
 */
typedef struct {
    uint64_t* k_values;
    double* predictions;
    uint64_t* primes;
    bool* is_mersenne;
    uint64_t count;
    double generation_time;
    uint64_t total_candidates;
    double efficiency_ratio;
    uint64_t excluded_count;        ///< NEW: Number of candidates that had specialized tests excluded
    double compute_savings_percent; ///< NEW: Measured compute savings percentage
} batch_result_t;

/**
 * Performance metrics for specialized test exclusion
 */
typedef struct {
    uint64_t total_candidates_processed;
    uint64_t rsa_like_candidates;
    uint64_t specialized_tests_skipped;
    double time_with_exclusion;
    double time_without_exclusion;
    double compute_savings_percent;
    double search_space_reduction_percent;
} exclusion_metrics_t;

/**
 * Calculate performance metrics for the exclusion functionality
 * 
 * @param with_exclusion_time Time taken with exclusion enabled
 * @param without_exclusion_time Time taken with full specialized testing
 * @param candidates_processed Total number of candidates processed
 * @param excluded_count Number of candidates that had tests excluded
 * @return Populated metrics structure
 */
exclusion_metrics_t calculate_exclusion_metrics(
    double with_exclusion_time,
    double without_exclusion_time, 
    uint64_t candidates_processed,
    uint64_t excluded_count
);

/**
 * Validate that the exclusion functionality achieves the claimed 40% compute savings
 * 
 * @param metrics The metrics to validate
 * @return true if the savings are within the expected range (36.8% - 43.2% CI)
 */
bool validate_compute_savings(const exclusion_metrics_t* metrics);

#ifdef __cplusplus
}
#endif

#endif /* SPECIALIZED_EXCLUSION_H */