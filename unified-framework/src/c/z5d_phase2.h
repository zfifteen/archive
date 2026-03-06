/**
 * Z5D Phase 2 - Parallel & SIMD Extensions
 * ========================================
 * 
 * Parallel and vectorized implementations of Z5D predictor functions.
 * Provides OpenMP batch processing and SIMD-optimized math kernels.
 * 
 * @file z5d_phase2.h
 * @author Unified Framework Team (Phase 2 Implementation)
 * @version 2.0.0
 */

#ifndef Z5D_PHASE2_H
#define Z5D_PHASE2_H

#include "z5d_predictor.h"
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Phase 2 feature flags (compile-time)
#ifndef Z5D_USE_OMP
#define Z5D_USE_OMP 1
#endif

#ifndef Z5D_USE_SIMD
#define Z5D_USE_SIMD 1
#endif

#ifndef Z5D_USE_ACCEL
#define Z5D_USE_ACCEL 0
#endif

#ifndef Z5D_USE_AMX
#  if defined(__APPLE__) && defined(__aarch64__)
#    define Z5D_USE_AMX 1  // Default-on for Apple Silicon (M1 Max+) builds
#  else
#    define Z5D_USE_AMX 0
#  endif
#endif

// Runtime environment variable names
#define Z5D_ENV_USE_OMP "Z5D_USE_OMP"
#define Z5D_ENV_USE_SIMD "Z5D_USE_SIMD"
#define Z5D_ENV_USE_ACCEL "Z5D_USE_ACCEL"
#define Z5D_ENV_USE_AMX "Z5D_USE_AMX"

// SIMD detection and intrinsics
#if Z5D_USE_SIMD && defined(__AVX2__) && defined(__FMA__)
#define Z5D_SIMD_AVX2 1
#include <immintrin.h>
#else
#define Z5D_SIMD_AVX2 0
#endif

#if Z5D_USE_SIMD && defined(__ARM_NEON) && defined(__APPLE__)
#define Z5D_SIMD_NEON 1
#include <arm_neon.h>
#if Z5D_USE_ACCEL
#include <Accelerate/Accelerate.h>
#endif
#else
#define Z5D_SIMD_NEON 0
#endif

// AMX detection for Apple Silicon (M1 Max and later)
#if Z5D_USE_AMX && defined(__APPLE__) && defined(__aarch64__)
#define Z5D_AMX_AVAILABLE 1
// AMX detection is runtime-based since it uses undocumented instructions
#else
#define Z5D_AMX_AVAILABLE 0
#endif

// OpenMP support with auto-detection
#ifndef __has_include
#  define __has_include(x) 0
#endif

#if Z5D_USE_OMP && __has_include("omp.h")
#include <omp.h>
#define Z5D_OMP_AVAILABLE 1
#else
#define Z5D_OMP_AVAILABLE 0
// Provide fallback OpenMP functions when not available
static inline int omp_get_max_threads(void) { return 1; }
static inline int omp_get_thread_num(void) { return 0; }
static inline void omp_set_num_threads(int num_threads) { (void)num_threads; }
#endif

// AMX types and constants (defined for compatibility even when AMX unavailable)

// AMX precision modes for adaptive precision selection
typedef enum {
    AMX_PRECISION_FAST = 0,    // 16-bit integers for preliminary calculations
    AMX_PRECISION_STANDARD = 1, // 32-bit for standard Z framework precision
    AMX_PRECISION_HIGH = 2     // 64-bit when approaching 1e-16 threshold
} amx_precision_mode_t;

// AMX matrix configuration for Z framework operations
typedef struct {
    uint64_t operand;
    double precision_threshold; // <1e-16 per Z framework guidelines
    int matrix_size;           // 32x32 for M1 Max AMX
} amx_z_config_t;

// AMX matrix types (32x32 aligned for optimal performance)
typedef struct __attribute__((aligned(64))) {
    int16_t data[32][32];
} amx_matrix_16_t;

typedef struct __attribute__((aligned(64))) {
    int32_t data[32][32];
} amx_matrix_32_t;

typedef struct __attribute__((aligned(64))) {
    int64_t data[32][32];
} amx_matrix_64_t;

