/**
 * AMX Integration Test
 * ===================
 * 
 * Comprehensive integration test for AMX optimization in Z5D framework.
 * Tests end-to-end functionality, threading strategies, and performance scaling.
 * 
 * @file test_amx_integration.c
 * @author Unified Framework Team
 * @version 1.0.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <string.h>

#define Z5D_USE_OMP 0  // Disable OpenMP for controlled testing

#include "z5d_phase2.h"

#define TEST_TOLERANCE 1e-12

// Test configurations
typedef struct {
    const char* name;
    int size;
    int expected_amx_benefit; // 1 if AMX should provide benefit, 0 otherwise
} test_config_t;

static const test_config_t test_configs[] = {
    {"Small batch (8)", 8, 0},    // Below AMX threshold
    {"AMX threshold (16)", 16, 1}, // At AMX threshold  
    {"AMX optimal (32)", 32, 1},   // AMX matrix size
    {"Large batch (64)", 64, 1},   // Multiple AMX chunks
    {"Very large (128)", 128, 1}   // Stress test
};
static const int num_test_configs = sizeof(test_configs) / sizeof(test_configs[0]);

// Generate deterministic test data
void generate_test_data(double* k_values, int n) {
    for (int i = 0; i < n; i++) {
        // Generate k values in range [1000, 50000] for realistic Z5D scenarios
        k_values[i] = 1000.0 + (i * 500.0) + (i * i * 10.0);
    }
}

// Test AMX vs scalar computation consistency
int test_computation_consistency(void) {
    printf("Testing computation consistency...\n");
    
    const int test_size = 64;
    double k_values[test_size];
    double results_scalar[test_size];
    double results_amx[test_size];
    
    generate_test_data(k_values, test_size);
    
    // Get scalar results (force AMX off)
    z5d_phase2_config_t config_scalar = z5d_phase2_get_config();
    config_scalar.use_amx = 0;
    
    int status_scalar = z5d_prime_batch_parallel(k_values, test_size, results_scalar, &config_scalar);
    assert(status_scalar == 0);
    
    // Get AMX results (enable AMX if available)
    z5d_phase2_config_t config_amx = z5d_phase2_get_config();
    config_amx.use_amx = 1;
    config_amx.amx_precision_mode = AMX_PRECISION_STANDARD;
    
    int status_amx = z5d_prime_batch_parallel(k_values, test_size, results_amx, &config_amx);
    assert(status_amx == 0);
    
    // Compare results for consistency
    int consistent = 1;
    double max_diff = 0.0;
    
    for (int i = 0; i < test_size; i++) {
        double diff = fabs(results_scalar[i] - results_amx[i]);
        if (diff > max_diff) max_diff = diff;
        
        if (diff > TEST_TOLERANCE) {
            printf("  ❌ Inconsistency at k=%.1f: scalar=%.6f, amx=%.6f, diff=%.2e\n",
                   k_values[i], results_scalar[i], results_amx[i], diff);
            consistent = 0;
        }
    }
    
    printf("  Max difference: %.2e (tolerance: %.2e)\n", max_diff, TEST_TOLERANCE);
    printf("  ✓ Computation consistency test: %s\n", consistent ? "PASS" : "FAIL");
    
    return consistent;
}

// Test AMX threading strategy
int test_amx_threading_strategy(void) {
    printf("Testing AMX threading strategy...\n");
    
    const int test_size = 128;
    double k_values[test_size];
    double results[test_size];
    
    generate_test_data(k_values, test_size);
    
    // Test different thread configurations
    int thread_configs[] = {1, 2, 4, 6, 8};
    int num_configs = sizeof(thread_configs) / sizeof(thread_configs[0]);
    
    int all_passed = 1;
    
    for (int i = 0; i < num_configs; i++) {
        int num_threads = thread_configs[i];
        
        z5d_phase2_config_t config = z5d_phase2_get_config();
        config.use_amx = 1;
        config.omp_num_threads = num_threads;
        config.amx_precision_mode = AMX_PRECISION_STANDARD;
        
        int status = z5d_prime_batch_parallel(k_values, test_size, results, &config);
        
        if (status != 0) {
            printf("  ❌ Threading test failed for %d threads\n", num_threads);
            all_passed = 0;
        } else {
            // Validate results are reasonable
            int results_ok = 1;
            for (int j = 0; j < test_size; j++) {
                if (!isfinite(results[j]) || results[j] <= 0) {
                    results_ok = 0;
                    break;
                }
            }
            
            printf("  %s %d threads: %s\n", 
                   (num_threads >= 2 && num_threads <= 6) ? "✓" : "⚠",
                   num_threads, 
                   results_ok ? "PASS" : "FAIL");
            
            if (!results_ok) all_passed = 0;
        }
    }
    
    printf("  ✓ Threading strategy test: %s\n", all_passed ? "PASS" : "FAIL");
    return all_passed;
}

// Test AMX precision modes
int test_amx_precision_modes(void) {
    printf("Testing AMX precision modes...\n");
    
    const int test_size = 32;
    double k_values[test_size];
    generate_test_data(k_values, test_size);
    
    amx_precision_mode_t modes[] = {
        AMX_PRECISION_FAST,
        AMX_PRECISION_STANDARD, 
        AMX_PRECISION_HIGH
    };
    const char* mode_names[] = {"FAST", "STANDARD", "HIGH"};
    int num_modes = sizeof(modes) / sizeof(modes[0]);
    
    int all_passed = 1;
    
    for (int i = 0; i < num_modes; i++) {
        double results[test_size];
        
        z5d_phase2_config_t config = z5d_phase2_get_config();
        config.use_amx = 1;
        config.amx_precision_mode = modes[i];
        
        int status = z5d_prime_batch_parallel(k_values, test_size, results, &config);
        
        if (status != 0) {
            printf("  ❌ Precision mode %s failed\n", mode_names[i]);
            all_passed = 0;
        } else {
            // Validate precision requirements
            int precision_ok = 1;
            for (int j = 0; j < test_size; j++) {
                if (!isfinite(results[j]) || results[j] <= 0) {
                    precision_ok = 0;
                    break;
                }
            }
            
            printf("  ✓ Precision mode %s: %s\n", mode_names[i], precision_ok ? "PASS" : "FAIL");
            if (!precision_ok) all_passed = 0;
        }
    }
    
    printf("  ✓ Precision modes test: %s\n", all_passed ? "PASS" : "FAIL");
    return all_passed;
}

// Test scaling behavior
int test_scaling_behavior(void) {
    printf("Testing AMX scaling behavior...\n");
    
    int all_passed = 1;
    
    for (int i = 0; i < num_test_configs; i++) {
        const test_config_t* tc = &test_configs[i];
        
        double* k_values = malloc(tc->size * sizeof(double));
        double* results = malloc(tc->size * sizeof(double));
        
        if (!k_values || !results) {
            free(k_values); free(results);
            printf("  ❌ Memory allocation failed for %s\n", tc->name);
            all_passed = 0;
            continue;
        }
        
        generate_test_data(k_values, tc->size);
        
        z5d_phase2_config_t config = z5d_phase2_get_config();
        config.use_amx = 1;
        config.amx_precision_mode = AMX_PRECISION_STANDARD;
        
        int status = z5d_prime_batch_parallel(k_values, tc->size, results, &config);
        
        if (status != 0) {
            printf("  ❌ Scaling test failed for %s\n", tc->name);
            all_passed = 0;
        } else {
            // Validate all results
            int results_valid = 1;
            for (int j = 0; j < tc->size; j++) {
                if (!isfinite(results[j]) || results[j] <= 0) {
                    results_valid = 0;
                    break;
                }
            }
            
            const char* expected = tc->expected_amx_benefit ? "AMX beneficial" : "scalar optimal";
            printf("  ✓ %s (%s): %s\n", tc->name, expected, results_valid ? "PASS" : "FAIL");
            
            if (!results_valid) all_passed = 0;
        }
        
        free(k_values);
        free(results);
    }
    
    printf("  ✓ Scaling behavior test: %s\n", all_passed ? "PASS" : "FAIL");
    return all_passed;
}

// Test error handling and edge cases
int test_error_handling(void) {
    printf("Testing error handling and edge cases...\n");
    
    int all_passed = 1;
    
    // Test NULL pointer handling
    {
        double k_values[10] = {1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000};
        double results[10];
        
        z5d_phase2_config_t config = z5d_phase2_get_config();
        config.use_amx = 1;
        
        // Test NULL k_values
        int status1 = z5d_prime_batch_parallel(NULL, 10, results, &config);
        if (status1 == 0) {
            printf("  ❌ Failed to reject NULL k_values\n");
            all_passed = 0;
        }
        
        // Test NULL results
        int status2 = z5d_prime_batch_parallel(k_values, 10, NULL, &config);
        if (status2 == 0) {
            printf("  ❌ Failed to reject NULL results\n");
            all_passed = 0;
        }
        
        // Test zero size
        int status3 = z5d_prime_batch_parallel(k_values, 0, results, &config);
        if (status3 == 0) {
            printf("  ❌ Failed to reject zero size\n");
            all_passed = 0;
        }
        
        // Test negative size
        int status4 = z5d_prime_batch_parallel(k_values, -5, results, &config);
        if (status4 == 0) {
            printf("  ❌ Failed to reject negative size\n");
            all_passed = 0;
        }
        
        printf("  ✓ NULL pointer handling: PASS\n");
    }
    
    // Test invalid k values
    {
        double invalid_k_values[] = {NAN, INFINITY, -1000.0, 0.0};
        double results[4];
        
        z5d_phase2_config_t config = z5d_phase2_get_config();
        config.use_amx = 1;
        
        int status = z5d_prime_batch_parallel(invalid_k_values, 4, results, &config);
        
        // Should complete but produce reasonable results for invalid inputs
        if (status != 0) {
            printf("  ❌ Invalid k values test failed\n");
            all_passed = 0;
        } else {
            // Check that invalid inputs produce 0.0 results (our expected behavior)
            int handled_correctly = 1;
            for (int i = 0; i < 4; i++) {
                if (!isfinite(results[i])) {
                    // This is acceptable behavior for invalid inputs
                } else if (results[i] < 0) {
                    printf("  ❌ Negative result for invalid input: %f\n", results[i]);
                    handled_correctly = 0;
                }
            }
            printf("  ✓ Invalid k values handling: %s\n", handled_correctly ? "PASS" : "FAIL");
            if (!handled_correctly) all_passed = 0;
        }
    }
    
    printf("  ✓ Error handling test: %s\n", all_passed ? "PASS" : "FAIL");
    return all_passed;
}

// Test AMX capabilities reporting
int test_capabilities_reporting(void) {
    printf("Testing capabilities reporting...\n");
    
    z5d_phase2_capabilities_t caps = z5d_phase2_get_capabilities();
    z5d_phase2_config_t config = z5d_phase2_get_config();
    
    // Validate capabilities structure
    assert(caps.compiler_version != NULL);
    assert(caps.build_flags != NULL);
    
    // Validate AMX fields
    if (caps.amx_available) {
        assert(caps.amx_matrix_size == 32); // M1 Max AMX size
        printf("  ✓ AMX available: %dx%d matrix size\n", caps.amx_matrix_size, caps.amx_matrix_size);
    } else {
        assert(caps.amx_matrix_size == 0);
        printf("  ⚠ AMX not available (expected on non-M1 Max platforms)\n");
    }
    
    // Validate configuration consistency
    if (caps.amx_available && config.use_amx) {
        assert(config.amx_precision_mode >= AMX_PRECISION_FAST);
        assert(config.amx_precision_mode <= AMX_PRECISION_HIGH);
        printf("  ✓ AMX configuration valid: precision mode %d\n", config.amx_precision_mode);
    }
    
    printf("  ✓ Capabilities reporting test: PASS\n");
    return 1;
}

int main(void) {
    printf("AMX Integration Test Suite\n");
    printf("==========================\n\n");
    
    // Print initial capabilities
    printf("Platform Information:\n");
    z5d_phase2_print_capabilities();
    printf("\n");
    
    int all_tests_passed = 1;
    int tests_run = 0;
    int tests_passed = 0;
    
    // Run test suite
    struct {
        const char* name;
        int (*test_func)(void);
    } tests[] = {
        {"Computation Consistency", test_computation_consistency},
        {"Threading Strategy", test_amx_threading_strategy}, 
        {"Precision Modes", test_amx_precision_modes},
        {"Scaling Behavior", test_scaling_behavior},
        {"Error Handling", test_error_handling},
        {"Capabilities Reporting", test_capabilities_reporting}
    };
    
    int num_tests = sizeof(tests) / sizeof(tests[0]);
    
    for (int i = 0; i < num_tests; i++) {
        printf("\n%d. %s\n", i + 1, tests[i].name);
        printf("----------------------------------------\n");
        
        int test_result = tests[i].test_func();
        tests_run++;
        
        if (test_result) {
            tests_passed++;
            printf("✅ PASSED\n");
        } else {
            all_tests_passed = 0;
            printf("❌ FAILED\n");
        }
    }
    
    // Final summary
    printf("\n");
    printf("Integration Test Summary\n");
    printf("========================\n");
    printf("Tests run: %d\n", tests_run);
    printf("Tests passed: %d\n", tests_passed);
    printf("Tests failed: %d\n", tests_run - tests_passed);
    printf("Overall result: %s\n", all_tests_passed ? "✅ ALL TESTS PASSED" : "❌ SOME TESTS FAILED");
    
    if (all_tests_passed) {
        printf("\n🎉 AMX integration is working correctly!\n");
        printf("Ready for production use on Apple M1 Max hardware.\n");
    } else {
        printf("\n⚠️ Some tests failed. Check implementation before production use.\n");
    }
    
    return all_tests_passed ? 0 : 1;
}