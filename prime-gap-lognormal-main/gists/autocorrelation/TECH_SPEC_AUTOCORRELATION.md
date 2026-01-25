# Technical Specification: Prime Gap Autocorrelation Discovery Gist

## Objective

Create a self-contained, executable demonstration that proves prime gaps exhibit strong autocorrelation across multiple lags and scales, contradicting the classical assumption of independent gap formation.

## Discovery Statement

**Prime gaps show statistically significant autocorrelation at multiple lags (1-50) across all tested scales. Lag-1 autocorrelation coefficients consistently exceed 0.3 with p-values < 0.001, indicating strong memory effects in gap sequences.**

## Implementation Requirements

### 1. Core Functionality

**Input:**

- Scale range: 10^6 to 10^8 (configurable)
- Band partitioning: 6 distinct magnitude ranges (log-spaced boundaries)
  - Bands defined by log10(prime) values
  - Boundaries: [6.0, 6.33, 6.67, 7.0, 7.33, 7.67, 8.0]
  - Each gap assigned to band based on smaller prime in the pair
- Lag range: 1 to 50 (maximum lag for autocorrelation computation)

**Processing:**

1. Generate primes using optimized sieve (or load pre-computed)
2. Extract consecutive prime gaps
3. **Data quality filtering:**
   - Remove gaps with value 0 (mathematically undefined for correlation analysis)
   - Apply minimum sample size requirement: **≥1000 gaps per band**
   - Report bands with insufficient samples as "INSUFFICIENT_DATA" (do not analyze)
   - Note: Do NOT filter outliers - preserve all non-zero gaps for scientific integrity
4. Partition gaps into bands by scale (assign each gap to band based on log10 of the smaller prime)
5. Compute autocorrelation function (ACF) for lags 1-50
6. Calculate statistical significance using **Ljung-Box test** and **Bartlett's formula**
   - Ljung-Box test: Joint test for autocorrelation significance across multiple lags
   - Bartlett's formula: 95% confidence bands at ±1.96/√n
**Output:**

- Autocorrelation coefficients ρ(k) for lags k=1 to 50 per band
- Statistical significance tests (p-values) from Ljung-Box test
- Comparison of ACF decay rates across bands
- Visual ACF plots with confidence bands
- Summary: Statistical significance of autocorrelation across bands

### 2. Statistical Tests

**Required tests (gold standard for autocorrelation analysis):**

- **Ljung-Box test** (PRIMARY): Tests joint significance of autocorrelations up to lag m
  - `statsmodels.stats.diagnostic.acorr_ljungbox(gaps, lags=[1,5,10,20,50])`
  - Tests null hypothesis: all autocorrelations up to lag m are zero
  - More powerful than individual lag tests
  - Returns Q-statistic and p-value for each lag

- **Bartlett's formula** (SECONDARY): Confidence bands for individual ACF coefficients
  - Standard error: SE(ρ) ≈ 1/√n under white noise assumption
  - 95% confidence band: ±1.96/√n
  - Coefficients outside band indicate statistical significance

**Optional supplementary tests:**
- Durbin-Watson test: Specific test for lag-1 autocorrelation
- Breusch-Godfrey test: More general serial correlation test
- Runs test: Non-parametric test for randomness

**Success criteria:** Ljung-Box p-value < 0.05 indicates statistically significant autocorrelation (rejection of independence hypothesis)

### 3. Visualization Requirements

**ACF Plots (Autocorrelation Function):** [ESSENTIAL - Gold Standard Proof]

- X-axis: Lag (k = 1 to 50)
- Y-axis: Autocorrelation coefficient ρ(k)
- Include 95% confidence bands (±1.96/√n horizontal lines)
- Vertical bars for each lag coefficient
- One plot per band or composite plot with 6 overlays
- **Why This Matters:** This is the **definitive visual proof** of autocorrelation. Bars extending beyond confidence bands demonstrate statistically significant correlation. A viewer can instantly see persistence = autocorrelation exists, requiring no statistics background.

**ACF Decay Comparison:**

- Overlay ACF curves from all 6 bands on single plot
- Compare decay rates across scales
- Annotate with lag-1 autocorrelation values
- Purpose: Show scale-invariance or scale-dependence of autocorrelation

