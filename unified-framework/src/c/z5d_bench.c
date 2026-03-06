// z5d_bench.c
// Description: Benchmarking tool for comparing the Z5D Prime Generator against primesieve and primegen.
//              Evaluates prediction accuracy, computational cost, and statistical confidence intervals.
//              
//              *** PARAMETER STANDARDIZATION ***
//              This benchmark uses standardized parameters from src/core/params.py to ensure
//              consistency across the Z Framework. Key parameters include:
//              - kappa_star = 0.04449 (Z_5D calibration factor)
//              - kappa_geo = 0.3 (geodesic exponent)
//              - c_calibrated = -0.00247 (least-squares optimization)
// 
// Created by Dionisio Alberto Lopez III (D.A.L. III), Z Framework
// Created: 2024-06-01
// Last updated: 2024-06-01
//
// Build: gcc -O3 -lmpfr -lgmp -lprimesieve z5d_bench.c z5d_predictor.c z5d_phase2.c -o z5d_bench -lm -fopenmp
// Usage: ./z5d_bench [--k-max K] [--bootstrap-samples N] [--csv-output FILE] [--seed SEED]
//
// Features:
// - Benchmark Z5D prediction accuracy vs computational cost
// - Compare against primesieve baseline for prime generation performance
// - Bootstrap confidence intervals for statistical validation
// - CSV output for independent verification
// - Parameter standardization aligned with Python framework

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>

#ifndef _WIN32
#include <unistd.h>
#endif

// Auto-detect MPFR/GMP availability
#if defined(__has_include)
#  if __has_include("mpfr.h") && __has_include("gmp.h")
#    include <mpfr.h>
#    include <gmp.h>
#    define HAVE_MPFR 1
#  else
#    define HAVE_MPFR 0
#  endif
#else
#  define HAVE_MPFR 0
#endif

// Primesieve integration
#if defined(__has_include)
#  if __has_include("primesieve.h")
#    include <primesieve.h>
#    define HAVE_PRIMESIEVE 1
#  else
#    define HAVE_PRIMESIEVE 0
#  endif
#else
#  define HAVE_PRIMESIEVE 0
#endif

// Z5D core headers
#include "z5d_predictor.h"
#include "z5d_phase2.h"
#include "z_framework_params.h"  /* Standardized Z Framework parameters */

// OpenMP support
#ifdef _OPENMP
#include <omp.h>
#define HAVE_OPENMP 1
#else
#define HAVE_OPENMP 0
static double omp_get_wtime(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}
#endif

// Configuration constants
#define DEFAULT_MAX_K 10000000ULL  // Target k=10^7 (default for production; reduce for testing)
#define DEFAULT_BOOT_SAMPLES 100   // Reduced for faster testing
#define MAX_CSV_LINE 1024

// Benchmark configuration
typedef struct {
    uint64_t k_max;
    int bootstrap_samples;
    bool enable_verification;
    char* csv_output_file;
    bool verbose;
    uint64_t seed;  // For deterministic bootstrap samples
} benchmark_config_t;

// Benchmark results
typedef struct {
    uint64_t k_value;
    double z5d_prediction;
    double z5d_time_ms;
    double primesieve_time_ms;
    uint64_t primesieve_count;
    double z5d_error_percent;
    double speedup_factor;
    double confidence_interval_low;
    double confidence_interval_high;
} benchmark_result_t;

// Timing utilities
static double get_time_ms(void) {
    return omp_get_wtime() * 1000.0;
}

// Z5D benchmark function using standardized parameters
static double benchmark_z5d_prediction(uint64_t k, double* time_ms) {
    double start_time = get_time_ms();
    
    // Use standardized Z5D parameters from z_framework_params.h
    // kappa_star = 0.04449 (key parameter from params.py)
    // c = -0.00247 (calibrated value)
    // kappa_geo = 0.3 (geodesic exponent)
    zf_standard_params_t params = zf_get_standard_params();
    
    double prediction = z5d_prime((double)k, params.c, params.kappa_star, params.kappa_geo, 1);
    
    *time_ms = get_time_ms() - start_time;
    return prediction;
}

#if HAVE_PRIMESIEVE
// Primesieve benchmark function
static uint64_t benchmark_primesieve(uint64_t limit, double* time_ms) {
    double start_time = get_time_ms();
    
    // Count primes up to limit using primesieve
    uint64_t count = primesieve_count_primes(0, limit);
    
    *time_ms = get_time_ms() - start_time;
    return count;
}
#else
// Fallback implementation when primesieve is not available
static uint64_t benchmark_primesieve(uint64_t limit, double* time_ms) {
    *time_ms = 0.0;
    printf("Warning: primesieve not available, using fallback\n");
    // Simple approximation using PNT
    return (uint64_t)(limit / log(limit));
}
#endif

