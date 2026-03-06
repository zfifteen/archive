"""
Autocorrelation Analysis Module

This module checks if log-gaps have "memory" – do past gaps influence future ones?
In circuits, components like capacitors store charge, creating echoes (autocorrelation).
If prime gaps behave similarly, it supports the damped system analogy.

We use:
- Ljung-Box test: Formal check for overall correlation (like asking if data is truly random).
- ACF (Autocorrelation Function): Measures direct correlations at different lags (delays).
- PACF (Partial Autocorrelation): Isolates direct vs. indirect influences.

Results help falsify: if gaps are uncorrelated (white noise), the hypothesis fails.
"""

import numpy as np
from statsmodels.stats.diagnostic import acorr_ljungbox  # Ljung-Box test
from statsmodels.tsa.stattools import acf, pacf  # ACF and PACF
import warnings


def ljung_box_test(data: np.ndarray, lags: int = 20):
    """
    Ljung-Box test: Check if the sequence is uncorrelated (random) up to given lags.

    Imagine testing if yesterday's weather predicts tomorrow's – but for gaps.
    It sums squared autocorrelations and compares to chi-squared distribution.
    High p-value (>0.05) means "no correlation detected" – data looks random.
    In our case, if p-values are low, gaps have memory, like a circuit's response.
    """
    lb_df = acorr_ljungbox(data, lags=lags, return_df=True)  # Compute test stats
    results = {}
    for lag in range(1, lags + 1):
        lb_stat = lb_df.loc[lag, "lb_stat"]  # Test statistic for this lag
        p_value = lb_df.loc[lag, "lb_pvalue"]  # Probability of false alarm
        results[f"lag_{lag}"] = {"lb_stat": lb_stat, "p_value": p_value}
    # Check if all lags show no correlation (p > 0.05)
    all_uncorrelated = all(res["p_value"] > 0.05 for res in results.values())
    return results, all_uncorrelated  # Dict of results, boolean summary


def compute_acf(data: np.ndarray, nlags: int = 20):
    """
    Autocorrelation Function (ACF): How much does a gap correlate with itself at delays?

    Like: Is gap N related to gap N-1, N-2, etc.?
    Values near 1.0 mean strong positive correlation; near -1.0 negative; 0 none.
    Uses FFT for speed on large data. Suppresses warnings for numerical issues.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Ignore minor warnings
        acf_values = acf(data, nlags=nlags, fft=True)  # Compute correlations
    return acf_values  # Array: lag 0 (always 1.0), lag 1, etc.


def compute_pacf(data: np.ndarray, nlags: int = 20):
    """
    Partial Autocorrelation Function (PACF): Direct correlation at each lag, removing intermediates.

    ACF includes indirect effects (e.g., lag 2 via lag 1), but PACF isolates direct ones.
    Helps identify AR (autoregressive) patterns, like AR(1) for simple memory.
    In circuits, this might reveal the "filter order" of the prime gap system.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pacf_values = pacf(data, nlags=nlags)  # Compute partials
    return pacf_values


def autocorrelation_analysis(data: np.ndarray, lags: int = 20):
    """
    Complete analysis of temporal dependencies in log-gaps.

    Runs Ljung-Box for overall randomness, ACF for direct correlations, PACF for structure.
    Identifies lags with strong correlations (threshold |corr| > 0.1).
    If significant lags exist, gaps have memory – supporting circuit-like behavior.
    Returns dict for plotting and falsification checks.
    """
    lb_results, all_uncorrelated = ljung_box_test(data, lags)  # Test for randomness
    acf_values = compute_acf(data, lags)  # Correlation strengths
    pacf_values = compute_pacf(data, lags)  # Direct influences

    # Find lags with notable correlations (above rough threshold)
    significant_acf = [i for i in range(1, len(acf_values)) if abs(acf_values[i]) > 0.1]
    significant_pacf = [
        i for i in range(1, len(pacf_values)) if abs(pacf_values[i]) > 0.1
    ]

    analysis = {
        "ljung_box": lb_results,  # Detailed test results
        "all_uncorrelated": all_uncorrelated,  # Boolean: is it white noise?
        "acf": acf_values,  # Correlation array
        "pacf": pacf_values,  # Partial correlation array
        "significant_acf_lags": significant_acf,  # Lags with strong ACF
        "significant_pacf_lags": significant_pacf,  # Lags with strong PACF
    }
    return analysis


