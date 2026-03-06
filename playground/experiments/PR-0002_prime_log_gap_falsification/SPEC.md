# Technical Design Specification: Prime Log-Gap Falsification Experiment

**PR Number:** PR-0002  
**Date:** 2025-12-21  
**Author:** zfifteen  
**Status:** Draft  

---

## 1. Executive Summary

This document specifies an experiment designed to rigorously test and potentially falsify the hypothesis that prime number gaps in logarithmic space exhibit circuit-like damped impulse response behavior. The experiment extends preliminary findings (9,592 primes to 10âµ) to larger scales (10â¸+ primes) with formal statistical validation.

---

## 2. Hypothesis Under Test

### 2.1 Primary Hypothesis (H-MAIN)

**Statement:** Prime gaps in log-space, defined as Î”â‚™ = ln(pâ‚™â‚Šâ‚) - ln(pâ‚™) = ln(pâ‚™â‚Šâ‚/pâ‚™), exhibit statistical properties consistent with a multiplicative damped system, specifically:

1. **H-MAIN-A (Decay):** Mean log-gap decreases monotonically as primes increase
2. **H-MAIN-B (Distribution):** Log-gaps follow a log-normal or related heavy-tailed multiplicative distribution
3. **H-MAIN-C (Memory):** Log-gap autocorrelation exhibits short-range structure (non-zero at low lags)

### 2.2 Null Hypotheses (For Falsification)

| ID | Null Hypothesis | Falsification Condition |
|----|-----------------|------------------------|
| H0-A | Log-gap mean is constant or increasing | 50-bin means show no decrease or increase with p |
| H0-B | Log-gaps are normally distributed | KS test p-value > 0.05 for normal fit, AND normal KS < log-normal KS |
| H0-C | Log-gaps are uncorrelated (white noise) | Ljung-Box test p-value > 0.05 at all lags â‰¤ 20 |
| H0-D | Log-gaps follow simple exponential decay | Exponential KS statistic < log-normal KS statistic |

### 2.3 Connection to Circuit Analogy

The hypothesis derives from the mapping:

| Electrical Domain | Number-Theoretic Domain |
|-------------------|------------------------|
| Voltage v | Logarithm ln(n) |
| Current i | Log-ratio ln(pâ‚™â‚Šâ‚/pâ‚™) |
| Impulse response | Prime gap distribution |
| Damping coefficient | Log-gap decay rate |
| RC time constant | Characteristic scale of gap correlation |

### 2.4 Connection to Relativistic Bounds

The Gist "Proof and Analysis of Relativistic Doppler Shift Bounds" establishes:

$$\frac{\delta}{1+\delta} < \beta < \frac{\delta}{1-\delta} \quad (0 < \delta < 1)$$

via the rapidity identity artanh(Î²) = ln(1+Î´). This logarithmic compression parallels the treatment of integers as "potentials" in the circuit analogy, where logarithms bound multiplicative growth analogously to how Î² < 1 bounds relativistic velocity.

---

## 3. Experimental Design

### 3.1 Data Generation

#### 3.1.1 Prime Generation Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Minimum prime | 2 | Include full range |
| Maximum prime | 10â¸ (extendable to 10â¹) | Sufficient for statistical power |
| Expected count | ~5.76 Ã— 10â¶ primes | From Ï€(10â¸) â‰ˆ 5,761,455 |
| Generation method | Segmented Sieve of Eratosthenes | Memory-efficient for large ranges |
| Validation | Cross-check count against known Ï€(x) values | Ensure no computational errors |

#### 3.1.2 Known Validation Points

| x | Ï€(x) | Source |
|---|------|--------|
| 10â¶ | 78,498 | Prime counting function tables |
| 10â· | 664,579 | Prime counting function tables |
| 10â¸ | 5,761,455 | Prime counting function tables |

### 3.2 Derived Quantities

For each consecutive prime pair (pâ‚™, pâ‚™â‚Šâ‚):

```
log_gap[n] = ln(p[n+1]) - ln(p[n]) = ln(p[n+1] / p[n])
regular_gap[n] = p[n+1] - p[n]
log_prime[n] = ln(p[n])
```

### 3.3 Statistical Tests

#### 3.3.1 Test Suite

| Test ID | Test Name | Target Hypothesis | Implementation |
|---------|-----------|-------------------|----------------|
| T1 | 50-Bin Mean Regression | H-MAIN-A | Linear regression of 50-bin means vs bin index (primary, robust) |
| T2 | Decile Mean Regression | H-MAIN-A | Legacy 10-bin check for backward compatibility |
| T3 | KS Test Battery | H-MAIN-B | Fit and compare: normal, log-normal, exponential, gamma, Weibull |
| T4 | Maximum Likelihood Estimation | H-MAIN-B | MLE for log-normal parameters (Î¼, Ïƒ) |
| T5 | Ljung-Box Test | H-MAIN-C | Autocorrelation significance at lags 1-20 |
| T6 | ACF/PACF Analysis | H-MAIN-C | Partial autocorrelation to identify AR structure |
| T7 | Skewness/Kurtosis | H-MAIN-B | Compare to theoretical values for candidate distributions |
| T8 | Q-Q Plots | H-MAIN-B | Visual and quantitative assessment of distribution fit |