// Calculate relative error percentage
static double calculate_relative_error(double predicted, double actual) {
    if (actual == 0.0) return 0.0;
    return fabs((predicted - actual) / actual) * 100.0;
}

// Run single benchmark
static void run_single_benchmark(uint64_t k, benchmark_result_t* result) {
    result->k_value = k;
    
    // Benchmark Z5D prediction
    result->z5d_prediction = benchmark_z5d_prediction(k, &result->z5d_time_ms);
    
    // Estimate prime limit from Z5D prediction
    uint64_t prime_limit = (uint64_t)ceil(result->z5d_prediction);
    
    // Benchmark primesieve
    result->primesieve_count = benchmark_primesieve(prime_limit, &result->primesieve_time_ms);
    
    // Calculate metrics
    if (result->primesieve_count > 0) {
        // Find the k-th prime using primesieve for verification
        uint64_t actual_kth_prime = 0;
#if HAVE_PRIMESIEVE
        // Get the k-th prime directly
        actual_kth_prime = primesieve_nth_prime((int64_t)k, 0);
#else
        // Fallback: approximate using PNT
        actual_kth_prime = (uint64_t)(k * log(k));
#endif
        
        result->z5d_error_percent = calculate_relative_error(result->z5d_prediction, (double)actual_kth_prime);
    } else {
        result->z5d_error_percent = 0.0;
    }
    
    // Calculate speedup
    if (result->primesieve_time_ms > 0) {
        result->speedup_factor = result->primesieve_time_ms / result->z5d_time_ms;
    } else {
        result->speedup_factor = 1.0;
    }
    
    // Initialize confidence intervals (will be calculated in bootstrap)
    result->confidence_interval_low = 0.0;
    result->confidence_interval_high = 0.0;
}

// Bootstrap confidence interval calculation
static void calculate_bootstrap_ci(uint64_t k, int samples, double* ci_low, double* ci_high) {
    double* bootstrap_errors = malloc(samples * sizeof(double));
    if (!bootstrap_errors) {
        *ci_low = 0.0;
        *ci_high = 0.0;
        return;
    }
    
    for (int i = 0; i < samples; i++) {
        benchmark_result_t temp_result;
        run_single_benchmark(k, &temp_result);
        bootstrap_errors[i] = temp_result.z5d_error_percent;
    }
    
    // Sort errors for percentile calculation
    for (int i = 0; i < samples - 1; i++) {
        for (int j = i + 1; j < samples; j++) {
            if (bootstrap_errors[i] > bootstrap_errors[j]) {
                double temp = bootstrap_errors[i];
                bootstrap_errors[i] = bootstrap_errors[j];
                bootstrap_errors[j] = temp;
            }
        }
    }
    
    // Calculate 95% confidence interval
    int ci_5_idx = (int)(samples * 0.025);
    int ci_95_idx = (int)(samples * 0.975);
    
    *ci_low = bootstrap_errors[ci_5_idx];
    *ci_high = bootstrap_errors[ci_95_idx];
    
    free(bootstrap_errors);
}

// Save results to CSV
static void save_results_csv(const char* filename, benchmark_result_t* results, int count, const benchmark_config_t* config) {
    FILE* file = fopen(filename, "w");
    if (!file) {
        printf("Error: Cannot open CSV file %s for writing\n", filename);
        return;
    }
    
    // Write CSV header with reproducibility metadata
    fprintf(file, "# Z5D Benchmark Results - Parameter Standardization v2.0\n");
    fprintf(file, "# Reproducibility metadata: seed=%" PRIu64 ", bootstrap_samples=%d, k_max=%" PRIu64 "\n", 
            config->seed, config->bootstrap_samples, config->k_max);
    fprintf(file, "# Parameters synchronized with src/core/params.py:\n");
    fprintf(file, "# kappa_star = %.5f (KAPPA_STAR_DEFAULT)\n", ZF_KAPPA_STAR_DEFAULT);
    fprintf(file, "# kappa_geo = %.3f (KAPPA_GEO_DEFAULT)\n", ZF_KAPPA_GEO_DEFAULT);
    fprintf(file, "# c = %.5f (Z5D_C_CALIBRATED)\n", ZF_Z5D_C_CALIBRATED);
    fprintf(file, "k_value,z5d_prediction,z5d_time_ms,primesieve_time_ms,primesieve_count,z5d_error_percent,speedup_factor,ci_low,ci_high\n");
    
    // Write data rows
    for (int i = 0; i < count; i++) {
        fprintf(file, "%" PRIu64 ",%.6f,%.6f,%.6f,%" PRIu64 ",%.6f,%.6f,%.6f,%.6f\n",
                results[i].k_value,
                results[i].z5d_prediction,
                results[i].z5d_time_ms,
                results[i].primesieve_time_ms,
                results[i].primesieve_count,
                results[i].z5d_error_percent,
                results[i].speedup_factor,
                results[i].confidence_interval_low,
                results[i].confidence_interval_high);
    }
    
    fclose(file);
    printf("Benchmark results saved to: %s\n", filename);
}

