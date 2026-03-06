#!/usr/bin/env python3
"""
Linear Curvature Approximation Module for Z Framework
=====================================================

Implements linearized κ_g ≈ Δθ'/Δs to replace trigonometric curvature calculations
with faster fixed-point arithmetic using golden ratio transformations.

This module provides:
1. gen_frac_phi(N, scale_bits=48) - iterator of {n/φ} via fixed-point Wythoff/Beatty recurrence
2. kappa_linear(n, u_prev, u_curr, k, ds) - linear curvature approximation

Key features:
- Fixed-point arithmetic with ALPHA = 1/φ as Q16.48 (or Q32.32)
- No divisions in the Wythoff/Beatty recurrence
- Faster than trigonometric calculations
- Maintains accuracy for geodesic uplift and Z5D ppm

Author: Z Framework / Small-Angle Curvature Implementation
"""

import math
import mpmath as mp

# Mathematical constants for fast computation
PHI_FLOAT = 1.6180339887498948  # Golden ratio φ = 1.618... (float64)
ALPHA_FLOAT = 0.6180339887498949  # 1/φ ≈ 0.618... (float64)

# High-precision constants for when needed
mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2  # Golden ratio φ = 1.618...
ALPHA = 1 / PHI  # 1/φ ≈ 0.618... for Wythoff/Beatty sequence


def gen_frac_phi(N, scale_bits=48, use_fast=True):
    """
    Generate iterator of {n/φ} via fixed-point Wythoff/Beatty recurrence (no divisions).
    
    Uses fixed-point arithmetic to compute fractional parts {n/φ} efficiently
    without floating-point divisions, implementing the Wythoff/Beatty sequence
    properties of the golden ratio.
    
    Args:
        N (int): Number of terms to generate
        scale_bits (int): Fixed-point scale bits (default 48 for Q16.48)
        use_fast (bool): Use fast float64 arithmetic when possible (default True)
        
    Yields:
        float: Fractional part {n/φ} for n = 1, 2, ..., N
        
    Mathematical foundation:
        The Wythoff sequence A000201 gives floor(n*φ) for n ≥ 1.
        The Beatty sequence uses the property that φ and φ/(φ-1) partition ℕ.
        We compute {n/φ} = n/φ - floor(n/φ) using fixed-point recurrence.
    """
    if N <= 0:
        return
    
    if use_fast and scale_bits <= 32:
        # Fast path using native float64 arithmetic
        alpha = ALPHA_FLOAT
        accumulator = 0.0
        
        for n in range(1, N + 1):
            accumulator += alpha
            if accumulator >= 1.0:
                accumulator -= 1.0
            yield accumulator
    else:
        # Fixed-point scale factor
        scale = 1 << scale_bits  # 2^scale_bits
        
        # ALPHA = 1/φ in fixed-point arithmetic (Q16.48 or Q32.32)
        alpha_fixed = int(ALPHA * scale)
        
        # Accumulator for fixed-point {n/φ} computation
        accumulator = 0
        
        for n in range(1, N + 1):
            # Add ALPHA to accumulator: accumulator += 1/φ
            accumulator += alpha_fixed
            
            # Wrap by subtracting 1 when accumulator >= scale (equivalent to mod 1)
            if accumulator >= scale:
                accumulator -= scale
            
            # Convert back to floating-point fractional part
            frac_part = accumulator / scale
            
            yield float(frac_part)


