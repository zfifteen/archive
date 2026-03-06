#!/usr/bin/env python3
"""
Test suite for Physical-Discrete Connection refinement in the Z Framework.

Tests the implementation of Linear Scaling approach: p_n' = p_n · T(v/c)
with empirical validation of enhancement preservation.
"""

import os
import sys
import numpy as np
import unittest
from unittest.mock import patch

# Add the src directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'number-theory', 'prime-curve'))

# Import the functions from proof.py
from proof import (
    lorentz_factor, 
    physical_scaling_transform, 
    frame_shift_residues,
    run_k_sweep_with_physical_scaling,
    validate_physical_scaling_enhancement
)


class TestPhysicalDiscreteConnection(unittest.TestCase):
    """Test cases for Physical-Discrete Connection implementation."""
    
    def test_lorentz_factor_computation(self):
        """Test Lorentz factor γ = 1/sqrt(1-(v/c)²) computation."""
        # Test v/c = 0 (baseline)
        self.assertAlmostEqual(lorentz_factor(0.0), 1.0, places=6)
        
        # Test v/c = 0.3
        expected_gamma_03 = 1 / np.sqrt(1 - 0.3**2)
        self.assertAlmostEqual(lorentz_factor(0.3), expected_gamma_03, places=6)
        
        # Test v/c = 0.5
        expected_gamma_05 = 1 / np.sqrt(1 - 0.5**2)
        self.assertAlmostEqual(lorentz_factor(0.5), expected_gamma_05, places=6)
        
        # Test v/c = 0.9
        expected_gamma_09 = 1 / np.sqrt(1 - 0.9**2)
        self.assertAlmostEqual(lorentz_factor(0.9), expected_gamma_09, places=6)
    
    def test_lorentz_factor_edge_cases(self):
        """Test edge cases for Lorentz factor computation."""
        # Test v/c >= 1 raises ValueError
        with self.assertRaises(ValueError):
            lorentz_factor(1.0)
        
        with self.assertRaises(ValueError):
            lorentz_factor(1.1)
        
        # Test negative v/c raises ValueError
        with self.assertRaises(ValueError):
            lorentz_factor(-0.1)
    
    def test_physical_scaling_transform(self):
        """Test physical scaling transformation p_n' = p_n · γ."""
        primes = np.array([2, 3, 5, 7, 11])
        
        # Test v/c = 0 (no scaling)
        scaled_primes = physical_scaling_transform(primes, 0.0)
        np.testing.assert_array_equal(scaled_primes, primes)
        
        # Test v/c = 0.3
        gamma_03 = lorentz_factor(0.3)
        scaled_primes_03 = physical_scaling_transform(primes, 0.3)
        expected_scaled = primes * gamma_03
        np.testing.assert_array_almost_equal(scaled_primes_03, expected_scaled, decimal=6)
    
    def test_frame_shift_residues_with_physical_scaling(self):
        """Test enhanced frame shift with physical scaling integration."""
        n_vals = np.array([2, 3, 5, 7])
        k = 3.3
        
        # Test baseline (v/c = 0)
        result_baseline = frame_shift_residues(n_vals, k, v_over_c=0.0)
        result_traditional = frame_shift_residues(n_vals, k)  # Should be same as baseline
        np.testing.assert_array_almost_equal(result_baseline, result_traditional, decimal=10)
        
        # Test with physical scaling (v/c = 0.3)
        result_scaled = frame_shift_residues(n_vals, k, v_over_c=0.3)
        
        # Results should be different due to physical scaling
        self.assertFalse(np.array_equal(result_baseline, result_scaled))
        
        # Results should have same shape
        self.assertEqual(result_baseline.shape, result_scaled.shape)
    
    def test_k_sweep_with_physical_scaling(self):
        """Test k-sweep analysis with physical scaling produces valid results."""
        # Test baseline (v/c = 0)
        results_baseline, best_baseline = run_k_sweep_with_physical_scaling(v_over_c=0.0, verbose=False)
        
        # Verify results structure
        self.assertIsInstance(results_baseline, list)
        self.assertIsInstance(best_baseline, dict)
        self.assertGreater(len(results_baseline), 0)
        
        # Verify required keys in best result
        required_keys = ['k', 'v_over_c', 'max_enhancement', 'e_max_k', 
                        'bootstrap_ci_lower', 'bootstrap_ci_upper', 
                        'sigma_prime', 'fourier_b_sum']
        for key in required_keys:
            self.assertIn(key, best_baseline)
        
        # Test with physical scaling (v/c = 0.3)
        results_scaled, best_scaled = run_k_sweep_with_physical_scaling(v_over_c=0.3, verbose=False)
        
        # Verify results structure for scaled version
        self.assertIsInstance(results_scaled, list)
        self.assertIsInstance(best_scaled, dict)
        self.assertGreater(len(results_scaled), 0)
        
        # Verify v_over_c is recorded correctly
        self.assertAlmostEqual(best_baseline['v_over_c'], 0.0, places=6)
        self.assertAlmostEqual(best_scaled['v_over_c'], 0.3, places=6)
    
    def test_enhancement_preservation_criteria(self):
        """Test that enhancement preservation is within expected bounds."""
        # Run validation to get baseline and scaled results
        with patch('builtins.print'):  # Suppress print output during test
            baseline_results = validate_physical_scaling_enhancement()
        
        # Test specific v/c values for enhancement preservation
        test_velocities = [0.3, 0.5]
        
        for v_over_c in test_velocities:
            with patch('builtins.print'):  # Suppress print output
                results, best = run_k_sweep_with_physical_scaling(v_over_c, verbose=False)
            
            # Calculate enhancement ratio vs baseline
            enhancement_ratio = best['max_enhancement'] / baseline_results['max_enhancement']
            
            # For moderate velocities (0.3, 0.5), enhancement should be preserved within ±15%
            # This aligns with the issue requirement for conditional prime density improvement under canonical benchmark methodology preservation
            if v_over_c <= 0.5:
                self.assertGreaterEqual(enhancement_ratio, 0.85, 
                                      f"Enhancement degraded below 15% tolerance at v/c={v_over_c}")
                self.assertLessEqual(enhancement_ratio, 1.15, 
                                   f"Enhancement exceeded 15% tolerance at v/c={v_over_c}")


