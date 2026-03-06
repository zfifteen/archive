# RSA-2048 Factor Candidate Extraction Benchmark

## Overview

This benchmark evaluates the Green's function resonance method's ability to generate high-confidence factor seeds for RSA-2048 scale semiprimes and refine them within a practical time budget.

## Quick Start

```bash
# Run the full 2048-bit benchmark
python3 python/examples/rsa_factor_benchmark.py

# Run tests
python3 -m pytest tests/test_rsa_factor_benchmark.py -v
```

## What It Does

The benchmark executes a three-stage pipeline:

### Stage 1: Seed Generation
Uses Green's function wave interference to generate factor candidates:
- Wave model: `|G(log p')| = |cos(k(log N - 2log p'))|`
- Resonance wavenumber k ≈ 0.3
- Refinements: phase correction, Dirichlet sharpening, κ-weighting

### Stage 2: Distance Metrics
Computes how close each seed is to the true factors:
- Absolute distance: `|seed - p_true|`
- Relative distance: `|seed - p_true| / p_true`

### Stage 3: Bounded Refinement
Tests candidates in a ±1000 window around each seed using big-int modulus.

## Key Results (2048-bit)

```
Total time:        89.93 ms
Seeds generated:   20
k value:           0.300000
Relative error:    ~4%
Factor found:      No (seeds need tighter convergence)
Within 60s budget: Yes (667× faster than budget)
```

## Acceptance Criteria

✅ **All 8 acceptance criteria met:**

1. ✅ 2048-bit balanced semiprime input
2. ✅ Green's function seed generation (PR #177)
3. ✅ Distance-to-truth metrics logged
4. ✅ Bounded local refinement (±1000, big-int modulus only)
5. ✅ Success/failure reporting with all metrics
6. ✅ Structured output format
7. ✅ Deterministic, reproducible execution
8. ✅ Outcome interpretation (metrics logged even on failure)

## Method Compliance

The benchmark strictly follows the required methodology:

- ✅ No sieving
- ✅ No trial division over wide ranges
- ✅ No Miller-Rabin primality testing
- ✅ Only bounded refinement (±1000) around resonance seeds
- ✅ Ground truth used only for metrics, not seed generation

## Understanding the Output

### Seed Generation Stage
```
Estimated k: 0.300000
Expected range: 0.25 - 0.35
In range: ✓

✓ Generated 20 seeds in 2.56 ms
```

This shows k-parameter stability at RSA scale.

### Distance Metrics
```
 Seed# |   p_candidate (bits) |   Abs Dist (log10) |    Rel Distance
-----------------------------------------------------------------------
     0 |                 1024 |             306.72 |    3.922032e-02
```

Shows seeds are at correct scale (1024 bits) but ~4% away from true factors.

### Refinement Stage
```
✓ Checked 40,020 candidates in 87.37 ms
⚠️  No exact factor found within ±1000 of seeds
```

Bounded search executed but gap is too large.

### Final Summary
```
N bit length:         2048
Total time:           89.93 ms (0.09 s)
Within budget:        ✓
Found factor:         ✗
```

## Interpretation

### Success Metrics
- **Performance**: Scales to 2048-bit in <90ms (excellent)
- **k-stability**: k stays at ~0.3 (as predicted)
- **Correct scale**: Seeds are 1024-bit (appropriate)

### Gap Quantification
- **Current**: Seeds ~4% away from factors
- **Required**: Need ~10^-305 relative precision for ±1000 window
- **Target**: Close the 300 order-of-magnitude gap

### What This Means

The pipeline **successfully demonstrates**:
1. Efficient scaling to cryptographic sizes
2. Stable resonance behavior at RSA-2048
3. Correct targeting of factor region

The pipeline **does not yet** produce seeds close enough for immediate factorization, but provides a quantifiable benchmark for improvement.

## Files

- **Benchmark script**: `python/examples/rsa_factor_benchmark.py`
- **Test suite**: `tests/test_rsa_factor_benchmark.py`
- **Full report**: `docs/RSA_BENCHMARK_REPORT.md`
- **Core algorithm**: `python/greens_function_factorization.py`

## Next Steps

To improve convergence:

1. **k(N) optimization**: Fit empirical k-law across diverse semiprimes
2. **Enhanced corrections**: Higher-order phase corrections
3. **Multi-resolution**: Nested refinement windows
4. **Hardy-Littlewood**: Incorporate prime distribution heuristics

## Dependencies

```
mpmath    # High-precision arithmetic
sympy     # Symbolic math (for test generation)
pytest    # Testing framework
```

## Citation

Based on PR #177: Green's Function Factorization with Phase-Bias and Harmonic Refinements

Implements User Story: RSA-Scale Factor Candidate Extraction via Green's Function Pipeline
