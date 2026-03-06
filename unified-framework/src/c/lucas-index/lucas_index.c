/**
 * @file lucas_index.c
 * @brief Lucas Index System (LIS) — Proof of Concept
 * @author Unified Framework Team
 * @version 1.0
 *
 * Proof of Concept (PoC): Core implementation of a Lucas/Fibonacci pre‑filter
 * combined with Miller–Rabin to reduce candidate checks for nth‑prime search.
 * The single, realistic baseline is wheel‑210 (coprime to 2·3·5·7), and the
 * primary metric printed by the demo is: MR‑call reduction vs baseline.
 */

#include "lucas_index.h"
/* Z5D headers removed: LIS demo is self-contained */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <inttypes.h>
#if defined(_OPENMP)
#include <omp.h>
#endif

/**
 * @brief Default Lucas sequence parameters optimized for prime searching
 */
#define LUCAS_DEFAULT_P 1
#define LUCAS_DEFAULT_Q -1
#define LUCAS_DEFAULT_MODULUS 1000000007ULL
#define LUCAS_DEFAULT_SEARCH_BOUND 1000000ULL
#define LUCAS_TARGET_REDUCTION 0.0

/**
 * @brief Maximum number of iterations for search algorithms
 */
#define LUCAS_MAX_ITERATIONS 10000

/**
 * @brief Tolerance for floating point comparisons
 */
#define LUCAS_EPSILON 1e-9

/**
 * @brief Fast modular exponentiation
 * @param base Base value
 * @param exp Exponent
 * @param mod Modulus
 * @return base^exp mod mod
 */
static uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = ((__uint128_t)result * base) % mod;
        }
        base = ((__uint128_t)base * base) % mod;
        exp >>= 1;
    }
    return result;
}

/**
 * @brief Check if a number is prime using Miller-Rabin test
 * @param n Number to test
 * @return true if likely prime, false if composite
 */
static bool is_prime_miller_rabin(uint64_t n) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;
    
    // Write n-1 as d * 2^r
    uint64_t d = n - 1;
    int r = 0;
    while (d % 2 == 0) {
        d /= 2;
        r++;
    }
    
    // Witness values for deterministic test up to certain bounds
    uint64_t witnesses[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    int num_witnesses = sizeof(witnesses) / sizeof(witnesses[0]);
    
    for (int i = 0; i < num_witnesses && witnesses[i] < n; i++) {
        uint64_t a = witnesses[i];
        uint64_t x = mod_pow(a, d, n);
        
        if (x == 1 || x == n - 1) continue;
        
        bool composite = true;
        for (int j = 0; j < r - 1; j++) {
            x = ((__uint128_t)x * x) % n;
            if (x == n - 1) {
                composite = false;
                break;
            }
        }
        
        if (composite) return false;
    }
    
    return true;
}

/**
 * @brief Compute Lucas sequence values efficiently
 * @param n Index
 * @param P Parameter P
 * @param Q Parameter Q
 * @param mod Modulus
 * @param U_n Pointer to store U_n
 * @param V_n Pointer to store V_n
 */
// Iterative computation of Lucas U/V sequences modulo 'mod'.
// P and Q are signed; intermediate products use 128-bit signed integers
// and are normalized back into [0, mod) to avoid under/overflow.
static void lucas_sequence(uint64_t n, int64_t P, int64_t Q, uint64_t mod,
                          uint64_t *U_n, uint64_t *V_n) {
    if (n == 0) {
        *U_n = 0;
        *V_n = 2;
        return;
    }
    if (n == 1) {
        *U_n = 1;
        *V_n = P;
        return;
    }
    
    uint64_t U_prev = 0, U_curr = 1;
    uint64_t V_prev = 2, V_curr = (uint64_t)((((__int128)P % (__int128)mod) + (__int128)mod) % (__int128)mod);
    
    for (uint64_t i = 2; i <= n; i++) {
        __int128 tU = ((__int128)P * (__int128)U_curr) - ((__int128)Q * (__int128)U_prev);
        __int128 tV = ((__int128)P * (__int128)V_curr) - ((__int128)Q * (__int128)V_prev);

        uint64_t U_next = (uint64_t)((tU % (__int128)mod + (__int128)mod) % (__int128)mod);
        uint64_t V_next = (uint64_t)((tV % (__int128)mod + (__int128)mod) % (__int128)mod);

        U_prev = U_curr;
        U_curr = U_next;
        V_prev = V_curr;
        V_curr = V_next;
    }
    
    *U_n = U_curr;
    *V_n = V_curr;
}

