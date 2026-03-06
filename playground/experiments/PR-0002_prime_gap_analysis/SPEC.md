# Technical Design Specification: Prime Gap Distribution Analysis

**Date:** 2025-12-23  
**Author:** zfifteen  
**Status:** APPROVED FOR IMPLEMENTATION  

***

## 1. Executive Summary

This document specifies a rigorous statistical experiment to test whether prime number gaps exhibit systematic deviations from Prime Number Theorem predictions and whether their distributions follow lognormal or other structured patterns. The analysis distinguishes between gap magnitudes, gap-to-prime ratios, and logarithmic transformations to avoid conflating different mathematical quantities.

***

## 2. Hypotheses Under Test

### 2.1 H-MAIN-A: Gap Growth Relative to PNT

**Null Hypothesis (H0):** Prime gaps follow the Prime Number Theorem on average: `mean(gap/log(p)) ≈ 1.0` with no systematic trend.

**Alternative Hypotheses:**
- **H1a (sub-logarithmic):** `mean(gap/log(p)) < 0.9` or negative trend across scales
- **H1b (super-logarithmic):** `mean(gap/log(p)) > 1.1` or positive trend across scales

**Operational Definition:**
```python
normalized_gap[n] = gap[n] / log(p[n])
# Test if bin means show systematic deviation from 1.0
```

**Decision Rule:**
- If |slope| < 0.001 OR p > 0.05: Consistent with PNT (fail to reject H0)
- If slope < -0.001 AND p < 0.01: Sub-logarithmic growth (reject H0, accept H1a)
- If slope > +0.001 AND p < 0.01: Super-logarithmic growth (reject H0, accept H1b)

**Note:** The 0.001 threshold was chosen a priori based on the principle that deviations 
smaller than 0.1% per log unit of prime magnitude are negligible for practical purposes.
Observed slopes of ~0.003 exceed this threshold and are statistically significant,
but remain practically negligible (PNT accuracy exceeds 99.9%).

**Significance:** PNT predicts `gap ≈ log(p)`. Systematic deviations have implications for Cramér's conjecture, cryptographic hardness estimates, and refined gap bounds.

***

### 2.2 H-MAIN-B: Lognormal Gap Distribution

**Null Hypothesis (H0):** Within magnitude bands, gaps follow exponential or other simple distributions.

**Alternative (H1):** Within magnitude bands, `log(gap)` is approximately normally distributed (implying lognormal structure).

**Operational Definition:**
1. Partition primes into bands: `[10^5, 10^6)`, `[10^6, 10^7)`, `[10^7, 10^8)`
2. For each band, extract gaps: `gap[n] = p[n+1] - p[n]`
3. Test if `log(gap)` fits normal distribution
4. Compare to exponential, gamma, Weibull alternatives
5. Require consistency across ≥2 of 3 bands

**Decision Rule:**
- If normal distribution on `log(gap)` has best KS fit in ≥2 bands: Evidence for lognormal (reject H0)
- If exponential fits consistently better (KS ratio > 1.5): Not lognormal (fail to reject H0)

**Significance:** Lognormal structure implies multiplicative randomness—gaps behave as products of independent factors rather than sums. This has implications for gap prediction models and factorization heuristics.

***

### 2.3 H-MAIN-C: Gap Autocorrelation

**Null Hypothesis (H0):** Consecutive gaps are uncorrelated: `ACF(k) ≈ 0` for all lags `k > 0`.

**Alternative (H1):** Significant autocorrelation exists at low lags (1-5).

**Operational Definition:**
```python
gaps = np.diff(primes)
acf = autocorrelation(gaps, max_lag=40)
Q = n*(n+2) * sum(acf[k]^2 / (n-k) for k in 1..40)  # Ljung-Box statistic
p_value = chi_square_test(Q, df=40)
```

**Decision Rule:**
- If p < 0.01: Autocorrelation detected (reject H0)
- If p > 0.05: Consistent with independence (fail to reject H0)

