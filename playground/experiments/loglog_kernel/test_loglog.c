/**
 * @file test_loglog.c
 * @brief Comprehensive test suite for loglog_mpfr library
 */

#include "loglog_mpfr.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ANSI color codes for output */
#define COLOR_GREEN "\033[0;32m"
#define COLOR_RED "\033[0;31m"
#define COLOR_RESET "\033[0m"

static int tests_passed = 0;
static int tests_failed = 0;

/* Helper function to print test results */
void print_test_result(const char* test_name, int passed) {
    if (passed) {
        printf("%s[PASS]%s %s\n", COLOR_GREEN, COLOR_RESET, test_name);
        tests_passed++;
    } else {
        printf("%s[FAIL]%s %s\n", COLOR_RED, COLOR_RESET, test_name);
        tests_failed++;
    }
}

/* Test: Version function */
void test_version(void) {
    const char* version = loglog_mpfr_version();
    int passed = (version != NULL && strlen(version) > 0);
    print_test_result("Version function returns non-empty string", passed);
}

/* Test: Basic computation for x = e^e (should give log(log(e^e)) = 1) */
void test_basic_e_to_e(void) {
    mpfr_t x, result, expected, e_base;
    mpfr_prec_t prec = 256;
    int passed;
    
    mpfr_init2(x, prec);
    mpfr_init2(result, prec);
    mpfr_init2(expected, prec);
    mpfr_init2(e_base, prec);
    
    /* Compute e = exp(1) */
    mpfr_set_ui(e_base, 1, MPFR_RNDN);
    mpfr_exp(e_base, e_base, MPFR_RNDN);
    
    /* Compute e^e */
    mpfr_pow(x, e_base, e_base, MPFR_RNDN);
    
    /* Compute log(log(e^e)) */
    loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    
    /* Expected result is 1 */
    mpfr_set_ui(expected, 1, MPFR_RNDN);
    
    /* Check if result is close to 1 (within tolerance) */
    mpfr_sub(expected, result, expected, MPFR_RNDN);
    mpfr_abs(expected, expected, MPFR_RNDN);
    passed = (mpfr_cmp_d(expected, 1e-15) < 0);
    
    mpfr_clear(x);
    mpfr_clear(result);
    mpfr_clear(expected);
    mpfr_clear(e_base);
    
    print_test_result("loglog(e^e) ≈ 1", passed);
}

/* Test: Computation for x = 2 */
void test_loglog_of_2(void) {
    mpfr_t x, result;
    mpfr_prec_t prec = 256;
    int passed;
    
    mpfr_init2(x, prec);
    mpfr_init2(result, prec);
    
    /* Set x = 2 */
    mpfr_set_ui(x, 2, MPFR_RNDN);
    
    /* Compute log(log(2)) */
    loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    
    /* log(log(2)) = log(0.693...) ≈ -0.3665... */
    /* Just verify it's negative and finite */
    passed = (mpfr_sgn(result) < 0 && mpfr_number_p(result));
    
    mpfr_clear(x);
    mpfr_clear(result);
    
    print_test_result("loglog(2) is negative and finite", passed);
}

/* Test: Computation for x = 10 */
void test_loglog_of_10(void) {
    mpfr_t x, result;
    mpfr_prec_t prec = 256;
    int passed;
    
    mpfr_init2(x, prec);
    mpfr_init2(result, prec);
    
    /* Set x = 10 */
    mpfr_set_ui(x, 10, MPFR_RNDN);
    
    /* Compute log(log(10)) */
    loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    
    /* log(log(10)) = log(2.302...) ≈ 0.8340... */
    /* Just verify it's positive and finite */
    passed = (mpfr_sgn(result) > 0 && mpfr_number_p(result));
    
    mpfr_clear(x);
    mpfr_clear(result);
    
    print_test_result("loglog(10) is positive and finite", passed);
}

