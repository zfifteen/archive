// z5d_optimized.c — Optimized Z5D implementations for 40% compute reduction
// Attribution: Created by Dionisio Alberto Lopez III (D.A.L. III), Z Framework
//
// This file contains highly optimized versions of Z5D predictor functions
// specifically designed to achieve the 40% compute reduction target through:
// - Vectorized math operations
// - Lookup table optimizations
// - Fast approximations where appropriate
// - Reduced computational complexity

#include "z5d_optimized.h"
#include <math.h>

// Fast lookup tables for common logarithms (trade memory for speed)
#define LOG_TABLE_SIZE 1024
static double log_table[LOG_TABLE_SIZE];
static bool log_table_initialized = false;

// Fast lookup tables for power functions
#define POW_TABLE_SIZE 256
static double pow_table[POW_TABLE_SIZE];
static bool pow_table_initialized = false;

// Initialize lookup tables
static void init_lookup_tables(void) {
    if (!log_table_initialized) {
        for (int i = 0; i < LOG_TABLE_SIZE; i++) {
            double x = 1.0 + (double)i / LOG_TABLE_SIZE * 10.0; // Range 1-11
            log_table[i] = log(x);
        }
        log_table_initialized = true;
    }
    
    if (!pow_table_initialized) {
        for (int i = 0; i < POW_TABLE_SIZE; i++) {
            double x = (double)i / POW_TABLE_SIZE; // Range 0-1
            pow_table[i] = pow(x, -1.0/3.0);
        }
        pow_table_initialized = true;
    }
}

// Fast logarithm approximation using lookup table
static inline double fast_log(double x) {
    if (x <= 0.0) return -INFINITY;
    if (x <= 1.0) return log(x); // Use standard log for x <= 1
    if (x > 11.0) return log(x); // Use standard log for x > 11
    
    double index_f = (x - 1.0) / 10.0 * (LOG_TABLE_SIZE - 1);
    int index = (int)index_f;
    double frac = index_f - index;
    
    if (index >= LOG_TABLE_SIZE - 1) return log_table[LOG_TABLE_SIZE - 1];
    
    // Linear interpolation
    return log_table[index] + frac * (log_table[index + 1] - log_table[index]);
}

// Fast power approximation for x^(-1/3)
static inline double fast_pow_neg_third(double x) {
    if (x <= 0.0) return 0.0;
    if (x > 1.0) return pow(x, -1.0/3.0); // Use standard pow for large values
    
    double index_f = x * (POW_TABLE_SIZE - 1);
    int index = (int)index_f;
    double frac = index_f - index;
    
    if (index >= POW_TABLE_SIZE - 1) return pow_table[POW_TABLE_SIZE - 1];
    
    // Linear interpolation
    return pow_table[index] + frac * (pow_table[index + 1] - pow_table[index]);
}

// Optimized Z5D prediction with reduced computational complexity
double z5d_prime_optimized(double k, double c, double k_star, double kappa_geo, int auto_calibrate) {
    // Initialize lookup tables on first call
    init_lookup_tables();
    
    // Input validation (minimal for performance)
    if (k < 2.0) return 0.0;
    
    // Use optimized calibration for auto mode
    if (auto_calibrate) {
        if (k < 1e4) {
            c = -0.00247;
            k_star = 0.04449;
            kappa_geo = 0.3;
        } else if (k < 1e7) {
            c = -0.00037;
            k_star = -0.11446;
            kappa_geo = 0.24;
        } else {
            c = -0.0001;
            k_star = -0.15;
            kappa_geo = 0.15;
        }
    }
    
    // Fast logarithm computations
    double ln_k = fast_log(k);
    double ln_ln_k = fast_log(ln_k);
    
    // Optimized PNT base computation (reduced precision for speed)
    double pnt_base = k * ln_k; // Simplified base
    double pnt_correction = k * ln_ln_k / ln_k; // Simplified correction
    double pnt = pnt_base - k + pnt_correction;
    
    // Fast dilation term (simplified)
    double ln_pnt = fast_log(pnt);
    double d_term = ln_pnt * ln_pnt / (54.6 * 54.6); // e^4 ≈ 54.6
    
    // Fast curvature term using lookup table
    double e_term = fast_pow_neg_third(pnt / 1000.0) * 31.6; // Normalized and scaled
    
    // Final Z5D result with optimized computation
    double z5d_result = pnt + c * d_term * pnt + k_star * e_term * pnt;
    
    return z5d_result > 0.0 ? z5d_result : 0.0;
}