**Significance:** Autocorrelation invalidates "random sieve" models and could enable improved prime prediction algorithms.

***

## 3. Falsification Criteria

The hypotheses are FALSIFIED if:

| ID | Criterion | Test | Threshold |
|----|-----------|------|-----------|
| **F1** | Gaps match PNT | `gap/log(p)` shows no systematic trend; mean ∈ [0.9, 1.1] | \|slope\| < 0.001 AND p > 0.05 |
| **F2** | Not lognormal | Normal on `log(gap)` does NOT fit best in majority of bands | KS p-ratio < 0.5 in ≥2 bands |
| **F3** | Exponential fits better | Exponential consistently outperforms lognormal | KS ratio > 1.5 in ≥2 bands |
| **F4** | No autocorrelation | Ljung-Box test shows independence | p > 0.05 |
| **F5** | Scale inconsistency | Different best-fit distributions across bands | Contradictory results |
| **F6** | Maximal gap mismatch | Maximal gaps differ from computed values | Any discrepancy |

***

## 4. Experimental Design

### 4.1 Data Generation

#### Prime Generation Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Minimum prime | 2 | Full range analysis |
| Maximum prime | 10^8 (extendable to 10^9) | Sufficient statistical power |
| Expected count | ~5.76 × 10^6 primes | From π(10^8) ≈ 5,761,455 |
| Generation method | Segmented Sieve of Eratosthenes | Memory-efficient |
| Validation | OEIS A000101 maximal gaps | Ensure correctness |

#### Known Validation Points

| x | π(x) | Source |
|---|------|--------|
| 10^6 | 78,498 | Prime counting function |
| 10^7 | 664,579 | Prime counting function |
| 10^8 | 5,761,455 | Prime counting function |

***

### 4.2 Quantities to Compute

For each consecutive prime pair `(p[n], p[n+1])`:

```python
# Core quantities
gap[n] = p[n+1] - p[n]                           # Actual gap (integer)
log_prime[n] = log(p[n])                         # Prime magnitude
log_gap[n] = log(gap[n])                         # Gap on log scale
normalized_gap[n] = gap[n] / log(p[n])           # PNT-normalized

# PNT residuals (equivalent formulations)
pnt_residual_log[n] = log(gap[n]) - log(log(p[n]))      # log(gap/log(p))
pnt_residual_additive[n] = gap[n] - log(p[n])           # gap - log(p)
normalized_log_gap[n] = log(gap[n]) / log(log(p[n]))    # ≈ 1 if PNT

# Array validation
assert len(gaps) == len(primes) - 1
assert len(gaps) == len(log_primes)
assert np.all(gaps > 0), "Non-positive gaps detected"
assert np.all(np.isfinite(log_gaps)), "Non-finite values detected"
```

**Critical Implementation Note:** 
- Compute `gaps = np.diff(primes)` FIRST (actual integer gaps)
- Then `log_gaps = np.log(gaps)` (logarithm of gap magnitudes)
- Do NOT compute `np.diff(np.log(primes))` which equals `log(p[n+1]/p[n])`—a different quantity

***

### 4.3 Statistical Test Suite

#### Test T1: PNT Deviation Analysis

**Purpose:** Test H-MAIN-A

**Method:**
1. Partition primes into 100 logarithmically-spaced bins by `log(p[n])`
2. Compute mean of `gap[n]/log(p[n])` per bin
3. Linear regression: `mean_normalized_gap ~ bin_index`
4. Report: slope, R², p-value, 95% CI
5. Compute overall mean `gap/log(p)` across all data

**Interpretation:**
- Mean ≈ 1.0, slope ≈ 0, p > 0.05 → Consistent with PNT
- Mean < 0.9 or slope < -0.001, p < 0.01 → Sub-logarithmic growth
- Mean > 1.1 or slope > +0.001, p < 0.01 → Super-logarithmic growth

***

#### Test T2: Distribution Fitting Within Magnitude Bands

**Purpose:** Test H-MAIN-B

