#!/usr/bin/env python3
"""
Unit tests for eigenvalue_calculator.py

Tests divisor functions, multiplicity calculations, and bound verification.
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from eigenvalue_calculator import EigenvalueMultiplicityCalculator


class TestEigenvalueCalculator(unittest.TestCase):
    """Test eigenvalue multiplicity calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calc = EigenvalueMultiplicityCalculator(dimension=7)
    
    def test_divisor_function(self):
        """Test divisor function d(k)."""
        # Known values
        self.assertEqual(self.calc.divisor_function(1), 1)
        self.assertEqual(self.calc.divisor_function(12), 6)  # 1,2,3,4,6,12
        self.assertEqual(self.calc.divisor_function(24), 8)  # 1,2,3,4,6,8,12,24
        self.assertEqual(self.calc.divisor_function(60), 12)  # 12 divisors
        
        # Primes have exactly 2 divisors
        self.assertEqual(self.calc.divisor_function(7), 2)
        self.assertEqual(self.calc.divisor_function(13), 2)
        self.assertEqual(self.calc.divisor_function(97), 2)
    
    def test_divisor_function_invalid_input(self):
        """Test divisor function with invalid input."""
        with self.assertRaises(ValueError):
            self.calc.divisor_function(0)
        with self.assertRaises(ValueError):
            self.calc.divisor_function(-5)
    
    def test_chi_mod_4(self):
        """Test non-principal character χ mod 4."""
        # Even numbers → 0
        self.assertEqual(self.calc.chi_mod_4(2), 0)
        self.assertEqual(self.calc.chi_mod_4(4), 0)
        self.assertEqual(self.calc.chi_mod_4(10), 0)
        
        # d ≡ 1 (mod 4) → 1
        self.assertEqual(self.calc.chi_mod_4(1), 1)
        self.assertEqual(self.calc.chi_mod_4(5), 1)
        self.assertEqual(self.calc.chi_mod_4(9), 1)
        
        # d ≡ 3 (mod 4) → -1
        self.assertEqual(self.calc.chi_mod_4(3), -1)
        self.assertEqual(self.calc.chi_mod_4(7), -1)
        self.assertEqual(self.calc.chi_mod_4(11), -1)
    
    def test_r_2_sum_of_squares(self):
        """Test r_2(k): sum of two squares representation."""
        # Known values from number theory
        # r_2(1) = 4: (±1, 0), (0, ±1)
        self.assertEqual(self.calc.r_2_sum_of_squares(1), 4)
        
        # r_2(2) = 4: (±1, ±1)
        self.assertEqual(self.calc.r_2_sum_of_squares(2), 4)
        
        # r_2(5) = 8: (±1, ±2), (±2, ±1)
        self.assertEqual(self.calc.r_2_sum_of_squares(5), 8)
        
        # r_2(3) = 0 (3 cannot be written as sum of 2 squares)
        self.assertEqual(self.calc.r_2_sum_of_squares(3), 0)
        
        # r_2(25) = 12: 25 = 5², multiple representations
        self.assertEqual(self.calc.r_2_sum_of_squares(25), 12)
    
    def test_r_2_invalid_input(self):
        """Test r_2 with invalid input."""
        with self.assertRaises(ValueError):
            self.calc.r_2_sum_of_squares(0)
        with self.assertRaises(ValueError):
            self.calc.r_2_sum_of_squares(-1)
    
    def test_divisor_bound_verification(self):
        """Test divisor bound d(k) ≪_ε k^ε."""
        k_vals, ratios = self.calc.divisor_bound_verification(k_max=100, epsilon=0.1)
        
        # Should have 100 values
        self.assertEqual(len(k_vals), 100)
        self.assertEqual(len(ratios), 100)
        
        # Ratios should be bounded (subpolynomial growth)
        max_ratio = max(ratios)
        self.assertLess(max_ratio, 10)  # Reasonable bound for ε=0.1, k≤100
        
        # Ratios should be positive
        self.assertTrue(all(r > 0 for r in ratios))
    
    def test_r_n_multiplicity_2d(self):
        """Test r_n multiplicity for n=2."""
        # Should match r_2_sum_of_squares
        for k in [1, 2, 5, 10, 13]:
            expected = self.calc.r_2_sum_of_squares(k)
            actual = self.calc.r_n_multiplicity(k, n=2, method='theoretical')
            self.assertEqual(expected, actual, f"Mismatch at k={k}")
    
    def test_r_n_multiplicity_4d(self):
        """Test r_n multiplicity for n=4 (Jacobi's four-square theorem)."""
        # Known values
        # r_4(1) = 8 (any number can be written as sum of 4 squares)
        r_1 = self.calc.r_n_multiplicity(1, n=4, method='theoretical')
        self.assertEqual(r_1, 8)
        
        # r_4(k) should always be positive for k > 0
        for k in range(1, 20):
            r_k = self.calc.r_n_multiplicity(k, n=4, method='theoretical')
            self.assertGreater(r_k, 0, f"r_4({k}) should be positive")
    
    def test_verify_multiplicity_bound_2d(self):
        """Test 2D multiplicity bound (max = 24 for nonzero eigenvalues)."""
        result = self.calc.verify_multiplicity_bound_2d(k_max=100)
        
        self.assertIn('k_max', result)
        self.assertIn('max_multiplicity_observed', result)
        self.assertIn('bound_24_holds', result)
        self.assertIn('violations', result)
        
        # Bound should hold for k ≤ 100
        self.assertTrue(result['bound_24_holds'])
        self.assertEqual(len(result['violations']), 0)
        self.assertLessEqual(result['max_multiplicity_observed'], 24)
    
    def test_correlate_multiplicity_with_divisors(self):
        """Test correlation analysis between r_n(k) and d(k)."""
        result = self.calc.correlate_multiplicity_with_divisors(k_max=50)
        
        self.assertIn('k_max', result)
        self.assertIn('data', result)
        self.assertIn('pearson_correlation', result)
        self.assertIn('mean_ratio_r_to_d', result)
        
        # Should have data for k=1..50
        self.assertEqual(len(result['data']), 50)
        
        # Correlation should be a valid number between -1 and 1
        corr = result['pearson_correlation']
        self.assertGreaterEqual(corr, -1.0)
        self.assertLessEqual(corr, 1.0)
        
        # Mean ratio should be positive
        self.assertGreater(result['mean_ratio_r_to_d'], 0)
    
    def test_count_representations_bruteforce_small(self):
        """Test brute force counting for small k."""
        # r_2(5) = 8
        count = self.calc.count_representations_bruteforce(k=5, n=2, max_coord=10)
        self.assertEqual(count, 8)
        
        # r_3(9) should include (±3,0,0), (0,±3,0), (0,0,±3) and permutations
        count_3d = self.calc.count_representations_bruteforce(k=9, n=3, max_coord=10)
        self.assertGreater(count_3d, 0)
    
    def test_r_n_invalid_input(self):
        """Test r_n with invalid input."""
        with self.assertRaises(ValueError):
            self.calc.r_n_multiplicity(0, n=2)
        with self.assertRaises(ValueError):
            self.calc.r_n_multiplicity(-5, n=2)
        with self.assertRaises(ValueError):
            self.calc.r_n_multiplicity(5, n=0)
        with self.assertRaises(ValueError):
            self.calc.r_n_multiplicity(5, n=-1)


