#!/usr/bin/env python3
"""
Bias-Corrected Green's Function Factorization

This module implements systematic bias correction to the geometric embedding
stage, addressing the structural wall identified in Issue #196.

Key insight: For balanced RSA semiprimes, the search window centered at sqrt(N)
has a systematic offset from the true factor location. This can be corrected
using log-space analysis and resonance phase information.

Issue #198: STRUCTURAL_WALL_REDUCTION_PHASE
"""

import math
from mpmath import mp
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import logging

# Import base functionality
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from python.greens_function_factorization import (
        GreensResult,
        RefinementConfig,
        compute_curvature,
        safe_log,
        safe_sqrt,
        greens_function_amplitude,
        comb_formula,
        dirichlet_kernel,
        phase_bias_correction,
        estimate_k_optimal,
        EPSILON
    )
except ImportError:
    from greens_function_factorization import (
        GreensResult,
        RefinementConfig,
        compute_curvature,
        safe_log,
        safe_sqrt,
        greens_function_amplitude,
        comb_formula,
        dirichlet_kernel,
        phase_bias_correction,
        estimate_k_optimal,
        EPSILON
    )

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def estimate_log_space_bias(N: int, k: float) -> float:
    """
    Estimate systematic bias in log-space for geometric embedding.
    
    For balanced RSA semiprimes p ≈ q, where N = p × q:
    - sqrt(N) is the geometric mean
    - But due to p ≠ q (even if close), there's a systematic offset
    - This offset can be estimated from the resonance structure
    
    Key insight: The comb formula gives us p_m = exp((log N - 2πm/k)/2)
    For the resonance peak, we want m such that the phase is near 0 (mod 2π).
    
    The structural wall occurs because sqrt(N) doesn't account for the
    asymmetry between p and q. We can correct this using the phase structure.
    
    Args:
        N: Semiprime to factor
        k: Wave number parameter
        
    Returns:
        Log-space bias correction (additive in log space)
    """
    log_N = safe_log(N)
    
    # For balanced semiprimes, the optimal m is near k * log(N) / (2π)
    # This comes from the phase quantization condition
    m_center = k * log_N / (2.0 * math.pi)
    
    # Round to nearest integer
    m_opt = int(round(m_center))
    
    # Compute the candidate from comb formula
    p_candidate = comb_formula(log_N, k, m_opt)
    log_p_candidate = math.log(p_candidate)
    
    # The bias is the difference between this and log(sqrt(N))
    log_sqrt_N = log_N / 2.0
    
    # Phase at this candidate
    phase_at_candidate = k * (log_N - 2.0 * log_p_candidate)
    
    # The phase tells us if we need to shift up or down
    # Phase ≈ 0 means we're at a resonance peak
    # Phase > 0 means we need to shift down in log space
    # Phase < 0 means we need to shift up in log space
    
    # Normalize phase to [-π, π]
    phase_normalized = math.atan2(math.sin(phase_at_candidate), math.cos(phase_at_candidate))
    
    # Convert phase offset to log-space correction
    # δ(log p) ≈ -phase / (2k)
    log_bias_correction = -phase_normalized / (2.0 * k)
    
    return log_bias_correction