/* Test: Integer input with loglog_mpfr_int */
void test_integer_input(void) {
    mpz_t n;
    mpfr_t result;
    mpfr_prec_t prec = 256;
    int passed;
    
    mpz_init(n);
    mpfr_init2(result, prec);
    
    /* Set n = 1000 */
    mpz_set_ui(n, 1000);
    
    /* Compute log(log(1000)) */
    loglog_mpfr_int(result, n, prec, MPFR_RNDN);
    
    /* log(log(1000)) = log(6.907...) ≈ 1.932... */
    /* Verify it's positive and finite */
    passed = (mpfr_sgn(result) > 0 && mpfr_number_p(result));
    
    mpz_clear(n);
    mpfr_clear(result);
    
    print_test_result("loglog(1000) via integer input is positive and finite", passed);
}

/* Test: Large integer input */
void test_large_integer(void) {
    mpz_t n;
    mpfr_t result;
    mpfr_prec_t prec = 512;
    int passed;
    
    mpz_init(n);
    mpfr_init2(result, prec);
    
    /* Set n = 2^100 */
    mpz_ui_pow_ui(n, 2, 100);
    
    /* Compute log(log(2^100)) */
    loglog_mpfr_int(result, n, prec, MPFR_RNDN);
    
    /* log(log(2^100)) = log(100*log(2)) = log(69.31...) ≈ 4.238... */
    /* Verify it's positive and finite */
    passed = (mpfr_sgn(result) > 0 && mpfr_number_p(result));
    
    mpz_clear(n);
    mpfr_clear(result);
    
    print_test_result("loglog(2^100) is positive and finite", passed);
}

/* Test: Precision consistency */
void test_precision_consistency(void) {
    mpfr_t x, result1, result2, diff;
    mpfr_prec_t prec1 = 128, prec2 = 256;
    int passed;
    
    mpfr_init2(x, prec2);
    mpfr_init2(result1, prec1);
    mpfr_init2(result2, prec2);
    mpfr_init2(diff, prec2);
    
    /* Set x = 100 */
    mpfr_set_ui(x, 100, MPFR_RNDN);
    
    /* Compute with different precisions */
    loglog_mpfr_real(result1, x, prec1, MPFR_RNDN);
    loglog_mpfr_real(result2, x, prec2, MPFR_RNDN);
    
    /* Results should be similar (lower precision should be subset of higher) */
    mpfr_sub(diff, result1, result2, MPFR_RNDN);
    mpfr_abs(diff, diff, MPFR_RNDN);
    
    /* Difference should be small */
    passed = (mpfr_cmp_d(diff, 1e-10) < 0);
    
    mpfr_clear(x);
    mpfr_clear(result1);
    mpfr_clear(result2);
    mpfr_clear(diff);
    
    print_test_result("Results consistent across different precisions", passed);
}

/* Test: Edge case x = 1 (should give -inf) */
void test_edge_case_one(void) {
    mpfr_t x, result;
    mpfr_prec_t prec = 256;
    int passed;
    
    mpfr_init2(x, prec);
    mpfr_init2(result, prec);
    
    /* Set x = 1 */
    mpfr_set_ui(x, 1, MPFR_RNDN);
    
    /* Compute log(log(1)) */
    loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    
    /* Result should be -inf */
    passed = mpfr_inf_p(result) && (mpfr_sgn(result) < 0);
    
    mpfr_clear(x);
    mpfr_clear(result);
    
    print_test_result("loglog(1) = -inf", passed);
}

/* Test: Edge case 0 < x < 1 (should give NaN) */
void test_edge_case_less_than_one(void) {
    mpfr_t x, result;
    mpfr_prec_t prec = 256;
    int passed;
    
    mpfr_init2(x, prec);
    mpfr_init2(result, prec);
    
    /* Set x = 0.5 */
    mpfr_set_d(x, 0.5, MPFR_RNDN);
    
    /* Compute log(log(0.5)) */
    loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    
    /* Result should be NaN (log(negative number)) */
    passed = mpfr_nan_p(result);
    
    mpfr_clear(x);
    mpfr_clear(result);
    
    print_test_result("loglog(0.5) = NaN", passed);
}

