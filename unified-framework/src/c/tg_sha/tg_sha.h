#ifndef TG_SHA_H
#define TG_SHA_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>  // for size_t

// Conditional compilation for MPFR/GMP support
#ifdef TG_SHA_HAVE_MPFR
#include <gmp.h>
#include <mpfr.h>
#else
// Fallback types for demonstration when MPFR/GMP not available
typedef struct { double value; } mpfr_t[1];
typedef struct { long long value; } mpz_t[1];
typedef int mpfr_rnd_t;
#define MPFR_RNDN 0
#define mpfr_init2(x, prec) ((x)->value = 0.0, (void)prec)
#define mpfr_clear(x) ((x)->value = 0.0)
#define mpfr_set_d(x, val, rnd) ((x)->value = (val), (void)rnd)
#define mpfr_set_ui(x, val, rnd) ((x)->value = (double)(val), (void)rnd)
#define mpfr_set(x, y, rnd) ((x)->value = (y)->value, (void)rnd)
#define mpfr_get_d(x, rnd) ((x)->value)
#define mpfr_pow(z, x, y, rnd) ((z)->value = pow((x)->value, (y)->value), (void)rnd)
#define mpfr_mul(z, x, y, rnd) ((z)->value = (x)->value * (y)->value, (void)rnd)
#define mpfr_div(z, x, y, rnd) ((z)->value = (x)->value / (y)->value, (void)rnd)
#define mpfr_add_ui(z, x, n, rnd) ((z)->value = (x)->value + (n), (void)rnd)
#define mpfr_get_ui(x, rnd) ((unsigned long)(x)->value)
#define mpfr_printf(fmt, x, ...) printf("%.10f\n", (x)->value)
#define mpz_init(x) ((x)->value = 0)
#define mpz_clear(x) ((x)->value = 0)
#endif

/**
 * @file tg_sha.h
 * @brief Transparent Geometric SHA (TG-SHA) - Header file
 * 
 * Demonstrates geometric predictability in SHA-like constants, exposing
 * a scalar parameter (k*) that when revealed allows prediction of internal 
 * states, analogous to the Dual_EC_DRBG 'd' parameter vulnerability.
 * 
 * Part of the Z Framework unified mathematical framework demonstrating
 * how geometric relationships can introduce predictable structures in
 * cryptographic constants.
 */

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// CONSTANTS AND CONFIGURATION
// ============================================================================

// TG-SHA Configuration
#define TG_SHA_BLOCK_SIZE   64      // Block size in bytes
#define TG_SHA_HASH_SIZE    32      // Output hash size in bytes
#define TG_SHA_ROUNDS       64      // Number of rounds
#define TG_SHA_MPFR_PREC    256     // MPFR precision in bits

// Z Framework Parameters (standardized across unified framework)
#define TG_SHA_KAPPA_GEO    0.3     // Geodesic mapping exponent
#define TG_SHA_KAPPA_STAR   0.04449 // Z Framework calibration parameter

// Geometric Parameters
#define TG_SHA_PHI_SCALED   1.618033988749895   // Golden ratio
#define TG_SHA_EULER_E      2.718281828459045   // Euler's number
#define TG_SHA_PI_VAL       3.141592653589793   // Pi

// ============================================================================
// DATA STRUCTURES
// ============================================================================

/**
 * @brief TG-SHA Context structure
 * 
 * Contains all state for TG-SHA operations including the critical
 * k* parameter that introduces geometric predictability.
 */
typedef struct {
    // Core SHA state
    uint32_t h[8];                    // Hash state (8 x 32-bit words)
    uint8_t  buffer[TG_SHA_BLOCK_SIZE]; // Input buffer
    uint64_t bitlen;                  // Total bits processed
    uint32_t datalen;                 // Current buffer length
    
    // Geometric parameters (Z Framework)
    mpfr_t kappa_geo;                 // Geodesic exponent (κ_geo)
    mpfr_t kappa_star;                // Critical geometric scalar (κ*)
    
    // Round constants with geometric structure
    uint32_t k_constants[TG_SHA_ROUNDS]; // Round constants
    
    // Security mode
    bool secure_mode;                 // true = k* hidden, false = k* exposed
    bool k_star_exposed;             // Flag indicating k* visibility
    
    // High-precision arithmetic context
    mpfr_t temp_calc;                // Temporary calculation space
    mpz_t  temp_int;                 // Temporary integer space
    
} tg_sha_ctx_t;

/**
 * @brief TG-SHA operation result codes
 */
typedef enum {
    TG_SHA_SUCCESS = 0,
    TG_SHA_ERROR_NULL_POINTER,
    TG_SHA_ERROR_INVALID_INPUT,
    TG_SHA_ERROR_GEOMETRIC_VIOLATION,
    TG_SHA_ERROR_PRECISION_LOSS,
    TG_SHA_ERROR_K_STAR_EXPOSED
} tg_sha_result_t;

/**
 * @brief Geometric analysis result structure
 */
