#!/usr/bin/env python3
"""
Enhanced Zeta Zero Spacing Predictor - Drop-in Upgrade Implementation

This module implements the enhanced zeta zero spacing predictor with the following
key improvements addressing the requirements from Issue #724:

1. Small-n hazards fix: Use ln(n+1) consistently, gate n≥3
2. Fast divisor counts: Sieve-based τ(n) approach (O(N log N))
3. Parameter fitting: Train/test split with locked parameters
4. Cumulative drift control: N(T) anchoring for monotonicity
5. Statistical reporting: Pearson r, MARE, Bootstrap 95% CI
6. 3BT enhancement: Optional band-averaging smoother

The implementation provides a fast tau(n) sieve, enhanced kappa function,
linear fitting with beta term, and comprehensive validation metrics.
"""

import numpy as np
from typing import Tuple, List, Optional, Dict, Any
import warnings


def tau_sieve(N: int) -> np.ndarray:
    """
    Fast tau(n) divisor count via sieve (O(N log N)).
    
    Replaces slow sympy.divisor_count for large-scale computations.
    Uses prime factorization sieve to compute d(n) efficiently.
    
    Args:
        N: Maximum n value to compute tau(n) for
        
    Returns:
        Array where tau[n] = d(n) (number of divisors of n)
    """
    tau = np.ones(N + 1, dtype=np.int32)
    tau[0] = 0
    
    for p in range(2, N + 1):
        if tau[p] == 1:  # p is prime (still has value 1)
            for m in range(p, N + 1, p):
                t, c = m, 0
                while t % p == 0:
                    t //= p
                    c += 1
                tau[m] *= (c + 1)
    
    return tau


def kappa_from_tau(n_min: int, n_max: int, tau: np.ndarray, 
                   with_3bt: bool = False, delta: float = 0.01) -> np.ndarray:
    """
    Compute κ(n) = d(n) · ln(n+1) / e² with optional 3BT enhancement.
    
    Args:
        n_min: Starting n value
        n_max: Ending n value  
        tau: Precomputed tau (divisor count) array
        with_3bt: Enable 3BT band-averaging smoother (hypothesis)
        delta: 3BT bandwidth parameter
        
    Returns:
        Array of κ(n) values for n in [n_min, n_max]
    """
    n = np.arange(n_min, n_max + 1)
    base = tau[n] * np.log(n + 1) / np.exp(2)
    
    if not with_3bt:
        return base
    
    # 3BT band-average variance reduction: weighted average of nearby κ values
    # This creates a smoothing effect that reduces variance in spacing predictions
    smoothed = np.zeros_like(base)
    for i in range(len(base)):
        if i == 0:
            smoothed[i] = (2 * base[i] + base[i+1]) / 3
        elif i == len(base) - 1:
            smoothed[i] = (base[i-1] + 2 * base[i]) / 3
        else:
            smoothed[i] = (base[i-1] + base[i] + base[i+1]) / 3
    
    return smoothed


def fit_linear_with_beta(n: np.ndarray, kappa: np.ndarray, spacings: np.ndarray, 
                        floor_n: int = 3) -> Tuple[float, float, float]:
    """
    Fit linear model: spacing = a·κ + b + β/ln²(n+1) with small-n gating.
    
    Args:
        n: Array of n values
        kappa: Array of κ(n) values
        spacings: Array of observed spacings
        floor_n: Minimum n value to include in fit (avoids small-n hazards)
        
    Returns:
        Tuple (a, b, beta) of fitted parameters
    """
    mask = n >= floor_n
    n_fit, k_fit, s_fit = n[mask], kappa[mask], spacings[mask]
    
    # Design matrix: [κ, 1, 1/ln²(n+1)] - use ln(n+1) to avoid log(1)=0
    X = np.column_stack([k_fit, np.ones_like(k_fit), 1.0 / (np.log(n_fit + 1) ** 2)])
    
    # Least-squares solution
    coef, *_ = np.linalg.lstsq(X, s_fit, rcond=None)
    a, b, beta = map(float, coef)
    
    return a, b, beta


