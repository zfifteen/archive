/**
 * Early-Exit Miller-Rabin with Geodesic Witnesses - Phase 2
 * ==========================================================
 * 
 * Enhanced Miller-Rabin implementation with geodesic-informed witness ordering
 * and early-exit optimization for Phase 2 Z5D implementation.
 * 
 * @file z5d_early_exit_mr.c
 * @author Unified Framework Team (Phase 2 Implementation)
 * @version 2.0.0
 */

#include "z5d_phase2.h"
// Auto-detect MPFR availability
#ifndef __has_include
#  define __has_include(x) 0
#endif
#if __has_include("gmp.h") && __has_include("mpfr.h")
#include <gmp.h>
#include <mpfr.h>
#define Z5D_HAVE_MPFR 1
#else
#define Z5D_HAVE_MPFR 0
// Provide basic fallback types
typedef struct { double value; } z5d_fallback_mpfr_t[1];
typedef struct { long long value; } z5d_fallback_mpz_t[1];
typedef int z5d_fallback_mpfr_rnd_t;
#define Z5D_FALLBACK_MPFR_RNDN 0
static inline void z5d_fallback_mpfr_init2(z5d_fallback_mpfr_t x, int prec) { (void)prec; x->value = 0.0; }
static inline void z5d_fallback_mpfr_clear(z5d_fallback_mpfr_t x) { x->value = 0.0; }
static inline void z5d_fallback_mpfr_set_d(z5d_fallback_mpfr_t rop, double op, z5d_fallback_mpfr_rnd_t rnd) { (void)rnd; rop->value = op; }
static inline double z5d_fallback_mpfr_get_d(z5d_fallback_mpfr_t op, z5d_fallback_mpfr_rnd_t rnd) { (void)rnd; return op->value; }
static inline void z5d_fallback_mpz_init(z5d_fallback_mpz_t x) { x->value = 0; }
static inline void z5d_fallback_mpz_clear(z5d_fallback_mpz_t x) { x->value = 0; }
static inline void z5d_fallback_mpz_set_ui(z5d_fallback_mpz_t rop, unsigned long op) { rop->value = (long long)op; }
static inline int z5d_fallback_mpz_probab_prime_p(z5d_fallback_mpz_t n, int reps) { (void)reps; return (n->value > 1) ? 1 : 0; }
#endif
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <assert.h>
#include <stdint.h>

#ifdef __linux__
#define _POSIX_C_SOURCE 200809L
#endif

// Early-exit MR configuration
#define MR_MAX_WITNESSES 20
#define MR_GEODESIC_WITNESSES 6
#define MR_STANDARD_WITNESSES 8

// MR telemetry structure
// High-precision timing
static double get_time_ms(void) {
#ifdef CLOCK_MONOTONIC
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
        return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
    }
#endif
    // Fallback to standard clock
    return (double)clock() / CLOCKS_PER_SEC * 1000.0;
}

#if Z5D_HAVE_MPFR
// Generate geodesic-informed witness based on signal
static void generate_geodesic_witness(mpz_t witness, const mpz_t n, double signal) {
    mpz_t tmp, n_minus_3;
    mpz_inits(tmp, n_minus_3, NULL);
    
    // Map signal to range [2, n-2]
    mpz_sub_ui(n_minus_3, n, 3);
    if (mpz_cmp_ui(n_minus_3, 1) <= 0) {
        mpz_set_ui(witness, 2);
        mpz_clears(tmp, n_minus_3, NULL);
        return;
    }
    
    // Use signal to deterministically select witness
    unsigned long hash = (unsigned long)(signal * 1000000.0);
    mpz_set_ui(tmp, hash);
    mpz_mod(tmp, tmp, n_minus_3);
    mpz_add_ui(witness, tmp, 2);
    
    mpz_clears(tmp, n_minus_3, NULL);
}

// Generate standard Miller-Rabin witnesses (small primes) 
static void generate_standard_witnesses(mpz_t* witnesses, int count) {
    const unsigned long standard_bases[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53};
    const int max_standard = sizeof(standard_bases) / sizeof(standard_bases[0]);
    
    for (int i = 0; i < count && i < max_standard; i++) {
        mpz_set_ui(witnesses[i], standard_bases[i]);
    }
}

