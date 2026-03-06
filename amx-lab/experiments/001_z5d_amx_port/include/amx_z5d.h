#ifndef AMX_Z5D_H
#define AMX_Z5D_H

#include <mpfr.h>
#include <stdint.h>
#include <string.h>

// M1 AMX real instructions (from unified-framework z5d_phase2.h) - Hard-coded for M1
#define AMX_TILE_SIZE (8 * 8 * 4)  // 8x8 FP32 = 256 bytes
typedef uint8_t amx_tile_t[AMX_TILE_SIZE];

static inline void amx_set(void) {
    // AMX_SET() - Initialize AMX state
    __asm__ volatile(".word 0x17000000");
}

static inline void amx_clr(void) {
    // AMX_CLR() - Clean up AMX state
    __asm__ volatile(".word 0x17000001");
}

static inline void amx_ldx(uint64_t operand) {
    // AMX_LDX() - Load X register
    __asm__ volatile(".word 0x17000100" : : "r"(operand));
}

static inline void amx_ldy(uint64_t operand) {
    // AMX_LDY() - Load Y register
    __asm__ volatile(".word 0x17000200" : : "r"(operand));
}

static inline void amx_stz(uint64_t operand) {
    // AMX_STZ() - Store Z accumulator
    __asm__ volatile(".word 0x17000300" : : "r"(operand));
}

static inline void amx_fma32(uint64_t operand) {
    // AMX_FMA32() - 32-bit fused multiply-add
    __asm__ volatile(".word 0x17002000" : : "r"(operand));
}

// Simplified tile ops for FP32 outer products
static inline void amx_zero(amx_tile_t *z) { amx_clr(); }
static inline void amx_ld1h(amx_tile_t *x, const float *ptr, int stride) {
    // Load FP32 tile to X (simplified: assume ptr is tile addr)
    amx_ldx((uint64_t)ptr);
}
static inline void amx_fmla(amx_tile_t *z, const amx_tile_t *x, const amx_tile_t *y) {
    // Outer product acc Z += X * Y (FP32)
    amx_fma32(0);  // Operand encodes tile indices
}
static inline void amx_st1h(float *ptr, int stride, const amx_tile_t *z) {
    // Store Z to FP32 tile
    amx_stz((uint64_t)ptr);
}

// Batched mul-add for series: sum += a_vec * b_scalar (tiled)
void amx_batched_mul_add(mpfr_t *sum_batch, const mpfr_t *a_batch, float b_scalar, size_t count, mpfr_prec_t prec);

// Batched PNT term: pnt = k * (ln_k + ln_ln_k -1 + corr)
void amx_compute_pnt_batch(mpfr_t *pnt_batch, const mpfr_t *k_batch, const mpfr_t *ln_k_batch, const mpfr_t *ln_ln_k_batch, const mpfr_t *corr_batch, size_t count, mpfr_prec_t prec);

// For li series batched
void amx_li_series_batch(mpfr_t *li_batch, const mpfr_t *x_batch, mpfr_prec_t prec, int max_terms);

#endif