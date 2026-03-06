#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>
#include <omp.h>
#include <time.h>
#include "z5d_factorization_shortcut.h"

#define SAMPLES 20
#define ITERATIONS 20
#define BITS 2048
#define MAX_ITERATIONS 1000

// Function to generate a random prime of specified bits
void generate_random_prime(mpz_t prime, gmp_randstate_ptr state, size_t bits) {
    mpz_t rand_num;
    mpz_init(rand_num);
    do {
        mpz_urandomb(rand_num, state, bits - 1);
        mpz_setbit(rand_num, bits - 1);  // Ensure it's at least 2^(bits-1)
        mpz_nextprime(prime, rand_num);
    } while (mpz_sizeinbase(prime, 2) > bits);
    mpz_clear(rand_num);
}

// Binary search for optimal epsilon
double find_optimal_epsilon() {
    int num_threads = omp_get_max_threads();
    gmp_randstate_ptr *states = malloc(num_threads * sizeof(gmp_randstate_ptr));
    if (states == NULL) {
        fprintf(stderr, "Error: malloc failed to allocate memory for states\n");
        exit(EXIT_FAILURE);
    }
    if (states == NULL) {
        fprintf(stderr, "Error: malloc failed to allocate memory for states\n");
        exit(EXIT_FAILURE);
    }
    for (int i = 0; i < num_threads; i++) {
        states[i] = malloc(sizeof(__gmp_randstate_struct));
        if (states[i] == NULL) {
            fprintf(stderr, "Error: malloc failed for states[%d]\n", i);
            // Free previously allocated states
            for (int j = 0; j < i; j++) {
                free(states[j]);
            }
            free(states);
            exit(EXIT_FAILURE);
        }
        if (states[i] == NULL) {
            fprintf(stderr, "Error: malloc failed for states[%d]\n", i);
            // Free previously allocated states
            for (int j = 0; j < i; j++) {
                gmp_randclear(states[j]);
                free(states[j]);
            }
            free(states);
            exit(EXIT_FAILURE);
        }
        gmp_randinit_default(states[i]);
        gmp_randseed_ui(states[i], time(NULL) + i);
    }

    double min_eps = 0.0;
    double max_eps = 1.0;
    int samples = SAMPLES;
    int iterations = ITERATIONS;
    size_t bits = BITS;

    for (int iter = 0; iter < iterations; iter++) {
        double eps = (min_eps + max_eps) / 2.0;
        int successes = 0;

        #pragma omp parallel for reduction(+:successes)
        for (int s = 0; s < samples; s++) {
            int thread_id = omp_get_thread_num();
            mpz_t p, q, n;
            mpz_inits(p, q, n, NULL);

            generate_random_prime(p, states[thread_id], bits);
            generate_random_prime(q, states[thread_id], bits);
            mpz_mul(n, p, q);  // n = p * q

            char *n_str = mpz_get_str(NULL, 10, n);
            z5d_factor_stat_t stat;
            int result = z5d_factorization_shortcut(n_str, MAX_ITERATIONS, eps, &stat);
            if (result == 1) {
                successes++;
            }
            z5d_factorization_free(&stat);
            free(n_str);

            mpz_clears(p, q, n, NULL);
        }

        double score = (double)successes / samples;
        if (score > 0.5) {
            max_eps = eps;
        } else {
            min_eps = eps;
        }
    }

    for (int i = 0; i < num_threads; i++) {
        gmp_randclear(states[i]);
        free(states[i]);
    }
    free(states);
    return (min_eps + max_eps) / 2.0;
}

int main() {
    double optimal_eps = find_optimal_epsilon();
    printf("Optimal epsilon (%d-bit modulus): %.4f\n", 2*BITS, optimal_eps);
    return 0;
}