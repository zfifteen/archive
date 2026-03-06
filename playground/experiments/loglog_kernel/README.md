# LogLog Kernel

A clean, self-contained C99 library for computing log(log(x)) using arbitrary-precision arithmetic with GMP and MPFR.

## Overview

This library provides a deterministic implementation of the double-logarithm function log(log(x)) for arbitrary-precision inputs. It uses only GMP for integer arithmetic and MPFR for floating-point arithmetic, with no fallback paths or use of hardware floating-point types.

## Features

- **Pure C99**: Standard-compliant C implementation
- **Arbitrary Precision**: Configurable precision in bits
- **Multiple Rounding Modes**: Support for all MPFR rounding modes
- **Integer and Real Inputs**: Functions for both `mpz_t` and `mpfr_t` inputs
- **Comprehensive Tests**: Extensive test suite with edge cases
- **Performance Benchmarks**: Detailed benchmarking suite

## Requirements

- C99-compliant compiler (e.g., GCC 4.5+, Clang 3.0+)
- GMP library (GNU Multiple Precision Arithmetic Library)
- MPFR library (Multiple Precision Floating-Point Reliable Library)
- Make

### Installing Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install libgmp-dev libmpfr-dev build-essential
```

**macOS (Homebrew):**
```bash
brew install gmp mpfr
```

**Fedora/RHEL:**
```bash
sudo dnf install gmp-devel mpfr-devel
```

## Building

Build all components (library, tests, and benchmarks):
```bash
make
```

Build specific targets:
```bash
make libloglog_mpfr.a    # Build static library only
make test_loglog         # Build test binary only
make benchmark_loglog    # Build benchmark binary only
```

## Usage

### API Reference

The library provides the following functions (see `loglog_mpfr.h` for details):

#### Core Functions

```c
int loglog_mpfr_real(mpfr_t result, const mpfr_t x, mpfr_prec_t prec, mpfr_rnd_t rnd);
```
Computes log(log(x)) for an arbitrary-precision real input.

**Parameters:**
- `result`: Output parameter for log(log(x))
- `x`: Input value (must be > 1 for real result)
- `prec`: Precision in bits for computation
- `rnd`: Rounding mode (MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD)

**Returns:** MPFR ternary value indicating rounding direction

**Special Cases:**
- For 0 < x < 1: Returns NaN (log of negative number)
- For x = 1: Returns -∞ (log of zero)
- For x > 1: Returns finite value

```c
int loglog_mpfr_int(mpfr_t result, const mpz_t n, mpfr_prec_t prec, mpfr_rnd_t rnd);
```
Computes log(log(n)) for an arbitrary-precision integer input.

#### Helper Functions

```c
void loglog_mpfr_init(mpfr_t var, mpfr_prec_t prec);
void loglog_mpfr_clear(mpfr_t var);
const char* loglog_mpfr_version(void);
```

### Example Code

```c
#include "loglog_mpfr.h"
#include <stdio.h>

int main(void) {
    mpfr_t x, result;
    mpfr_prec_t prec = 256;  // 256 bits of precision
    
    // Initialize variables
    loglog_mpfr_init(x, prec);
    loglog_mpfr_init(result, prec);
    
    // Set x = 1000
    mpfr_set_ui(x, 1000, MPFR_RNDN);
    
    // Compute log(log(1000))
    loglog_mpfr_real(result, x, prec, MPFR_RNDN);
    
    // Print result
    printf("log(log(1000)) = ");
    mpfr_out_str(stdout, 10, 0, result, MPFR_RNDN);
    printf("\n");
    
    // Clean up
    loglog_mpfr_clear(x);
    loglog_mpfr_clear(result);
    
    return 0;
}
```

Compile and link:
```bash
gcc -std=c99 -o example example.c -L. -lloglog_mpfr -lgmp -lmpfr
```

## Testing

Run the comprehensive test suite:
```bash
make test
```

The test suite includes:
- Basic functionality tests
- Edge case handling (x = 1, x < 1)
- Precision consistency tests
- Monotonicity verification
- High-precision computations
- Integer input tests

## Benchmarking

Run the standard benchmark suite:
```bash
./run_benchmark.sh
```

Or run benchmarks directly:
```bash
make benchmark
```

The benchmark suite measures performance for:
- Small integer inputs (2 to 10,000)
- Large integer inputs (2^64 to 2^1024)
- Varying precision (64 to 2048 bits)
- Different rounding modes
- Various real number inputs (e, π, e^e, π^π)

Results are saved to timestamped files (`benchmark_results_YYYYMMDD_HHMMSS.txt`).

## Architecture

### File Structure

```
loglog_kernel/
├── loglog_mpfr.h          # Public API header
├── loglog_mpfr.c          # Implementation
├── test_loglog.c          # Test suite
├── benchmark_loglog.c     # Benchmark suite
├── Makefile               # Build system
├── run_benchmark.sh       # Benchmark runner script
└── README.md              # This file
```

### Implementation Details

The library uses a straightforward two-step process:
1. Compute log(x) using MPFR's `mpfr_log` function
2. Compute log of the result using `mpfr_log` again

All computations are performed at the specified precision with no intermediate rounding until the final result.

### Design Decisions

- **No hardware floats**: Exclusively uses GMP/MPFR types
- **No fallbacks**: Single code path for all inputs
- **Deterministic**: Given the same input and settings, always produces the same output
- **C99 only**: No C11 or later features, maximum compatibility
- **Static library**: Simple linking, no runtime dependencies beyond GMP/MPFR

## Mathematical Background

The double-logarithm function log(log(x)) has several interesting properties:

- **Domain**: (1, ∞) for real outputs
- **Range**: (-∞, ∞)
- **Monotonicity**: Strictly increasing on its domain
- **Special values**:
  - log(log(e^e)) = 1
  - log(log(e)) = log(1) = 0
  - log(log(e^(1/e))) = log(1/e) = -1

This function appears in various applications including:
- Complexity analysis (log-log plots)
- Number theory (prime number distribution)
- Algorithm analysis (doubly-logarithmic time complexity)

## License

This is experimental code for the playground repository. See repository LICENSE for details.

## Contributing

This is a standalone experiment. For modifications or improvements, please follow the repository's contribution guidelines.

## Version

Current version: 1.0.0

## References

1. GMP Manual: https://gmplib.org/manual/
2. MPFR Manual: https://www.mpfr.org/mpfr-current/mpfr.html
