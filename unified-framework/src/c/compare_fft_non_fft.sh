#!/bin/bash

# Script to compare performance of FFT-zeta enabled vs non-FFT z5d_prime_gen

# Check for required commands
echo "Checking for required tools..."
command -v gdate >/dev/null 2>&1 || { echo "gdate is required. Install with 'brew install coreutils'"; exit 1; }
command -v bc >/dev/null 2>&1 || { echo "bc is required. Install with 'brew install bc'"; exit 1; }

# Input values to test
inputs=(
  700
  1000000
  1000000000
  1000000000000
  1000000000000000
)

# Paths to binaries
FFT_BINARY="./bin/z5d_prime_gen"
NON_FFT_BINARY="./bin/z5d_prime_gen_non_fft"

# Check if binaries exist
if [ ! -f "$FFT_BINARY" ]; then
  echo "FFT binary not found at $FFT_BINARY. Please build it first."
  exit 1
fi
if [ ! -f "$NON_FFT_BINARY" ]; then
  echo "Non-FFT binary not found at $NON_FFT_BINARY. Please build it first."
  exit 1
fi

echo "Starting performance comparison between FFT-zeta and non-FFT z5d_prime_gen..."
echo "========================================================================"

# Test loop for both binaries
for n in "${inputs[@]}"; do
  echo "Testing k=$n..."
  
  # Test FFT version
  echo "  FFT-zeta enabled version:"
  START=$(gdate +%s.%N)
  OUTPUT_FFT=$($FFT_BINARY $n --stats)
  END=$(gdate +%s.%N)
  TIME_FFT=$(echo "($END-$START)*1000" | bc)
  echo "    Time: $TIME_FFT ms"
  echo "$OUTPUT_FFT" | grep -E "prediction|Refined|MR rounds"
  echo ""

  # Test non-FFT version
  echo "  Non-FFT version:"
  START=$(gdate +%s.%N)
  OUTPUT_NON_FFT=$($NON_FFT_BINARY $n --stats)
  END=$(gdate +%s.%N)
  TIME_NON_FFT=$(echo "($END-$START)*1000" | bc)
  echo "    Time: $TIME_NON_FFT ms"
  echo "$OUTPUT_NON_FFT" | grep -E "prediction|Refined|MR rounds"
  echo ""

  # Calculate and display time difference
  TIME_DIFF=$(echo "$TIME_FFT - $TIME_NON_FFT" | bc)
  if [ $(echo "$TIME_DIFF > 0" | bc) -eq 1 ]; then
    echo "  Difference: FFT is slower by $TIME_DIFF ms"
  else
    TIME_DIFF=$(echo "-$TIME_DIFF" | bc)
    echo "  Difference: FFT is faster by $TIME_DIFF ms"
  fi
  echo "========================================================================"
done

echo "Performance comparison complete."
