
# TECH-SPEC: Falsifying Z-normalization Artifacts

## 1. Objective

Test whether observed prime gap autocorrelation (ACF(1) ≈ 0.8) is a mathematical artifact caused by **Z-normalization** (standardization) of finite datasets, rather than a genuine property of prime gap sequences.

The experiment should answer:

- Does Z-normalizing a sequence of truly independent random variables produce spurious autocorrelation?
- Can the observed ACF(1) ≈ 0.8 be replicated by applying Z-normalization to synthetic i.i.d. datasets?
- Is the autocorrelation magnitude sensitive to sample size N?
- Does the artifact magnitude match the claimed ACF(1) value?

---

## 2. High-level design

### Core methodology:

- Generate synthetic sequences of **truly independent** random variables (Gaussian, uniform, Poisson).
- Apply **Z-normalization** (subtract mean, divide by std).
- Compute **sample autocorrelation function** ACF(k) for lags k = 1, 2, ..., k_max.
- Compare observed ACF values against:
  - **Theoretical i.i.d. baseline** (should be ~0).
  - **Prime gap ACF values** from actual data.
- Test across multiple sample sizes: N ∈ {100, 500, 1000, 5000, 10000}.

### Null hypothesis:

If Z-normalization creates spurious autocorrelation, then:
- ACF(1) of Z-normalized i.i.d. data should be **non-zero**.
- Magnitude should depend on sample size N.
- Effect should vanish as N → ∞.

### Falsification criteria:

- **Falsified** if Z-normalized i.i.d. sequences produce ACF(1) ≥ 0.7.
- **Supported** if Z-normalized i.i.d. sequences maintain ACF(1) ≈ 0.

---

## 3. Data and inputs

### Synthetic datasets:

1. **Gaussian i.i.d.**: X_n ~ N(0, 1), n = 1, 2, ..., N
2. **Uniform i.i.d.**: X_n ~ Uniform(0, 1)
3. **Poisson i.i.d.**: X_n ~ Poisson(λ=5)
4. **Lognormal i.i.d.**: X_n ~ Lognormal(μ=0, σ=1)

### Sample sizes:

- N ∈ {100, 500, 1000, 5000, 10000}
- For each (distribution, N), run M = 1000 Monte Carlo replicates.

### Reference data:

- **Prime log-gaps** Δ_n = ln(p_{n+1} / p_n) from ranges:
  - [10^6, 10^7]
  - [10^9, 10^10]
  - [10^12, 10^13]

---

## 4. Models and null hypotheses

### Model A: Z-normalization artifact hypothesis

**Claim**: Observed ACF(1) ≈ 0.8 is a byproduct of Z-normalization.

**Prediction**:
- Z-normalized i.i.d. data will exhibit ACF(1) > 0.5.
- Effect magnitude inversely proportional to √N.

**Test**:
For Z-normalized synthetic data:
```
Z_n = (X_n - mean(X)) / std(X)
ACF(1) = Corr(Z_1:N-1, Z_2:N)
```

### Model B: True independence (null)

**Claim**: Z-normalization preserves independence structure.

**Prediction**:
- Z-normalized i.i.d. data will maintain ACF(1) ≈ 0.
- Observed values within ±2/√N confidence interval.

---

## 5. Metrics and analysis

### Primary metrics:

1. **Sample ACF(1)**:
   ```
   ACF(1) = Σ[(Z_n - Z̄)(Z_{n+1} - Z̄)] / Σ[(Z_n - Z̄)²]
   ```

2. **Mean ACF(1) across replicates**:
   ```
   E[ACF(1)] = (1/M) Σ ACF_m(1)
   ```

3. **Standard error**:
   ```
   SE = std(ACF(1)) / √M
   ```

### Statistical tests:

1. **One-sample t-test**:
   - H0: E[ACF(1)] = 0
   - Test if observed mean significantly different from zero.

2. **Comparison against prime data**:
   - Two-sample test: ACF(1)_synthetic vs ACF(1)_primes
   - Equivalence testing with threshold δ = 0.1

### Visualizations:

- **ACF(1) vs sample size N** (log-scale x-axis)
- **ACF(k) decay** for k = 1, 2, ..., 20
- **Distribution of ACF(1) across replicates** (histograms)
- **Comparison**: Synthetic vs prime gap ACF

