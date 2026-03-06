#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Z5D Inverse Mersenne Factorization
=================================================

Comprehensive test suite validating the Z5D inverse factorization hypothesis
and benchmarking against baseline methods.

**RESEARCH/HYPOTHESIS TESTING ONLY**
"""

import unittest
import numpy as np
import time
import logging
from typing import List, Tuple
import warnings

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.z_framework.cryptography.z5d_inverse_factorization import (
    Z5DInverseFactorizer,
    FactorizationResult, 
    generate_test_semiprimes,
    validate_z5d_factorization_hypothesis
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestZ5DInverseFactorizer(unittest.TestCase):
    """
    Test suite for Z5D-based semiprime factorization.
    
    Tests both the mathematical correctness and performance characteristics
    of the inverse factorization approach.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.factorizer = Z5DInverseFactorizer(precision_dps=50, geodesic_calibration=0.3)
        
        # Test semiprimes with known factors (small for quick testing)
        self.small_test_cases = [
            (15, 3, 5),      # 4-bit
            (21, 3, 7),      # 5-bit
            (33, 3, 11),     # 6-bit
            (35, 5, 7),      # 6-bit
            (51, 3, 17),     # 6-bit
            (57, 3, 19),     # 6-bit
            (77, 7, 11),     # 7-bit
            (85, 5, 17),     # 7-bit
            (87, 3, 29),     # 7-bit
            (91, 7, 13),     # 7-bit
        ]
        
        # Medium test cases for performance testing
        self.medium_test_cases = [
            (203, 7, 29),         # ~8-bit
            (323, 17, 19),        # 9-bit  
            (437, 19, 23),        # 9-bit
            (493, 17, 29),        # 9-bit
            (667, 23, 29),        # 10-bit
            (713, 23, 31),        # 10-bit
            (899, 29, 31),        # 10-bit
            (1073, 29, 37),       # 11-bit
            (1147, 31, 37),       # 11-bit
            (1271, 31, 41),       # 11-bit
        ]
    
    def test_initialization(self):
        """Test factorizer initialization."""
        factorizer = Z5DInverseFactorizer(precision_dps=40, geodesic_calibration=0.25)
        self.assertEqual(factorizer.precision_dps, 40)
        self.assertEqual(factorizer.geodesic_k, 0.25)
        self.assertAlmostEqual(factorizer.phi, (1 + np.sqrt(5)) / 2, places=10)
        self.assertEqual(factorizer.mersenne_bias, 0.04449)
    
    def test_prime_index_estimation(self):
        """Test inverse prime index estimation."""
        # Test known small primes
        test_cases = [
            (2, 1),      # Approximate: p_1 = 2
            (3, 2),      # Approximate: p_2 = 3  
            (5, 3),      # Approximate: p_3 = 5
            (7, 4),      # Approximate: p_4 = 7
            (11, 5),     # Approximate: p_5 = 11
            (13, 6),     # Approximate: p_6 = 13
        ]
        
        for prime, expected_index in test_cases:
            estimated_k = self.factorizer._estimate_prime_index(prime)
            # Allow reasonable tolerance for estimation
            self.assertAlmostEqual(estimated_k, expected_index, delta=2.0,
                                 msg=f"Prime {prime} index estimation failed")
    
    def test_geodesic_search_pattern(self):
        """Test geodesic search pattern generation."""
        center_k = 100.0
        search_radius = 10
        
        pattern = self.factorizer._geodesic_search_pattern(center_k, search_radius)
        
        # Check pattern properties
        self.assertIsInstance(pattern, list)
        self.assertGreater(len(pattern), 0)
        self.assertLessEqual(len(pattern), 2 * search_radius + 1)
        
        # Check all indices are positive
        self.assertTrue(all(k > 0 for k in pattern))
        
        # Check search radius is respected (approximately)
        min_k = min(pattern)
        max_k = max(pattern)
        self.assertGreaterEqual(min_k, center_k - search_radius - 1)
        self.assertLessEqual(max_k, center_k + search_radius + 1)
    
    def test_mersenne_structural_bias(self):
        """Test Mersenne structural bias calculation."""
        # Test various prime types
        test_primes = [3, 7, 31, 127, 17, 19, 23, 29]
        
        for p in test_primes:
            bias = self.factorizer._mersenne_structural_bias(p)
            
            # Bias should be positive
            self.assertGreater(bias, 0)
            
            # Bias should be reasonable (not extreme)
            self.assertLess(bias, 2.0)
        
        # Mersenne primes should have higher bias
        mersenne_primes = [3, 7, 31, 127]  # 2^2-1, 2^3-1, 2^5-1, 2^7-1
        non_mersenne_primes = [17, 19, 23, 29]
        
        avg_mersenne_bias = np.mean([self.factorizer._mersenne_structural_bias(p) 
                                   for p in mersenne_primes])
        avg_non_mersenne_bias = np.mean([self.factorizer._mersenne_structural_bias(p) 
                                       for p in non_mersenne_primes])
        
        # Mersenne primes should generally have higher bias
        self.assertGreater(avg_mersenne_bias, avg_non_mersenne_bias)
    
    def test_small_semiprime_factorization(self):
        """Test factorization on small semiprimes."""
        successes = 0
        total_trials = 0
        
        for n, expected_p1, expected_p2 in self.small_test_cases:
            with self.subTest(n=n):
                result = self.factorizer.factor_semiprime(n, max_trials=1000, timeout_seconds=30)
                
                total_trials += result.trials
                
                if result.success:
                    successes += 1
                    
                    # Check factors are correct
                    factors = sorted(result.factors)
                    expected_factors = sorted([expected_p1, expected_p2])
                    self.assertEqual(factors, expected_factors, 
                                   f"Incorrect factors for {n}: got {factors}, expected {expected_factors}")
                    
                    # Check factorization is valid
                    self.assertEqual(factors[0] * factors[1], n)
                    
                    # Check performance metrics
                    self.assertGreater(result.trials, 0)
                    self.assertGreater(result.time_seconds, 0)
                    self.assertIn(result.method, ["z5d_inverse_mersenne", "z5d_small_hybrid"])
                else:
                    logger.warning(f"Failed to factor {n} = {expected_p1} × {expected_p2}")
        
        # We should have reasonable success rate on small semiprimes
        success_rate = successes / len(self.small_test_cases)
        logger.info(f"Small semiprime success rate: {success_rate:.1%} ({successes}/{len(self.small_test_cases)})")
        self.assertGreater(success_rate, 0.6, "Success rate too low on small semiprimes")
    
    def test_medium_semiprime_factorization(self):
        """Test factorization on medium-sized semiprimes."""
        successes = 0
        total_reduction = 0
        reduction_count = 0
        
        for n, expected_p1, expected_p2 in self.medium_test_cases[:5]:  # Test subset for speed
            with self.subTest(n=n):
                result = self.factorizer.factor_semiprime(n, max_trials=2000, timeout_seconds=60)
                
                if result.success:
                    successes += 1
                    
                    # Check factors are correct
                    factors = sorted(result.factors)
                    expected_factors = sorted([expected_p1, expected_p2])
                    self.assertEqual(factors, expected_factors)
                    
                    # Track search space reduction
                    if result.search_space_reduction is not None:
                        total_reduction += result.search_space_reduction
                        reduction_count += 1
                else:
                    logger.warning(f"Failed to factor {n} = {expected_p1} × {expected_p2}")
        
        success_rate = successes / min(5, len(self.medium_test_cases))
        logger.info(f"Medium semiprime success rate: {success_rate:.1%}")
        
        if reduction_count > 0:
            avg_reduction = total_reduction / reduction_count
            logger.info(f"Average search space reduction: {avg_reduction:.1%}")
    
    def test_trivial_cases(self):
        """Test handling of trivial cases."""
        # Even number
        result = self.factorizer.factor_semiprime(14)
        self.assertTrue(result.success)
        self.assertEqual(sorted(result.factors), [2, 7])
        self.assertEqual(result.method, "trivial_even")
        
        # Very small numbers
        result = self.factorizer.factor_semiprime(1)
        self.assertFalse(result.success)
        self.assertEqual(result.method, "trivial")
        
        result = self.factorizer.factor_semiprime(2)
        self.assertFalse(result.success)
        self.assertEqual(result.method, "trivial")
    
    def test_timeout_handling(self):
        """Test timeout functionality."""
        # Use a larger semiprime that might timeout
        n = 1073  # 29 × 37
        
        # Very short timeout to force timeout
        result = self.factorizer.factor_semiprime(n, timeout_seconds=0.001)
        
        # Should handle timeout gracefully
        self.assertIsInstance(result, FactorizationResult)
        self.assertLessEqual(result.time_seconds, 0.1)  # Should timeout quickly
    
    def test_max_trials_handling(self):
        """Test max trials limitation."""
        n = 1073  # 29 × 37
        
        # Very low trial limit
        result = self.factorizer.factor_semiprime(n, max_trials=5)
        
        # Should respect trial limit
        self.assertLessEqual(result.trials, 5)
        self.assertIsInstance(result, FactorizationResult)


