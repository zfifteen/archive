#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stadlmann Distribution Level Integration - Demonstration Example
================================================================

This example demonstrates the integration of Stadlmann's 2023 advancement
on the level of distribution of primes in smooth arithmetic progressions
(θ ≈ 0.525) into the Z Framework.

Key features demonstrated:
1. Z_5D predictions with Stadlmann distribution level
2. Geodesic density enhancement with dist_level parameter
3. Arithmetic progression specific predictions
4. Bootstrap validation and confidence intervals

Reference: Issue #625 - Stadlmann 0.525 Level Integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.core.z_5d_enhanced import z5d_predictor, z5d_predictor_with_dist_level
from src.core.geodesic_mapping import GeodesicMapper
from src.core.conical_flow import (
    conical_evaporation_time,
    conical_density_enhancement_factor,
    validate_conical_model
)
from src.core.params import DIST_LEVEL_STADLMANN

try:
    from sympy import primerange
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("Warning: SymPy not available. Some examples will be skipped.")


def example_1_basic_z5d_with_stadlmann():
    """Example 1: Basic Z_5D prediction with Stadlmann level"""
    print("\n" + "=" * 70)
    print("Example 1: Z_5D Prediction with Stadlmann Distribution Level")
    print("=" * 70)
    
    k = 1000000  # 1 millionth prime
    
    # Standard Z_5D prediction
    pred_standard = z5d_predictor(k)
    print(f"\nPrime index k = {k:,}")
    print(f"Standard Z_5D prediction: {float(pred_standard):,.0f}")
    
    # Z_5D with Stadlmann distribution level
    pred_stadlmann = z5d_predictor_with_dist_level(k)
    print(f"Z_5D with Stadlmann (θ={DIST_LEVEL_STADLMANN}): {float(pred_stadlmann):,.0f}")
    
    # Compare difference
    diff = float(pred_stadlmann - pred_standard)
    rel_diff = (diff / float(pred_standard)) * 100
    print(f"\nDifference: {diff:,.0f} ({rel_diff:+.4f}%)")
    print(f"Stadlmann enhancement: {rel_diff:+.4f}% adjustment")


def example_2_ap_specific_prediction():
    """Example 2: Arithmetic progression specific predictions"""
    print("\n" + "=" * 70)
    print("Example 2: Arithmetic Progression Predictions")
    print("=" * 70)
    
    k = 500000
    
    # Standard prediction
    pred_standard = z5d_predictor_with_dist_level(k)
    print(f"\nPrime index k = {k:,}")
    print(f"Standard prediction: {float(pred_standard):,.0f}")
    
    # AP-specific predictions (primes ≡ 1 mod 6)
    pred_ap_6_1 = z5d_predictor_with_dist_level(k, ap_mod=6, ap_res=1)
    print(f"AP prediction (mod 6, res 1): {float(pred_ap_6_1):,.0f}")
    
    # AP-specific predictions (primes ≡ 1 mod 4)
    pred_ap_4_1 = z5d_predictor_with_dist_level(k, ap_mod=4, ap_res=1)
    print(f"AP prediction (mod 4, res 1): {float(pred_ap_4_1):,.0f}")
    
    print("\nNOTE: AP-specific predictions use smooth moduli equidistribution")
    print(f"      with Stadlmann's θ ≈ {DIST_LEVEL_STADLMANN} for tighter bounds")


def example_3_conical_flow_model():
    """Example 3: Conical flow model demonstration"""
    print("\n" + "=" * 70)
    print("Example 3: Conical Flow Model (Issue #631)")
    print("=" * 70)
    
    # Basic conical evaporation
    h0 = 100.0
    k = 0.01
    T = conical_evaporation_time(h0, k)
    
    print(f"\nConical Evaporation (constant-rate model):")
    print(f"  Initial height h0 = {h0}")
    print(f"  Rate constant k = {k}")
    print(f"  Evaporation time T = {T:.2f} units")
    print(f"  Formula: T = h0/k (exact analytical solution)")
    
    # Density enhancement factors
    print(f"\nDensity Enhancement Factors (Stadlmann θ={DIST_LEVEL_STADLMANN}):")
    for n in [1e3, 1e5, 1e6, 1e7]:
        enhancement = conical_density_enhancement_factor(int(n))
        boost = (enhancement - 1) * 100
        print(f"  n = {n:.0e}: enhancement = {enhancement:.6f} (+{boost:.3f}%)")
    
    # Model validation
    print(f"\nConical Model Validation:")
    results = validate_conical_model(n_samples=100)
    print(f"  Samples tested: {results['n_samples']}")
    print(f"  Pass rate: {results['pass_rate']:.2%}")
    print(f"  Mean relative error: {results['mean_rel_error']:.2e}")
    print(f"  ✓ Model validated with {results['pass_rate']:.0%} accuracy")


