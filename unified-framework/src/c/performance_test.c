// Performance test comparing original vs enhanced prime generation
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <gmp.h>
#include <mpfr.h>
#include "z5d_predictor.h"

// Original simple approach
static void next_prime_simple(const mpz_t start, mpz_t out) {
    mpz_set(out, start);
    for (;;) {
        int r = mpz_probab_prime_p(out, 25);
        if (r > 0) return;
        mpz_add_ui(out, out, 2);
    }
}

// Enhanced approach (simplified version)
static unsigned long calculate_z5d_jump_simple(const mpz_t current) {
    double candidate_val = mpz_get_d(current);
    if (candidate_val <= 3.0) return 2;
    
    double ln_candidate = log(candidate_val);
    double approx_k = candidate_val / ln_candidate;
    double next_k = approx_k + 1.0;
    
    double predicted_next = z5d_prime(next_k, 
                                     ZF_Z5D_C_CALIBRATED,
                                     ZF_KAPPA_STAR_DEFAULT,
                                     ZF_KAPPA_GEO_DEFAULT,
                                     1);
    
    if (!isfinite(predicted_next) || predicted_next <= candidate_val) {
        double geodesic_jump = ln_candidate * ZF_KAPPA_GEO_DEFAULT;
        return (unsigned long)fmax(2.0, geodesic_jump);
    }
    
    double jump = predicted_next - candidate_val;
    double max_jump = ln_candidate * 10.0;
    double min_jump = 2.0;
    
    return (unsigned long)fmax(min_jump, fmin(jump, max_jump));
}

static void next_prime_enhanced(const mpz_t start, mpz_t out) {
    mpz_set(out, start);
    for (;;) {
        // Quick pre-filter
        if (mpz_probab_prime_p(out, 1) > 0) {
            // Adaptive reps
            size_t bits = mpz_sizeinbase(out, 2);
            int reps = (bits < 64) ? 5 : (bits < 256) ? 10 : (bits < 1024) ? 15 : 25;
            if (mpz_probab_prime_p(out, reps) > 0) return;
        }
        
        unsigned long jump = calculate_z5d_jump_simple(out);
        if (jump % 2 == 0 && mpz_odd_p(out)) jump += 1;
        mpz_add_ui(out, out, jump);
        if (mpz_even_p(out)) mpz_add_ui(out, out, 1);
    }
}

static double time_in_ms() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

int main() {
    printf("Prime Generation Performance Test\n");
    printf("================================\n\n");
    
    mpz_t start, prime1, prime2;
    mpz_inits(start, prime1, prime2, NULL);
    
    // Test with different ranges
    unsigned long test_starts[] = {1000007, 10000007, 100000007, 1000000007};
    int num_tests = sizeof(test_starts) / sizeof(test_starts[0]);
    
    for (int i = 0; i < num_tests; i++) {
        mpz_set_ui(start, test_starts[i]);
        
        printf("Testing from %lu:\n", test_starts[i]);
        
        // Test original approach
        double t1 = time_in_ms();
        next_prime_simple(start, prime1);
        double simple_time = time_in_ms() - t1;
        
        // Test enhanced approach
        double t2 = time_in_ms();
        next_prime_enhanced(start, prime2);
        double enhanced_time = time_in_ms() - t2;
        
        // Verify both found the same prime
        if (mpz_cmp(prime1, prime2) == 0) {
            gmp_printf("  Next prime: %Zd\n", prime1);
            printf("  Simple approach:   %.3f ms\n", simple_time);
            printf("  Enhanced approach: %.3f ms\n", enhanced_time);
            double speedup = simple_time / enhanced_time;
            printf("  Speedup: %.2fx", speedup);
            if (speedup > 1.4) printf(" (TARGET ACHIEVED: >40%% improvement)");
            printf("\n\n");
        } else {
            printf("  ERROR: Methods found different primes!\n");
            gmp_printf("  Simple: %Zd\n", prime1);
            gmp_printf("  Enhanced: %Zd\n", prime2);
            printf("\n");
        }
    }
    
    mpz_clears(start, prime1, prime2, NULL);
    return 0;
}