typedef struct {
    double predictability_score;     // Measure of geometric predictability
    double k_star_correlation;       // Correlation when k* is known
    uint32_t predicted_rounds[16];   // Predicted future round values
    bool geometric_vulnerability;    // Whether vulnerability is present
    char analysis_summary[256];      // Human-readable analysis
} tg_sha_analysis_t;

// ============================================================================
// CORE TG-SHA FUNCTIONS
// ============================================================================

/**
 * @brief Initialize TG-SHA context
 * 
 * @param ctx Pointer to TG-SHA context
 * @param secure_mode If true, k* is hidden; if false, k* is exposed
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_init(tg_sha_ctx_t* ctx, bool secure_mode);

/**
 * @brief Update TG-SHA with input data
 * 
 * @param ctx Pointer to TG-SHA context
 * @param data Input data buffer
 * @param len Length of input data
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_update(tg_sha_ctx_t* ctx, const uint8_t* data, size_t len);

/**
 * @brief Finalize TG-SHA and produce hash
 * 
 * @param ctx Pointer to TG-SHA context
 * @param hash Output buffer for hash (must be TG_SHA_HASH_SIZE bytes)
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_final(tg_sha_ctx_t* ctx, uint8_t* hash);

/**
 * @brief Clean up TG-SHA context
 * 
 * @param ctx Pointer to TG-SHA context
 */
void tg_sha_cleanup(tg_sha_ctx_t* ctx);

// ============================================================================
// GEOMETRIC VULNERABILITY ANALYSIS
// ============================================================================

/**
 * @brief Generate round constants with geometric structure
 * 
 * Creates SHA-like round constants with hidden geometric relationships
 * controlled by k* parameter. In secure mode, k* is hidden; in broken
 * mode, k* can be exposed for analysis.
 * 
 * @param ctx Pointer to TG-SHA context
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_generate_constants(tg_sha_ctx_t* ctx);

/**
 * @brief Expose k* parameter (switches to broken mode)
 * 
 * This function deliberately exposes the critical k* parameter,
 * demonstrating the geometric vulnerability similar to Dual_EC_DRBG's
 * 'd' parameter exposure.
 * 
 * @param ctx Pointer to TG-SHA context
 * @param k_star_value Pointer to receive k* value (high-precision)
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_expose_k_star(tg_sha_ctx_t* ctx, mpfr_t k_star_value);

/**
 * @brief Predict internal states using exposed k*
 * 
 * Demonstrates how knowledge of k* allows prediction of internal
 * states and future round constants, showing the geometric vulnerability.
 * 
 * @param ctx Pointer to TG-SHA context (must be in broken mode)
 * @param analysis Output structure for analysis results
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_predict_states(tg_sha_ctx_t* ctx, tg_sha_analysis_t* analysis);

/**
 * @brief Demonstrate geometric predictability
 * 
 * Shows how geometric relationships in the constants can be exploited
 * when k* is known, providing empirical validation of the vulnerability.
 * 
 * @param ctx Pointer to TG-SHA context
 * @param num_predictions Number of predictions to make
 * @param predictions Output array for predictions
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_demonstrate_predictability(tg_sha_ctx_t* ctx, 
                                                 int num_predictions, 
                                                 uint32_t* predictions);

// ============================================================================
// Z FRAMEWORK INTEGRATION
// ============================================================================

/**
 * @brief Apply geodesic mapping to constants
 * 
 * Applies Z Framework geodesic enhancement using κ_geo parameter
 * to introduce geometric structure in constants.
 * 
 * @param input Input value
 * @param output Output value after geodesic mapping
 * @param kappa_geo Geodesic exponent
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_geodesic_map(mpfr_t input, mpfr_t output, mpfr_t kappa_geo);

/**
 * @brief Validate Z Framework parameters
 * 
 * Ensures parameters conform to Z Framework standards and
 * geometric consistency requirements.
 * 
 * @param ctx Pointer to TG-SHA context
 * @return TG_SHA_SUCCESS if valid, error code if invalid
 */
tg_sha_result_t tg_sha_validate_parameters(tg_sha_ctx_t* ctx);

/**
 * @brief Generate geometric analysis report
 * 
 * Creates comprehensive analysis of geometric relationships,
 * predictability scores, and vulnerability assessment.
 * 
 * @param ctx Pointer to TG-SHA context
 * @param report_buffer Buffer for report text
 * @param buffer_size Size of report buffer
 * @return TG_SHA_SUCCESS on success, error code on failure
 */
tg_sha_result_t tg_sha_generate_report(tg_sha_ctx_t* ctx, 
                                      char* report_buffer, 
                                      size_t buffer_size);

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * @brief Convert result code to human-readable string
 * 
 * @param result TG-SHA result code
 * @return String description of result
 */
const char* tg_sha_result_string(tg_sha_result_t result);

/**
 * @brief Print hash in hexadecimal format
 * 
 * @param hash Hash bytes
 * @param len Length of hash
 */
void tg_sha_print_hash(const uint8_t* hash, size_t len);

/**
 * @brief Print geometric analysis
 * 
 * @param analysis Pointer to analysis structure
 */
void tg_sha_print_analysis(const tg_sha_analysis_t* analysis);

#ifdef __cplusplus
}
#endif

#endif /* TG_SHA_H */