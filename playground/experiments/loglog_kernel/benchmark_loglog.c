/**
 * @file benchmark_loglog.c
 * @brief Benchmark suite for loglog_mpfr library
 */

#include "loglog_mpfr.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>

/* Get current time in microseconds */
static double get_time_us(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (double)tv.tv_sec * 1000000.0 + (double)tv.tv_usec;
}

/* Benchmark: Small integer values */
void benchmark_small_integers(void) {
    mpz_t n;
    mpfr_t result;
    mpfr_prec_t prec = 256;
    int iterations = 10000;
    double start, end;
    
    mpz_init(n);
    mpfr_init2(result, prec);
    
    printf("\n--- Small Integers Benchmark ---\n");
    printf("Iterations: %d\n", iterations);
    printf("Precision: %lu bits\n\n", (unsigned long)prec);
    
    /* Benchmark for various small values */
    unsigned long values[] = {2, 10, 100, 1000, 10000};
    int num_values = sizeof(values) / sizeof(values[0]);
    
    for (int i = 0; i < num_values; i++) {
        mpz_set_ui(n, values[i]);
        
        start = get_time_us();
        for (int j = 0; j < iterations; j++) {
            loglog_mpfr_int(result, n, prec, MPFR_RNDN);
        }
        end = get_time_us();
        
        double elapsed = end - start;
        double per_call = elapsed / iterations;
        
        printf("n = %-6lu: %.2f μs total, %.3f μs per call, %.0f ops/sec\n",
               values[i], elapsed, per_call, 1000000.0 / per_call);
    }
    
    mpz_clear(n);
    mpfr_clear(result);
}

/* Benchmark: Large integer values */
void benchmark_large_integers(void) {
    mpz_t n;
    mpfr_t result;
    mpfr_prec_t prec = 512;
    int iterations = 1000;
    double start, end;
    
    mpz_init(n);
    mpfr_init2(result, prec);
    
    printf("\n--- Large Integers Benchmark ---\n");
    printf("Iterations: %d\n", iterations);
    printf("Precision: %lu bits\n\n", (unsigned long)prec);
    
    /* Benchmark for powers of 2 */
    unsigned long exponents[] = {64, 128, 256, 512, 1024};
    int num_exponents = sizeof(exponents) / sizeof(exponents[0]);
    
    for (int i = 0; i < num_exponents; i++) {
        mpz_ui_pow_ui(n, 2, exponents[i]);
        
        start = get_time_us();
        for (int j = 0; j < iterations; j++) {
            loglog_mpfr_int(result, n, prec, MPFR_RNDN);
        }
        end = get_time_us();
        
        double elapsed = end - start;
        double per_call = elapsed / iterations;
        
        printf("n = 2^%-4lu: %.2f μs total, %.3f μs per call, %.0f ops/sec\n",
               exponents[i], elapsed, per_call, 1000000.0 / per_call);
    }
    
    mpz_clear(n);
    mpfr_clear(result);
}

/* Benchmark: Varying precision */
void benchmark_varying_precision(void) {
    mpfr_t x, result;
    int iterations = 1000;
    double start, end;
    
    printf("\n--- Varying Precision Benchmark ---\n");
    printf("Iterations: %d\n", iterations);
    printf("Input: x = 1000\n\n");
    
    mpfr_prec_t precisions[] = {64, 128, 256, 512, 1024, 2048};
    int num_precisions = sizeof(precisions) / sizeof(precisions[0]);
    
    for (int i = 0; i < num_precisions; i++) {
        mpfr_prec_t prec = precisions[i];
        
        mpfr_init2(x, prec);
        mpfr_init2(result, prec);
        mpfr_set_ui(x, 1000, MPFR_RNDN);
        
        start = get_time_us();
        for (int j = 0; j < iterations; j++) {
            loglog_mpfr_real(result, x, prec, MPFR_RNDN);
        }
        end = get_time_us();
        
        double elapsed = end - start;
        double per_call = elapsed / iterations;
        
        printf("Precision %-4lu bits: %.2f μs total, %.3f μs per call, %.0f ops/sec\n",
               (unsigned long)prec, elapsed, per_call, 1000000.0 / per_call);
        
        mpfr_clear(x);
        mpfr_clear(result);
    }
}

