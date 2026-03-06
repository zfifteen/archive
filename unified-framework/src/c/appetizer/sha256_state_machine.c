#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <CommonCrypto/CommonDigest.h>

// Function to compute SHA-256 hash of input string
void compute_sha256(const char *input, unsigned char *output) {
    CC_SHA256(input, strlen(input), output);
}

// Function to compute alignment pattern and coverage
void compute_alignment(uint32_t *words, int *alignment, int *aligned_count) {
    double phi = (1.0 + sqrt(5.0)) / 2.0;
    double k_star = 0.03;
    double width_factor = 0.35;
    int primes[8] = {2, 3, 5, 7, 11, 13, 17, 19};
    *aligned_count = 0;
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
        if (within_bounds) (*aligned_count)++;
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <input1> [input2 ...]\n", argv[0]);
        return 1;
    }
    printf("SHA-256 State Machine Classifier\n");
    printf("================================\n\n");
    int current_state = 0; // 0 for Not Aligned, 1 for Aligned
    for (int arg = 1; arg < argc; arg++) {
        const char *input = argv[arg];
        unsigned char hash[CC_SHA256_DIGEST_LENGTH];
        compute_sha256(input, hash);
        uint32_t words[8];
        for (int i = 0; i < 8; i++) {
            words[i] = (hash[i*4] << 24) | (hash[i*4+1] << 16) | (hash[i*4+2] << 8) | hash[i*4+3];
        }
        int alignment[8];
        int aligned_count;
        compute_alignment(words, alignment, &aligned_count);
        int new_state = (aligned_count >= 5) ? 1 : 0;
        printf("Input: %s\n", input);
        printf("Coverage: %d/8 (%.1f%%)\n", aligned_count, (double)aligned_count / 8 * 100.0);
        printf("8-bit Alignment Pattern: ");
        for (int i = 0; i < 8; i++) {
            printf("%d", alignment[i]);
        }
        printf("\nClassification: %s\n", new_state ? "Aligned" : "Not Aligned");
        printf("State Transition: %s -> %s\n\n", current_state ? "Aligned" : "Not Aligned", new_state ? "Aligned" : "Not Aligned");
        current_state = new_state;
    }
    printf("=== Conclusion ===\n");
    printf("State machine tracks transitions based on geometric alignment of SHA-256 outputs.\n");
    return 0;
}
