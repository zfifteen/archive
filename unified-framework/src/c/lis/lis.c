/**
 * @file lis.c
 * @brief Lucas Index System (LIS) — Proof of Concept implementation
 */

#include "lis.h"

static uint64_t mod_pow_u64(uint64_t base, uint64_t exp, uint64_t mod) {
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
    __int128 two_b_minus_a = ( (__int128)2 * b - a );
    uint64_t c = (uint64_t)((((__int128)a * two_b_minus_a) % (__int128)m + (__int128)m) % (__int128)m);
    uint64_t d = (uint64_t)((((__int128)a * a + (__int128)b * b) % (__int128)m + (__int128)m) % (__int128)m);
    if ((n & 1) == 0) {
        *F_n = c;
        *F_n1 = d;
    } else {
        *F_n = d;
        *F_n1 = (c + d) % m;
    }
}

static int lucas_frobenius_filter(uint64_t n, const lis_config_t* cfg) {
    if (n < 2) return 0;
    if (n == 2) return 1;
    if ((n % 2) == 0) return 0;
    if (n % 5 == 0) return (n == 5);
    if (!(cfg && cfg->P == 1 && cfg->Q == -1)) {
        return 1;
    }
    uint64_t t = mod_pow_u64(5 % n, (n - 1) / 2, n);
    int legendre;
    if (t == 1) legendre = 1;
    else if (t == n - 1) legendre = -1;
    else return 0;
    uint64_t k = (legendre == 1) ? (n - 1) : (n + 1);
    uint64_t Fk, Fk1;
    fib_doubling_mod(k, n, &Fk, &Fk1);
    return (Fk % n) == 0;
}

void lis_init_default(lis_config_t* cfg) {
    if (!cfg) return;
    cfg->P = 1;
    cfg->Q = -1;
}

int lis_passes_wheel210(uint64_t n) {
    return (n % 2 != 0) && (n % 3 != 0) && (n % 5 != 0) && (n % 7 != 0);
}

int lis_filter(uint64_t n, const lis_config_t* cfg) {
    if (!lis_passes_wheel210(n)) return 0;
    return lucas_frobenius_filter(n, cfg);
}

void lis_filter_batch(const uint64_t* in, size_t len, uint8_t* out, const lis_config_t* cfg) {
    if (!in || !out) return;
    for (size_t i = 0; i < len; ++i) {
        out[i] = (uint8_t)(lis_filter(in[i], cfg) ? 1 : 0);
    }
}

