#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <CommonCrypto/CommonDigest.h>

// Function to compute SHA-256 hash of input string
void compute_sha256(const char *input, unsigned char *output) {
    CC_SHA256(input, strlen(input), output);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <input_string>\n", argv[0]);
        return 1;
    }
    unsigned char hash[CC_SHA256_DIGEST_LENGTH];
    compute_sha256(argv[1], hash);
    uint32_t words[8];
    for (int i = 0; i < 8; i++) {
        words[i] = (hash[i*4] << 24) | (hash[i*4+1] << 16) | (hash[i*4+2] << 8) | hash[i*4+3];
    }
    printf("SHA-256 Classifier for input: %s\n", argv[1]);
    printf("=============================================\n\n");
    printf("=== SHA-256 Output Values ===\n");
    printf("Values as uint32_t (big-endian):\n");
    printf("---------------------------------\n");
    for (int i = 0; i < 8; i++) {
        printf("H%d: 0x%08x\n", i, words[i]);
    }
    printf("Note: Derived from SHA-256(\"%s\")\n\n", argv[1]);
    double phi = (1.0 + sqrt(5.0)) / 2.0;
    double k_star = 0.03;
    double width_factor = 0.35;
    int primes[8] = {2, 3, 5, 7, 11, 13, 17, 19};
    int alignment[8] = {0};
    int aligned_count = 0;
    printf("=== Geometric Lens Analysis (k* = %.5f, width_factor = %.3f) ===\n", k_star, width_factor);
    printf("\nFractional Parts and Predicted Bounds (Circular Distance):\n");
    printf("--------------------------------------------------------\n");
    for (int i = 0; i < 8; i++) {
        double frac = (double)words[i] / 4294967296.0; // 2^32
        double m = primes[i];
        double center = sqrt(m * log(m));
        center -= floor(center); // fractional part
        double mod_phi = fmod(m, phi);
        double theta_prime = phi * pow((mod_phi / phi), k_star);
        center = fmod(center + theta_prime, 1.0);
        double width = theta_prime * width_factor;
        double lower = fmod(center - width / 2.0, 1.0);
        double upper = fmod(center + width / 2.0, 1.0);
        int within_bounds = 0;
        if (lower < upper) {
            within_bounds = (frac >= lower && frac <= upper);
        } else {
            within_bounds = (frac >= lower || frac <= upper);
        }
        alignment[i] = within_bounds;
        if (within_bounds) aligned_count++;
        printf("H%d (prime=%d): Frac=%.6f, Predicted Center=%.6f, Width=%.6f, Within Bounds=%s\n",
               i, primes[i], frac, center, width, within_bounds ? "Yes" : "No");
    }
    printf("Coverage (Circular): %d/8 values within predicted bounds (%.1f%%)\n", aligned_count, (double)aligned_count / 8 * 100.0);
    printf("\n8-bit Alignment Pattern: ");
    for (int i = 0; i < 8; i++) {
        printf("%d", alignment[i]);
    }
    printf("\nClassification: %s (Threshold >= 5/8 bits set)\n", aligned_count >= 5 ? "Aligned" : "Not Aligned");
    printf("\nNote: Bounds centered on predicted fractional parts using m*log(m) approximation.\n");
    printf("Method adapted from hash-bounds.py (theta_prime = phi * (((m %% phi)/phi) ** k_star)).\n\n");
    printf("=== Conclusion ===\n");
    printf("This classifier checks if SHA-256 output shows geometric predictability tied to prime roots.\n");
    return 0;
}