class TestDivisorProperties(unittest.TestCase):
    """Test mathematical properties of divisor function."""
    
    def test_divisor_multiplicativity(self):
        """Test that d(mn) ≥ d(m) for coprime m,n."""
        calc = EigenvalueMultiplicityCalculator()
        
        # For coprime m, n: d(mn) = d(m) * d(n)
        m, n = 3, 5  # coprime
        d_m = calc.divisor_function(m)
        d_n = calc.divisor_function(n)
        d_mn = calc.divisor_function(m * n)
        
        self.assertEqual(d_mn, d_m * d_n)
    
    def test_divisor_prime_powers(self):
        """Test d(p^k) = k+1 for prime p."""
        calc = EigenvalueMultiplicityCalculator()
        
        # d(2^k) = k+1
        self.assertEqual(calc.divisor_function(2**1), 2)  # d(2) = 2
        self.assertEqual(calc.divisor_function(2**2), 3)  # d(4) = 3
        self.assertEqual(calc.divisor_function(2**3), 4)  # d(8) = 4
        
        # d(3^k) = k+1
        self.assertEqual(calc.divisor_function(3**1), 2)  # d(3) = 2
        self.assertEqual(calc.divisor_function(3**2), 3)  # d(9) = 3
        self.assertEqual(calc.divisor_function(3**3), 4)  # d(27) = 4


if __name__ == '__main__':
    unittest.main()
