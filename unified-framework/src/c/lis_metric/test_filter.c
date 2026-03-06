#include <stdio.h>
#include <stdint.h>

// Copy the functions from lis_metric.c for testing
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

static void lucas_u_doubling_mod(uint64_t n, uint64_t m, uint64_t *U_n, uint64_t *U_n1) {
    if (n == 0) {
        *U_n = 0;
        *U_n1 = 1 % m;
        return;
    }
    uint64_t a, b;
    lucas_u_doubling_mod(n >> 1, m, &a, &b);
    __uint128_t two_b_minus_a = ((__uint128_t)2 * b - a + (__uint128_t)m) % (__uint128_t)m;
    uint64_t c = (uint64_t)((((__uint128_t)a * two_b_minus_a) % (__uint128_t)m));
    uint64_t d = (uint64_t)((((__uint128_t)a * a + (__uint128_t)b * b) % (__uint128_t)m));
    if ((n & 1) == 0) {
        *U_n = c;
        *U_n1 = d;
    } else {
        *U_n = d;
        *U_n1 = (c + d) % m;
    }
}

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

int main() {
    // First 50 primes
    uint64_t primes[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 213, 227, 229};
    int num_primes = sizeof(primes) / sizeof(primes[0]);

    printf("Testing Lucas-Frobenius filter against known primes:\n");
    printf("Prime\tFilter Result\tStatus\n");

    int failures = 0;
    for (int i = 0; i < num_primes; i++) {
        int result = lucas_frobenius_filter(primes[i]);
        printf("%lu\t%d\t\t%s\n", primes[i], result, result ? "PASS" : "FAIL");
        if (!result) {
            failures++;
        }
    }

    printf("\nSummary: %d failures out of %d primes tested\n", failures, num_primes);
    return 0;
}