def kappa_linear(n, u_prev, u_curr, k, ds, use_fast=True):
    """
    Compute linearized curvature κ = (φ*(u_curr^k - u_prev^k)) / ds.
    
    Implements small-angle approximation for curvature using golden ratio
    scaling and power law differences. This replaces trigonometric curvature
    calculations with linear approximations for improved performance.
    
    Args:
        n (int): Integer position
        u_prev (float): Previous fractional value {(n-1)/φ}
        u_curr (float): Current fractional value {n/φ}
        k (float): Curvature exponent (typically 0.2-0.4)
        ds (float): Arc length differential (spacing parameter)
        use_fast (bool): Use fast float64 arithmetic when possible (default True)
        
    Returns:
        float: Linear curvature approximation κ_linear
        
    Mathematical foundation:
        κ_g ≈ Δθ'/Δs where θ'(n,k) = φ · {n/φ}^k
        Linear approximation: κ ≈ (φ*(u_curr^k - u_prev^k)) / ds
        This avoids trigonometric functions while maintaining geometric meaning.
    """
    if ds == 0:
        return 0.0
    
    if use_fast:
        # Fast path using native float64 arithmetic
        phi = PHI_FLOAT
        
        # Bounds checking for numerical stability
        u_prev = max(0.0, min(1.0 - 1e-15, u_prev))
        u_curr = max(0.0, min(1.0 - 1e-15, u_curr))
        
        # Compute power terms
        if k == 0:
            power_diff = 0.0
        else:
            power_curr = u_curr ** k if u_curr > 0 else 0.0
            power_prev = u_prev ** k if u_prev > 0 else 0.0
            power_diff = power_curr - power_prev
        
        # Linear curvature: κ = φ * (u_curr^k - u_prev^k) / ds
        kappa = phi * power_diff / ds
        
        return kappa
    else:
        # High-precision path using mpmath
        phi = PHI
        u_prev = mp.mpmathify(u_prev)
        u_curr = mp.mpmathify(u_curr)
        k = mp.mpmathify(k)
        ds = mp.mpmathify(ds)
        
        # Compute power terms with bounds checking
        if k == 0:
            # k=0 case: u^0 = 1, so difference is 0
            power_diff = mp.mpf(0)
        else:
            # Handle edge cases for numerical stability
            if u_prev < 0:
                u_prev = mp.mpf(0)
            elif u_prev >= 1:
                u_prev = mp.mpf(1) - mp.mpf('1e-15')
                
            if u_curr < 0:
                u_curr = mp.mpf(0)
            elif u_curr >= 1:
                u_curr = mp.mpf(1) - mp.mpf('1e-15')
            
            # Compute power difference: u_curr^k - u_prev^k
            power_curr = u_curr ** k if u_curr > 0 else mp.mpf(0)
            power_prev = u_prev ** k if u_prev > 0 else mp.mpf(0)
            power_diff = power_curr - power_prev
        
        # Linear curvature: κ = φ * (u_curr^k - u_prev^k) / ds
        kappa = phi * power_diff / ds
        
        return float(kappa)


def kappa_linear_sequence(N, k=0.3, ds=1.0, scale_bits=48, use_fast=True):
    """
    Generate a sequence of linear curvature values for n = 1, 2, ..., N.
    
    Convenience function that combines gen_frac_phi and kappa_linear
    to compute curvature sequences efficiently.
    
    Args:
        N (int): Number of terms to compute
        k (float): Curvature exponent (default 0.3)
        ds (float): Arc length differential (default 1.0)
        scale_bits (int): Fixed-point scale bits (default 48)
        use_fast (bool): Use fast float64 arithmetic when possible (default True)
        
    Returns:
        list: Linear curvature values [κ_1, κ_2, ..., κ_N]
    """
    # Generate fractional parts {n/φ}
    frac_phi_gen = gen_frac_phi(N, scale_bits, use_fast)
    frac_values = list(frac_phi_gen)
    
    if len(frac_values) == 0:
        return []
    
    # Compute curvature sequence
    kappa_values = []
    
    for i in range(len(frac_values)):
        if i == 0:
            # First term: use u_prev = 0
            u_prev = 0.0
            u_curr = frac_values[i]
        else:
            u_prev = frac_values[i-1]
            u_curr = frac_values[i]
        
        kappa = kappa_linear(i+1, u_prev, u_curr, k, ds, use_fast)
        kappa_values.append(kappa)
    
    return kappa_values


