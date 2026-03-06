# Performance Profiling for PR-0003

This directory contains tools for profiling and analyzing the performance of the prime log-gap experiment.

## Files

- `__init__.py` - Profiling utilities (PerformanceProfiler class)
- `profile_experiment.py` - Main profiling script
- `test_scaling.py` - Unit tests for validating scaling behavior

## Quick Start

### Profile at multiple scales:

```bash
python3 profiling/profile_experiment.py --scales 1e6,1e7 --bins 100
```

This will:
1. Profile the experiment at 10^6 and 10^7 scales
2. Time each major component
3. Calculate scaling exponents
4. Save results to `profiling_results.json`

### Run scaling validation tests:

```bash
python3 profiling/test_scaling.py
```

This runs unit tests that verify:
- Prime generation scales as expected
- Binning is sub-linear (fixed bins)
- Statistical tests have expected complexity
- Ljung-Box test is quadratic (bottleneck)
- Caching provides speedup

## Output

### profiling_results.json

Contains detailed timing data for each component at each scale, plus scaling analysis.

Example structure:
```json
{
  "profiling_date": "2025-12-22...",
  "scales_profiled": [1000000, 10000000],
  "results_by_scale": {
    "1000000": {
      "metadata": {...},
      "timings": {...},
      "memory": {...}
    },
    "10000000": {...}
  },
  "scaling_analysis": {
    "components": {
      "1_prime_generation": {
        "scaling_exponent": 0.56,
        "is_sublinear": true,
        ...
      },
      "4d_ljung_box": {
        "scaling_exponent": 2.03,
        "is_sublinear": false,
        ...
      }
    },
    "overall_scaling_exponent": 1.39
  }
}
```

## Key Findings

See `PERFORMANCE_ANALYSIS.md` for detailed findings. Summary:

- **Overall scaling (without viz): 1.39 (super-linear)**
- **Ljung-Box bottleneck: 2.03 (quadratic)**
- Prime generation: 0.56 (sub-linear with caching)
- Binning: 0.21 (genuinely sub-linear)
- KS tests: 0.91 (linear as expected)

## Options

```bash
python3 profiling/profile_experiment.py --help
```

- `--scales`: Comma-separated list (e.g., "1e6,1e7,1e8")
- `--bins`: Number of bins (default: 100)
- `--no-cache`: Disable caching to measure true computation time
- `--output`: Output JSON file (default: profiling_results.json)

## Understanding Results

### Scaling Exponent Interpretation

If time = k * n^α:
- α < 1.0: Sub-linear (faster than linear growth)
- α ≈ 1.0: Linear
- α > 1.0: Super-linear (slower than linear growth)

### Component Classifications

- **Sub-linear (α < 0.9)**: Binning, regression on bins
- **Linear (0.9 ≤ α ≤ 1.1)**: KS tests, ACF/PACF
- **Super-linear (α > 1.1)**: Ljung-Box test (α ≈ 2.0)

## Performance Recommendations

Based on profiling:

1. **For 10^8 scale**: Ljung-Box will take ~45 minutes
   - Consider using alternative autocorrelation test
   - Or skip autocorrelation testing at this scale

2. **For 10^9 scale**: Ljung-Box would take ~40-50 hours
   - MUST replace with approximate/sampled approach
   - Or remove this statistical test

3. **Caching is critical**: Reduces rerun time by 10x+

## Troubleshooting

### "No module named profiling"
Make sure you're running from the experiment directory:
```bash
cd experiments/PR-0003_prime_log_gap_optimized
python3 profiling/profile_experiment.py ...
```

### Out of memory
Reduce the maximum scale or increase available RAM.

### Very slow at 10^7
This is expected - Ljung-Box test takes ~45 seconds at this scale.
