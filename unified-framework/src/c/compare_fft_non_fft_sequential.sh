#!/bin/bash

# Script to compare performance of FFT-zeta enabled vs non-FFT z5d_prime_gen sequentially

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

echo "Starting performance comparison between FFT-zeta and non-FFT z5d_prime_gen..."
echo "========================================================================"

echo "Building and testing non-FFT version..."
make clean && make gen FFT_ZETA_ENHANCE=0
if [ $? -ne 0 ]; then
  echo "Failed to build non-FFT version."
  exit 1
fi

# Arrays to store timing results for non-FFT
non_fft_times=()

# Test non-FFT version
for n in "${inputs[@]}"; do
  echo "Testing non-FFT for k=$n..."
  START=$(gdate +%s.%N)
  OUTPUT_NON_FFT=$(./bin/z5d_prime_gen $n --stats)
  END=$(gdate +%s.%N)
  TIME_NON_FFT=$(echo "($END-$START)*1000" | bc)
  non_fft_times+=("$TIME_NON_FFT")
  echo "  Non-FFT version:"
  echo "    Time: $TIME_NON_FFT ms"
  echo "$OUTPUT_NON_FFT" | grep -E "prediction|Refined|MR rounds"
  echo ""
done

echo "Building and testing FFT-zeta enabled version..."
make clean && make gen FFT_ZETA_ENHANCE=1 FFTW_AVAILABLE=1
if [ $? -ne 0 ]; then
  echo "Failed to build FFT version."
  exit 1
fi

# Arrays to store timing results for FFT
fft_times=()

# Test FFT version
for n in "${inputs[@]}"; do
  echo "Testing FFT-zeta for k=$n..."
  START=$(gdate +%s.%N)
  OUTPUT_FFT=$(./bin/z5d_prime_gen $n --stats)
  END=$(gdate +%s.%N)
  TIME_FFT=$(echo "($END-$START)*1000" | bc)
  fft_times+=("$TIME_FFT")
  echo "  FFT-zeta enabled version:"
  echo "    Time: $TIME_FFT ms"
  echo "$OUTPUT_FFT" | grep -E "prediction|Refined|MR rounds"
  echo ""
done

echo "Summary of Performance Comparison:"
echo "========================================================================"
for i in "${!inputs[@]}"; do
  n=${inputs[$i]}
  TIME_FFT=${fft_times[$i]}
  TIME_NON_FFT=${non_fft_times[$i]}
  TIME_DIFF=$(echo "$TIME_FFT - $TIME_NON_FFT" | bc)
  echo "k=$n:"
  echo "  Non-FFT Time: $TIME_NON_FFT ms"
  echo "  FFT Time: $TIME_FFT ms"
  if [ $(echo "$TIME_DIFF > 0" | bc) -eq 1 ]; then
    echo "  Difference: FFT is slower by $TIME_DIFF ms"
  else
    TIME_DIFF=$(echo "-$TIME_DIFF" | bc)
    echo "  Difference: FFT is faster by $TIME_DIFF ms"
  fi
  echo ""
done

echo "Performance comparison complete."
