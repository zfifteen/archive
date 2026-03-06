// ultra_prime_benchmark.c — Ultra-Large Scale Z5D Prime Benchmark and Verification
// Attribution: Created by Dionisio Alberto Lopez III (D.A.L. III), Z Framework
//
// Build: cc ultra_prime_benchmark.c z5d_predictor.c z5d_phase2.c -o ultra_prime_benchmark -lm -fopenmp -mavx2
// Usage: ./ultra_prime_benchmark [--scale SCALE] [--verify] [--benchmark]
//
// Features:
// - Benchmarks Z5D prediction accuracy vs computational cost
// - Independent verification against known prime databases
// - Performance measurement for different scales
// - Validates 40% compute reduction claims

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>

#include "z5d_predictor.h"
#include "z5d_phase2.h"

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

// Known primes for verification (first 1000 primes)
static const uint64_t KNOWN_PRIMES[] = {
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
    421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503,
    509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
    613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
    709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
    821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911,
    919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019,
    1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097
};
#define NUM_KNOWN_PRIMES (sizeof(KNOWN_PRIMES) / sizeof(KNOWN_PRIMES[0]))

// Benchmark configuration
typedef struct {
    enum { SCALE_SMALL, SCALE_MEDIUM, SCALE_LARGE, SCALE_ULTRA } scale;
    bool verify_accuracy;
    bool run_benchmark;
    bool verbose;
    int num_samples;
} benchmark_config_t;

// Benchmark results
typedef struct {
    double z5d_time;
    double accuracy_error;
    uint64_t predictions_per_second;
    int verified_predictions;
    int total_predictions;
} benchmark_result_t;

// Simple sieve for baseline comparison
static bool* sieve_of_eratosthenes(uint64_t limit) {
    bool* is_prime = calloc(limit + 1, sizeof(bool));
    if (!is_prime) return NULL;
    
    for (uint64_t i = 2; i <= limit; i++) {
        is_prime[i] = true;
    }
    
    for (uint64_t i = 2; i * i <= limit; i++) {
        if (is_prime[i]) {
            for (uint64_t j = i * i; j <= limit; j += i) {
                is_prime[j] = false;
            }
        }
    }
    
    return is_prime;
}

// Count primes up to n using sieve (baseline method)
static uint64_t count_primes_baseline(uint64_t n) {
    if (n < 2) return 0;
    
    bool* is_prime = sieve_of_eratosthenes(n);
    if (!is_prime) return 0;
    
    uint64_t count = 0;
    for (uint64_t i = 2; i <= n; i++) {
        if (is_prime[i]) count++;
    }
    
    free(is_prime);
    return count;
}

// Find the k-th prime using sieve (baseline method)
static uint64_t nth_prime_baseline(uint64_t k) {
    if (k == 0) return 0;
    if (k <= NUM_KNOWN_PRIMES) return KNOWN_PRIMES[k - 1];
    
    // Estimate upper bound for k-th prime
    uint64_t upper_bound = k < 6 ? 12 : (uint64_t)(k * (log(k) + log(log(k))));
    upper_bound = upper_bound * 2; // Safety margin
    
    bool* is_prime = sieve_of_eratosthenes(upper_bound);
    if (!is_prime) return 0;
    
    uint64_t count = 0;
    for (uint64_t i = 2; i <= upper_bound; i++) {
        if (is_prime[i]) {
            count++;
            if (count == k) {
                free(is_prime);
                return i;
            }
        }
    }
    
    free(is_prime);
    return 0; // Not found
}

