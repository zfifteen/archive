
# TECH-SPEC: Falsifying "Strong Autocorrelation" in Prime Gaps

## 1. Objective

Formally test whether prime log-gaps exhibit **strong autocorrelation** (specifically ACF(1) ≈ 0.8 as claimed), which would contradict classical **independence assumptions** such as Cramér's conjecture.

The experiment should answer:

- Do prime log-gaps show **statistically significant autocorrelation** at lag 1 (and higher lags)?
- Is the observed ACF(1) ≈ 0.8 **robust** across different prime ranges and window sizes?
- Can **simpler null models** (Cramér-like independence, sieve-based simulations) produce similar autocorrelation through parameter tuning?
- Does the autocorrelation structure differ from what would be expected from **long-range dependence** or **ARMA/GARCH** processes?

## 2. High-level design

- Extract prime log-gaps $$\Delta_n = \ln(p_{n+1}/p_n)$$ over multiple disjoint ranges.
- Compute **sample autocorrelation function (ACF)** for lags $$k = 1, 2, ..., K_{\max}$$ (typically $$K_{\max} = 50-100$$).
- Use **rigorous significance thresholds** that account for heavy tails and potential long-range dependence.
- Compare observed ACF against:
  - **Cramér-like models**: independent draws from empirical distribution.
  - **Sieve-based simulations**: randomized Eratosthenes sieve.
  - **ARMA/GARCH models**: tunable correlation structures.
- Apply **permutation tests** and **block bootstrap** to assess whether observed ACF is statistically distinguishable from null models.
- Test **partial autocorrelation function (PACF)** to identify direct vs indirect dependencies.

## 3. Inputs and data preparation

### 3.1 Prime ranges

- Configure disjoint prime ranges:  
  - Range A: $$[10^8, 10^9]$$  
  - Range B: $$[10^9, 10^{10}]$$  
  - Range C: $$[10^{10}, 10^{11}]$$

Requirements:
- Each range must contain ≥$$10^5$$ consecutive gaps for stable ACF estimation.
- All primes generated deterministically.

### 3.2 Log-gap extraction

For each range:
- Extract primes $$p_i$$ with $$P_{\min} \le p_i \le P_{\max}$$.
- Form log-gaps $$\Delta_i = \ln(p_{i+1}/p_i)$$.
- Record sequence $$(\Delta_1, \Delta_2, ..., \Delta_N)$$.

### 3.3 Windowing strategy

For robustness, divide each range into **overlapping windows**:
- Window size: $$W = 10^4$$ or $$10^5$$ gaps.
- Overlap: 50% (to increase number of independent estimates).
- Compute ACF separately for each window, then aggregate.

## 4. Autocorrelation function estimation

### 4.1 Sample ACF

For a sequence $$\{\Delta_i\}_{i=1}^N$$, the sample autocorrelation at lag $$k$$ is:

$$\hat{\rho}(k) = \frac{\sum_{i=1}^{N-k} (\Delta_i - \bar{\Delta})(\Delta_{i+k} - \bar{\Delta})}{\sum_{i=1}^N (\Delta_i - \bar{\Delta})^2}$$

where $$\bar{\Delta} = \frac{1}{N}\sum_{i=1}^N \Delta_i$$.

### 4.2 Significance thresholds

**Standard threshold** (assuming white noise):
$$\pm \frac{1.96}{\sqrt{N}}$$

However, this assumes:
- Independent observations.
- Light-tailed distributions.
- No long-range dependence.

**Robust threshold** (accounting for heavy tails):
Use **bootstrap** or **permutation** methods to construct empirical confidence bands (see Section 6).

### 4.3 Partial autocorrelation function (PACF)

PACF at lag $$k$$ measures the correlation between $$\Delta_i$$ and $$\Delta_{i+k}$$ after removing the linear influence of intermediate lags $$1, ..., k-1$$.

Estimate PACF using **Yule-Walker equations** or **Burg's method**.

**Interpretation**:
- If PACF(1) is large but PACF(k) for k > 1 is small → suggests AR(1) process.
- If both ACF and PACF decay slowly → suggests long-range dependence or ARIMA.

## 5. Cross-range and cross-window consistency

### 5.1 Per-range ACF estimates

For each prime range, compute:
- ACF(1), ACF(2), ..., ACF(K)
- Standard error of ACF using Bartlett's formula (for MA processes) or block bootstrap.

### 5.2 Consistency criterion

For the claim ACF(1) ≈ 0.8 to be robust:
- All ranges must yield $$0.7 \le \text{ACF}(1) \le 0.9$$.
- ACF(1) estimates across ranges should have variance $$\text{Var}(\hat{\rho}(1)) < 0.05^2$$.
- ACF should show similar decay patterns (e.g., exponential decay vs power-law decay).

### 5.3 Window-level variability

