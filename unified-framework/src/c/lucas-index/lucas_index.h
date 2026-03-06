/**
 * @file lucas_index.h
 * @brief Lucas Index System (LIS) — Demonstration API
 * @author Unified Framework Team
 * @version 1.0
 *
 * Overview
 * --------
 * Proof of Concept (PoC): this header declares a small demonstration API for
 * a light‑weight Lucas/Fibonacci probable‑prime pre‑filter in front of MR.
 * It reduces the number of MR calls a typical prime‑search pipeline would
 * perform compared to a wheel‑210 presieve alone.
 *
 * Baseline semantics
 * ------------------
 * The benchmark baseline used throughout is a modern, realistic presieve:
 *   - wheel-210 (coprime to 2·3·5·7)
 * It represents the number of candidates that a reasonable implementation
 * would forward to MR after eliminating obvious composites. The demo measures
 * MR calls after Lucas filtering and reports the ratio vs this baseline. Higher
 * reduction means fewer MR calls than baseline (i.e., better).
 *
 * Important
 * ---------
 * - The demo focuses on MR-call savings, not on implementing a production-grade
 *   prime enumerator. For small inputs, printed “reference” values (e.g., PNT or
 *   Dusart estimates) are contextual estimates and are not used for performance
 *   metrics.
 */

#ifndef LUCAS_INDEX_H
#define LUCAS_INDEX_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/**
 * @brief Lucas-index configuration parameters
 */
typedef struct {
    int64_t  P;              ///< Lucas sequence parameter P (signed)
    int64_t  Q;              ///< Lucas sequence parameter Q (signed)
    uint64_t modulus;        ///< Modulus for finite field operations
    uint64_t search_bound;   ///< Upper bound for search operations
    double   reduction_factor; ///< Desired reduction threshold (optional; default uses baseline-only goal)
} lucas_index_config_t;

/**
 * @brief Lucas-index search result
 */
typedef struct {
    uint64_t prime_candidate;   ///< Candidate prime found
    uint64_t lucas_index;       ///< Corresponding Lucas index
    uint64_t iterations;        ///< Number of iterations required
    double efficiency_ratio;    ///< Iterations vs baseline (wheel-210). Lower is better.
    uint64_t baseline_wheel210; ///< Count of baseline (wheel-210) candidates considered
    bool is_verified_prime;     ///< Whether candidate was verified as prime
} lucas_search_result_t;

/**
 * @brief Return codes for Lucas-index operations
 */
typedef enum {
    LUCAS_SUCCESS = 0,
    LUCAS_ERROR_INVALID_PARAMS,
    LUCAS_ERROR_OVERFLOW,
    LUCAS_ERROR_NOT_FOUND,
    LUCAS_ERROR_MEMORY
} lucas_error_t;

/**
 * @brief Initialize Lucas-index configuration with default parameters
 * @param config Pointer to configuration structure to initialize
 * @return LUCAS_SUCCESS on success, error code otherwise
 */
lucas_error_t lucas_index_init(lucas_index_config_t *config);

/**
 * @brief Compute nth Lucas number modulo m
 * @param n Index of Lucas number to compute
 * @param P Lucas sequence parameter P
 * @param Q Lucas sequence parameter Q
 * @param m Modulus for computation
 * @return nth Lucas number mod m
 */
uint64_t lucas_number_mod(uint64_t n, int64_t P, int64_t Q, uint64_t m);

/**
 * @brief Find nth prime using Lucas-index addressing
 * @param n Index of prime to find (1-indexed)
 * @param config Lucas-index configuration
 * @param result Pointer to store search result
 * @return LUCAS_SUCCESS on success, error code otherwise
 */
lucas_error_t lucas_find_nth_prime(uint64_t n, const lucas_index_config_t *config, 
                                  lucas_search_result_t *result);

/**
 * @brief Invert prime to find its index using Lucas addressing
 * @param prime Prime number to invert
 * @param config Lucas-index configuration  
 * @param result Pointer to store search result
 * @return LUCAS_SUCCESS on success, error code otherwise
 */
lucas_error_t lucas_invert_prime(uint64_t prime, const lucas_index_config_t *config,
                                lucas_search_result_t *result);

/**
 * @brief Benchmark Lucas-index performance against standard Z5D
 * @param start_n Starting prime index for benchmark
 * @param end_n Ending prime index for benchmark
 * @param config Lucas-index configuration
 * @param reduction_achieved Pointer to store achieved reduction factor
 * @return LUCAS_SUCCESS on success, error code otherwise
 */
lucas_error_t lucas_benchmark_performance(uint64_t start_n, uint64_t end_n,
                                        const lucas_index_config_t *config,
                                        double *reduction_achieved);

/* (Removed) Z5D validation helpers: the demo is LIS-only now. */

/**
 * @brief Print Lucas-index configuration and status
 * @param config Configuration to display
 */
void lucas_print_config(const lucas_index_config_t *config);

/**
 * @brief Print Lucas search result details
 * @param result Search result to display
 */
void lucas_print_result(const lucas_search_result_t *result);

#endif /* LUCAS_INDEX_H */
