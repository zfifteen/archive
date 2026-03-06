# Z5D-Biased Generation of Crypto-Friendly Primes - Test Plan Implementation

This directory contains the complete implementation of the Z5D-biased crypto-friendly prime generation test plan as specified in Issue #677.

## Overview

The test plan validates six hypotheses about Z5D-biased prime generation:

- **H1**: Z5D Accuracy - Median relative error ≤ 0.01%, 99th-pct ≤ 0.03%
- **H2**: Form Hit-Rate Uplift - ≥20% improvement or ≥1.2× ratio for special-form primes
- **H3**: Sqrt-Friendly Fraction QC - Unbiased ≈50% distribution of p ≡ 3 (mod 4)
- **H4**: Montgomery Multiplication Speed - ≥10% speedup for special-form primes
- **H5**: Density Enhancement - Same as H2 (density enhancement metric)
- **H6**: Zeta Consistency - Pearson r ≥ 0.90 (optional)

## Implementation Structure

### Core API
- `src/discrete/crypto_prime_generator.py` - Main API for crypto-friendly prime generation
- `src/discrete/__init__.py` - Module initialization

### Test Automation Scripts
- `scripts/invert_pnt.py` - PNT inversion for bit-length to k mapping
- `scripts/test_z5d_accuracy.py` - H1: Z5D accuracy validation
- `scripts/bench_form_hitrate.py` - H2: Special-form hit-rate testing
- `scripts/bench_modmul_speed.py` - H4: Montgomery multiplication benchmarking
- `scripts/qc_sqrt_mod4.py` - H3: Sqrt-friendly fraction QC
- `scripts/summary_gate_report.py` - Final gate assessment and reporting

### Demo and Documentation
- `demo_crypto_prime_test_pipeline.py` - Complete pipeline demonstration
- `README_CRYPTO_PRIME_TEST.md` - This documentation

## Quick Start

### 1. Run Complete Demo Pipeline

```bash
# Quick demo with small parameters (fast, ~2 minutes)
python demo_crypto_prime_test_pipeline.py --clean --quick

# Full demo with realistic parameters (slower, ~15 minutes)
python demo_crypto_prime_test_pipeline.py --clean --full
```

### 2. Run Individual Test Components

```bash
# PNT inversion for crypto bit lengths
python -m scripts.invert_pnt --m-list 128,192,224,255,256,384,521

# Z5D accuracy testing
python -m scripts.test_z5d_accuracy --k-min 1e5 --k-max 1e7 --grid log --points 200

# Form hit-rate benchmarking
python -m scripts.bench_form_hitrate --m 256 --predicate pseudo_mersenne --W 262144 --budget 200000

# Montgomery multiplication speed benchmarking
python -m scripts.bench_modmul_speed --m 256 --predicate pseudo_mersenne --trials 5 --ops 100000000

# Sqrt-friendly fraction QC
python -m scripts.qc_sqrt_mod4 --m 256 --generate-samples --sample-size 1000

# Generate final gate report
python -m scripts.summary_gate_report --metrics-dir metrics
```

## Output Structure

The test pipeline generates structured output in two directories:

### `results/` - Detailed CSV Data
- `z5d_accuracy_results.csv` - Z5D accuracy test results
- `form_hitrate_{m}_{predicate}.csv` - Hit-rate benchmarking data
- `modmul_{m}_{predicate}.csv` - Montgomery multiplication timing data
- `sqrt_frac_{m}.csv` - Sqrt-friendly fraction analysis

### `metrics/` - JSON Metrics and Gates
- `accuracy.json` - H1 accuracy metrics and pass/fail
- `form_hitrate_{m}_{predicate}.json` - H2 hit-rate metrics
- `modmul_{m}_{predicate}.json` - H4 speed metrics
- `sqrt_frac_{m}.json` - H3 QC metrics
- `gate_report.json` - Final gate assessment

### `REPORT.md` - Final Gate Report
Comprehensive Markdown report with:
- Overall PASS/FAIL assessment
- Hypothesis-by-hypothesis results
- Bootstrap confidence intervals
- Test file references
- Gate definitions

## API Usage

### Basic Prime Generation

```python
from src.discrete import generate_crypto_primes

# Generate crypto-friendly primes using Z5D-biased search
result = generate_crypto_primes(
    k_values=[1000000],  # Target k values
    kind="z5d_biased",   # Use Z5D centering
    window=2**18,        # Search window
    max_hits=50,         # Max primes to find
    prime_bits=256,      # Target bit length
    seed=42              # Reproducible results
)

print(f"Found {len(result.primes)} primes")
print(f"Special-form count: {result.special_form_count}")
print(f"Hit rate: {result.hit_rate:.4f}")
```

### Benchmarking Hit-Rates

