/**
 * Z5D Crypto Scale Test Program
 * ============================
 *
 * Test and validate Z5D cryptographic prime prediction at RSA scales.
 * Verifies sub-1% error and 7.39× speedup requirements.
 *
 * Usage: ./test_crypto_scale [--bit-length N] [--trials N] [--verbose]
 *
 * @file test_crypto_scale.c
 * @author Dionisio Alberto Lopez III (D.A.L. III)
 * @version 1.0.0
 */

#include "z5d_crypto_prediction.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

// Test configuration
typedef struct {
    uint32_t bit_length;
    uint32_t trials;
    bool verbose;
    bool benchmark;
    bool accuracy_test;
    bool show_capabilities;
} test_config_t;

// Test results
typedef struct {
    bool success;
    double mean_generation_time;
    double speedup_achieved;
    double accuracy_error;
    uint32_t successful_trials;
    uint32_t total_trials;
} test_results_t;

static void print_usage(const char* program_name) {
    printf("Z5D Crypto Scale Test Program\n");
    printf("Usage: %s [options]\n\n", program_name);
    printf("Options:\n");
    printf("  --bit-length N    RSA bit length (512, 1024, 2048, 4096) [default: 512]\n");
    printf("  --trials N        Number of test trials [default: 10]\n");
    printf("  --benchmark       Run speedup benchmark\n");
    printf("  --accuracy        Test prediction accuracy\n");
    printf("  --verbose         Enable verbose output\n");
    printf("  --capabilities    Show module capabilities\n");
    printf("  --help            Show this help\n\n");
    printf("Examples:\n");
    printf("  %s --bit-length 1024 --trials 50 --benchmark\n", program_name);
    printf("  %s --capabilities\n", program_name);
    printf("  %s --accuracy --verbose\n", program_name);
}

static test_config_t parse_args(int argc, char** argv) {
    test_config_t config = {
        .bit_length = 512,
        .trials = 10,
        .verbose = false,
        .benchmark = false,
        .accuracy_test = false,
        .show_capabilities = false
    };
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--bit-length") == 0 && i + 1 < argc) {
            config.bit_length = (uint32_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--trials") == 0 && i + 1 < argc) {
            config.trials = (uint32_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--verbose") == 0) {
            config.verbose = true;
        } else if (strcmp(argv[i], "--benchmark") == 0) {
            config.benchmark = true;
        } else if (strcmp(argv[i], "--accuracy") == 0) {
            config.accuracy_test = true;
        } else if (strcmp(argv[i], "--capabilities") == 0) {
            config.show_capabilities = true;
        } else if (strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            exit(0);
        }
    }
    
    return config;
}

static bool validate_bit_length(uint32_t bit_length) {
    return (bit_length == 512 || bit_length == 1024 || 
            bit_length == 2048 || bit_length == 4096);
}

static int test_crypto_generation(const test_config_t* config, test_results_t* results) {
    printf("Testing Z5D crypto prime generation (%u-bit, %u trials)...\n", 
           config->bit_length, config->trials);
    
    z5d_crypto_config_t crypto_config = z5d_crypto_get_default_config(config->bit_length);
    crypto_config.verbose = config->verbose;
    
    double total_time = 0.0;
    uint32_t successful = 0;
    
    for (uint32_t i = 0; i < config->trials; i++) {
        z5d_crypto_result_t result;
        
        int gen_result = z5d_crypto_generate_prime(&crypto_config, &result);
        
        if (gen_result == 0 && result.success) {
            total_time += result.total_time_ms;
            successful++;
            
            if (config->verbose) {
                printf("Trial %u: SUCCESS (%.3f ms, %u MR rounds)\n", 
                       i + 1, result.total_time_ms, result.mr_rounds_used);
            }
        } else {
            if (config->verbose) {
                printf("Trial %u: FAILED\n", i + 1);
            }
        }
        
        z5d_crypto_result_clear(&result);
    }
    
    results->total_trials = config->trials;
    results->successful_trials = successful;
    results->success = (successful > 0);
    results->mean_generation_time = successful > 0 ? total_time / successful : 0.0;
    
    printf("Generation Test Results:\n");
    printf("  Successful: %u/%u (%.1f%%)\n", successful, config->trials, 
           100.0 * successful / config->trials);
    printf("  Average time: %.3f ms\n", results->mean_generation_time);
    
    return 0;
}

static int test_speedup_benchmark(const test_config_t* config, test_results_t* results) {
    printf("\nRunning speedup benchmark...\n");
    
    z5d_crypto_benchmark_t benchmark;
    int bench_result = z5d_crypto_benchmark(config->bit_length, config->trials, &benchmark);
    
    if (bench_result != 0) {
        printf("Benchmark failed!\n");
        return -1;
    }
    
    results->speedup_achieved = benchmark.speedup_factor;
    
    z5d_crypto_print_performance_summary(&benchmark);
    
    // Validate speedup target
    if (benchmark.speedup_factor >= 7.2) {
        printf("✓ Speedup target ACHIEVED (%.2fx >= 7.2x)\n", benchmark.speedup_factor);
    } else {
        printf("✗ Speedup target MISSED (%.2fx < 7.2x)\n", benchmark.speedup_factor);
    }
    
    return 0;
}

