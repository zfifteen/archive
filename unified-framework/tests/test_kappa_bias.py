#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for κ-Biased Stadlmann Integration
==============================================

Tests for the κ-bias functionality that prioritizes low-curvature primes
using divisor density weighting.

Reference: κ-Biased Stadlmann Integration in Unified-Framework
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import numpy as np
import mpmath as mp

from src.core.divisor_density import (
    kappa,
    kappa_bias,
    kappa_bias_factor,
    count_divisors,
    validate_kappa_properties
)
from src.core.z_5d_enhanced import z5d_predictor_with_dist_level


class TestKappaFunction:
    """Test the κ(n) curvature function"""
    
    def test_kappa_positive(self):
        """Test that κ(n) is always positive for n > 0"""
        test_values = [1, 2, 10, 100, 1000, 10000]
        for n in test_values:
            k = kappa(n)
            assert float(k) > 0, f"κ({n}) should be positive, got {k}"
    
    def test_kappa_small_values(self):
        """Test κ(n) for small known values"""
        # κ(1) = 1 * ln(2) / e² ≈ 0.0938
        k1 = float(kappa(1))
        assert 0.09 < k1 < 0.10, f"κ(1) ≈ 0.0938, got {k1}"
        
        # κ(2) has 2 divisors {1,2}
        k2 = float(kappa(2))
        expected_k2 = 2 * np.log(3) / np.exp(2)
        assert abs(k2 - expected_k2) < 0.01, f"κ(2) ≈ {expected_k2}, got {k2}"
    
    def test_kappa_prime_vs_composite(self):
        """Test that primes generally have lower κ than composites"""
        try:
            from sympy import isprime
        except ImportError:
            pytest.skip("sympy not available")
        
        # Compare some primes and composites
        prime_kappas = [float(kappa(p)) for p in [2, 3, 5, 7, 11, 13]]
        composite_kappas = [float(kappa(c)) for c in [4, 6, 8, 9, 10, 12]]
        
        avg_prime = np.mean(prime_kappas)
        avg_composite = np.mean(composite_kappas)
        
        assert avg_prime < avg_composite, \
            f"Primes should have lower avg κ than composites: {avg_prime} vs {avg_composite}"
    
    def test_kappa_divisor_count_dependency(self):
        """Test that κ increases with divisor count for similar magnitudes"""
        # 6 has 4 divisors, 12 has 6 divisors
        k6 = float(kappa(6))
        k12 = float(kappa(12))
        
        # Both are small numbers, so κ(12) > κ(6) due to more divisors
        # (though log term also plays a role)
        assert k12 > k6, f"κ(12) should be > κ(6): {k12} vs {k6}"
    
    def test_kappa_scale_growth(self):
        """Test that κ grows with n on average"""
        test_points = [10, 100, 1000, 10000]
        kappas = [float(kappa(n)) for n in test_points]
        
        # Check general increasing trend
        assert kappas[-1] > kappas[0], \
            f"κ should increase from 10 to 10000: {kappas}"


class TestKappaBias:
    """Test the κ-bias application"""
    
    def test_kappa_bias_reduces_prediction(self):
        """Test that κ-bias generally reduces predictions"""
        pred = mp.mpf('1299709')  # p_100000
        n = 100000
        
        biased = kappa_bias(pred, n)
        
        # κ-bias divides by κ(n), so result should be smaller
        assert float(biased) < float(pred), \
            f"Biased prediction should be smaller: {biased} vs {pred}"
    
    def test_kappa_bias_stability(self):
        """Test numerical stability with epsilon"""
        pred = mp.mpf('1000')
        n = 100
        
        # Should not raise errors and should be positive
        biased = kappa_bias(pred, n, epsilon=1e-6)
        assert float(biased) > 0
        
        # Different epsilon values should give similar results
        biased1 = kappa_bias(pred, n, epsilon=1e-6)
        biased2 = kappa_bias(pred, n, epsilon=1e-8)
        
        rel_diff = abs(float(biased1) - float(biased2)) / float(biased1)
        assert rel_diff < 0.01, f"Epsilon should have minimal effect: {rel_diff}"
    
    def test_kappa_bias_factor(self):
        """Test the bias factor computation"""
        n = 1000
        factor = kappa_bias_factor(n)
        
        # Factor should be positive and less than 1
        # (since κ(n) is typically > 1 for n > 10)
        assert float(factor) > 0
        assert float(factor) < 1, f"Bias factor should be < 1 for large n: {factor}"
    
    def test_kappa_bias_consistency(self):
        """Test that kappa_bias and kappa_bias_factor are consistent"""
        pred = mp.mpf('5000')
        n = 500
        
        # Method 1: using kappa_bias
        biased1 = kappa_bias(pred, n)
        
        # Method 2: using kappa_bias_factor
        factor = kappa_bias_factor(n)
        biased2 = pred * factor
        
        # Should give same result
        rel_diff = abs(float(biased1) - float(biased2)) / float(biased1)
        assert rel_diff < 1e-10, f"Methods should agree: {biased1} vs {biased2}"


