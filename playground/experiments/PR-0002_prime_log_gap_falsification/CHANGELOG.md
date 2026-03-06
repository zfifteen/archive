# Changelog

All notable changes to the Prime Log-Gap Falsification Experiment will be documented in this file.

## [Unreleased]

### Changed
- **BREAKING**: Ljung-Box autocorrelation test is now **optional and disabled by default** due to O(n²) performance bottleneck at scale (>10^7 points). Enable with `--autocorr=ljungbox` when needed.
- Autocorrelation analysis now separated into modular components:
  - Fast ACF/PACF computation (O(n log n) via FFT) always available for descriptive analysis
  - Optional Ljung-Box omnibus test (O(n²)) disabled by default
- When Ljung-Box is disabled, falsification criterion F4 (white noise hypothesis) is marked as "not evaluated" rather than tested
- ACF/PACF plots remain available regardless of Ljung-Box setting

### Added
- New CLI interface with `--autocorr` flag supporting modes: `none` (default), `ljungbox`, `ljungbox-fixed`, `ljungbox-subsample`
- Configuration options for `--max-lag` and `--subsample-rate` to control Ljung-Box behavior when enabled
- New modular analysis package with separate ACF and Ljung-Box modules (`src/analysis/`)
- Comprehensive test suite for autocorrelation functionality with performance guards
- Documentation of performance implications and usage examples in README

### Performance
- Default configuration (--autocorr=none) achieves approximately linear scaling with dataset size
- Observed 4-5x speedup on medium datasets (n~10^4) when Ljung-Box is disabled
- Larger datasets (n>10^7) now practical without multi-hour Ljung-Box computation

### Scientific Impact
- Autocorrelation claims now require explicit opt-in via `--autocorr=ljungbox`
- Results marked clearly as "autocorrelation not evaluated" when test is disabled
- ACF/PACF descriptive statistics still available for qualitative assessment

## [Previous Versions]

### PR-0002 Initial Release
- Implemented full prime log-gap falsification experiment
- Statistical tests for decay, distribution fitting, and autocorrelation
- Visualization suite for histograms, Q-Q plots, trends, and ACF/PACF
- Falsification criteria F1-F6