def compute_autocorrelation_analysis(
    data: np.ndarray,
    nlags: int = 20,
    run_ljungbox: bool = True,
    max_lag: int = None,
    subsample: int = None,
    seed: int = None
):
    """
    Wrapper function for autocorrelation analysis with optional Ljung-Box test.
    
    This function provides the interface expected by run_experiment.py and makes
    the Ljung-Box test optional. By default, Ljung-Box is enabled for backward
    compatibility, but it should be disabled at scale for performance.
    
    Args:
        data: Time series data (e.g., log-gaps)
        nlags: Number of lags for ACF/PACF (default: 20)
        run_ljungbox: Whether to run the O(n²) Ljung-Box test (default: True for compatibility)
        max_lag: Maximum lag for Ljung-Box if enabled (default: nlags)
        subsample: If set, subsample data for Ljung-Box test (approximate)
        seed: Random seed for reproducible subsampling
        
    Returns:
        Dictionary with analysis results compatible with run_experiment.py
    """
    if max_lag is None:
        max_lag = nlags
    
    # Always compute ACF/PACF (inexpensive, descriptive)
    acf_values = compute_acf(data, nlags)
    pacf_values = compute_pacf(data, nlags)
    
    # Find significant lags in ACF
    significant_lags = [i for i in range(1, len(acf_values)) if abs(acf_values[i]) > 0.1]
    
    # Check for short-range structure (lags 1-5)
    has_short_range_structure = any(abs(acf_values[i]) > 0.1 for i in range(1, min(6, len(acf_values))))
    
    # Conditionally run Ljung-Box test (O(n²) bottleneck)
    if run_ljungbox:
        lb_results, all_uncorrelated = ljung_box_test(data, max_lag)
        ljungbox_all_p_above_005 = all_uncorrelated
        f4_falsified = all_uncorrelated  # F4: white noise hypothesis
        ljungbox_status = "evaluated"
    else:
        # Ljung-Box disabled - mark as not evaluated
        lb_results = None
        ljungbox_all_p_above_005 = None
        f4_falsified = None
        ljungbox_status = "not_evaluated"
    
    return {
        'nlags': nlags,
        'acf': acf_values,
        'pacf': pacf_values,
        'significant_lags': significant_lags,
        'has_short_range_structure': has_short_range_structure,
        'ljungbox_all_p_above_005': ljungbox_all_p_above_005,
        'f4_falsified': f4_falsified,
        'ljungbox_status': ljungbox_status,
        'ljungbox_results': lb_results  # Full results if enabled, None otherwise
    }


if __name__ == "__main__":
    # Test with random (uncorrelated) data – should show no memory
    np.random.seed(42)  # Reproducible
    data = np.random.randn(100)  # Normal random data (no autocorrelation)
    
    # Test new wrapper with Ljung-Box enabled
    print("Test 1: With Ljung-Box enabled (backward compatible)")
    analysis = compute_autocorrelation_analysis(data, nlags=20, run_ljungbox=True)
    print("  Ljung-Box status:", analysis["ljungbox_status"])
    print("  Ljung-Box all p > 0.05:", analysis["ljungbox_all_p_above_005"])
    print("  Significant ACF lags:", analysis["significant_lags"])
    
    # Test new wrapper with Ljung-Box disabled
    print("\nTest 2: With Ljung-Box disabled (default for scale)")
    analysis_fast = compute_autocorrelation_analysis(data, nlags=20, run_ljungbox=False)
    print("  Ljung-Box status:", analysis_fast["ljungbox_status"])
    print("  Ljung-Box result:", analysis_fast["ljungbox_all_p_above_005"])
    print("  Significant ACF lags:", analysis_fast["significant_lags"])
    print("  Has short-range structure:", analysis_fast["has_short_range_structure"])
    
    # Test old function for backward compatibility
    print("\nTest 3: Old autocorrelation_analysis function")
    analysis_old = autocorrelation_analysis(data)
    print("  All uncorrelated:", analysis_old["all_uncorrelated"])
    print("  Significant ACF lags:", analysis_old["significant_acf_lags"])