// Generate geodesic witnesses using Z5D-informed signals
static void generate_geodesic_witnesses(mpz_t* witnesses, int count, const mpz_t n, double k) {
    // Geodesic signal 1: Golden ratio modulation
    double phi = 1.61803398874989;
    double nd = mpz_get_d(n);
    double frac = fmod(nd, phi) / phi;
    double kappa = 0.3; // Default geodesic exponent
    double signal1 = phi * pow(frac, kappa);
    
    if (count > 0) generate_geodesic_witness(witnesses[0], n, signal1);
    
    // Geodesic signal 2: Z5D curvature-informed
    if (count > 1) {
        double ln_k_plus_1 = log(k + 1.0);
        double e_squared = 7.38905609893065;
        double signal2 = (ln_k_plus_1 / e_squared) * (1.0 + 0.5 * sin(log(nd)));
        generate_geodesic_witness(witnesses[1], n, signal2);
    }
    
    // Geodesic signal 3: Prime number theorem modulation
    if (count > 2) {
        double signal3 = nd / log(nd) * 0.618033988749; // Golden ratio inverse
        generate_geodesic_witness(witnesses[2], n, signal3);
    }
    
    // Additional geodesic witnesses using various mathematical signals
    if (count > 3) {
        double signal4 = sin(nd * 0.01) * cos(k * 0.01) * 1000.0;
        generate_geodesic_witness(witnesses[3], n, signal4);
    }
    
    if (count > 4) {
        double signal5 = fmod(nd * k, 997.0); // Use large prime as modulus
        generate_geodesic_witness(witnesses[4], n, signal5);
    }
    
    if (count > 5) {
        double signal6 = pow(nd, 0.123456789) * pow(k, 0.987654321);
        generate_geodesic_witness(witnesses[5], n, signal6);
    }
}

// Single Miller-Rabin round
static int miller_rabin_round(const mpz_t n, const mpz_t witness) {
    mpz_t d, x, n_minus_1;
    mpz_inits(d, x, n_minus_1, NULL);
    
    // Write n-1 as d * 2^r
    mpz_sub_ui(d, n, 1);
    unsigned long r = 0;
    while (mpz_even_p(d)) {
        mpz_fdiv_q_2exp(d, d, 1);
        r++;
    }
    
    // Compute witness^d mod n
    mpz_powm(x, witness, d, n);
    
    // Check if x ≡ 1 (mod n)
    if (mpz_cmp_ui(x, 1) == 0) {
        mpz_clears(d, x, n_minus_1, NULL);
        return 1; // Probably prime
    }
    
    // Check if x ≡ -1 (mod n)
    mpz_sub_ui(n_minus_1, n, 1);
    if (mpz_cmp(x, n_minus_1) == 0) {
        mpz_clears(d, x, n_minus_1, NULL);
        return 1; // Probably prime
    }
    
    // Square x repeatedly
    for (unsigned long i = 0; i < r - 1; i++) {
        mpz_powm_ui(x, x, 2, n);
        if (mpz_cmp(x, n_minus_1) == 0) {
            mpz_clears(d, x, n_minus_1, NULL);
            return 1; // Probably prime
        }
    }
    
    mpz_clears(d, x, n_minus_1, NULL);
    return 0; // Composite
}

