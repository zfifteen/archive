# Falsifying Strong Autocorrelation in Prime Gaps

This experiment implements the protocol defined in [TECH-SPEC.md](./TECH-SPEC.md) to test the claim that prime log-gaps exhibit strong autocorrelation (ACF(1) ≈ 0.8).

## Overview

The experiment performs the following steps:
1. **Data Extraction**: Generates primes in multiple disjoint ranges (e.g., $10^8$ to $10^{11}$) and computes log-gaps.
2. **Autocorrelation Analysis**: Computes ACF and PACF up to lag 100.
3. **Statistical Significance**: Uses permutation tests (10,000 iterations) to determine if observed autocorrelation could arise by chance.
4. **Robustness Testing**: Uses block bootstrap to construct 95% confidence intervals for ACF(1).
5. **Long-Range Dependence**: Estimates the Hurst exponent and performs Detrended Fluctuation Analysis (DFA).
6. **Null Model Comparison**: Compares observed results against:
   - **Cramér Model**: Independent draws (shuffled gaps).
   - **AR(1) Model**: A simple autoregressive process.
   - **Sieve Model**: A randomized sieve simulation.
7. **Falsification Check**: Evaluates the results against predefined success/falsification criteria.

## Usage

Run the experiment using the provided script:

```bash
python run_acf_falsification.py \
  --ranges "1e8:1e9,1e9:1e10,1e10:1e11" \
  --window-size 100000 \
  --max-lag 100 \
  --output results/
```

### Arguments

- `--ranges`: Comma-separated list of `P_min:P_max` pairs.
- `--window-size`: Number of gaps per window for stationarity analysis.
- `--max-lag`: Maximum lag for ACF/PACF computation.
- `--permutations`: Number of iterations for the permutation test.
- `--bootstrap-iterations`: Number of iterations for the block bootstrap.
- `--null-models`: Comma-separated list of null models to run (`cramer`, `ar1`, `sieve`).

## Outputs

Results are saved to the specified `--output` directory:
- `report.md`: A human-readable summary of the findings and the falsification verdict.
- `results.json`: Machine-readable data for all ranges and tests.
- `acf_{range}.png`: ACF plots for each range.
- `pacf_{range}.png`: PACF plots for each range.
- `acf_comparison.png`: Overlay of ACF curves across all ranges.
- `null_model_comparison.png`: Comparison of observed ACF(1) vs null models.
