#!/usr/bin/env python3
"""
Test suite for PrimeGenerator class validating user findings and implementation.

This test suite validates:
1. Basic prime generation functionality
2. User-reported scenarios (overgen_factor=5 vs overgen_factor=50)
3. Dynamic adjustment behavior
4. k parameter sensitivity
5. Frame shift residues method correctness
"""

import sys
import os
import unittest
import numpy as np
from sympy import isprime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from applications.prime_generator import PrimeGenerator, PrimeGenerationResult


class TestPrimeGenerator(unittest.TestCase):
    """Test cases for PrimeGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = PrimeGenerator(k=0.3, auto_adjust=True)

    def test_basic_initialization(self):
        """Test basic generator initialization."""
        generator = PrimeGenerator()
        self.assertEqual(generator.k, 0.3)
        self.assertEqual(generator.default_overgen_factor, 10.0)
        self.assertEqual(generator.max_candidate, 10**6)
        self.assertTrue(generator.auto_adjust)

    def test_frame_shift_residues(self):
        """Test frame_shift_residues method correctness."""
        # Test with known values
        indices = np.array([1, 2, 3, 4, 5])
        result = self.generator.frame_shift_residues(indices)
        
        # Should return array of same length
        self.assertEqual(len(result), len(indices))
        
        # All values should be positive and bounded by phi
        self.assertTrue(np.all(result > 0))
        self.assertTrue(np.all(result <= self.generator.phi))
        
        # Test with different k values
        result_k1 = self.generator.frame_shift_residues(indices, k=1.0)
        result_k05 = self.generator.frame_shift_residues(indices, k=0.5)
        
        # Results should be different for different k values
        self.assertFalse(np.array_equal(result_k1, result_k05))

    def test_user_reported_scenario_overgen_5(self):
        """Test user-reported scenario with overgen_factor=5."""
        # This should trigger auto-adjustment
        result = self.generator.generate_primes(
            num_primes=10, 
            overgen_factor=5.0,
            max_candidate=10**6
        )
        
        # Should successfully generate 10 primes despite low initial factor
        self.assertEqual(len(result.primes), 10)
        self.assertEqual(result.success_rate, 1.0)
        
        # Should have auto-adjusted the overgen_factor
        if self.generator.auto_adjust:
            self.assertGreater(result.overgen_factor_used, 5.0)
        
        # All results should be prime
        for prime in result.primes:
            self.assertTrue(isprime(prime), f"{prime} is not prime")

    def test_user_reported_scenario_overgen_50(self):
        """Test user-reported scenario with overgen_factor=50."""
        result = self.generator.generate_primes(
            num_primes=10, 
            overgen_factor=50.0,
            max_candidate=10**6
        )
        
        # Should successfully generate 10 primes
        self.assertEqual(len(result.primes), 10)
        self.assertEqual(result.success_rate, 1.0)
        
        # Should use the specified overgen_factor (or close to it)
        self.assertLessEqual(abs(result.overgen_factor_used - 50.0), 5.0)
        
        # All results should be prime
        for prime in result.primes:
            self.assertTrue(isprime(prime), f"{prime} is not prime")

    def test_auto_adjustment_disabled(self):
        """Test behavior with auto-adjustment disabled."""
        generator = PrimeGenerator(auto_adjust=False)
        
        # With very low overgen_factor and no auto-adjustment,
        # might not achieve target (but should not crash)
        result = generator.generate_primes(
            num_primes=10, 
            overgen_factor=2.0
        )
        
        # Should not auto-adjust
        self.assertEqual(result.overgen_factor_used, 2.0)
        
        # May or may not achieve full target, but should be reasonable
        self.assertGreaterEqual(len(result.primes), 0)
        self.assertLessEqual(len(result.primes), 10)

    def test_k_parameter_sensitivity(self):
        """Test sensitivity to k parameter changes."""
        k_values = [0.1, 0.3, 0.5]
        results = {}
        
        for k in k_values:
            generator = PrimeGenerator(k=k, auto_adjust=True)
            result = generator.generate_primes(num_primes=5)
            results[k] = result
            
            # Should generate target number of primes
            self.assertEqual(len(result.primes), 5)
            
            # All should be prime
            for prime in result.primes:
                self.assertTrue(isprime(prime))
        
        # Different k values should potentially give different results
        primes_01 = set(results[0.1].primes)
        primes_03 = set(results[0.3].primes)
        primes_05 = set(results[0.5].primes)
        
        # At least some primes should be different (not a strict requirement,
        # but likely given the randomness)
        total_unique = len(primes_01 | primes_03 | primes_05)
        total_primes = len(primes_01) + len(primes_03) + len(primes_05)
        uniqueness_ratio = total_unique / total_primes
        
        # Expect some diversity (this is probabilistic)
        self.assertGreater(uniqueness_ratio, 0.6)

    def test_overgen_factor_estimation(self):
        """Test the overgen_factor estimation algorithm."""
        # Test different scenarios
        test_cases = [
            (5, 10**6, "small_target"),
            (10, 10**6, "medium_target"),
            (20, 10**6, "large_target"),
            (10, 10**7, "large_range"),
        ]
        
        for num_primes, max_candidate, description in test_cases:
            with self.subTest(case=description):
                estimated = self.generator._estimate_required_overgen_factor(
                    num_primes, max_candidate
                )
                
                # Should be within reasonable bounds
                self.assertGreaterEqual(estimated, 5.0)
                self.assertLessEqual(estimated, 100.0)
                
                # Larger targets should generally need larger factors
                if num_primes > 10:
                    self.assertGreater(estimated, 10.0)

    def test_prime_generation_result_structure(self):
        """Test that PrimeGenerationResult contains expected data."""
        result = self.generator.generate_primes(num_primes=5)
        
        # Check result structure
        self.assertIsInstance(result, PrimeGenerationResult)
        self.assertIsInstance(result.primes, list)
        self.assertIsInstance(result.candidates_generated, int)
        self.assertIsInstance(result.overgen_factor_used, float)
        self.assertIsInstance(result.generation_time, float)
        self.assertIsInstance(result.success_rate, float)
        self.assertIsInstance(result.k_parameter, float)
        self.assertIsInstance(result.max_candidate, int)
        
        # Check value ranges
        self.assertGreaterEqual(result.success_rate, 0.0)
        self.assertLessEqual(result.success_rate, 1.0)
        self.assertGreater(result.generation_time, 0.0)
        self.assertGreater(result.candidates_generated, 0)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with num_primes=1
        result = self.generator.generate_primes(num_primes=1)
        self.assertEqual(len(result.primes), 1)
        self.assertTrue(isprime(result.primes[0]))
        
        # Test with larger num_primes
        result = self.generator.generate_primes(num_primes=25)
        self.assertEqual(len(result.primes), 25)
        for prime in result.primes:
            self.assertTrue(isprime(prime))

    def test_reproducibility_with_fixed_seed(self):
        """Test that results can be made reproducible with fixed random seed."""
        # Set numpy random seed
        np.random.seed(42)
        result1 = self.generator.generate_primes(num_primes=5, overgen_factor=20.0)
        
        # Reset seed and generate again
        np.random.seed(42)
        result2 = self.generator.generate_primes(num_primes=5, overgen_factor=20.0)
        
        # Results should be identical with same seed and parameters
        self.assertEqual(result1.primes, result2.primes)

    def test_validation_configuration(self):
        """Test the validate_configuration method."""
        k_values = [0.2, 0.3, 0.4]
        results = self.generator.validate_configuration(k_values, num_primes=3)
        
        # Should return results for all k values
        self.assertEqual(len(results), len(k_values))
        
        for k in k_values:
            self.assertIn(k, results)
            result = results[k]
            self.assertEqual(len(result.primes), 3)
            self.assertEqual(result.k_parameter, k)


def run_performance_benchmarks():
    """Run performance benchmarks and print results."""
    print("\n=== Performance Benchmarks ===")
    
    generator = PrimeGenerator()
    
    # Benchmark different scenarios
    benchmarks = [
        (5, "Small (5 primes)"),
        (10, "Medium (10 primes)"),
        (25, "Large (25 primes)"),
    ]
    
    for num_primes, description in benchmarks:
        result = generator.generate_primes(num_primes=num_primes)
        print(f"{description}:")
        print(f"  Time: {result.generation_time:.3f}s")
        print(f"  Overgen factor: {result.overgen_factor_used:.1f}")
        print(f"  Candidates: {result.candidates_generated}")
        print(f"  Success rate: {result.success_rate:.1%}")


if __name__ == "__main__":
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmarks
    run_performance_benchmarks()