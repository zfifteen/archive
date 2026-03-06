
# TECH-SPEC: Falsifying "Lognormal Beats Exponential" for Prime Gaps

## 1. Objective

Formally test whether finite-range prime gaps are **better modeled by lognormal distributions than by exponential distributions**, in a way that can *falsify* the claim under stronger controls than the original playground experiments.

The experiment should answer:

- When gaps are suitably banded by scale, does the **lognormal** model consistently outperform the **exponential** model on **held-out** data?  
- Does this preference persist across **disjoint prime ranges**, **alternative bandings**, and **robustness checks**, or does it collapse under stricter methodology?

## 2. High-level design

- Use a high-quality prime source (either a local sieve or trusted tables) to extract **consecutive prime gaps** over multiple disjoint ranges $$[P_{\min}, P_{\max}]$$.
- Within each range, **band** primes by scale and collect the associated gaps.  
- For each band:  
  - Fit **lognormal** and **exponential** models on a **training subset** of gaps.  
  - Evaluate both models on a **held-out test subset** using:  
    - Log-likelihood and likelihood-ratio tests.  
    - Information criteria (AIC, BIC).  
    - Goodness-of-fit tests on the *test* data (KS, Anderson–Darling on the CDF).  
- Aggregate results across bands and ranges with predefined success/failure criteria that can falsify the "lognormal wins" claim.

## 3. Inputs and data preparation

### 3.1 Prime ranges