// Early-exit Miller-Rabin with geodesic witnesses first
static int miller_rabin_early_exit(const mpz_t n, double k, z5d_mr_telemetry_t* telemetry) {
    // Initialize telemetry
    if (telemetry) {
        telemetry->rounds_std = 0;
        telemetry->rounds_geo = 0;
        telemetry->early_exit_hit = 0;
        telemetry->time_ms_std = 0.0;
        telemetry->time_ms_geo = 0.0;
        telemetry->witness_type = 2; // Mixed
    }
    
    // Handle trivial cases
    if (mpz_cmp_ui(n, 2) < 0) return 0;
    if (mpz_cmp_ui(n, 2) == 0) return 1;
    if (mpz_even_p(n)) return 0;
    if (mpz_cmp_ui(n, 3) == 0) return 1;
    
    // Allocate witnesses
    mpz_t geodesic_witnesses[MR_GEODESIC_WITNESSES];
    mpz_t standard_witnesses[MR_STANDARD_WITNESSES];
    
    for (int i = 0; i < MR_GEODESIC_WITNESSES; i++) {
        mpz_init(geodesic_witnesses[i]);
    }
    for (int i = 0; i < MR_STANDARD_WITNESSES; i++) {
        mpz_init(standard_witnesses[i]);
    }
    
    // Generate witnesses
    generate_geodesic_witnesses(geodesic_witnesses, MR_GEODESIC_WITNESSES, n, k);
    generate_standard_witnesses(standard_witnesses, MR_STANDARD_WITNESSES);
    
    // Test geodesic witnesses first (early exit opportunity)
    double start_geo = get_time_ms();
    for (int i = 0; i < MR_GEODESIC_WITNESSES; i++) {
        if (telemetry) telemetry->rounds_geo++;
        
        if (miller_rabin_round(n, geodesic_witnesses[i]) == 0) {
            // Composite detected early!
            if (telemetry) {
                telemetry->early_exit_hit = 1;
                telemetry->time_ms_geo = get_time_ms() - start_geo;
            }
            
            // Clean up
            for (int j = 0; j < MR_GEODESIC_WITNESSES; j++) mpz_clear(geodesic_witnesses[j]);
            for (int j = 0; j < MR_STANDARD_WITNESSES; j++) mpz_clear(standard_witnesses[j]);
            
            return 0; // Composite
        }
    }
    double end_geo = get_time_ms();
    if (telemetry) telemetry->time_ms_geo = end_geo - start_geo;
    
    // Continue with standard witnesses
    double start_std = get_time_ms();
    for (int i = 0; i < MR_STANDARD_WITNESSES; i++) {
        if (telemetry) telemetry->rounds_std++;
        
        if (miller_rabin_round(n, standard_witnesses[i]) == 0) {
            if (telemetry) telemetry->time_ms_std = get_time_ms() - start_std;
            
            // Clean up
            for (int j = 0; j < MR_GEODESIC_WITNESSES; j++) mpz_clear(geodesic_witnesses[j]);
            for (int j = 0; j < MR_STANDARD_WITNESSES; j++) mpz_clear(standard_witnesses[j]);
            
            return 0; // Composite
        }
    }
    double end_std = get_time_ms();
    if (telemetry) telemetry->time_ms_std = end_std - start_std;
    
    // Clean up
    for (int i = 0; i < MR_GEODESIC_WITNESSES; i++) mpz_clear(geodesic_witnesses[i]);
    for (int i = 0; i < MR_STANDARD_WITNESSES; i++) mpz_clear(standard_witnesses[i]);
    
    return 1; // Probably prime
}

// Batch primality testing with early-exit MR and Phase-2 parity enforcement
int z5d_batch_primality_test(const double* k_values, int n, int* results, 
                            z5d_mr_telemetry_t* telemetry_array) {
    if (!k_values || !results || n <= 0) return -1;
    
    for (int i = 0; i < n; i++) {
        // Generate candidate using Z5D predictor
        double prediction = z5d_prime(k_values[i], 0.0, 0.0, 0.3, 1);
        
        // Phase-2 parity enforcement: ensure candidate is odd
        uint64_t candidate_int = (uint64_t)round(prediction);
        candidate_int |= 1ULL;  // enforce odd (never ^= 1)
        
        // Hard pre-MR guard
#ifndef NDEBUG
        assert((candidate_int & 1ULL) == 1ULL);
#endif
        
        // Convert to mpz_t for Miller-Rabin
        mpz_t candidate;
        mpz_init(candidate);
        mpz_set_ui(candidate, candidate_int);
        
        // Apply early-exit Miller-Rabin
        z5d_mr_telemetry_t tel_internal;
        z5d_mr_telemetry_t* tel = telemetry_array ? &tel_internal : NULL;
        results[i] = miller_rabin_early_exit(candidate, k_values[i], tel);
        
        // Copy telemetry if requested
        if (telemetry_array && tel) {
            telemetry_array[i].rounds_std = tel->rounds_std;
            telemetry_array[i].rounds_geo = tel->rounds_geo;
            telemetry_array[i].early_exit_hit = tel->early_exit_hit;
            telemetry_array[i].time_ms_std = tel->time_ms_std;
            telemetry_array[i].time_ms_geo = tel->time_ms_geo;
            telemetry_array[i].witness_type = tel->witness_type;
        }
        
        mpz_clear(candidate);
    }
    
    return 0;
}

