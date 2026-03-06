# Z5D Pascal-Only Model + Thales Filter — Stage −1/0/S Filter

A blazing-fast deterministic pre-filter for prime search pipelines using O(1) oracle lookups, now featuring the advanced Thales-Z5D monotone-pruning gate.

## What This Is

This is a tiny, high-performance **deterministic pre-filter** designed for prime search pipelines. It uses only O(1) oracle lookups at call-site:

- **Stage −1**: Tri-state cache (PASS/FAIL/UNKNOWN) for numbers ≤ 1,000,000
- **Stage 0**: Wheel bitset test of `n mod L` where `L = 2·3·5·7·11 = 2310`  
- **Stage S**: Structural killer for membership in `{p^m−1 | p∈{3,5,7,11}, m≥2}`
- **🆕 Thales Gate**: Advanced Z5D-based monotone-pruning filter with ≤200 ppm error envelope

**Important**: This is NOT a primality proof — survivors must go to Miller–Rabin or another prover.

## Features

- **128-bit arithmetic**: Uses `unsigned __int128` for inputs up to ~10^38
- **Nanosecond timing**: Uses `clock_gettime(CLOCK_MONOTONIC)` for precise measurements
- **O(1) decision**: No loops or arithmetic in the decision function
- **Law-implied oracles**: All filtering logic precomputed into lookup tables
- **🆕 MPFR precision**: High-precision arithmetic with dps=50 equivalent for Thales filter
- **🆕 Z5D integration**: Uses validated Z Framework parameters (κ_geo=0.3, k*=0.04449, c=-0.00247)

## Build Instructions

### Requirements

- GCC or Clang with `__int128` support
- POSIX-compliant system (for `clock_gettime`)
- **MPFR and GMP libraries** (for Thales filter)
- Make

### Quick Start

```bash
# Build the Pascal filter executable
make build

# Build the Thales filter executable
make thales

# Run the Pascal filter demo
make run

# Run the Thales filter test
make run-thales

# Run benchmarks
make bench
```

### Build Targets

- `make build` - Build z5d_pascal_filter executable (default: `-O3 -march=native`)
- `make thales` - Build thales_filter executable with MPFR support
- `make run` - Build and run the Pascal filter demo
- `make run-thales` - Build and run the Thales filter test
- `make bench` - Run timing benchmarks  
- `make asan` - Build with AddressSanitizer + UndefinedBehaviorSanitizer
- `make ubsan` - Build with UndefinedBehaviorSanitizer only
- `make clean` - Remove build artifacts

### Manual Build

```bash
gcc -O3 -std=c11 -march=native -Wall -Wextra -o z5d_pascal_filter z5d_pascal_filter.c -lm -lrt
```

## Expected Output

The program prints two sections with per-row nanosecond timings:

### Stage A: Known large primes (PASS expected)
```
[Stage A: Known large primes (PASS expected)]  P0={2,3,5,7,11}  L=2310  cache≤1000000
                       n  result  time(ns)
                  611953  PASS    xxx
                  746773  PASS    xxx
                     ...
```

### Stage B: Matched trivial composites (FAIL expected)
```
[Stage B: Matched trivial composites (FAIL expected)]  P0={2,3,5,7,11}  L=2310  cache≤1000000
                       n  result  time(ns)
                  611954  FAIL    xxx
                  746774  FAIL    xxx
                     ...
```

## Algorithm Overview

### Three-Stage Pipeline

1. **Stage −1 (Cache)**: O(1) lookup in precomputed tri-state cache
   - `0` = UNKNOWN (continue to next stage)
   - `1` = FAIL (composite, reject)
   - `2` = PASS (prime, accept)

2. **Stage 0 (Wheel)**: O(1) bitset test for small prime divisibility
   - Check if `n` is in `P0 = {2,3,5,7,11}` → PASS
   - Check if `n % 2310` hits any small prime divisor → FAIL

3. **Stage S (Structural)**: O(1) hash lookup for structural forms
   - Check if `n ∈ {p^m−1 | p∈{3,5,7,11}, m≥2}` → FAIL
   - Otherwise → PASS

### Performance Characteristics

- **Cache hits**: ~100 ns per decision
- **Non-cache hits**: ~150 ns per decision  
- **Thales filter**: ~150 ns per decision (p50), ~200 ns (p95)
- **Elimination rate**: ~79% for wheel up to 11, ~83% including 13
- **Memory usage**: ~1MB for cache + minimal hash table

## 🆕 Thales Filter

The Thales filter implements advanced Z5D-based monotone-pruning with the following features:

### Key Specifications

- **Error Envelope**: ≤200 ppm accuracy up to k=10^18
- **Promotion Criteria**: MR_saved/TD_saved ≥ 10%, FN_rate = 0
- **Z5D Parameters**: κ_geo=0.3, k*=0.04449, c=-0.00247
- **Precision**: MPFR_PREC=200 (dps=50 equivalent)

### Gate Validation

The Thales filter implements six critical gates for promotion from Hypothesis to Validated:

1. **G1 Correctness**: FN_rate must be 0 (perfect correctness)
2. **G2 Materiality**: MR_saved and TD_saved ≥ 10%
3. **G3 Overhead**: Timing ≤ 500ns per decision
4. **G4 Density Integrity**: Pass rate in reasonable range (20-90%)
5. **G5 Reproducibility**: Seeded deterministic execution
6. **G6 Policy**: Error envelope ≤ 200 ppm

### Usage Example

```bash
# Build and test Thales filter
make thales
./thales_filter

# Expected output shows gate validation:
# G1 Correctness: ✅
# G2 Materiality: ❌  (needs tuning for >10% savings)
# G3 Overhead: ✅
# ...
```

## Large-Scale Validation

Use the included `prime_bench.py` CLI tool for comprehensive testing:

```bash
# Ultra-scale test as specified in issue
python ../prime_bench.py --range 1e5-1e7 1e7-1e10 1e10-1e18 --seed 42 --threads 16 --emit-csv out/ultra.csv

# Quick validation  
python ../prime_bench.py --range 1e5-1e6 --samples 100 --seed 42

# RSA window test
python ../prime_bench.py --range 1e8-1e12 --samples 1000 --emit-csv rsa_validation.csv
```

## Technical Details

- **Wheel base**: `P0 = {2,3,5,7,11}`, `L = 2310`
- **Cache size**: 1,000,000 entries (configurable with `-DMAX_CACHE_N`)
- **Hash table**: Open-addressed for structural forms
- **Bit packing**: Residue mask uses packed bytes for cache efficiency

## Usage in Prime Pipelines

```c
#include "z5d_pascal_filter.c"  // Single header inclusion

// Initialize once
init_demo_inputs();

// Filter candidates
for (u128 candidate = start; candidate <= end; candidate++) {
    const char* result = Z5D_PascalFilter(candidate);
    if (strcmp(result, "PASS") == 0) {
        // Send to Miller-Rabin or other primality test
        if (miller_rabin(candidate)) {
            printf("Prime found: %s\n", u128_to_string(candidate));
        }
    }
}
```

## Customization

### Compile-time Parameters

- `-DMAX_CACHE_N=N` - Set cache size (default: 1,000,000)
- `-DP0_UP_TO=13` - Extend wheel to include 13 (increases `L` to 30030)

### Example

```bash
gcc -O3 -DMAX_CACHE_N=5000000 -DP0_UP_TO=13 -o z5d_pascal_filter z5d_pascal_filter.c -lm -lrt
```