class TestTestDataGeneration(unittest.TestCase):
    """Test the test data generation utilities."""
    
    def test_generate_test_semiprimes(self):
        """Test semiprime generation for testing."""
        bit_lengths = [32, 64]
        count_per_length = 2
        
        test_cases = generate_test_semiprimes(bit_lengths, count_per_length)
        
        # Should generate expected number of cases
        self.assertGreater(len(test_cases), 0)
        self.assertLessEqual(len(test_cases), len(bit_lengths) * count_per_length)
        
        # Check structure of test cases
        for semiprime, p1, p2 in test_cases:
            # Verify it's actually a semiprime
            self.assertEqual(p1 * p2, semiprime)
            
            # Check bit length is approximately correct
            actual_bits = semiprime.bit_length()
            # Find the closest expected bit length with tolerance
            closest_expected = min(bit_lengths, key=lambda bl: abs(actual_bits - bl))
            self.assertLessEqual(abs(actual_bits - closest_expected), 6)  # Increased tolerance


class TestBenchmarking(unittest.TestCase):
    """Test benchmarking functionality."""
    
    def setUp(self):
        """Set up benchmarking tests."""
        self.factorizer = Z5DInverseFactorizer(precision_dps=50)
        
        # Small test semiprimes for quick benchmarking
        self.benchmark_cases = [15, 21, 33, 35, 51, 77, 85, 91]
    
    def test_benchmark_against_baseline(self):
        """Test benchmarking against baseline methods."""
        results = self.factorizer.benchmark_against_baseline(
            self.benchmark_cases, 
            baseline_method="trial_division"
        )
        
        # Check result structure
        self.assertIn('z5d_results', results)
        self.assertIn('baseline_results', results) 
        self.assertIn('comparison', results)
        
        # Check we have results for each test case
        self.assertEqual(len(results['z5d_results']), len(self.benchmark_cases))
        self.assertEqual(len(results['baseline_results']), len(self.benchmark_cases))
        
        # Check comparison metrics
        comparison = results['comparison']
        required_metrics = [
            'z5d_success_rate', 'baseline_success_rate',
            'avg_trials_reduction', 'avg_time_reduction'
        ]
        for metric in required_metrics:
            self.assertIn(metric, comparison)
            self.assertIsInstance(comparison[metric], (int, float))
        
        logger.info(f"Benchmark results: Z5D success rate {comparison['z5d_success_rate']:.1%}, "
                   f"trials reduction {comparison['avg_trials_reduction']:.1%}")