// Function declarations (available regardless of AMX support)
int z5d_amx_is_available(void);
amx_precision_mode_t z5d_amx_select_precision(double current_error, double target_precision);
int z5d_amx_validate_causality_constraints(const int16_t* matrix, size_t dimensions);
int z5d_amx_verify_precision_threshold(const double* results, size_t count, double threshold);
int z5d_amx_compute_z_matrix(const int16_t* A_matrix, 
                            const int16_t* B_over_c_matrix,
                            int32_t* Z_result,
                            size_t dimensions,
                            const amx_z_config_t* config);
int z5d_amx_compute_kappa_function(const uint32_t* n_values,
                                  double* kappa_results,
                                  size_t count,
                                  amx_precision_mode_t precision_mode);
int z5d_amx_batch_compute(const double* k_values, int n, double* results,
                         const amx_z_config_t* config);

#if Z5D_AMX_AVAILABLE

// AMX instruction wrappers (based on z-amx insights) - only available when AMX enabled
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

static inline void amx_mac16(uint64_t operand) {
    // AMX_MAC16() - 16-bit multiply-accumulate
    __asm__ volatile(".word 0x17001000" : : "r"(operand));
}

static inline void amx_fma32(uint64_t operand) {
    // AMX_FMA32() - 32-bit fused multiply-add
    __asm__ volatile(".word 0x17002000" : : "r"(operand));
}

static inline void amx_fma64(uint64_t operand) {
    // AMX_FMA64() - 64-bit fused multiply-add for high precision
    __asm__ volatile(".word 0x17003000" : : "r"(operand));
}

#endif // Z5D_AMX_AVAILABLE

// Phase 2 configuration structure
typedef struct {
    int use_omp;
    int use_simd;
    int use_accel;
    int use_amx;
    int omp_num_threads;
    int chunk_size;
    int amx_precision_mode;  // 0=fast(16-bit), 1=standard(32-bit), 2=high(64-bit)
} z5d_phase2_config_t;

// Phase 2 statistics
typedef struct {
    double time_ms_sequential;
    double time_ms_parallel;
    double speedup;
    int cores_used;
    int simd_lanes;
    int fallback_count;
} z5d_phase2_stats_t;

/**
 * Get Phase 2 configuration from environment variables and defaults
 */
z5d_phase2_config_t z5d_phase2_get_config(void);

/**
 * Parallel batch Z5D prediction with OpenMP
 * 
 * @param k_values Array of k values to predict
 * @param n Number of k values
 * @param results Output array for predictions (must be allocated)
 * @param config Phase 2 configuration (NULL for defaults)
 * @return 0 on success, negative on error
 */
int z5d_prime_batch_parallel(const double* k_values, int n, double* results, 
                           const z5d_phase2_config_t* config);

/**
 * SIMD-optimized math kernels for Z5D computation
 */

#if Z5D_SIMD_AVX2
/**
 * AVX2 vectorized logarithm computation (4 doubles at once)
 */
void z5d_simd_log_avx2(const double* input, double* output, int n);

/**
 * AVX2 vectorized power computation
 */
void z5d_simd_pow_avx2(const double* base, const double* exp, double* output, int n);
#endif

#if Z5D_SIMD_NEON
/**
 * NEON vectorized operations for Apple Silicon
 */
void z5d_simd_log_neon(const double* input, double* output, int n);
void z5d_simd_pow_neon(const double* base, const double* exp, double* output, int n);
#endif

#if Z5D_AMX_AVAILABLE
/**
 * AMX-accelerated matrix operations for Apple M1 Max
 * Implements Z = A(B/c) computations with precision management
 */

/**
 * AMX-accelerated Z matrix computation using the Z framework equation Z = A(B/c)
 * 
 * @param A_matrix Input matrix A (16-bit integers for performance)
 * @param B_over_c_matrix Pre-computed B/c matrix (16-bit integers)
 * @param Z_result Output Z result matrix (32-bit integers for precision)
 * @param dimensions Matrix dimensions (must be ≤ 32 for M1 Max AMX)
 * @param config AMX configuration including precision thresholds
 * @return 0 on success, -1 on causality constraint violation, -2 on precision error
 */
int z5d_amx_compute_z_matrix(const int16_t* A_matrix, 
                            const int16_t* B_over_c_matrix,
                            int32_t* Z_result,
                            size_t dimensions,
                            const amx_z_config_t* config);

