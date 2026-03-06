/**
 * Inverse Mersenne Probe - Z5D-Guided Factorization Tool
 * ========================================================
 * 
 * Test and benchmark Z5D-guided inverse Mersenne probe on RSA Challenge numbers.
 * Uses Z5D predictions to guide factor search near sqrt(N) for potential
 * search space reduction vs uniform scanning.
 * 
 * @file tools/inverse_mersenne_probe.c
 * @author Unified Framework Team
 * @version 1.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <gmp.h>
#include <mpfr.h>

#ifdef _OPENMP
#include <omp.h>
#endif

// Include existing Z5D predictor
#include "../src/c/z5d_predictor.h"

/* Probe configuration */
#define PROBE_PRECISION_BITS 256
#define MILLER_RABIN_ROUNDS 5
#define MAX_JSON_OUTPUT 4096

typedef struct {
    int n_bits;
    int window_trials;
    double time_ms;
    int found;
    int factor_bits;
    int z5d_preds;
    int mr_tests;
    char* factor_str;  // For JSON output
} probe_result_t;

/* Miller-Rabin primality test for GMP integers */
static int miller_rabin_gmp(const mpz_t n, int rounds) {
    if (mpz_cmp_ui(n, 1) <= 0) return 0;
    if (mpz_cmp_ui(n, 2) == 0) return 1;
    if (mpz_even_p(n)) return 0;
    
    return mpz_probab_prime_p(n, rounds);
}

/* Check if p divides n */
static int divides(const mpz_t p, const mpz_t n) {
    mpz_t remainder;
    mpz_init(remainder);
    mpz_mod(remainder, n, p);
    int result = (mpz_cmp_ui(remainder, 0) == 0);
    mpz_clear(remainder);
    return result;
}

/* Z5D-guided factor search around sqrt(N) */
static int z5d_guided_factor_search(const mpz_t N, int window_trials, double kappa_geo, probe_result_t* result) {
    mpz_t sqrt_n, candidate, factor;
    mpfr_t n_mpfr, sqrt_mpfr;
    gmp_randstate_t rstate;
    clock_t start_time, end_time;
    
    mpz_init(sqrt_n);
    mpz_init(candidate);
    mpz_init(factor);
    mpfr_init2(n_mpfr, PROBE_PRECISION_BITS);
    mpfr_init2(sqrt_mpfr, PROBE_PRECISION_BITS);
    gmp_randinit_default(rstate);
    gmp_randseed_ui(rstate, (unsigned long)time(NULL));
    
    start_time = clock();
    
    // Convert N to MPFR and compute sqrt
    mpfr_set_z(n_mpfr, N, MPFR_RNDN);
    mpfr_sqrt(sqrt_mpfr, n_mpfr, MPFR_RNDN);
    mpfr_get_z(sqrt_n, sqrt_mpfr, MPFR_RNDN);
    
    result->n_bits = (int)mpz_sizeinbase(N, 2);
    result->window_trials = window_trials;
    result->found = 0;
    result->z5d_preds = 0;
    result->mr_tests = 0;
    result->factor_str = NULL;
    
    // Z5D-guided search around sqrt(N)
    for (int trial = 0; trial < window_trials && !result->found; trial++) {
        // Generate candidate value near sqrt(N)
        double candidate_val = mpfr_get_d(sqrt_mpfr, MPFR_RNDN) + trial - window_trials/2;
        if (candidate_val < 2.0) candidate_val = 2.0;
        
        // Use Z5D prediction to guide candidate selection
        double z5d_pred = z5d_prime(candidate_val, Z5D_DEFAULT_C, Z5D_DEFAULT_K_STAR, kappa_geo, 1);
        if (isfinite(z5d_pred) && z5d_pred > 0) {
            result->z5d_preds++;
            
            // Use Z5D prediction as a filter (e.g., only test candidates with high prediction)
            if (z5d_pred < 0.5) {
                continue;
            }
            
            // Set candidate to integer value near sqrt(N)
            mpz_set_d(candidate, candidate_val);
            
            // Make candidate odd if even
            if (mpz_even_p(candidate)) {
                mpz_add_ui(candidate, candidate, 1);
            }
            
            // Skip if candidate is 1
            if (mpz_cmp_ui(candidate, 1) <= 0) {
                continue;
            }
            
            // Test if candidate divides N
            if (divides(candidate, N)) {
                // Found a factor!
                result->found = 1;
                result->factor_bits = (int)mpz_sizeinbase(candidate, 2);
                
                // Convert factor to string for JSON output
                size_t str_size = mpz_sizeinbase(candidate, 10) + 2;
                result->factor_str = malloc(str_size);
                if (result->factor_str) {
                    mpz_get_str(result->factor_str, 10, candidate);
                }
                break;
            }
            
            // Test primality of candidate with Miller-Rabin
            if (miller_rabin_gmp(candidate, MILLER_RABIN_ROUNDS)) {
                result->mr_tests++;
            }
        }
    }
    
    end_time = clock();
    result->time_ms = ((double)(end_time - start_time) / CLOCKS_PER_SEC) * 1000.0;
    
    // Cleanup
    mpz_clear(sqrt_n);
    mpz_clear(candidate);
    mpz_clear(factor);
    mpfr_clear(n_mpfr);
    mpfr_clear(sqrt_mpfr);
    gmp_randclear(rstate);
    
    return result->found;
}

