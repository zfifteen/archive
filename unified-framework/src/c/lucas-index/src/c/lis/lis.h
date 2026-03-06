/**
 * @file lis.h
 * @brief Lucas Index System (LIS) — Proof of Concept API
 *
 * Proof of Concept (PoC): Minimal, self-contained interface for a
 * Lucas/Fibonacci probable-prime pre-filter combined with a wheel-210
 * presieve. Intended to reduce the number of Miller–Rabin calls in a
 * typical pipeline; does not predict p(n).
 */

#ifndef LIS_H
#define LIS_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int64_t P;          /* Lucas parameter P (default: 1) */
    int64_t Q;          /* Lucas parameter Q (default: -1) */
} lis_config_t;

/* Initialize LIS config with defaults (P=1, Q=-1). */
void lis_init_default(lis_config_t* cfg);

/* Return non-zero if n passes wheel-210 presieve. */
int lis_passes_wheel210(uint64_t n);

/* Return non-zero if n passes LIS (wheel-210 + Lucas/Fibonacci filter). */
int lis_filter(uint64_t n, const lis_config_t* cfg);

/* Batch filter: out[i] set to 1 if in[i] passes LIS, else 0. */
void lis_filter_batch(const uint64_t* in, size_t len, uint8_t* out, const lis_config_t* cfg);

#ifdef __cplusplus
}
#endif

#endif /* LIS_H */
