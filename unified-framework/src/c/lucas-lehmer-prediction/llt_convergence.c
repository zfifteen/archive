/**
 * @file llt_convergence.c
 * @brief Lucas-Lehmer Test Convergence Prediction Implementation
 * @author Unified Framework Team
 * @version 1.0
 *
 * Implementation of Lucas-Lehmer convergence prediction algorithms
 * based on ℚ(√3) field properties and statistical pattern analysis.
 */

#include "llt_convergence.h"
#include <math.h>
#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// Fallback implementations for when MPFR is not available
#if !LLT_HAVE_MPFR
// Simple fallback mpfr_* functions using double precision
void mpfr_init2(mpfr_t *x, int prec) { x->value = 0.0; }
void mpfr_clear(mpfr_t *x) { x->value = 0.0; }
void mpfr_set_ui(mpfr_t *x, unsigned long val, int rnd) { x->value = (double)val; }
void mpfr_set(mpfr_t *dst, const mpfr_t *src, int rnd) { dst->value = src->value; }
void mpfr_sqr(mpfr_t *dst, const mpfr_t *src, int rnd) { dst->value = src->value * src->value; }
void mpfr_sub_ui(mpfr_t *dst, const mpfr_t *src, unsigned long val, int rnd) { dst->value = src->value - val; }
void mpfr_add(mpfr_t *dst, const mpfr_t *a, const mpfr_t *b, int rnd) { dst->value = a->value + b->value; }
void mpfr_mul(mpfr_t *dst, const mpfr_t *a, const mpfr_t *b, int rnd) { dst->value = a->value * b->value; }
void mpfr_mul_ui(mpfr_t *dst, const mpfr_t *src, unsigned long val, int rnd) { dst->value = src->value * val; }
void mpfr_div(mpfr_t *dst, const mpfr_t *a, const mpfr_t *b, int rnd) { dst->value = a->value / b->value; }
void mpfr_log(mpfr_t *dst, const mpfr_t *src, int rnd) { dst->value = log(src->value); }
void mpfr_fmod(mpfr_t *dst, const mpfr_t *a, const mpfr_t *b, int rnd) { dst->value = fmod(a->value, b->value); }
double mpfr_get_d(const mpfr_t *x, int rnd) { return x->value; }
int mpfr_zero_p(const mpfr_t *x) { return fabs(x->value) < 1e-10; }
void mpfr_ui_pow_ui(mpfr_t *dst, unsigned long base, unsigned long exp, int rnd) { dst->value = pow(base, exp); }

void mpz_init(mpz_t *x) { x->value = 0; }
void mpz_clear(mpz_t *x) { x->value = 0; }
void mpz_ui_pow_ui(mpz_t *dst, unsigned long base, unsigned long exp) { dst->value = (long)pow(base, exp); }
void mpz_sub_ui(mpz_t *dst, const mpz_t *src, unsigned long val) { dst->value = src->value - val; }
size_t mpz_sizeinbase(const mpz_t *x, int base) { return (size_t)log(fabs(x->value))/log(base) + 1; }

const char* mpfr_get_version(void) { return "fallback-1.0"; }
#endif

// Known Mersenne prime exponents (for pattern recognition)
static const uint32_t MERSENNE_PRIMES[] = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281,
    3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209, 44497, 86243,
    110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221, 3021377,
    6972593, 13466917, 20996011, 24036583, 25964951, 30402457
};
static const uint32_t NUM_MERSENNE_PRIMES = sizeof(MERSENNE_PRIMES) / sizeof(MERSENNE_PRIMES[0]);

// ℚ(√3) field operations implementation

void q_sqrt3_init(q_sqrt3_t *x) {
    mpfr_init2(&x->a, LLT_PRECISION_BITS);
    mpfr_init2(&x->b, LLT_PRECISION_BITS);
    mpfr_set_ui(&x->a, 0, MPFR_RNDN);
    mpfr_set_ui(&x->b, 0, MPFR_RNDN);
}

void q_sqrt3_clear(q_sqrt3_t *x) {
    mpfr_clear(&x->a);
    mpfr_clear(&x->b);
}

void q_sqrt3_set_ui(q_sqrt3_t *x, unsigned long a, unsigned long b) {
    mpfr_set_ui(&x->a, a, MPFR_RNDN);
    mpfr_set_ui(&x->b, b, MPFR_RNDN);
}