```python
from src.discrete.crypto_prime_generator import benchmark_vs_baseline

# Compare Z5D-biased vs baseline across bit lengths
results = benchmark_vs_baseline(
    m_values=[128, 192, 256, 384, 521],
    window=2**18,
    budget=200000,
    special_form=SpecialFormType.PSEUDO_MERSENNE
)

for m, data in results.items():
    print(f"{m}-bit: {data['ratio']:.2f}× hit-rate improvement")
```

## Test Hypothesis Details

### H1: Z5D Accuracy
- **Claim**: For k ≥ 10^5, Z5D median relative error ≤ 0.01%; 99th-pct ≤ 0.03%
- **Test Method**: Sample k on log grid, compute |p̂_k - p_k|/p_k
- **Pass Gate**: median ≤ 1e-4 AND 99th-pct ≤ 3e-4

### H2: Form Hit-Rate Uplift  
- **Claim**: Z5D-biased neighborhoods yield higher hit-rate of special-form primes
- **Test Method**: Compare baseline vs Z5D-biased with equal primality test budgets
- **Pass Gate**: lower-CI(Δ) ≥ +20% OR ratio lower-CI ≥ 1.2×, p<0.01

### H3: Sqrt-Friendly Fraction QC
- **Claim**: Fraction of p ≡ 3 (mod 4) should be ≈50% (unbiased)
- **Test Method**: Analyze found primes for mod 4 residue distribution
- **Pass Gate**: |Z5D_frac - 0.5| ≤ 1% AND |Z5D_frac - Baseline_frac| ≤ 1.5%

### H4: Montgomery Multiplication Speed
- **Claim**: Special-form primes yield faster Montgomery reduction
- **Test Method**: Dynamic C compilation for Montgomery multiplication benchmarking (with Python fallback)
- **Pass Gate**: median speedup ≥ 10% AND 95% CI lower-bound ≥ 5%

### H5: Density Enhancement
- **Definition**: Same as H2 (uplift in SF hit-rate)
- **Pass Gate**: Same as H2

### H6: Zeta Consistency (Optional)
- **Claim**: Correlation with first 1M zeta zeros remains high
- **Pass Gate**: Pearson r ≥ 0.90, p < 1e-10

## Implementation Notes

### Special-Form Detection
- **Pseudo-Mersenne**: p = 2^m - c with small c (sweep c_max ∈ {19, 100, 1000, 5000})
- **Generalized**: p = 2^α(2^β - γ) - 1 with small γ (sweep γ_max ∈ {32, 256, 2000})

### Statistical Methods
- Bootstrap confidence intervals with 10k resamples
- Wilson confidence intervals for binomial proportions  
- Bias-corrected percentile method for bootstrap CIs

### Performance Benchmarking
- C implementation with GCC/Clang optimization (-O3 -march=native)
- Python fallback for development/testing
- taskset pinning and turbo-off for production benchmarks
- 64-bit Montgomery multiplication with portable big-int fallback

## Expected Results

With proper parameters (k ≥ 10^5, adequate window sizes, sufficient samples):

- **H1**: Should PASS for k ≥ 10^5 (Z5D predictor is highly accurate)
- **H2**: May PASS or FAIL depending on special-form density in Z5D neighborhoods
- **H3**: Should PASS (Z5D bias doesn't affect mod 4 distribution)
- **H4**: May PASS for true special-form primes (Montgomery reduction benefits)
- **H5**: Same as H2
- **H6**: Should PASS if zeta zeros dataset is available

## Troubleshooting

### Common Issues

1. **No special-form primes found**: Increase window size or lower c_max/γ_max thresholds
2. **Statistical test failures**: Increase sample sizes for more statistical power
3. **Montgomery benchmark errors**: Script dynamically compiles C code; ensure GCC/Clang is available, or use Python fallback
4. **Primality test timeouts**: For k > 10^6, true prime computation becomes infeasible

### Performance Tips

1. Use dynamically compiled C Montgomery benchmarks for accurate timing (falls back to Python if compiler unavailable)
2. Run benchmarks with turbo disabled and taskset pinning
3. Use bootstrap_samples=10000 for production confidence intervals
4. Test with multiple random seeds to verify reproducibility

## References

- Issue #677: Z5D-Biased Generation of Crypto-Friendly Primes Test Plan
- Z5D Predictor: Enhanced PNT with zeta-derived corrections
- Montgomery Multiplication: Fast modular arithmetic for cryptography
- Wilson Confidence Intervals: Exact binomial proportion CIs

## Primality Testing

The implementation uses deterministic Miller-Rabin tests for small primes (≤2^64) and probabilistic Miller-Rabin with Baillie-PSW for larger candidates. **Note**: The current implementation does not include ECPP (Elliptic Curve Primality Proving) - primality claims are scoped to the deterministic/probabilistic methods implemented.

---

*This implementation provides a comprehensive test framework for validating Z5D-biased crypto-friendly prime generation claims with rigorous statistical methods and performance benchmarking.*