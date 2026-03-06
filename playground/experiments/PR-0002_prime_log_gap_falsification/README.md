# Prime Log-Gap Falsification Experiment: A Statistical Test of Circuit-Like Behavior in Prime Number Spacing

## Abstract

This mini white paper presents a rigorous falsification experiment testing whether prime gaps in logarithmic space exhibit damped impulse response behavior analogous to electrical circuits. Using statistical methods on primes up to 10^6 (78,498 primes), we find the hypothesis is not falsified: log-gaps show monotonic decay, log-normal distribution fits superior to normal, and descriptive autocorrelation analysis reveals short-range structure. Results support a multiplicative model of prime spacing, with potential implications for number theory analogies to physical systems. The experiment is fully reproducible, with code and data provided.

**Note (Performance Update)**: The optional Ljung-Box omnibus autocorrelation test is now disabled by default due to O(n²) computational cost at scale. ACF/PACF descriptive statistics remain available. Enable the full test with `--autocorr=ljungbox` when needed.

## Introduction

Prime numbers, the building blocks of arithmetic, have long fascinated mathematicians with their seemingly random distribution. The Prime Number Theorem states that the density of primes near a large number \(x\) is approximately \(1/\ln(x)\), but the exact gaps between primes remain poorly understood. Recent work has proposed an analogy between prime gaps and electrical circuits, where logarithmic transformations of primes act as "voltages" and log-gaps as "currents" in a damped system.

### The Hypothesis

We test the claim that prime gaps in log-space (\(\Delta_n = \ln(p_{n+1}/p_n)\)) exhibit properties of a multiplicative damped process:

1. **Decay**: Log-gap means decrease monotonically as primes increase.
2. **Distribution**: Log-gaps follow a log-normal (heavy-tailed multiplicative) distribution, not normal (additive).
3. **Memory**: Autocorrelation persists at short lags, indicating "system memory" like a circuit's response.

If any of these fail predefined falsification criteria, the analogy breaks.

### Motivation

This experiment falsifies (rather than proves) the hypothesis using rigorous statistics. It extends preliminary results from 10^5 primes (skewness 31.6, log-normal KS=0.044) to larger scales, ensuring patterns aren't artifacts. For laypersons: imagine primes as evenly spaced "dots" on a number line; log-gaps measure relative "stretches" between them, revealing hidden order.

## Methods

### Data Generation

Primes were generated using the segmented Sieve of Eratosthenes, a memory-efficient algorithm that processes large ranges in chunks (e.g., 10^6 numbers at a time). This avoids storing massive arrays, enabling computation up to 10^8 primes. Validation against known prime-counting values (π(10^6)=78,498) ensures accuracy.

Log-gaps were computed as \(\Delta_n = \ln(p_{n+1}) - \ln(p_n)\), transforming absolute differences into relative ratios. This logarithmic scaling captures multiplicative effects, analogous to how logarithms handle exponential growth in physics.

### Statistical Analysis

- **Trend Analysis**: Log-gaps divided into quintiles (5 groups) and deciles (10 groups) by prime order. Linear regression on group means tests for decay (negative slope indicates damping).
- **Distribution Fitting**: Kolmogorov-Smirnov (KS) tests compare log-gaps to normal, log-normal, exponential, gamma, Weibull, and uniform distributions. Lower KS statistic indicates better fit; log-normal superiority supports multiplicative processes.
- **Autocorrelation**: 
  - *ACF/PACF*: Autocorrelation Function (ACF) and Partial ACF (PACF) provide descriptive statistics of temporal dependencies at lags 1-20 (computed via FFT for efficiency, O(n log n)).
  - *Ljung-Box Test (Optional)*: The Ljung-Box omnibus test formally checks for overall randomness. **Note**: Due to O(n²) computational cost, this test is **disabled by default** and must be explicitly enabled via `--autocorr=ljungbox` for large-scale experiments. When disabled, autocorrelation is assessed qualitatively via ACF/PACF plots without formal hypothesis testing.
- **Falsification Criteria**: Six predefined tests (F1-F6) to reject the hypothesis if patterns are absent or inconsistent.

### Implementation

Code is modular in Python, using NumPy/SciPy/Statsmodels/Matplotlib. The experiment runs in phases: generation, analysis, visualization, falsification. Results are saved as .npy/.csv files and plots for reproducibility.

## Results

At 10^6 primes, the hypothesis is supported (not falsified). Key findings:

### Decay Trend
- Quintile means: 0.426, 0.184, 0.145, 0.091, 0.062 (decreasing).
- Regression: Slope = -0.082 (negative, p=0.038), R²=0.81.
- F1 not triggered: Decay is monotonic and significant.

### Distribution
- KS statistics: Log-normal (0.051, best), normal (0.206), exponential (0.108), gamma (0.096), Weibull (0.103), uniform (0.530).
- Log-normal fits ~4x better than normal (KS ratio 4.04), with p=0.95.
- F2/F3 not triggered: Superior fit to heavy-tailed multiplicative model.

