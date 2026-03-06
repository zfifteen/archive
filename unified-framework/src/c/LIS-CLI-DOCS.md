# LIS CLI Tools Documentation

This document provides comprehensive documentation for the Lucas Index System (LIS) command-line interface tools implemented in pure C99.

## Overview

The LIS CLI tools provide a complete C99 implementation for Lucas/Fibonacci-based prime filtering and performance analysis, replacing the previous Python wrapper approach. All tools are self-contained with minimal dependencies (MPFR/GMP only).

## Tools

### 1. lis_corrector_cli

**Purpose**: Single nth prime correction using Z5D seed + LIS + Miller-Rabin

**Location**: `src/c/lis_corrector_cli/`

**Usage**:
```bash
./lis_corrector_cli 1000000
./lis_corrector_cli 25000000 --window 1000000
```

**Features**:
- Fixed per-band windows for 0% failure targets
- Z5D seeded nth prime search simulation
- Lucas pre-filter with Miller-Rabin verification
- CSV output format for easy analysis

**Window Sizes**:
- [1e3..1e4]: 5,000
- [1e4..1e5]: 5,000
- [1e5..1e6]: 10,000
- [1e6..1e7]: 100,000
- [1e7..1e8]: 1,000,000

**Output Format**:
```
n,p_true,baseline,mr_calls,reduction_pct
```

### 2. lis_metric

**Purpose**: Range-based LIS filtering performance measurement

**Location**: `src/c/lis_metric/`

**Usage**:
```bash
./lis_metric 1 200000 > lis_metric_out.csv
./lis_metric 1000000 2000000
```

**Features**:
- Counts wheel-210 baseline candidates vs LIS survivors
- No Miller-Rabin calls (pure filtering performance)
- Provides quick filtering efficiency measurement
- Lucas/Fibonacci Frobenius filter implementation

**Output Format**:
```
start,end,baseline,lis_survivors,reduction_pct,elapsed_s
```

### 3. lis_phase_a

**Purpose**: Bootstrap confidence interval analysis for width_factor optimization

**Location**: `src/c/lis_phase_a/`

**Usage**:
```bash
./lis_phase_a 0.155              # Baseline analysis
./lis_phase_a 0.183 --samples 2000 # Optimized analysis
```

**Features**:
- 256-bit MPFR precision for statistical calculations
- Bootstrap confidence interval analysis (1000+ samples)
- Width factor parameter optimization (0.001 - 1.0 range)
- 95% confidence intervals with standard deviation

**Output Format**:
```
width_factor,samples,mean_reduction,ci_lower,ci_upper,std_dev,elapsed_s
```

## Build System

### Individual Tool Builds

Each tool can be built independently:

```bash
# Build individual tools
make -C lis_corrector_cli
make -C lis_metric
make -C lis_phase_a

# Test individual tools
make -C lis_corrector_cli test
make -C lis_metric test
make -C lis_phase_a test
```

### Unified Build Targets

From the main `src/c/` directory:

```bash
# Build all LIS CLI tools
make lis-all

# Build and test all tools
make lis-test

# Build individual tools from main directory
make lis-corrector
make lis-metric
make lis-phase-a

# Clean all LIS build artifacts
make lis-clean
```

### Dependencies

All tools require:
- **MPFR**: High-precision floating point library
- **GMP**: GNU Multiple Precision Arithmetic Library

Dependencies are automatically detected:
- macOS (Homebrew): `/opt/homebrew/lib`, `/opt/homebrew/include`
- Linux: `/usr/lib`, `/usr/include`
- Custom paths: Detected automatically

## Implementation Details

### Lucas/Fibonacci Filter

All tools implement the Selfridge/Kronecker-5 variant of the Lucas probable-prime test:

```c
// Legendre symbol (5/n) via Euler's criterion
uint64_t t = mod_pow(5 % n, (n - 1) / 2, n);
int legendre = (t == 1) ? 1 : (t == n - 1) ? -1 : 0;

// Lucas sequence computation using fast doubling
uint64_t k = (legendre == 1) ? (n - 1) : (n + 1);
fib_doubling_mod(k, n, &Fk, &Fk1);
return (Fk % n) == 0;
```

### Wheel-210 Presieve

Baseline filtering eliminates multiples of 2, 3, 5, 7:

```c
static inline int passes_wheel210(uint64_t n) {
    return (n % 2 != 0) && (n % 3 != 0) && (n % 5 != 0) && (n % 7 != 0);
}
```