/**
 * @brief Wheel-30 presieve: allow residues coprime to 2,3,5.
 */
// Modern minimal baseline presieve: eliminate multiples of 2,3,5,7.
// Using explicit mod checks keeps the logic obvious for this demo.
static inline bool passes_wheel210(uint64_t n) {
    return (n % 2 != 0) && (n % 3 != 0) && (n % 5 != 0) && (n % 7 != 0);
}

lucas_error_t lucas_index_init(lucas_index_config_t *config) {
    if (!config) return LUCAS_ERROR_INVALID_PARAMS;
    
    config->P = LUCAS_DEFAULT_P;
    config->Q = LUCAS_DEFAULT_Q;
    config->modulus = LUCAS_DEFAULT_MODULUS;
    config->search_bound = LUCAS_DEFAULT_SEARCH_BOUND;
    config->reduction_factor = LUCAS_TARGET_REDUCTION;
    
    return LUCAS_SUCCESS;
}

uint64_t lucas_number_mod(uint64_t n, int64_t P, int64_t Q, uint64_t m) {
    uint64_t U_n, V_n;
    lucas_sequence(n, P, Q, m, &U_n, &V_n);
    return U_n;
}

/**
 * @brief Fast doubling Fibonacci (U-sequence with P=1,Q=-1) modulo m
 */
// Fast-doubling Fibonacci modulo m used by the Lucas filter when P=1,Q=-1.
// Only intended as a utility for the demo (not a general big-int routine).
static void fib_doubling_mod(uint64_t n, uint64_t m, uint64_t *F_n, uint64_t *F_n1) {
    if (n == 0) {
        *F_n = 0;
        *F_n1 = 1 % m;
        return;
    }
    uint64_t a, b;
    fib_doubling_mod(n >> 1, m, &a, &b); // a=F(k), b=F(k+1)
    __int128 two_b_minus_a = ( (__int128)2 * b - a );
    uint64_t c = (uint64_t)((((__int128)a * two_b_minus_a) % (__int128)m + (__int128)m) % (__int128)m); // F(2k)
    uint64_t d = (uint64_t)((((__int128)a * a + (__int128)b * b) % (__int128)m + (__int128)m) % (__int128)m); // F(2k+1)
    if ((n & 1) == 0) {
        *F_n = c;
        *F_n1 = d;
    } else {
        *F_n = d;
        *F_n1 = (c + d) % m;
    }
}

/**
 * @brief Lucas/Fibonacci-based Frobenius filter (Selfridge/Kronecker-5 variant)
 * Returns true if n passes the Lucas Fibonacci probable-prime filter.
 */
static bool lucas_frobenius_filter(uint64_t n, const lucas_index_config_t *config) {
    if (n < 2) return false;
    if (n == 2) return true;
    if ((n % 2) == 0) return false;
    if (n % 5 == 0) return (n == 5);

    // Only defined for P=1,Q=-1 (Fibonacci). Otherwise skip filter.
    if (!(config->P == 1 && config->Q == -1)) {
        return true;
    }

    // Legendre symbol (5/n) via Euler's criterion: 5^((n-1)/2) mod n
    uint64_t t = mod_pow(5 % n, (n - 1) / 2, n);
    int legendre;
    if (t == 1) legendre = 1;
    else if (t == n - 1) legendre = -1;
    else return false; // composite or gcd(n,5) != 1 (handled earlier)

    uint64_t k = (legendre == 1) ? (n - 1) : (n + 1);
    uint64_t Fk, Fk1;
    fib_doubling_mod(k, n, &Fk, &Fk1);
    return (Fk % n) == 0;
}

/**
 * @brief Real search for nth prime using Lucas filter + Miller-Rabin
 */
