/**
 * @file lis_corrector.c
 * @brief LIS-enhanced nth-prime correction using Z5D seed (PoC)
 */

#include "lis_corrector.h"
#include "../lis/lis.h"
#include "../z5d_predictor.h"
#include <math.h>
#include <stdint.h>
#include <stddef.h>

static uint64_t ll_round_u64(double x) {
    if (x <= 0.0) return 0;
    double r = floor(x + 0.5);
    if (r < 0.0) return 0;
    return (uint64_t)r;
}

static int is_probable_prime_mr(uint64_t n);

/* Dusart-style pi(x) approximation for direction only. */
static uint64_t pi_approx(uint64_t x) {
    if (x < 2) return 0;
    double xd = (double)x;
    double ln = log(xd);
    if (ln <= 0.0) return 0;
    double denom = ln - 1.0 - (1.0 / ln);
    if (denom <= 0.0) denom = ln;
    double est = xd / denom;
    if (est < 0.0) est = 0.0;
    return (uint64_t)(est);
}

int lis_correct_nth_prime(uint64_t n, uint64_t window,
                          uint64_t* out_prime,
                          uint64_t* out_mr_calls,
                          uint64_t* out_baseline) {
    if (!out_prime || n == 0) return -1;
    if (window == 0) window = 100000; /* default window */

    /* Seed with Z5D */
    double p0d = z5d_prime((double)n, Z5D_DEFAULT_C, Z5D_DEFAULT_K_STAR, Z5D_DEFAULT_KAPPA_GEO, 1);
    uint64_t p0 = ll_round_u64(p0d);
    if (p0 < 3) p0 = 3;
    if ((p0 % 2) == 0) p0 += 1; /* odd */

    /* Direction from pi approx */
    uint64_t n0 = pi_approx(p0);
    int64_t delta = (int64_t)n - (int64_t)n0;
    int dir = (delta >= 0) ? +1 : -1;

    lis_config_t cfg; lis_init_default(&cfg);

    uint64_t mr_calls = 0;
    uint64_t baseline = 0;

    uint64_t candidate = p0;
    uint64_t steps = 0;
    uint64_t limit = window;

    /* Handle small primes */
    if (n <= 5) {
        static const uint64_t small[] = {0,2,3,5,7,11};
        *out_prime = small[n];
        if (out_mr_calls) *out_mr_calls = 0;
        if (out_baseline) *out_baseline = 0;
        return 0;
    }

    while (steps <= limit) {
        if (candidate < 3) candidate = 3;

        if (lis_passes_wheel210(candidate)) {
            baseline++;
            if (lis_filter(candidate, &cfg)) {
                if (is_probable_prime_mr(candidate)) {
                    mr_calls++;
                    if (dir > 0) delta -= 1; else delta += 1;
                    if (delta == 0) {
                        *out_prime = candidate;
                        if (out_mr_calls) *out_mr_calls = mr_calls;
                        if (out_baseline) *out_baseline = baseline;
                        return 0;
                    }
                }
            }
        }

        /* step */
        int64_t next = (int64_t)candidate + (int64_t)(2 * dir);
        if (next < 3) {
            /* bounce and switch direction if needed */
            dir = +1;
            next = 3;
        }
        candidate = (uint64_t)next;
        steps++;
    }

    return -2; /* not found within window */
}

/* Deterministic Miller–Rabin for 64-bit */
static uint64_t mod_mul_u128(uint64_t a, uint64_t b, uint64_t mod) {
    return (uint64_t)(((__uint128_t)a * b) % mod);
}

static uint64_t mod_pow64(uint64_t a, uint64_t d, uint64_t mod) {
    uint64_t r = 1;
    a %= mod;
    while (d) {
        if (d & 1) r = mod_mul_u128(r, a, mod);
        a = mod_mul_u128(a, a, mod);
        d >>= 1;
    }
    return r;
}

static int is_probable_prime_mr(uint64_t n) {
    if (n < 2) return 0;
    static const uint64_t known[] = {2ULL,3ULL,5ULL,7ULL,11ULL,13ULL,17ULL,19ULL,23ULL,0};
    for (int i=0; known[i]; ++i) if (n == known[i]) return 1;
    if ((n & 1ULL) == 0ULL) return 0;

    /* write n-1 = d * 2^s */
    uint64_t d = n - 1, s = 0;
    while ((d & 1ULL) == 0ULL) { d >>= 1; ++s; }

    const uint64_t bases[] = {2ULL,3ULL,5ULL,7ULL,11ULL,13ULL,17ULL,0};
    for (int i=0; bases[i]; ++i) {
        uint64_t a = bases[i] % n;
        if (a == 0) continue;
        uint64_t x = mod_pow64(a, d, n);
        if (x == 1 || x == n-1) continue;
        int composite = 1;
        for (uint64_t r=1; r<s; ++r) {
            x = mod_mul_u128(x, x, n);
            if (x == n-1) { composite = 0; break; }
        }
        if (composite) return 0;
    }
    return 1;
}