/* Test: Monotonicity - loglog should be monotonically increasing for x > 1 */
void test_monotonicity(void) {
    mpfr_t x1, x2, result1, result2;
    mpfr_prec_t prec = 256;
    int passed;
    
    mpfr_init2(x1, prec);
    mpfr_init2(x2, prec);
    mpfr_init2(result1, prec);
    mpfr_init2(result2, prec);
    
    /* Set x1 = 10, x2 = 100 */
    mpfr_set_ui(x1, 10, MPFR_RNDN);
    mpfr_set_ui(x2, 100, MPFR_RNDN);
    
    /* Compute log(log(x)) for both */
    loglog_mpfr_real(result1, x1, prec, MPFR_RNDN);
    loglog_mpfr_real(result2, x2, prec, MPFR_RNDN);
    
    /* result2 should be greater than result1 */
    passed = (mpfr_cmp(result2, result1) > 0);
    
    mpfr_clear(x1);
    mpfr_clear(x2);
    mpfr_clear(result1);
    mpfr_clear(result2);
    
    print_test_result("loglog is monotonically increasing (loglog(100) > loglog(10))", passed);
}

/* Test: Helper functions (init/clear) */
void test_helper_functions(void) {
    mpfr_t var;
    int passed = 1;
    
    /* Test init */
    loglog_mpfr_init(var, 128);
    
    /* Verify variable is initialized (set a value and read it back) */
    mpfr_set_ui(var, 42, MPFR_RNDN);
    passed = (mpfr_cmp_ui(var, 42) == 0);
    
    /* Test clear */
    loglog_mpfr_clear(var);
    
    print_test_result("Helper functions (init/clear) work correctly", passed);
}

/* Test: Very high precision computation */
void test_high_precision(void) {
    mpfr_t x, result, e_base;
    mpfr_prec_t prec = 1024;
    int passed;
    
    mpfr_init2(x, prec);
    mpfr_init2(result, prec);
    mpfr_init2(e_base, prec);
    
    /* Compute e = exp(1) */
    mpfr_set_ui(e_base, 1, MPFR_RNDN);
    mpfr_exp(e_base, e_base, MPFR_RNDN);
    
    /* Compute e^e */
    mpfr_pow(x, e_base, e_base, MPFR_RNDN);
    
    /* Compute log(log(e^e)) with high precision */
    loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    
    /* Result should be very close to 1 */
    mpfr_sub_ui(result, result, 1, MPFR_RNDN);
    mpfr_abs(result, result, MPFR_RNDN);
    passed = (mpfr_cmp_d(result, 1e-30) < 0);
    
    mpfr_clear(x);
    mpfr_clear(result);
    mpfr_clear(e_base);
    
    print_test_result("High precision (1024 bits) computation is accurate", passed);
}

int main(void) {
    printf("=== LogLog MPFR Test Suite ===\n\n");
    
    /* Run all tests */
    test_version();
    test_basic_e_to_e();
    test_loglog_of_2();
    test_loglog_of_10();
    test_integer_input();
    test_large_integer();
    test_precision_consistency();
    test_edge_case_one();
    test_edge_case_less_than_one();
    test_monotonicity();
    test_helper_functions();
    test_high_precision();
    
    /* Print summary */
    printf("\n=== Test Summary ===\n");
    printf("Passed: %s%d%s\n", COLOR_GREEN, tests_passed, COLOR_RESET);
    printf("Failed: %s%d%s\n", tests_failed > 0 ? COLOR_RED : COLOR_GREEN, 
           tests_failed, COLOR_RESET);
    printf("Total:  %d\n", tests_passed + tests_failed);
    
    return (tests_failed == 0) ? 0 : 1;
}