Within each range, compute ACF for multiple windows:
- If ACF(1) varies widely across windows (e.g., range from 0.3 to 0.9), this suggests:
  - Non-stationarity.
  - Local correlation that doesn't generalize.
- Report mean, median, and interquartile range of ACF(1) across windows.

## 6. Null model comparisons

### 6.1 Cramér-like independence model

**Construction**:
- Sample $$N$$ gaps independently from the **empirical distribution** of observed log-gaps.
- This preserves marginal distribution but removes all temporal correlation.

**Test**:
- Compute ACF for synthetic independent sequence.
- Repeat 1000 times to get distribution of ACF(1) under independence.

**Expected outcome**:
- If gaps are truly independent (Cramér), observed ACF(1) should fall within the 95% CI of the Cramér model.
- If observed ACF(1) ≈ 0.8 is far outside this CI, independence is rejected.

### 6.2 Sieve-based simulation

**Construction**:
- Generate primes via Eratosthenes sieve.
- Add randomization: for each composite, include as "pseudo-prime" with probability $$\epsilon$$, or exclude true primes with probability $$\delta$$.
- Tune $$(\epsilon, \delta)$$ to match global gap distribution and **also match observed ACF(1)**.

**Test**:
- If sieve model can match ACF(1) ≈ 0.8 with reasonable $$(\epsilon, \delta)$$ values, this suggests autocorrelation arises from sieve structure.
- If sieve model cannot match ACF(1) even with aggressive tuning, autocorrelation is not a simple sieve artifact.

### 6.3 ARMA/GARCH models

**Construction**:
- Fit **AR(1)** model: $$\Delta_i = \phi \Delta_{i-1} + \epsilon_i$$ where $$\epsilon_i$$ are i.i.d. innovations.
- Fit **GARCH(1,1)** model to allow for volatility clustering.
- Tune $$\phi$$ to match observed ACF(1).

**Test**:
- Compare higher-order ACF: does AR(1) with $$\phi \approx 0.8$$ match the full ACF structure?
- If yes, prime gaps may be well-described by a simple AR(1) process.
- If no (e.g., ACF decays differently), more complex structure is needed.

## 7. Permutation tests and block bootstrap

### 7.1 Permutation test for ACF(1)

**Procedure**:
1. Compute observed ACF(1) from data: $$\hat{\rho}_\text{obs}(1)$$.
2. Randomly permute the log-gaps (destroying temporal order).
3. Compute ACF(1) for permuted data: $$\hat{\rho}_\text{perm}(1)$$.
4. Repeat 10,000 times to build null distribution.
5. Compute p-value: $$p = P(\hat{\rho}_\text{perm}(1) \ge \hat{\rho}_\text{obs}(1))$$.

**Interpretation**:
- If $$p < 0.01$$, reject independence hypothesis.
- If $$p > 0.05$$, observed correlation could arise by chance.

### 7.2 Block bootstrap for confidence intervals

**Procedure**:
1. Divide sequence into blocks of size $$B$$ (e.g., $$B = 100$$).
2. Resample blocks with replacement to form bootstrap sequences.
3. Compute ACF(1) for each bootstrap sample.
4. Construct 95% CI from bootstrap distribution.

**Why block bootstrap?**
- Standard bootstrap assumes independence.
- Block bootstrap respects local correlation structure.
- Provides more accurate CI when data have autocorrelation.

## 8. Long-range dependence tests

### 8.1 Hurst exponent estimation

Use **rescaled range (R/S) analysis** to estimate Hurst exponent $$H$$:
- $$H = 0.5$$: short-range dependence (white noise).
- $$0.5 < H < 1$$: long-range dependence (persistent).
- $$H = 1$$: random walk.

**Method**:
1. Divide sequence into subranges of length $$n$$.
2. Compute rescaled range $$R/S$$ for each subrange.
3. Plot $$\log(R/S)$$ vs $$\log(n)$$ and estimate slope $$\approx H$$.

### 8.2 Detrended fluctuation analysis (DFA)

Alternative method to detect long-range correlations:
1. Integrate the series: $$Y(i) = \sum_{j=1}^i (\Delta_j - \bar{\Delta})$$.
2. Divide into windows, fit linear trend in each, compute residuals.
3. Compute fluctuation function $$F(n)$$ vs window size $$n$$.
4. Estimate scaling exponent $$\alpha$$ from $$F(n) \sim n^\alpha$$.

**Relation to Hurst**: $$\alpha \approx H$$ for stationary processes.

## 9. Success / falsification criteria

### 9.1 "Strong autocorrelation confirmed" criteria

For the autocorrelation claim to be **not falsified**, **all** of the following must hold:

