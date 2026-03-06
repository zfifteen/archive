"""
Tests for Z Framework core geometric invariants.

Tests the curvature metric κ(n) and golden-ratio phase θ'(n,k) functions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np
from src.z_framework import (
    divisor_count,
    curvature_metric,
    golden_ratio_phase,
    PHI,
    E_SQUARED,
    ZFrameworkCalculator
)


class TestDivisorCount(unittest.TestCase):
    """Test the divisor_count function (IMPLEMENTED)."""
    
    def test_divisor_count_small_primes(self):
        """Test divisor count for small primes (should be 2)."""
        self.assertEqual(divisor_count(2), 2)
        self.assertEqual(divisor_count(3), 2)
        self.assertEqual(divisor_count(5), 2)
        self.assertEqual(divisor_count(7), 2)
    
    def test_divisor_count_composites(self):
        """Test divisor count for composite numbers."""
        self.assertEqual(divisor_count(4), 3)   # 1, 2, 4
        self.assertEqual(divisor_count(6), 4)   # 1, 2, 3, 6
        self.assertEqual(divisor_count(12), 6)  # 1, 2, 3, 4, 6, 12
        self.assertEqual(divisor_count(24), 8)  # 1, 2, 3, 4, 6, 8, 12, 24
    
    def test_divisor_count_one(self):
        """Test divisor count for 1."""
        self.assertEqual(divisor_count(1), 1)
    
    def test_divisor_count_perfect_square(self):
        """Test divisor count for perfect squares."""
        self.assertEqual(divisor_count(9), 3)   # 1, 3, 9
        self.assertEqual(divisor_count(16), 5)  # 1, 2, 4, 8, 16
        self.assertEqual(divisor_count(25), 3)  # 1, 5, 25
    
    def test_divisor_count_invalid(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            divisor_count(0)
        with self.assertRaises(ValueError):
            divisor_count(-5)


class TestCurvatureMetric(unittest.TestCase):
    """Test the curvature_metric function."""
    
    def test_curvature_basic(self):
        """Test basic curvature computation."""
        # Test a known prime
        kappa_7 = curvature_metric(7)
        # d(7) = 2, κ(7) = 2 * ln(8) / e² ≈ 0.565
        expected = 2 * np.log(8) / E_SQUARED
        self.assertAlmostEqual(kappa_7, expected, places=6)
        
        # Test a known composite
        kappa_12 = curvature_metric(12)
        # d(12) = 6, κ(12) = 6 * ln(13) / e² ≈ 2.08
        expected = 6 * np.log(13) / E_SQUARED
        self.assertAlmostEqual(kappa_12, expected, places=6)
    
    def test_curvature_prime_vs_composite(self):
        """Test that primes have lower curvature than composites."""
        # Compare prime 7 vs composite 8
        kappa_prime = curvature_metric(7)
        kappa_composite = curvature_metric(8)
        self.assertLess(kappa_prime, kappa_composite)
        
        # Compare prime 11 vs composite 12
        kappa_11 = curvature_metric(11)
        kappa_12 = curvature_metric(12)
        self.assertLess(kappa_11, kappa_12)
    
    def test_curvature_array_input(self):
        """Test curvature computation with array input."""
        n_array = np.array([7, 8, 11, 12])
        kappa_array = curvature_metric(n_array)
        
        # Check shape
        self.assertEqual(kappa_array.shape, (4,))
        
        # Check individual values match scalar calls
        self.assertAlmostEqual(kappa_array[0], curvature_metric(7), places=6)
        self.assertAlmostEqual(kappa_array[1], curvature_metric(8), places=6)
        self.assertAlmostEqual(kappa_array[2], curvature_metric(11), places=6)
        self.assertAlmostEqual(kappa_array[3], curvature_metric(12), places=6)
    
    def test_curvature_invalid_input(self):
        """Test that invalid inputs raise appropriate errors."""
        with self.assertRaises(ValueError):
            curvature_metric(0)
        with self.assertRaises(ValueError):
            curvature_metric(-5)
        with self.assertRaises(ValueError):
            curvature_metric(np.array([1, 2, -3, 4]))


class TestGoldenRatioPhase(unittest.TestCase):
    """Test the golden_ratio_phase function."""
    
    def test_phase_basic(self):
        """Test basic phase computation."""
        # Test with k=0 (should return φ regardless of n)
        theta_0 = golden_ratio_phase(10, k=0)
        self.assertAlmostEqual(theta_0, PHI, places=6)
        
        # Test with k=1 (linear in fractional part)
        theta_1 = golden_ratio_phase(10, k=1)
        expected = PHI * ((10 % PHI) / PHI)
        self.assertAlmostEqual(theta_1, expected, places=6)
    
    def test_phase_range(self):
        """Test that phase values are in expected range [0, φ]."""
        # Test multiple values
        for n in [1, 10, 100, 1000]:
            for k in [0.0, 0.3, 0.5, 1.0]:
                theta = golden_ratio_phase(n, k=k)
                self.assertGreaterEqual(theta, 0)
                self.assertLessEqual(theta, PHI)
    
    def test_phase_k_parameter(self):
        """Test effect of k parameter on phase."""
        n = 100
        
        # k=0 should give maximum value (φ)
        theta_0 = golden_ratio_phase(n, k=0)
        
        # Higher k should generally give different values
        theta_03 = golden_ratio_phase(n, k=0.3)
        theta_1 = golden_ratio_phase(n, k=1.0)
        
        # All should be in valid range
        for theta in [theta_0, theta_03, theta_1]:
            self.assertGreaterEqual(theta, 0)
            self.assertLessEqual(theta, PHI)
    
    def test_phase_array_input(self):
        """Test phase computation with array input."""
        n_array = np.array([10, 20, 30, 40])
        k = 0.3
        
        theta_array = golden_ratio_phase(n_array, k=k)
        
        # Check shape
        self.assertEqual(theta_array.shape, (4,))
        
        # Check individual values match scalar calls
        for i, n in enumerate(n_array):
            expected = golden_ratio_phase(int(n), k=k)
            self.assertAlmostEqual(theta_array[i], expected, places=6)
    
    def test_phase_invalid_input(self):
        """Test that invalid inputs raise appropriate errors."""
        # Negative k
        with self.assertRaises(ValueError):
            golden_ratio_phase(10, k=-0.5)
        
        # Non-positive n
        with self.assertRaises(ValueError):
            golden_ratio_phase(0, k=0.3)
        with self.assertRaises(ValueError):
            golden_ratio_phase(-5, k=0.3)
        
        # Array with non-positive values
        with self.assertRaises(ValueError):
            golden_ratio_phase(np.array([1, 2, -3, 4]), k=0.3)


class TestZFrameworkCalculator(unittest.TestCase):
    """Test the ZFrameworkCalculator class."""
    
    def test_calculator_init(self):
        """Test calculator initialization."""
        pass
    
    def test_batch_computation(self):
        """Test batch computation with caching."""
        pass
    
    def test_cache_efficiency(self):
        """Test that caching improves performance."""
        pass


if __name__ == '__main__':
    unittest.main()