static lucas_error_t lucas_real_search(uint64_t target_index,
                                       const lucas_index_config_t *config,
                                       lucas_search_result_t *result) {
    if (!config || !result || target_index == 0) return LUCAS_ERROR_INVALID_PARAMS;
    if (config->modulus <= 1 || config->search_bound == 0) return LUCAS_ERROR_INVALID_PARAMS;

    memset(result, 0, sizeof(lucas_search_result_t));
    result->lucas_index = target_index;

    uint64_t found = 0;
    uint64_t candidate = 2;
    uint64_t baseline_wheel210_tests = 0; // modern baseline: wheel-210 presieve
    uint64_t mr_calls = 0;               // MR tests actually performed after Lucas filter

    while (candidate <= config->search_bound) {
        if (candidate == 2) {
            // Handle 2
            if (++found == target_index) {
                result->prime_candidate = candidate;
                result->iterations = mr_calls; // 0 MR calls so far
                result->is_verified_prime = true;
                result->baseline_wheel210 = baseline_wheel210_tests;
                result->efficiency_ratio = (baseline_wheel210_tests == 0) ? 1.0 : (double)mr_calls / (double)baseline_wheel210_tests;
                return LUCAS_SUCCESS;
            }
            candidate = 3;
            continue;
        }

        // Baseline: wheel-210 presieve (modern minimal baseline)
        if (passes_wheel210(candidate)) baseline_wheel210_tests++;

        // Handle small primes that are excluded by wheel-210
        if (candidate == 3 || candidate == 5 || candidate == 7) {
            found++;
            if (found == target_index) {
                result->prime_candidate = candidate;
                result->iterations = mr_calls;
                result->is_verified_prime = true;
                result->baseline_wheel210 = baseline_wheel210_tests;
                result->efficiency_ratio = (baseline_wheel210_tests == 0) ? 1.0 : (double)mr_calls / (double)baseline_wheel210_tests;
                return LUCAS_SUCCESS;
            }
            candidate += 2;
            continue;
        }

        // Only consider candidates that pass the baseline presieve
        if (passes_wheel210(candidate)) {
            bool pass_lucas = lucas_frobenius_filter(candidate, config);
            if (pass_lucas) {
            mr_calls++;
            if (is_prime_miller_rabin(candidate)) {
                found++;
                if (found == target_index) {
                    result->prime_candidate = candidate;
                    result->iterations = mr_calls;
                    result->is_verified_prime = true;
                    result->baseline_wheel210 = baseline_wheel210_tests;
                    result->efficiency_ratio = (double)mr_calls / (double)(baseline_wheel210_tests ? baseline_wheel210_tests : 1);
                    return LUCAS_SUCCESS;
                }
            }
            }
        }

        candidate += 2; // next odd
    }

    return LUCAS_ERROR_NOT_FOUND;
}

lucas_error_t lucas_find_nth_prime(uint64_t n, const lucas_index_config_t *config,
                                  lucas_search_result_t *result) {
    if (n == 0 || !config || !result) return LUCAS_ERROR_INVALID_PARAMS;
    
    return lucas_real_search(n, config, result);
}

/**
 * @brief Prime Number Theorem-based index estimate for a given prime value
 * @param prime Prime to invert
 * @return Estimated index (0 if undefined)
 */
static uint64_t estimate_prime_index(uint64_t prime) {
    if (prime > 2) {
        double ln_p = log((double)prime);
        if (ln_p > 0.0) {
            double denom = ln_p - 1.0 - (1.0 / ln_p); // Dusart-style correction
            if (denom > 0.0) {
                double est = (double)prime / denom;
                if (est > 0.0) return (uint64_t)(est);
            }
            return (uint64_t)((double)prime / ln_p);
        }
    }
    return 0;
}