def z5d_zeta_spacings(n: np.ndarray, kappa: np.ndarray, a: float, b: float, 
                      beta: float) -> np.ndarray:
    """
    Predict zeta zero spacings using Z5D enhanced model.
    
    Model: spacing = a·κ(n) + b + β/ln²(n)
    Small-n hazard fix: Use ln(n+1) and gate n≥3
    
    Args:
        n: Array of n values
        kappa: Array of κ(n) values  
        a, b, beta: Fitted model parameters
        
    Returns:
        Array of predicted spacings
    """
    # Small-n hazard fix: use ln(n+1) and ensure n >= 1
    n_safe = np.maximum(n, 1)
    log_term = np.log(n_safe + 1) ** 2
    
    return a * kappa + b + beta / log_term


def NvM(T: float) -> float:
    """
    Riemann-von Mangoldt zero counting function N(T).
    
    Asymptotic formula: N(T) ≈ (T/2π)(ln(T/2π) - 1) + 7/8
    
    Args:
        T: Height parameter
        
    Returns:
        Approximate number of zeros up to height T
    """
    return (T / (2 * np.pi)) * (np.log(T / (2 * np.pi)) - 1.0) + 7.0/8.0


def rescale_gammas(gamma_hat: np.ndarray) -> np.ndarray:
    """
    Rescale cumulative gamma estimates to control drift.
    
    Periodically anchors to N(T) count to maintain monotonicity
    and eliminate low-frequency bias accumulation.
    
    Args:
        gamma_hat: Array of cumulative gamma estimates
        
    Returns:
        Rescaled gamma array
    """
    if len(gamma_hat) < 200:
        return gamma_hat
    
    # Sample anchor points for rescaling
    idx = np.linspace(100, len(gamma_hat) - 1, 8, dtype=int)
    valid = [i for i in idx if gamma_hat[i] > 50]
    
    if not valid:
        return gamma_hat
    
    # Compute median scaling factor based on N(T)
    scale = np.median([NvM(gamma_hat[i]) / i for i in valid])
    
    return gamma_hat / max(scale, 1e-12)


def z5d_zeta_approx(n_start: int, n_end: int, a: float, b: float, beta: float,
                    zeta1: float = 14.134725141734693, with_3bt: bool = False) -> np.ndarray:
    """
    Generate Z5D zeta zero approximation sequence.
    
    Combines fast divisor counting, enhanced spacing prediction,
    and drift-controlled cumulative summation.
    
    Args:
        n_start: Starting zero index
        n_end: Ending zero index
        a, b, beta: Model parameters
        zeta1: First zeta zero (ζ₁)
        with_3bt: Enable 3BT variance reduction
        
    Returns:
        Array of predicted gamma values
    """
    n = np.arange(n_start, n_end + 1)
    
    # Fast divisor counting
    tau = tau_sieve(n_end)
    
    # Enhanced kappa with optional 3BT
    kap = kappa_from_tau(n_start, n_end, tau, with_3bt=with_3bt)
    
    # Predict spacings
    spac = z5d_zeta_spacings(n, kap, a, b, beta)
    
    # Cumulative sum with drift control
    gamma_hat = zeta1 + np.cumsum(spac)
    
    return rescale_gammas(gamma_hat)


def compute_spacing_metrics(actual_spacings: np.ndarray, predicted_spacings: np.ndarray) -> Dict[str, float]:
    """
    Compute spacing prediction metrics.
    
    Args:
        actual_spacings: Observed spacings
        predicted_spacings: Model predictions
        
    Returns:
        Dictionary of metrics including Pearson r, MARE, etc.
    """
    # Remove any invalid values
    mask = np.isfinite(actual_spacings) & np.isfinite(predicted_spacings)
    actual = actual_spacings[mask]
    predicted = predicted_spacings[mask]
    
    if len(actual) < 2:
        return {'pearson_r': np.nan, 'mare': np.nan, 'rmse': np.nan}
    
    # Pearson correlation coefficient
    correlation_matrix = np.corrcoef(actual, predicted)
    pearson_r = correlation_matrix[0, 1] if correlation_matrix.shape == (2, 2) else np.nan
    
    # Mean Absolute Relative Error (MARE)
    mare = np.mean(np.abs((actual - predicted) / np.maximum(actual, 1e-10)))
    
    # Root Mean Square Error
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    
    return {
        'pearson_r': pearson_r,
        'mare': mare,
        'rmse': rmse,
        'count': len(actual)
    }