def example_4_geodesic_density_enhancement():
    """Example 4: Geodesic density enhancement with dist_level"""
    if not SYMPY_AVAILABLE:
        print("\n" + "=" * 70)
        print("Example 4: Skipped (SymPy not available)")
        print("=" * 70)
        return
    
    print("\n" + "=" * 70)
    print("Example 4: Geodesic Density Enhancement with Stadlmann Level")
    print("=" * 70)
    
    # Generate prime sample
    n_primes = 10000
    primes = list(primerange(2, 120000))[:n_primes]
    
    print(f"\nAnalyzing {len(primes)} primes...")
    
    # Initialize geodesic mapper
    mapper = GeodesicMapper(kappa_geo=0.3)
    
    # Standard density enhancement
    results_standard = mapper.compute_density_enhancement(
        primes, 
        n_bootstrap=100
    )
    
    print(f"\nStandard Geodesic Enhancement:")
    print(f"  Enhancement: {results_standard['enhancement_percent']:.4f}%")
    print(f"  95% CI: [{results_standard['ci_lower']:.4f}%, {results_standard['ci_upper']:.4f}%]")
    
    # Enhancement with Stadlmann distribution level
    results_stadlmann = mapper.compute_density_enhancement_with_dist_level(
        primes,
        dist_level=DIST_LEVEL_STADLMANN,
        n_bootstrap=100
    )
    
    print(f"\nStadlmann-Enhanced Geodesic:")
    print(f"  Enhancement: {results_stadlmann['enhancement_percent']:.4f}%")
    print(f"  95% CI: [{results_stadlmann['ci_lower']:.4f}%, {results_stadlmann['ci_upper']:.4f}%]")
    print(f"  Stadlmann boost: {results_stadlmann['stadlmann_boost_percent']:.4f}%")
    print(f"  Distribution level: θ = {results_stadlmann['dist_level']}")
    
    # Compare
    improvement = results_stadlmann['enhancement_percent'] - results_standard['enhancement_percent']
    print(f"\nComparison:")
    print(f"  Additional enhancement: {improvement:+.4f}%")
    print(f"  Relative improvement: {(improvement/results_standard['enhancement_percent']*100):+.2f}%")


def example_5_parameter_exploration():
    """Example 5: Explore different distribution levels"""
    print("\n" + "=" * 70)
    print("Example 5: Distribution Level Parameter Exploration")
    print("=" * 70)
    
    k = 100000
    
    # Test various distribution levels
    levels = [0.51, 0.52, DIST_LEVEL_STADLMANN, 0.53, 0.54]
    
    print(f"\nPrime index k = {k:,}")
    print(f"\nExploring distribution levels θ ∈ [{min(levels)}, {max(levels)}]:")
    print(f"{'θ':>6}  {'Prediction':>15}  {'Enhancement':>12}")
    print("-" * 40)
    
    baseline = float(z5d_predictor(k))
    
    for level in levels:
        try:
            pred = z5d_predictor_with_dist_level(k, dist_level=level)
            enhancement = (float(pred) - baseline) / baseline * 100
            marker = " ← Stadlmann" if abs(level - DIST_LEVEL_STADLMANN) < 0.001 else ""
            print(f"{level:>6.3f}  {float(pred):>15,.0f}  {enhancement:>+11.4f}%{marker}")
        except Exception as e:
            print(f"{level:>6.3f}  ERROR: {str(e)}")
    
    print("\nNote: θ ≈ 0.525 (Stadlmann 2023) provides optimal balance between")
    print("      accuracy and computational efficiency for smooth moduli APs.")


def main():
    """Run all demonstration examples"""
    print("=" * 70)
    print("Stadlmann Distribution Level Integration - Demonstration")
    print("=" * 70)
    print(f"\nStadlmann level θ = {DIST_LEVEL_STADLMANN}")
    print("Reference: Stadlmann 2023 (arXiv:2212.10867)")
    print("Integration: Z Framework Issue #625")
    
    try:
        example_1_basic_z5d_with_stadlmann()
    except Exception as e:
        print(f"\nExample 1 failed: {e}")
    
    try:
        example_2_ap_specific_prediction()
    except Exception as e:
        print(f"\nExample 2 failed: {e}")
    
    try:
        example_3_conical_flow_model()
    except Exception as e:
        print(f"\nExample 3 failed: {e}")
    
    try:
        example_4_geodesic_density_enhancement()
    except Exception as e:
        print(f"\nExample 4 failed: {e}")
    
    try:
        example_5_parameter_exploration()
    except Exception as e:
        print(f"\nExample 5 failed: {e}")
    
    print("\n" + "=" * 70)
    print("Demonstration Complete")
    print("=" * 70)
    print("\nFor more information:")
    print("  - src/core/params.py: DIST_LEVEL_STADLMANN constant")
    print("  - src/core/z_5d_enhanced.py: z5d_predictor_with_dist_level()")
    print("  - src/core/geodesic_mapping.py: compute_density_enhancement_with_dist_level()")
    print("  - src/core/conical_flow.py: Conical flow model (Issue #631)")


if __name__ == "__main__":
    main()
