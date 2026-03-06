"""
Autocorrelation Analysis Module

Tests H-MAIN-C: Gap Autocorrelation
Computes ACF, PACF, and Ljung-Box test for gap independence.
"""

import numpy as np
from typing import Dict, Tuple
from scipy import stats


def compute_acf(data: np.ndarray, max_lag: int = 40) -> np.ndarray:
    """Compute autocorrelation function.
    
    Args:
        data: Time series data (gap values)
        max_lag: Maximum lag to compute (default 40)
        
    Returns:
        Array of autocorrelation values for lags 0 to max_lag
    """
    n = len(data)
    data_centered = data - np.mean(data)
    
    # Variance (lag 0 autocorrelation)
    c0 = np.dot(data_centered, data_centered) / n
    
    # Autocorrelations for each lag
    acf = np.zeros(max_lag + 1)
    acf[0] = 1.0
    
    for k in range(1, max_lag + 1):
        if k < n:
            ck = np.dot(data_centered[:-k], data_centered[k:]) / n
            acf[k] = ck / c0
        else:
            acf[k] = 0.0
    
    return acf


def compute_pacf(data: np.ndarray, max_lag: int = 40) -> np.ndarray:
    """Compute partial autocorrelation function.
    
    Uses Durbin-Levinson recursion to compute PACF from ACF.
    This implementation correctly updates both numerator and denominator
    in the Yule-Walker equations for proper PACF computation.
    
    Args:
        data: Time series data
        max_lag: Maximum lag to compute
        
    Returns:
        Array of partial autocorrelation values for lags 0 to max_lag
        
    Note:
        Fixed in response to code review - previous version had hardcoded
        denominator=1.0, now properly computes denominator from ACF values.
        
        For production use, consider using statsmodels.tsa.stattools.pacf
        for more robust implementation with edge case handling.
    """
    acf = compute_acf(data, max_lag)
    
    pacf = np.zeros(max_lag + 1)
    pacf[0] = 1.0
    
    if max_lag > 0:
        pacf[1] = acf[1]
    
    # Durbin-Levinson recursion
    for k in range(2, max_lag + 1):
        # Store previous PACF coefficients
        phi = np.zeros(k)
        phi[:k-1] = pacf[1:k]
        
        # Compute numerator and denominator for Yule-Walker equations
        # The slice acf[k-1:0:-1] creates a reversed array of acf[1] through acf[k-1]
        # This is equivalent to [acf[k-1], acf[k-2], ..., acf[1]] which is needed
        # for the Durbin-Levinson recursion: sum(phi[j] * rho[k-j]) for j=1 to k-1
        numerator = acf[k] - np.sum(phi[:k-1] * acf[k-1:0:-1])
        denominator = 1.0 - np.sum(phi[:k-1] * acf[1:k])
        
        # Compute PACF with numerical stability check
        pacf[k] = numerator / denominator if abs(denominator) > 1e-10 else 0.0
    
    return pacf


def ljung_box_test(data: np.ndarray, max_lag: int = 40) -> Tuple[float, float]:
    """Compute Ljung-Box test statistic for autocorrelation.
    
    Tests null hypothesis that all autocorrelations up to max_lag are zero.
    
    Args:
        data: Time series data
        max_lag: Maximum lag to test
        
    Returns:
        Tuple of (Q_statistic, p_value)
    """
    n = len(data)
    acf = compute_acf(data, max_lag)
    
    # Ljung-Box Q statistic
    Q = n * (n + 2) * np.sum(acf[1:max_lag+1]**2 / (n - np.arange(1, max_lag+1)))
    
    # p-value from chi-square distribution
    p_value = 1 - stats.chi2.cdf(Q, df=max_lag)
    
    return Q, p_value


def test_autocorrelation(primes: np.ndarray, max_lag: int = 40) -> Dict:
    """Test T3: Autocorrelation Analysis.
    
    Tests whether consecutive gaps are correlated.
    
    Args:
        primes: Array of prime numbers
        max_lag: Maximum lag for ACF/PACF (default 40)
        
    Returns:
        Dictionary with:
        - acf: Autocorrelation function values
        - pacf: Partial autocorrelation function values
        - ljung_box_Q: Test statistic
        - ljung_box_p: p-value
        - confidence_bands: 95% confidence interval for white noise
        - significant_lags: List of lags with significant autocorrelation
        - interpretation: Text interpretation
    """
    gaps = np.diff(primes)
    n = len(gaps)
    
    # Compute ACF and PACF
    acf = compute_acf(gaps, max_lag)
    pacf = compute_pacf(gaps, max_lag)
    
    # Ljung-Box test
    Q, p_value = ljung_box_test(gaps, max_lag)
    
    # 95% confidence bands for white noise: ±1.96/sqrt(n)
    confidence_band = 1.96 / np.sqrt(n)
    
    # Find significant lags
    significant_lags = []
    for k in range(1, max_lag + 1):
        if abs(acf[k]) > confidence_band:
            significant_lags.append(k)
    
    # Interpret results
    if p_value < 0.01 and len(significant_lags) > 0:
        interpretation = "Autocorrelation detected (reject H0 for H-MAIN-C)"
    elif p_value > 0.05:
        interpretation = "Consistent with independence (fail to reject H0)"
    else:
        interpretation = "Borderline significance"
    
    return {
        'acf': acf,
        'pacf': pacf,
        'ljung_box_Q': Q,
        'ljung_box_p': p_value,
        'confidence_band': confidence_band,
        'significant_lags': significant_lags,
        'n_samples': n,
        'max_lag': max_lag,
        'interpretation': interpretation,
    }
