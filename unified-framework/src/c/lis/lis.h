/**
 * @file lis.h
 * @brief Lucas Index System (LIS) — Proof of Concept API
 */

#ifndef LIS_H
#define LIS_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int64_t P;
    int64_t Q;
} lis_config_t;

void lis_init_default(lis_config_t* cfg);
int lis_passes_wheel210(uint64_t n);
int lis_filter(uint64_t n, const lis_config_t* cfg);
void lis_filter_batch(const uint64_t* in, size_t len, uint8_t* out, const lis_config_t* cfg);

#ifdef __cplusplus
}
#endif

#endif /* LIS_H */

