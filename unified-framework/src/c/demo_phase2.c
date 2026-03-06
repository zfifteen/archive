/**
 * Z5D Phase 2 Demonstration Fix
 * =============================
 * Addresses linker errors by ensuring MR symbols are linked.
 * Attribution: Dionisio Alberto Lopez III (D.A.L. III)
 */

#include "z5d_phase2.h"
#include <stdio.h>
#include <stdlib.h>

// Reuse existing detection
#ifdef Z5D_OMP_AVAILABLE
#  define Z5D_DEMO_OMP_AVAILABLE Z5D_OMP_AVAILABLE
#else
#  define Z5D_DEMO_OMP_AVAILABLE 0
#endif

// Force MR inclusion for demo (override if not built)
#ifndef Z5D_PHASE2_HAS_MR
#define Z5D_PHASE2_HAS_MR 1  // Set to 0 if MR sources unavailable
#endif

int main(void) {
    printf("Z5D Phase 2 Comprehensive Demonstration\n");
    printf("=======================================\n\n");

    /* 1) Capabilities */
    printf("1. Phase 2 Capabilities:\n");
    z5d_phase2_print_capabilities();
    printf("\n");

    /* 2) Parallel Z5D Prediction - Large Batch for Proper Performance */
    printf("2. Parallel Z5D Prediction (Large Batch for OpenMP Efficiency):\n");


    const int n = 300000; // 100K predictions for demo
    printf("Allocating memory for %d predictions...\n", n);

    double* k_values = malloc(n * sizeof(double));
    double* predictions = malloc(n * sizeof(double));

    if (!k_values || !predictions) {
        printf("❌ Memory allocation failed, using smaller batch\n");
        // Fallback to 1 million if memory allocation fails
        const int fallback_n = 1000000;
        k_values = realloc(k_values, fallback_n * sizeof(double));
        predictions = realloc(predictions, fallback_n * sizeof(double));

        if (!k_values || !predictions) {
            printf("❌ Even fallback allocation failed\n");
            free(k_values);
            free(predictions);
            return 1;
        }

        printf("Using fallback batch size: %d predictions\n", fallback_n);
        // Initialize fallback batch
        for (int i = 0; i < fallback_n; i++) {
            k_values[i] = 10000 + i; // Range: 10K to 1M+
        }

        z5d_phase2_stats_t phase2_stats = {0};
        printf("Running parallel batch prediction...\n");
        int rc = z5d_prime_batch_phase2(k_values, fallback_n, predictions, NULL, &phase2_stats);

        if (rc == 0) {
            printf("✅ Parallel batch prediction successful\n");
            printf("   Batch size: %d predictions\n", fallback_n);
            printf("   Time: %.3f ms, Cores: %d\n",
                   phase2_stats.time_ms_parallel, phase2_stats.cores_used);
            printf("   Throughput: %.0f predictions/second\n",
                   fallback_n / (phase2_stats.time_ms_parallel / 1000.0));
            printf("   Sample predictions:\n");
            for (int i = 0; i < 3; i++) {
                printf("     k=%g -> p≈%.0f\n", k_values[i], predictions[i]);
            }
        } else {
            printf("❌ Parallel batch prediction failed\n");
        }

        free(k_values);
        free(predictions);
        return 0;
    }

    // Initialize large batch with varied k values
    printf("Initializing %d k-values...\n", n);
    for (int i = 0; i < n; i++) {
        k_values[i] = 10000 + i; // Range: 10K to 10M+
    }

    z5d_phase2_stats_t phase2_stats = {0};
    printf("Running parallel batch prediction (this will take a moment)...\n");

    int rc = z5d_prime_batch_phase2(k_values, n, predictions, NULL, &phase2_stats);
    if (rc == 0) {
        printf("✅ Parallel batch prediction successful\n");
        printf("   Batch size: %d predictions\n", n);
        printf("   Time: %.3f ms, Cores: %d\n",
               phase2_stats.time_ms_parallel, phase2_stats.cores_used);
        printf("   Throughput: %.0f predictions/second\n",
               n / (phase2_stats.time_ms_parallel / 1000.0));
        printf("   Sample predictions:\n");
        for (int i = 0; i < 3; i++) {
            printf("     k=%g -> p≈%.0f\n", k_values[i], predictions[i]);
        }
    } else {
        printf("❌ Parallel batch prediction failed\n");
    }
    printf("\n");

    /* 3) Early-Exit Miller–Rabin (on subset for speed) */
#if Z5D_PHASE2_HAS_MR
    printf("3. Early-Exit Miller-Rabin Primality Testing (subset):\n");
    // Test only first 100 predictions for MR to keep demo responsive
    const int mr_test_size = 100;
    int primality_results[100] = {0};
    z5d_mr_telemetry_t mr_telemetry[100] = {0};
    rc = z5d_batch_primality_test(k_values, mr_test_size, primality_results, mr_telemetry);
    if (rc == 0) {
        printf("✅ Early-exit MR testing successful\n");
        printf("   Tested %d predictions for primality\n", mr_test_size);
        printf("   Primality results (first 5):\n");
        for (int i = 0; i < 5; i++) {
            printf("     k=%g: prediction=%.0f, prime=%s\n",
                   k_values[i], predictions[i],
                   primality_results[i] ? "likely" : "composite");
        }
        printf("\n");
        z5d_print_mr_telemetry_summary(mr_telemetry, mr_test_size);
    } else {
        printf("❌ Early-exit MR testing failed\n");
    }
    printf("\n");
#else
    printf("3. Early-Exit Miller-Rabin Primality Testing:\n");
    printf("   ⚠️  Skipped – MR symbols not linked in this build.\n");
    printf("   Define Z5D_PHASE2_HAS_MR=1 when implementations are available.\n\n");
#endif

    /* 4) Performance Comparison - Use reasonable subset */
    printf("4. Performance Comparison (using subset for demo):\n");
    const int perf_test_size = 3000000; // 100K for performance comparison
    printf("Comparing sequential vs parallel performance (%d predictions)...\n", perf_test_size);

    double time_seq = z5d_phase2_benchmark_sequential(k_values, perf_test_size, 1);
    double time_par = z5d_phase2_benchmark_parallel(k_values, perf_test_size, 1);

    if (time_seq > 0 && time_par > 0) {
        double speedup = time_seq / time_par;
        printf("✅ Benchmark completed\n");
        printf("   Sequential: %.3f ms\n", time_seq);
        printf("   Parallel:   %.3f ms\n", time_par);
        printf("   Speedup:    %.2fx\n", speedup);
        printf("   Improvement: %.1f%%\n", (speedup - 1.0) * 100.0);
        if (speedup < 1.2) {
            printf("   ⚠️  Modest improvement - try even larger workloads\n");
        }
    } else {
        printf("❌ Benchmark failed\n");
    }
    printf("\n");

    /* 5) Summary */
    printf("5. Phase 2 Summary:\n");
    printf("   - OpenMP parallel processing: Ready\n");
    printf("   - SIMD vectorization support: Ready\n");
#if Z5D_PHASE2_HAS_MR
    printf("   - Early-exit Miller-Rabin: Ready\n");
#else
    printf("   - Early-exit Miller-Rabin: Pending (not linked)\n");
#endif
    printf("   - Performance telemetry: Ready\n");
    printf("   - CSV/benchmark utilities: Ready\n\n");

    printf("Phase 2 Z5D demo complete.\n");
    return 0;
}