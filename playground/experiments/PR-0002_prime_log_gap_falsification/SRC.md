# Source Code: Prime Log-Gap Falsification Experiment

This document describes the core Python scripts in the `src/` directory, which implement the experiment's computational pipeline. These modules handle prime generation, log-gap analysis, statistical tests, visualization, and autocorrelation, enabling end-to-end execution from raw primes to hypothesis evaluation. They use NumPy, SciPy, and Statsmodels for efficiency and reproducibility.

## visualization.py

Python script for generating plots of log-gap distributions, trends, and correlations.

This module defines functions to create Matplotlib-based visualizations: `plot_log_gap_histogram` for 50-bin histograms showing skewed distributions; `plot_qq_lognormal` for Q-Q plots assessing log-normal fits; `plot_decay_trend` for line plots of quintile/decile means with regression; and `plot_acf_pacf` for autocorrelation functions. It uses `plt.savefig` to save PNGs to `results/figures/`. Dependencies: NumPy, Matplotlib. Usage: Import and call `generate_all_plots(log_gaps, quintile_means, decile_means, acf, pacf)` after analysis.

[View file](src/visualization.py)

## autocorrelation.py

Python script for computing autocorrelation and partial autocorrelation of log-gaps.

This module implements time-series analysis: `ljung_box_test` performs Ljung-Box Q-test on up to 20 lags to detect non-white noise; `compute_acf` and `compute_pacf` use Statsmodels for FFT-based ACF and PACF estimation; `autocorrelation_analysis` aggregates results, identifying significant lags. It checks for short-range memory consistent with damped systems. Dependencies: NumPy, Statsmodels. Usage: Call `autocorrelation_analysis(data)` to get ACF/PACF arrays and uncorrelated flags for falsification.

[View file](src/autocorrelation.py)

## distribution_tests.py

Python script for fitting and comparing statistical distributions to log-gaps.

This module runs Kolmogorov-Smirnov tests against normal, log-normal, exponential, gamma, Weibull, and uniform distributions using SciPy's fit and kstest functions. It computes KS statistics and p-values, identifies the best fit, and extracts MLE parameters (e.g., μ, σ for log-normal). Designed to falsify normality hypotheses. Dependencies: NumPy, SciPy. Usage: `run_distribution_tests(data)` returns a dict of test results; `find_best_fit` selects the superior model (e.g., log-normal with KS=0.051).

[View file](src/distribution_tests.py)

## log_gap_analysis.py

Python script for computing prime log-gaps and statistical summaries.

This module calculates log-gaps via `np.diff(np.log(primes))` and derives basic stats (mean, std, skewness, kurtosis). It bins gaps into quintiles/deciles for trend analysis, performs linear regression on means, and computes regular gaps for comparison. Core to detecting monotonic decay. Dependencies: NumPy, SciPy. Usage: `analyze_log_gaps(primes)` returns a dict with arrays and regression results, used in `run_analysis.py` for hypothesis testing.

[View file](src/log_gap_analysis.py)

## prime_generator.py

Python script for efficient prime generation using segmented sieve.

This module implements a memory-efficient sieve: `segmented_sieve` processes large ranges in segments (default 10^6) using small primes up to sqrt(limit); `generate_primes_up_to` yields arrays of primes; `count_primes_up_to` counts without storage. Handles up to 10^8 primes in ~60 seconds. Dependencies: NumPy, math. Usage: `primes = generate_primes_up_to(1000000)` for baseline data; validated against π(x) in tests.

[View file](src/prime_generator.py)