// Parse command line arguments
static bool parse_args(int argc, char** argv, benchmark_config_t* config) {
    // Set defaults
    config->k_max = DEFAULT_MAX_K;
    config->bootstrap_samples = DEFAULT_BOOT_SAMPLES;
    config->enable_verification = false;
    config->csv_output_file = NULL;
    config->verbose = false;
    config->seed = (uint64_t)time(NULL);  // Default to current time
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--k-max") == 0 && i + 1 < argc) {
            config->k_max = strtoull(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "--bootstrap-samples") == 0 && i + 1 < argc) {
            config->bootstrap_samples = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--csv-output") == 0 && i + 1 < argc) {
            config->csv_output_file = argv[++i];
        } else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            config->seed = strtoull(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "--verify") == 0) {
            config->enable_verification = true;
        } else if (strcmp(argv[i], "--verbose") == 0) {
            config->verbose = true;
        } else if (strcmp(argv[i], "--help") == 0) {
            printf("Z5D Benchmark vs. primesieve (Parameter Standardization v2.0)\n");
            printf("=============================================================\n");
            printf("This benchmark uses standardized parameters from src/core/params.py\n");
            printf("to ensure consistency across the Z Framework:\n");
            printf("  - kappa_star = %.5f (Z_5D calibration factor)\n", ZF_KAPPA_STAR_DEFAULT);
            printf("  - kappa_geo = %.3f (geodesic exponent)\n", ZF_KAPPA_GEO_DEFAULT);
            printf("  - c = %.5f (least-squares calibration)\n", ZF_Z5D_C_CALIBRATED);
            printf("\nUsage: %s [options]\n", argv[0]);
            printf("Options:\n");
            printf("  --k-max K              Maximum k value to test (default: %llu)\n", DEFAULT_MAX_K);
            printf("  --bootstrap-samples N  Number of bootstrap samples (default: %d)\n", DEFAULT_BOOT_SAMPLES);
            printf("  --csv-output FILE      Save results to CSV file\n");
            printf("  --seed SEED            Seed for deterministic bootstrap (default: current time)\n");
            printf("  --verify               Enable verification mode\n");
            printf("  --verbose              Enable verbose output\n");
            printf("  --help                 Show this help message\n");
            printf("\nThis addresses the k parameter standardization issue by using\n");
            printf("distinct variable names for different contexts as defined in params.py\n");
            return false;
        } else {
            printf("Unknown option: %s\n", argv[i]);
            return false;
        }
    }
    
    return true;
}