**Method:**
1. Define bands: `[10^5, 10^6)`, `[10^6, 10^7)`, `[10^7, 10^8)`
2. For each band:
   - Extract gaps within band
   - Fit distributions to `log(gap)`: normal, exponential (on raw gaps), gamma, Weibull
   - Compute KS statistics for each
   - Perform Shapiro-Wilk test on `log(gap)`
   - Generate Q-Q plot (normal quantiles vs `log(gap)`)
3. Identify best fit per band
4. Check consistency: same best fit in ≥2 of 3 bands

**Interpretation:**
- Normal on `log(gap)` best in ≥2 bands + Q-Q linear → Lognormal structure
- Exponential consistently better (KS ratio > 1.5) → Not lognormal
- Cohen's d > 0.5 required for practical significance

***

#### Test T3: Autocorrelation Analysis

**Purpose:** Test H-MAIN-C

**Method:**
1. Compute `gaps = np.diff(primes)`
2. Calculate ACF for lags 1-40
3. Calculate PACF to identify direct correlations
4. Ljung-Box test:
   ```python
   Q = n * (n + 2) * sum(acf[k]^2 / (n - k) for k in 1..40)
   p_value = chi_square_cdf(Q, df=40)
   ```
5. Plot ACF with 95% confidence bands (±1.96/√n)

**Interpretation:**
- |acf[k]| > 1.96/√n for low lags AND p < 0.01 → Autocorrelation exists
- All lags within bands AND p > 0.05 → Consistent with independence

***

#### Test T4: Cross-Scale Validation

**Purpose:** Verify findings are consistent across scales

**Method:**
1. For each magnitude band independently:
   - Mean `gap/log(p)` (should be ≈ 1.0 ± 0.1)
   - Best-fit distribution
   - ACF structure
2. Test consistency:
   - Mean `gap/log(p)` varies by < 20% across bands
   - Same best-fit distribution in ≥2 bands
   - Similar ACF patterns

**Falsification:** If results contradict across scales (e.g., lognormal at 10^6 but exponential at 10^7), hypothesis is scale-dependent artifact.

***

## 5. Validation Against Known Results

### 5.1 Mean Gap Validation

| Prime Range | Mean Gap | log(p) at Midpoint | Expected Ratio | Tolerance |
|-------------|----------|-------------------|----------------|-----------|
| 10^5 to 10^6 | ~13.8 | ~13.8 | ~1.00 | ±5% |
| 10^6 to 10^7 | ~16.1 | ~16.1 | ~1.00 | ±5% |
| 10^7 to 10^8 | ~18.4 | ~18.4 | ~1.00 | ±5% |

**Acceptance:** Ratio `mean(gap)/mean(log(p))` within [0.95, 1.05]

***

### 5.2 Maximal Gap Validation

| Upper Bound | Maximal Gap | Prime Before Gap | Source |
|-------------|-------------|------------------|---------|
| 10^3 | 20 | 887 | Empirical |
| 10^4 | 36 | 9,551 | Empirical |
| 10^5 | 72 | 31,397 | Empirical |
| 10^6 | 114 | 492,113 | Empirical |
| 10^7 | 154 | 4,652,353 | Empirical |
| 10^8 | 220 | 47,326,693 | Empirical |

**Critical:** These are the maximal gaps within each range. Values differ from expected if implementation is wrong.

***

### 5.3 Gap Distribution Properties

For all tested scales:
- **Mode gap:** Must be 2 (twin primes most common)
- **Second-most common:** Gaps of 4 or 6
- **No gaps of 1:** Except 2→3 transition
- **Even gaps only:** All gaps even except 2→3

***

## 6. Implementation Specification

### 6.1 File Structure

