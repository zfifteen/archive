# Reproducibility Checklist

This document provides guidance for external reviewers who want to validate the conformal anisotropy framework and replicate the key findings.

## Prerequisites

### Software Requirements

- Python 3.8+
- gmpy2 (arbitrary precision arithmetic)
- NumPy, SciPy
- Matplotlib (for visualization)

### Hardware Requirements

- Consumer-grade machine (tested on 8+ GB RAM)
- Typical runtime: 1.5-2 seconds per 50k candidates

## Core Experiments

### 1. Z5D Enrichment Validation

**Script:** `experiments/joukowski/z5d_validation.py` (or equivalent)

**Expected outcomes:**
- Enrichment near q (larger factor): ~5-10x above baseline in top-10K slices
- Enrichment near p (smaller factor): ~1x (indistinguishable from random)
- Asymmetry ratio: Enrichment_q / Enrichment_p > 5 for unbalanced semiprimes

**Validation criteria:**
- [ ] Run on semiprimes with known factors (test set)
- [ ] Compare top-K Z5D scores to random baseline
- [ ] Verify asymmetry increases with q/p ratio

### 2. O(1) Scaling Test

**Script:** `experiments/scaling_test.py` (or equivalent)

**Expected outcomes:**
| Scale | Magnitude | Bits | Time (50k) | % Increase |
|-------|-----------|------|------------|------------|
| 10^5 | 87,713 | 17 | ~1.5s | 0% |
| 10^15 | 799.7T | 50 | ~1.8s | <20% |
| 10^18 | 562P | 60 | ~1.8s | <20% |

**Validation criteria:**
- [ ] Time increase <20% across 13+ orders of magnitude
- [ ] No numerical overflow or instability
- [ ] gmpy2 arbitrary precision functioning correctly

### 3. Statistical Significance Test

**Script:** `experiments/statistical_tests.py` (or equivalent)

**Expected outcomes:**
- KS test p-value: < 10^-6 (minimum threshold)
- Mann-Whitney U distance ratio: ~0.2-0.3
- Factor-proximate vs random distributions: clearly distinguishable

**Validation criteria:**
- [ ] p-value significantly below threshold
- [ ] Test with shuffled labels as control (should show p ~0.5)

## Key Parameters

### Z5D Amplitude Function

```
A(k) = |cos(ψ + ln(k) · φ)| / ln(k) + |cos(ln(k) · e)| / 2
```

**Standard parameters:**
- c = -0.00247 (phase offset)
- k* = 0.04449 (scaling constant)
- φ = (1 + √5) / 2 (golden ratio)
- e = 2.71828... (Euler's number)

### Search Window

For semiprime N:
- Window center: √N
- Window radius: 13% of √N (default)
- Sampling density: 10^5 - 10^6 candidates

## Known Limitations

1. **Coverage Paradox:** Blind sampling at 10^6 candidates provides ~10^-11% coverage of search space - insufficient for direct factor discovery on large semiprimes

2. **Balanced primes:** Enrichment asymmetry collapses to ~1x when q/p ≈ 1 (RSA-style balanced factors)

3. **Signal vs. discovery:** Framework detects factors with high confidence but does not provide polynomial-time factorization

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| No enrichment detected | Parameters incorrect | Verify ψ, k* values |
| Overflow errors | Integer too large | Ensure gmpy2 is installed |
| Slow performance | Float operations | Use gmpy2 mpfr for precision |
| Asymmetry too low | Balanced semiprime | Test with q/p > 2 |

## Contact

For questions about reproducibility, refer to:
- Issue #43: Proposed Algorithmic Pivot
- Issue #41: Improved Experiment Design
- White paper Section 11.5: Post-Validation Updates
