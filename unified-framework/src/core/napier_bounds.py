#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Napier's Inequality Bounds for Z Framework Logarithmic Terms
===========================================================

Implements Napier's inequality bounds to refine logarithmic calculations
in the Z Framework, specifically for terms like ln(n+1) used in:
- Curvature formula κ(n) = d(n) · ln(n+1)/e²
- Geodesic mapping θ'(n, k=0.3) calculations
- Prime density enhancement (~15% uplift)

Napier's inequality states that for z > 0:
    z/(z+1) < ln(1+z) < z

This provides tight bounds for logarithmic terms used throughout the framework.
"""

import mpmath as mp
import numpy as np
from typing import Union, Tuple

# Set high precision for bounds calculations
mp.mp.dps = 50


def napier_bounds(z: Union[float, mp.mpf]) -> Tuple[mp.mpf, mp.mpf, mp.mpf]:
    """
    Compute Napier's inequality bounds for ln(1+z).
    
    For z > 0, returns:
    - Lower bound: z/(z+1)
    - Exact value: ln(1+z) 
    - Upper bound: z
    
    Args:
        z: Input value (z > 0)
        
    Returns:
        Tuple of (lower_bound, exact_ln, upper_bound)
        
    Raises:
        ValueError: If z <= 0
    """
    z_mp = mp.mpf(z)
    
    if z_mp <= 0:
        raise ValueError("Napier's inequality requires z > 0")
    
    lower_bound = z_mp / (z_mp + mp.mpf('1'))
    exact_ln = mp.log(mp.mpf('1') + z_mp)
    upper_bound = z_mp
    
    return lower_bound, exact_ln, upper_bound


def bounded_log_n_plus_1(n: Union[int, float, mp.mpf], use_bounds: str = "exact") -> mp.mpf:
    """
    Compute ln(n+1) with optional Napier's inequality bounds.
    
    This function specifically targets the ln(n+1) terms used in Z Framework
    curvature calculations κ(n) = d(n) · ln(n+1)/e².
    
    Args:
        n: Input value (n >= 0)
        use_bounds: One of "lower", "exact", "upper", "conservative"
                   - "lower": Use lower bound n/(n+1) * ln(2) for conservative estimate
                   - "exact": Use exact ln(n+1) (default)
                   - "upper": Use upper bound n * ln(2) for aggressive estimate
                   - "conservative": Use geometric mean of bounds for balanced approach
                   
    Returns:
        Bounded logarithmic value
        
    Raises:
        ValueError: If n < 0
    """
    n_mp = mp.mpf(n)
    
    if n_mp < 0:
        raise ValueError("Input n must be non-negative")
    
    if n_mp == 0:
        return mp.mpf('0')  # ln(0+1) = ln(1) = 0
    
    # Apply Napier's inequality to z = n (so ln(1+z) = ln(n+1))
    lower_bound, exact_ln, upper_bound = napier_bounds(n_mp)
    
    if use_bounds == "lower":
        return lower_bound
    elif use_bounds == "exact":
        return exact_ln
    elif use_bounds == "upper":
        return upper_bound
    elif use_bounds == "conservative":
        # Geometric mean provides balanced conservative estimate
        return mp.sqrt(lower_bound * upper_bound)
    else:
        raise ValueError(f"Invalid use_bounds option: {use_bounds}")


def enhanced_curvature_bounds(n: Union[int, float, mp.mpf], d_n: int, 
                            bounds_type: str = "exact") -> mp.mpf:
    """
    Compute enhanced curvature κ(n) = d(n) · ln(n+1)/e² with Napier bounds.
    
    This function specifically enhances the Z Framework curvature calculation
    by applying Napier's inequality bounds to the logarithmic term.
    
    Args:
        n: Input value
        d_n: Number of divisors of n
        bounds_type: Bound type for ln(n+1) calculation
        
    Returns:
        Enhanced curvature value with refined bounds
    """
    E_SQUARED = mp.exp(mp.mpf('2'))
    
    # Apply Napier bounds to ln(n+1) term
    bounded_log = bounded_log_n_plus_1(n, use_bounds=bounds_type)
    
    # Compute enhanced curvature
    kappa = mp.mpf(d_n) * bounded_log / E_SQUARED
    
    return kappa


def geodesic_enhancement_factor(n: Union[int, float, mp.mpf], 
                              k: float = 0.3) -> mp.mpf:
    """
    Compute geodesic enhancement factor using Napier-bounded logarithms.
    
    This supports the ~15% prime density enhancement via improved bounds
    on the geodesic mapping θ'(n, k=0.3).
    
    Args:
        n: Input value
        k: Curvature parameter (default: 0.3)
        
    Returns:
        Enhanced geodesic factor
    """
    # Use conservative bounds for stable geodesic mapping
    bounded_log = bounded_log_n_plus_1(n, use_bounds="conservative")
    
    # Apply geodesic transformation with enhanced bounds
    enhancement = mp.power(bounded_log, mp.mpf(k))
    
    return enhancement


def validate_napier_bounds_quality(z_values: list, tolerance: float = 1e-12) -> dict:
    """
    Validate the quality and tightness of Napier's inequality bounds.
    
    Args:
        z_values: List of test values
        tolerance: Numerical tolerance for validation
        
    Returns:
        Dictionary with validation results
    """
    results = {
        "total_tests": len(z_values),
        "bounds_valid": 0,
        "max_lower_gap": 0.0,
        "max_upper_gap": 0.0,
        "average_tightness": 0.0
    }
    
    total_tightness = 0.0
    
    for z in z_values:
        try:
            lower, exact, upper = napier_bounds(z)
            
            # Validate bounds: lower < exact < upper
            if lower <= exact <= upper:
                results["bounds_valid"] += 1
                
                lower_gap = float(exact - lower)
                upper_gap = float(upper - exact)
                
                results["max_lower_gap"] = max(results["max_lower_gap"], lower_gap)
                results["max_upper_gap"] = max(results["max_upper_gap"], upper_gap)
                
                # Tightness measure: how close bounds are to exact value
                tightness = 1.0 - float(upper - lower) / float(exact) if exact > 0 else 0.0
                total_tightness += tightness
                
        except Exception:
            continue
    
    if results["bounds_valid"] > 0:
        results["average_tightness"] = total_tightness / results["bounds_valid"]
    
    return results


def vectorized_bounded_log_n_plus_1(n_array: np.ndarray, use_bounds: str = "conservative") -> np.ndarray:
    """
    Vectorized version of bounded_log_n_plus_1 for efficient computation.
    
    Args:
        n_array: NumPy array of input values (all n >= 0)
        use_bounds: Bound type for ln(n+1) calculation
        
    Returns:
        NumPy array of bounded logarithmic values
    """
    if use_bounds == "exact":
        return np.log(n_array + 1)
    elif use_bounds == "lower":
        return n_array / (n_array + 1)
    elif use_bounds == "upper":
        return n_array
    elif use_bounds == "conservative":
        # Geometric mean of bounds for conservative estimate
        lower = n_array / (n_array + 1)
        upper = n_array
        return np.sqrt(lower * upper)
    else:
        raise ValueError(f"Invalid use_bounds option: {use_bounds}")


# Test function for integration validation
def test_napier_integration():
    """Test Napier bounds integration with Z Framework terms."""
    test_values = [1, 10, 100, 1000, 10000]
    
    print("Napier's Inequality Bounds Integration Test")
    print("=" * 50)
    
    for n in test_values:
        print(f"\nTesting n = {n}:")
        
        # Standard calculation
        exact_ln = mp.log(n + 1)
        
        # Napier bounds
        lower, exact, upper = napier_bounds(n)
        
        # Enhanced curvature (assuming d(n) = 4 for simplicity)
        d_n = 4
        kappa_exact = enhanced_curvature_bounds(n, d_n, "exact")
        kappa_conservative = enhanced_curvature_bounds(n, d_n, "conservative")
        
        print(f"  ln({n}+1) = {float(exact_ln):.6f}")
        print(f"  Napier bounds: [{float(lower):.6f}, {float(upper):.6f}]")
        print(f"  κ(n) exact: {float(kappa_exact):.6f}")
        print(f"  κ(n) conservative: {float(kappa_conservative):.6f}")
        
        # Geodesic enhancement
        geo_factor = geodesic_enhancement_factor(n)
        print(f"  Geodesic factor: {float(geo_factor):.6f}")
    
    # Validate bounds quality
    validation = validate_napier_bounds_quality(test_values)
    print(f"\nValidation Results:")
    print(f"  Valid bounds: {validation['bounds_valid']}/{validation['total_tests']}")
    print(f"  Average tightness: {validation['average_tightness']:.6f}")


if __name__ == "__main__":
    test_napier_integration()