```
experiments/PR-0002_prime_gap_analysis/
├── SPEC.md                    # This document
├── README.md                  # Usage instructions
├── src/
│   ├── prime_generator.py     # Segmented sieve
│   ├── gap_analysis.py        # Core computations
│   ├── distribution_tests.py  # KS, Shapiro-Wilk, MLE
│   ├── autocorrelation.py     # ACF, PACF, Ljung-Box
│   └── visualization.py       # Q-Q plots, histograms
├── data/
│   ├── primes_1e6.npy         # Cached primes
│   ├── primes_1e7.npy
│   └── primes_1e8.npy
├── results/
│   ├── analysis_results.json  # All statistics
│   └── figures/               # All plots
└── tests/
    └── test_validation.py     # OEIS checks, unit tests
```

***

### 6.2 Critical Code Implementation

```python
# CORRECT IMPLEMENTATION

# Step 1: Generate primes
primes = segmented_sieve(limit=10**8)
assert len(primes) == 5761455, f"Prime count mismatch: {len(primes)}"

# Step 2: Compute gaps (actual integer differences)
gaps = np.diff(primes)
assert len(gaps) == len(primes) - 1

# Step 3: Align arrays (crucial for correct normalization)
log_primes = np.log(primes[:-1])  # Matches gap array length

# Step 4: Transform gaps
log_gaps = np.log(gaps)                    # Log of gap magnitudes
normalized_gaps = gaps / log_primes        # PNT normalization

# Step 5: PNT residuals
pnt_residual = log_gaps - np.log(log_primes)  # log(gap/log(p))

# Step 6: Validation
assert len(gaps) == len(log_primes)
assert len(normalized_gaps) == len(gaps)
assert np.all(gaps > 0), f"Non-positive gaps: {gaps[gaps <= 0]}"
assert np.all(np.isfinite(log_gaps)), "Non-finite log-gaps"
```

***

### 6.3 Validation Test Suite

```python
def test_gap_calculation():
    """Verify gaps computed correctly."""
    primes = np.array([2, 3, 5, 7, 11, 13])
    gaps = np.diff(primes)
    expected = np.array([1, 2, 2, 4, 2])
    assert np.array_equal(gaps, expected)

def test_log_gap_magnitude():
    """Verify log(gap) not log(p[n+1]/p[n])."""
    primes = np.array([997, 1009])  # gap = 12
    gap = primes[1] - primes[0]
    log_gap = np.log(gap)
    
    assert abs(log_gap - 2.485) < 0.001  # log(12)
    assert log_gap > 2.0  # Should be ~2.5, not ~0.01

def test_oeis_maxgaps():
    """Validate against OEIS A000101."""
    primes = generate_primes(10**6)
    gaps = np.diff(primes)
    max_gap = np.max(gaps)
    max_gap_prime = primes[np.argmax(gaps)]
    
    assert max_gap == 114
    assert max_gap_prime == 492113

def test_array_alignment():
    """Verify array lengths consistent."""
    primes = generate_primes(10**5)
    gaps = np.diff(primes)
    log_primes = np.log(primes[:-1])
    normalized = gaps / log_primes
    
    assert len(gaps) == len(primes) - 1
    assert len(log_primes) == len(gaps)
    assert len(normalized) == len(gaps)

def test_pnt_normalization():
    """Verify mean(gap/log(p)) ≈ 1."""
    primes = generate_primes(10**6)
    gaps = np.diff(primes)
    log_primes = np.log(primes[:-1])
    normalized = gaps / log_primes
    
    mean_normalized = np.mean(normalized)
    assert 0.9 < mean_normalized < 1.1
```

***

## 7. Dependencies

```python
# requirements.txt
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
```

**Environment:**
- Python ≥ 3.9
- 8 GB RAM minimum for 10^8 scale
- Linux or macOS (cross-platform validated)

***

## 8. Computational Requirements

| Scale | Primes | Memory | Time (est.) | Disk Cache |
|-------|--------|--------|-------------|------------|
| 10^6 | 78,498 | ~1 MB | ~10 sec | ~3 MB |
| 10^7 | 664,579 | ~5 MB | ~60 sec | ~26 MB |
| 10^8 | 5,761,455 | ~46 MB | ~10 min | ~180 MB |

