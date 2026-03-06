#!/usr/bin/env python3
"""
Integration Test for Linear Curvature with Z5D Framework
========================================================

Tests integration of the kappa_linear module with existing Z5D framework,
demonstrating performance improvements and accuracy validation.

Author: Z Framework / Small-Angle Curvature Integration Testing
"""

import pytest
import numpy as np
import math
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.kappa_linear import (
    gen_frac_phi, kappa_linear, kappa_linear_sequence, 
    benchmark_linear_vs_traditional, kappa_linear_replace_trigonometric,
    PHI_FLOAT, ALPHA_FLOAT
)
from core.domain import DiscreteZetaShift


class TestLinearCurvatureIntegration:
    """Integration tests for linear curvature with Z Framework."""
    
    def test_performance_vs_existing_curvature(self):
        """Test performance improvement vs existing curvature calculations."""
        N = 500
        
        # Benchmark our linear implementation
        results = benchmark_linear_vs_traditional(N=N, k=0.3, use_fast=True)
        
        # Should be faster than traditional approach
        assert results['speedup_factor'] > 1.0, f"Linear should be faster, got {results['speedup_factor']}x"
        
        # Should achieve reasonable performance (> 2x speedup)
        assert results['speedup_factor'] > 2.0, f"Expected >2x speedup, got {results['speedup_factor']}x"
        
        print(f"✓ Performance test: {results['speedup_factor']:.2f}x speedup achieved")
    
    def test_trigonometric_replacement_accuracy(self):
        """Test accuracy of trigonometric function replacements."""
        n_values = list(range(1, 51))  # Small test set
        
        # Get linear approximations
        trig_replacements = kappa_linear_replace_trigonometric(n_values, use_fast=True)
        
        # Compare with actual trigonometric functions for small angles
        theta_values = trig_replacements['theta_linear']
        sin_linear = trig_replacements['sin_linear']
        cos_linear = trig_replacements['cos_linear']
        
        # Test small-angle approximations
        small_angle_errors_sin = []
        small_angle_errors_cos = []
        
        for theta, sin_approx, cos_approx in zip(theta_values, sin_linear, cos_linear):
            theta_norm = theta % (2 * math.pi)
            if theta_norm > math.pi:
                theta_norm -= 2 * math.pi
            
            if abs(theta_norm) < 0.5:  # Small angle regime
                actual_sin = math.sin(theta_norm)
                actual_cos = math.cos(theta_norm)
                
                sin_error = abs(sin_approx - actual_sin)
                cos_error = abs(cos_approx - actual_cos)
                
                small_angle_errors_sin.append(sin_error)
                small_angle_errors_cos.append(cos_error)
        
        # Small-angle approximations should be accurate
        if small_angle_errors_sin:
            max_sin_error = max(small_angle_errors_sin)
            max_cos_error = max(small_angle_errors_cos)
            
            assert max_sin_error < 0.1, f"Sin approximation error too large: {max_sin_error}"
            assert max_cos_error < 0.1, f"Cos approximation error too large: {max_cos_error}"
            
            print(f"✓ Trigonometric replacement: max sin error {max_sin_error:.6f}, max cos error {max_cos_error:.6f}")
    
    def test_z5d_framework_compatibility(self):
        """Test compatibility with existing Z5D framework."""
        # Create DiscreteZetaShift instances using traditional curvature
        n_values = [7, 11, 13, 17, 19, 23]
        traditional_results = []
        
        for n in n_values:
            dzs = DiscreteZetaShift(n)
            traditional_results.append({
                'n': n,
                'kappa_raw': float(dzs.kappa_raw),
                'kappa_bounded': float(dzs.kappa_bounded),
                'delta_n': float(dzs.delta_n),
                'z': float(dzs.compute_z())
            })
        
        # Generate linear curvature for same values
        linear_kappa = kappa_linear_sequence(len(n_values), k=0.3, use_fast=True)
        
        # Results should be reasonable (finite, non-zero variation)
        assert all(np.isfinite(k) for k in linear_kappa), "Linear curvature should be finite"
        assert len(set(linear_kappa)) > 1, "Linear curvature should have variation"
        
        # Linear curvature should have same order of magnitude as traditional
        trad_kappa_values = [r['kappa_raw'] for r in traditional_results]
        
        # Compare ranges (should be within 2 orders of magnitude)
        linear_range = max(linear_kappa) - min(linear_kappa)
        trad_range = max(trad_kappa_values) - min(trad_kappa_values)
        
        if trad_range > 0 and linear_range > 0:
            range_ratio = max(linear_range / trad_range, trad_range / linear_range)
            assert range_ratio < 100, f"Range ratio too large: {range_ratio}"
        
        print(f"✓ Z5D compatibility: traditional range {trad_range:.6f}, linear range {linear_range:.6f}")
    
    def test_fixed_point_accuracy_scaling(self):
        """Test fixed-point accuracy with different scale_bits."""
        N = 30
        k = 0.3
        
        # Test different scale_bits
        scale_bits_values = [16, 32, 48]
        results = {}
        
        for scale_bits in scale_bits_values:
            frac_values = list(gen_frac_phi(N, scale_bits=scale_bits, use_fast=False))
            kappa_seq = kappa_linear_sequence(N, k=k, scale_bits=scale_bits, use_fast=False)
            
            results[scale_bits] = {
                'frac_values': frac_values,
                'kappa_seq': kappa_seq
            }
        
        # Higher scale_bits should generally be more accurate
        # Compare 16-bit vs 48-bit
        frac_16 = results[16]['frac_values']
        frac_48 = results[48]['frac_values']
        
        max_frac_diff = max(abs(a - b) for a, b in zip(frac_16, frac_48))
        
        # Should see some difference due to precision
        assert max_frac_diff > 1e-8, "Should see precision differences"
        assert max_frac_diff < 0.01, "Precision differences shouldn't be huge"
        
        print(f"✓ Fixed-point scaling: max difference {max_frac_diff:.8f} between 16-bit and 48-bit")
    
    def test_geodesic_uplift_preservation(self):
        """Test that geodesic uplift properties are preserved."""
        N = 100
        k_values = [0.2, 0.3, 0.4]  # Different curvature exponents
        
        results = {}
        for k in k_values:
            linear_kappa = kappa_linear_sequence(N, k=k, use_fast=True)
            
            # Check for reasonable geodesic properties
            # 1. Finite values
            assert all(np.isfinite(kappa) for kappa in linear_kappa)
            
            # 2. Non-trivial variation
            std_dev = np.std(linear_kappa)
            assert std_dev > 1e-10, f"Too little variation for k={k}: {std_dev}"
            
            # 3. Reasonable magnitude
            max_abs = max(abs(kappa) for kappa in linear_kappa)
            assert max_abs < 100, f"Values too large for k={k}: {max_abs}"
            
            results[k] = {
                'mean': np.mean(linear_kappa),
                'std': std_dev,
                'max_abs': max_abs
            }
        
        # Different k values should produce different statistics
        means = [results[k]['mean'] for k in k_values]
        assert len(set([round(m, 6) for m in means])) > 1, "Different k should give different means"
        
        print(f"✓ Geodesic uplift: k=0.3 mean={results[0.3]['mean']:.6f}, std={results[0.3]['std']:.6f}")
    
    def test_small_angle_approximation_validity(self):
        """Test validity of small-angle approximations in curvature context."""
        # Generate small angles using golden ratio fractional parts
        N = 50
        frac_values = list(gen_frac_phi(N, use_fast=True))
        
        # Convert to angles in [0, 2π)
        angles = [2 * math.pi * frac for frac in frac_values]
        
        # For each angle, test small-angle approximation validity
        small_angles = [a for a in angles if a < 0.5]  # Small angle regime
        
        if small_angles:
            sin_errors = []
            for angle in small_angles:
                sin_exact = math.sin(angle)
                sin_approx = angle  # Linear approximation: sin(θ) ≈ θ
                
                error = abs(sin_exact - sin_approx)
                sin_errors.append(error)
            
            max_error = max(sin_errors)
            mean_error = np.mean(sin_errors)
            
            # Small-angle approximation should be accurate
            assert max_error < 0.05, f"Small-angle approximation error too large: {max_error}"
            assert mean_error < 0.01, f"Mean small-angle error too large: {mean_error}"
            
            print(f"✓ Small-angle validity: {len(small_angles)} angles, max error {max_error:.6f}")
    
    def test_integration_with_existing_tests(self):
        """Test that linear curvature doesn't break existing functionality."""
        # Run a basic DiscreteZetaShift operation
        n = 17
        dzs = DiscreteZetaShift(n)
        
        # Should still work normally
        z_value = dzs.compute_z()
        attributes = dzs.attributes
        
        # Convert to float for testing
        z_float = float(z_value)
        assert np.isfinite(z_float), "Z value should be finite"
        assert isinstance(attributes, dict), "Attributes should be dict"
        assert 'z' in attributes, "Should have z attribute"
        
        # Linear curvature should work alongside
        linear_kappa = kappa_linear_sequence(10, k=0.3, use_fast=True)
        assert len(linear_kappa) == 10, "Should generate correct number of values"
        
        print(f"✓ Integration: DZS z={z_float:.6f}, linear curvature works alongside")