/**
 * AMX-accelerated discrete domain computation: Z = n(Δₙ/Δₘₐₓ) with κ(n)=d(n)·ln(n+1)/e²
 * 
 * @param n_values Array of n values for discrete computation
 * @param kappa_results Output κ(n) results
 * @param count Number of values to process (batched for AMX efficiency)
 * @param precision_mode AMX precision mode selection
 * @return 0 on success, negative on error
 */
int z5d_amx_compute_kappa_function(const uint32_t* n_values,
                                  double* kappa_results,
                                  size_t count,
                                  amx_precision_mode_t precision_mode);

/**
 * Z framework compliant AMX wrapper with error handling and causality constraints
 * 
 * @param k_values Array of k values for Z5D prediction
 * @param n Number of k values
 * @param results Output array for Z framework results
 * @param config AMX configuration with precision settings
 * @return 0 on success, negative on error (maintains Z framework error codes)
 */
int z5d_amx_batch_compute(const double* k_values, int n, double* results,
                         const amx_z_config_t* config);

/**
 * Validate causality constraints: |v| < c check to prevent superluminal computations
 */
int z5d_amx_validate_causality_constraints(const int16_t* matrix, size_t dimensions);

/**
 * Verify precision threshold compliance (|error| < 1e-16 per Z framework guidelines)
 */
int z5d_amx_verify_precision_threshold(const double* results, size_t count, double threshold);

#endif // Z5D_AMX_AVAILABLE

/**
 * Fallback scalar implementations
 */
void z5d_simd_log_scalar(const double* input, double* output, int n);
void z5d_simd_pow_scalar(const double* base, const double* exp, double* output, int n);

/**
 * Auto-dispatched vectorized functions (runtime selection)
 */
void z5d_simd_log(const double* input, double* output, int n);
void z5d_simd_pow(const double* base, const double* exp, double* output, int n);

/**
 * SIMD-optimized Z5D prediction for arrays
 * 
 * @param k_values Array of k values
 * @param n Number of values
 * @param results Output predictions
 * @param config Phase 2 configuration
 * @return 0 on success, negative on error
 */
int z5d_prime_batch_simd(const double* k_values, int n, double* results);

/**
 * Combined parallel + SIMD batch prediction (Phase 2 flagship)
 * 
 * @param k_values Array of k values
 * @param n Number of values  
 * @param results Output predictions
 * @param config Phase 2 configuration (NULL for auto-detect)
 * @param stats Optional statistics output (NULL to ignore)
 * @return 0 on success, negative on error
 */
int z5d_prime_batch_phase2(const double* k_values, int n, double* results,
                          const z5d_phase2_config_t* config, z5d_phase2_stats_t* stats);

/**
 * Feature detection and capability reporting
 */
typedef struct {
    int openmp_available;
    int openmp_threads;
    int avx2_available;
    int fma_available;
    int neon_available;
    int accelerate_available;
    int amx_available;
    int amx_matrix_size;
    const char* compiler_version;
    const char* build_flags;
} z5d_phase2_capabilities_t;

z5d_phase2_capabilities_t z5d_phase2_get_capabilities(void);
void z5d_phase2_print_capabilities(void);

/**
 * Performance benchmarking utilities
 */
double z5d_phase2_benchmark_sequential(const double* k_values, int n, int reps);
double z5d_phase2_benchmark_parallel(const double* k_values, int n, int reps);
double z5d_phase2_benchmark_simd(const double* k_values, int n, int reps);

/**
 * Early-Exit Miller-Rabin with Geodesic Witnesses
 */

// MR telemetry structure
typedef struct {
    unsigned long rounds_std;
    unsigned long rounds_geo;
    int early_exit_hit;
    double time_ms_std;
    double time_ms_geo;
    int witness_type;
} z5d_mr_telemetry_t;

/**
 * Batch primality testing with early-exit Miller-Rabin
 * 
 * @param k_values Array of k values for Z5D prediction
 * @param n Number of values
 * @param results Output array for primality results (1=prime, 0=composite)
 * @param telemetry_array Optional telemetry output (NULL to ignore)
 * @return 0 on success, negative on error
 */
int z5d_batch_primality_test(const double* k_values, int n, int* results, 
                            z5d_mr_telemetry_t* telemetry_array);

/**
 * Print Miller-Rabin telemetry summary
 */
void z5d_print_mr_telemetry_summary(const z5d_mr_telemetry_t* telemetry, int n);

#ifdef __cplusplus
}
#endif

#endif /* Z5D_PHASE2_H */