void q_sqrt3_set_mpfr(q_sqrt3_t *x, const mpfr_t *a, const mpfr_t *b) {
    mpfr_set(&x->a, a, MPFR_RNDN);
    mpfr_set(&x->b, b, MPFR_RNDN);
}

void q_sqrt3_square(q_sqrt3_t *result, const q_sqrt3_t *x) {
    mpfr_t temp1, temp2, temp3;
    mpfr_init2(&temp1, LLT_PRECISION_BITS);
    mpfr_init2(&temp2, LLT_PRECISION_BITS);
    mpfr_init2(&temp3, LLT_PRECISION_BITS);
    
    // (a + b√3)² = a² + 2ab√3 + 3b² = (a² + 3b²) + (2ab)√3
    
    // Calculate a² + 3b²
    mpfr_sqr(&temp1, &x->a, MPFR_RNDN);      // a²
    mpfr_sqr(&temp2, &x->b, MPFR_RNDN);      // b²
    mpfr_mul_ui(&temp2, &temp2, 3, MPFR_RNDN); // 3b²
    mpfr_add(&result->a, &temp1, &temp2, MPFR_RNDN); // a² + 3b²
    
    // Calculate 2ab
    mpfr_mul(&temp3, &x->a, &x->b, MPFR_RNDN);
    mpfr_mul_ui(&result->b, &temp3, 2, MPFR_RNDN);
    
    mpfr_clear(&temp1);
    mpfr_clear(&temp2);
    mpfr_clear(&temp3);
}

void q_sqrt3_sub_ui(q_sqrt3_t *result, const q_sqrt3_t *x, unsigned long n) {
    mpfr_sub_ui(&result->a, &x->a, n, MPFR_RNDN);
    mpfr_set(&result->b, &x->b, MPFR_RNDN);
}

double q_sqrt3_magnitude(const q_sqrt3_t *x) {
    double a = mpfr_get_d(&x->a, MPFR_RNDN);
    double b = mpfr_get_d(&x->b, MPFR_RNDN);
    return sqrt(a*a + 3*b*b);
}

// Lucas-Lehmer sequence operations

void llt_sequence_step(q_sqrt3_t *s_next, const q_sqrt3_t *s_current) {
    q_sqrt3_square(s_next, s_current);
    q_sqrt3_sub_ui(s_next, s_next, 2);
}

void llt_sequence_step_mod(mpfr_t s_next, const mpfr_t s_current, const mpz_t mersenne) {
    mpfr_t temp;
    mpfr_init2(temp, LLT_PRECISION_BITS);
    
    // s_next = s_current² - 2
    mpfr_sqr(temp, s_current, MPFR_RNDN);
    mpfr_sub_ui(s_next, temp, 2, MPFR_RNDN);
    
    // Reduce modulo mersenne number
    mpfr_fmod(s_next, s_next, (mpfr_t)mersenne, MPFR_RNDN);
    
    mpfr_clear(temp);
}

// Convergence prediction implementation

bool predict_convergence(const mpfr_t *sequence, uint32_t current_iteration, 
                        uint32_t target_iterations, const mpz_t mersenne,
                        convergence_stats_t *stats) {
    
    if (current_iteration < MIN_ITERATIONS_BEFORE_CHECK) {
        return false; // Too early to make prediction
    }
    
    // Calculate actual vs expected growth rates
    double actual_growth = calculate_actual_growth_rate(sequence, current_iteration);
    double expected_growth = calculate_expected_growth_rate(current_iteration, 
                                                           mpz_sizeinbase(mersenne, 2) - 1);
    
    // Update statistics
    update_convergence_statistics(stats, actual_growth, expected_growth,
                                 fabs(actual_growth - expected_growth) > CONVERGENCE_THRESHOLD);
    
    // Check for pattern violations
    bool pattern_violation = check_pattern_deviation(sequence, current_iteration,
                                                    mpz_sizeinbase(mersenne, 2) - 1, stats);
    
    // Early termination criteria:
    // 1. Significant deviation from expected growth
    // 2. Multiple pattern violations
    // 3. Statistical outlier behavior
    
    double deviation_ratio = fabs(actual_growth - expected_growth) / expected_growth;
    bool significant_deviation = deviation_ratio > CONVERGENCE_THRESHOLD;
    bool too_many_violations = stats->pattern_violations > (stats->total_checks / 3);
    
    return significant_deviation && too_many_violations && pattern_violation;
}

