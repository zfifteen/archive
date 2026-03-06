#!/bin/zsh

# Check for required commands
type gdate >/dev/null 2>&1 || { echo "gdate is required. Install with 'brew install coreutils'"; exit 1; }
type bc >/dev/null 2>&1 || { echo "bc is required. Install with 'brew install bc'"; exit 1; }

inputs=(
  700
  1000000
  1000000000
  1000000000000
  1000000000000000
  1000000000000000000
)

for n in $inputs; do
  START=$(gdate +%s.%N)
  ./bin/z5d_prime_gen $n --stats
  END=$(gdate +%s.%N)
  printf "Time for k=$n: %.3f ms\n\n" "$(echo "($END-$START)*1000" | bc)"
done