def test_comprehensive_performance_benchmark():
    """Comprehensive performance test across different scales."""
    print("\n=== Comprehensive Performance Benchmark ===")
    
    scales = [100, 500, 1000]
    k_values = [0.2, 0.3, 0.4]
    
    for N in scales:
        for k in k_values:
            results = benchmark_linear_vs_traditional(N=N, k=k, use_fast=True)
            
            print(f"N={N:4d}, k={k:.1f}: {results['speedup_factor']:6.2f}x speedup, "
                  f"correlation={results['correlation']:6.3f}")
            
            # Should achieve speedup
            assert results['speedup_factor'] > 1.0, f"No speedup achieved for N={N}, k={k}"


def test_accuracy_validation():
    """Validate accuracy across different parameter ranges."""
    print("\n=== Accuracy Validation ===")
    
    # Test with different parameters
    test_cases = [
        {'N': 50, 'k': 0.1, 'ds': 1.0},
        {'N': 100, 'k': 0.3, 'ds': 0.5},
        {'N': 200, 'k': 0.5, 'ds': 2.0},
    ]
    
    for case in test_cases:
        kappa_seq = kappa_linear_sequence(**case, use_fast=True)
        
        # Check properties
        assert len(kappa_seq) == case['N']
        assert all(np.isfinite(k) for k in kappa_seq)
        
        mean_kappa = np.mean(kappa_seq)
        std_kappa = np.std(kappa_seq)
        
        print(f"N={case['N']:3d}, k={case['k']:3.1f}, ds={case['ds']:3.1f}: "
              f"mean={mean_kappa:8.5f}, std={std_kappa:8.5f}")


if __name__ == "__main__":
    # Run manual tests
    test_comprehensive_performance_benchmark()
    test_accuracy_validation()
    print("\nAll integration tests completed successfully!")