/**
 * Phase 2 Z5D Benchmark - OpenMP + SIMD Performance Harness
 * =========================================================
 * 
 * Benchmarks Z5D predictor with parallel and vectorized optimizations.
 * Measures wall-clock time, throughput, and generates CSV telemetry.
 * 
 * Usage: ./bench_z5d_phase2 [--k-start N] [--k-stop N] [--step N] [--reps N] [--csv file.csv]
 * 
 * @author Unified Framework Team (Phase 2 Implementation)
 * @version 2.0.1 (OMP fallback deduped)
 */

#include "z5d_phase2.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/times.h>

#if defined(__APPLE__)
#include <sys/types.h>
#include <sys/sysctl.h>
#endif

/*
 * Reuse Phase 2 header's OpenMP detection/fallbacks to avoid duplicate symbols.
 * The header already defines omp_get_max_threads/thread_num/set_num_threads
 * fallbacks when <omp.h> is unavailable.
 */
#ifdef Z5D_OMP_AVAILABLE
#  define Z5D_BENCH_OMP_AVAILABLE Z5D_OMP_AVAILABLE
#else
#  define Z5D_BENCH_OMP_AVAILABLE 0
#endif

// Benchmark configuration
typedef struct {
    double k_start;
    double k_stop;
    double step;
    int reps;
    int warmup;
    char csv_file[256];
    int use_omp;
    int use_simd;
    int use_accel;
} bench_config_t;

// Benchmark results
typedef struct {
    double k;
    double prediction;
    double time_ms_sequential;
    double time_ms_parallel;
    double speedup;
    int cores_used;
    double cpu_pct;
    double ghz;
} bench_result_t;

// Default configuration
static bench_config_t default_config = {
    .k_start = 1e6,
    .k_stop = 1e7,
    .step = 1e6,
    .reps = 5,
    .warmup = 2,
    .csv_file = "perf_phase2.csv",
    .use_omp = 1,
    .use_simd = 1,
    .use_accel = 0
};

// High-precision timing
static double get_time_ms(void) {
    struct timespec ts;
#if defined(CLOCK_MONOTONIC)
    clock_gettime(CLOCK_MONOTONIC, &ts);
#else
    clock_gettime(CLOCK_REALTIME, &ts);
#endif
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

// CPU usage estimation
static double get_cpu_usage(void) {
    static struct tms prev_tms;
    static clock_t prev_time = 0;
    struct tms curr_tms;
    clock_t curr_time = times(&curr_tms);
    
    if (prev_time == 0) {
        prev_tms = curr_tms;
        prev_time = curr_time;
        return 0.0;
    }
    
    double elapsed = (double)(curr_time - prev_time) / sysconf(_SC_CLK_TCK);
    double cpu_time = (double)((curr_tms.tms_utime + curr_tms.tms_stime) -
                               (prev_tms.tms_utime + prev_tms.tms_stime)) / sysconf(_SC_CLK_TCK);

    prev_tms = curr_tms;
    prev_time = curr_time;

    return (elapsed > 0) ? (cpu_time / elapsed) * 100.0 : 0.0;
}

// Sequential Z5D batch processing
static void z5d_batch_sequential(const double* k_values, int n, double* results) {
    for (int i = 0; i < n; i++) {
        results[i] = z5d_prime(k_values[i], 0.0, 0.0, 0.3, 1);
    }
}

// Parallel Z5D batch processing (Phase 2)
static void z5d_batch_parallel(const double* k_values, int n, double* results) {
#if Z5D_BENCH_OMP_AVAILABLE
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < n; i++) {
        results[i] = z5d_prime(k_values[i], 0.0, 0.0, 0.3, 1);
    }
#else
    // Fallback to sequential if OpenMP not available
    z5d_batch_sequential(k_values, n, results);
#endif
}

