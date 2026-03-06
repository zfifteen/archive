
# TECH-SPEC: Falsifying "Fractal Cascade Structure" in Prime Gaps

## 1. Objective

Formally test whether prime log-gaps exhibit **recursive log-normal structure within magnitude strata**, suggesting multiplicative cascade dynamics analogous to turbulent energy dissipation.

The experiment should answer:

- Do prime log-gaps, when stratified by magnitude (quintiles, deciles, etc.), show **log-normal distributions within each stratum** with consistent goodness-of-fit?
- Does variance scaling across strata follow a **power-law relationship** $$\sigma_k \sim \mu_k^H$$ with a stable **Hurst exponent** $$H \approx 0.8$$?
- Can simple **additive noise models** or **sieve-based simulations** reproduce these patterns, or do they require multiplicative cascade structure?

## 2. High-level design

- Extract prime log-gaps $$\Delta_n = \ln(p_{n+1}/p_n)$$ over multiple disjoint ranges.
- **Stratify** gaps by magnitude into quintiles, deciles, or finer partitions (25, 125 bins).
- For each stratum:
  - Fit log-normal distribution and record parameters $$(\mu_k, \sigma_k)$$.
  - Compute KS statistic to assess goodness-of-fit.
- Test **variance scaling**: plot $$\log \sigma_k$$ vs $$\log \mu_k$$ and estimate Hurst exponent $$H$$ from the slope.
- Compare observed patterns against:
  - **Cramér-like additive models** (independent gaps with matched marginals).
  - **Sieve-based simulations** (Eratosthenes with randomization).
  - **Pure multiplicative cascade models** (tunable parameters).
- Estimate **multifractal spectrum** to check for cascade signatures.

## 3. Inputs and data preparation

### 3.1 Prime ranges

- Configure an ordered list of disjoint prime ranges:  
  - Range A: $$[10^8, 10^9]$$  
  - Range B: $$[10^9, 10^{10}]$$  
  - Range C: $$[10^{10}, 10^{11}]$$  
  (Same as lognormal-vs-exponential test for consistency.)

Requirements:

- Each range must contain **at least** $$10^5$$ consecutive gaps.
- All primes generated deterministically or loaded from verified tables.

### 3.2 Log-gap extraction

For each range:

- Extract primes $$p_i$$ with $$P_{\min} \le p_i \le P_{\max}$$.
- Form log-gaps $$\Delta_i = \ln(p_{i+1}/p_i) = \ln(g_i)$$ where $$g_i = p_{i+1} - p_i$$.
- Record $$(p_i, \Delta_i)$$ for each gap.

### 3.3 Stratification scheme

Within each range, stratify log-gaps by magnitude:

**Primary stratifications**:
- **Quintiles** (5 strata): partition gaps into 5 equal-sized bins by magnitude.
- **Deciles** (10 strata): partition into 10 bins.
- **Finer** (25 or 125 strata): for high-resolution analysis.

For each stratum $$k$$:
- Define magnitude bounds $$[\Delta_{k,\min}, \Delta_{k,\max})$$.
- Collect all gaps whose $$\Delta_i$$ falls in that range.

Per-stratum requirements:
- Minimum gaps per stratum: $$N_\text{stratum} \ge 1000$$ (to allow reliable KS tests).
- Strata failing this are flagged and excluded from analysis.

## 4. Within-stratum log-normal fitting

### 4.1 Model specification

For each stratum $$k$$, assume log-gaps $$\Delta_{k,i}$$ follow a log-normal distribution:

$$\Delta \sim \text{Lognormal}(\mu_k, \sigma_k)$$

Equivalently, $$\ln \Delta \sim N(\mu_k, \sigma_k^2)$$.

### 4.2 Parameter estimation

For each stratum $$k$$:

- Fit $$(\mu_k, \sigma_k)$$ via **maximum likelihood**:  
  - $$\hat{\mu}_k = \text{mean}(\ln \Delta_{k,i})$$  
  - $$\hat{\sigma}_k^2 = \text{var}(\ln \Delta_{k,i})$$