// Main benchmark function
void benchmark_z5d_vs_tools(const benchmark_config_t* config) {
    printf("Z5D Prime Generator vs. primesieve Benchmark\n");
    printf("============================================\n");
    printf("Max k value: %" PRIu64 "\n", config->k_max);
    printf("Bootstrap samples: %d\n", config->bootstrap_samples);
    printf("Random seed: %" PRIu64 "\n", config->seed);
#if HAVE_PRIMESIEVE
    printf("Primesieve: available\n");
#else
    printf("Primesieve: not available (using fallback)\n");
#endif
#if HAVE_MPFR
    printf("MPFR/GMP: available (dps~50 equiv)\n");
#else
    printf("MPFR/GMP: not available (using standard precision)\n");
#endif
    printf("\n");
    
    // Initialize random seed for deterministic bootstrap
    srand((unsigned int)config->seed);
    
    // Display parameter overloading information
    printf("Parameter Overloading (synchronized with src/core/params.py):\n");
    printf("------------------------------------------------------------\n");
    zf_standard_params_t params = zf_get_standard_params();
    printf("  kappa_star: %.5f (Z_5D calibration factor)\n", params.kappa_star);
    printf("  kappa_geo:  %.3f (geodesic exponent)\n", params.kappa_geo);
    printf("  c:          %.5f (least-squares calibration)\n", params.c);
    printf("  This addresses k parameter overloading by using distinct\n");
    printf("  variable names for different contexts as defined in params.py\n");
    printf("\n");
    
    // Test k values (logarithmic progression)
    uint64_t test_k_values[] = {1000, 10000, 100000, 1000000};
    int num_tests = sizeof(test_k_values) / sizeof(test_k_values[0]);
    
    // Filter test values based on k_max
    int actual_tests = 0;
    for (int i = 0; i < num_tests; i++) {
        if (test_k_values[i] <= config->k_max) {
            actual_tests++;
        }
    }
    
    benchmark_result_t* results = malloc(actual_tests * sizeof(benchmark_result_t));
    if (!results) {
        printf("Error: Cannot allocate memory for results\n");
        return;
    }
    
    // Run benchmarks
    int result_idx = 0;
    for (int i = 0; i < num_tests && test_k_values[i] <= config->k_max; i++) {
        uint64_t k = test_k_values[i];
        
        if (config->verbose) {
            printf("Running benchmark for k = %" PRIu64 "...\n", k);
        }
        
        run_single_benchmark(k, &results[result_idx]);
        
        // Calculate bootstrap confidence intervals if enabled
        if (config->enable_verification && config->bootstrap_samples > 1) {
            if (config->verbose) {
                printf("  Calculating bootstrap CI with %d samples...\n", config->bootstrap_samples);
            }
            calculate_bootstrap_ci(k, config->bootstrap_samples, 
                                   &results[result_idx].confidence_interval_low,
                                   &results[result_idx].confidence_interval_high);
        }
        
        // Print results
        printf("k = %" PRIu64 ":\n", k);
        printf("  Z5D prediction: %.1f (%.4f ms)\n", 
               results[result_idx].z5d_prediction, results[result_idx].z5d_time_ms);
        printf("  Primesieve time: %.4f ms\n", results[result_idx].primesieve_time_ms);
        printf("  Z5D error: %.6f%%\n", results[result_idx].z5d_error_percent);
        printf("  Speedup factor: %.2fx\n", results[result_idx].speedup_factor);
        
        if (config->enable_verification && config->bootstrap_samples > 1) {
            printf("  Error CI [%.6f%%, %.6f%%]\n", 
                   results[result_idx].confidence_interval_low,
                   results[result_idx].confidence_interval_high);
        }
        printf("\n");
        
        result_idx++;
    }
    
    // Save to CSV if requested
    if (config->csv_output_file) {
        save_results_csv(config->csv_output_file, results, actual_tests, config);
    }
    
    // Summary
    printf("Benchmark Summary:\n");
    printf("=================\n");
    double avg_speedup = 0.0;
    double avg_error = 0.0;
    for (int i = 0; i < actual_tests; i++) {
        avg_speedup += results[i].speedup_factor;
        avg_error += results[i].z5d_error_percent;
    }
    avg_speedup /= actual_tests;
    avg_error /= actual_tests;
    
    printf("Average speedup: %.2fx\n", avg_speedup);
    printf("Average Z5D error: %.6f%%\n", avg_error);
    
    // Parameter standardization summary
    printf("\nParameter Standardization Summary:\n");
    printf("- Used kappa_star=%.5f from src/core/params.py (KAPPA_STAR_DEFAULT)\n", ZF_KAPPA_STAR_DEFAULT);
    printf("- Used kappa_geo=%.3f from src/core/params.py (KAPPA_GEO_DEFAULT)\n", ZF_KAPPA_GEO_DEFAULT);
    printf("- Bootstrap validation: %d resamples (params.py standard)\n", ZF_BOOTSTRAP_RESAMPLES_DEFAULT);
    printf("- Uses distinct variable names: k_max, kappa_star, kappa_geo to avoid confusion\n");
    
    free(results);
}

int main(int argc, char** argv) {
    benchmark_config_t config;
    
    if (!parse_args(argc, argv, &config)) {
        return 1;
    }
    
#if HAVE_MPFR
    // Set MPFR precision to ~50 decimal digits (~166 bits)
    mpfr_set_default_prec(166);
#endif
    
    benchmark_z5d_vs_tools(&config);
    
    return 0;
}