1. **ACF(1) magnitude**:
   - All ranges yield $$\text{ACF}(1) \in [0.7, 0.9]$$.
   - Mean ACF(1) across ranges: $$0.75 \le \bar{\rho}(1) \le 0.85$$.

2. **Cross-range consistency**:
   - Variance of ACF(1) across ranges: $$\text{Var}(\hat{\rho}(1)) < 0.05^2$$.
   - All ranges show similar ACF decay patterns (not contradictory structures).

3. **Statistical significance**:
   - Permutation test p-value: $$p < 0.01$$ for all ranges.
   - ACF(1) is outside 99% CI of Cramér independence model.

4. **Null model failure**:
   - Cramér independence model yields $$|\text{ACF}(1)| < 0.2$$ on average.
   - Sieve model cannot match ACF(1) ≈ 0.8 without unrealistic $$(\epsilon, \delta)$$ (e.g., $$\epsilon, \delta > 0.3$$).

5. **Robustness**:
   - ACF(1) remains in $$[0.7, 0.9]$$ across different window sizes ($$10^4$$, $$10^5$$ gaps).
   - Bootstrap CI for ACF(1) does not include 0.

### 9.2 Falsification conditions

The autocorrelation claim is **falsified** if **any** of the following hold:

- **ACF(1) out of range**: At least two ranges yield $$\text{ACF}(1) < 0.6$$ or $$\text{ACF}(1) > 1.0$$.

- **High variance**: Variance of ACF(1) across ranges exceeds 0.1.

- **Not statistically significant**: Permutation test yields $$p > 0.05$$ for at least two ranges.

- **Null model success**: Cramér or sieve models produce $$\text{ACF}(1) \in [0.7, 0.9]$$ with reasonable parameters.

- **ARMA/GARCH equivalence**: Simple AR(1) or GARCH(1,1) model fully explains ACF structure, suggesting no special prime-specific mechanism.

- **Non-stationarity**: ACF(1) varies by >0.4 across windows within a single range, indicating local effects rather than global structure.

If any falsification condition is triggered:
- Report that the **strong autocorrelation claim failed** under this protocol.
- Specify which condition(s) caused the failure.

## 10. Outputs

### 10.1 Structured machine-readable results

A JSON or CSV file with:

**Per-range ACF results**:
- `range_id`, `p_min`, `p_max`, `n_gaps`
- `ACF_1`, `ACF_2`, ..., `ACF_K` (autocorrelation at lags 1 through K)
- `PACF_1`, `PACF_2`, ..., `PACF_K` (partial autocorrelation)
- `ACF_1_SE` (standard error of ACF(1) from block bootstrap)
- `ACF_1_95CI_lower`, `ACF_1_95CI_upper`
- `permutation_p_value` (from permutation test)
- `hurst_exponent`, `hurst_95CI_lower`, `hurst_95CI_upper`

**Per-window ACF results** (for variability analysis):
- `range_id`, `window_id`, `window_start`, `window_end`
- `ACF_1_window`
- Summary statistics: mean, median, IQR of ACF(1) across windows

**Null model comparisons**:
- `model_type` ("Cramer", "sieve", "AR1", "GARCH")
- `ACF_1_null_mean`, `ACF_1_null_sd`
- `ACF_1_null_95CI_lower`, `ACF_1_null_95CI_upper`
- `can_match_observed` (boolean: whether null model can produce ACF(1) ≈ 0.8)

### 10.2 Human-readable summary report

A Markdown file (`report.md`) with:
- **Summary verdict**: "Strong autocorrelation confirmed" or "Autocorrelation claim falsified".
- **Per-range ACF(1) estimates** with confidence intervals.
- **Cross-range consistency**: mean, variance, and range of ACF(1).
- **Permutation test results**: p-values for each range.
- **Null model comparison**: which models can/cannot match observed ACF.
- **Long-range dependence**: Hurst exponent estimates.
- **Falsification trigger** (if any): which criterion caused failure.

### 10.3 Visualizations

**Required plots** (PNG, one per range):

1. **ACF plot**:
   - Bar plot of ACF(k) vs lag k.
   - Include 95% confidence bands (from block bootstrap).
   - Annotate ACF(1) value prominently.

2. **PACF plot**:
   - Bar plot of PACF(k) vs lag k.
   - Helps identify AR order.

3. **ACF comparison across ranges**:
   - Overlay ACF curves for all ranges on one plot.
   - Shows consistency/variability.

4. **ACF distribution across windows**:
   - Histogram of ACF(1) values from all windows.
   - Shows robustness within range.

5. **Null model comparison**:
   - Box plot showing ACF(1) distributions for:
     - Observed data
     - Cramér model
     - Sieve model
     - AR(1) model

6. **Hurst exponent plot** (log-log plot):
   - $$\log(R/S)$$ vs $$\log(n)$$ with fitted line.
   - Annotate slope = H estimate.

## 11. Implementation notes