### 4.3 Goodness-of-fit tests

For each stratum $$k$$:

- Compute **Kolmogorov-Smirnov (KS)** statistic comparing:  
  - Empirical CDF of $$\ln \Delta_{k,i}$$  
  - Theoretical CDF of $$N(\hat{\mu}_k, \hat{\sigma}_k^2)$$
- Record $$(\text{KS}_k, p_k)$$.

**Acceptance criterion**:  
- Stratum passes if $$\text{KS}_k < 0.10$$ (loose threshold) or $$p_k > 0.01$$ after multiple-testing correction.
- Track percentage of strata passing across all ranges.

## 5. Variance scaling and Hurst exponent

### 5.1 Power-law relationship

The cascade hypothesis predicts:

$$\sigma_k \sim \mu_k^H$$

or equivalently:

$$\log \sigma_k = H \log \mu_k + C$$

where $$H$$ is the **Hurst exponent** and $$C$$ is a constant.

For turbulent cascades, typically $$0.5 \le H \le 1$$. The original claim suggests $$H \approx 0.8$$ for prime gaps.

### 5.2 Hurst exponent estimation

For each range:

- Collect all stratum parameters $$(\mu_k, \sigma_k)$$ from that range.
- Perform **log-log linear regression**:  
  - $$y_k = \log \sigma_k$$  
  - $$x_k = \log \mu_k$$  
  - Fit $$y = H x + C$$ via OLS.
- Record:
  - $$\hat{H}$$ (estimated Hurst exponent)  
  - $$R^2$$ (goodness-of-fit for the power law)  
  - 95% confidence interval for $$H$$

### 5.3 Cross-range consistency

Compute $$\hat{H}$$ for each prime range independently.

**Consistency criterion**:  
- Cascade claim requires $$H$$ to be stable across ranges:  
  - $$|\hat{H}_A - \hat{H}_B| < 0.2$$  
  - $$|\hat{H}_A - \hat{H}_C| < 0.2$$  
  - $$|\hat{H}_B - \hat{H}_C| < 0.2$$
- Additionally, all ranges should yield $$H \in [0.6, 1.0]$$ with $$R^2 > 0.85$$.

## 6. Null model comparisons

To determine whether the observed patterns require cascade structure, we generate control datasets from simpler models.

### 6.1 Cramér-like additive model

**Construction**:  
- Sample gaps independently from the **global empirical distribution** of log-gaps observed in real data.
- This preserves marginal distribution but removes all correlation and cascade structure.

**Test**:  
- Stratify these synthetic gaps by magnitude (same quintiles/deciles).
- Fit log-normal to each stratum and compute KS statistics.
- Estimate Hurst exponent $$H_\text{Cramér}$$ from variance scaling.

**Expected outcome**:  
- If cascade structure is essential, the Cramér model should **fail** to produce:  
  - Consistent log-normal fits in strata (higher KS statistics).  
  - Power-law variance scaling with $$H \approx 0.8$$ (expect $$H \approx 0.5$$ or no clear power law).

### 6.2 Sieve-based simulation

**Construction**:  
- Use Eratosthenes sieve to generate primes up to $$N$$.
- Introduce randomization: for each composite, retain it as "pseudo-prime" with small probability $$\epsilon$$, or remove true primes with probability $$\delta$$.
- Tune $$(\epsilon, \delta)$$ to match the **global gap distribution**.

**Test**:  
- Extract log-gaps from the perturbed sieve.
- Stratify and test for log-normality within strata.
- Estimate $$H_\text{sieve}$$.

**Expected outcome**:  
- If simple sieve noise explains the pattern, $$H_\text{sieve}$$ should match $$H_\text{observed}$$.  
- If not, the cascade structure is genuinely distinct from sieve-based randomness.

### 6.3 Pure multiplicative cascade model