#ifdef __AVX2__
// AVX2 vectorized Z5D prediction for batch processing
void z5d_prime_batch_avx2(const double* k_values, double* results, int n,
                          double c, double k_star, double kappa_geo, int auto_calibrate) {
    init_lookup_tables();
    
    const int simd_width = 4;
    const int vectorized_n = (n / simd_width) * simd_width;
    
    // Process vectorized portion
    for (int i = 0; i < vectorized_n; i += simd_width) {
        __m256d k_vec = _mm256_loadu_pd(&k_values[i]);
        
        // Fast logarithm (approximation for vectorization)
        __m256d ln_k_vec = _mm256_set1_pd(0.0);
        __m256d ln_ln_k_vec = _mm256_set1_pd(0.0);
        
        // Extract values for scalar processing (can be optimized further)
        double k_arr[4];
        _mm256_storeu_pd(k_arr, k_vec);
        
        for (int j = 0; j < simd_width; j++) {
            if (k_arr[j] >= 2.0) {
                double ln_k = fast_log(k_arr[j]);
                double ln_ln_k = fast_log(ln_k);
                
                // Simple PNT computation
                double pnt = k_arr[j] * ln_k - k_arr[j] + k_arr[j] * ln_ln_k / ln_k;
                
                // Simplified dilation and curvature
                double ln_pnt = fast_log(pnt);
                double d_term = ln_pnt * ln_pnt / (54.6 * 54.6);
                double e_term = fast_pow_neg_third(pnt / 1000.0) * 31.6;
                
                // Auto calibration
                double local_c = c, local_k_star = k_star;
                if (auto_calibrate) {
                    if (k_arr[j] < 1e4) {
                        local_c = -0.00247;
                        local_k_star = 0.04449;
                    } else if (k_arr[j] < 1e7) {
                        local_c = -0.00037;
                        local_k_star = -0.11446;
                    } else {
                        local_c = -0.0001;
                        local_k_star = -0.15;
                    }
                }
                
                results[i + j] = pnt + local_c * d_term * pnt + local_k_star * e_term * pnt;
            } else {
                results[i + j] = 0.0;
            }
        }
    }
    
    // Process remaining elements
    for (int i = vectorized_n; i < n; i++) {
        results[i] = z5d_prime_optimized(k_values[i], c, k_star, kappa_geo, auto_calibrate);
    }
}
#endif

// Batch processing with OpenMP optimization
void z5d_prime_batch_parallel_optimized(const double* k_values, double* results, int n,
                                       double c, double k_star, double kappa_geo, int auto_calibrate) {
    init_lookup_tables();
    
#ifdef _OPENMP
    #pragma omp parallel for schedule(static, 64)
#endif
    for (int i = 0; i < n; i++) {
        results[i] = z5d_prime_optimized(k_values[i], c, k_star, kappa_geo, auto_calibrate);
    }
}

// Memory-optimized batch processing for ultra-large scales
void z5d_prime_batch_ultra_scale(const double* k_values, double* results, int n,
                                double c, double k_star, double kappa_geo, int auto_calibrate,
                                int chunk_size) {
    init_lookup_tables();
    
    if (chunk_size <= 0) chunk_size = 1000; // Default chunk size
    
    for (int start = 0; start < n; start += chunk_size) {
        int end = start + chunk_size;
        if (end > n) end = n;
        
        int chunk_n = end - start;
        
#ifdef __AVX2__
        // Use AVX2 if available
        z5d_prime_batch_avx2(&k_values[start], &results[start], chunk_n,
                             c, k_star, kappa_geo, auto_calibrate);
#else
        // Fallback to parallel processing
        z5d_prime_batch_parallel_optimized(&k_values[start], &results[start], chunk_n,
                                         c, k_star, kappa_geo, auto_calibrate);
#endif
    }
}

// Performance profiling function
z5d_perf_stats_t z5d_benchmark_optimizations(int n_samples, double k_start, double k_step) {
    z5d_perf_stats_t stats = {0};
    
    // Allocate test data
    double* k_values = malloc(n_samples * sizeof(double));
    double* results_original = malloc(n_samples * sizeof(double));
    double* results_optimized = malloc(n_samples * sizeof(double));
    
    if (!k_values || !results_original || !results_optimized) {
        free(k_values);
        free(results_original);
        free(results_optimized);
        return stats;
    }
    
    // Generate test k values
    for (int i = 0; i < n_samples; i++) {
        k_values[i] = k_start + i * k_step;
    }
    
    // Benchmark original implementation
    double start_time = (double)clock() / CLOCKS_PER_SEC;
    
    for (int i = 0; i < n_samples; i++) {
        results_original[i] = z5d_prime(k_values[i], 0.0, 0.0, 0.3, 1);
    }
    
    double end_time = (double)clock() / CLOCKS_PER_SEC;
    stats.original_time = end_time - start_time;
    
    // Benchmark optimized implementation
    start_time = (double)clock() / CLOCKS_PER_SEC;
    
    z5d_prime_batch_ultra_scale(k_values, results_optimized, n_samples,
                               0.0, 0.0, 0.3, 1, 64);
    
    end_time = (double)clock() / CLOCKS_PER_SEC;
    stats.optimized_time = end_time - start_time;
    
    // Calculate statistics
    stats.speedup_factor = stats.original_time / stats.optimized_time;
    stats.compute_reduction = (stats.original_time - stats.optimized_time) / stats.original_time;
    
    // Calculate accuracy difference
    double total_error = 0.0;
    int valid_comparisons = 0;
    
    for (int i = 0; i < n_samples; i++) {
        if (isfinite(results_original[i]) && isfinite(results_optimized[i]) && 
            results_original[i] > 0 && results_optimized[i] > 0) {
            double error = fabs(results_original[i] - results_optimized[i]) / results_original[i];
            total_error += error;
            valid_comparisons++;
        }
    }
    
    stats.accuracy_error = valid_comparisons > 0 ? total_error / valid_comparisons : 0.0;
    stats.samples_processed = n_samples;
    
    // Cleanup
    free(k_values);
    free(results_original);
    free(results_optimized);
    
    return stats;
}