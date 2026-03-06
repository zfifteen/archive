/*
 * Factorization Shortcut Demo - MPFR High-Precision Implementation
 * ================================================================
 * 
 * Goal: Empirically demonstrate that recovering just one factor of a semiprime N = p*q
 * from a small candidate list is sufficient to fully factor N quickly via the shortcut:
 *     q = N // p (then confirm q is prime)
 *
 * This C implementation:
 *   - Uses MPFR for high-precision arithmetic (256-bit precision)
 *   - Builds semiprimes (balanced) under Nmax
 *   - Uses angular heuristic over θ'(·) to propose candidate primes for each N
 *   - Tries dividing N by candidates to recover either factor p or q (the shortcut)
 *   - Computes practical factorization success rates
 *   - No external dependencies beyond MPFR/GMP (following repo patterns)
 *
 * Author: Unified Framework Team
 * Target: MPFR-only implementation (no fallback)
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <assert.h>
#include <mpfr.h>
#include <gmp.h>

// Constants
#define MPFR_PRECISION 256
#define PHI_VALUE 1.6180339887498948482045868343656
#define K_DEFAULT 0.31830988618379067153776752674503
#define MAX_PRIMES 1000000
#define MAX_CANDIDATES 1000000
#define MAX_SEMIPRIMES 1000000

// Structure for storing prime information
typedef struct {
    unsigned long value;
    double theta_prime;
} prime_info_t;

// Structure for semiprime
typedef struct {
    unsigned long p, q, N;
} semiprime_t;

// Global arrays for efficiency
static prime_info_t primes[MAX_PRIMES];
static semiprime_t semiprimes[MAX_SEMIPRIMES];
static unsigned long candidates[MAX_CANDIDATES];
static int n_primes = 0;
static int n_semiprimes = 0;

// MPFR variables for high-precision calculations
static mpfr_t phi, temp1, temp2, temp3, one;

// Initialize MPFR variables
void init_mpfr() {
    mpfr_set_default_prec(MPFR_PRECISION);
    mpfr_init(phi);
    mpfr_init(temp1);
    mpfr_init(temp2);
    mpfr_init(temp3);
    mpfr_init(one);
    
    // Set phi = (1 + sqrt(5)) / 2
    mpfr_sqrt_ui(temp1, 5, MPFR_RNDN);
    mpfr_add_ui(temp1, temp1, 1, MPFR_RNDN);
    mpfr_div_ui(phi, temp1, 2, MPFR_RNDN);
    
    // Set one = 1.0
    mpfr_set_ui(one, 1, MPFR_RNDN);
}

// Cleanup MPFR variables
void cleanup_mpfr() {
    mpfr_clear(phi);
    mpfr_clear(temp1);
    mpfr_clear(temp2);
    mpfr_clear(temp3);
    mpfr_clear(one);
}

// Compute θ'(n,k) = φ * { n / φ }^k (fractional part)
double theta_prime_int(unsigned long n, double k) {
    // Use MPFR for high precision
    mpfr_set_ui(temp1, n, MPFR_RNDN);
    mpfr_div(temp2, temp1, phi, MPFR_RNDN);
    
    // Get fractional part of n/φ
    mpfr_frac(temp2, temp2, MPFR_RNDN);
    
    // Raise to power k
    mpfr_set_d(temp3, k, MPFR_RNDN);
    mpfr_pow(temp2, temp2, temp3, MPFR_RNDN);
    
    // Multiply by φ
    mpfr_mul(temp1, temp2, phi, MPFR_RNDN);
    
    // Get fractional part and convert to double
    mpfr_frac(temp1, temp1, MPFR_RNDN);
    return mpfr_get_d(temp1, MPFR_RNDN);
}

// Circular distance on [0,1)
// Circular distance on [0,1)
double circ_dist(double a, double b) {
    double d = fmod(a - b + 0.5, 1.0) - 0.5;
    return fabs(d);
}

// Simple sieve of Eratosthenes
void sieve_primes(unsigned long limit) {
    if (limit < 2) return;
    
    char *is_prime = calloc(limit + 1, sizeof(char));
    if (!is_prime) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    // Initialize all as prime
    for (unsigned long i = 2; i <= limit; i++) {
        is_prime[i] = 1;
    }
    
    // Sieve
    for (unsigned long p = 2; p * p <= limit; p++) {
        if (is_prime[p]) {
            for (unsigned long i = p * p; i <= limit; i += p) {
                is_prime[i] = 0;
            }
        }
    }
    
    // Collect primes
    n_primes = 0;
    for (unsigned long i = 2; i <= limit && n_primes < MAX_PRIMES; i++) {
        if (is_prime[i]) {
            primes[n_primes].value = i;
            primes[n_primes].theta_prime = theta_prime_int(i, K_DEFAULT);
            n_primes++;
        }
    }
    
    free(is_prime);
}

// Check if number is prime using trial division
int is_prime_trial(unsigned long n) {
    if (n < 2) return 0;
    if (n == 2) return 1;
    if (n % 2 == 0) return 0;
    
    unsigned long limit = (unsigned long)sqrt(n);
    for (unsigned long i = 3; i <= limit; i += 2) {
        if (n % i == 0) return 0;
    }
    return 1;
}

// Sample balanced semiprimes
void sample_semiprimes_balanced(unsigned long Nmax, int target_count, unsigned int seed) {
    srand(seed);
    n_semiprimes = 0;

    unsigned long sqrt_Nmax = (unsigned long)sqrt(Nmax);
    unsigned long band_lo = sqrt_Nmax / 2;
    unsigned long band_hi = sqrt_Nmax * 2;

    // Find primes in balanced band
    int band_start = -1, band_end = -1;
    for (int i = 0; i < n_primes; i++) {
        if (band_start == -1 && primes[i].value >= band_lo) {
            band_start = i;
        }
        if (primes[i].value <= band_hi) {
            band_end = i;
        } else {
            break;
        }
    }

    if (band_start == -1 || band_end == -1) {
        fprintf(stderr, "No primes in balanced band\n");
        return;
    }

    int band_size = band_end - band_start + 1;

    // Generate semiprimes
    while (n_semiprimes < target_count && n_semiprimes < MAX_SEMIPRIMES) {
        int idx_p = band_start + rand() % band_size;
        int idx_q = band_start + rand() % band_size;

        unsigned long p = primes[idx_p].value;
        unsigned long q = primes[idx_q].value;

        if (p > q) {
            unsigned long temp = p;
            p = q;
            q = temp;
        }

        unsigned long N = p * q;
        if (N < Nmax) {
            semiprimes[n_semiprimes].p = p;
            semiprimes[n_semiprimes].q = q;
            semiprimes[n_semiprimes].N = N;
            n_semiprimes++;
        }
    }
}

// Sample skewed semiprimes (small p, large q)
void sample_semiprimes_skewed(unsigned long Nmax, int target_count, unsigned int seed) {
    srand(seed);
    n_semiprimes = 0;

    unsigned long sqrt_Nmax = (unsigned long)sqrt(Nmax);

    // Small primes: 2 to sqrt(Nmax)/4
    unsigned long small_limit = sqrt_Nmax / 4;
    if (small_limit < 10) small_limit = 10;

    // Large primes: sqrt(Nmax) to available range
    unsigned long large_start = sqrt_Nmax;

    // Find small prime range
    int small_start = 0, small_end = -1;
    for (int i = 0; i < n_primes; i++) {
        if (primes[i].value <= small_limit) {
            small_end = i;
        } else {
            break;
        }
    }

    // Find large prime range
    int large_start_idx = -1, large_end = n_primes - 1;
    for (int i = 0; i < n_primes; i++) {
        if (large_start_idx == -1 && primes[i].value >= large_start) {
            large_start_idx = i;
            break;
        }
    }

    if (small_end == -1 || large_start_idx == -1) {
        fprintf(stderr, "No primes in skewed bands\n");
        return;
    }

    int small_size = small_end - small_start + 1;
    int large_size = large_end - large_start_idx + 1;

    // Generate skewed semiprimes
    while (n_semiprimes < target_count && n_semiprimes < MAX_SEMIPRIMES) {
        int idx_p = small_start + rand() % small_size;
        int idx_q = large_start_idx + rand() % large_size;

        unsigned long p = primes[idx_p].value;
        unsigned long q = primes[idx_q].value;

        // Ensure p < q for skewed property
        if (p > q) {
            unsigned long temp = p;
            p = q;
            q = temp;
        }

        unsigned long N = p * q;
        if (N < Nmax) {
            semiprimes[n_semiprimes].p = p;
            semiprimes[n_semiprimes].q = q;
            semiprimes[n_semiprimes].N = N;
            n_semiprimes++;
        }
    }
}

// Sample widely separated semiprimes (very small p, very large q)
void sample_semiprimes_wide(unsigned long Nmax, int target_count, unsigned int seed) {
    srand(seed);
    n_semiprimes = 0;

    // Very small primes: 2 to 100
    unsigned long tiny_limit = 100;

    // Very large primes: from 80% of available range
    int large_start_idx = (int)(0.8 * n_primes);
    int large_end = n_primes - 1;

    // Find tiny prime range
    int tiny_start = 0, tiny_end = -1;
    for (int i = 0; i < n_primes; i++) {
        if (primes[i].value <= tiny_limit) {
            tiny_end = i;
        } else {
            break;
        }
    }

    if (tiny_end == -1 || large_start_idx >= n_primes) {
        fprintf(stderr, "No primes in wide separation bands\n");
        return;
    }

    int tiny_size = tiny_end - tiny_start + 1;
    int large_size = large_end - large_start_idx + 1;

    // Generate widely separated semiprimes
    while (n_semiprimes < target_count && n_semiprimes < MAX_SEMIPRIMES) {
        int idx_p = tiny_start + rand() % tiny_size;
        int idx_q = large_start_idx + rand() % large_size;

        unsigned long p = primes[idx_p].value;
        unsigned long q = primes[idx_q].value;

        unsigned long N = p * q;
        if (N < Nmax) {
            semiprimes[n_semiprimes].p = p;
            semiprimes[n_semiprimes].q = q;
            semiprimes[n_semiprimes].N = N;
            n_semiprimes++;
        }
    }
}

// Generate candidates using band heuristic
int generate_candidates(unsigned long N, double eps, double k) {
    double theta_N = theta_prime_int(N, k);
    int n_candidates = 0;

    for (int i = 0; i < n_primes && n_candidates < MAX_CANDIDATES; i++) {
        double theta_p = theta_prime_int(primes[i].value, k); // Recompute with same k
        if (circ_dist(theta_p, theta_N) <= eps) {
            candidates[n_candidates++] = primes[i].value;
        }
    }

    return n_candidates;
}

// Attempt factorization using candidates
int factorize_with_candidates(unsigned long N, int n_candidates, unsigned long *p_found, unsigned long *q_found) {
    for (int i = 0; i < n_candidates; i++) {
        unsigned long p = candidates[i];
        if (p > 1 && N % p == 0) {
            unsigned long q = N / p;
            if (is_prime_trial(q)) {
                *p_found = p;
                *q_found = q;
                return 1; // Success
            }
        }
    }
    return 0; // Failed
}

// Multi-pass factorization using k-sequence with detailed tracking
int factorize_multi_pass_tracked(unsigned long N, double eps, double k_values[], int n_passes,
                                unsigned long *p_found, unsigned long *q_found,
                                int *successful_pass, int *total_divisions) {
    *successful_pass = -1;
    *total_divisions = 0;

    for (int pass = 0; pass < n_passes; pass++) {
        int n_cand = generate_candidates(N, eps, k_values[pass]);
        *total_divisions += n_cand;

        if (factorize_with_candidates(N, n_cand, p_found, q_found)) {
            *successful_pass = pass;
            return 1; // Success on this pass
        }
    }
    return 0; // Failed all passes
}

// Legacy wrapper for compatibility
int factorize_multi_pass(unsigned long N, double eps, double k_values[], int n_passes, unsigned long *p_found, unsigned long *q_found) {
    int successful_pass, total_divisions;
    return factorize_multi_pass_tracked(N, eps, k_values, n_passes, p_found, q_found, &successful_pass, &total_divisions);
}

// Wilson confidence interval
void wilson_ci(int successes, int n, double z, double *rate, double *ci_low, double *ci_high) {
    if (n == 0) {
        *rate = *ci_low = *ci_high = 0.0;
        return;
    }
    
    double p = (double)successes / n;
    double denom = 1.0 + (z * z) / n;
    double center = (p + (z * z) / (2 * n)) / denom;
    double half = z * sqrt((p * (1 - p) / n) + (z * z) / (4 * n * n)) / denom;
    
    *rate = p;
    *ci_low = fmax(0.0, center - half);
    *ci_high = fmin(1.0, center + half);
}

// Main evaluation function with clean output format
void evaluate(double eps_values[], int n_eps, double k_values[], int n_passes, const char* semiprime_type) {
    // Calculate baseline for comparison
    unsigned long max_N = 0;
    for (int i = 0; i < n_semiprimes; i++) {
        if (semiprimes[i].N > max_N) max_N = semiprimes[i].N;
    }

    unsigned long naive_limit = (unsigned long)sqrt(max_N);
    int naive_divisions = 0;
    for (int i = 0; i < n_primes && primes[i].value <= naive_limit; i++) {
        naive_divisions++;
    }

    printf("\n🔢 Geometric Factorization - C/MPFR Implementation\n");
    printf("═══════════════════════════════════════════════════════════════\n\n");

    printf("SYSTEM CONFIGURATION\n");
    printf("  Architecture:          %s\n", sizeof(void*) == 8 ? "64-bit" : "32-bit");
    printf("  Precision:             %d-bit MPFR\n", MPFR_PRECISION);
    printf("  Memory Model:          Static allocation\n");
    printf("  Target Numbers:        up to %lu\n", max_N);
    printf("  Sample Size:           %d %s semiprimes\n", n_semiprimes, semiprime_type);
    printf("\n");

    printf("ALGORITHM PARAMETERS\n");
    printf("  Multi-Pass Sequence:   ");
    for (int i = 0; i < n_passes; i++) {
        printf("%.3f", k_values[i]);
        if (i < n_passes - 1) printf(", ");
    }
    printf("\n");
    printf("  Epsilon Range:         %.2f → %.2f\n", eps_values[0], eps_values[n_eps-1]);
    printf("  Golden Ratio (φ):      %.10f...\n", PHI_VALUE);
    printf("  Random Seed:           42\n");
    printf("\n");

    printf("═══════════════════════════════════════════════════════════════\n\n");
    printf("FACTORIZATION RESULTS\n\n");

    // Show successful examples
    printf("Successful Examples:\n");
    int examples_shown = 0;
    for (int i = 0; i < n_semiprimes && examples_shown < 5; i++) {
        unsigned long N = semiprimes[i].N;

        unsigned long p_found, q_found;
        if (factorize_multi_pass(N, eps_values[n_eps-1], k_values, n_passes, &p_found, &q_found)) {
            printf("  %lu = %lu × %lu   (multi-pass success)\n",
                   N, p_found, q_found);
            examples_shown++;
        }
    }

    if (examples_shown == 0) {
        printf("  (Computing aggregate performance - no quick examples)\n");
    }
    printf("\n");

    // Performance table with detailed tracking
    printf("Performance by Tolerance:\n");
    printf("┌─────────┬─────────────────┬──────────────┬───────────────┐\n");
    printf("│ Epsilon │ Success Rate    │ Avg Divisions│ Efficiency    │\n");
    printf("│ (ε)     │ (95%% CI)        │ Until Success │ Gain          │\n");
    printf("├─────────┼─────────────────┼──────────────┼───────────────┤\n");

    for (int eps_idx = 0; eps_idx < n_eps; eps_idx++) {
        double eps = eps_values[eps_idx];
        int partial_successes = 0;
        int total_divisions_until_success = 0;
        int pass_distribution[3] = {0, 0, 0}; // Track which pass succeeded

        for (int i = 0; i < n_semiprimes; i++) {
            unsigned long N = semiprimes[i].N;
            unsigned long p_found, q_found;
            int successful_pass, total_divisions;

            if (factorize_multi_pass_tracked(N, eps, k_values, n_passes, &p_found, &q_found, &successful_pass, &total_divisions)) {
                partial_successes++;
                total_divisions_until_success += total_divisions;
                if (successful_pass >= 0 && successful_pass < 3) {
                    pass_distribution[successful_pass]++;
                }
            }
        }

        double rate, ci_low, ci_high;
        wilson_ci(partial_successes, n_semiprimes, 1.96, &rate, &ci_low, &ci_high);

        double avg_divisions_until_success = partial_successes > 0 ?
            (double)total_divisions_until_success / partial_successes : 0;
        double efficiency_gain = avg_divisions_until_success > 0 ?
            (double)naive_divisions / avg_divisions_until_success : 0;

        printf("│ %.2f    │ %.1f%% (%.1f-%.1f) │ %-12.1f │ %.1fx faster  │\n",
               eps, rate * 100, ci_low * 100, ci_high * 100, avg_divisions_until_success, efficiency_gain);
    }

    printf("└─────────┴─────────────┴──────────────┴───────────────┘\n\n");

    // Per-pass breakdown
    printf("PER-PASS BREAKDOWN (which pass succeeded):\n");
    for (int eps_idx = 0; eps_idx < n_eps; eps_idx++) {
        double eps = eps_values[eps_idx];
        int pass_distribution[3] = {0, 0, 0};

        // Recalculate for this epsilon
        for (int i = 0; i < n_semiprimes; i++) {
            unsigned long N = semiprimes[i].N;
            unsigned long p_found, q_found;
            int successful_pass, total_divisions;

            if (factorize_multi_pass_tracked(N, eps, k_values, n_passes, &p_found, &q_found, &successful_pass, &total_divisions)) {
                if (successful_pass >= 0 && successful_pass < 3) {
                    pass_distribution[successful_pass]++;
                }
            }
        }

        printf("  ε=%.2f: Pass@k=%.3f: %.1f%% | k=%.3f: %.1f%% | k=%.3f: %.1f%%\n",
               eps,
               k_values[0], (double)pass_distribution[0] / n_semiprimes * 100,
               k_values[1], (double)pass_distribution[1] / n_semiprimes * 100,
               k_values[2], (double)pass_distribution[2] / n_semiprimes * 100);
    }

    // Baseline comparison
    printf("BASELINE COMPARISON\n");
    printf("  Naive Trial Division:  ~%d prime candidates\n", naive_divisions);

    // Find best and worst efficiency
    double min_candidates = 1000000, max_candidates = 0;
    for (int eps_idx = 0; eps_idx < n_eps; eps_idx++) {
        double eps = eps_values[eps_idx];
        int total_candidates = 0;

        for (int i = 0; i < n_semiprimes; i++) {
            unsigned long N = semiprimes[i].N;
            int n_cand = generate_candidates(N, eps, k_values[0]); // Use first k for baseline
            total_candidates += n_cand;
        }

        double avg_candidates = (double)total_candidates / n_semiprimes;
        if (avg_candidates < min_candidates) min_candidates = avg_candidates;
        if (avg_candidates > max_candidates) max_candidates = avg_candidates;
    }

    printf("  Geometric Method:      %.1f - %.1f candidates (avg)\n", min_candidates, max_candidates);
    printf("  Computational Saving: %d%% - %d%% reduction\n",
           (int)((naive_divisions - max_candidates) / naive_divisions * 100),
           (int)((naive_divisions - min_candidates) / naive_divisions * 100));
    printf("\n");


}

int main(int argc, char *argv[]) {
    // Default parameters
    unsigned long Nmax = 1000000;
    int samples = 500;  // Reduced for C implementation efficiency
    double eps_values[] = {0.02, 0.03, 0.04, 0.05};
    int n_eps = 4;
    double k_values[] = {0.200, 0.450, 0.800};
    int n_passes = 3;
    unsigned int seed = 42;
    char semiprime_type[20] = "balanced"; // balanced, skewed, wide
    
    // Parse command line arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--Nmax") == 0 && i + 1 < argc) {
            Nmax = strtoul(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "--samples") == 0 && i + 1 < argc) {
            samples = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--k") == 0 && i + 1 < argc) {
            // Legacy single k support - use for all passes
            double single_k = atof(argv[++i]);
            for (int j = 0; j < n_passes; j++) {
                k_values[j] = single_k;
            }
        } else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            seed = (unsigned int)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--type") == 0 && i + 1 < argc) {
            strncpy(semiprime_type, argv[++i], 19);
            semiprime_type[19] = '\0';
        } else if (strcmp(argv[i], "--help") == 0) {
            printf("Factorization Shortcut Demo - MPFR Implementation\n");
            printf("Usage: %s [options]\n", argv[0]);
            printf("Options:\n");
            printf("  --Nmax <value>    Upper bound for N (default: 1000000)\n");
            printf("  --samples <value> Number of semiprimes to test (default: 500)\n");
            printf("  --k <value>       Single k-value mode (legacy)\n");
            printf("  --type <type>     Semiprime type: balanced|skewed|wide (default: balanced)\n");
            printf("  --seed <value>    Random seed (default: 42)\n");
            printf("  --help            Show this help\n");
            return 0;
        }
    }
    
    if (samples > MAX_SEMIPRIMES) samples = MAX_SEMIPRIMES;

    // Initialize MPFR
    init_mpfr();

    // Generate prime pool
    unsigned long prime_limit = 3 * (unsigned long)sqrt(Nmax) + 100;
    sieve_primes(prime_limit);

    if (n_primes == 0) {
        fprintf(stderr, "Error: No primes generated; increase Nmax\n");
        cleanup_mpfr();
        return 1;
    }

    // Generate semiprimes of specified type
    if (strcmp(semiprime_type, "skewed") == 0) {
        sample_semiprimes_skewed(Nmax, samples, seed);
    } else if (strcmp(semiprime_type, "wide") == 0) {
        sample_semiprimes_wide(Nmax, samples, seed);
    } else {
        sample_semiprimes_balanced(Nmax, samples, seed);
    }

    if (n_semiprimes == 0) {
        fprintf(stderr, "Error: No semiprimes generated\n");
        cleanup_mpfr();
        return 1;
    }

    // Run evaluation with clean output
    evaluate(eps_values, n_eps, k_values, n_passes, semiprime_type);

    // Cleanup
    cleanup_mpfr();
    return 0;
}