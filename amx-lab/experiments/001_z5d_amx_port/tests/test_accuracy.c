/**
 * Z5D nth-Prime Predictor - Accuracy Test (Single Entry)
 * ======================================================
 *
 * Tests predictor accuracy against known value n=100000, prime=1299709
 *
 * @file test_accuracy.c
 * @version 1.0
 */

#include "../include/z5d_predictor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    printf("Z5D nth-Prime Predictor - Accuracy Test\n");
    printf("========================================\n\n");

    z5d_init();

    mpz_t predicted_prime;
    mpz_init(predicted_prime);

    const char* n_str = "100000";
    const char* expected_prime_str = "1299709";

    // Predict
    if (z5d_predict_nth_prime_str(predicted_prime, n_str) != 0) {
        fprintf(stderr, "Prediction failed for n=%s\n", n_str);
        return 1;
    }

        // Check if matches
        char* pred_str = mpz_get_str(NULL, 10, predicted_prime);
        if (pred_str == NULL) {
            fprintf(stderr, "mpz_get_str failed for n=%s\n", n_str);
            continue;
        }
        int match = strcmp(pred_str, prime_str) == 0;
        free(pred_str);

    printf("n=%s, match=%s\n", n_str, match ? "YES" : "NO");

    mpz_clear(predicted_prime);
    z5d_cleanup();

    printf("\n========================================\n");
    printf("Accuracy Summary:\n");
    printf("Matches: %d/1 (%.2f%%)\n", match, 100.0 * match);

    return 0;
}