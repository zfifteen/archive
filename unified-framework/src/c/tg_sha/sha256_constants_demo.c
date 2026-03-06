#include <stdio.h>
#include <stdint.h>
#include <math.h>

// SHA-256 initial hash values (fractional parts of square roots of first 8 primes)
uint32_t h[8] = {
    0x6a09e667, // sqrt(2)
    0xbb67ae85, // sqrt(3)
    0x3c6ef372, // sqrt(5)
    0xa54ff53a, // sqrt(7)
    0x510e527f, // sqrt(11)
    0x9b05688c, // sqrt(13)
    0x1f83d9ab, // sqrt(17)
    0x5be0cd19  // sqrt(19)
};

// Corresponding prime numbers for initial hash values
int primes[8] = {2, 3, 5, 7, 11, 13, 17, 19};

// First 16 of 64 SHA-256 round constants (fractional parts of cube roots of first 64 primes)
uint32_t k[16] = {
    0x428a2f98, // cube root of 2
    0x71374491, // cube root of 3
    0xb5c0fbcf, // cube root of 5
    0xe9b5dba5, // cube root of 7
    0x3956c25b, // cube root of 11
    0x59f111f1, // cube root of 13
    0x923f82a4, // cube root of 17
    0xab1c5ed5, // cube root of 19
    0xd807aa98, // cube root of 23
    0x12835b01, // cube root of 29
    0x243185be, // cube root of 31
    0x550c7dc3, // cube root of 37
    0x72be5d74, // cube root of 41
    0x80deb1fe, // cube root of 43
    0x9bdc06a7, // cube root of 47
    0xc19bf174  // cube root of 53
};

// Corresponding prime numbers for round constants
int k_primes[16] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53};

// k* parameter from Z Framework (tuning factor for geometric bounds)
double k_star = 0.04449;

// Width factor optimized for ~50% coverage from hash-bounds experiments
double width_factor = 0.155;

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

int main() {
    // Golden ratio (phi) for geometric adjustment
    double phi = (1.0 + sqrt(5.0)) / 2.0;
    
    printf("SHA-256 Constants Geometric Predictability Demonstration\n");
    printf("=======================================================\n\n");
    
    printf("=== A: Standard View (Raw Constants) ===\n");
    printf("Initial Hash Values (fractional parts of square roots of primes):\n");
    for (int i = 0; i < 8; i++) {
        printf("H%d (sqrt(%d)): 0x%08x\n", i, primes[i], h[i]);
    }
    printf("\nFirst 16 Round Constants (fractional parts of cube roots of primes):\n");
    for (int i = 0; i < 16; i++) {
        printf("K%d (cube root of %d): 0x%08x\n", i, k_primes[i], k[i]);
    }
    printf("Summary: In standard view, constants appear random and unrelated.\n\n");
    
    printf("=== B: Geometric Lens (Bounds Analysis with k* = %.5f) ===\n", k_star);
    printf("Analyzing fractional parts against geometric bounds using k*...\n");
    printf("Width Factor: %.3f (optimized for ~50%% coverage from hash-bounds experiments)\n", width_factor);
    printf("Fractional Parts of Initial Hash Values and Predicted Bounds:\n");
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
    printf("Summary for Initial Hash Values: %d/8 within predicted bounds (%.1f%% coverage)\n", 
           h_within_count, (double)h_within_count / 8 * 100.0);
    
    printf("\nFractional Parts of First 16 Round Constants and Predicted Bounds:\n");
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
    printf("Summary for Round Constants: %d/16 within predicted bounds (%.1f%% coverage)\n", 
           k_within_count, (double)k_within_count / 16 * 100.0);
    
    printf("\nNote: Bounds are centered on predicted fractional parts using a simple m*log(m) approximation.\n");
    printf("This adapts the hash-bounds.py approach (theta_prime = phi * (((m %% phi)/phi) ** k_star)).\n");
    printf("Summary: Through the geometric lens with k*, we test if SHA-256 constants fall within predictable bounds.\n\n");
    
    printf("=== Conclusion ===\n");
    printf("- Standard View (A): SHA-256 constants appear random, ensuring cryptographic strength.\n");
    printf("- Geometric Lens (B): Using k* = %.5f and width_factor = %.3f, bounds coverage is assessed,\n", k_star, width_factor);
    printf("  suggesting potential structural patterns tied to prime numbers under this analysis.\n");
    printf("This demonstration explores whether even random constants may have hidden geometric properties.\n");
    
    return 0;
}