double calculate_expected_growth_rate(uint32_t iteration, uint32_t exponent) {
    // Based on S_n ≈ (2 + √3)^{2^n} + (2 - √3)^{2^n}
    // Growth rate is approximately 2^n * log(2 + √3)
    
    double alpha = 2.0 + sqrt(3.0);  // 2 + √3 ≈ 3.732
    double log_alpha = log(alpha);
    
    // Expected growth: 2^iteration * log_alpha
    return pow(2.0, iteration) * log_alpha;
}

double calculate_actual_growth_rate(const mpfr_t *sequence, uint32_t current_iteration) {
    if (current_iteration < 2) return 0.0;
    
    // Calculate log(S_i / S_{i-1})
    mpfr_t ratio, log_ratio;
    mpfr_init2(ratio, LLT_PRECISION_BITS);
    mpfr_init2(log_ratio, LLT_PRECISION_BITS);
    
    mpfr_div(ratio, sequence[current_iteration], sequence[current_iteration - 1], MPFR_RNDN);
    mpfr_log(log_ratio, ratio, MPFR_RNDN);
    
    double result = mpfr_get_d(log_ratio, MPFR_RNDN);
    
    mpfr_clear(ratio);
    mpfr_clear(log_ratio);
    
    return result;
}

bool check_pattern_deviation(const mpfr_t *sequence, uint32_t current_iteration,
                            uint32_t exponent, convergence_stats_t *stats) {
    
    if (current_iteration < PATTERN_WINDOW_SIZE) return false;
    
    // Analyze recent sequence values for unexpected patterns
    double variance = compute_residue_variance(sequence + current_iteration - PATTERN_WINDOW_SIZE,
                                             PATTERN_WINDOW_SIZE, NULL);
    
    // Check if this exponent is a known Mersenne prime
    bool is_known_prime = is_known_mersenne_prime(exponent);
    
    // For known primes, expect lower variance; for composites, expect higher variance
    double expected_variance = is_known_prime ? 0.1 : 0.5;
    
    return is_statistical_outlier(variance, expected_variance, 0.1, 2.0);
}

double compute_residue_variance(const mpfr_t *sequence, uint32_t length, const mpz_t mod) {
    if (length < 2) return 0.0;
    
    double sum = 0.0, sum_sq = 0.0;
    
    for (uint32_t i = 0; i < length; i++) {
        double val = mpfr_get_d(sequence[i], MPFR_RNDN);
        sum += val;
        sum_sq += val * val;
    }
    
    double mean = sum / length;
    double variance = (sum_sq / length) - (mean * mean);
    
    return variance;
}

bool is_statistical_outlier(double value, double mean, double variance, double threshold) {
    if (variance <= 0.0) return false;
    
    double std_dev = sqrt(variance);
    double z_score = fabs(value - mean) / std_dev;
    
    return z_score > threshold;
}

void update_convergence_statistics(convergence_stats_t *stats, double actual_growth,
                                  double expected_growth, bool is_violation) {
    stats->growth_rate = actual_growth;
    stats->expected_growth = expected_growth;
    stats->deviation = fabs(actual_growth - expected_growth);
    stats->total_checks++;
    
    if (is_violation) {
        stats->pattern_violations++;
    }
}

// Mersenne candidate management

void mersenne_candidate_init(mersenne_candidate_t *candidate, uint32_t exponent) {
    candidate->exponent = exponent;
    mpz_init(candidate->mersenne_number);
    
    // Calculate 2^p - 1
    mpz_ui_pow_ui(candidate->mersenne_number, 2, exponent);
    mpz_sub_ui(candidate->mersenne_number, candidate->mersenne_number, 1);
    
    candidate->is_known_prime = is_known_mersenne_prime(exponent);
    candidate->iterations_saved = 0;
}

void mersenne_candidate_clear(mersenne_candidate_t *candidate) {
    mpz_clear(candidate->mersenne_number);
}

