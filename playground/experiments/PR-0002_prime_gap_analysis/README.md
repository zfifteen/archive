# Prime Gap Distribution Analysis

This experiment tests whether prime number gaps exhibit systematic deviations from Prime Number Theorem (PNT) predictions and whether their distributions follow lognormal or other structured patterns.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the complete experiment (10^6 scale)
python run_experiment.py --scale 1e6

# Run validation tests
python -m pytest tests/test_validation.py -v

# Run at larger scales (10^7, 10^8)
python run_experiment.py --scale 1e7
python run_experiment.py --scale 1e8
```

## Overview

### Hypotheses Under Test

1. **H-MAIN-A**: Gap Growth Relative to PNT
   - Tests if `mean(gap/log(p)) ≈ 1.0` as predicted by PNT
   - Looks for systematic sub/super-logarithmic trends

2. **H-MAIN-B**: Lognormal Gap Distribution
   - Tests if `log(gap)` follows a normal distribution within magnitude bands
   - Compares against exponential, gamma, and Weibull alternatives

3. **H-MAIN-C**: Gap Autocorrelation
   - Tests if consecutive gaps are correlated
   - Uses Ljung-Box test and ACF/PACF analysis

### Critical Implementation Details

**IMPORTANT:** This analysis focuses on **actual gap magnitudes** `gap[n] = p[n+1] - p[n]`, not log-space gaps `ln(p[n+1]/p[n])`.

```python
# CORRECT: Actual gap magnitudes
gaps = np.diff(primes)          # Integer differences
log_gaps = np.log(gaps)         # log(gap magnitudes)

# WRONG: Don't do this
log_gaps = np.diff(np.log(primes))  # This is log(p[n+1]/p[n])
```

## File Structure

```
PR-0002_prime_gap_analysis/
├── SPEC.md                    # Full technical specification
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── run_experiment.py          # Main experiment runner
├── src/
│   ├── prime_generator.py     # Segmented Sieve of Eratosthenes
│   ├── gap_analysis.py        # Core gap computations and PNT tests
│   ├── distribution_tests.py  # KS, Shapiro-Wilk, MLE fitting
│   ├── autocorrelation.py     # ACF, PACF, Ljung-Box
│   └── visualization.py       # Plotting functions
├── data/
│   └── primes_*.npy          # Cached prime arrays
├── results/
│   ├── analysis_results.json  # Statistical results
│   └── figures/               # Generated plots
└── tests/
    └── test_validation.py     # OEIS validation tests
```

## Validation

The implementation is validated against:

1. **Prime counts**: π(10^6) = 78,498, π(10^7) = 664,579, π(10^8) = 5,761,455
2. **OEIS A000101**: Maximal gaps at each scale
3. **PNT predictions**: Mean gap ratios within ±5%

## Usage Examples

### Run Full Analysis

```python
from src.prime_generator import generate_primes
from src.gap_analysis import analyze_gaps
from src.distribution_tests import test_distributions
from src.autocorrelation import test_autocorrelation

# Generate primes
primes = generate_primes(10**6)

# Analyze gaps relative to PNT
pnt_results = analyze_gaps(primes)

# Test distributions
dist_results = test_distributions(primes)

# Test autocorrelation
acf_results = test_autocorrelation(primes)
```

### Generate Specific Plots

```python
from src.visualization import plot_qq, plot_acf, plot_gap_histogram

# Q-Q plot for lognormal test
plot_qq(gaps, band='1e6_1e7', output='results/figures/qq_plot.png')

# ACF plot
plot_acf(gaps, output='results/figures/acf.png')

# Gap distribution histogram
plot_gap_histogram(gaps, output='results/figures/gap_hist.png')
```

## Expected Results

### Phase 1: Validation (10^6 scale)
- Prime count: 78,498
- Max gap: 114 at prime 492,113
- Mean gap/log(p): ~1.0 ± 0.05

### Phase 2: Extension (10^7 scale)
- Prime count: 664,579
- Max gap: 154 at prime 4,652,353
- Cross-scale consistency check

### Phase 3: Full Scale (10^8)
- Prime count: 5,761,455
- Max gap: 220 at prime 47,326,693
- Final statistical conclusions

## Computational Requirements

| Scale | Primes | Memory | Time (est.) |
|-------|--------|--------|-------------|
| 10^6  | 78,498 | ~1 MB  | ~10 sec     |
| 10^7  | 664,579| ~5 MB  | ~60 sec     |
| 10^8  | 5.76M  | ~46 MB | ~10 min     |

## References

- **SPEC.md**: Complete technical specification
- **OEIS A000101**: First occurrence of prime gaps
- **Prime Number Theorem**: π(x) ~ x/ln(x)
- **Cramér's conjecture**: max gap ~ (log p)²

## Status

**Version:** 1.0  
**Status:** Implementation in progress  
**Last Updated:** 2025-12-23