**Construction**:  
- Implement a standard multiplicative cascade (e.g. **p-model** or **β-model** from turbulence):  
  - Start with uniform interval $$[0,1]$$.  
  - At each level, split into sub-intervals and assign multiplicative weights drawn from a log-normal distribution.  
  - After $$L$$ levels, read off the "energy" at each point as a synthetic gap magnitude.
- Tune the cascade parameters to match the **global mean and variance** of observed log-gaps.

**Test**:  
- Stratify cascade-generated gaps and fit log-normal within strata.
- Estimate $$H_\text{cascade}$$ from variance scaling.

**Expected outcome**:  
- A properly tuned cascade should reproduce:  
  - Log-normal distributions within strata.  
  - Power-law variance scaling with $$H \approx 0.8$$.
- If the cascade model matches but Cramér/sieve do not, this supports the cascade hypothesis.

## 7. Multifractal spectrum analysis

### 7.1 Partition function method

To test for multifractal scaling, compute the **partition function**:

$$Z_q(\ell) = \sum_{i=1}^{N(\ell)} \left(\frac{\Delta_i(\ell)}{\sum_j \Delta_j(\ell)}\right)^q$$

where:
- $$\ell$$ is a scale (box size).
- $$\Delta_i(\ell)$$ is the sum of gaps in the $$i$$-th box of size $$\ell$$.
- $$q$$ is a moment order (typically $$q \in [-5, 5]$$).

For a multifractal process:

$$Z_q(\ell) \sim \ell^{\tau(q)}$$

where $$\tau(q)$$ is the **mass exponent**.

### 7.2 Singularity spectrum $$f(\alpha)$$

From $$\tau(q)$$, compute the **singularity spectrum** via Legendre transform:

$$\alpha(q) = \frac{d\tau}{dq}, \quad f(\alpha) = q\alpha - \tau(q)$$

For a **monofractal** (uniform scaling), $$f(\alpha)$$ is a point.  
For a **multifractal** (cascade), $$f(\alpha)$$ is a concave parabola.

### 7.3 Expected signature

If prime gaps follow a multiplicative cascade:
- $$f(\alpha)$$ should be a smooth parabola with width $$\Delta \alpha > 0.2$$.
- The peak should occur near $$\alpha_0 \approx 1$$ (box dimension).

If gaps are additive noise:
- $$f(\alpha)$$ collapses to a point or very narrow peak.

## 8. Success / falsification criteria

Define clear, pre-registered criteria.

### 8.1 "Cascade structure confirmed" criteria

For the cascade hypothesis to be **not falsified**, **all** of the following must hold:

1. **Within-stratum log-normality**:  
   - ≥80% of strata across all ranges pass KS test ($$\text{KS} < 0.10$$ or $$p > 0.01$$).

2. **Hurst exponent stability**:  
   - All ranges yield $$H \in [0.6, 1.0]$$.  
   - Cross-range variation $$|\hat{H}_i - \hat{H}_j| < 0.2$$ for all pairs.
   - Power-law fits have $$R^2 > 0.85$$.

3. **Null model failure**:  
   - Cramér and sieve models show **degraded** performance:  
     - <60% of strata pass KS test, or  
     - $$H_\text{null}$$ differs from $$H_\text{observed}$$ by >0.3, or  
     - $$R^2_\text{null} < 0.70$$.

4. **Cascade model success**:  
   - Pure multiplicative cascade reproduces observed patterns:  
     - ≥75% of strata pass KS test.  
     - $$|H_\text{cascade} - H_\text{observed}| < 0.15$$.

5. **Multifractal signature**:  
   - Singularity spectrum $$f(\alpha)$$ has width $$\Delta \alpha > 0.2$$ and smooth parabolic shape.

### 8.2 Falsification conditions

The cascade claim is **falsified** if **any** of the following hold:

- **Within-stratum failure**: <50% of strata pass KS test in at least two ranges.

- **Hurst instability**: Hurst exponent varies by >0.2 across ranges, or falls outside $$[0.6, 1.0]$$, or $$R^2 < 0.85$$ in any range.