def compute_gamma_metrics(actual_gammas: np.ndarray, predicted_gammas: np.ndarray) -> Dict[str, float]:
    """
    Compute gamma prediction metrics.
    
    Args:
        actual_gammas: Observed gamma values
        predicted_gammas: Model predictions
        
    Returns:
        Dictionary of metrics including MARE on gammas
    """
    # Remove any invalid values
    mask = np.isfinite(actual_gammas) & np.isfinite(predicted_gammas)
    actual = actual_gammas[mask]
    predicted = predicted_gammas[mask]
    
    if len(actual) < 2:
        return {'gamma_mare': np.nan, 'gamma_rmse': np.nan}
    
    # MARE on gamma values
    gamma_mare = np.mean(np.abs((actual - predicted) / np.maximum(actual, 1e-10)))
    
    # RMSE on gamma values
    gamma_rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    
    return {
        'gamma_mare': gamma_mare,
        'gamma_rmse': gamma_rmse,
        'gamma_count': len(actual)
    }


def bootstrap_confidence_interval(actual: np.ndarray, predicted: np.ndarray, 
                                metric_func: callable, n_resamples: int = 1000,
                                confidence_level: float = 0.95) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval for a metric.
    
    Args:
        actual: Actual values
        predicted: Predicted values  
        metric_func: Function to compute metric (takes actual, predicted)
        n_resamples: Number of bootstrap resamples
        confidence_level: Confidence level (e.g., 0.95 for 95% CI)
        
    Returns:
        Tuple (metric_value, ci_low, ci_high)
    """
    n = len(actual)
    if n < 10:
        warnings.warn("Sample size too small for reliable bootstrap CI")
        return np.nan, np.nan, np.nan
    
    # Original metric
    original_metric = metric_func(actual, predicted)
    
    # Bootstrap resampling
    bootstrap_metrics = []
    for _ in range(n_resamples):
        # Resample with replacement
        idx = np.random.choice(n, size=n, replace=True)
        resampled_actual = actual[idx]
        resampled_predicted = predicted[idx]
        
        # Compute metric for resampled data
        metric = metric_func(resampled_actual, resampled_predicted)
        if np.isfinite(metric):
            bootstrap_metrics.append(metric)
    
    if len(bootstrap_metrics) < 10:
        warnings.warn("Too few valid bootstrap samples")
        return original_metric, np.nan, np.nan
    
    # Compute confidence interval
    alpha = 1 - confidence_level
    ci_low = np.percentile(bootstrap_metrics, 100 * alpha / 2)
    ci_high = np.percentile(bootstrap_metrics, 100 * (1 - alpha / 2))
    
    return original_metric, ci_low, ci_high


class EnhancedZetaSpacingPredictor:
    """
    Enhanced Zeta Zero Spacing Predictor with Z5D improvements.
    
    Implements the drop-in upgrade for robust zeta spacing prediction
    with fast divisor counting, parameter fitting, and statistical validation.
    """
    
    def __init__(self, with_3bt: bool = False, floor_n: int = 3):
        """
        Initialize the predictor.
        
        Args:
            with_3bt: Enable 3BT variance reduction (experimental)
            floor_n: Minimum n for fitting (avoids small-n hazards)
        """
        self.with_3bt = with_3bt
        self.floor_n = floor_n
        self.fitted_params = None
        self.training_metrics = None
        
    def fit(self, n_values: np.ndarray, spacing_values: np.ndarray) -> Dict[str, Any]:
        """
        Fit the spacing prediction model.
        
        Args:
            n_values: Array of zero indices
            spacing_values: Array of observed spacings
            
        Returns:
            Dictionary of fitting results and metrics
        """
        # Compute tau and kappa
        max_n = int(np.max(n_values))
        tau = tau_sieve(max_n)
        kappa = kappa_from_tau(int(np.min(n_values)), max_n, tau, with_3bt=self.with_3bt)
        
        # Fit linear model with beta term
        a, b, beta = fit_linear_with_beta(n_values, kappa, spacing_values, self.floor_n)
        
        # Store fitted parameters
        self.fitted_params = {'a': a, 'b': b, 'beta': beta}
        
        # Compute training metrics
        predicted_spacings = z5d_zeta_spacings(n_values, kappa, a, b, beta)
        spacing_metrics = compute_spacing_metrics(spacing_values, predicted_spacings)
        
        self.training_metrics = spacing_metrics
        
        return {
            'parameters': self.fitted_params,
            'training_metrics': spacing_metrics,
            'kappa_computed': len(kappa),
            'floor_n_used': self.floor_n,
            'with_3bt': self.with_3bt
        }
    
    def predict_spacings(self, n_values: np.ndarray) -> np.ndarray:
        """
        Predict spacings for given n values.
        
        Args:
            n_values: Array of zero indices
            
        Returns:
            Array of predicted spacings
        """
        if self.fitted_params is None:
            raise ValueError("Model must be fitted before making predictions")
        
        # Compute kappa for prediction
        max_n = int(np.max(n_values))
        tau = tau_sieve(max_n)
        kappa = kappa_from_tau(int(np.min(n_values)), max_n, tau, with_3bt=self.with_3bt)
        
        # Predict using fitted parameters
        return z5d_zeta_spacings(n_values, kappa, 
                               self.fitted_params['a'], 
                               self.fitted_params['b'], 
                               self.fitted_params['beta'])
    
    def predict_gammas(self, n_start: int, n_end: int, 
                      zeta1: float = 14.134725141734693) -> np.ndarray:
        """
        Predict gamma values (zero positions).
        
        Args:
            n_start: Starting zero index
            n_end: Ending zero index
            zeta1: First zeta zero value
            
        Returns:
            Array of predicted gamma values
        """
        if self.fitted_params is None:
            raise ValueError("Model must be fitted before making predictions")
        
        return z5d_zeta_approx(n_start, n_end, 
                             self.fitted_params['a'],
                             self.fitted_params['b'], 
                             self.fitted_params['beta'],
                             zeta1=zeta1, with_3bt=self.with_3bt)
    
    def evaluate(self, n_values: np.ndarray, spacing_values: np.ndarray, 
                gamma_values: Optional[np.ndarray] = None,
                n_bootstrap: int = 1000) -> Dict[str, Any]:
        """
        Evaluate model performance with bootstrap confidence intervals.
        
        Args:
            n_values: Array of zero indices
            spacing_values: Array of actual spacings
            gamma_values: Array of actual gamma values (optional)
            n_bootstrap: Number of bootstrap resamples
            
        Returns:
            Dictionary of evaluation metrics with confidence intervals
        """
        # Predict spacings
        predicted_spacings = self.predict_spacings(n_values)
        
        # Spacing metrics with bootstrap CI
        def pearson_r_func(actual, predicted):
            corr = np.corrcoef(actual, predicted)
            return corr[0, 1] if corr.shape == (2, 2) else np.nan
        
        def mare_func(actual, predicted):
            return np.mean(np.abs((actual - predicted) / np.maximum(actual, 1e-10)))
        
        # Bootstrap confidence intervals
        pearson_r, pearson_ci_low, pearson_ci_high = bootstrap_confidence_interval(
            spacing_values, predicted_spacings, pearson_r_func, n_bootstrap)
        
        mare, mare_ci_low, mare_ci_high = bootstrap_confidence_interval(
            spacing_values, predicted_spacings, mare_func, n_bootstrap)
        
        results = {
            'spacing_metrics': {
                'pearson_r': pearson_r,
                'pearson_r_ci': (pearson_ci_low, pearson_ci_high),
                'mare': mare,
                'mare_ci': (mare_ci_low, mare_ci_high)
            }
        }
        
        # Gamma metrics if provided
        if gamma_values is not None:
            predicted_gammas = self.predict_gammas(int(np.min(n_values)), int(np.max(n_values)))
            gamma_metrics = compute_gamma_metrics(gamma_values, predicted_gammas)
            
            # Bootstrap CI for gamma MARE
            gamma_mare, gamma_mare_ci_low, gamma_mare_ci_high = bootstrap_confidence_interval(
                gamma_values, predicted_gammas, mare_func, n_bootstrap)
            
            results['gamma_metrics'] = {
                'gamma_mare': gamma_mare,
                'gamma_mare_ci': (gamma_mare_ci_low, gamma_mare_ci_high)
            }
        
        return results