**Note:** The original implementation used quintiles (5 bins), but this was increased to 50 bins for more robust statistical proof. Quintile analysis is retained for backward compatibility.

#### 3.3.2 Significance Thresholds

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| p-value for rejection | < 0.01 | Conservative threshold to avoid false positives |
| KS statistic comparison | Ratio > 1.5 | One distribution fits substantially better |
| Regression RÂ² | > 0.90 | Strong linear relationship in decay |
| Slope significance | p < 0.001 | Decay slope is significantly negative |

### 3.4 Falsification Criteria

**The hypothesis is FALSIFIED if ANY of the following occur:**

1. **F1:** 50-bin means show non-decreasing trend (T1 regression slope â‰¥ 0 with p > 0.05)
2. **F2:** Normal distribution fits log-gaps better than log-normal (T3: KS_normal < KS_lognormal)
3. **F3:** Log-gaps are indistinguishable from uniform random (T3: uniform KS p-value > 0.05)
4. **F4:** Autocorrelation is flat at all lags (T5: Ljung-Box p > 0.05 for all lags)
5. **F5:** Skewness and kurtosis are consistent with normal distribution (T7: |skewness| < 0.5, |excess kurtosis| < 1)
6. **F6:** Results at 10â¸ contradict results at 10âµ (directional inconsistency)

**The hypothesis is SUPPORTED (not proven) if:**

1. All falsification criteria fail to trigger
2. Log-normal or heavy-tailed fit is statistically superior
3. Decay trend is monotonic and statistically significant
4. Results are consistent across scales (10âµ â†’ 10â¶ â†’ 10â· â†’ 10â¸)

---

## 4. Implementation Specification

### 4.1 File Structure

```
experiments/PR-0002_prime_log_gap_falsification/
â”œâ”€â”€ SPEC.md                    # This document
â”œâ”€â”€ FINDINGS.md                # Results and conclusions
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ prime_generator.py     # Segmented sieve implementation
â”‚   â”œâ”€â”€ log_gap_analysis.py    # Core statistical analysis
â”‚   â”œâ”€â”€ distribution_tests.py  # KS tests and MLE fitting
â”‚   â”œâ”€â”€ autocorrelation.py     # ACF/PACF and Ljung-Box
â”‚   â””â”€â”€ visualization.py       # Q-Q plots, histograms, trend plots
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ primes_1e6.npy         # Cached prime arrays
â”‚   â”œâ”€â”€ primes_1e7.npy
â”‚   â”œâ”€â”€ primes_1e8.npy
â”‚   â””â”€â”€ log_gaps_*.csv         # Computed log-gaps
â”œâ”€â”€ results/
â”‚   â”œâ”€â”€ quintile_analysis.csv
â”‚   â”œâ”€â”€ distribution_fits.csv
â”‚   â”œâ”€â”€ autocorrelation.csv
â”‚   â””â”€â”€ figures/
â”‚       â”œâ”€â”€ log_gap_histogram.png
â”‚       â”œâ”€â”€ qq_plot_lognormal.png
â”‚       â”œâ”€â”€ decay_trend.png
â”‚       â””â”€â”€ acf_pacf.png
â””â”€â”€ tests/
    â””â”€â”€ test_prime_generator.py # Validation against known Ï€(x)
```

### 4.2 Dependencies

```
numpy >= 1.21.0
scipy >= 1.7.0
statsmodels >= 0.13.0
matplotlib >= 3.5.0
pandas >= 1.3.0
sympy >= 1.9  # For symbolic verification
```

### 4.3 Computational Requirements

| Scale | Estimated Primes | Memory (primes) | Memory (gaps) | Time (est.) |
|-------|------------------|-----------------|---------------|-------------|
| 10â¶ | 78,498 | ~0.6 MB | ~0.6 MB | < 1 sec |
| 10â· | 664,579 | ~5 MB | ~5 MB | ~5 sec |
| 10â¸ | 5,761,455 | ~46 MB | ~46 MB | ~60 sec |
| 10â¹ | 50,847,534 | ~407 MB | ~407 MB | ~15 min |

### 4.4 Algorithm: Segmented Sieve

```python
def segmented_sieve(limit, segment_size=10**6):
    """
    Memory-efficient prime generation using segmented sieve.

    1. Generate small primes up to sqrt(limit) using basic sieve
    2. Process [sqrt(limit), limit] in segments of segment_size
    3. For each segment, mark composites using small primes
    4. Yield primes from each segment
    """
    pass  # Implementation in src/prime_generator.py
```

---

## 5. Analysis Protocol

### 5.1 Phase 1: Validation (Scale 10â¶)

1. Generate primes to 10â¶
2. Verify count matches Ï€(10â¶) = 78,498
3. Compute log-gaps
4. Run full test suite (T1-T8)
5. Compare to preliminary results (10âµ scale)
6. Document any discrepancies

### 5.2 Phase 2: Extension (Scale 10â·)

