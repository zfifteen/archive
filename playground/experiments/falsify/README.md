# Falsification Tests for Prime Gap Claims

This directory contains systematic falsification experiments designed to test the claims made about prime gap distributions and prediction models. Each subdirectory contains a complete technical specification, implementation, and results for a specific falsification test.

## Overview

The claims being tested originate from empirical observations about prime gaps that suggest:

1. Prime log-gaps follow **lognormal distributions** rather than exponential distributions
2. This lognormal behavior exhibits **fractal-like self-similarity** across magnitude strata
3. Prime gaps show strong **autocorrelation**, contradicting independence assumptions
4. Prediction model residuals exhibit **golden-ratio harmonic structure** in their frequency spectra
5. A "Z-normalization" framework reveals **scale-invariant patterns** in both gaps and residuals

Our approach is to design rigorous, pre-registered experiments that can **falsify** these claims under stronger controls than the original exploratory analyses.

---

## Planned Falsification Tests

### 1. Lognormal vs Exponential Distribution

**Directory:** `lognormal-vs-exponential/`

**Claim being tested:** Prime gaps in log-space are better modeled by lognormal distributions than by exponential distributions.

**Approach:**
- Extract consecutive prime gaps over multiple disjoint ranges (10⁸ to 10¹¹)
- Band primes by scale and collect associated gaps
- Fit both lognormal and exponential models on training data (70%)
- Evaluate on held-out test data (30%) using:
  - Log-likelihood and likelihood-ratio tests
  - Information criteria (AIC, BIC)
  - Goodness-of-fit tests (Kolmogorov-Smirnov, Anderson-Darling)
- Apply multiple-testing corrections (Benjamini-Hochberg FDR)

**Falsification criteria:**
- Lognormal fails if it doesn't beat exponential by ΔBIC ≥ 10 in ≥50% of bands across two independent ranges
- Lognormal fails if exponential systematically has lower BIC in ≥2/3 of bands in any range
- Lognormal fails if advantage disappears under robustness checks (alternative bandings, gap filters, different seeds)

**Status:** Implementation complete

---

### 2. Fractal Cascade Structure

**Directory:** `fractal-cascade-structure/`

**Claim being tested:** Log-gaps exhibit recursive log-normal structure within magnitude strata, suggesting multiplicative cascade dynamics.

**Approach:**
- Stratify gaps into quintiles/deciles by magnitude
- Fit log-normal distribution to each stratum independently
- Test if variance scaling follows power law: σₖ ∼ μₖᴴ with stable Hurst exponent H ≈ 0.8
- Compare observed stratified KS statistics against:
  - Additive noise models (Cramér-like)
  - Simple sieve-based simulations
  - Pure multiplicative cascade models
- Estimate multifractal spectrum and check for consistency across ranges

**Falsification criteria:**
- Cascade claim fails if Hurst exponent H varies by >0.2 across ranges
- Cascade claim fails if simple additive models can reproduce stratified log-normality with similar KS fits
- Cascade claim fails if variance scaling doesn't follow predicted power law in ≥50% of range pairs

**Status:** Implementation complete

---
### 3. Autocorrelation and Independence Tests

**Directory:** `autocorrelation-tests/` (planned)

**Claim being tested:** Prime log-gaps exhibit strong autocorrelation (ACF(1) ≈ 0.8), contradicting classical independence models like Cramér's conjecture.

**Approach:**
- Compute sample autocorrelation function (ACF) of log-gaps over large windows
- Use rigorous significance thresholds accounting for heavy tails and long-range dependence
- Generate surrogate data from:
  - Cramér-like models with matched marginal distributions
  - Sieve-based simulations calibrated to observed densities
  - ARMA and GARCH models with tunable correlation
- Use block bootstrap and permutation tests to assess whether observed ACF can arise from null models

**Falsification criteria:**
- Autocorrelation claim fails if multiple well-calibrated null models (sieve + Cramér variants) produce similar ACF(1) values
- Autocorrelation claim fails if ACF(1) varies by >0.3 across disjoint prime ranges of similar size
- Autocorrelation claim fails if permutation tests show observed ACF is not statistically significant after correction

**Status:** Spec in development

---

### 4. Z-Normalization Artifact Testing

**Directory:** `z-normalization-artifacts/` (planned)

**Claim being tested:** The "Z-normalization" framework (scaling by local/global variance ratios) reveals genuine prime-specific structure rather than manufacturing artifacts.

**Approach:**
- Apply the exact Z-transformation used in original claims to:
  - Synthetic data from known processes (log-normal cascades, ARMA, GARCH, pure noise)
  - Randomized/permuted versions of real prime gaps
  - Data from other number-theoretic sequences (composites, semiprimes, etc.)
- Test whether "self-similarity" and "scale invariance" patterns appear in control datasets
- Measure false-positive rate: how often does Z-normalization produce impressive-looking patterns in null data?