- **Null model success**: Cramér or sieve models produce comparable results:  
  - ≥70% of null-model strata pass KS test, **and**  
  - $$|H_\text{null} - H_\text{observed}| < 0.15$$.

- **Cascade model failure**: Pure multiplicative cascade cannot reproduce observed patterns even after parameter tuning.

- **No multifractal signature**: $$f(\alpha)$$ width $$\Delta \alpha < 0.1$$ or collapses to monofractal.

If any falsification condition is triggered, the script must:
- Report that the **cascade structure claim failed** under this protocol.
- Specify which condition(s) caused the failure.

## 9. Robustness and sensitivity checks

### 9.1 Alternative stratifications

Repeat the experiment with:
- Different numbers of strata (5, 10, 25, 125).
- Quantile-based vs fixed-width magnitude bins.

Cascade structure should persist under these variations.

### 9.2 Bootstrap confidence intervals

For Hurst exponent estimation:
- Use bootstrap resampling (1000 iterations) to estimate 95% CI for $$H$$.
- Check if CI includes the claimed value $$H = 0.8$$.

### 9.3 Subrange tests

Divide each prime range into smaller windows and compute $$H$$ locally.
- If cascade is genuine, local $$H$$ estimates should cluster around global $$H$$.

## 10. Outputs

The script implementing this spec should produce:

### 10.1 Structured machine-readable results

A JSON or CSV file with entries:

**Per-stratum results**:
- `range_id`, `stratum_id`, `delta_min`, `delta_max`
- `n_gaps` (number of gaps in stratum)
- `mu_hat`, `sigma_hat` (fitted log-normal parameters)
- `KS_stat`, `KS_p` (goodness-of-fit test)
- `pass_KS` (boolean: whether stratum passes threshold)

**Per-range Hurst analysis**:
- `range_id`
- `H_estimate` (Hurst exponent from log-log regression)
- `H_95CI_lower`, `H_95CI_upper` (bootstrap confidence interval)
- `R_squared` (power-law fit quality)
- `n_strata_used` (number of strata with sufficient data)
- `pct_strata_pass_KS` (percentage passing KS test)

**Null model comparisons**:
- `model_type` ("Cramér", "sieve", "cascade")
- `H_null`, `R_squared_null`
- `pct_strata_pass_KS_null`
- `delta_H` (difference from observed $$H$$)

**Multifractal analysis**:
- `range_id`
- `tau_q` (array of mass exponents for different $$q$$)
- `alpha_spectrum`, `f_alpha_spectrum` (singularity spectrum)
- `delta_alpha_width` (width of $$f(\alpha)$$ spectrum)

### 10.2 Human-readable summary report

A Markdown file (`report.md`) with:
- **Summary verdict**: "Cascade structure confirmed" or "Cascade claim falsified"
- **Per-range results**:
  - Hurst exponent estimates with CI
  - Percentage of strata passing KS test
  - Comparison with null models
- **Cross-range consistency**: variance of $$H$$ across ranges
- **Multifractal signature**: description of $$f(\alpha)$$ shape and width
- **Falsification trigger** (if any): which criterion caused failure

### 10.3 Visualizations

**Required plots** (PNG, one per range):

1. **Stratified log-normal fits**:  
   - Faceted histograms showing data vs fitted log-normal for each stratum.
   - Annotate each panel with $$\mu_k$$, $$\sigma_k$$, KS statistic.

2. **Variance scaling plot** ($$\log \sigma_k$$ vs $$\log \mu_k$$):  
   - Scatter plot with OLS regression line.
   - Display $$H$$ estimate, $$R^2$$, and 95% CI as annotation.

3. **Q-Q plots per stratum**:  
   - $$\ln \Delta$$ quantiles vs theoretical normal quantiles.
   - Assess deviations from log-normality.

