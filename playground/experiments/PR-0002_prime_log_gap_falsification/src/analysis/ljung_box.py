"""
Ljung-Box Omnibus Autocorrelation Test Module

This module provides the optional O(n²) Ljung-Box test for omnibus
autocorrelation testing. Due to its computational cost, this test is
DISABLED by default and must be explicitly enabled via configuration.

The Ljung-Box test checks if a time series is uncorrelated (white noise)
by summing squared autocorrelations across multiple lags. At large scales
(n > 1e7), this becomes a performance bottleneck.

When disabled, ACF/PACF plots remain available as descriptive statistics,
but no formal omnibus test claim is made.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional
from statsmodels.stats.diagnostic import acorr_ljungbox


@dataclass
class LjungBoxResult:
    """
    Result container for Ljung-Box test.
    
    Attributes:
        lags: List of lag values tested
        q_stat: Ljung-Box Q-statistics at each lag
        p_values: P-values at each lag (low p-value = reject null of no correlation)
        n_eff: Effective sample size used
        method: Method used for ACF computation (e.g., "fft_acf")
        notes: Additional notes about the test (e.g., subsampling applied)
    """
    lags: list
    q_stat: np.ndarray
    p_values: np.ndarray
    n_eff: int
    method: str
    notes: str = ""


def run_ljung_box(
    series: np.ndarray,
    max_lag: int = 40,
    method: str = "fft_acf",
    subsample: Optional[int] = None,
    seed: Optional[int] = None
) -> LjungBoxResult:
    """
    Run Ljung-Box autocorrelation test.
    
    The Ljung-Box test checks if a time series exhibits significant autocorrelation
    by testing the null hypothesis that all autocorrelations up to lag k are zero.
    
    WARNING: This is an O(n²) operation for large n and can be a performance bottleneck.
    Use with caution on datasets > 1e7 points.
    
    Args:
        series: Time series data (e.g., log-gaps)
        max_lag: Maximum lag to test (default: 40). Higher values increase cost.
        method: ACF computation method (default: "fft_acf"). Currently fixed to FFT.
        subsample: If set, randomly sample this many points before testing (reduces cost)
        seed: Random seed for reproducible subsampling
        
    Returns:
        LjungBoxResult with test statistics and metadata
        
    Examples:
        # Standard test on full data
        result = run_ljung_box(log_gaps, max_lag=40)
        
        # Approximate test on subsample for large datasets
        result = run_ljung_box(log_gaps, max_lag=40, subsample=100000, seed=42)
    """
    # Apply subsampling if requested
    if subsample is not None and len(series) > subsample:
        if seed is not None:
            np.random.seed(seed)
        indices = np.random.choice(len(series), subsample, replace=False)
        test_series = series[indices]
        notes = f"Subsampled {subsample} points from {len(series)} (approximate test)"
    else:
        test_series = series
        notes = "Full dataset"
    
    n_eff = len(test_series)
    
    # Run Ljung-Box test
    # The test computes Q-statistics and p-values for lags 1 through max_lag
    lb_df = acorr_ljungbox(test_series, lags=max_lag, return_df=True)
    
    lags = list(range(1, max_lag + 1))
    q_stat = lb_df["lb_stat"].values
    p_values = lb_df["lb_pvalue"].values
    
    return LjungBoxResult(
        lags=lags,
        q_stat=q_stat,
        p_values=p_values,
        n_eff=n_eff,
        method=method,
        notes=notes
    )


def ljung_box_all_uncorrelated(result: LjungBoxResult, alpha: float = 0.05) -> bool:
    """
    Check if Ljung-Box test indicates no significant autocorrelation.
    
    Args:
        result: LjungBoxResult from run_ljung_box
        alpha: Significance level (default: 0.05)
        
    Returns:
        True if all p-values > alpha (fail to reject null of white noise)
    """
    return all(p > alpha for p in result.p_values)


def ljung_box_summary(result: LjungBoxResult, alpha: float = 0.05) -> dict:
    """
    Generate a summary of Ljung-Box test results.
    
    Args:
        result: LjungBoxResult from run_ljung_box
        alpha: Significance level (default: 0.05)
        
    Returns:
        Dictionary with summary statistics
    """
    significant_lags = [lag for lag, p in zip(result.lags, result.p_values) if p < alpha]
    all_uncorrelated = len(significant_lags) == 0
    
    return {
        'all_uncorrelated': all_uncorrelated,
        'significant_lags': significant_lags,
        'min_p_value': float(np.min(result.p_values)),
        'max_p_value': float(np.max(result.p_values)),
        'n_effective': result.n_eff,
        'method': result.method,
        'notes': result.notes
    }


if __name__ == "__main__":
    # Test with random (uncorrelated) data - should show high p-values
    print("Testing Ljung-Box with white noise (should NOT reject null):")
    np.random.seed(42)
    data = np.random.randn(1000)
    result = run_ljung_box(data, max_lag=20)
    summary = ljung_box_summary(result)
    print(f"  All uncorrelated: {summary['all_uncorrelated']}")
    print(f"  Significant lags: {summary['significant_lags']}")
    print(f"  Min p-value: {summary['min_p_value']:.4f}")
    
    # Test with AR(1) data - should show low p-values
    print("\nTesting Ljung-Box with AR(1) data (should reject null):")
    ar1_data = np.zeros(1000)
    ar1_data[0] = np.random.randn()
    for i in range(1, 1000):
        ar1_data[i] = 0.7 * ar1_data[i-1] + np.random.randn()
    result_ar1 = run_ljung_box(ar1_data, max_lag=20)
    summary_ar1 = ljung_box_summary(result_ar1)
    print(f"  All uncorrelated: {summary_ar1['all_uncorrelated']}")
    print(f"  Significant lags: {summary_ar1['significant_lags'][:5]}...")
    print(f"  Min p-value: {summary_ar1['min_p_value']:.4e}")