/* Output JSON result */
static void output_json_result(const probe_result_t* result) {
    printf("{");
    printf("\"n_bits\":%d,", result->n_bits);
    printf("\"window_trials\":%d,", result->window_trials);
    printf("\"time_ms\":%.3f,", result->time_ms);
    printf("\"found\":%s,", result->found ? "true" : "false");
    printf("\"factor_bits\":%d,", result->factor_bits);
    printf("\"z5d_preds\":%d,", result->z5d_preds);
    printf("\"mr_tests\":%d", result->mr_tests);
    if (result->factor_str) {
        printf(",\"factor\":\"%s\"", result->factor_str);
    }
    printf("}\n");
}

/* Print usage information */
static void print_usage(const char* program) {
    printf("Usage: %s <semiprime> <window_trials> <kappa_geo>\n", program);
    printf("\n");
    printf("Z5D-guided inverse Mersenne probe for RSA Challenge factorization.\n");
    printf("\n");
    printf("Parameters:\n");
    printf("  semiprime     - The composite number to factor (decimal)\n");
    printf("  window_trials - Number of candidates to test around sqrt(N)\n");
    printf("  kappa_geo     - Z5D geometric density parameter (e.g., 0.30769)\n");
    printf("\n");
    printf("Output: JSON line with timing and factorization results\n");
    printf("\n");
    printf("Example:\n");
    printf("  %s 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139 1024 0.30769\n", program);
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        print_usage(argv[0]);
        return 1;
    }
    
    // Parse arguments
    char* semiprime_str = argv[1];
    int window_trials = atoi(argv[2]);
    double kappa_geo = atof(argv[3]);
    
    // Validate arguments
    if (window_trials <= 0) {
        fprintf(stderr, "Error: window_trials must be positive\n");
        return 1;
    }
    
    if (kappa_geo <= 0.0 || kappa_geo > 10.0) {
        fprintf(stderr, "Error: kappa_geo must be in range (0.0, 10.0]\n");
        return 1;
    }
    
    // Initialize GMP number
    mpz_t N;
    mpz_init(N);
    
    if (mpz_set_str(N, semiprime_str, 10) != 0) {
        fprintf(stderr, "Error: Invalid decimal number format\n");
        mpz_clear(N);
        return 1;
    }
    
    if (mpz_cmp_ui(N, 1) <= 0) {
        fprintf(stderr, "Error: Number must be greater than 1\n");
        mpz_clear(N);
        return 1;
    }
    
    // Run Z5D-guided probe
    probe_result_t result;
    z5d_guided_factor_search(N, window_trials, kappa_geo, &result);
    
    // Output JSON result
    output_json_result(&result);
    
    // Cleanup
    if (result.factor_str) {
        free(result.factor_str);
    }
    mpz_clear(N);
    
    return 0;
}
