# Quick Start Guide

## Installation

```bash
cd experiments/PR-0002_prime_gap_analysis
pip install -r requirements.txt
```

## Run Validation Tests

```bash
python tests/test_validation.py
```

Expected output:
```
============================================================
Running Validation Tests
============================================================
✓ test_gap_calculation passed
✓ test_log_gap_magnitude passed
✓ test_array_alignment passed
✓ test_gap_properties passed (mode=6)
✓ π(1,000,000) = 78,498
✓ π(10,000,000) = 664,579
✓ test_oeis_maxgaps_1e6 passed: max_gap=114, prime=492113
✓ test_pnt_normalization passed: mean=1.0017

============================================================
All validation tests passed! ✓
============================================================
```

## Run Full Experiment

### At 10^6 scale (recommended for testing)
```bash
python run_experiment.py --scale 1e6
```

### At 10^7 scale (more comprehensive)
```bash
python run_experiment.py --scale 1e7
```

### At 10^8 scale (full analysis, ~10 min)
```bash
python run_experiment.py --scale 1e8
```

## Output Files

After running, you'll find:

```
results/
├── analysis_results_{scale}.json   # Numerical results
└── figures/
    ├── pnt_deviation.png          # PNT analysis
    ├── acf_plot.png               # Autocorrelation
    ├── gap_histogram.png          # Gap distribution
    └── qq_plot_{band}.png         # Lognormal test
```

## Example Usage in Python

```python
from src.prime_generator import generate_primes
from src.gap_analysis import analyze_gaps
from src.distribution_tests import test_distributions
from src.autocorrelation import test_autocorrelation

# Generate primes
primes = generate_primes(10**6)
print(f"Generated {len(primes):,} primes")

# Analyze gaps
gap_results = analyze_gaps(primes)
print(f"Mean gap/log(p): {gap_results['pnt_analysis']['overall_mean']:.4f}")

# Test distributions
dist_results = test_distributions(primes)
print(f"Distribution: {dist_results['interpretation']}")

# Test autocorrelation
acf_results = test_autocorrelation(primes)
print(f"ACF p-value: {acf_results['ljung_box_p']:.6f}")
```

## Understanding Results

### H-MAIN-A: PNT Deviation
- `overall_mean` near 1.0 → PNT is accurate
- `slope` near 0 → No systematic trend
- `p_value < 0.01` → Significant deviation

### H-MAIN-B: Lognormal
- `lognormal_count ≥ 2` → Evidence for lognormal
- `exponential_count ≥ 2` → Not lognormal

### H-MAIN-C: Autocorrelation
- `ljung_box_p < 0.01` → Gaps are correlated
- `ljung_box_p > 0.05` → Gaps are independent

## Validation Checks

The framework validates:
1. Prime counts against known values (π(10^6) = 78,498, etc.)
2. Maximal gaps against computed values
3. Array alignments and consistency
4. PNT normalization (mean gap/log(p) ≈ 1.0)

All checks must pass for results to be trustworthy.