def benchmark_linear_vs_traditional(N=1000, k=0.3, use_fast=True):
    """
    Benchmark linear curvature vs traditional curvature computation.
    
    Compares performance and accuracy of the linear approximation
    against the traditional κ(n) = d(n) · ln(n+1)/e² calculation.
    
    Args:
        N (int): Number of test values
        k (float): Curvature exponent
        use_fast (bool): Use fast mode for linear curvature
        
    Returns:
        dict: Benchmark results with timing and accuracy metrics
    """
    import time
    import numpy as np
    from sympy import divisors
    
    # Generate test data
    test_n_values = list(range(1, N+1))
    
    # Benchmark linear curvature
    start_time = time.time()
    linear_kappa = kappa_linear_sequence(N, k=k, use_fast=use_fast)
    linear_time = time.time() - start_time
    
    # Benchmark traditional curvature
    start_time = time.time()
    traditional_kappa = []
    for n in test_n_values:
        d_n = len(list(divisors(n)))
        kappa_trad = d_n * math.log(n + 1) / math.exp(2)
        traditional_kappa.append(kappa_trad)
    traditional_time = time.time() - start_time
    
    # Compute accuracy metrics
    linear_array = np.array(linear_kappa)
    trad_array = np.array(traditional_kappa)
    
    # Scale arrays to comparable ranges for meaningful comparison
    linear_scaled = linear_array / np.max(np.abs(linear_array)) if np.max(np.abs(linear_array)) > 0 else linear_array
    trad_scaled = trad_array / np.max(np.abs(trad_array)) if np.max(np.abs(trad_array)) > 0 else trad_array
    
    mse = np.mean((linear_scaled - trad_scaled) ** 2)
    correlation = np.corrcoef(linear_scaled, trad_scaled)[0, 1] if len(linear_scaled) > 1 else 0.0
    
    return {
        'linear_time': linear_time,
        'traditional_time': traditional_time,
        'speedup_factor': traditional_time / linear_time if linear_time > 0 else float('inf'),
        'mse': mse,
        'correlation': correlation,
        'linear_values': linear_kappa,
        'traditional_values': traditional_kappa
    }


def kappa_linear_replace_trigonometric(n_values, theta_values=None, use_fast=True):
    """
    Replace trigonometric curvature calculations with linear approximations.
    
    This function demonstrates how to replace sin/cos curvature calculations
    with the linearized κ_g approximation for performance improvement.
    
    Args:
        n_values (list): List of integer positions
        theta_values (list, optional): Corresponding theta values; if None, computed from {n/φ}
        use_fast (bool): Use fast mode computation
        
    Returns:
        dict: Contains linear approximations that can replace trigonometric calculations
    """
    N = len(n_values)
    
    if theta_values is None:
        # Generate theta values from golden ratio fractional parts
        frac_phi_gen = gen_frac_phi(N, use_fast=use_fast)
        theta_values = [2 * math.pi * frac for frac in frac_phi_gen]
    
    # Linear approximations replacing trigonometric functions
    results = {
        'n_values': n_values,
        'theta_linear': theta_values,
        'kappa_linear': [],
        'cos_linear': [],  # Small-angle approximation: cos(θ) ≈ 1 - θ²/2
        'sin_linear': [],  # Small-angle approximation: sin(θ) ≈ θ
    }
    
    for i, (n, theta) in enumerate(zip(n_values, theta_values)):
        # Previous and current fractional parts for curvature
        u_prev = 0.0 if i == 0 else (theta_values[i-1] / (2 * math.pi)) % 1
        u_curr = (theta / (2 * math.pi)) % 1
        
        # Linear curvature
        kappa = kappa_linear(n, u_prev, u_curr, k=0.3, ds=1.0, use_fast=use_fast)
        results['kappa_linear'].append(kappa)
        
        # Small-angle approximations for trigonometric functions
        # For small angles (θ << 1): sin(θ) ≈ θ, cos(θ) ≈ 1 - θ²/2
        theta_normalized = theta % (2 * math.pi)
        if theta_normalized > math.pi:
            theta_normalized -= 2 * math.pi  # Map to [-π, π]
        
        if abs(theta_normalized) < 0.5:  # Small angle regime
            sin_approx = theta_normalized
            cos_approx = 1.0 - (theta_normalized ** 2) / 2.0
        else:
            # Fall back to actual trig functions for large angles
            sin_approx = math.sin(theta_normalized)
            cos_approx = math.cos(theta_normalized)
        
        results['sin_linear'].append(sin_approx)
        results['cos_linear'].append(cos_approx)
    
    return results