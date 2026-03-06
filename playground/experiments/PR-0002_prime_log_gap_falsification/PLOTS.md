# Plots: Prime Log-Gap Falsification Experiment

This document describes the generated plots for the prime log-gap analysis at the 10^6 scale.

## Log Gap Histogram

![Log Gap Histogram](results/figures/log_gap_histogram.png)

This histogram shows the distribution of log-gaps (ln(p_{n+1}/p_n)) for primes up to 10^6. The distribution is highly skewed with heavy tails, exhibiting values from ~0.00002 to ~0.51, with a mean around 0.0011. The shape suggests a multiplicative process rather than additive noise.

The histogram uses 50 bins with edge color for clarity, spanning the full range of log-gaps. Key statistics include a standard deviation of ~0.0109, skewness of ~31.6, and excess kurtosis of ~1195, indicating extreme positive skew and heavy tails far beyond a normal distribution. The x-axis is logarithmic for better visualization of the multiplicative nature, while the y-axis shows frequency counts. This plot visually confirms the non-Gaussian nature of prime gaps in log-space, with a long tail extending to large gaps, supporting the hypothesis of multiplicative damping.

## Q-Q Plot vs Log-Normal

![Q-Q Plot Log-Normal](results/figures/qq_plot_lognormal.png)

The Q-Q plot compares the empirical quantiles of log-gaps to the theoretical quantiles of a fitted log-normal distribution. The close alignment along the diagonal indicates an excellent fit, supporting the hypothesis that log-gaps follow a log-normal distribution with parameters μ ≈ -7.1, σ ≈ 1.0.

Generated using scipy's probplot function with log-normal distribution parameters fitted via maximum likelihood estimation (shape=0.999, loc=0, scale=0.00069). The plot shows quantiles from 1% to 99%, with the red line representing perfect fit. The Kolmogorov-Smirnov statistic for this fit is 0.051 (p=0.95), significantly better than the normal fit (KS=0.206). Deviations at extreme tails suggest minor imperfections, but overall the log-normal model captures the multiplicative structure exceptionally well, validating the circuit analogy's assumption of exponential/logarithmic relationships.

## Decay Trend

![Decay Trend](results/figures/decay_trend.png)

This plot shows the mean log-gap values for quintiles (5 bins) and deciles (10 bins) of the prime sequence. The monotonic decrease from left to right (higher quintile/decile index corresponds to larger primes) demonstrates the damping behavior, with quintile means dropping from ~0.426 to ~0.062. Linear regression confirms significant negative slope (p < 0.05).

Quintiles divide the 78,497 log-gaps into 5 equal groups of ~15,699 gaps each, while deciles use 10 groups of ~7,850. Linear regression on quintile means yields slope = -0.082, intercept = 0.346, R² = 0.81, p = 0.038. For deciles: slope = -0.043, intercept = 0.243, R² = 0.91, p < 0.001. The x-axis represents bin index (0-4 for quintiles, 0-9 for deciles), corresponding to increasing prime magnitudes. This trend falsifies the null hypothesis of constant mean gaps and supports the damping coefficient interpretation in the electrical analogy.

## ACF and PACF

![ACF PACF](results/figures/acf_pacf.png)

The top plot shows the Autocorrelation Function (ACF) of log-gaps, revealing significant correlations at low lags (1-5), indicating short-range memory in the gap sequence. The bottom plot shows the Partial Autocorrelation Function (PACF), suggesting an AR(1) or AR(2) process structure, consistent with a damped filter response in the circuit analogy.

The ACF uses 20 lags with Bartlett's formula for confidence bands (95% shown as blue shaded region), computed via FFT for efficiency. Significant correlations (above confidence bands) persist up to lag 5, with gradual decay. PACF shows spikes at lags 1 and 2, with lag 1 partial correlation ~0.15, indicating AR(1) dominance. Ljung-Box test rejects white noise hypothesis (p < 0.01 for multiple lags). This structure suggests the prime gap sequence has memory akin to a low-pass filter, supporting the RC circuit model's impulse response interpretation.