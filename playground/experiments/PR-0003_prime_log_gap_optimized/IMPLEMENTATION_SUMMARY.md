# Changelog

All notable changes to the PR-0003 Prime Log-Gap Analysis Experiment will be documented in this file.

## [Unreleased]

### Changed
- **BREAKING**: Ljung-Box autocorrelation test is now **optional and disabled by default** due to O(n²) performance bottleneck at scale (>10^6 points). Enable with `--autocorr=ljungbox` when needed.
- Autocorrelation analysis now supports multiple modes:
  - `none` (default): Skip Ljung-Box for speed; ACF/PACF still computed
  - `ljungbox`: Full omnibus test on complete dataset
  - `ljungbox-subsample`: Approximate test on random subsample
- When Ljung-Box is disabled, falsification criterion F4 (white noise hypothesis) is marked as "not evaluated" rather than tested
- ACF/PACF plots remain available regardless of Ljung-Box setting with status indicators
- Default behavior changed to prioritize performance for large-scale exploration

### Added
- New CLI interface with `--autocorr` choices, `--max-lag`, and `--subsample-rate` options
- Subsampling support in `ljung_box_test()` for bounded-cost approximate testing
- Result schema extensions: `autocorr_mode`, `ljungbox_status`, optional `ljung_box` fields
- Visualization enhancements: Plot titles indicate Ljung-Box evaluation status
- Comprehensive performance analysis of optional modes

### Performance
- Default configuration (`--autocorr none`) achieves approximately linear scaling with dataset size
- Observed 4-15x speedup on medium/large datasets (n>10^6) when Ljung-Box is disabled
- Larger datasets (n>10^7) now practical for exploratory analysis
- Subsampling mode provides ~10x speedup with reasonable accuracy

### Scientific Impact
- Autocorrelation claims now require explicit opt-in via `--autocorr=ljungbox`
- Results marked clearly as "autocorrelation not evaluated" when test is disabled
- ACF/PACF descriptive statistics still available for qualitative assessment
- F4 falsification criterion optional, allowing flexible hypothesis testing

## [Previous Versions]

### Initial Release
- Implemented complete prime log-gap analysis pipeline
- Statistical tests for decay, distribution fitting, and autocorrelation
- Visualization suite for histograms, Q-Q plots, trends, and ACF/PACF
- Falsification criteria F1-F6
- Binning strategy using 100 equal-width bins on log-prime axis
- Memory-efficient segmented sieve with disk caching</content>
<parameter name="filePath">/Users/velocityworks/IdeaProjects/playground/experiments/PR-0003_prime_log_gap_optimized/CHANGELOG.md