- Configure an ordered list of disjoint prime ranges, e.g.:  
  - Range A: $$[10^8, 10^9]$$  
  - Range B: $$[10^9, 10^{10}]$$  
  - Range C: $$[10^{10}, 10^{11}]$$  
  (Exact defaults can be tuned, but must be documented in the script's CLI help.)

Requirements:

- Each range must contain **at least** $$10^5$$ consecutive gaps after filtering, or the range is skipped with a logged warning.  
- All primes are to be generated deterministically (e.g. segmented sieve) or loaded from verified prime tables.

### 3.2 Gap extraction

For each range:

- Extract primes $$p_i$$ with $$P_{\min} \le p_i \le P_{\max}$$.  
- Form consecutive gaps $$g_i = p_{i+1} - p_i$$ where both $$p_i$$ and $$p_{i+1}$$ lie inside the range.  
- Discard any gaps with $$g_i \le 0$$ (should not occur for valid primes).  
- Record $$(p_i, g_i)$$ for each gap.

### 3.3 Banding scheme

Within each range, define a banding scheme by **prime size**:

- Default: **6 log-spaced bands** in $$\log_{10} p$$ between $$\log_{10} P_{\min}$$ and $$\log_{10} P_{\max}$$.
- For each band $$b$$, define:  
  - $$p \in [B_{b,\min}, B_{b,\max})$$.  
  - Collect all gaps $$g_i$$ whose **left prime** $$p_i$$ lies in that band.

Per-band requirements:

- Minimum gaps per band (after all filters): $$N_\text{band} \ge 5000$$.  
- Bands failing this are skipped, with a clear note in the results.

## 4. Models

### 4.1 Exponential model

For each band:

- Model: $$g \sim \text{Exp}(\lambda)$$ with density $$f(g) = \lambda e^{-\lambda g}$$ for $$g > 0$$.  
- Fit $$\lambda$$ by **maximum likelihood** on the *training* subset of gaps:  
  - $$\hat{\lambda} = 1/\bar{g}_{\text{train}}$$.

### 4.2 Lognormal model

For each band:

- Model: $$g \sim \text{Lognormal}(\mu, \sigma)$$, meaning $$\ln g \sim N(\mu, \sigma^2)$$.  
- Fit $$(\mu, \sigma)$$ by **maximum likelihood** on the *training* subset of gaps:  
  - $$\hat{\mu} = \text{mean}(\ln g_\text{train})$$  
  - $$\hat{\sigma}^2 = \text{var}(\ln g_\text{train})$$.

## 5. Train/test split

For each band:

- Randomly shuffle the gaps (with fixed RNG seed for reproducibility).  
- Split into:  
  - Train: 70%  
  - Test: 30%  
- All **parameter fitting** must use only the train subset.  
- All **model comparison metrics** (likelihood, KS, AD, AIC/BIC) must be computed on the **test** subset.

## 6. Metrics and statistical tests

All tests are per-band, per-range, then aggregated.

### 6.1 Log-likelihood and likelihood ratio

For each band on the **test** gaps:

- Compute log-likelihoods:  
  - $$\log L_{\text{exp}} = \sum \log f_\text{exp}(g_i \mid \hat{\lambda})$$.  
  - $$\log L_{\text{ln}} = \sum \log f_\text{ln}(g_i \mid \hat{\mu}, \hat{\sigma})$$.  
- Compute $$\Delta \log L = \log L_{\text{ln}} - \log L_{\text{exp}}$$.  
- Optionally, compute a **likelihood-ratio statistic**  
  - $$2 (\log L_{\text{ln}} - \log L_{\text{exp}})$$  
  and a corresponding p-value under an appropriate asymptotic approximation (null: exponential is as good as lognormal).

### 6.2 Information criteria (AIC, BIC)

For each model on **test** gaps:

- AIC: $$ \text{AIC} = 2k - 2\log L$$, where  
  - $$k_\text{exp} = 1$$, $$k_\text{ln} = 2$$.  
- BIC: $$ \text{BIC} = k \ln n - 2\log L$$, where $$n$$ = size of test subset.  
- Compute $$\Delta \text{AIC} = \text{AIC}_\text{exp} - \text{AIC}_\text{ln}$$, and similarly for BIC; **positive** values favor lognormal.

### 6.3 Goodness-of-fit: KS and AD

For each model on **test** gaps:

- Compute the **empirical CDF** of the test gaps.  
- Compute the **model CDF** using the fitted parameters.  
- Run:  
  - **Kolmogorov–Smirnov (KS)** test (with parameters treated as fixed).  
  - **Anderson–Darling (AD)** test if available.

Record:

- KS statistic and p-value for both models.  
- AD statistic and p-value for both models.

### 6.4 Multiple-testing control

Because we test across many bands and ranges:

- Use a **Benjamini–Hochberg FDR** correction on the set of "lognormal beats exponential" KS/AD p-values per range.
- Alternatively, allow configuration for simple Bonferroni as a stricter option.

## 7. Success / falsification criteria

Define clear, pre-registered criteria.

### 7.1 "Lognormal wins" criteria

For a **given band**:

- **Primary**: Lognormal has **lower BIC** than exponential by at least a margin $$\Delta\text{BIC} \ge 10$$ (strong evidence) on the test subset.  
- **Secondary** (must both hold):  
  - KS and/or AD p-value for lognormal is **greater** than for exponential and **above** a preset threshold (e.g. $$p_\text{ln} \ge 0.05$$), after multiple-testing correction.  
  - $$\Delta \log L > 0$$ (lognormal has higher test log-likelihood).

### 7.2 Falsification conditions

The original claim is **falsified** (for the tested ranges and banding) if **any** of the following hold:

- Across all bands in at least **two independent ranges**, fewer than **50% of bands** satisfy the "lognormal wins" criteria; i.e. exponential is competitive or better in most bands.  
- There exists a range where **exponential** systematically has **lower BIC** in ≥ 2/3 of valid bands, and this pattern remains under modest changes to banding (e.g. 4 bands instead of 6).  
- Sensitivity analysis (Section 8) reveals that the lognormal advantage disappears under small, reasonable perturbations to the methodology (e.g. alternative splits, slight band shifts), indicating the effect is not robust.

If any falsification condition is triggered, the script must:

- Explicitly report that the **lognormal > exponential** claim **failed** under this protocol.  
- Include which ranges/bands drove the failure.

## 8. Robustness and sensitivity checks

### 8.1 Alternative bandings

Repeat the full experiment with:

- Different numbers of bands (e.g. 4, 8).  
- Slightly shifted band boundaries (e.g. jitter boundaries by ±5% in $$\log_{10} p$$).

Lognormal should remain favored under these perturbations if the claim is robust.

### 8.2 Gap filters

Re-run with different gap filters:

- Exclude the smallest gaps (e.g. $$g = 2$$) and re-evaluate fits.  
- Apply upper trimming (e.g. Winsorize extreme 0.1% of gaps) to check influence of tail outliers.

### 8.3 Train/test splits and seeds

- Repeat the train/test split with multiple RNG seeds.  
- Require that **qualitative conclusions** (lognormal vs exponential dominance per range) remain stable.

## 9. Outputs

The script implementing this spec should produce:

1. **Structured machine-readable results**  
   - A JSON or CSV per run with entries:  
     - `range_id`, `band_id`, `p_min`, `p_max`  
     - `n_train`, `n_test`  
     - `lambda_hat`, `mu_hat`, `sigma_hat`  
     - `logL_exp_test`, `logL_ln_test`  
     - `AIC_exp`, `AIC_ln`, `BIC_exp`, `BIC_ln`  
     - `KS_stat_exp`, `KS_p_exp`, `KS_stat_ln`, `KS_p_ln`  
     - (optionally) `AD_stat_exp`, `AD_p_exp`, `AD_stat_ln`, `AD_p_ln`  
     - Flags for "lognormal wins", "exponential wins", "ambiguous".

2. **Human-readable summary report**  
   - Text/Markdown summary highlighting:  
     - Per-range counts of bands where lognormal/exponential wins.  
     - Whether falsification criteria were met.

3. **Optional plots** (not required for falsification, but useful)  
   - Q–Q plots of $$\ln g$$ vs normal for lognormal fit, per band.  
   - CDF plots: empirical vs model CDFs for both distributions on test data.

## 10. Implementation notes

- Language: expected to be **Python** with standard scientific stack (NumPy, SciPy, possibly statsmodels), but spec should be language-agnostic.  
- Performance: segmented sieve or precomputed primes should be used so that experiments up to at least $$10^{11}$$ are practical on a modern workstation.
- Reproducibility:  
  - All random choices (band jitter, splits) must respect a global `--seed` parameter.  
  - The spec version and parameters used must be embedded in the output metadata.
