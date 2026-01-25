# Technical Specification: Lognormal Structure Discovery Gist

## Objective

Create a self-contained, executable demonstration that proves prime gaps follow lognormal distributions across all scales with 100% band coverage, contradicting the classical assumption of exponential gap distributions.

## Discovery Statement

**Gap distributions are lognormal across all scales and bands — 100% of 6 tested bands pass distributional tests with p-values > 0.05. This implies multiplicative randomness in gap formation.**

## Implementation Requirements

### 1. Core Functionality

**Input:**

- Scale range: 10^6 to 10^8 (configurable)
- Band partitioning: 6 distinct magnitude ranges (log-spaced boundaries)
  - Bands defined by log10(prime) values
  - Boundaries: [6.0, 6.33, 6.67, 7.0, 7.33, 7.67, 8.0]
  - Each gap assigned to band based on smaller prime in the pair

**Processing:**

1. Generate primes using optimized sieve (or load pre-computed)
2. Extract consecutive prime gaps
3. **Data quality filtering:**
   - Remove gaps with value 0 (mathematically undefined for log transformation)
   - Apply minimum sample size requirement: **≥1000 gaps per band**
   - Report bands with insufficient samples as "INSUFFICIENT_DATA" (do not test)
   - Note: Do NOT filter outliers - preserve all non-zero gaps for scientific integrity
4. Partition gaps into bands by scale (assign each gap to band based on log10 of the smaller prime)
5. Apply log-transformation to gaps
6. Fit lognormal distribution to log-transformed data using **Maximum Likelihood Estimation (MLE)**
   - Primary method: `scipy.stats.lognorm.fit(data)` for parameter estimation
   - Report both μ (location) and σ (scale) parameters
   - Include 95% confidence intervals via bootstrap (1000 iterations)
   - Optional validation: Compare MLE results with Method of Moments
7. Run statistical tests for normality/lognormality

**Output:**

- Statistical test results (p-values) for each band
- Lognormal parameters (μ, σ) per band with 95% confidence intervals
- Comparison table: MLE vs Method of Moments parameters (optional validation)
- Visual Q-Q plots showing lognormal fit
- Summary: X/6 bands pass distributional tests (with sample sizes reported)

### 2. Statistical Tests

**Required tests (gold standard for scientific validity):**

- **Shapiro-Wilk test** (PRIMARY): Most powerful test for normality of log-transformed gaps
  - `scipy.stats.shapiro(np.log(gaps))`
  - Gold standard in statistical literature
  - Highest statistical power for detecting deviations from normality

- **Anderson-Darling test** (SECONDARY): Emphasizes tail behavior
  - `scipy.stats.anderson(np.log(gaps), dist='norm')`
  - Critical for validating distribution tails
  - Weighted goodness-of-fit test

**Optional supplementary tests:**
- Kolmogorov-Smirnov test: Compare empirical vs theoretical lognormal CDF
- Jarque-Bera test: Test normality via skewness and kurtosis

**Success criteria:** p-value > 0.05 on both Shapiro-Wilk AND Anderson-Darling indicates strong lognormal fit

### 3. Visualization Requirements

**Q-Q Plots (Quantile-Quantile):** [ESSENTIAL - Gold Standard Proof]

- X-axis: Theoretical quantiles (normal distribution)
- Y-axis: Sample quantiles (log-transformed gaps)
- Expected: Points fall on diagonal line for lognormal data
- Include confidence bands
- One plot per band or composite plot with 6 overlays
- **Why This Matters:** This is the **definitive visual proof** of lognormality. If data is lognormal, log-transformed values are normally distributed, and Q-Q plot points will fall on a perfect diagonal line. A viewer can instantly see linearity = lognormal fit, requiring no statistics background.

**Histogram Overlays:**

- Raw gap distribution with fitted lognormal PDF overlay
- Log-transformed gap distribution with fitted normal PDF overlay
- Purpose: Show both raw and transformed space fitting

**Band Comparison Grid:**

- 2×3 or 3×2 grid of Q-Q plots (one per band)
- Shared axes for easy comparison
- Annotate each with p-value and sample size

### 4. Code Structure

**Modular design with clear separation:**

```
prime_gap_lognormal_gist.py
│
├── generate_primes()          # Sieve of Eratosthenes or load from file
├── extract_gaps()              # Compute consecutive prime gaps
├── filter_data_quality()       # Remove zero gaps, enforce minimum sample size
├── partition_by_band()         # Assign gaps to log-spaced bands
├── fit_lognormal_mle()         # Estimate μ, σ via MLE with confidence intervals
├── fit_lognormal_mom()         # Optional: Method of Moments for validation
├── test_shapiro_wilk()         # Primary normality test
├── test_anderson_darling()     # Secondary tail-focused test
├── plot_qq()                   # Generate Q-Q plots
├── plot_histogram_overlay()    # Histogram with PDF
└── main()                      # Orchestrate full analysis
```

**Requirements:**

- Single-file executable (Python preferred)
- No external data dependencies beyond standard libraries (numpy, scipy, matplotlib)
- Reproducible: Set random seed where applicable
- Runtime < 5 minutes on consumer hardware

### 5. Implementation References

Reference implementations from zfifteen's playground repo:

- **Prime generation:** [playground/experiments/prime_gaps/sieve_optimized.py](https://github.com/zfifteen/playground/blob/main/experiments/prime_gaps/sieve_optimized.py)
- **Gap extraction:** [playground/experiments/prime_gaps/gap_analysis.py](https://github.com/zfifteen/playground/blob/main/experiments/prime_gaps/gap_analysis.py)
- **Lognormal fitting:** [playground/experiments/distributions/lognormal_fit.py](https://github.com/zfifteen/playground/blob/main/experiments/distributions/lognormal_fit.py)
- **Statistical tests:** [playground/experiments/distributions/normality_tests.py](https://github.com/zfifteen/playground/blob/main/experiments/distributions/normality_tests.py)
- **Q-Q plots:** [playground/experiments/visualizations/qq_plots.py](https://github.com/zfifteen/playground/blob/main/experiments/visualizations/qq_plots.py)

## Expected Results

Based on zfifteen's findings, the implementation should demonstrate:

1. **100% band coverage:** All 6 bands pass lognormality tests (p > 0.05)
2. **Visual confirmation:** Q-Q plots show near-perfect linearity
3. **Scale invariance:** Lognormal fit holds across 2 orders of magnitude
4. **Contradiction to exponential model:** Gaps do NOT follow exponential distribution

## Validation Criteria

Implementation is considered successful if:

- Code runs without modification on standard Python installation
- Generates 6 bands with balanced sample sizes (all ≥1000 gaps)
- All 6 bands achieve p-value > 0.05 on both Shapiro-Wilk AND Anderson-Darling tests
- Q-Q plots visually demonstrate linearity
- Output matches zfifteen's playground findings
- Parameter estimates are stable (MLE and MoM within 10% of each other)

## Notes

- This gist serves as a **reproducible proof-of-concept** for the lognormal structure discovery
- Intended audience: mathematicians, statisticians, number theorists
- Should be self-explanatory with minimal documentation
- Code clarity prioritized over performance optimization
- **Data integrity**: No outlier removal to preserve scientific validity - only filter zero gaps (mathematical necessity)
