/**
 * @file llt_convergence.h
 * @brief Lucas-Lehmer Test Convergence Prediction in ℚ(√3)
 * @author Unified Framework Team
 * @version 1.0
 *
 * Header for Lucas-Lehmer convergence prediction algorithms.
 * Implements early termination logic based on ℚ(√3) field properties
 * and statistical pattern matching for Mersenne prime candidates.
 */

#ifndef LLT_CONVERGENCE_H
#define LLT_CONVERGENCE_H

// Check for MPFR availability
#ifndef __has_include
#define __has_include(x) 0
#endif

#if __has_include(<mpfr.h>) && __has_include(<gmp.h>)
#include <mpfr.h>
#include <gmp.h>
#define LLT_HAVE_MPFR 1
#else
#define LLT_HAVE_MPFR 0
// Fallback types for demonstration
typedef struct { double value; } mpfr_t;
typedef struct { long value; } mpz_t;
#define MPFR_RNDN 0

// Fallback function declarations
void mpfr_init2(mpfr_t *x, int prec);
void mpfr_clear(mpfr_t *x);
void mpfr_set_ui(mpfr_t *x, unsigned long val, int rnd);
void mpfr_set(mpfr_t *dst, const mpfr_t *src, int rnd);
void mpfr_sqr(mpfr_t *dst, const mpfr_t *src, int rnd);
void mpfr_sub_ui(mpfr_t *dst, const mpfr_t *src, unsigned long val, int rnd);
void mpfr_add(mpfr_t *dst, const mpfr_t *a, const mpfr_t *b, int rnd);
void mpfr_mul(mpfr_t *dst, const mpfr_t *a, const mpfr_t *b, int rnd);
void mpfr_mul_ui(mpfr_t *dst, const mpfr_t *src, unsigned long val, int rnd);
void mpfr_div(mpfr_t *dst, const mpfr_t *a, const mpfr_t *b, int rnd);
void mpfr_log(mpfr_t *dst, const mpfr_t *src, int rnd);
void mpfr_fmod(mpfr_t *dst, const mpfr_t *a, const mpfr_t *b, int rnd);
double mpfr_get_d(const mpfr_t *x, int rnd);
int mpfr_zero_p(const mpfr_t *x);
void mpfr_ui_pow_ui(mpfr_t *dst, unsigned long base, unsigned long exp, int rnd);

void mpz_init(mpz_t *x);
void mpz_clear(mpz_t *x);
void mpz_ui_pow_ui(mpz_t *dst, unsigned long base, unsigned long exp);
void mpz_sub_ui(mpz_t *dst, const mpz_t *src, unsigned long val);
size_t mpz_sizeinbase(const mpz_t *x, int base);

const char* mpfr_get_version(void);
#endif

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Precision configuration
#define LLT_PRECISION_BITS 256
#define LLT_DECIMAL_PLACES 77  // Approximately 256 bits precision
#define MAX_ITERATIONS 10000   // Safety limit

// Statistical thresholds for early termination
#define CONVERGENCE_THRESHOLD 0.15      // 15% deviation threshold
#define PATTERN_WINDOW_SIZE 10          // Window size for pattern analysis
#define MIN_ITERATIONS_BEFORE_CHECK 5   // Minimum iterations before convergence check

/**
 * @brief Structure to represent elements in ℚ(√3)
 * 
 * Elements of the form a + b√3 where a, b are rational numbers
 */
typedef struct {
    mpfr_t a;  // Rational coefficient
    mpfr_t b;  // √3 coefficient
} q_sqrt3_t;

/**
 * @brief Statistical data for convergence analysis
 */
typedef struct {
    double growth_rate;           // Current growth rate
    double expected_growth;       // Expected growth rate
    double deviation;             // Deviation from expected
    uint32_t pattern_violations;  // Number of pattern violations
    uint32_t total_checks;        // Total convergence checks performed
} convergence_stats_t;

/**
 * @brief Mersenne candidate information
 */
typedef struct {
    uint32_t exponent;           // Mersenne exponent p
    mpz_t mersenne_number;       // 2^p - 1
    bool is_known_prime;         // Whether this is a known Mersenne prime
    uint32_t iterations_saved;   // Iterations saved by early termination
} mersenne_candidate_t;

// ℚ(√3) field operations
void q_sqrt3_init(q_sqrt3_t *x);
void q_sqrt3_clear(q_sqrt3_t *x);
void q_sqrt3_set_ui(q_sqrt3_t *x, unsigned long a, unsigned long b);
void q_sqrt3_set_mpfr(q_sqrt3_t *x, const mpfr_t a, const mpfr_t b);
void q_sqrt3_square(q_sqrt3_t *result, const q_sqrt3_t *x);
void q_sqrt3_sub_ui(q_sqrt3_t *result, const q_sqrt3_t *x, unsigned long n);
void q_sqrt3_mod(q_sqrt3_t *result, const q_sqrt3_t *x, const mpz_t mod);
double q_sqrt3_magnitude(const q_sqrt3_t *x);

// Lucas-Lehmer sequence operations
void llt_sequence_step(q_sqrt3_t *s_next, const q_sqrt3_t *s_current);
void llt_sequence_step_mod(mpfr_t s_next, const mpfr_t s_current, const mpz_t mersenne);

// Convergence prediction functions
bool predict_convergence(const mpfr_t *sequence, uint32_t current_iteration, 
                        uint32_t target_iterations, const mpz_t mersenne,
                        convergence_stats_t *stats);

double calculate_expected_growth_rate(uint32_t iteration, uint32_t exponent);
double calculate_actual_growth_rate(const mpfr_t *sequence, uint32_t current_iteration);
bool check_pattern_deviation(const mpfr_t *sequence, uint32_t current_iteration,
                            uint32_t exponent, convergence_stats_t *stats);

// Statistical analysis functions
double compute_residue_variance(const mpfr_t *sequence, uint32_t length, const mpz_t mod);
bool is_statistical_outlier(double value, double mean, double variance, double threshold);
void update_convergence_statistics(convergence_stats_t *stats, double actual_growth,
                                  double expected_growth, bool is_violation);

// Mersenne candidate management
void mersenne_candidate_init(mersenne_candidate_t *candidate, uint32_t exponent);
void mersenne_candidate_clear(mersenne_candidate_t *candidate);
bool is_known_mersenne_prime(uint32_t exponent);

// Main prediction interface
typedef struct {
    bool early_termination_enabled;
    double convergence_threshold;
    uint32_t pattern_window_size;
    uint32_t min_iterations_before_check;
    bool verbose_output;
} llt_prediction_config_t;

/**
 * @brief Result of Lucas-Lehmer convergence prediction
 */
typedef struct {
    bool is_prime;                    // Predicted primality result
    bool early_termination_triggered; // Whether early termination was used
    uint32_t iterations_performed;    // Actual iterations performed
    uint32_t iterations_saved;        // Iterations saved by early termination
    double efficiency_gain;           // Percentage efficiency improvement
    convergence_stats_t stats;        // Detailed statistical information
} llt_prediction_result_t;

// Main prediction function
int lucas_lehmer_with_prediction(uint32_t exponent, const llt_prediction_config_t *config,
                                llt_prediction_result_t *result);

// Utility functions
void print_convergence_stats(const convergence_stats_t *stats);
void print_prediction_result(const llt_prediction_result_t *result, uint32_t exponent);
const char* get_known_mersenne_primes_list(void);

#ifdef __cplusplus
}
#endif

#endif // LLT_CONVERGENCE_H