"""
FFT-based Autocorrelation Analysis Module

This module provides efficient O(n log n) computation of ACF and PACF
using FFT, separated from the O(n²) Ljung-Box test for performance.

ACF (Autocorrelation Function) and PACF (Partial Autocorrelation Function)
are inexpensive descriptive statistics that help visualize temporal patterns.
They remain available regardless of whether the Ljung-Box test is enabled.
"""

import numpy as np
from statsmodels.tsa.stattools import acf, pacf
import warnings


def compute_acf_fft(data: np.ndarray, nlags: int = 20) -> np.ndarray:
    """
    Compute Autocorrelation Function using FFT (fast, O(n log n)).
    
    ACF measures how much a gap correlates with itself at different delays.
    Values near 1.0 indicate strong positive correlation; near -1.0 negative; 0 none.
    
    Args:
        data: Time series data (e.g., log-gaps)
        nlags: Number of lags to compute (default: 20)
        
    Returns:
        Array of ACF values at lags 0 through nlags
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        acf_values = acf(data, nlags=nlags, fft=True)
    return acf_values


def compute_pacf_yw(data: np.ndarray, nlags: int = 20) -> np.ndarray:
    """
    Compute Partial Autocorrelation Function using Yule-Walker method.
    
    PACF isolates direct correlations at each lag, removing indirect effects.
    Helps identify AR (autoregressive) patterns like AR(1).
    
    Args:
        data: Time series data (e.g., log-gaps)
        nlags: Number of lags to compute (default: 20)
        
    Returns:
        Array of PACF values at lags 0 through nlags
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pacf_values = pacf(data, nlags=nlags)
    return pacf_values


def identify_significant_lags(acf_values: np.ndarray, threshold: float = 0.1) -> list:
    """
    Find lags with notable autocorrelation above a threshold.
    
    Args:
        acf_values: Array of ACF values
        threshold: Minimum absolute correlation to consider significant (default: 0.1)
        
    Returns:
        List of lag indices with |ACF| > threshold (excluding lag 0)
    """
    significant = [i for i in range(1, len(acf_values)) if abs(acf_values[i]) > threshold]
    return significant


def check_short_range_structure(acf_values: np.ndarray, max_short_lag: int = 5, threshold: float = 0.1) -> bool:
    """
    Check if there's significant autocorrelation in short-range lags (1-5).
    
    Args:
        acf_values: Array of ACF values
        max_short_lag: Maximum lag to consider as "short-range" (default: 5)
        threshold: Minimum absolute correlation to consider significant (default: 0.1)
        
    Returns:
        True if any short-range lag has |ACF| > threshold
    """
    for i in range(1, min(max_short_lag + 1, len(acf_values))):
        if abs(acf_values[i]) > threshold:
            return True
    return False


if __name__ == "__main__":
    # Test with random (uncorrelated) data
    np.random.seed(42)
    data = np.random.randn(1000)
    
    acf_vals = compute_acf_fft(data, nlags=20)
    pacf_vals = compute_pacf_yw(data, nlags=20)
    sig_lags = identify_significant_lags(acf_vals)
    has_structure = check_short_range_structure(acf_vals)
    
    print(f"ACF values: {acf_vals[:5]}")
    print(f"PACF values: {pacf_vals[:5]}")
    print(f"Significant lags: {sig_lags}")
    print(f"Has short-range structure: {has_structure}")