// Statistics and reporting functions
void z5d_print_mr_telemetry_summary(const z5d_mr_telemetry_t* telemetry, int n) {
    if (!telemetry || n <= 0) return;
    
    unsigned long total_rounds_geo = 0;
    unsigned long total_rounds_std = 0;
    int total_early_exits = 0;
    double total_time_geo = 0.0;
    double total_time_std = 0.0;
    
    for (int i = 0; i < n; i++) {
        total_rounds_geo += telemetry[i].rounds_geo;
        total_rounds_std += telemetry[i].rounds_std;
        total_early_exits += telemetry[i].early_exit_hit;
        total_time_geo += telemetry[i].time_ms_geo;
        total_time_std += telemetry[i].time_ms_std;
    }
    
    printf("Miller-Rabin Early-Exit Telemetry Summary\n");
    printf("=========================================\n");
    printf("Total tests: %d\n", n);
    printf("Geodesic rounds: %lu (avg: %.1f per test)\n", 
           total_rounds_geo, (double)total_rounds_geo / n);
    printf("Standard rounds: %lu (avg: %.1f per test)\n", 
           total_rounds_std, (double)total_rounds_std / n);
    printf("Early exits: %d (%.1f%%)\n", 
           total_early_exits, (double)total_early_exits / n * 100.0);
    printf("Average geo time: %.3f ms\n", total_time_geo / n);
    printf("Average std time: %.3f ms\n", total_time_std / n);
    printf("Total rounds saved by early exit: %d\n", 
           total_early_exits * MR_STANDARD_WITNESSES);
}

#else // Z5D_HAVE_MPFR not available - provide simple fallbacks

// Fallback implementations when GMP/MPFR not available
int z5d_batch_primality_test(const double* k_values, int n, int* results, 
                            z5d_mr_telemetry_t* telemetry_array) {
    // Simple fallback - use basic primality test on rounded predictions
    if (!k_values || !results || n <= 0) return -1;
    
    for (int i = 0; i < n; i++) {
        double prediction = z5d_prime(k_values[i], 0.0, 0.0, 0.3, 1);
        long candidate = (long)round(prediction);
        
        // Simple trial division up to sqrt(candidate)
        results[i] = 1; // Assume prime unless proven otherwise
        if (candidate < 2) {
            results[i] = 0;
        } else if (candidate == 2) {
            results[i] = 1;
        } else if (candidate % 2 == 0) {
            results[i] = 0;
        } else {
            for (long d = 3; d * d <= candidate; d += 2) {
                if (candidate % d == 0) {
                    results[i] = 0;
                    break;
                }
            }
        }
        
        // Clear telemetry if provided
        if (telemetry_array) {
            telemetry_array[i].rounds_geo = 0;
            telemetry_array[i].rounds_std = 1;
            telemetry_array[i].early_exit_hit = 0;
            telemetry_array[i].time_ms_geo = 0.0;
            telemetry_array[i].time_ms_std = 1.0;
        }
    }
    
    return 0;
}

void z5d_print_mr_telemetry_summary(const z5d_mr_telemetry_t* telemetry, int n) {
    if (!telemetry || n <= 0) {
        printf("No telemetry data available\n");
        return;
    }
    
    printf("Miller-Rabin Early-Exit Telemetry Summary\n");
    printf("=========================================\n");
    printf("Total tests: %d\n", n);
    
    // Calculate aggregated statistics
    unsigned long total_std_rounds = 0;
    unsigned long total_geo_rounds = 0;
    int early_exits = 0;
    double total_std_time = 0.0;
    double total_geo_time = 0.0;
    
    for (int i = 0; i < n; i++) {
        total_std_rounds += telemetry[i].rounds_std;
        total_geo_rounds += telemetry[i].rounds_geo;
        if (telemetry[i].early_exit_hit) early_exits++;
        total_std_time += telemetry[i].time_ms_std;
        total_geo_time += telemetry[i].time_ms_geo;
    }
    
    printf("Standard MR rounds: %lu (avg: %.1f per test)\n", 
           total_std_rounds, (double)total_std_rounds / n);
    printf("Geodesic MR rounds: %lu (avg: %.1f per test)\n", 
           total_geo_rounds, (double)total_geo_rounds / n);
    printf("Early exits: %d (%.1f%%)\n", 
           early_exits, 100.0 * early_exits / n);
    printf("Standard MR time: %.3f ms (avg: %.3f ms per test)\n", 
           total_std_time, total_std_time / n);
    printf("Geodesic MR time: %.3f ms (avg: %.3f ms per test)\n", 
           total_geo_time, total_geo_time / n);
    
    if (total_std_time > 0.0 && total_geo_time > 0.0) {
        printf("Speedup factor: %.2fx\n", total_std_time / total_geo_time);
    }
}

#endif // Z5D_HAVE_MPFR