#!/bin/bash

# SHA-256 Output Classifier and 64-bit State Machine White Paper
# This script generates a live white paper with dynamic results from the SHA-256 Classifier.

# Ensure the binary exists
if [ ! -f "bin/sha256_state_machine_64bit_all_constants" ]; then
  echo "Error: Binary not found. Compiling sha256_state_machine_64bit_all_constants.c..."
  clang -Wall -Wextra -O2 -lm -o bin/sha256_state_machine_64bit_all_constants sha256_state_machine_64bit_all_constants.c
  if [ $? -ne 0 ]; then
    echo "Compilation failed. Exiting."
    exit 1
  fi
fi

# Create a file for the white paper content
WHITE_PAPER="sha256_white_paper_output.md"

# Write the static content to the white paper
cat << 'END' > $WHITE_PAPER
# SHA-256 Output Classifier and 64-bit State Machine White Paper
*Generated on: $(date)*

## Introduction
This white paper explores the SHA-256 Output Classifier, a novel tool for detecting geometric patterns in SHA-256 hash outputs based on prime-root predictability. We refine this into a 64-bit state machine, where each state encapsulates alignment patterns tied to SHA-256 seed constants (both initial hash values H0-H7 and round constants K0-K63, derived from primes). This live document includes dynamic results generated on Apple M1 Max hardware for optimal performance.

## Methodology
The classifier computes the SHA-256 hash of an input, splits it into 8 32-bit words (H0-H7), and assesses each word’s fractional part against predicted geometric bounds using frac(sqrt(m * log(m))) as the center, adjusted by phi and k*=0.03. An 8-bit alignment pattern (1 for aligned, 0 otherwise) is generated, with a threshold of >=3/8 bits (37.5%) for 'Aligned' classification, matching the baseline coverage of round constants. Additionally, alignment for a subset of round constants (K0-K7) is shown for baseline comparison. The 64-bit state machine encodes the H0-H7 pattern into a 64-bit state value (replicated across bytes for readability), tracking transitions over sequential inputs.

## 64-bit State Machine Design
The state machine uses a 64-bit integer to represent states, with each 8-bit segment reflecting the alignment pattern of the latest input’s hash (H0-H7). States transition with each input based on new patterns, providing up to 256 unique states. This ties to SHA-256 seed constants through the prime-based geometric model for both initial hash values and round constants, offering a detailed view of alignment behavior over input sequences.

## Live Results
Below are dynamic results from running the state machine on a sequence of test inputs. These are generated in real-time to demonstrate the classifier’s behavior and state transitions, incorporating analysis of both initial hash values and a subset of round constants.

### Test Sequence: Incremental Digit Strings and Diverse Inputs

```bash
END

# Run the state machine on a set of inputs and capture output
./bin/sha256_state_machine_64bit_all_constants "1" "11" "111" "CallMeIshmael" "RandomString" >> $WHITE_PAPER

# Append the closing part of the white paper
cat << 'END' >> $WHITE_PAPER
```

## Analysis of Results
The live results above illustrate how the 64-bit state machine transitions between states based on alignment patterns for H0-H7, with baseline alignment shown for a subset of round constants (K0-K7). Each state (displayed in hex) reflects the geometric predictability of SHA-256 outputs, with 'Aligned' classifications indicating significant matches (>=3/8 bits set, or 37.5%) to predicted bounds tied to seed constants, matching the round constants' baseline. Variability in state transitions, even for related inputs, highlights SHA-256’s pseudo-random nature, while recurring high-coverage states may suggest underlying structures worth further cryptanalytic exploration.

## Conclusion
The SHA-256 Output Classifier and its 64-bit state machine provide a novel framework for analyzing hash outputs through a geometric lens. Running on Apple M1 Max hardware ensures efficient computation, leveraging native cryptographic libraries. This live white paper demonstrates the tool’s ability to track alignment behavior dynamically, incorporating both initial hash values and round constants. Future work could refine state encoding, correlate input features with states, or visualize transitions for deeper insights. This approach remains exploratory, with potential applications in cryptographic pattern detection.

*End of Live White Paper. Re-run this script to refresh results.*
END

# Display the generated white paper
cat $WHITE_PAPER

# Make the script executable for future runs
chmod +x sha256_white_paper.sh

echo "White paper generated as $WHITE_PAPER and script made executable."
