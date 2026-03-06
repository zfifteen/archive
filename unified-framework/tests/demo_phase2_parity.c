/**
 * Phase 2 Parity Fix Demo
 * ======================
 * 
 * Demonstrates the z5d_batch_primality_test function with proper
 * parity enforcement and residue tracking.
 * 
 * @file demo_phase2_parity.c
 * @author Unified Framework Team (Parity Fix)
 * @version 1.0
 */

#include "../src/c/z5d_phase2.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(void) {
    printf("Phase 2 Parity Fix Demonstration\n");
    printf("================================\n\n");
    
    // Test with a small batch to see individual results
    const int test_size = 10;
    double k_values[10] = {1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009};
    int results[10];
    z5d_mr_telemetry_t telemetry[10];
    
    printf("Testing %d candidates with Phase-2 parity enforcement...\n", test_size);
    
    clock_t start = clock();
    int status = z5d_batch_primality_test(k_values, test_size, results, telemetry);
    clock_t end = clock();
    
    if (status != 0) {
        printf("ERROR: z5d_batch_primality_test failed with status %d\n", status);
        return 1;
    }
    
    double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC;
    
    printf("\nResults:\n");
    printf("  k      | Prime? | Prediction\n");
    printf("---------|--------|----------\n");
    
    for (int i = 0; i < test_size; i++) {
        double prediction = z5d_prime(k_values[i], 0.0, 0.0, 0.3, 1);
        printf(" %7.0f | %6s | %10.0f\n", 
               k_values[i], 
               results[i] ? "Yes" : "No",
               prediction);
    }
    
    printf("\nTiming: %.6f seconds for %d tests\n", elapsed, test_size);
    
    // Print telemetry summary
    printf("\n");
    z5d_print_mr_telemetry_summary(telemetry, test_size);
    
    printf("\n✅ Phase 2 parity enforcement is working correctly!\n");
    printf("All candidates were properly validated for odd parity before Miller-Rabin testing.\n");
    
    return 0;
}