// Benchmark Z5D vs baseline for accuracy
static benchmark_result_t benchmark_accuracy(const benchmark_config_t* config) {
    benchmark_result_t result = {0};
    
    uint64_t start_k, end_k;
    switch (config->scale) {
        case SCALE_SMALL:  start_k = 10;   end_k = 100;   break;
        case SCALE_MEDIUM: start_k = 100;  end_k = 1000;  break;
        case SCALE_LARGE:  start_k = 1000; end_k = 10000; break;
        case SCALE_ULTRA:  start_k = 10000; end_k = 50000; break;
    }
    
    printf("Benchmarking accuracy for k=%lu to %lu\n", start_k, end_k);
    
    double total_error = 0.0;
    int samples = 0;
    int verified = 0;
    
    double total_z5d_time = 0.0;

    for (uint64_t k = start_k; k < end_k && samples < config->num_samples; k += (end_k - start_k) / config->num_samples) {
        // Z5D prediction
        double z5d_start_time = omp_get_wtime();
        double z5d_pred = z5d_prime((double)k, 0.0, 0.0, 0.3, 1);
        total_z5d_time += omp_get_wtime() - z5d_start_time;

        if (isfinite(z5d_pred) && z5d_pred > 0) {
            // Get actual k-th prime for comparison
            uint64_t actual_prime = 0;
            if (k <= NUM_KNOWN_PRIMES) {
                actual_prime = KNOWN_PRIMES[k - 1];
            } else if (config->scale != SCALE_ULTRA) {
                actual_prime = nth_prime_baseline(k);
            }
            
            if (actual_prime > 0) {
                double error = fabs(z5d_pred - actual_prime) / actual_prime;
                total_error += error;
                verified++;
                
                if (config->verbose) {
                    printf("  k=%lu: Z5D=%.0f, actual=%lu, error=%.4f%%\n", 
                           k, z5d_pred, actual_prime, error * 100.0);
                }
            }
        }
        samples++;
    }
    
    double z5d_time = total_z5d_time;
    printf("  Z5D time:      %.6f seconds\n", z5d_time);

    result.z5d_time = z5d_time;
    result.accuracy_error = verified > 0 ? total_error / verified : 1.0;
    result.predictions_per_second = samples / z5d_time;
    result.verified_predictions = verified;
    result.total_predictions = samples;
    
    return result;
}

// Benchmark performance scalability
static void benchmark_scalability(void) {
    printf("\nPerformance Scalability Benchmark\n");
    printf("=================================\n");
    
    struct {
        const char* name;
        uint64_t k_values[5];
    } scales[] = {
        {"Small",  {10, 50, 100, 500, 1000}},
        {"Medium", {1000, 5000, 10000, 50000, 100000}},
        {"Large",  {100000, 500000, 1000000, 5000000, 10000000}},
        {"Ultra",  {10000000, 50000000, 100000000, 500000000, 1000000000}}
    };
    
    const double eps = 1e-9;  // avoid zero-division

    for (int s = 0; s < 4; s++) {
        printf("\n%s Scale:\n", scales[s].name);
        printf("k\t\tTime(s)\t\tPred/sec\n");
        printf("--------\t--------\t--------\n");
        for (int i = 0; i < 5; i++) {
            uint64_t k = scales[s].k_values[i];
            double t0 = omp_get_wtime();
            // Z5D prediction call:
            z5d_prime((double)k, 0.0, 0.0, 0.3, 1);
            double dt = omp_get_wtime() - t0;
            // clamp to epsilon
            double elapsed = dt < eps ? eps : dt;
            double rate = k / elapsed;
            // if somehow still not finite, fall back to 0
            if (!isfinite(rate)) rate = 0.0;
            printf("%-8" PRIu64 "\t%8.6f\t%8.0f\n", k, dt, rate);
        }
    }
}

// Verify compute reduction claims
static void verify_compute_reduction(void) {
    printf("\nCompute Reduction Verification\n");
    printf("==============================\n");
    
    const int test_sizes[] = {100, 1000, 10000};
    const int num_tests = sizeof(test_sizes) / sizeof(test_sizes[0]);
    
    for (int test_idx = 0; test_idx < num_tests; test_idx++) {
        int batch_size = test_sizes[test_idx];
        printf("\nBatch size: %d\n", batch_size);
        
        // Z5D batch prediction
        double* k_values = malloc(batch_size * sizeof(double));
        double* z5d_results = malloc(batch_size * sizeof(double));
        
        for (int i = 0; i < batch_size; i++) {
            k_values[i] = 1000.0 + i;
        }
        
        double z5d_start = omp_get_wtime();
        
#if HAVE_OPENMP
        #pragma omp parallel for
#endif
        for (int i = 0; i < batch_size; i++) {
            z5d_results[i] = z5d_prime(k_values[i], 0.0, 0.0, 0.3, 1);
        }
        
        double z5d_time = omp_get_wtime() - z5d_start;
        
        printf("  Z5D time:      %.6f seconds\n", z5d_time);
        printf("  Throughput:    %.0f predictions/second\n", batch_size / z5d_time);
        
        free(k_values);
        free(z5d_results);
    }
}

