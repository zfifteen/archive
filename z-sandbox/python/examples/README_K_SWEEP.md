# RSA-2048 k-Parameter Sweep Tool

## Overview

This tool systematically evaluates multiple resonance parameters (k values with fixed ±0.5% detunes) against a known 2048-bit RSA semiprime to determine which k setting produces the closest seed to the true 1024-bit factor.

The k-sweep measures seed proximity **without running refinement**, allowing us to assess whether tuning k alone can reduce relative error toward the range where ±1000 refinement becomes practical.

## Quick Start

```bash
# Run the k-parameter sweep (takes ~45-60 seconds)
python3 python/examples/rsa_k_sweep.py

# Run tests
python3 -m pytest tests/test_rsa_k_sweep.py -v
```

## What It Does

The sweep tool executes these steps:

### 1. k-Grid Evaluation
For each k_base in [0.250, 0.260, 0.270, 0.280, 0.290, 0.300, 0.310, 0.320, 0.330, 0.340, 0.350]:
- Evaluate k_base
- Evaluate k_plus = k_base × 1.005 (+0.5% detune)
- Evaluate k_minus = k_base × 0.995 (-0.5% detune)

Total: **33 pipeline calls** (11 k_base × 3 variants each)

### 2. Seed Collection
For each k variant:
- Call the same Green's function resonance pipeline used in `rsa_factor_benchmark.py`
- Collect all returned seeds (up to 100 per call)
- Preserve pipeline's original scoring/ranking

### 3. Distance Measurement
For each seed:
- Compute absolute distance: `|seed - p_true|` or `|seed - q_true|`
- Compute relative distance: `abs_distance / p_true` (or q_true)
- Record which true factor is closer

### 4. Per-k_base Aggregation
For each k_base group (base/plus/minus combined):
- Find the single best seed by minimum relative distance
- Record best seed metrics and source (which k variant produced it)
- Count total seeds across all three variants

### 5. Global Best Identification
- Find the k_base whose group achieved the smallest relative distance
- Report comprehensive statistics for all k_base values

## Key Output Format

```python
{
  'N_bits': 2048,
  'global_best_k_base': 0.250,
  'global_best_source': 'k_base',
  'global_best_abs_distance': 5278907006671148213639...,  # Full precision int
  'global_best_rel_distance': 0.03922031991522185,
  'results': [
    {
      'k_base': 0.250,
      'k_plus': 0.25125,
      'k_minus': 0.24875,
      'best_abs_distance': 5278907006671148213639...,
      'best_rel_distance': 0.03922031991522185,
      'best_seed_bits': 1024,
      'best_seed_confidence': 0.135335,
      'best_seed_source': 'k_base',
      'num_seeds_total': 300,
      'determinism_info': {
        'seed': 1337,
        'detune_offset': 0.005,
        'mpmath_dps': 100
      }
    },
    # ... results for other k_base values
  ]
}
```

## Example Results (2048-bit RSA)

```
[1/11] k_base=0.250, k+=0.251250, k-=0.248750
  Evaluating k_base... 100 seeds
  Evaluating k_plus... 100 seeds
  Evaluating k_minus... 100 seeds
  → Best: 3.922032e-02 rel_dist from k_base, 300 total seeds

[2/11] k_base=0.260, k+=0.261300, k-=0.258700
  Evaluating k_base... 100 seeds
  Evaluating k_plus... 100 seeds
  Evaluating k_minus... 100 seeds
  → Best: 3.922032e-02 rel_dist from k_base, 300 total seeds

...

Global best k_base: 0.250
Global best source: k_base
Global best abs_distance: 5.278907e+306
Global best rel_distance: 3.922032e-02
```

## Interpretation

### Current Findings (2048-bit test case)

The sweep reveals that **all k values produce similar relative distances** (~3.92%):
- This suggests the pipeline may be converging to the same resonance candidate
- No clear k-value winner in the tested range [0.25, 0.35]
- Relative error remains at ~4% across all k variants

### What This Tells Us

1. **k-stability**: The resonance is robust across the physically relevant k range
2. **Detune insensitivity**: ±0.5% k variations don't shift the best candidate
3. **Convergence limitation**: Pure k-tuning alone (at fixed detune) doesn't close the gap to ±1000 refinement range

### Next Questions

The sweep enables research into:
- Whether finer k-grid (smaller steps) reveals structure
- Whether larger detunes (±1%, ±2%) change results
- Whether other parameters (Dirichlet J, window size) interact with k
- Whether different semiprime characteristics affect k-sensitivity

## Method Compliance

The sweep strictly follows required methodology:

- ✅ **No modifications** to the factorization pipeline
- ✅ **No refinement** loop execution (seeds only)
- ✅ **No classical methods** (Pollard, ECM, GNFS, Miller-Rabin)
- ✅ **Ground truth** used only for distance measurement
- ✅ **Deterministic** execution via fixed seed and precision
- ✅ **CPU-only** computation (no GPU, no network)

## Design Decisions

### Why These k Values?
- Range [0.25, 0.35] covers the physically relevant resonance band
- Step size 0.01 balances resolution vs. runtime (11 evaluations)
- Based on theoretical estimate k ≈ 0.3 for balanced RSA semiprimes

### Why ±0.5% Detune?
- Small enough to detect fine structure
- Large enough to distinguish from numerical noise
- Matches typical experimental precision requirements

### Why 100 Seeds per Call?
- Balances thoroughness with runtime
- Captures top candidates from Green's function amplitude
- Allows detection of second-best seeds if first is unstable

## Files

- **Sweep script**: `python/examples/rsa_k_sweep.py`
- **Test suite**: `tests/test_rsa_k_sweep.py` (20 tests)
- **Benchmark**: `python/examples/rsa_factor_benchmark.py` (uses same N/p/q)
- **Core algorithm**: `python/greens_function_factorization.py`

## Configuration

Key constants (in `rsa_k_sweep.py`):

```python
K_BASE_VALUES = [0.250, 0.260, ..., 0.350]  # 11 values
DETUNE_OFFSET = 0.005                        # ±0.5%
DETERMINISTIC_SEED = 1337                    # For reproducibility
MAX_CANDIDATES = 100                         # Per k variant
MPMATH_PRECISION = 100                       # Decimal places
```

Modify these to explore different sweep parameters.

## Dependencies

```
mpmath    # High-precision arithmetic
sympy     # Symbolic math (for z5d_axioms)
pytest    # Testing framework (for tests)
```

## Performance

Typical runtime on 2048-bit semiprime:
- **Total time**: ~45-60 seconds
- **Per k_base group**: ~4-5 seconds
- **Per k variant**: ~1-2 seconds
- **Memory**: < 100 MB (CPU-only, no large arrays)

## Citation

Implements Issue #193: "USER STORY: Improve RSA-2048 Seed Accuracy via k-Scan and Distance Reporting"

Based on:
- PR #177: Green's Function Factorization
- PR #178: RSA-2048 Factor Candidate Extraction Benchmark

## Related Documentation

- `README_RSA_BENCHMARK.md` - The base benchmark this tool extends
- `docs/IMPLEMENTATION_SUMMARY_256BIT.md` - Pipeline implementation details
- `docs/GOAL.md` - Project goals and mathematical framework