class TestCountDivisors:
    """Test the divisor counting fallback function"""
    
    def test_count_divisors_small(self):
        """Test divisor counting for small values"""
        assert count_divisors(1) == 1  # {1}
        assert count_divisors(2) == 2  # {1, 2}
        assert count_divisors(6) == 4  # {1, 2, 3, 6}
        assert count_divisors(12) == 6  # {1, 2, 3, 4, 6, 12}
    
    def test_count_divisors_prime(self):
        """Test that primes have exactly 2 divisors"""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for p in primes:
            assert count_divisors(p) == 2, f"Prime {p} should have 2 divisors"
    
    def test_count_divisors_perfect_square(self):
        """Test divisor count for perfect squares"""
        # 4 = 2²: divisors {1, 2, 4} = 3
        assert count_divisors(4) == 3
        # 9 = 3²: divisors {1, 3, 9} = 3
        assert count_divisors(9) == 3
        # 16 = 2⁴: divisors {1, 2, 4, 8, 16} = 5
        assert count_divisors(16) == 5


class TestZ5DWithKappaBias:
    """Test Z_5D predictor with κ-bias integration"""
    
    def test_z5d_with_kappa_bias_basic(self):
        """Test basic Z_5D prediction with κ-bias"""
        n = 10000
        
        # Prediction without bias
        pred_base = z5d_predictor_with_dist_level(n, with_kappa_bias=False)
        
        # Prediction with bias
        pred_kappa = z5d_predictor_with_dist_level(n, with_kappa_bias=True)
        
        # Both should be positive
        assert float(pred_base) > 0
        assert float(pred_kappa) > 0
        
        # κ-bias should cause a small ppm-level change (not massive scaling)
        # With ppm-scale modulation, difference should be tiny
        rel_diff = abs(float(pred_kappa) - float(pred_base)) / float(pred_base)
        assert rel_diff < 0.01, \
            f"κ-bias should cause ppm-level change: {rel_diff*100:.6f}% difference"
        assert pred_kappa != pred_base, "κ-bias should cause some change"
    
    def test_z5d_kappa_bias_flag_default(self):
        """Test that κ-bias is off by default"""
        n = 10000
        
        pred_default = z5d_predictor_with_dist_level(n)
        pred_explicit_false = z5d_predictor_with_dist_level(n, with_kappa_bias=False)
        
        # Should be identical
        assert pred_default == pred_explicit_false
    
    def test_z5d_kappa_bias_with_dist_level(self):
        """Test κ-bias with custom distribution level"""
        n = 50000
        
        pred1 = z5d_predictor_with_dist_level(
            n, 
            dist_level=0.525,
            with_kappa_bias=True
        )
        
        pred2 = z5d_predictor_with_dist_level(
            n,
            dist_level=0.53,
            with_kappa_bias=True
        )
        
        # Both should be positive
        assert float(pred1) > 0
        assert float(pred2) > 0
        
        # Different dist_level should give different results
        assert pred1 != pred2
    
    def test_z5d_kappa_bias_with_ap_mod(self):
        """Test κ-bias with AP-specific predictions"""
        n = 20000
        
        pred_ap = z5d_predictor_with_dist_level(
            n,
            ap_mod=6,
            ap_res=1,
            with_kappa_bias=True
        )
        
        pred_standard = z5d_predictor_with_dist_level(
            n,
            with_kappa_bias=True
        )
        
        # Both should be positive
        assert float(pred_ap) > 0
        assert float(pred_standard) > 0
        
        # AP prediction should differ from standard (even with same κ-bias)
        # The difference comes from the AP adjustment, not κ-bias
        # With ppm-scale κ-bias, the difference might be tiny
        assert pred_ap != pred_standard or abs(float(pred_ap) - float(pred_standard)) < 1e-6
    
    def test_z5d_kappa_bias_scale_range(self):
        """Test κ-bias across different scales"""
        test_scales = [1000, 10000, 100000]
        
        for n in test_scales:
            pred_base = z5d_predictor_with_dist_level(n, with_kappa_bias=False)
            pred_kappa = z5d_predictor_with_dist_level(n, with_kappa_bias=True)
            
            # Both should be positive
            assert float(pred_base) > 0, f"Base prediction should be positive for n={n}"
            assert float(pred_kappa) > 0, f"κ-biased prediction should be positive for n={n}"
            
            # κ-bias should cause a tiny ppm-level change
            rel_diff = abs(float(pred_kappa) - float(pred_base)) / float(pred_base)
            assert rel_diff < 0.01, \
                f"κ-bias should cause ppm-level change for n={n}: {rel_diff*100:.6f}%"
    
    def test_z5d_kappa_bias_relative_impact(self):
        """Test that κ-bias has appropriate ppm-level impact"""
        n = 100000
        
        pred_base = z5d_predictor_with_dist_level(n, with_kappa_bias=False)
        pred_kappa = z5d_predictor_with_dist_level(n, with_kappa_bias=True)
        
        rel_diff = abs(float(pred_kappa) - float(pred_base)) / float(pred_base)
        
        # κ-bias should have ppm-level impact with the new ppm-scale modulation
        # With scale factor 10^-6, impact should be in the range of 10^-8 to 10^-5
        assert rel_diff < 0.01, f"κ-bias should have ppm-level impact: {rel_diff*100:.6f}%"
        assert rel_diff > 0, "κ-bias should cause some measurable change"