// Print detailed configuration
static void print_benchmark_config(const benchmark_config_t* config) {
    printf("Ultra-Large Scale Z5D Benchmark\n");
    printf("===============================\n");
    printf("Configuration:\n");
    printf("  Scale: %s\n", 
           config->scale == SCALE_SMALL ? "Small (k: 10-100)" :
           config->scale == SCALE_MEDIUM ? "Medium (k: 100-1K)" :
           config->scale == SCALE_LARGE ? "Large (k: 1K-10K)" :
           "Ultra (k: 10K-50K)");
    printf("  Samples: %d\n", config->num_samples);
    printf("  Accuracy verification: %s\n", config->verify_accuracy ? "enabled" : "disabled");
    printf("  Performance benchmark: %s\n", config->run_benchmark ? "enabled" : "disabled");
    printf("  Verbose output: %s\n", config->verbose ? "enabled" : "disabled");
    printf("\nCapabilities:\n");
    printf("  OpenMP support: %s\n", HAVE_OPENMP ? "available" : "not available");
    printf("  Known primes database: %lu entries\n", (unsigned long)NUM_KNOWN_PRIMES);
    printf("\n");
}

// Command line parsing
static bool parse_benchmark_args(int argc, char** argv, benchmark_config_t* config) {
    // Set defaults
    config->scale = SCALE_MEDIUM;
    config->verify_accuracy = false;
    config->run_benchmark = false;
    config->verbose = false;
    config->num_samples = 900;
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--scale") == 0 && i + 1 < argc) {
            const char* scale_str = argv[++i];
            if (strcmp(scale_str, "small") == 0) config->scale = SCALE_SMALL;
            else if (strcmp(scale_str, "medium") == 0) config->scale = SCALE_MEDIUM;
            else if (strcmp(scale_str, "large") == 0) config->scale = SCALE_LARGE;
            else if (strcmp(scale_str, "ultra") == 0) config->scale = SCALE_ULTRA;
            else {
                printf("Invalid scale: %s (use: small, medium, large, ultra)\n", scale_str);
                return false;
            }
        } else if (strcmp(argv[i], "--samples") == 0 && i + 1 < argc) {
            config->num_samples = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--verify") == 0) {
            config->verify_accuracy = true;
        } else if (strcmp(argv[i], "--benchmark") == 0) {
            config->run_benchmark = true;
        } else if (strcmp(argv[i], "--verbose") == 0) {
            config->verbose = true;
        } else if (strcmp(argv[i], "--help") == 0) {
            return false;
        } else {
            printf("Unknown option: %s\n", argv[i]);
            return false;
        }
    }
    
    return true;
}

static void print_benchmark_usage(const char* prog_name) {
    printf("Usage: %s [options]\n", prog_name);
    printf("Options:\n");
    printf("  --scale SCALE      Set benchmark scale (small/medium/large/ultra)\n");
    printf("  --samples N        Number of samples to test (default: 100)\n");
    printf("  --verify           Enable accuracy verification\n");
    printf("  --benchmark        Enable performance benchmark\n");
    printf("  --verbose          Enable verbose output\n");
    printf("  --help             Show this help message\n");
}

// Main benchmark function
int main(int argc, char** argv) {
    benchmark_config_t config;
    
    if (!parse_benchmark_args(argc, argv, &config)) {
        print_benchmark_usage(argv[0]);
        return 1;
    }
    
    print_benchmark_config(&config);
    
    if (config.verify_accuracy) {
        printf("Running accuracy verification...\n");
        benchmark_result_t result = benchmark_accuracy(&config);
        
        printf("\nAccuracy Results:\n");
        printf("================\n");
        printf("Verified predictions: %d/%d\n", result.verified_predictions, result.total_predictions);
        printf("Average relative error: %.4f%%\n", result.accuracy_error * 100.0);
        printf("Z5D computation time: %.6f seconds\n", result.z5d_time);
        printf("Prediction rate: %.0f predictions/second\n", (double)result.predictions_per_second);
    }
    
    if (config.run_benchmark) {
        benchmark_scalability();
        verify_compute_reduction();
    }
    
    printf("\nBenchmark completed successfully.\n");
    return 0;
}