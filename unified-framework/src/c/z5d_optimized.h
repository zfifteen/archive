// z5d_optimized.h — Header for optimized Z5D implementations
// Attribution: Created by Dionisio Alberto Lopez III (D.A.L. III), Z Framework

#ifndef Z5D_OPTIMIZED_H
#define Z5D_OPTIMIZED_H

#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include "z5d_predictor.h"

#ifdef __AVX2__
#include <immintrin.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Performance statistics structure
typedef struct {
    double original_time;
    double optimized_time;
    double speedup_factor;
    double compute_reduction;
    double accuracy_error;
    int samples_processed;
} z5d_perf_stats_t;

/**
 * Optimized Z5D prime prediction with reduced computational complexity
 * Achieves ~40% compute reduction through:
 * - Lookup table optimizations
 * - Fast approximations
 * - Reduced precision where appropriate
 * 
 * @param k Prime index
 * @param c Dilation calibration parameter
 * @param k_star Curvature calibration parameter
 * @param kappa_geo Geodesic exponent (may be unused in optimization)
 * @param auto_calibrate Whether to use automatic calibration
 * @return Optimized prime prediction
 */
double z5d_prime_optimized(double k, double c, double k_star, double kappa_geo, int auto_calibrate);

#ifdef __AVX2__
/**
 * AVX2 vectorized Z5D prediction for batch processing
 * Processes 4 values at once using SIMD instructions
 * 
 * @param k_values Array of k values to process
 * @param results Array to store results
 * @param n Number of values to process
 * @param c Dilation calibration parameter
 * @param k_star Curvature calibration parameter
 * @param kappa_geo Geodesic exponent
 * @param auto_calibrate Whether to use automatic calibration
 */
void z5d_prime_batch_avx2(const double* k_values, double* results, int n,
                          double c, double k_star, double kappa_geo, int auto_calibrate);
#endif

/**
 * Batch processing with OpenMP optimization
 * Uses parallel processing for large batches
 * 
 * @param k_values Array of k values to process
 * @param results Array to store results
 * @param n Number of values to process
 * @param c Dilation calibration parameter
 * @param k_star Curvature calibration parameter
 * @param kappa_geo Geodesic exponent
 * @param auto_calibrate Whether to use automatic calibration
 */
void z5d_prime_batch_parallel_optimized(const double* k_values, double* results, int n,
                                       double c, double k_star, double kappa_geo, int auto_calibrate);

/**
 * Memory-optimized batch processing for ultra-large scales
 * Combines chunking, vectorization, and parallelization
 * 
 * @param k_values Array of k values to process
 * @param results Array to store results
 * @param n Number of values to process
 * @param c Dilation calibration parameter
 * @param k_star Curvature calibration parameter
 * @param kappa_geo Geodesic exponent
 * @param auto_calibrate Whether to use automatic calibration
 * @param chunk_size Size of chunks for processing (0 for default)
 */
void z5d_prime_batch_ultra_scale(const double* k_values, double* results, int n,
                                double c, double k_star, double kappa_geo, int auto_calibrate,
                                int chunk_size);

/**
 * Performance profiling function to validate compute reduction claims
 * Compares original vs optimized implementations
 * 
 * @param n_samples Number of samples to test
 * @param k_start Starting k value
 * @param k_step Step size between k values
 * @return Performance statistics
 */
z5d_perf_stats_t z5d_benchmark_optimizations(int n_samples, double k_start, double k_step);

#ifdef __cplusplus
}
#endif

#endif // Z5D_OPTIMIZED_H