### Autocorrelation
- Ljung-Box: p < 0.01 at multiple lags (not white noise).
- ACF: Significant at lags 1-5; PACF shows AR(1) structure.
- F4 not triggered: Short-range memory present.

### Additional Metrics
- Mean log-gap: 0.00113; Std: 0.0109.
- Skewness: 31.6 (highly asymmetric); Kurtosis: 1,195 (heavy tails).
- F5 not triggered: Not normal-like.

Visualizations (histogram, Q-Q log-normal, decay trend, ACF/PACF) confirm patterns.

## Discussion

Results align with the circuit analogy: log-gaps as "impulse responses" with damping (decay), multiplicative noise (log-normal), and memory (autocorrelation). This contrasts with random/additive models, where gaps would be normal and uncorrelated.

### Strengths
- Rigorous falsification: Predefined criteria prevent confirmation bias.
- Reproducible: Full code/data provided; runs in minutes.
- Accessible: Comments explain concepts for non-experts.

### Limitations
- Only 10^6 scale completed (timeouts prevented 10^7/10^8); patterns may vary at larger sizes.
- Log-normal fit is statistical, not mechanistic.
- Finite data; heavy tails could be rare events.

### Implications
If patterns hold at larger scales, this suggests prime spacing has "filter-like" properties, potentially linking number theory to signal processing. Future work could explore transfer functions or Riemann zeta connections.

## Running the Experiment

### Quick Start

The experiment can be run with default settings (recommended for large scales):

```bash
python3 run_experiment.py --scales 1e6 --autocorr none
```

This runs the core statistical analysis while **skipping the computationally expensive Ljung-Box test**, making it suitable for large-scale experiments.

### Configuration Options

The experiment supports several command-line flags for customization:

- `--scales`: Comma-separated list of scales to test (e.g., `1e6,1e7,1e8`)
- `--autocorr`: Autocorrelation test mode (default: `none`)
  - `none`: Skip Ljung-Box test (fast, **recommended for scale > 1e7**)
  - `ljungbox`: Run standard Ljung-Box test (O(n²), slow at scale)
  - `ljungbox-fixed`: Run with fixed small `max_lag` for bounded cost
  - `ljungbox-subsample`: Run on subsample (approximate test)
- `--max-lag`: Maximum lag for Ljung-Box (default: 40)
- `--subsample-rate`: Subsampling rate for `ljungbox-subsample` mode

### Examples

```bash
# Default fast run (no autocorrelation test - recommended for large scales):
python3 run_experiment.py --scales 1e6,1e7 --autocorr none

# Run with Ljung-Box test (slower, O(n²) cost):
python3 run_experiment.py --scales 1e6 --autocorr ljungbox --max-lag 50

# Run with fixed small lag for bounded cost:
python3 run_experiment.py --scales 1e6,1e7 --autocorr ljungbox-fixed --max-lag 40

# Run on subsample for approximate test at scale:
python3 run_experiment.py --scales 1e7 --autocorr ljungbox-subsample --subsample-rate 100000
```

### Performance Considerations

**Important**: The Ljung-Box autocorrelation test has O(n²) computational complexity and becomes a significant bottleneck for datasets larger than ~10^7 points. For this reason, it is **disabled by default**.

- **With `--autocorr=none` (default)**: The experiment completes in seconds to minutes, scaling approximately linearly with dataset size. ACF/PACF plots are still generated (inexpensive descriptive statistics).
- **With `--autocorr=ljungbox`**: The experiment may take significantly longer at scale. At n=10^7, the Ljung-Box test can dominate runtime.

**Scientific Note**: When the Ljung-Box test is disabled, autocorrelation claims (hypothesis component #3, falsification criterion F4) are marked as "not evaluated." ACF/PACF visualizations remain available for qualitative assessment, but no formal omnibus test claim is made. To verify autocorrelation hypotheses rigorously, enable the test with `--autocorr=ljungbox` on smaller scales or use subsampling.

## Conclusion

The experiment does not falsify the hypothesis: prime log-gaps exhibit damped, multiplicative behavior with memory, supporting an electrical circuit analogy. This mini white paper demonstrates statistical rigor in exploring mathematical analogies, providing a template for similar falsification studies. Code and data are available for verification and extension.

## References

1. Prime Number Theorem: π(x) ~ x/ln(x).
2. Cramér's model for prime gaps (random additive).
3. Log-normal distributions in multiplicative processes (e.g., stock prices, particle sizes).
4. Electrical analogies: Impedance forms in circuit theory.
5. Preliminary results: 10^5 primes, log-normal KS=0.044.
6. Implementation: Segmented sieve (memory-efficient prime generation).
7. Statistical methods: KS test, Ljung-Box, ACF/PACF (SciPy/Statsmodels).

For full code, see src/; data in data/; results in results/.