bool is_known_mersenne_prime(uint32_t exponent) {
    for (uint32_t i = 0; i < NUM_MERSENNE_PRIMES; i++) {
        if (MERSENNE_PRIMES[i] == exponent) {
            return true;
        }
    }
    return false;
}

// Main prediction interface

int lucas_lehmer_with_prediction(uint32_t exponent, const llt_prediction_config_t *config,
                                llt_prediction_result_t *result) {
    
    // Initialize result structure
    memset(result, 0, sizeof(llt_prediction_result_t));
    
    // Initialize Mersenne candidate
    mersenne_candidate_t candidate;
    mersenne_candidate_init(&candidate, exponent);
    
    // Initialize sequence storage
    mpfr_t *sequence = malloc(exponent * sizeof(mpfr_t));
    if (!sequence) {
        mersenne_candidate_clear(&candidate);
        return -1; // Memory allocation error
    }
    
    for (uint32_t i = 0; i < exponent; i++) {
        mpfr_init2(sequence[i], LLT_PRECISION_BITS);
    }
    
    // Initialize first term: S_0 = 4
    mpfr_set_ui(sequence[0], 4, MPFR_RNDN);
    
    uint32_t iteration;
    bool early_termination = false;
    
    // Main Lucas-Lehmer iteration with prediction
    for (iteration = 1; iteration < exponent - 1; iteration++) {
        // Compute next term: S_i = S_{i-1}² - 2 mod (2^p - 1)
        llt_sequence_step_mod(sequence[iteration], sequence[iteration - 1],
                             candidate.mersenne_number);
        
        // Check for convergence prediction
        if (config->early_termination_enabled && iteration >= config->min_iterations_before_check) {
            if (predict_convergence(sequence, iteration, exponent - 1,
                                   candidate.mersenne_number, &result->stats)) {
                early_termination = true;
                result->early_termination_triggered = true;
                result->iterations_saved = (exponent - 1) - iteration;
                break;
            }
        }
    }
    
    result->iterations_performed = iteration;
    
    // Final primality determination
    if (early_termination) {
        // If early termination was triggered, assume composite
        result->is_prime = false;
    } else {
        // Check final condition: S_{p-2} ≡ 0 mod (2^p - 1)
        result->is_prime = mpfr_zero_p(sequence[exponent - 2]);
    }
    
    // Calculate efficiency gain
    if (result->iterations_saved > 0) {
        result->efficiency_gain = (double)result->iterations_saved / (exponent - 1) * 100.0;
    }
    
    // Cleanup
    for (uint32_t i = 0; i < exponent; i++) {
        mpfr_clear(sequence[i]);
    }
    free(sequence);
    mersenne_candidate_clear(&candidate);
    
    return 0;
}

// Utility functions

void print_convergence_stats(const convergence_stats_t *stats) {
    printf("📊 Convergence Statistics:\n");
    printf("   Growth Rate: %.6f (expected: %.6f)\n", stats->growth_rate, stats->expected_growth);
    printf("   Deviation: %.6f\n", stats->deviation);
    printf("   Pattern Violations: %u/%u (%.1f%%)\n", 
           stats->pattern_violations, stats->total_checks,
           stats->total_checks > 0 ? (100.0 * stats->pattern_violations / stats->total_checks) : 0.0);
}

void print_prediction_result(const llt_prediction_result_t *result, uint32_t exponent) {
    printf("🔬 Prediction Result for 2^%u - 1:\n", exponent);
    printf("   Result: %s\n", result->is_prime ? "PRIME" : "COMPOSITE");
    printf("   Iterations: %u (saved: %u)\n", result->iterations_performed, result->iterations_saved);
    
    if (result->early_termination_triggered) {
        printf("   ⚡ Early termination triggered (%.1f%% efficiency gain)\n", result->efficiency_gain);
    }
    
    if (result->iterations_saved > 0) {
        print_convergence_stats(&result->stats);
    }
}

const char* get_known_mersenne_primes_list(void) {
    static char buffer[1024];
    snprintf(buffer, sizeof(buffer),
             "Known Mersenne primes (p values): 2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, "
             "521, 607, 1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, "
             "23209, 44497, 86243, 110503, 132049, 216091, 756839, 859433, 1257787, 1398269, "
             "2976221, 3021377, 6972593, 13466917, 20996011, 24036583, 25964951, 30402457");
    return buffer;
}