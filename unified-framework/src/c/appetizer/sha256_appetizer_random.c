#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>

/*
 * Appetizer Random Test: SHA-256 Constants Geometric Predictability Critique
 * =========================================================================
 * This test evaluates a critique that coverage results (up to 75.0% for hash values)
 * in the Appetizer Demo are artifacts of the test setup, reproducible with random
 * numbers. It replaces SHA-256 constants with random uint32_t values and applies
 * the same predictive model and optimized parameters to compare coverage.
 *
 * Parameter Optimization Summary:
 * - k_star=0.03: Curvature parameter, tested across 0.02-0.08 with minimal
 *   impact on small primes (2-53); selected as a representative optimal value.
 * - width_factor=0.35: Bound width factor, optimized via sweeps (0.1-0.5) to
 *   achieve coverage of 75.0% for initial hash values and 62.5% for round
 *   constants, surpassing the initial ~50% target from Z Framework experiments.
 * - Findings: Parameter sweeps (Oct 2023) showed width_factor as the primary
 *   driver of coverage, with latest tests pushing hash coverage to 75.0%.
 *
 * Predictive Model: Uses a simple m*log(m) approximation for prime estimation,
 * adapted from fallback logic in hash_bounds.py, to center bounds on predicted
 * fractional parts.
 *
 * Objective: If coverage with random numbers matches SHA-256 results (~75.0% hash),
 * the critique holds (artifact of setup). If significantly different, the critique
 * is falsified, supporting unique patterns in SHA-256 constants.
 */

// Random initial hash values (replacing SHA-256 hash values, same size)
uint32_t h[8];

// Corresponding prime numbers for initial hash values (unchanged)
int primes[8] = {2, 3, 5, 7, 11, 13, 17, 19};

// Random round constants (replacing SHA-256 round constants, same size)
uint32_t k[16];

// Corresponding prime numbers for round constants (unchanged)
int k_primes[16] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53};

// k* parameter from Z Framework (tuning factor for geometric bounds, optimized via sweeps)
double k_star = 0.03;

// Width factor optimized via sweeps for improved coverage (75.0% hash, 62.5% round)
double width_factor = 0.35;

// Function to extract fractional part as a double (for analysis)
double get_fractional_part(uint32_t val) {
    return (double)val / (double)(1ULL << 32);
}

// Function to compute theta_prime using k* and prime index m
// Based on hash_bounds.py: theta_prime = phi * (((m % phi)/phi) ** k_star)
double compute_theta_prime(double m, double k_star, double phi) {
    double mod_val = fmod(m, phi);
    double normalized = mod_val / phi;
    return phi * pow(normalized, k_star);
}

// Function to predict approximate prime value using m * log(m) fallback
double predict_prime_approx(int m) {
    if (m <= 1) return 2.0;
    double m_d = (double)m;
    return m_d * log(m_d);
}

// Function to predict fractional part of square root for initial hash values
double predict_frac_sqrt(int m) {
    double p_approx = predict_prime_approx(m);
    double sqrt_val = sqrt(p_approx);
    return sqrt_val - floor(sqrt_val);
}

// Function to predict fractional part of cube root for round constants
double predict_frac_cbrt(int m) {
    double p_approx = predict_prime_approx(m);
    double cbrt_val = cbrt(p_approx);
    return cbrt_val - floor(cbrt_val);
}

// Function to check if fractional part is within bounds
int within_bounds(double frac, double center, double width) {
    double lower = center - (width / 2.0);
    double upper = center + (width / 2.0);
    if (lower < 0.0) lower = 0.0;
    if (upper > 1.0) upper = 1.0;
    return frac >= lower && frac <= upper;
}

// Function to initialize random arrays with a given seed
void init_random_arrays(unsigned int seed) {
    srand(seed);
    for (int i = 0; i < 8; i++) {
        h[i] = (uint32_t)rand();
    }
    for (int i = 0; i < 16; i++) {
        k[i] = (uint32_t)rand();
    }
}