lucas_error_t lucas_invert_prime(uint64_t prime, const lucas_index_config_t *config,
                                lucas_search_result_t *result) {
    if (prime < 2 || !config || !result) return LUCAS_ERROR_INVALID_PARAMS;
    
    // Enumerate primes and count index until we reach the target prime
    // Use Lucas filter + MR to accelerate, but count baseline odd tests for ratio
    if (config->modulus <= 1 || config->search_bound == 0) return LUCAS_ERROR_INVALID_PARAMS;

    memset(result, 0, sizeof(lucas_search_result_t));
    result->prime_candidate = prime;

    uint64_t found = 0;
    uint64_t candidate = 2;
    uint64_t baseline_wheel210_tests = 0;
    uint64_t mr_calls = 0;

    while (candidate <= config->search_bound) {
        if (candidate == 2) {
            found++;
            if (prime == 2) {
                result->lucas_index = 1;
                result->iterations = 0;
                result->is_verified_prime = true;
                result->efficiency_ratio = 1.0;
                return LUCAS_SUCCESS;
            }
            candidate = 3;
            continue;
        }

        if (passes_wheel210(candidate)) baseline_wheel210_tests++;
        if (passes_wheel210(candidate) && lucas_frobenius_filter(candidate, config)) {
            mr_calls++;
            if (is_prime_miller_rabin(candidate)) {
                found++;
                if (candidate == prime) {
                    result->lucas_index = found;
                    result->iterations = mr_calls;
                    result->is_verified_prime = true;
                    result->baseline_wheel210 = baseline_wheel210_tests;
                    result->efficiency_ratio = (double)mr_calls / (double)(baseline_wheel210_tests ? baseline_wheel210_tests : 1);
                    return LUCAS_SUCCESS;
                }
            }
        }
        candidate += 2;
    }

    // If we didn't find within search_bound, provide a heuristic index estimate
    uint64_t est = estimate_prime_index(prime);
    if (est > 0) {
        result->lucas_index = est;
        result->iterations = mr_calls;
        result->is_verified_prime = false;
        result->baseline_wheel210 = baseline_wheel210_tests;
        result->efficiency_ratio = (baseline_wheel210_tests == 0) ? 1.0 : (double)mr_calls / (double)baseline_wheel210_tests;
        return LUCAS_ERROR_NOT_FOUND;
    }

    return LUCAS_ERROR_NOT_FOUND;
}

lucas_error_t lucas_benchmark_performance(uint64_t start_n, uint64_t end_n,
                                        const lucas_index_config_t *config,
                                        double *reduction_achieved) {
    if (start_n >= end_n || !config || !reduction_achieved) {
        return LUCAS_ERROR_INVALID_PARAMS;
    }
    
    double total_lucas_iterations = 0.0;
    double total_standard_iterations = 0.0;
    uint64_t successful_searches = 0;
    
#if defined(_OPENMP)
#pragma omp parallel for reduction(+:total_lucas_iterations,total_standard_iterations,successful_searches)
#endif
    for (uint64_t n = start_n; n <= end_n; n++) {
        lucas_search_result_t result;
        
        // Test Lucas-enhanced search
        if (lucas_find_nth_prime(n, config, &result) == LUCAS_SUCCESS && result.efficiency_ratio > 0.0) {
            total_lucas_iterations += (double)result.iterations;
            total_standard_iterations += (double)result.iterations / result.efficiency_ratio; // invert ratio to get baseline
            successful_searches++;
        }
    }
    
    if (successful_searches == 0) {
        *reduction_achieved = 0.0;
        return LUCAS_ERROR_NOT_FOUND;
    }
    
    double avg_lucas = (double)total_lucas_iterations / successful_searches;
    double avg_standard = (double)total_standard_iterations / successful_searches;
    
    *reduction_achieved = 1.0 - (avg_lucas / avg_standard);
    
    return LUCAS_SUCCESS;
}

/* (Removed) Z5D validation: LIS demo does not depend on Z5D. */

void lucas_print_config(const lucas_index_config_t *config) {
    if (!config) return;
    
    printf("Lucas-Index Configuration:\n");
    printf("  P parameter: %" PRId64 "\n", config->P);
    printf("  Q parameter: %" PRId64 "\n", config->Q);
    printf("  Modulus: %" PRIu64 "\n", config->modulus);
    printf("  Search bound: %" PRIu64 "\n", config->search_bound);
    printf("  Goal: reduce MR calls vs baseline (no fixed %% target)\n");
}

void lucas_print_result(const lucas_search_result_t *result) {
    if (!result) return;
    
    printf("Lucas Search Result:\n");
    printf("  Prime candidate: %" PRIu64 "\n", result->prime_candidate);
    printf("  Lucas index: %" PRIu64 "\n", result->lucas_index);
    printf("  Iterations (MR calls): %" PRIu64 "\n", result->iterations);
    printf("  Baseline (wheel-210) candidates: %" PRIu64 "\n", result->baseline_wheel210);
    double reduction = (result->efficiency_ratio > 0.0) ? (1.0 - result->efficiency_ratio) : 0.0;
    printf("  MR-call reduction vs wheel-210 baseline: %.2f%%\n", reduction * 100.0);
    printf("  Verified prime: %s\n", result->is_verified_prime ? "Yes" : "No");
}
