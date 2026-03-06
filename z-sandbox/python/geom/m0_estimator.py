#!/usr/bin/env python3
"""
Geometric Resonance Estimator for m₀

Estimates the optimal comb index m₀ that maps closest to √N using
geometric/resonance principles from the Z5D framework.

For RSA semiprimes, the comb formula is:
    p_m = exp((log N - 2πm/k)/2)

To find √N, we need:
    exp((log N - 2πm₀/k)/2) ≈ √N
    (log N - 2πm₀/k)/2 ≈ log(√N) = log(N)/2
    log N - 2πm₀/k ≈ log N
    2πm₀/k ≈ 0
    m₀ ≈ 0

For balanced RSA semiprimes, factors cluster near m=0.
"""

from mpmath import mp, mpf, log as mplog, exp as mpexp, pi as mp_pi, sqrt as mpsqrt
from typing import Optional
from .z5d_predictor import compute_confidence_ppm


def estimate_m0_balanced(N: int, k: float, dps: int = 1000) -> float:
    """
    Estimate m₀ for balanced RSA semiprimes.
    
    For balanced semiprimes (p ≈ q ≈ √N), the true factors correspond to
    fractional m values very close to 0.
    
    Args:
        N: The semiprime to factor
        k: Wave number parameter (typically ~0.3)
        dps: Decimal precision (≥1000 for RSA-260)
        
    Returns:
        Estimated m₀ (typically very close to 0.0 for RSA)
    """
    # Set precision
    original_dps = mp.dps
    mp.dps = dps
    
    try:
        # For balanced RSA, m₀ ≈ 0
        # This is where the geometric resonance peaks for equal factors
        m0 = mpf(0.0)
        
        # Add small correction based on curvature if needed
        # For now, keep it at exactly 0 as empirical evidence suggests
        return float(m0)
        
    finally:
        mp.dps = original_dps


def estimate_m0_from_residue(N: int, k: float, dps: int = 1000) -> float:
    """
    Estimate m₀ using residue analysis.
    
    This uses the quantization condition:
        log N - 2 log p = 2πm/k
    
    For p ≈ √N:
        log N - 2 log(√N) = log N - log N = 0
        So m ≈ 0
        
    Args:
        N: The semiprime to factor
        k: Wave number parameter
        dps: Decimal precision
        
    Returns:
        Estimated m₀
    """
    original_dps = mp.dps
    mp.dps = dps
    
    try:
        log_N = mplog(N)
        sqrt_N = mpsqrt(N)
        log_sqrt_N = mplog(sqrt_N)
        
        # Phase difference for balanced case
        phase_diff = log_N - 2 * log_sqrt_N
        
        # Convert to m-space
        m0 = (k * phase_diff) / (2 * mp_pi)
        
        return float(m0)
        
    finally:
        mp.dps = original_dps


def estimate_m0_from_z5d_prior(N: int, k: float, confidence: float = 0.95, dps: int = 1000) -> tuple[float, float, float, float]:
    """
    Estimate m₀ and confidence window, including epsilon_ppm and safety.
    
    Returns (m0, window_width, epsilon_ppm, safety) where the true m value is likely
    within [m0 - window_width, m0 + window_width].
    
    Args:
        N: The semiprime to factor
        k: Wave number parameter
        confidence: Confidence level (0 to 1)
        dps: Decimal precision
        
    Returns:
        Tuple of (m0, window_width, epsilon_ppm, safety)
    """
    m0 = estimate_m0_balanced(N, k, dps)
    
    epsilon_ppm, safety = compute_confidence_ppm(N, dps)

    # Use ε to derive m-window via Δm ≈ (k/π) * ε * S
    # window_width represents the half-width of the search window
    window_width = (mpf(k) / mp_pi) * (mpf(epsilon_ppm) / 1_000_000) * mpf(safety)

    return m0, float(window_width), epsilon_ppm, safety


def get_resonance_metadata(N: int, k: float, dps: int = 1000) -> dict:
    """
    Get comprehensive resonance metadata for diagnostics.
    
    Args:
        N: The semiprime to factor
        k: Wave number parameter
        dps: Decimal precision
        
    Returns:
        Dictionary with resonance parameters
    """
    original_dps = mp.dps
    mp.dps = dps
    
    try:
        log_N = mplog(N)
        center = log_N / 2
        m0_balanced = estimate_m0_balanced(N, k, dps)
        m0_residue = estimate_m0_from_residue(N, k, dps)
        m0, window = estimate_m0_window(N, k, dps=dps)
        
        return {
            'log_N': float(log_N),
            'center': float(center),
            'm0_balanced': m0_balanced,
            'm0_residue': m0_residue,
            'm0_recommended': m0,
            'window_width': window,
            'k': k,
            'dps': dps
        }
        
    finally:
        mp.dps = original_dps