int main() {
    // Golden ratio (phi) for geometric adjustment
    double phi = (1.0 + sqrt(5.0)) / 2.0;
    
    // Test with multiple seeds for robustness
    unsigned int seeds[] = {42, 12345, 67890};
    int num_seeds = 3;
    
    printf("SHA-256 Constants Geometric Predictability Critique Test (Random)\n");
    printf("=================================================================\n\n");
    printf("Testing if coverage results are artifacts of test setup using random numbers.\n");
    printf("Running with multiple seeds for robustness...\n\n");
    
    for (int s = 0; s < num_seeds; s++) {
        unsigned int seed = seeds[s];
        init_random_arrays(seed);
        printf("=== Test Run with Seed: %u ===\n", seed);
        printf("Random Initial Hash Values (fractional parts, replacing SHA-256):\n");
        printf("-------------------------------------------------------------\n");
        for (int i = 0; i < 8; i++) {
            printf("H%d (random): 0x%08x\n", i, h[i]);
        }
        printf("\nRandom Round Constants (fractional parts, replacing SHA-256):\n");
        printf("------------------------------------------------------------------\n");
        for (int i = 0; i < 16; i++) {
            printf("K%d (random): 0x%08x\n", i, k[i]);
        }
        printf("Summary: Random values replace SHA-256 constants to test setup bias.\n\n");
        
        printf("=== Geometric Lens (Bounds Analysis with k* = %.5f) ===\n", k_star);
        printf("Analyzing fractional parts against geometric bounds using k*...\n");
        printf("Width Factor: %.3f (optimized for ~75.0%% hash coverage with SHA-256)\n", width_factor);
        printf("Fractional Parts of Random Initial Hash Values and Predicted Bounds:\n");
        printf("-------------------------------------------------------------\n");
        int h_within_count = 0;
        for (int i = 0; i < 8; i++) {
            double frac = get_fractional_part(h[i]);
            double theta_prime = compute_theta_prime(primes[i], k_star, phi);
            double width = theta_prime * width_factor;
            double frac_pred = predict_frac_sqrt(primes[i]);
            int in_bounds = within_bounds(frac, frac_pred, width);
            if (in_bounds) h_within_count++;
            printf("H%d (prime=%d): Frac=%.6f, Predicted Center=%.6f, Width=%.6f, Within Bounds=%s\n", 
                   i, primes[i], frac, frac_pred, width, in_bounds ? "Yes" : "No");
        }
        printf("Summary for Random Initial Hash Values: %d/8 within predicted bounds (%.1f%% coverage)\n", 
               h_within_count, (double)h_within_count / 8 * 100.0);
        
        printf("\nFractional Parts of Random Round Constants and Predicted Bounds:\n");
        printf("------------------------------------------------------------------\n");
        int k_within_count = 0;
        for (int i = 0; i < 16; i++) {
            double frac = get_fractional_part(k[i]);
            double theta_prime = compute_theta_prime(k_primes[i], k_star, phi);
            double width = theta_prime * width_factor;
            double frac_pred = predict_frac_cbrt(k_primes[i]);
            int in_bounds = within_bounds(frac, frac_pred, width);
            if (in_bounds) k_within_count++;
            printf("K%d (prime=%d): Frac=%.6f, Predicted Center=%.6f, Width=%.6f, Within Bounds=%s\n", 
                   i, k_primes[i], frac, frac_pred, width, in_bounds ? "Yes" : "No");
        }
        printf("Summary for Random Round Constants: %d/16 within predicted bounds (%.1f%% coverage)\n", 
               k_within_count, (double)k_within_count / 16 * 100.0);
        printf("\n");
    }
    
    printf("=== Conclusion of Critique Test ===\n");
    printf("- Baseline SHA-256 Coverage: 75.0% (Hash), 62.5% (Round) with k*=%.5f, width_factor=%.3f.\n", k_star, width_factor);
    printf("- Compare above random coverage to baseline to assess if results are setup artifacts.\n");
    printf("  Similar coverage suggests critique holds (artifact of setup).\n");
    printf("  Significantly different coverage falsifies critique (unique SHA-256 patterns).\n");
    
    return 0;
}