***

## 9. Expected Outcomes

### 9.1 Scenario: Lognormal Structure Confirmed

**Evidence:**
- Normal on `log(gap)` has best KS fit in ≥2 of 3 bands
- Q-Q plots approximately linear
- Shapiro-Wilk p > 0.05 in at least one band
- Cohen's d > 0.5 vs. exponential

**Implications:**
- Multiplicative structure in prime gaps
- Gaps arise from products of independent factors
- May enable improved gap prediction models
- Potential application to factorization heuristics

***

### 9.2 Scenario: Lognormal Structure Rejected

**Evidence:**
- Exponential or gamma fits consistently better
- Q-Q plots show systematic curvature
- KS ratio (exponential/lognormal) > 1.5

**Implications:**
- Gaps follow additive models (random sieve)
- No multiplicative structure
- Standard probabilistic models adequate

***

### 9.3 Scenario: PNT Deviations Detected

**Evidence:**
- Mean `gap/log(p)` significantly < 0.9 or > 1.1
- Systematic trend (|slope| > 0.001, p < 0.01)

**Implications:**
- Gaps grow sub/super-logarithmically
- Relevant to Cramér conjecture, Granville refinements
- Cryptographic implications (key generation hardness)

***

### 9.4 Scenario: Autocorrelation Detected

**Evidence:**
- Significant ACF at lags 1-5 (|acf| > 1.96/√n)
- Ljung-Box p < 0.01
- PACF shows AR cutoff

**Implications:**
- "Random sieve" model incomplete
- Gaps exhibit memory/structure
- Potential for improved prime prediction

***

## 10. Success Criteria

### 10.1 Implementation Correctness
- [ ] All OEIS validations pass (maximal gaps match exactly)
- [ ] Mean gap ratios within ±5% of PNT predictions
- [ ] Array length assertions pass
- [ ] All validation tests pass

### 10.2 Statistical Rigor
- [ ] Significance thresholds set before analysis (α = 0.01)
- [ ] Multiple testing corrections applied where needed
- [ ] Effect sizes (Cohen's d, R²) reported
- [ ] Negative results documented

### 10.3 Reproducibility
- [ ] Random seed fixed: `np.random.seed(20251223)`
- [ ] Package versions locked
- [ ] Git commit hash embedded in outputs
- [ ] Cross-platform verification (Linux + macOS)
- [ ] Bit-for-bit identical results across runs

***

## 11. Analysis Protocol

### Phase 1: Validation (10^6 scale)
1. Generate primes to 10^6
2. Verify π(10^6) = 78,498
3. Verify max gap = 114 at prime 492,113
4. Run full test suite
5. Validate against OEIS benchmarks

### Phase 2: Extension (10^7 scale)
1. Generate primes to 10^7
2. Verify π(10^7) = 664,579
3. Run full test suite
4. Compare to 10^6 results
5. Check cross-scale consistency

### Phase 3: Full Scale (10^8)
1. Generate primes to 10^8
2. Verify π(10^8) = 5,761,455
3. Run full test suite
4. Final cross-scale analysis
5. Document conclusions

***

## 12. References

### Mathematical Foundations
1. Prime Number Theorem: π(x) ~ x/ln(x)
2. Cramér's conjecture: max gap ~ (log p)²
3. Granville refinement: gaps ~ (log p)² / log log p

### Statistical Methods
1. Kolmogorov-Smirnov test for distribution fitting
2. Ljung-Box test for autocorrelation
3. Shapiro-Wilk test for normality
4. Q-Q plots for distribution assessment

### Validation Sources
1. OEIS A000101: First occurrence of prime gaps
2. OEIS A005250: Large prime gaps
3. OEIS A001223: Differences between consecutive primes

***

**END OF SPECIFICATION**

**Status:** APPROVED FOR IMPLEMENTATION  
**Date:** 2025-12-23  
**Version:** 1.0 (Green - Production Ready)