// Benchmark a single k value
static bench_result_t benchmark_k(double k, const bench_config_t* config) {
    bench_result_t result = {0};
    result.k = k;
    
    // Use MUCH larger batch size to amortize OpenMP overhead
    // 100M predictions will take significant compute time vs thread overhead
    const int batch_size = 30000000;

    // Allocate memory for large batch processing
    double* k_values = malloc(batch_size * sizeof(double));
    double* results_seq = malloc(batch_size * sizeof(double));
    double* results_par = malloc(batch_size * sizeof(double));

    if (!k_values || !results_seq || !results_par) {
        printf("Error: Failed to allocate memory for large batch (%d predictions)\n", batch_size);
        // Fallback to smaller batch if memory allocation fails
        const int fallback_batch = 1000000; // 1 million fallback
        k_values = realloc(k_values, fallback_batch * sizeof(double));
        results_seq = realloc(results_seq, fallback_batch * sizeof(double));
        results_par = realloc(results_par, fallback_batch * sizeof(double));

        if (!k_values || !results_seq || !results_par) {
            printf("Error: Even fallback batch allocation failed\n");
            free(k_values); free(results_seq); free(results_par);
            return result;
        }
        printf("Using fallback batch size: %d predictions\n", fallback_batch);
        // Update batch_size to fallback value
        const int actual_batch = fallback_batch;

        for (int i = 0; i < actual_batch; i++) {
            k_values[i] = k + i * 0.001; // Small variation to avoid cache effects
        }

        // Warmup run
        printf("Warming up with %d predictions...\n", actual_batch);
        z5d_batch_sequential(k_values, actual_batch, results_seq);
        if (config->use_omp) {
            z5d_batch_parallel(k_values, actual_batch, results_par);
        }

        // Sequential timing
        printf("Running sequential benchmark (%d predictions)...\n", actual_batch);
        double start = get_time_ms();
        z5d_batch_sequential(k_values, actual_batch, results_seq);
        double end = get_time_ms();
        result.time_ms_sequential = end - start;
        result.prediction = results_seq[0];

        // Parallel timing (if enabled)
        if (config->use_omp) {
            printf("Running parallel benchmark (%d predictions, %d threads)...\n",
                   actual_batch, omp_get_max_threads());
            start = get_time_ms();
            z5d_batch_parallel(k_values, actual_batch, results_par);
            end = get_time_ms();
            result.time_ms_parallel = end - start;
            result.speedup = result.time_ms_sequential / result.time_ms_parallel;
            result.cores_used = omp_get_max_threads();
        } else {
            result.time_ms_parallel = result.time_ms_sequential;
            result.speedup = 1.0;
            result.cores_used = 1;
        }

        free(k_values); free(results_seq); free(results_par);
        return result;
    }

    // Initialize k values with small variations
    printf("Initializing %d predictions...\n", batch_size);
    for (int i = 0; i < batch_size; i++) {
        k_values[i] = k + i * 0.001; // Small variation to avoid cache effects
    }
    
    // Single warmup run with large batch
    printf("Warming up with %d predictions...\n", batch_size);
    z5d_batch_sequential(k_values, batch_size, results_seq);
    if (config->use_omp) {
        z5d_batch_parallel(k_values, batch_size, results_par);
    }
    
    // Sequential timing - single run due to large batch size
    printf("Running sequential benchmark (%d predictions)...\n", batch_size);
    double start = get_time_ms();
    z5d_batch_sequential(k_values, batch_size, results_seq);
    double end = get_time_ms();
    result.time_ms_sequential = end - start;
    result.prediction = results_seq[0]; // Use first result as representative
    
    // Parallel timing (if enabled)
    if (config->use_omp) {
#if Z5D_BENCH_OMP_AVAILABLE
        int num_threads = omp_get_max_threads();
        printf("Running parallel benchmark (%d predictions, %d threads)...\n",
               batch_size, num_threads);
#endif
        start = get_time_ms();
        z5d_batch_parallel(k_values, batch_size, results_par);
        end = get_time_ms();
        result.time_ms_parallel = end - start;
        result.speedup = result.time_ms_sequential / result.time_ms_parallel;
        
#if Z5D_BENCH_OMP_AVAILABLE
        result.cores_used = omp_get_max_threads();
#else
        result.cores_used = 1;
#endif
    } else {
        result.time_ms_parallel = result.time_ms_sequential;
        result.speedup = 1.0;
        result.cores_used = 1;
    }
    
    result.cpu_pct = get_cpu_usage();
    result.ghz = 0.0; // Placeholder

    // Cleanup
    free(k_values);
    free(results_seq);
    free(results_par);

    return result;
}

// Write CSV header
static void write_csv_header(FILE* fp) {
    fprintf(fp, "k,prediction,time_ms_sequential,time_ms_parallel,speedup,cores_used,cpu_pct,ghz,omp,simd,accel\n");
}

// Write CSV row
static void write_csv_row(FILE* fp, const bench_result_t* result, const bench_config_t* config) {
    fprintf(fp, "%.0f,%.6f,%.6f,%.6f,%.3f,%d,%.1f,%.1f,%d,%d,%d\n",
            result->k, result->prediction, 
            result->time_ms_sequential, result->time_ms_parallel, result->speedup,
            result->cores_used, result->cpu_pct, result->ghz,
            config->use_omp, config->use_simd, config->use_accel);
}