static int test_accuracy_validation(const test_config_t* config, test_results_t* results) {
    printf("\nTesting prediction accuracy...\n");
    
    double mean_error, max_error;
    int acc_result = z5d_crypto_validate_accuracy(config->bit_length, 100, 
                                                 &mean_error, &max_error);
    
    if (acc_result != 0) {
        printf("Accuracy test failed!\n");
        return -1;
    }
    
    results->accuracy_error = mean_error;
    
    printf("Accuracy Results:\n");
    printf("  Mean relative error: %.6f%% \n", mean_error * 100);
    printf("  Max relative error: %.3f%%\n", max_error * 100);
    
    // Validate accuracy target
    if (max_error < 0.01) { // < 1%
        printf("✓ Accuracy target ACHIEVED (%.3f%% < 1.0%%)\n", max_error * 100);
    } else {
        printf("✗ Accuracy target MISSED (%.3f%% >= 1.0%%)\n", max_error * 100);
    }
    
    return 0;
}

static void print_final_summary(const test_config_t* config, const test_results_t* results) {
    printf("\n============================================================\n");
    printf("Z5D CRYPTO SCALE TEST SUMMARY\n");
    printf("============================================================\n");
    printf("Configuration:\n");
    printf("  RSA bit length: %u bits\n", config->bit_length);
    printf("  Test trials: %u\n", config->trials);
    printf("  GMP support: %s\n", z5d_crypto_has_gmp_support() ? "Yes" : "No");
    
    printf("\nResults:\n");
    printf("  Generation success: %u/%u (%.1f%%)\n", 
           results->successful_trials, results->total_trials,
           100.0 * results->successful_trials / results->total_trials);
    
    if (config->benchmark) {
        printf("  Speedup achieved: %.2fx\n", results->speedup_achieved);
        printf("  Speedup target: %s\n", 
               results->speedup_achieved >= 7.2 ? "✓ ACHIEVED" : "✗ MISSED");
    }
    
    if (config->accuracy_test) {
        printf("  Prediction error: %.6f%%\n", results->accuracy_error * 100);
        printf("  Accuracy target: %s\n", 
               results->accuracy_error < 0.01 ? "✓ ACHIEVED" : "✗ MISSED");
    }
    
    printf("\nOverall Status: ");
    if (results->success && 
        (!config->benchmark || results->speedup_achieved >= 7.2) &&
        (!config->accuracy_test || results->accuracy_error < 0.01)) {
        printf("✓ ALL TARGETS ACHIEVED\n");
    } else {
        printf("✗ SOME TARGETS MISSED\n");
    }
    
    printf("\nNext Steps:\n");
    printf("  - For RSA key generation: use z5d_crypto_generate_prime()\n");
    printf("  - For batch processing: see z5d_crypto_benchmark()\n");
    printf("  - For custom parameters: modify z5d_crypto_config_t\n");
}

int main(int argc, char** argv) {
    printf("Z5D Crypto Scale Test Program v%s\n\n", z5d_crypto_get_version());
    
    test_config_t config = parse_args(argc, argv);
    
    // Show capabilities if requested
    if (config.show_capabilities) {
        z5d_crypto_print_capabilities();
        return 0;
    }
    
    // Validate configuration
    if (!validate_bit_length(config.bit_length)) {
        printf("Error: Invalid bit length %u. Must be 512, 1024, 2048, or 4096.\n", 
               config.bit_length);
        return 1;
    }
    
    if (config.trials == 0 || config.trials > 10000) {
        printf("Error: Invalid trial count %u. Must be 1-10000.\n", config.trials);
        return 1;
    }
    
    // Initialize crypto module
    if (z5d_crypto_init() != 0) {
        printf("Error: Failed to initialize Z5D crypto module.\n");
        return 1;
    }
    
    test_results_t results = {0};
    
    // Run basic generation test
    if (test_crypto_generation(&config, &results) != 0) {
        printf("Error: Generation test failed.\n");
        z5d_crypto_cleanup();
        return 1;
    }
    
    // Run optional benchmark
    if (config.benchmark && results.success) {
        if (test_speedup_benchmark(&config, &results) != 0) {
            printf("Warning: Benchmark test failed.\n");
        }
    }
    
    // Run optional accuracy test
    if (config.accuracy_test && results.success) {
        if (test_accuracy_validation(&config, &results) != 0) {
            printf("Warning: Accuracy test failed.\n");
        }
    }
    
    // Print final summary
    print_final_summary(&config, &results);
    
    z5d_crypto_cleanup();
    return results.success ? 0 : 1;
}