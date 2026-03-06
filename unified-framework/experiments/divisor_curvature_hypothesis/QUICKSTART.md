# Divisor-Based Curvature Hypothesis - Quick Start

## One-Line Summary
Tests if κ(n) = d(n)·ln(n)/e² separates primes from composites with 83% accuracy (actual: 93.8%).

## Run the Experiment

```bash
cd experiments/divisor_curvature_hypothesis
python run_experiment.py
```

## Expected Output
```
Prime mean κ: 0.739 (target: 0.74) - ✓ PASS
Composite mean κ: 2.252 (target: 2.25) - ✓ PASS
Separation ratio: 3.05x (target: ~3x) - ✓ PASS
Classification accuracy: 93.8% (target: ≥83%) - ✓ PASS
```

## View Results
- Results: `results.json`
- Plots: `plots/curvature_analysis.png` and `plots/golden_ratio_test.png`
- Summary: `EXPERIMENT_SUMMARY.md`

## Test Everything
```bash
python test_all.py
```

## Key Findings
1. **Primes have low curvature** (avg 0.739) because d(p) = 2
2. **Composites have high curvature** (avg 2.252) due to more divisors
3. **93.8% classification accuracy** exceeds 83% hypothesis target
4. **Golden ratio mod 1 is equidistributed** (χ² = 0.200)

## What is κ(n)?
```python
def curvature(n):
    d = count_divisors(n)  # Number of divisors
    return d * log(n) / (e**2)
```

For n=12: d(12) = 6 (divisors: 1,2,3,4,6,12), so κ(12) = 6 × ln(12) / 7.389 ≈ 2.02

## References
- Full documentation: `README.md`
- Detailed results: `EXPERIMENT_SUMMARY.md`
- All files: `MANIFEST.txt`