// Parse command line arguments
static int parse_args(int argc, char* argv[], bench_config_t* config) {
    *config = default_config;
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--k-start") == 0 && i+1 < argc) {
            config->k_start = atof(argv[++i]);
        } else if (strcmp(argv[i], "--k-stop") == 0 && i+1 < argc) {
            config->k_stop = atof(argv[++i]);
        } else if (strcmp(argv[i], "--step") == 0 && i+1 < argc) {
            config->step = atof(argv[++i]);
        } else if (strcmp(argv[i], "--reps") == 0 && i+1 < argc) {
            config->reps = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--warmup") == 0 && i+1 < argc) {
            config->warmup = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--csv") == 0 && i+1 < argc) {
            strncpy(config->csv_file, argv[++i], sizeof(config->csv_file)-1);
        } else if (strcmp(argv[i], "--no-omp") == 0) {
            config->use_omp = 0;
        } else if (strcmp(argv[i], "--no-simd") == 0) {
            config->use_simd = 0;
        } else if (strcmp(argv[i], "--help") == 0) {
            printf("Usage: %s [options]\n", argv[0]);
            printf("Options:\n");
            printf("  --k-start N    Start k value (default: %.0f)\n", default_config.k_start);
            printf("  --k-stop N     Stop k value (default: %.0f)\n", default_config.k_stop);
            printf("  --step N       Step size (default: %.0f)\n", default_config.step);
            printf("  --reps N       Repetitions per measurement (default: %d)\n", default_config.reps);
            printf("  --warmup N     Warmup runs (default: %d)\n", default_config.warmup);
            printf("  --csv FILE     CSV output file (default: %s)\n", default_config.csv_file);
            printf("  --no-omp       Disable OpenMP\n");
            printf("  --no-simd      Disable SIMD\n");
            printf("  --help         Show this help\n");
            return 0;
        }
    }
    return 1;
}

int main(int argc, char* argv[]) {
    bench_config_t config;
    
    if (!parse_args(argc, argv, &config)) {
        return 0;
    }
    
    printf("Z5D Phase 2 Performance Benchmark\n");
    printf("==================================\n");
    printf("Range: %.0f to %.0f (step %.0f)\n", config.k_start, config.k_stop, config.step);
    printf("Repetitions: %d (warmup: %d)\n", config.reps, config.warmup);
    printf("OpenMP: %s", config.use_omp ? "enabled" : "disabled");
#if Z5D_BENCH_OMP_AVAILABLE
    if (config.use_omp) {
        printf(" (%d threads)", omp_get_max_threads());
    }
#endif
    printf("\n");
    printf("SIMD: %s\n", config.use_simd ? "enabled" : "disabled");

#if defined(__APPLE__) && defined(__aarch64__)
    int amx_present = 0;
    size_t len = sizeof(amx_present);
    if (sysctlbyname("hw.optional.amx", &amx_present, &len, NULL, 0) == 0) {
        printf("Apple AMX: %s\n", amx_present ? "available" : "not available");
    }
#endif

    printf("CSV output: %s\n", config.csv_file);
    printf("\n");
    
    // What and Why Explanation
    printf("The benchmark:\n");
    printf("• Runs Z5D predictions sequentially (single-threaded)\n");
    printf("• Runs the same predictions in parallel (multi-threaded with OpenMP)\n");
    printf("• Measures wall-clock execution time for both approaches\n");
    printf("• Calculates speedup ratios and performance improvements\n");
    printf("• Generates CSV telemetry data for further analysis\n");
    printf("\n");
    printf("Beginning Performance Analysis...\n");
    printf("================================\n");

    // Open CSV file
    FILE* csv_fp = fopen(config.csv_file, "w");
    if (!csv_fp) {
        fprintf(stderr, "Error: Cannot open CSV file '%s'\n", config.csv_file);
        return 1;
    }
    write_csv_header(csv_fp);
    
    // Run benchmarks
    double total_speedup = 0.0;
    int sample_count = 0;
    
    printf("k-value       | Prediction    | Seq Time (ms) | Par Time (ms) | Speedup | Cores\n");
    printf("--------------|---------------|---------------|---------------|---------|-------\n");
    
    for (double k = config.k_start; k <= config.k_stop; k += config.step) {
        bench_result_t result = benchmark_k(k, &config);
        
        printf("%12.0f | %13.6f | %13.6f | %13.6f | %7.2fx | %5d\n",
               result.k, result.prediction,
               result.time_ms_sequential, result.time_ms_parallel,
               result.speedup, result.cores_used);
        
        write_csv_row(csv_fp, &result, &config);
        fflush(csv_fp);
        
        total_speedup += result.speedup;
        sample_count++;
    }
    
    fclose(csv_fp);
    
    // Summary
    double avg_speedup = sample_count > 0 ? total_speedup / sample_count : 1.0;
    double performance_improvement = (avg_speedup - 1.0) * 100.0;
    
    printf("\n");
    printf("Summary\n");
    printf("=======\n");
    printf("Average speedup: %.2fx\n", avg_speedup);
    printf("Performance improvement: %.1f%%\n", performance_improvement);
    printf("CSV data written to: %s\n", config.csv_file);
    
    return 0;
}