class TestHypothesisValidation(unittest.TestCase):
    """Test the overall hypothesis validation."""
    
    def test_hypothesis_validation_structure(self):
        """Test the structure of hypothesis validation results."""
        # Run with very small test cases to keep test fast
        validation = validate_z5d_factorization_hypothesis(max_bit_length=64)
        
        # Check result structure
        required_keys = [
            'hypothesis_validated', 'target_reduction', 'achieved_reduction',
            'test_cases_count', 'detailed_results', 'conclusion'
        ]
        for key in required_keys:
            self.assertIn(key, validation)
        
        # Check types
        self.assertIsInstance(validation['hypothesis_validated'], bool)
        self.assertIsInstance(validation['target_reduction'], float)
        self.assertIsInstance(validation['achieved_reduction'], (int, float))
        self.assertIsInstance(validation['test_cases_count'], int)
        self.assertIsInstance(validation['conclusion'], str)
        
        # Log results
        logger.info(f"Hypothesis validation: {validation['conclusion']}")
    
    def test_research_warning(self):
        """Test that appropriate research warnings are issued."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # This should trigger the research warning
            validate_z5d_factorization_hypothesis(max_bit_length=64)
            
            # Check that warning was issued
            warning_messages = [str(warning.message) for warning in w]
            research_warning_found = any("RESEARCH HYPOTHESIS ONLY" in msg for msg in warning_messages)
            self.assertTrue(research_warning_found, "Research warning not issued")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up error handling tests."""
        self.factorizer = Z5DInverseFactorizer()
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Negative numbers
        result = self.factorizer.factor_semiprime(-5)
        self.assertFalse(result.success)
        
        # Zero
        result = self.factorizer.factor_semiprime(0)
        self.assertFalse(result.success)
        
        # Prime numbers (not semiprimes)
        result = self.factorizer.factor_semiprime(7, max_trials=100, timeout_seconds=5)
        # This should fail since 7 is prime, not semiprime
        self.assertFalse(result.success)
    
    def test_large_semiprime_handling(self):
        """Test behavior with large semiprimes."""
        # Use a known large semiprime
        large_semiprime = 1073 * 1009  # Two moderately large primes
        
        result = self.factorizer.factor_semiprime(
            large_semiprime, 
            max_trials=100,  # Low limit for test speed
            timeout_seconds=5
        )
        
        # Should handle gracefully (may or may not succeed)
        self.assertIsInstance(result, FactorizationResult)
        self.assertEqual(result.n, large_semiprime)


if __name__ == '__main__':
    # Configure test logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run tests
    unittest.main(verbosity=2)