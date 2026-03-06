# FINDINGS: Hypothesis Falsification Test

**Experiment ID:** experiment_20251226_063932  
**Date:** 2025-12-26 06:39:33.974094  
**Repository:** zfifteen/playground  

---

## CONCLUSION

**Verdict:** FALSIFIED (high confidence)

The experimental evidence **FALSIFIES** the hypothesis. The claimed patterns do not replicate under rigorous testing.

### Key Findings:

- **Lognormal Vs Exponential**: ✓ CONFIRMED
- **Fractal Cascade**: ✗ NOT CONFIRMED
- **Bottom Up Advantage**: ✗ NOT CONFIRMED
- **Reversed Hierarchy**: ✗ NOT CONFIRMED

**Statistical Summary:** 1/4 hypothesis components supported



## TECHNICAL EVIDENCE

### 1. Distribution Comparison: Lognormal vs Exponential

- **Win Rate:** 100.0%
- **Threshold:** 70.0%
- **Supported:** True

| Metric | Value |
|--------|-------|
| Lognormal wins | 6 |
| Exponential wins | 0 |
| Total trials | 6 |

### 2. Fractal Cascade Structure

- **Detection Rate:** 0.0%
- **Threshold:** 50.0%
- **Supported:** False

### 3. Bottom-Up vs Top-Down Analysis

- **Bottom-Up Win Rate:** 0.0%
- **Threshold:** 50.0%
- **Supported:** False

| Approach | Wins |
|----------|------|
| Bottom-Up | 0 |
| Top-Down | 6 |

### 4. Reversed Hierarchy Pattern Replication

- **Replication Rate:** 0.0%
- **Threshold:** 70.0%
- **Supported:** False



## METHODOLOGY

### Experimental Design

- **Number of Trials:** 3 per range
- **Prime Ranges:** 2 ranges tested
- **Random Seed:** 42 (for reproducibility)

### Hypothesis Components Tested

1. **Lognormal vs Exponential:** Prime gaps better modeled by lognormal than exponential distribution
2. **Fractal Cascade:** Self-similar structure with stable Hurst exponent H ∈ [0.7, 0.9]
3. **Bottom-Up Advantage:** Bottom-up analysis outperforms top-down assumptions
4. **Reversed Hierarchy:** Higher-order moments converge faster (from PR-0005)

### Statistical Methods

- **Distribution Fitting:** Maximum likelihood estimation
- **Goodness-of-Fit:** Kolmogorov-Smirnov test, Anderson-Darling test
- **Model Comparison:** AIC and BIC information criteria
- **Fractal Analysis:** Log-log regression for Hurst exponent
- **Moment Analysis:** Factorial-normalized convergence rates

### Falsification Criteria

Hypothesis **SUPPORTED** if:
- Lognormal wins ≥70% of trials (ΔBIC ≥ 10)
- Fractal cascade detected in ≥50% of trials
- Bottom-up wins ≥50% of comparisons
- Reversed hierarchy replicates in ≥70% of trials

Hypothesis **FALSIFIED** if ≥2 components fail to meet thresholds.



## RAW DATA

Complete experimental results are available in: `results/experiment_results.json`

## REFERENCES

Related experiments in this repository:
- `PR-0005_reversed_hierarchy_discovery` - Reversed hierarchy pattern
- `falsify/fractal-cascade-structure` - Fractal cascade testing  
- `falsify/lognormal-vs-exponential` - Distribution comparison
- `PR-0003_prime_log_gap_optimized` - Prime generation utilities

---

*This document was automatically generated from experimental data.*