/* Benchmark: Different rounding modes */
void benchmark_rounding_modes(void) {
    mpfr_t x, result;
    mpfr_prec_t prec = 256;
    int iterations = 5000;
    double start, end;
    
    mpfr_init2(x, prec);
    mpfr_init2(result, prec);
    mpfr_set_ui(x, 1000, MPFR_RNDN);
    
    printf("\n--- Rounding Modes Benchmark ---\n");
    printf("Iterations: %d\n", iterations);
    printf("Precision: %lu bits\n", (unsigned long)prec);
    printf("Input: x = 1000\n\n");
    
    struct {
        mpfr_rnd_t mode;
        const char* name;
    } modes[] = {
        {MPFR_RNDN, "MPFR_RNDN (nearest)"},
        {MPFR_RNDZ, "MPFR_RNDZ (toward zero)"},
        {MPFR_RNDU, "MPFR_RNDU (toward +inf)"},
        {MPFR_RNDD, "MPFR_RNDD (toward -inf)"}
    };
    int num_modes = sizeof(modes) / sizeof(modes[0]);
    
    for (int i = 0; i < num_modes; i++) {
        start = get_time_us();
        for (int j = 0; j < iterations; j++) {
            loglog_mpfr_real(result, x, prec, modes[i].mode);
        }
        end = get_time_us();
        
        double elapsed = end - start;
        double per_call = elapsed / iterations;
        
        printf("%-26s: %.2f μs total, %.3f μs per call, %.0f ops/sec\n",
               modes[i].name, elapsed, per_call, 1000000.0 / per_call);
    }
    
    mpfr_clear(x);
    mpfr_clear(result);
}

/* Benchmark: Real number inputs */
void benchmark_real_numbers(void) {
    mpfr_t x, result, e_base, temp;
    mpfr_prec_t prec = 256;
    int iterations = 5000;
    double start, end;
    
    printf("\n--- Real Number Inputs Benchmark ---\n");
    printf("Iterations: %d\n", iterations);
    printf("Precision: %lu bits\n\n", (unsigned long)prec);
    
    mpfr_init2(x, prec);
    mpfr_init2(result, prec);
    mpfr_init2(e_base, prec);
    mpfr_init2(temp, prec);
    
    /* Compute e = exp(1) for later use */
    mpfr_set_ui(e_base, 1, MPFR_RNDN);
    mpfr_exp(e_base, e_base, MPFR_RNDN);
    
    /* e */
    mpfr_set(x, e_base, MPFR_RNDN);
    start = get_time_us();
    for (int j = 0; j < iterations; j++) {
        loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    }
    end = get_time_us();
    printf("x = e       : %.2f μs total, %.3f μs per call\n",
           end - start, (end - start) / iterations);
    
    /* π */
    mpfr_const_pi(x, MPFR_RNDN);
    start = get_time_us();
    for (int j = 0; j < iterations; j++) {
        loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    }
    end = get_time_us();
    printf("x = π       : %.2f μs total, %.3f μs per call\n",
           end - start, (end - start) / iterations);
    
    /* e^e */
    mpfr_pow(x, e_base, e_base, MPFR_RNDN);
    start = get_time_us();
    for (int j = 0; j < iterations; j++) {
        loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    }
    end = get_time_us();
    printf("x = e^e     : %.2f μs total, %.3f μs per call\n",
           end - start, (end - start) / iterations);
    
    /* π^π */
    mpfr_const_pi(x, MPFR_RNDN);
    mpfr_set(temp, x, MPFR_RNDN);
    mpfr_pow(x, temp, x, MPFR_RNDN);
    start = get_time_us();
    for (int j = 0; j < iterations; j++) {
        loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    }
    end = get_time_us();
    printf("x = π^π     : %.2f μs total, %.3f μs per call\n",
           end - start, (end - start) / iterations);
    
    mpfr_clear(temp);
    mpfr_clear(e_base);
    mpfr_clear(x);
    mpfr_clear(result);
}

int main(void) {
    printf("====================================\n");
    printf("  LogLog MPFR Benchmark Suite\n");
    printf("====================================\n");
    
    printf("\nLibrary version: %s\n", loglog_mpfr_version());
    printf("GMP version: %s\n", gmp_version);
    printf("MPFR version: %s\n", mpfr_get_version());
    
    /* Run all benchmarks */
    benchmark_small_integers();
    benchmark_large_integers();
    benchmark_varying_precision();
    benchmark_rounding_modes();
    benchmark_real_numbers();
    
    printf("\n====================================\n");
    printf("  Benchmark Complete\n");
    printf("====================================\n");
    
    return 0;
}