1. Generate primes to 10â·
2. Verify count matches Ï€(10â·) = 664,579
3. Compute log-gaps
4. Run full test suite
5. Compare decay rates across scales
6. Check for scale-dependent effects

### 5.3 Phase 3: Full Scale (10â¸)

1. Generate primes to 10â¸
2. Verify count matches Ï€(10â¸) = 5,761,455
3. Compute log-gaps
4. Run full test suite
5. Final statistical analysis
6. Aggregate cross-scale comparison

### 5.4 Phase 4: Robustness Checks

1. **Windowed analysis:** Analyze log-gaps in non-overlapping windows of 10âµ primes
2. **Bootstrap confidence intervals:** 1000 resamples for key statistics
3. **Sensitivity analysis:** Vary bin counts, significance thresholds
4. **Alternative metrics:** Test ln(1 + gap/p) as alternative to ln(p_{n+1}/p_n)

---

## 6. Expected Outcomes

### 6.1 If Hypothesis is Supported

| Finding | Implication |
|---------|-------------|
| Log-normal fit confirmed at scale | Multiplicative structure in prime gaps is real |
| Decay rate consistent across scales | "Damping coefficient" is a stable invariant |
| Short-range autocorrelation | "Filter memory" model is viable |
| Heavy tails persist | Rare large gaps follow predictable statistics |

### 6.2 If Hypothesis is Falsified

| Finding | Implication |
|---------|-------------|
| Normal distribution fits better | Circuit analogy breaks down; gaps are additive |
| No decay in log-gap means | Logarithmic "voltage" is not the right variable |
| White noise autocorrelation | No memory/filter structure exists |
| Scale-dependent reversals | Preliminary results were artifacts of small sample |

### 6.3 Theoretical Connections

**If supported**, the results suggest:

1. Rational bounds on prime density analogous to Î²â€“Î´ Doppler bounds
2. Transfer function formulation H(z) for prime-counting approximations
3. Poles/zeros corresponding to Riemann zeta structure

**These must be tested separately** and are not part of this experiment's scope.

---

## 7. Constraints and Limitations

### 7.1 What This Experiment Does NOT Test

1. Riemann Hypothesis implications
2. Cryptographic applications (key generation speedup)
3. CRISPR/bioinformatics applications
4. Specific transfer function designs
5. Predictions beyond the computed range

### 7.2 Known Limitations

1. Finite computational range (10â¸ or 10â¹ maximum practical)
2. Cannot distinguish between "true" log-normal and close approximations
3. Autocorrelation may be sensitive to window size choices
4. Heavy tails make variance estimates unstable

### 7.3 Potential Confounds

1. **Numerical precision:** Log of large primes may lose precision
   - Mitigation: Use np.float128 or mpmath for extended precision
2. **Edge effects:** First/last quintiles may behave differently
   - Mitigation: Exclude extreme quintiles in robustness checks
3. **Sieve artifacts:** Computational errors could create spurious patterns
   - Mitigation: Validate against known Ï€(x) at multiple checkpoints

---

## 8. Success Criteria

### 8.1 Experiment Success (Independent of Hypothesis Outcome)

- [ ] All phases (10â¶, 10â·, 10â¸) complete
- [ ] Prime counts match known values within Â±1
- [ ] All statistical tests execute without error
- [ ] Results are reproducible (seed-fixed where applicable)
- [ ] FINDINGS.md documents clear conclusion with evidence

### 8.2 Scientific Rigor Checklist

- [ ] Falsification criteria defined BEFORE running tests
- [ ] No data fabrication or selective reporting
- [ ] Negative results documented equally to positive
- [ ] Code is version-controlled and reproducible
- [ ] Statistical thresholds are conventional (not cherry-picked)

---

## 9. References

### 9.1 Mathematical Foundations

1. Prime Number Theorem: Ï€(x) ~ x/ln(x)
2. CramÃ©r's model for prime gaps
3. Napier's inequality: z/(z+1) < ln(1+z) < z for z > 0
4. Mechanicalâ€“electrical analogies (impedance/mobility forms)
5. Z-transform and Dirichlet series correspondence

### 9.2 Prior Work in This Project

1. Gist: "Proof and Analysis of Relativistic Doppler Shift Bounds" (zfifteen/d095ef208231ec991a8cacb7bdc5cc92)
2. Preliminary experiment: experiments/electrical_number_theory_analogy_test/

### 9.3 Statistical Methods

1. Kolmogorov-Smirnov test for distribution fitting
2. Ljung-Box test for autocorrelation
3. Maximum likelihood estimation for distribution parameters
4. Q-Q plots for distribution assessment

---

## 10. Appendix: Preliminary Results Summary

From initial experiment (9,592 primes to 10âµ):

| Metric | Value |
|--------|-------|
| Log-gap range | [0.000020, 0.510826] |
| Log-gap mean | 0.001128 |
| Log-gap std | 0.010868 |
| Q1 mean | 0.004704 |
| Q5 mean | 0.000128 |
| Decay ratio (Q1/Q5) | 36.8 |
| Best distribution fit | Log-normal (KS=0.0438) |
| Skewness | 31.55 |
| Excess kurtosis | 1194.87 |

These results motivate the current experiment but do not predetermine its outcome.
