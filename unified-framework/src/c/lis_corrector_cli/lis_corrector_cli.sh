#!/bin/bash
# LIS-Corrector CLI Test Suite - Cosmic Scale Edition
# ===================================================
#
# Comprehensive test of Z5D-seeded nth prime finder with Lucas pre-filtering
# and deterministic Miller-Rabin verification. Tests empirical accuracy vs PNT
# across 18 orders of magnitude from n=10^1 to n=10^18.
#
# Output format explanation:
# - n:               Prime index (1-indexed)
# - p_true:          True nth prime (from known values or search result)
# - z5d_seed:        Z5D predictor seed value
# - baseline:        Total candidates checked (wheel-30 optimization)
# - mr_calls:        Miller-Rabin primality test calls (after Lucas filter)
# - reduction_pct:   Lucas filter efficiency: (1 - mr_calls/baseline) * 100
# - z5d_accuracy_pct: Z5D prediction accuracy: (1 - |z5d_seed - p_true|/p_true) * 100
# - verified:        1 if verified against known prime, 0 if unverified
# - elapsed_s:       Wall-clock time in seconds

echo "# LIS-Corrector Z5D Performance Analysis - Cosmic Scale Edition"
echo "# Z Framework: Empirical prime prediction across 18 orders of magnitude"
echo "# Testing range: n=10^1 to n=10^18 (1 quintillion scale)"
echo "# Author: Dionisio Alberto Lopez III (D.A.L. III)"
echo ""
echo "Hardware Configuration:"
echo "======================"
echo "CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || uname -p)"
echo "Cores: $(sysctl -n hw.ncpu 2>/dev/null || nproc)"
echo "Memory: $(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1024 / 1024 / 1024 ))GB"
echo "Architecture: $(uname -m)"
echo "OS: $(uname -s) $(uname -r)"
echo ""
echo "n,p_true,z5d_seed,baseline,mr_calls,reduction_pct,z5d_accuracy_pct,verified,elapsed_s"

# Test case 1: Small primes (n=10^1)
./bin/lis_corrector_cli 10

# Test case 2: Medium primes (n=10^2)
./bin/lis_corrector_cli 100

# Test case 3: Large primes (n=10^3)
./bin/lis_corrector_cli 1000

# Test case 4: Very large primes (n=10^4)
./bin/lis_corrector_cli 10000

# Test case 5: Ultra-large primes (n=10^5)
./bin/lis_corrector_cli 100000

# Test case 6: Mega-scale primes (n=10^6)
./bin/lis_corrector_cli 1000000

# Test case 7: Giga-scale primes (n=10^7) with reduced window
# Note: Using smaller window to test graceful degradation
./bin/lis_corrector_cli 10000000 --window 100000

# Test case 8: Extreme-scale primes (n=10^8)
./bin/lis_corrector_cli 100000000

# Test case 8a: Mid-range verification points for accuracy validation
./bin/lis_corrector_cli 200000000
./bin/lis_corrector_cli 300000000
./bin/lis_corrector_cli 500000000
./bin/lis_corrector_cli 750000000

# Test case 9: Tera-scale primes (n=10^9) - First verified giga-scale point
# Z5D accuracy expected <0.001% based on O(1/n) scaling
./bin/lis_corrector_cli 1000000000

# Test case 10: Peta-scale primes (n=10^10) - Historical APL 1994 verification
# Deterministic MR with 7-witness set handles all uint64_t primes
./bin/lis_corrector_cli 10000000000

# Test case 11: Exa-scale primes (n=10^11) - Publicly verified computation
# Testing Z5D extrapolation limits with bootstrap CI validation
./bin/lis_corrector_cli 100000000000

# Test case 12: Zetta-scale primes (n=10^12) - Last verified tera-scale point
# Ultra-high precision MPFR arithmetic at 256-bit precision
./bin/lis_corrector_cli 1000000000000

# Test case 12a: Sequential prime prediction around n=10^12
# Demonstrate Z5D accuracy for consecutive nth primes (statistical sampling)
echo "# Testing sequential prediction accuracy around tera-scale (n=10^12 ± 50)"
for offset in $(seq -50 5 50); do
  n=$((1000000000000 + offset))
  ./bin/lis_corrector_cli "$n"
done

# Test case 12b: Dense sampling around multiple verification points
# Shows Z5D interpolation capability between known anchors
echo "# Dense sampling around verified mega-scale points"
for base in 1000000 10000000 100000000; do
  echo "# Sequential testing around n=$base"
  for offset in $(seq -10 2 10); do
    ./bin/lis_corrector_cli $((base + offset))
  done
done

# Test case 12c: Power-of-10 neighborhoods
# Testing Z5D performance in immediate vicinity of clean powers
echo "# Testing n=10^6 neighborhood (verified anchor)"
for n in 999990 999995 1000000 1000005 1000010; do
  ./bin/lis_corrector_cli "$n"
done

echo "# Testing n=10^9 neighborhood (giga-scale verified anchor)"
for n in 999999990 999999995 1000000000 1000000005 1000000010; do
  ./bin/lis_corrector_cli "$n"
done

echo "# Testing n=10^10 neighborhood (historical APL 1994 anchor)"
for n in 9999999990 9999999995 10000000000 10000000005 10000000010; do
  ./bin/lis_corrector_cli "$n"
done

# Test case 13: Yotta-scale primes (n=10^13)
# Z Framework geodesic mapping with κ_geo=0.3 optimization
./bin/lis_corrector_cli 10000000000000

# Test case 14: Ronna-scale primes (n=10^14)
# Testing theoretical Z5D limits with statistical significance
./bin/lis_corrector_cli 100000000000000

# Test case 15: Quetta-scale primes (n=10^15)
# Maximum validated range for empirical Z5D accuracy claims
./bin/lis_corrector_cli 1000000000000000

# Test case 16: Ultra-scale primes (n=10^16)
# Approaching theoretical limits of deterministic MR witnesses
./bin/lis_corrector_cli 10000000000000000

# Test case 17: Hyper-scale primes (n=10^17)
# Clean run up to uint64_t
./bin/lis_corrector_cli 100000000000000000

# Test case 18: Cosmic-scale primes (n=10^18)
# Ultimate test of Z Framework mathematical foundations
# Note: Entering calming waters... and hitting the uint64_t wall.
./bin/lis_corrector_cli 1000000000000000000
