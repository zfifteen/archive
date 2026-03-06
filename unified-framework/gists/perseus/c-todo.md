# C99 Port of perseus.py - Implementation Plan

## Overview
Create an algorithmically identical C99 version of perseus.py, including the imported predictor function p_newton_R from z5d_newton_r_predictor.py. Use subfolders for organization: `make/` for build files, `std/` for custom headers/utilities.

## Dependencies
- GMP (for arbitrary precision integers, as mpmath uses big ints)
- MPFR (for arbitrary precision floats, replacing mpmath mpf)
- Build system: Makefile in `make/` subfolder
- External executable: `z5d_prime_gen` (assumed available in project root)

## Multi-Threading Opportunity
- The main parameter sweep loop (n from START_N to END_N) is independent per iteration, making it ideal for parallelization.
- Use OpenMP (via libomp, install with `brew install libomp` if needed) for simplicity on macOS.
- Add `-fopenmp` to Makefile CFLAGS and LDFLAGS.
- Implementation: Wrap the sweep loop with `#pragma omp parallel for` to distribute work across CPU cores (e.g., 4-8x speedup on M1 Max for large sweeps).
- Thread-safety: Ensure output (printf) is mutex-protected or use per-thread buffers; no shared MPFR state needed.
- Caveats: Overhead for small ranges (<1000); MPFR ops are CPU-bound but not vectorizable.

## Test-Driven Design (TDD) Approach
- Adopt TDD: Start with tests, implement stubs to pass tests and achieve 100% code coverage, then refine to full functionality.
- Testing Framework: Use Unity (lightweight C testing framework; install via `brew install unity` or clone from GitHub).
- Test Harness: Create `test/` subfolder with test files (e.g., `test_perseus.c`, `test_predictor.c`).
- Coverage: Use gcov/lcov for 100% branch and line coverage; integrate into Makefile (e.g., `make test` runs tests with coverage report).
- Steps:
    1. **Define Tests First**: For each function (e.g., `p_newton_R`, `fractional_sqrt`, `sha256_frac_to_u32_hex`, main sweep), create unit tests with assertions on inputs/outputs, edge cases, and error handling.
    2. **Implement Stubs**: Create non-functional stubs (e.g., return dummy values, no real computation) in corresponding .c files to satisfy compilation and allow tests to run without crashing.
    3. **Achieve 100% Coverage**: Run tests with coverage; stubs ensure all paths are hit (e.g., if/else branches with dummy logic).
    4. **Iterative Refinement**: Once coverage is 100%, incrementally replace stubs with full implementations, updating tests as needed to validate correctness.
    5. **Integration Tests**: Add end-to-end tests for the full sweep loop, verifying output format and bounds.

## Steps
1. **Install dependencies**: Use Homebrew to install GMP, MPFR, Unity, and OpenMP (libomp) if not present.
2. **Create directory structure**:
    - `std/`: Custom headers (e.g., utils.h for helpers)
    - `make/`: Makefile (include coverage flags: -fprofile-arcs -ftest-coverage)
    - `test/`: Test files and Unity framework
3. **Port z5d_newton_r_predictor.py**:
    - Implement `mu`, `riemann_R`, `riemann_R_prime`, `p_newton_R` in C using MPFR.
    - Handle high precision (equivalent to mp.dps=50).
    - Use MPFR for li() function (logarithmic integral).
4. **Port perseus.py main logic**:
    - Use popen() to call z5d_prime_gen for nth_prime.
    - Implement fractional_sqrt using MPFR sqrt and frac.
    - sha256_frac_to_u32_hex: Use MPFR to compute hex.
    - Parameter sweep and bounds checking.
    - Output results similar to Python.
5. **Makefile**: Compile with gcc, link GMP/MPFR, include paths, and test targets.
6. **Testing**: Run and verify against Python output for small n.

## Key Challenges
- MPFR initialization and memory management.
- Equivalent of mpmath's li(), nsum (use loops for sums).
- Popen parsing for z5d_prime_gen output.
- High precision floating point operations.

## Files to Create
- `perseus.c`: Main program.
- `predictor.c`: Port of predictor functions.
- `predictor.h`: Header for predictor.
- `std/utils.h`: Utility functions (e.g., string parsing).
- `make/Makefile`: Build script.
- `test/test_perseus.c`: Test harness for main logic.
- `test/test_predictor.c`: Tests for predictor functions.

## Build and Run
- `cd make && make`
- `./perseus` (executable in perseus/ ? or make/)
- `make test` for coverage report