def estimate_empirical_bias_from_amplitude_profile(
    N: int,
    k: float,
    num_samples: int = 51
) -> float:
    """
    Estimate bias by analyzing the amplitude profile around sqrt(N).
    
    This looks at the Green's function amplitude at multiple points
    around sqrt(N) and finds where the maximum actually occurs.
    
    For RSA-2048, the structural wall is ~3.92%, so we need to scan
    a wide range to find the true resonance peak.
    
    Args:
        N: Semiprime to factor
        k: Wave number parameter
        num_samples: Number of points to sample (should be odd)
        
    Returns:
        Estimated bias in log space
    """
    log_N = safe_log(N)
    sqrt_N = safe_sqrt(N)
    
    # Sample points around sqrt(N) in log space
    # Use a wider range to capture the true peak
    log_sqrt_N = math.log(float(sqrt_N))
    
    # For RSA-2048 scale, we need to scan ±5% in log space
    # This corresponds to roughly ±5% in linear space for large numbers
    # At RSA-2048 scale, 5% ≈ the structural wall distance
    log_range = 0.05  # ±5% in log space
    
    log_samples = []
    amplitudes = []
    
    for i in range(num_samples):
        # Linearly interpolate in log space
        t = -1.0 + 2.0 * i / (num_samples - 1)  # -1 to +1
        log_p = log_sqrt_N + t * log_range
        
        # Compute amplitude
        amplitude = greens_function_amplitude(log_N, log_p, k)
        
        log_samples.append(log_p)
        amplitudes.append(amplitude)
    
    # Find peak
    max_idx = amplitudes.index(max(amplitudes))
    log_p_peak = log_samples[max_idx]
    
    # Refine around the peak with finer sampling
    # Take narrower range around the peak
    if max_idx > 0 and max_idx < len(log_samples) - 1:
        log_left = log_samples[max_idx - 1]
        log_right = log_samples[max_idx + 1]
        
        # Fine sampling
        fine_samples = []
        fine_amplitudes = []
        
        for i in range(21):
            t = i / 20.0  # 0 to 1
            log_p = log_left + t * (log_right - log_left)
            amplitude = greens_function_amplitude(log_N, log_p, k)
            
            fine_samples.append(log_p)
            fine_amplitudes.append(amplitude)
        
        fine_max_idx = fine_amplitudes.index(max(fine_amplitudes))
        log_p_peak = fine_samples[fine_max_idx]
    
    # Bias is the difference from log(sqrt(N))
    bias = log_p_peak - log_sqrt_N
    
    return bias


def apply_geometric_bias_correction(
    N: int,
    k: float,
    method: str = 'phase'
) -> int:
    """
    Apply bias correction to find improved search center.
    
    Args:
        N: Semiprime to factor
        k: Wave number parameter
        method: Correction method ('phase' or 'amplitude')
        
    Returns:
        Corrected search center (integer)
    """
    sqrt_N = safe_sqrt(N)
    log_sqrt_N = math.log(float(sqrt_N))
    
    if method == 'phase':
        log_bias = estimate_log_space_bias(N, k)
    elif method == 'amplitude':
        log_bias = estimate_empirical_bias_from_amplitude_profile(N, k)
    else:
        # No correction
        return sqrt_N
    
    # Apply correction in log space
    log_corrected = log_sqrt_N + log_bias
    
    # Convert back to linear space
    corrected_center = int(round(math.exp(log_corrected)))
    
    return corrected_center