4. **Multifractal spectrum $$f(\alpha)$$**:  
   - Plot $$f(\alpha)$$ vs $$\alpha$$ for observed data and null models.
   - Highlight parabolic shape if cascade structure is present.

5. **Hurst exponent comparison** (across ranges and models):  
   - Bar plot showing $$H$$ estimates with error bars.
   - Compare observed, Cramér, sieve, and cascade models.

### 10.4 Null model synthetic data

Store generated synthetic gaps from null models for reproducibility:
- `synthetic_cramer_gaps.csv`
- `synthetic_sieve_gaps.csv`
- `synthetic_cascade_gaps.csv`

## 11. Implementation notes

### 11.1 Language and dependencies

- **Language**: Python 3.9+
- **Required libraries**:
  - NumPy, SciPy (numerical computation, statistical tests)
  - pandas (data management)
  - matplotlib, seaborn (visualization)
  - scikit-learn (regression, bootstrap)
  - statsmodels (statistical models, KS tests)
  - Optional: `pymultifracs` or custom implementation for multifractal analysis

### 11.2 Prime generation

- Use **segmented sieve** or precomputed prime tables to handle ranges up to $$10^{11}$$.
- Ensure deterministic generation (no randomness in prime selection).

### 11.3 Computational considerations

- **Stratification** with 125 bins may require ≥$$10^6$$ gaps per range.
- **Bootstrap** for Hurst CI: 1000 iterations should complete in <10 minutes per range.
- **Multifractal analysis**: partition function computation scales as $$O(N \cdot n_q \cdot n_\ell)$$; use efficient vectorized code.

### 11.4 Reproducibility

- All random choices (bootstrap sampling, synthetic data generation) must use a global `--seed` parameter.
- Embed spec version, parameters, and timestamps in output metadata.
- Log all intermediate steps (stratification boundaries, fit parameters) for audit.

### 11.5 CLI interface

Example usage:

```bash
python run_cascade_falsification.py \
  --ranges "1e8:1e9,1e9:1e10,1e10:1e11" \
  --strata 10 \
  --seed 42 \
  --output results/ \
  --null-models cramer,sieve,cascade \
  --bootstrap-iterations 1000
```

Flags:
- `--ranges`: Comma-separated list of range pairs `P_min:P_max`.
- `--strata`: Number of magnitude strata (5, 10, 25, 125).
- `--seed`: RNG seed for reproducibility.
- `--output`: Directory for results.
- `--null-models`: Which control models to run (default: all).
- `--bootstrap-iterations`: Number of bootstrap samples for Hurst CI.
- `--multifractal`: Enable multifractal spectrum analysis (slower).

### 11.6 Performance targets

- **Single range** ($$10^8$$ to $$10^9$$, 10 strata, no null models): <5 minutes on modern CPU.
- **Full protocol** (3 ranges, 3 null models, bootstrap, multifractal): <2 hours.

---

## 12. Relationship to other tests

This test builds on **lognormal-vs-exponential**:
- That test confirmed log-normal fits **globally** and within magnitude bands.
- This test asks: **why** are they log-normal? Is it additive noise, or multiplicative cascade?

Depends on:
- `lognormal-vs-exponential/` for prime data and basic log-normal validation.

Feeds into:
- `autocorrelation-tests/` (cascade structure predicts long-range correlation).
- `hybrid-model-tests/` (cascade is one component of the hybrid model).

---

## References

- **Kolmogorov (1962)**: "A refinement of previous hypotheses concerning the local structure of turbulence in a viscous incompressible fluid at high Reynolds number."
- **Frisch (1995)**: *Turbulence: The Legacy of A. N. Kolmogorov*. (Multiplicative cascades, multifractal formalism)
- **Mandelbrot (1974)**: "Intermittent turbulence in self-similar cascades."
- **Cramér (1936)**: "On the order of magnitude of the difference between consecutive prime numbers." (Additive independence model)
- **Original claim**: [prime-gap-lognormal Discussion #1](https://github.com/zfifteen/prime-gap-lognormal/discussions/1)
