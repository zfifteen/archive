/**
 * @file lis_metric.c
 * @brief LIS Metric CLI - Range-based filtering performance measurement
 * @author Unified Framework Team
 * @version 1.0
 *
 * Command-line tool for measuring LIS filtering performance across ranges.
 * Counts wheel-210 baseline candidates and LIS survivors (no MR calls).
 * Provides quick filtering efficiency measurement without primality verification.
 *
 * Usage:
 *   ./lis_metric 1 200000 > lis_metric_out.csv
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>
#include <time.h>
#include <math.h>

/**
 * @brief LIS metric result structure
 */
typedef struct {
    uint64_t start;
    uint64_t end;
    uint64_t baseline_candidates;
    uint64_t lis_survivors;
    double reduction_pct;
    double elapsed_s;
} lis_metric_result_t;

/**
 * @brief Wheel-210 presieve: allow residues coprime to 2,3,5,7
 */
static inline int passes_wheel210(uint64_t n) {
    return (n % 2 != 0) && (n % 3 != 0) && (n % 5 != 0) && (n % 7 != 0);
}

/**
 * @brief Fast modular exponentiation
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
 * @brief Fast doubling Lucas U sequence modulo m (P=1, Q=-1, D=5)
 */
static void lucas_u_doubling_mod(uint64_t n, uint64_t m, uint64_t *U_n, uint64_t *U_n1) {
    if (n == 0) {
        *U_n = 0;
        *U_n1 = 1 % m;
        return;
    }
    uint64_t a, b;
    lucas_u_doubling_mod(n >> 1, m, &a, &b); // a=U(k), b=U(k+1)
    // For Lucas U with P=1, Q=-1: U(2k) = U(k) * V(k), U(2k+1) = (P*U(k+1)*U(k) + V(k+1)*V(k))/2
    // But we use the simpler identity: U(2k) = U(k) * (2*U(k+1) - U(k))
    __uint128_t two_b_minus_a = ((__uint128_t)2 * b - a + (__uint128_t)m) % (__uint128_t)m;
    uint64_t c = (uint64_t)((((__uint128_t)a * two_b_minus_a) % (__uint128_t)m)); // U(2k)
    uint64_t d = (uint64_t)((((__uint128_t)a * a + (__uint128_t)b * b) % (__uint128_t)m)); // U(2k+1)
    if ((n & 1) == 0) {
        *U_n = c;
        *U_n1 = d;
    } else {
        *U_n = d;
        *U_n1 = (c + d) % m;
    }
}

/**
 * @brief Lucas U pseudoprime test (Selfridge/Kronecker-5 variant)
 */
static int lucas_frobenius_filter(uint64_t n) {
    if (n < 2) return 0;
    if (n == 2) return 1;
    if ((n % 2) == 0) return 0;
    if (n % 5 == 0) return (n == 5);

    // Legendre symbol (5/n) via Euler's criterion: 5^((n-1)/2) mod n
    uint64_t t = mod_pow(5 % n, (n - 1) / 2, n);
    int legendre;
    if (t == 1) legendre = 1;
    else if (t == n - 1) legendre = -1;
    else return 0; // composite or gcd(n,5) != 1

    uint64_t k = (legendre == 1) ? (n - 1) : (n + 1);
    uint64_t Uk, Uk1;
    lucas_u_doubling_mod(k, n, &Uk, &Uk1);
    return (Uk % n) == 0;
}

/**
 * @brief Measure LIS filtering performance across a range
 */
static int lis_metric_range(uint64_t start, uint64_t end, lis_metric_result_t *result) {
    if (!result || start >= end || start < 3) {
        return -1; // invalid parameters
    }

    clock_t start_time = clock();

    result->start = start;
    result->end = end;
    result->baseline_candidates = 0;
    result->lis_survivors = 0;

    // Count filtering performance across range
    for (uint64_t n = start; n <= end; n += 2) { // odd numbers only
        if (passes_wheel210(n)) {
            result->baseline_candidates++;

            if (lucas_frobenius_filter(n)) {
                result->lis_survivors++;
            }
        }
    }

    clock_t end_time = clock();
    result->elapsed_s = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;

    // Calculate reduction percentage
    if (result->baseline_candidates > 0) {
        result->reduction_pct = 100.0 * (1.0 - (double)result->lis_survivors / (double)result->baseline_candidates);
    } else {
        result->reduction_pct = 0.0;
    }

    return 0; // success
}

/**
 * @brief Print usage information
 */
static void print_usage(const char *program_name) {
    printf("Usage: %s <start> <end>\n", program_name);
    printf("\n");
    printf("LIS Metric: Pre-filter efficiency measurement (Miller-Rabin call reduction)\n");
    printf("\n");
    printf("Arguments:\n");
    printf("  start          Start of range (inclusive, must be >= 3)\n");
    printf("  end            End of range (inclusive)\n");
    printf("\n");
    printf("Output format (CSV):\n");
    printf("  start,end,wheel210_candidates,lucas_survivors,mr_reduction_pct,elapsed_s\n");
    printf("\n");
    printf("Description:\n");
    printf("  Measures computational efficiency of Lucas/Fibonacci pre-filtering.\n");
    printf("  - wheel210_candidates: Numbers coprime to 2,3,5,7 (NOT actual primes)\n");
    printf("  - lucas_survivors: Candidates requiring Miller-Rabin verification\n");
    printf("  - mr_reduction_pct: Percentage reduction in expensive primality tests\n");
    printf("  No actual primality verification performed - pure filtering benchmark.\n");
    printf("\n");
    printf("Examples:\n");
    printf("  %s 1 200000 > lis_metric_out.csv\n", program_name);
    printf("  %s 1000000 2000000\n", program_name);
}

/**
 * @brief Main function
 */
int main(int argc, char *argv[]) {
    if (argc != 3) {
        if (argc > 1 && (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0)) {
            print_usage(argv[0]);
            return 0;
        }
        fprintf(stderr, "Error: Invalid number of arguments\n");
        print_usage(argv[0]);
        return 1;
    }

    // Parse arguments
    uint64_t start = strtoull(argv[1], NULL, 10);
    uint64_t end = strtoull(argv[2], NULL, 10);

    // Validate inputs
    if (start == 0 || end == 0) {
        fprintf(stderr, "Error: Invalid range values\n");
        return 1;
    }

    if (start >= end) {
        fprintf(stderr, "Error: Start must be less than end\n");
        return 1;
    }

    if (start < 3) {
        fprintf(stderr, "Error: Start must be >= 3\n");
        return 1;
    }

    if (end > 1000000000ULL) {
        fprintf(stderr, "Error: End value too large (max: 1,000,000,000)\n");
        return 1;
    }

    // Print CSV header with clarified column names
    printf("start,end,wheel210_candidates,lucas_survivors,mr_reduction_pct,elapsed_s\n");

    // Execute metric measurement
    lis_metric_result_t result;
    int ret = lis_metric_range(start, end, &result);
    if (ret != 0) {
        fprintf(stderr, "Error: LIS metric measurement failed\n");
        return 1;
    }

    // Output CSV result
    printf("%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%.2f,%.6f\n",
           result.start, result.end, result.baseline_candidates,
           result.lis_survivors, result.reduction_pct, result.elapsed_s);

    return 0;
}