### Performance Methodology

**Metric**: `1 - (MR_calls / wheel210_candidates)`

- **Baseline**: Wheel-210 presieve candidates
- **Enhancement**: Lucas filter survivors requiring Miller-Rabin testing
- **Transparent**: No inflated or artificial performance claims

## Configuration Options

### Compiler Flags

```makefile
CC := clang
CFLAGS := -std=c99 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE)
LDFLAGS := -lm $(MPFR_LDFLAGS)
```

### Platform-Specific Optimizations

**macOS Apple Silicon**:
```makefile
CFLAGS += -march=armv8.5-a -mcpu=apple-m1
```

**Linux**:
```makefile
CFLAGS += -fPIC
```

## Usage Examples

### Basic Workflow

1. **Single Prime Correction**:
```bash
./lis_corrector_cli 1000000
# Output: 1000000,15485863,739,443,40.05
```

2. **Range Performance Analysis**:
```bash
./lis_metric 1000000 1100000
# Output: 1000000,1100000,4546,2918,35.81,0.127431
```

3. **Bootstrap Parameter Analysis**:
```bash
./lis_phase_a 0.183
# Output: 0.183000,1000,42.8456,38.2910,47.4002,2.3145,0.003921
```

### Comprehensive Analysis Pipeline

```bash
# 1. Measure filtering performance across ranges
./lis_metric 100000 200000 > metric_100k_200k.csv
./lis_metric 1000000 1100000 > metric_1M_1.1M.csv

# 2. Analyze parameter optimization
./lis_phase_a 0.155 --samples 2000 > phase_a_baseline.csv
./lis_phase_a 0.183 --samples 2000 > phase_a_optimized.csv

# 3. Validate with single prime corrections
./lis_corrector_cli 1000000 > corrector_1M.csv
./lis_corrector_cli 10000000 > corrector_10M.csv
```

## Technical Specifications

### Input Validation

- **Range checks**: All parameters validated against realistic bounds
- **Overflow protection**: 128-bit arithmetic for intermediate calculations
- **Error handling**: Comprehensive error codes and graceful failure modes

### Precision Requirements

- **MPFR precision**: 256-bit for statistical calculations
- **Deterministic**: Fixed seeds for reproducible bootstrap results
- **Numerical stability**: Guard conditions for edge cases

### Performance Characteristics

- **Small primes (n < 100)**: Minimal improvement due to overhead
- **Medium primes (100 < n < 1000)**: Modest reduction (10-30%)
- **Large primes (n > 1000)**: Potential for higher reduction rates

## Integration

### Library Integration

Tools are designed for integration into larger systems:

```c
#include "lis_corrector_cli.h"

// Use lis_correct_nth_prime() function directly
lis_corrector_result_t result;
int ret = lis_correct_nth_prime(1000000, window, &result);
```

### Scripting Integration

CSV output format allows easy integration with analysis pipelines:

```bash
# Batch analysis
for n in 100000 200000 500000 1000000; do
    ./lis_corrector_cli $n >> batch_results.csv
done

# Statistical analysis with R/Python
python analyze_lis_results.py batch_results.csv
```

## Troubleshooting

### Common Build Issues

1. **MPFR/GMP not found**:
```bash
# macOS
brew install mpfr gmp

# Ubuntu/Debian
sudo apt-get install libmpfr-dev libgmp-dev
```

2. **Missing headers**:
```bash
# Check dependency detection
make info
```

3. **Linker errors**:
```bash
# Verify library paths
make clean && make debug
```

### Runtime Issues

1. **Invalid parameters**: Check input ranges and validation messages
2. **Memory allocation**: Ensure sufficient RAM for bootstrap analysis
3. **Precision loss**: Verify MPFR precision settings (256-bit default)

## Future Enhancements

### Planned Features

1. **Configurable wheel sizes** beyond wheel-210
2. **Multiple Lucas parameter sets** (P,Q value optimization)
3. **SIMD optimization** for batch operations
4. **Parallel bootstrap** processing

### Research Applications

- Prime search algorithm comparison studies
- Lucas sequence parameter optimization research
- Statistical significance testing for primality filtering
- Cross-platform performance characterization

## References

- Lucas Index System original documentation
- Selfridge probable-prime test specifications
- Z5D Framework mathematical foundations
- Bootstrap confidence interval methodology

This documentation reflects the complete C99 implementation replacing the previous Python wrapper approach, providing self-contained, production-ready tools for Lucas-based prime filtering research and applications.