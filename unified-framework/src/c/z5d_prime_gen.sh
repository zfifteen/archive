#!/bin/zsh

# Check for required commands
type gdate >/dev/null 2>&1 || { echo "gdate is required. Install with 'brew install coreutils'"; exit 1; }
type bc >/dev/null 2>&1 || { echo "bc is required. Install with 'brew install bc'"; exit 1; }

inputs=(
  700
  701
  702
  703
  704
  705
  706
  707
  708
  709
  710
  1000000
  10000000
  100000000
  1000000000
  10000000000
  100000000000
  100001000001
  100001000002
  100001000003
  100001000004
  100001000005
  100001000006
  100001000007
  100001000008
  100001000009
  100001000010
  1000000000000
  10000000000000
  100000000000000
  1000000000000000
  10000000000000000
  100000000000000000
  1000000000000000000
  10000000000000000000
)

for n in $inputs; do
  START=$(gdate +%s.%N)
  ./bin/z5d_prime_gen $n
  END=$(gdate +%s.%N)
  printf "Time: %.3f ms\n" "$(echo "($END-$START)*1000" | bc)"
done
