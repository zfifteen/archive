#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpfr.h>
#include <gmp.h>

#define PHI 1.618033988749895
#define K_MIN 0.1
#define K_MAX 1.0
#define K_STEP 0.01
#define MAX_N 10000
#define THETA_MIN 0.4
#define THETA_MAX 1.2

// Simple primality test (for small n)
int is_prime(int n) {
    if (n <= 1) return 0;
    if (n <= 3) return 1;
    if (n % 2 == 0 || n % 3 == 0) return 0;
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return 0;
    }
    return 1;
}

// θ'(n,k) = φ * ((n mod φ) / φ)^k
double theta_prime(int n, double k) {
    double mod_phi = fmod(n, PHI);
    double ratio = mod_phi / PHI;
    return PHI * pow(ratio, k);
}

// Optimize k by brute-force
void optimize_k() {
    double best_k = 0.0;
    double best_f1 = 0.0;
    int true_primes[MAX_N] = {0};
    int num_true_primes = 0;

    // Precompute true primes
    for (int n = 2; n <= MAX_N; n++) {
        if (is_prime(n)) {
            true_primes[num_true_primes++] = n;
        }
    }

    printf("Optimizing k for θ'(n,k) predictor\n");
    printf("Max N: %d, True Primes: %d\n", MAX_N, num_true_primes);

    for (double k = K_MIN; k <= K_MAX; k += K_STEP) {
        int candidates[MAX_N];
        int num_candidates = 0;

        for (int n = 2; n <= MAX_N; n++) {
            double theta = theta_prime(n, k);
            if (theta >= THETA_MIN && theta <= THETA_MAX) {
                candidates[num_candidates++] = n;
            }
        }

        // Compute stats
        int tp = 0, fp = 0;
        for (int i = 0; i < num_candidates; i++) {
            if (is_prime(candidates[i])) tp++;
            else fp++;
        }
        int fn = num_true_primes - tp;
        double recall = (tp + fn) > 0 ? (double)tp / (tp + fn) : 0;
        double precision = (tp + fp) > 0 ? (double)tp / (tp + fp) : 0;
        double f1 = (precision + recall) > 0 ? 2 * precision * recall / (precision + recall) : 0;
        double reduction = (1.0 - (double)num_candidates / (MAX_N - 1)) * 100;

        printf("k=%.2f: Candidates=%d (%.1f%%), TP=%d, FP=%d, FN=%d, Prec=%.4f, Rec=%.4f, F1=%.4f\n",
               k, num_candidates, reduction, tp, fp, fn, precision, recall, f1);

        if (f1 > best_f1) {
            best_f1 = f1;
            best_k = k;
        }
    }

    printf("Best k: %.2f, Best F1: %.4f\n", best_k, best_f1);
}

int main() {
    optimize_k();
    return 0;
}