### 11.1 Language and dependencies

- **Language**: Python 3.9+
- **Required libraries**:
  - NumPy, SciPy (numerical computation, ACF/PACF)
  - pandas (data management)
  - statsmodels (time series analysis, ARMA/GARCH fitting, Hurst estimation)
  - matplotlib, seaborn (visualization)
  - arch (GARCH models)

### 11.2 Prime generation

- Use segmented sieve or precomputed prime tables for ranges up to $$10^{11}$$.
- Ensure deterministic generation (no randomness in prime selection).

### 11.3 Computational considerations

**ACF estimation**:
- For $$N = 10^6$$ gaps, computing ACF up to lag 100 takes <1 second.
- Use FFT-based ACF computation for efficiency: $$O(N \log N)$$ instead of $$O(N K)$$.

**Permutation tests**:
- 10,000 permutations of $$10^5$$ gaps ≈ 5 minutes per range.
- Parallelize across ranges for speed.

**Block bootstrap**:
- 1000 bootstrap samples with block size 100 ≈ 2 minutes per range.

**Total runtime estimate**:
- Full protocol (3 ranges, all tests) ≈ 30-60 minutes on modern CPU.

### 11.4 Reproducibility

- All random operations (permutations, bootstrap) use global `--seed` parameter.
- Embed spec version, parameters, and timestamps in output metadata.
- Log all intermediate steps (window boundaries, null model parameters) for audit.

### 11.5 CLI interface

Example usage:

```bash
python run_acf_falsification.py \
  --ranges "1e8:1e9,1e9:1e10,1e10:1e11" \
  --window-size 100000 \
  --max-lag 100 \
  --seed 42 \
  --output results/ \
  --null-models cramer,sieve,ar1 \
  --permutations 10000 \
  --bootstrap-iterations 1000
```

Flags:
- `--ranges`: Comma-separated list of range pairs `P_min:P_max`.
- `--window-size`: Number of gaps per window for within-range analysis.
- `--max-lag`: Maximum lag K for ACF/PACF computation.
- `--seed`: RNG seed for reproducibility.
- `--output`: Directory for results.
- `--null-models`: Which control models to run (default: all).
- `--permutations`: Number of permutation test iterations.
- `--bootstrap-iterations`: Number of block bootstrap samples.
- `--block-size`: Block size for block bootstrap (default: 100).
- `--hurst-analysis`: Enable Hurst exponent estimation (R/S and DFA).

### 11.6 Performance targets

- **Single range** ($$10^8$$ to $$10^9$$, ACF only): <5 minutes.
- **Full protocol** (3 ranges, all null models, permutation + bootstrap): <1 hour.

---

## 12. Relationship to other tests

This test complements:

**Fractal cascade structure**:
- If autocorrelation is strong (ACF(1) ≈ 0.8), this is consistent with multiplicative cascades.
- Cascade models typically produce long-range correlation.

**Lognormal vs exponential**:
- Log-normal distributions can arise from correlated multiplicative processes.
- Strong autocorrelation would support the log-normal hypothesis.

Depends on:
- Prime data generation from previous tests.

Feeds into:
- `hybrid-model-tests/` (correlation is a key signature to explain).

---

## 13. Robustness checks

### 13.1 Alternative window sizes

Repeat ACF estimation with windows of $$10^4$$, $$5 \times 10^4$$, $$10^5$$ gaps.
- If ACF(1) is robust, estimates should be stable across window sizes.

### 13.2 Detrending

Apply linear or polynomial detrending before computing ACF:
- Remove any global trends (e.g., logarithmic growth in gap sizes).
- Recompute ACF on detrended series.
- If ACF(1) persists after detrending, correlation is not due to trends.

### 13.3 Subrange tests

Divide each range into smaller non-overlapping subranges (e.g., 10 subranges).
- Compute ACF(1) for each subrange.
- If ACF(1) is consistent across subranges, correlation is stationary.
- If ACF(1) varies widely, suggests non-stationary or local effects.

---

## References

- **Cramér (1936)**: "On the order of magnitude of the difference between consecutive prime numbers." (Independence conjecture)
- **Box & Jenkins (1976)**: *Time Series Analysis: Forecasting and Control*. (ACF, PACF, ARMA models)
- **Beran (1994)**: *Statistics for Long-Memory Processes*. (Hurst exponent, long-range dependence)
- **Peng et al. (1994)**: "Mosaic organization of DNA nucleotides." *Physical Review E*. (Detrended fluctuation analysis)
- **Efron & Tibshirani (1993)**: *An Introduction to the Bootstrap*. (Block bootstrap methods)
- **Original claim**: [prime-gap-lognormal Discussion #1](https://github.com/zfifteen/prime-gap-lognormal/discussions/1) (ACF(1) ≈ 0.796 reported)