---

## 6. Falsification criteria

### Evidence SUPPORTING artifact hypothesis:

✓ Z-normalized i.i.d. data shows ACF(1) ≥ 0.5  
✓ ACF(1) magnitude decreases as N increases (O(1/√N))  
✓ Multiple distributions (Gaussian, uniform, Poisson) all show similar artifact  
✓ Magnitude matches observed prime gap ACF(1)

### Evidence REFUTING artifact hypothesis:

✗ Z-normalized i.i.d. data maintains ACF(1) ≈ 0  
✗ ACF(1) stays within theoretical bounds ±2/√N  
✗ Prime gap ACF(1) significantly larger than synthetic  
✗ No systematic bias introduced by Z-normalization

**Decision rule**:
- If mean ACF(1) > 0.3 for N ≥ 1000 across all distributions → **Artifact confirmed**
- If mean ACF(1) < 0.1 for N ≥ 1000 → **Artifact rejected**

---

## 7. Expected outputs

### Quantitative results:

1. **Table**: Mean ACF(1) ± SE for each (distribution, N)
2. **p-values**: One-sample t-test against H0: ACF(1) = 0
3. **Effect size**: Cohen's d for ACF(1) deviation from zero
4. **Comparison**: |ACF(1)_synthetic - ACF(1)_primes|

### Plots:

1. `acf1_vs_sample_size.png`: ACF(1) vs N (log-log scale)
2. `acf_decay.png`: ACF(k) for k = 1...20 (multiple distributions)
3. `acf1_distribution.png`: Histogram of ACF(1) across replicates
4. `synthetic_vs_primes.png`: Side-by-side ACF comparison

### Report:

- `z_normalization_report.md`: Interpretation, statistical tests, conclusions

---

## 8. Implementation notes

### Python libraries:

```python
import numpy as np
from statsmodels.tsa.stattools import acf
from scipy import stats
import matplotlib.pyplot as plt
```

### Algorithm outline:

```python
for distribution in [gaussian, uniform, poisson, lognormal]:
    for N in [100, 500, 1000, 5000, 10000]:
        acf1_values = []
        for m in range(M):  # M = 1000 replicates
            X = generate_iid(distribution, N)
            Z = (X - np.mean(X)) / np.std(X)
            acf_vals = acf(Z, nlags=20, fft=False)
            acf1_values.append(acf_vals[1])
        
        # Statistical analysis
        mean_acf1 = np.mean(acf1_values)
        se = np.std(acf1_values) / np.sqrt(M)
        t_stat, p_value = stats.ttest_1samp(acf1_values, 0)
        
        # Store results
        results[(distribution, N)] = {
            'mean': mean_acf1,
            'se': se,
            'p': p_value
        }
```

### Validation checks:

- Verify synthetic data is truly i.i.d. (Ljung-Box test on raw X)
- Confirm Z-normalization: mean(Z) ≈ 0, std(Z) ≈ 1
- Check ACF confidence bounds: ±1.96/√N

---

## 9. Timeline

- **Day 1**: Generate synthetic datasets, implement Z-normalization
- **Day 2**: Compute ACF for all (distribution, N, replicate) combinations
- **Day 3**: Statistical analysis, hypothesis testing
- **Day 4**: Create plots, compare against prime gap data
- **Day 5**: Write report, document conclusions

---

## 10. Potential pitfalls

1. **Finite-sample bias**: ACF estimator itself has small-sample bias → use bias-corrected estimator if N < 500
2. **Multiple testing**: Adjust p-values (Bonferroni correction) when testing across multiple N
3. **Distribution choice**: Ensure synthetic distributions span different tail behaviors
4. **Implementation**: Double-check ACF calculation (manual vs statsmodels)

---

## 11. References

- **Box & Jenkins (1976)**: *Time Series Analysis: Forecasting and Control*. (Bias in ACF estimators)
- **Brockwell & Davis (1991)**: *Time Series: Theory and Methods*. (Asymptotic properties of sample ACF)
- **Chatfield (2003)**: *The Analysis of Time Series*. (ACF interpretation, confidence intervals)
