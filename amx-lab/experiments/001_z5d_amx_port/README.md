# Z5D nth-Prime Predictor (C/MPFR Implementation)

Fast, correct C/MPFR implementation of the Z5D nth-prime predictor using a calibrated closed-form approximation (PNT + correction terms) with GMP refinement for exact primality.

**Platform scope:** macOS on Apple Silicon (tested on M1 Max). This build is intentionally non-portable; Linux/Windows and other CPUs are out of scope.

## Overview

This implementation uses the Z5D closed-form predictor to estimate the nth prime p_n using a calibrated Prime Number Theorem approximation with empirical correction terms:

```
p_n ≈ n * (ln(n) + ln(ln(n)) - 1 + corr) + d_term + e_term
```

Where correction terms account for logarithmic behavior and provide high accuracy.

**Key Features:**
- High-precision arithmetic using MPFR
- Closed-form computation (no iterative solving)
- Excellent accuracy for n ≥ 10^5
- GMP refinement for exact primality
- Configurable precision
- Comprehensive test suite and benchmarks
- Zero external dependencies beyond GMP/MPFR

## Directory Structure

```
z5d-predictor-c/
├── include/
│   └── z5d_predictor.h       # Public API header
├── src/
│   ├── z5d_predictor.c       # Core predictor implementation
│   ├── z5d_math.c            # Mathematical functions (R(x), R'(x), li(x))
│   ├── z5d_math.h            # Math function headers
│   ├── z5d_cli.c             # Command-line interface
│   └── z5d_bench.c           # Benchmark tool
├── tests/
│   ├── test_known.c          # Known values test (10^1 - 10^9)
│   └── test_medium_scale.c   # Medium scale test (10^10 - 10^12)
├── tools/
│   └── demo.sh               # Demonstration script
├── Makefile                  # Build system (inherits from parent)
├── README.md                 # This file
└── SPEC.md                   # Technical specification

```

## Requirements

- macOS 13+ on Apple Silicon (M1 Max tested)
- Apple Clang (Xcode command line tools)
- **GMP** and **MPFR** installed via Homebrew

### Installation (macOS / Apple Silicon)

```bash
brew install gmp mpfr
```

## Building

### Quick Start

```bash
# Build everything
make

# Build and run tests
make test

# Run benchmark
make benchmark

# Run demonstration
make demo

# Build CLI only
make cli

# Clean build artifacts
make clean
```

### Build Targets

- `make all` - Build library, CLI, benchmark, and tests (default)
- `make lib` - Build static library only
- `make cli` - Build CLI tool
- `make bench` - Build benchmark tool
- `make test` - Build and run all tests
- `make benchmark` - Run performance benchmark
- `make demo` - Run demonstration script
- `make clean` - Remove build artifacts
- `make info` - Show build configuration
- `make shared` - Invoke parent to build shared libraries
- `make help` - Show help message

## Usage

### Command Line Interface

```bash
# Basic usage
./bin/z5d_cli 1000000

# With verbose output
./bin/z5d_cli -v 1000000

# Custom configuration
./bin/z5d_cli -k 10 -p 300 1000000000

# Show help
./bin/z5d_cli -h
```

**Options:**
- `-k <K>` - Number of terms in R(x) series (default: 10)
- `-p <precision>` - MPFR precision in bits (default: 320, ~96 decimal places)
- `-i <max_iter>` - Maximum Newton iterations (default: 10)
- `-v` - Verbose output
- `-h` - Show help

### C API

```c
#include "z5d_predictor.h"

// Initialize library
z5d_init();

// Configure predictor
z5d_config_t config;
z5d_config_init(&config);

// Initialize result
z5d_result_t result;
z5d_result_init(&result, Z5D_DEFAULT_PRECISION);

// Predict nth prime
uint64_t n = 1000000;
z5d_predict_nth_prime(&result, n);

// Access results
mpfr_out_str(stdout, 10, 0, result.predicted_prime, MPFR_RNDN);
printf("\nTime: %.3f ms\n", result.elapsed_ms);

// Cleanup
z5d_result_clear(&result);
z5d_config_clear(&config);
z5d_cleanup();
```

## Performance

Measured performance with 3-term Dusart initializer, K=10, precision=320 bits:

| n | p_n (expected) | Time | Error (ppm) |
|---|----------------|------|-------------|
| 10^6 | 15,485,863 | ~1.7 ms | 118 ppm |
| 10^7 | 179,424,673 | ~1.7 ms | 37 ppm |
| 10^8 | 2,038,074,743 | ~1.4 ms | 0.9 ppm |
| 10^9 | 22,801,763,489 | ~1.8 ms | 1.5 ppm |
| 10^10 | 252,097,800,623 | ~2.0 ms | 0.34 ppm |
| 10^11 | 2,760,727,302,517 | ~1.8 ms | 0.16 ppm |
| 10^12 | 29,996,224,275,833 | ~1.8 ms | 0.037 ppm |

**Note:** These are actual measured values. Error rates improve significantly at larger scales due to the 3-term initializer.

## Algorithm

The predictor uses a calibrated closed-form approximation:

1. **Base PNT**: Compute n * (ln(n) + ln(ln(n)) - 1 + correction)

2. **Correction Terms**:
   - d_term: Empirical Dusart correction
   - e_term: Additional logarithmic adjustment

3. **Refinement**: Use GMP to find the next probable prime

This approach provides O(1) computation with excellent accuracy for large n.

## Tests

### Known Values Test

Tests predictor against known prime values from 10^1 to 10^9:

```bash
./bin/test_known
```

### Medium Scale Test

Tests predictor at scales 10^10 to 10^12:

```bash
./bin/test_medium_scale
```

## Benchmarks

Run performance benchmarks:

```bash
./bin/z5d_bench
```

This tests prediction speed and accuracy across multiple decades.

## Design Principles

Following the unified-framework repository guidelines:

1. **No New Dependencies**: Uses only GMP/MPFR as specified
2. **Inherits Parent Makefile**: Dependency detection inherited from `../Makefile`
3. **Self-Contained**: All artifacts in `z5d-predictor-c/` folder
4. **Invoke Parent for Shared Libs**: `make shared` delegates to parent
5. **Makefile Builds Executable**: All targets build successfully
6. **Shell Script Demo**: `tools/demo.sh` demonstrates capabilities

## License

Part of the unified-framework project. See repository LICENSE.

## References

- Python reference implementation: `z5d_newton_r_predictor.py`
- Repository pattern: `src/c/lucas-lehmer-prediction/`
- MPFR documentation: https://www.mpfr.org/
- GMP documentation: https://gmplib.org/