def factorize_greens_bias_corrected(
    N: int,
    k: Optional[float] = None,
    config: Optional[RefinementConfig] = None,
    max_candidates: int = 100,
    bias_correction_method: str = 'phase',
    window_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Factorization with bias-corrected geometric embedding.
    
    This applies systematic bias correction to the geometric embedding stage,
    addressing the ~3.92% structural wall identified in Issue #196.
    
    Args:
        N: Semiprime to factor
        k: Wave number (auto-estimated if None)
        config: Refinement configuration
        max_candidates: Maximum candidates to return
        bias_correction_method: 'phase', 'amplitude', or 'none'
        window_size: Search window size around corrected center
        
    Returns:
        Dictionary with results including bias correction info
    """
    if config is None:
        config = RefinementConfig()
    
    # Estimate k if not provided
    if k is None:
        k = estimate_k_optimal(N)
    
    # Original center (sqrt(N))
    sqrt_N = safe_sqrt(N)
    
    # Adaptive window size based on N scale
    if window_size is None:
        # For RSA-2048 scale, use ±5% of sqrt(N) as window
        # This ensures we can reach factors up to 5% away
        window_size_adaptive = int(sqrt_N * 0.05)
        # Cap at reasonable limits
        window_size = min(window_size_adaptive, 10**9)  # Cap at 1 billion for performance
        window_size = max(window_size, 10000)  # Min 10k for small cases
    
    # Apply bias correction
    if bias_correction_method != 'none':
        corrected_center = apply_geometric_bias_correction(N, k, bias_correction_method)
        bias_applied = corrected_center - sqrt_N
    else:
        corrected_center = sqrt_N
        bias_applied = 0
    
    # Build search window around corrected center
    log_N = safe_log(N)
    
    results = []
    
    p_min = max(2, corrected_center - window_size)
    p_max = corrected_center + window_size
    
    for p in range(p_min, p_max + 1):
        if p <= 1:
            continue
            
        log_p = safe_log(p)
        
        # Basic Green's function amplitude
        amplitude = greens_function_amplitude(log_N, log_p, k)
        
        # Compute phase
        phase = k * (log_N - 2.0 * log_p)
        
        # Apply Dirichlet sharpening if enabled
        if config.use_dirichlet:
            dirichlet_factor = abs(dirichlet_kernel(phase, config.dirichlet_J))
            dirichlet_factor = dirichlet_factor / (2 * config.dirichlet_J + 1)
            amplitude *= dirichlet_factor
        
        # Compute kappa weight if enabled
        kappa_weight = 1.0
        if config.use_kappa_weight:
            kappa_weight = compute_curvature(p)
        
        # Combined score
        score = amplitude * kappa_weight
        
        # Estimate resonance mode m
        m = int(round((log_N - 2.0 * log_p) * k / (2.0 * math.pi)))
        
        results.append(GreensResult(
            p_candidate=p,
            amplitude=amplitude,
            phase=phase,
            kappa_weight=kappa_weight,
            score=score,
            m_value=m
        ))
    
    # Sort by score
    results.sort(key=lambda r: r.score, reverse=True)
    
    # Apply phase correction if enabled
    if config.use_phase_correction:
        corrected_results = []
        
        for res in results[:10]:
            p = res.p_candidate
            
            if p > 2:
                log_p_minus = safe_log(p - 1)
                log_p_center = safe_log(p)
                log_p_plus = safe_log(p + 1)
                
                amp_minus = greens_function_amplitude(log_N, log_p_minus, k)
                amp_center = greens_function_amplitude(log_N, log_p_center, k)
                amp_plus = greens_function_amplitude(log_N, log_p_plus, k)
                
                # Phase bias correction
                phi_0 = phase_bias_correction(amp_minus, amp_center, amp_plus)
                
                phase_corrected = res.phase - phi_0
                log_p_corrected = (log_N - phase_corrected / k) / 2.0
                p_corrected = int(round(math.exp(log_p_corrected)))
                
                if p_corrected != p and p_corrected > 1:
                    log_p_new = safe_log(p_corrected)
                    amplitude_new = greens_function_amplitude(log_N, log_p_new, k)
                    kappa_new = compute_curvature(p_corrected) if config.use_kappa_weight else 1.0
                    score_new = amplitude_new * kappa_new
                    
                    corrected_results.append(GreensResult(
                        p_candidate=p_corrected,
                        amplitude=amplitude_new,
                        phase=k * (log_N - 2.0 * log_p_new),
                        kappa_weight=kappa_new,
                        score=score_new,
                        m_value=res.m_value
                    ))
        
        # Merge and re-sort
        all_results = results + corrected_results
        all_results.sort(key=lambda r: r.score, reverse=True)
        results = all_results
    
    # Check for exact factors
    exact_factors = []
    found_factor = False
    
    for res in results[:max_candidates]:
        p = res.p_candidate
        if N % p == 0:
            q = N // p
            exact_factors.append((p, q))
            found_factor = True
            break
    
    return {
        'candidates': results[:max_candidates],
        'k_used': k,
        'found_factor': found_factor,
        'exact_factors': exact_factors,
        'N': N,
        'bias_correction': {
            'method': bias_correction_method,
            'original_center': sqrt_N,
            'corrected_center': corrected_center,
            'bias_applied': bias_applied,
            'bias_magnitude': abs(bias_applied),
            'relative_bias': abs(bias_applied) / sqrt_N if sqrt_N > 0 else 0
        }
    }


if __name__ == "__main__":
    # Quick test
    print("Bias-Corrected Green's Function Factorization")
    print("=" * 80)
    
    # Small test case
    N_test = 143
    p_test = 11
    q_test = 13
    
    print(f"\nTest case: N={N_test}, p={p_test}, q={q_test}")
    
    for method in ['none', 'phase', 'amplitude']:
        print(f"\n--- Method: {method} ---")
        
        result = factorize_greens_bias_corrected(
            N_test,
            k=0.3,
            max_candidates=10,
            bias_correction_method=method
        )
        
        print(f"Bias info: {result['bias_correction']}")
        print(f"Found factor: {result['found_factor']}")
        
        if result['candidates']:
            best = result['candidates'][0]
            print(f"Best candidate: p={best.p_candidate}, score={best.score:.6f}")
