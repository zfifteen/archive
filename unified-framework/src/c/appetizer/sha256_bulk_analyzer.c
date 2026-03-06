#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <CommonCrypto/CommonDigest.h>

// Function to compute SHA-256 hash of input string
void compute_sha256(const char *input, unsigned char *output) {
    CC_SHA256(input, strlen(input), output);
}

// Function to compute alignment pattern and coverage for hash values (H0-H7)
void compute_alignment_hash(uint32_t *words, int *alignment, int *aligned_count) {
    double phi = (1.0 + sqrt(5.0)) / 2.0;
    double k_star = 0.03;
    double width_factor = 0.35;
    int primes[8] = {2, 3, 5, 7, 11, 13, 17, 19}; // Primes for initial hash constants
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
    // CSV header for easy parsing
    printf("Input,InputLength,CoveragePercent,AlignedCount,AlignmentPattern,Classification,StateHex\n");
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
        compute_alignment_hash(words, alignment, &aligned_count);
        uint64_t new_state = 0;
        for (int i = 0; i < 8; i++) {
            new_state |= ((uint64_t)alignment[i] << (7 - i));
        }
        for (int i = 1; i < 8; i++) {
            new_state |= (new_state & 0xFF) << (i * 8);
        }
        double coverage_percent = (double)aligned_count / 8 * 100.0;
        char pattern[9];
        for (int i = 0; i < 8; i++) {
            pattern[i] = alignment[i] ? '1' : '0';
        }
        pattern[8] = '\0';
        const char *classification = aligned_count >= 3 ? "Aligned" : "Not Aligned";
        // Escape commas in input to avoid CSV issues
        char escaped_input[1024];
        strncpy(escaped_input, input, sizeof(escaped_input) - 1);
        escaped_input[sizeof(escaped_input) - 1] = '\0';
        char *p = escaped_input;
        while (*p) {
            if (*p == ',') *p = ';';
            p++;
        }
        printf("%s,%zu,%.1f,%d,%s,%s,0x%016llx\n", escaped_input, strlen(input), coverage_percent, aligned_count, pattern, classification, new_state);
    }
    return 0;
}