**Lag-1 Heatmap:**

- Grid visualization showing lag-1 autocorrelation across bands
- Color intensity proportional to ρ(1)
- Annotate cells with exact coefficient values and p-values

**Band Comparison Grid:**

- 2×3 or 3×2 grid of ACF plots (one per band)
- Shared axes for easy comparison
- Annotate each with Ljung-Box p-value and sample size

### 4. Code Structure

**Modular design with clear separation:**

```
prime_gap_autocorrelation_gist.py
│
├── generate_primes()              # Sieve of Eratosthenes or load from file
├── extract_gaps()                  # Compute consecutive prime gaps
├── filter_data_quality()           # Remove zero gaps, enforce minimum sample size
├── partition_by_band()             # Assign gaps to log-spaced bands
├── compute_acf()                   # Calculate autocorrelation function for lags 1-50
├── compute_confidence_bands()      # Bartlett's formula: ±1.96/√n
├── ljung_box_test()                # Primary test for joint autocorrelation significance
├── durbin_watson_test()            # Optional: Lag-1 specific test
├── plot_acf()                      # Generate ACF plots with confidence bands
├── plot_acf_comparison()           # Overlay ACF curves across bands
├── plot_lag1_heatmap()             # Heatmap of lag-1 correlations
└── main()                          # Orchestrate full analysis
```

**Requirements:**

- Single-file executable (Python preferred)
- No external data dependencies beyond standard libraries (numpy, scipy, matplotlib, statsmodels)
- Reproducible: Set random seed where applicable
- Runtime < 5 minutes on consumer hardware

### 5. Implementation References

Reference implementations from zfifteen's playground repo:

- **Prime generation:** [playground/experiments/prime_gaps/sieve_optimized.py](https://github.com/zfifteen/playground/blob/main/experiments/prime_gaps/sieve_optimized.py)
- **Gap extraction:** [playground/experiments/prime_gaps/gap_analysis.py](https://github.com/zfifteen/playground/blob/main/experiments/prime_gaps/gap_analysis.py)
- **Autocorrelation computation:** [playground/experiments/time_series/acf_computation.py](https://github.com/zfifteen/playground/blob/main/experiments/time_series/acf_computation.py)
- **Ljung-Box test:** [playground/experiments/time_series/ljung_box.py](https://github.com/zfifteen/playground/blob/main/experiments/time_series/ljung_box.py)
- **ACF plots:** [playground/experiments/visualizations/acf_plots.py](https://github.com/zfifteen/playground/blob/main/experiments/visualizations/acf_plots.py)

## Expected Results

Based on zfifteen's findings, the implementation should demonstrate:

1. **Significant lag-1 autocorrelation:** All 6 bands show ρ(1) > 0.3 with p < 0.001
2. **Multi-lag persistence:** Significant autocorrelation extends to lags 5-20 in most bands
3. **Slow decay:** ACF decays gradually rather than dropping immediately to zero
4. **Scale consistency:** Autocorrelation pattern consistent across 2 orders of magnitude
5. **Contradiction to independence assumption:** Gaps are NOT independently distributed

## Validation Criteria

Implementation is considered successful if:

- Code runs without modification on standard Python installation
- Generates 6 bands with balanced sample sizes (all ≥1000 gaps)
- All 6 bands achieve Ljung-Box p-value < 0.05 at lag-10
- Lag-1 autocorrelation ρ(1) > 0.25 for at least 5 of 6 bands
- ACF plots visually demonstrate coefficients exceeding confidence bands
- Output matches zfifteen's playground findings
- Results are numerically stable across multiple runs

## Notes

- This gist serves as a **reproducible proof-of-concept** for the autocorrelation discovery
- Intended audience: mathematicians, statisticians, time series analysts, number theorists
- Should be self-explanatory with minimal documentation
- Code clarity prioritized over performance optimization
- **Data integrity**: No outlier removal to preserve scientific validity - only filter zero gaps (mathematical necessity)
- **Interpretation**: Autocorrelation in gap sequences suggests **memory effects** in prime distribution, contradicting classical probabilistic models that assume independent gap formation
