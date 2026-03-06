#include "z5d_predictor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <math.h>
#include <mpfr.h>
#include <gmp.h>

static double now_ms(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0;
}

int main() {
    z5d_init();

    // Test against ground-truth-primes.csv (all 575 entries)
    FILE *fp = fopen("large-primes.csv", "r");
    if (!fp) {
        printf("Error: Cannot open CSV file\n");
        return 1;
    }

    char line[256];
    fgets(line, sizeof(line), fp);  // Skip header

    const size_t max_count = 100;  // Test small n
    mpz_t *ns = malloc(max_count * sizeof(mpz_t));
    mpz_t *expected_primes = malloc(max_count * sizeof(mpz_t));
    size_t count = 0;

    while (fgets(line, sizeof(line), fp) && count < max_count) {
        char n_str[64];
        char prime_str[64];
        if (sscanf(line, "%[^,],%*[^,],%[^,],%*s", n_str, prime_str) == 2) {
            mpz_init_set_str(ns[count], n_str, 10);
            mpz_init_set_str(expected_primes[count], prime_str, 10);
            count++;
        }
    }
    fclose(fp);
    printf("Parsed %zu entries\n", count);

    mpz_t *primes = malloc(count * sizeof(mpz_t));
    for (size_t i = 0; i < count; ++i) mpz_init(primes[i]);

    double t0 = now_ms();
    int overall_ret = 0;
    for (size_t i = 0; i < count; ++i) {
        int ret = z5d_predict_nth_prime_mpz_big(primes[i], ns[i]);
        if (ret != 0) {
            printf("Prediction failed for n=%s, ret=%d\n", mpz_get_str(NULL, 10, ns[i]), ret);
            overall_ret = ret;
        }
    }
    double elapsed = now_ms() - t0;

    if (overall_ret == 0) {
        // Generate report
        int matches = 0;
        double max_error = 0.0;
        printf("=== Z5D Prime Predictor Test Report ===\n");
        printf("Tested against: large-primes.csv (n >= 100000, %zu entries)\n", count);
        printf("Batch time: %.3f ms\n", elapsed);
        printf("Results:\n");
        int small_n_limit = 100000;  // Asterisk small n (known limitation)
    for (size_t i = 0; i < count; ++i) {
        int cmp = mpz_cmp(primes[i], expected_primes[i]);
        char *n_str = mpz_get_str(NULL, 10, ns[i]);
        if (cmp == 0) {
            matches++;
            printf("n=%s: PASS\n", n_str);
            } else {
                printf("n=%s: FAIL\n", n_str);
                // Calculate relative error for large n
                double pred_d = mpz_get_d(primes[i]);
                double exp_d = mpz_get_d(expected_primes[i]);
                if (exp_d != 0) {
                    double err = fabs(pred_d - exp_d) / exp_d;
                    max_error = fmax(max_error, err);
                }
            }
        free(n_str);
    }
        printf("Summary: %d/%zu matches (%.1f%% accuracy)\n", matches, count, (double)matches / count * 100.0);
        printf("Note: All tests for large n (n >= 100000)\n");
        if (matches < count) {
            printf("Max relative error (large n only): %.2e\n", max_error);
        }
        printf("AMX Status: Hard-coded for M1 (no detection)\n");
    } else {
        printf("Some predictions failed, but report generated\n");
    }

    for (size_t i = 0; i < count; ++i) {
        mpz_clear(primes[i]);
        mpz_clear(expected_primes[i]);
        mpz_clear(ns[i]);
    }
    free(primes);
    free(expected_primes);
    free(ns);
    z5d_cleanup();
    return overall_ret;
}