**Falsification criteria:**
- Z-normalization claim fails if ≥40% of synthetic datasets show similar "self-similar" signatures
- Z-normalization claim fails if permuted prime gaps produce indistinguishable Z-normalized distributions (KS test p > 0.1)
- Z-normalization claim fails if other number sequences (composites, semiprimes) show equivalent structure

**Status:** Spec in development

---

### 5. Golden-Ratio Spectral Peaks

**Directory:** `phi-harmonic-spectrum/` (planned)

**Claim being tested:** Prediction model residuals, after Z-normalization, exhibit spectral peaks at golden-ratio harmonic frequencies 2πk/φ with ~97% alignment.

**Approach:**
- Reimplement the Z5D predictor independently and verify residual generation
- Compute FFT of residuals across multiple disjoint prime ranges
- Apply the claimed Z-normalization (by maximum spectral power)
- Test peak alignment against φ-harmonic grid with preregistered tolerance (0.5%)
- Control for "look-elsewhere effect":
  - Generate surrogate residual series with matched variance and autocorrelation
  - Measure how often ≥97% of peaks fall within 0.5% of *any* irrational constant
- Test different window sizes, tapers, and zero-padding choices for robustness

**Falsification criteria:**
- φ-harmonic claim fails if surrogate data shows ≥97% alignment for ≥20% of tested irrational constants
- φ-harmonic claim fails if peak alignment drops below 90% in two independent prime ranges
- φ-harmonic claim fails if alignment disappears when using different FFT parameters (window, taper)

**Status:** Spec in development

---

### 6. Hybrid Dynamics Model Comparison

**Directory:** `hybrid-model-tests/` (planned)

**Claim being tested:** Primes require a "hybrid" model (deterministic φ-resonance × multiplicative cascade noise) rather than simpler alternatives.

**Approach:**
- Construct minimal null models:
  - Pure multiplicative cascade (no φ component)
  - Pure quasiperiodic φ-driven signal + additive noise
  - Simple random models (Poisson, Cramér) with parameter tuning
- For each model, generate synthetic "primes" and measure which features match real data:
  - KS statistics in magnitude strata
  - Hurst exponent estimates
  - ACF values
  - Spectral peak distributions
- Use model selection criteria (AIC, BIC) to compare hybrid vs simpler models

**Falsification criteria:**
- Hybrid claim fails if a simpler single-mechanism model (cascade-only or φ-only) reproduces ≥80% of observed signatures
- Hybrid claim fails if random models with <3 tunable parameters can match most features
- Hybrid claim fails if hybrid model doesn't outperform alternatives by ΔBIC ≥ 10 on held-out data

**Status:** Spec in development

---

## General Methodology Principles

All falsification tests follow these principles:

1. **Pre-registration**: Success and failure criteria are defined *before* running experiments
2. **Train/test splits**: All model fitting on training data, all evaluation on held-out test data
3. **Multiple-testing corrections**: Bonferroni or Benjamini-Hochberg FDR applied across bands/ranges
4. **Replication**: Tests must succeed across multiple independent prime ranges
5. **Robustness checks**: Alternative parameterizations, bandwidths, and preprocessing must not break results
6. **Control comparisons**: Synthetic data, permuted data, and alternative sequences tested under identical protocols
7. **Reproducibility**: All code, random seeds, and data sources documented; results machine-readable

---

## Running the Tests

Each subdirectory contains:

- `TECH-SPEC.md`: Complete technical specification
- `run_experiment.py`: Main experiment script
- `requirements.txt`: Python dependencies
- `results/`: Output directory for data and plots
- `README.md`: Experiment-specific documentation

To run a specific test:

```bash
cd <test-directory>
pip install -r requirements.txt
python run_experiment.py --seed 42 --ranges "1e8:1e9,1e9:1e10" --output results/
```

---

## Status Summary

| Test | Status | Tech Spec | Implementation | Results |
|------|--------|-----------|----------------|----------|
| Lognormal vs Exponential | Active | ✓ Complete | ✓ Complete | Pending |
| Fractal Cascade | Active | ✓ Complete | ✓ Complete | Pending |
| Autocorrelation Tests | Planned | In development | Not started | Pending |
| Z-Normalization Artifacts | Planned | In development | Not started | Pending |
| Golden-Ratio Spectrum | Planned | In development | Not started | Pending |
| Hybrid Model Comparison | Planned | In development | Not started | Pending |

---

## Contributing

To add a new falsification test:

1. Create a new subdirectory under `experiments/falsify/`
2. Write a complete `TECH-SPEC.md` following the template from `lognormal-vs-exponential/`
3. Implement the test following the general methodology principles above
4. Update this README with the new test description
5. Submit results and analysis when complete

---

## References

These tests are designed to falsify claims from:

- **Original discussion**: [prime-gap-lognormal Discussion #1](https://github.com/zfifteen/prime-gap-lognormal/discussions/1)
- **Theoretical background**: Cramér's conjecture, multiplicative cascade theory, quasiperiodic resonances
- **Statistical methodology**: Train/test splitting, information criteria, multiple testing corrections, permutation tests
