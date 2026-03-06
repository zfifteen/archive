# Inverse Mersenne Probe Tool

This directory contains the inverse Mersenne probe tool for benchmarking Z5D-guided factorization on RSA Challenge numbers.

## Build

```bash
make probe
```

This builds the `bin/probe` executable.

## Usage

```bash
./bin/probe <semiprime> <window_trials> <kappa_geo>
```

**Parameters:**
- `semiprime`: The composite number to factor (decimal)
- `window_trials`: Number of candidates to test around sqrt(N)
- `kappa_geo`: Z5D geometric density parameter (e.g., 0.30769)

**Output:** JSON line with timing and factorization results

## Example

```bash
# Test on RSA-100
./bin/probe 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139 1024 0.30769

# Test on small semiprime
./bin/probe 15 10 0.30769
# Output: {"n_bits":4,"window_trials":10,"time_ms":0.117,"found":true,"factor_bits":2,"z5d_preds":2,"mr_tests":0,"factor":"3"}
```

## Benchmark Harness

Use the Python benchmark harness to run comprehensive tests:

```bash
python3 scripts/benchmark_inverse_probe_rsa.py --windows 1024 4096 16384 --reps 5
```

This will:
- Test all RSA challenge numbers (RSA-100 through RSA-140) 
- Run multiple window sizes and repetitions
- Generate CSV and Markdown reports with bootstrap confidence intervals
- Save results to `benchmarks/` directory

## Implementation Details

The probe uses:
- **Z5D Predictions**: Guides factor search around sqrt(N) using Z5D prime prediction
- **High-Precision Arithmetic**: MPFR/GMP for accurate large number operations  
- **Miller-Rabin Testing**: Probabilistic primality testing for candidates
- **JSON Output**: Structured results for automated analysis

The tool integrates with the existing Z5D predictor (`src/c/z5d_predictor.c`) to provide guidance for factor search, testing the hypothesis that Z5D predictions can concentrate factors enough to reduce search cost vs uniform scanning.

**Note**: This is a research tool for hypothesis testing. Cryptographic claims require p < 10⁻¹⁰ statistical evidence.