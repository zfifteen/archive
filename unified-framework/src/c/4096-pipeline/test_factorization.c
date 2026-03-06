#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/bn.h>
#include "z5d_factorization_shortcut.h"

/**
 * Test harness for z5d_factorization_shortcut
 *
 * Tests the Z Framework geometric factorization approach on known RSA moduli.
 */

static void print_test_result(const char *test_name, z5d_factor_stat_t *stat,
                              const char *expected_p, const char *expected_q) {
    printf("\n=== %s ===\n", test_name);
    printf("Success: %s\n", stat->success ? "YES" : "NO");
    printf("Divisions tried: %d\n", stat->divisions_tried);
    printf("Time: %.4f seconds\n", stat->elapsed_seconds);

    if (stat->success) {
        printf("Factor p: %s\n", stat->factor_p);
        printf("Factor q: %s\n", stat->factor_q);

        // Verify correctness if expected values provided
        if (expected_p && expected_q) {
            int p_match = (strcmp(stat->factor_p, expected_p) == 0 ||
                          strcmp(stat->factor_p, expected_q) == 0);
            int q_match = (strcmp(stat->factor_q, expected_p) == 0 ||
                          strcmp(stat->factor_q, expected_q) == 0);

            if (p_match && q_match && strcmp(stat->factor_p, stat->factor_q) != 0) {
                printf("✓ CORRECT FACTORIZATION\n");
            } else {
                printf("✗ INCORRECT FACTORIZATION\n");
            }
        }
    }
}

int main(int argc, char *argv[]) {
    printf("Z5D Factorization Shortcut Test Suite\n");
    printf("======================================\n\n");

    // Test 1: Small RSA modulus (64-bit primes)
    // N = 17 × 19 = 323
    printf("Test 1: Tiny semiprime (323 = 17 × 19)\n");
    z5d_factor_stat_t stat1;
    int result1 = z5d_factorization_shortcut("323", 1000, 0.1, &stat1);
    print_test_result("Tiny Semiprime", &stat1, "17", "19");
    z5d_factorization_free(&stat1);

    // Test 2: Slightly larger (256-bit primes)
    // Let's use a known small semiprime for testing
    // N = 48611 × 53993 = 2624652323
    printf("\n\nTest 2: Small semiprime (2624652323 = 48611 × 53993)\n");
    z5d_factor_stat_t stat2;
    int result2 = z5d_factorization_shortcut("2624652323", 10000, 0.1, &stat2);
    print_test_result("Small Semiprime", &stat2, "48611", "53993");
    z5d_factorization_free(&stat2);

    // Test 3: Custom modulus from command line
    if (argc > 1) {
        printf("\n\nTest 3: Custom modulus from command line\n");
        const char *modulus = argv[1];
        int max_iter = (argc > 2) ? atoi(argv[2]) : 100000;
        double epsilon = (argc > 3) ? atof(argv[3]) : 0.15;

        printf("Modulus: %s\n", modulus);
        printf("Max iterations: %d\n", max_iter);
        printf("Epsilon: %.4f\n", epsilon);

        z5d_factor_stat_t stat3;
        int result3 = z5d_factorization_shortcut(modulus, max_iter, epsilon, &stat3);
        print_test_result("Custom Modulus", &stat3, NULL, NULL);
        z5d_factorization_free(&stat3);
    }

    // Summary
    printf("\n\n=== SUMMARY ===\n");
    printf("Test 1 (323): %s\n", result1 ? "PASSED" : "FAILED");
    printf("Test 2 (2624652323): %s\n", result2 ? "PASSED" : "FAILED");

    printf("\n\nNOTE: This is an experimental factorization approach using Z Framework\n");
    printf("geometric resolution. Success rates depend on:\n");
    printf("  - Epsilon threshold (circular distance tolerance)\n");
    printf("  - K parameter (currently fixed at 0.45)\n");
    printf("  - Random prime generation matching theta_N\n");
    printf("\nFor cryptographically strong RSA moduli (2048-bit+), this approach\n");
    printf("is NOT expected to succeed in reasonable time without additional\n");
    printf("mathematical insights or parameter optimization.\n");

    return 0;
}
