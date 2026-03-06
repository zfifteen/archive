#include <stdio.h>
#include <stdint.h>

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

static void fib_doubling_mod(uint64_t n, uint64_t m, uint64_t *F_n, uint64_t *F_n1) {
    if (n == 0) {
        *F_n = 0;
        *F_n1 = 1 % m;
        return;
    }
    uint64_t a, b;
    fib_doubling_mod(n >> 1, m, &a, &b);
    __uint128_t two_b_minus_a = ((__uint128_t)2 * b - a);
    uint64_t c = (uint64_t)((((__uint128_t)a * two_b_minus_a) % (__uint128_t)m + (__uint128_t)m) % (__uint128_t)m);
    uint64_t d = (uint64_t)((((__uint128_t)a * a + (__uint128_t)b * b) % (__uint128_t)m + (__uint128_t)m) % (__uint128_t)m);
    if ((n & 1) == 0) {
        *F_n = c;
        *F_n1 = d;
    } else {
        *F_n = d;
        *F_n1 = (c + d) % m;
    }
}

int main() {
    uint64_t n = 107;
    printf("Debugging Lucas-Frobenius filter for n = %llu\n", n);

    // Step 1: Legendre symbol (5/n)
    uint64_t t = mod_pow(5 % n, (n - 1) / 2, n);
    printf("5^((n-1)/2) mod n = 5^%llu mod %llu = %llu\n", (n-1)/2, n, t);

    int legendre;
    if (t == 1) legendre = 1;
    else if (t == n - 1) legendre = -1;
    else {
        printf("ERROR: Invalid Legendre result %llu (should be 1 or %llu)\n", t, n-1);
        return 1;
    }
    printf("Legendre symbol (5/%llu) = %d\n", n, legendre);

    // Step 2: Calculate k
    uint64_t k = (legendre == 1) ? (n - 1) : (n + 1);
    printf("k = %llu\n", k);

    // Step 3: Calculate F_k mod n
    uint64_t Fk, Fk1;
    fib_doubling_mod(k, n, &Fk, &Fk1);
    printf("F_%llu mod %llu = %llu\n", k, n, Fk);

    // Step 4: Check if F_k ≡ 0 (mod n)
    int result = (Fk % n) == 0;
    printf("F_k mod n == 0? %s\n", result ? "YES (prime)" : "NO (composite)");

    // Let's also check what the correct Lucas test should be
    printf("\n--- Checking correct Lucas pseudoprime test ---\n");
    printf("For prime p, we should have:\n");
    printf("- If (5/p) = 1, then U_%llu ≡ 0 (mod p) where U_n is Lucas U sequence\n", n-1);
    printf("- If (5/p) = -1, then U_%llu ≡ 0 (mod p)\n", n+1);
    printf("But we're computing Fibonacci numbers, not Lucas U sequence!\n");

    return 0;
}