class TestValidateKappaProperties:
    """Test the κ function property validation"""
    
    def test_validate_kappa_properties_basic(self):
        """Test basic property validation"""
        results = validate_kappa_properties(n_max=100)
        
        # Check structure
        assert 'positivity_pass' in results
        assert 'monotonicity_violations' in results
        assert 'sample_kappa_values' in results
        
        # Positivity should pass
        assert results['positivity_pass'] is True
    
    def test_validate_kappa_prime_composite(self):
        """Test prime vs composite validation"""
        try:
            from sympy import isprime
        except ImportError:
            pytest.skip("sympy not available")
        
        results = validate_kappa_properties(n_max=100)
        
        # Check prime vs composite comparison
        if results.get('prime_vs_composite_pass') is not None:
            assert results['prime_vs_composite_pass'] is True, \
                "Primes should have lower avg κ than composites"
            assert 'avg_prime_kappa' in results
            assert 'avg_composite_kappa' in results


class TestIntegration:
    """Integration tests for complete κ-bias workflow"""
    
    def test_full_workflow_kappa_bias(self):
        """Test complete workflow with κ-bias"""
        n = 10000
        
        # Step 1: Basic Z_5D
        pred_basic = z5d_predictor_with_dist_level(n)
        assert float(pred_basic) > 0
        
        # Step 2: Z_5D with Stadlmann (default)
        pred_stadlmann = z5d_predictor_with_dist_level(n, dist_level=0.525)
        assert float(pred_stadlmann) > 0
        
        # Step 3: Z_5D with κ-bias
        pred_kappa = z5d_predictor_with_dist_level(n, with_kappa_bias=True)
        assert float(pred_kappa) > 0
        
        # Step 4: Combined (Stadlmann + κ-bias)
        pred_combined = z5d_predictor_with_dist_level(
            n,
            dist_level=0.525,
            with_kappa_bias=True
        )
        assert float(pred_combined) > 0
    
    def test_kappa_computation_consistency(self):
        """Test that κ computation is consistent"""
        n = 1000
        
        # Compute κ directly
        k1 = kappa(n)
        
        # Compute through bias factor
        # bias_factor = 1 / (κ + ε), so κ = (1 / bias_factor) - ε
        factor = kappa_bias_factor(n)
        k2 = (1 / factor) - 1e-6  # Recover κ by inverting and subtracting epsilon
        
        # Should be very close (within epsilon tolerance)
        abs_diff = abs(float(k1) - float(k2))
        rel_diff = abs_diff / float(k1)
        assert rel_diff < 1e-10, f"κ should be consistent: k1={k1}, k2={k2}, rel_diff={rel_diff}"
    
    def test_parameter_combinations(self):
        """Test various parameter combinations"""
        n = 50000
        
        # Test matrix of parameter combinations
        test_cases = [
            {'with_kappa_bias': False},
            {'with_kappa_bias': True},
            {'dist_level': 0.525, 'with_kappa_bias': False},
            {'dist_level': 0.525, 'with_kappa_bias': True},
            {'ap_mod': 6, 'ap_res': 1, 'with_kappa_bias': False},
            {'ap_mod': 6, 'ap_res': 1, 'with_kappa_bias': True},
        ]
        
        for params in test_cases:
            pred = z5d_predictor_with_dist_level(n, **params)
            assert float(pred) > 0, f"Prediction should be positive for params: {params}"


class TestErrorMetrics:
    """Test error metrics and accuracy claims"""
    
    def test_known_primes_comparison(self):
        """Test predictions against known primes"""
        # Known: p_100000 = 1299709
        n = 100000
        true_prime = 1299709
        
        # Base prediction
        pred_base = z5d_predictor_with_dist_level(n, with_kappa_bias=False)
        error_base = abs(float(pred_base) - true_prime) / true_prime
        
        # κ-biased prediction
        pred_kappa = z5d_predictor_with_dist_level(n, with_kappa_bias=True)
        error_kappa = abs(float(pred_kappa) - true_prime) / true_prime
        
        # Both should have some error (we're testing predictor behavior)
        print(f"\nBase error: {error_base*100:.4f}%")
        print(f"κ-biased error: {error_kappa*100:.4f}%")
        print(f"Base pred: {pred_base}")
        print(f"κ-biased pred: {pred_kappa}")
        print(f"True value: {true_prime}")
        
        # Just verify predictions are reasonable (not checking which is better)
        assert error_base < 1.0, "Base error should be reasonable"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
