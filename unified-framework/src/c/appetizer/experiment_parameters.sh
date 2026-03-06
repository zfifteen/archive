#!/bin/bash

# Script to experiment with different thresholds and parameters for SHA-256 Classifier

# Ensure the binary exists
if [ ! -f "bin/sha256_bulk_analyzer_exp" ]; then
  echo "Error: Binary not found. Compiling sha256_bulk_analyzer_exp.c..."
  cat > sha256_bulk_analyzer_exp.c << 'CODE'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <CommonCrypto/CommonDigest.h>

void compute_sha256(const char *input, unsigned char *output) {
    CC_SHA256(input, strlen(input), output);
}

void compute_alignment_hash(uint32_t *words, int *alignment, int *aligned_count, double k_star, double width_factor) {
    double phi = (1.0 + sqrt(5.0)) / 2.0;
    int primes[8] = {2, 3, 5, 7, 11, 13, 17, 19};
    *aligned_count = 0;
    for (int i = 0; i < 8; i++) {
        double frac = (double)words[i] / 4294967296.0;
        double m = primes[i];
        double center = sqrt(m * log(m));
        center -= floor(center);
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
    if (argc < 4) {
        printf("Usage: %s <k_star> <width_factor> <input1> [input2 ...]\n", argv[0]);
        return 1;
    }
    double k_star = atof(argv[1]);
    double width_factor = atof(argv[2]);
    printf("Input,InputLength,CoveragePercent,AlignedCount,AlignmentPattern,Classification25,Classification375,Classification50,Classification625,StateHex\n");
    for (int arg = 3; arg < argc; arg++) {
        const char *input = argv[arg];
        unsigned char hash[CC_SHA256_DIGEST_LENGTH];
        compute_sha256(input, hash);
        uint32_t words[8];
        for (int i = 0; i < 8; i++) {
            words[i] = (hash[i*4] << 24) | (hash[i*4+1] << 16) | (hash[i*4+2] << 8) | hash[i*4+3];
        }
        int alignment[8];
        int aligned_count;
        compute_alignment_hash(words, alignment, &aligned_count, k_star, width_factor);
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
        pattern[8] = '\\0';
        const char *class25 = aligned_count >= 2 ? "Aligned" : "Not Aligned"; // 25%
        const char *class375 = aligned_count >= 3 ? "Aligned" : "Not Aligned"; // 37.5%
        const char *class50 = aligned_count >= 4 ? "Aligned" : "Not Aligned"; // 50%
        const char *class625 = aligned_count >= 5 ? "Aligned" : "Not Aligned"; // 62.5%
        char escaped_input[1024];
        strncpy(escaped_input, input, sizeof(escaped_input) - 1);
        escaped_input[sizeof(escaped_input) - 1] = '\\0';
        char *p = escaped_input;
        while (*p) {
            if (*p == ',') *p = ';';
            p++;
        }
        printf("%s,%zu,%.1f,%d,%s,%s,%s,%s,%s,0x%016llx\n", escaped_input, strlen(input), coverage_percent, aligned_count, pattern, class25, class375, class50, class625, new_state);
    }
    return 0;
}
CODE
  clang -Wall -Wextra -O2 -lm -o bin/sha256_bulk_analyzer_exp sha256_bulk_analyzer_exp.c
  if [ $? -ne 0 ]; then
    echo "Compilation failed. Exiting."
    exit 1
  fi
fi

# Read inputs from file
INPUTS=()
while IFS= read -r line; do
    INPUTS+=("$line")
done < large_input_set.txt

# Test different thresholds by running with default parameters but different classification in output
# Test different k_star and width_factor values
for k_star in 0.02 0.03 0.04; do
  for width in 0.3 0.35 0.4; do
    echo "Running experiment with k_star=$k_star, width_factor=$width"
    ./bin/sha256_bulk_analyzer_exp "$k_star" "$width" "${INPUTS[@]}" > "results_k${k_star}_w${width}.csv"
    echo "Completed: k_star=$k_star, width_factor=$width, saved to results_k${k_star}_w${width}.csv"
  done
done

echo "All experiments completed. Results saved to respective CSV files."