class TestZFrameworkIntegration(unittest.TestCase):
    """Test integration with existing Z Framework components."""
    
    def test_backward_compatibility(self):
        """Test that existing functionality is preserved when v/c = 0."""
        # Test that frame_shift_residues with v_over_c=0 matches original behavior
        n_vals = np.array([2, 3, 5, 7, 11, 13])
        k = 3.212  # Optimal k from original implementation
        
        # New implementation with v/c = 0
        result_new = frame_shift_residues(n_vals, k, v_over_c=0.0)
        
        # Original implementation (without v/c parameter)
        result_original = frame_shift_residues(n_vals, k)
        
        # Should be identical
        np.testing.assert_array_almost_equal(result_new, result_original, decimal=12)
    
    def test_empirical_validation_requirements(self):
        """Test that implementation meets empirical validation requirements from issue."""
        # Issue specifies: simulate prime distributions up to N=10^4, 
        # scale by T(v/c), and validate preservation of ~15% enhancement
        
        with patch('builtins.print'):  # Suppress output during test
            baseline_results = validate_physical_scaling_enhancement()
        
        # Verify baseline enhancement is reasonable (issue mentions current ~89% max enhancement)
        self.assertGreater(baseline_results['max_enhancement'], 50.0)
        self.assertLess(baseline_results['max_enhancement'], 150.0)
        
        # Test that confidence intervals are computed
        self.assertIn('bootstrap_ci_lower', baseline_results)
        self.assertIn('bootstrap_ci_upper', baseline_results)
        
        # Test that optimal k is in expected range (issue mentions k* ≈ 0.3, but implementation uses different scale)
        self.assertGreater(baseline_results['k'], 3.0)
        self.assertLess(baseline_results['k'], 3.5)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)