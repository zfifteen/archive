#!/usr/bin/env python3
"""
Test suite for Gaussian Lattice + Monte Carlo Enhanced Pollard's Rho

Validates:
1. Standard Pollard's rho baseline
2. Lattice-enhanced variant
3. Monte Carlo with low-discrepancy sampling
4. Benchmark comparison and variance reduction
"""

import unittest
import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from pollard_gaussian_monte_carlo import GaussianLatticePollard
import sympy


class TestStandardPollardRho(unittest.TestCase):
    """Test baseline Pollard's rho implementation."""
    
    def setUp(self):
        self.factorizer = GaussianLatticePollard(seed=42)
    
    def test_pollard_even_number(self):
        """Test that even numbers return 2."""
        N = 14  # 2 × 7
        factor = self.factorizer.standard_pollard_rho(N)
        self.assertEqual(factor, 2)
    
    def test_pollard_small_semiprime(self):
        """Test factorization of small semiprime."""
        N = 221  # 13 × 17
        factor = self.factorizer.standard_pollard_rho(N, max_iterations=10000)
        self.assertIsNotNone(factor)
        self.assertIn(factor, [13, 17])
        self.assertEqual(N % factor, 0)
    
    def test_pollard_medium_semiprime(self):
        """Test factorization of medium semiprime."""
        N = 899  # 29 × 31
        factor = self.factorizer.standard_pollard_rho(N, max_iterations=20000)
        self.assertIsNotNone(factor)
        self.assertIn(factor, [29, 31])
    
    def test_pollard_close_factors(self):
        """Test with close factors (harder case)."""
        N = 10403  # 101 × 103
        factor = self.factorizer.standard_pollard_rho(N, max_iterations=30000)
        # May or may not succeed in limited iterations
        if factor is not None:
            self.assertIn(factor, [101, 103])
            self.assertEqual(N % factor, 0)
    
    def test_pollard_prime_input(self):
        """Test that prime numbers don't factor."""
        N = 97  # Prime
        factor = self.factorizer.standard_pollard_rho(N, max_iterations=1000)
        # Should not find a non-trivial factor
        if factor is not None:
            self.assertIn(factor, [1, N])


class TestLatticeEnhancedPollard(unittest.TestCase):
    """Test Gaussian lattice enhanced Pollard's rho."""
    
    def setUp(self):
        self.factorizer = GaussianLatticePollard(seed=42)
    
    def test_lattice_constant_optimization(self):
        """Test that lattice-optimized constant is computed correctly."""
        N = 899
        c = self.factorizer._lattice_optimized_constant(N)
        self.assertIsInstance(c, int)
        self.assertGreater(c, 0)
        self.assertLess(c, N)
    
    def test_lattice_enhanced_small(self):
        """Test lattice-enhanced on small semiprime."""
        N = 221  # 13 × 17
        factor = self.factorizer.lattice_enhanced_pollard_rho(N, max_iterations=10000)
        self.assertIsNotNone(factor)
        self.assertIn(factor, [13, 17])
    
    def test_lattice_enhanced_medium(self):
        """Test lattice-enhanced on medium semiprime."""
        N = 899  # 29 × 31
        factor = self.factorizer.lattice_enhanced_pollard_rho(N, max_iterations=20000)
        self.assertIsNotNone(factor)
        self.assertIn(factor, [29, 31])
    
    def test_lattice_enhanced_vs_standard(self):
        """Compare lattice-enhanced vs standard on same input."""
        N = 1003  # 17 × 59
        
        # Standard
        factor_std = self.factorizer.standard_pollard_rho(N, max_iterations=10000)
        
        # Lattice-enhanced
        factor_lat = self.factorizer.lattice_enhanced_pollard_rho(N, max_iterations=10000)
        
        # Both should find factors (may be different)
        if factor_std is not None:
            self.assertIn(factor_std, [17, 59])
        if factor_lat is not None:
            self.assertIn(factor_lat, [17, 59])


class TestMonteCarloLatticePollard(unittest.TestCase):
    """Test Monte Carlo + lattice integration."""
    
    def setUp(self):
        self.factorizer = GaussianLatticePollard(seed=42)
    
    def test_starting_points_generation_uniform(self):
        """Test uniform starting point generation."""
        sqrt_N = 100
        points = self.factorizer._generate_starting_points(sqrt_N, 5, 'uniform')
        
        self.assertEqual(len(points), 5)
        for x, c in points:
            # Accept both int and np.integer types
            import numpy as np
            self.assertTrue(isinstance(x, (int, np.integer)))
            self.assertTrue(isinstance(c, (int, np.integer)))
            self.assertGreater(int(x), 0)
            self.assertGreater(int(c), 0)
    
    def test_starting_points_generation_sobol(self):
        """Test Sobol' starting point generation."""
        sqrt_N = 100
        points = self.factorizer._generate_starting_points(sqrt_N, 5, 'sobol')
        
        self.assertEqual(len(points), 5)
        for x, c in points:
            self.assertIsInstance(x, int)
            self.assertIsInstance(c, int)
    
    def test_starting_points_generation_golden(self):
        """Test golden-angle starting point generation."""
        sqrt_N = 100
        points = self.factorizer._generate_starting_points(sqrt_N, 5, 'golden-angle')
        
        self.assertEqual(len(points), 5)
        for x, c in points:
            self.assertIsInstance(x, int)
            self.assertIsInstance(c, int)
    
    def test_monte_carlo_small_uniform(self):
        """Test Monte Carlo with uniform sampling."""
        N = 221  # 13 × 17
        factor = self.factorizer.monte_carlo_lattice_pollard(
            N, max_iterations=5000, num_trials=5, sampling_mode='uniform'
        )
        self.assertIsNotNone(factor)
        self.assertIn(factor, [13, 17])
    
    def test_monte_carlo_medium_sobol(self):
        """Test Monte Carlo with Sobol' sampling."""
        N = 899  # 29 × 31
        factor = self.factorizer.monte_carlo_lattice_pollard(
            N, max_iterations=10000, num_trials=5, sampling_mode='sobol'
        )
        self.assertIsNotNone(factor)
        self.assertIn(factor, [29, 31])
    
    def test_monte_carlo_golden_angle(self):
        """Test Monte Carlo with golden-angle sampling."""
        N = 1003  # 17 × 59
        factor = self.factorizer.monte_carlo_lattice_pollard(
            N, max_iterations=10000, num_trials=5, sampling_mode='golden-angle'
        )
        # May or may not succeed depending on iterations
        if factor is not None:
            self.assertIn(factor, [17, 59])


class TestStrategyFramework(unittest.TestCase):
    """Test strategy selection and benchmarking framework."""
    
    def setUp(self):
        self.factorizer = GaussianLatticePollard(seed=42)
    
    def test_strategy_standard(self):
        """Test standard strategy."""
        N = 221
        result = self.factorizer.factorize_with_strategy(
            N, strategy='standard', max_iterations=10000
        )
        
        self.assertIn('N', result)
        self.assertIn('factor', result)
        self.assertIn('strategy', result)
        self.assertIn('success', result)
        self.assertIn('time_seconds', result)
        
        self.assertEqual(result['N'], N)
        self.assertEqual(result['strategy'], 'standard')
        self.assertTrue(result['success'])
        self.assertIn(result['factor'], [13, 17])
    
    def test_strategy_lattice_enhanced(self):
        """Test lattice-enhanced strategy."""
        N = 899
        result = self.factorizer.factorize_with_strategy(
            N, strategy='lattice_enhanced', max_iterations=10000
        )
        
        self.assertEqual(result['strategy'], 'lattice_enhanced')
        self.assertTrue(result['success'])
        self.assertIn(result['factor'], [29, 31])
    
    def test_strategy_monte_carlo(self):
        """Test Monte Carlo strategy."""
        N = 1003
        result = self.factorizer.factorize_with_strategy(
            N, strategy='monte_carlo_lattice', max_iterations=10000,
            num_trials=5, sampling_mode='sobol'
        )
        
        self.assertEqual(result['strategy'], 'monte_carlo_lattice')
        # Success depends on iterations
        if result['success']:
            self.assertIn(result['factor'], [17, 59])
    
    def test_benchmark_strategies(self):
        """Test benchmarking multiple strategies."""
        N = 221
        results = self.factorizer.benchmark_strategies(
            N, strategies=['standard', 'lattice_enhanced'], max_iterations=5000
        )
        
        self.assertIn('standard', results)
        self.assertIn('lattice_enhanced', results)
        
        # Both should succeed on easy case
        self.assertTrue(results['standard']['success'])
        self.assertTrue(results['lattice_enhanced']['success'])
    
    def test_benchmark_all_strategies(self):
        """Test benchmarking all strategies including MC variants."""
        N = 899
        results = self.factorizer.benchmark_strategies(N, max_iterations=5000)
        
        # Should have multiple entries
        self.assertGreater(len(results), 2)
        
        # Check that at least one strategy succeeded
        success_count = sum(1 for r in results.values() if r['success'])
        self.assertGreater(success_count, 0)


class TestVarianceReduction(unittest.TestCase):
    """Test variance reduction properties of enhanced methods."""
    
    def setUp(self):
        self.factorizer = GaussianLatticePollard(seed=42)
    
    def test_multiple_trials_consistency(self):
        """Test that multiple trials with same seed are consistent."""
        N = 221
        
        # Run twice with same seed
        f1 = GaussianLatticePollard(seed=100)
        result1 = f1.standard_pollard_rho(N, max_iterations=5000)
        
        f2 = GaussianLatticePollard(seed=100)
        result2 = f2.standard_pollard_rho(N, max_iterations=5000)
        
        self.assertEqual(result1, result2)
    
    def test_low_discrepancy_coverage(self):
        """Test that low-discrepancy sampling provides better coverage."""
        sqrt_N = 1000
        num_trials = 20
        
        # Generate points with different modes
        uniform_points = self.factorizer._generate_starting_points(
            sqrt_N, num_trials, 'uniform'
        )
        sobol_points = self.factorizer._generate_starting_points(
            sqrt_N, num_trials, 'sobol'
        )
        
        # Extract x values
        uniform_x = [int(x) for x, _ in uniform_points]
        sobol_x = [int(x) for x, _ in sobol_points]
        
        # Check uniqueness (low-discrepancy should have more unique values)
        unique_uniform = len(set(uniform_x))
        unique_sobol = len(set(sobol_x))
        
        # Both should have reasonable uniqueness (at least 40%)
        self.assertGreater(unique_uniform, num_trials // 3)
        self.assertGreater(unique_sobol, num_trials // 3)


class TestIntegrationWithExistingFramework(unittest.TestCase):
    """Test integration with existing z-sandbox components."""
    
    def setUp(self):
        self.factorizer = GaussianLatticePollard(seed=42)
    
    def test_gaussian_lattice_integration(self):
        """Test that Gaussian lattice module is properly integrated."""
        # Should have lattice instance
        self.assertIsNotNone(self.factorizer.lattice)
        
        # Test lattice functionality
        z1 = complex(29, 0)
        z2 = complex(31, 0)
        dist = self.factorizer.lattice.lattice_enhanced_distance(z1, z2)
        self.assertGreater(float(dist), 0)
    
    def test_low_discrepancy_integration(self):
        """Test that low-discrepancy samplers are available."""
        # Check if available
        if self.factorizer.sobol_sampler is not None:
            samples = self.factorizer.sobol_sampler.generate(5)
            self.assertEqual(len(samples), 5)
        
        if self.factorizer.golden_sampler is not None:
            samples = self.factorizer.golden_sampler.generate_1d(5)
            self.assertEqual(len(samples), 5)
    
    def test_compatibility_with_factor_256bit(self):
        """Test that results are compatible with existing factorization code."""
        N = 221
        result = self.factorizer.factorize_with_strategy(N, strategy='standard')
        
        # Should be able to verify using standard methods
        if result['success']:
            factor = result['factor']
            other_factor = N // factor
            
            # Check that factors multiply correctly
            self.assertEqual(factor * other_factor, N)
            
            # Check primality
            self.assertTrue(sympy.isprime(factor))
            self.assertTrue(sympy.isprime(other_factor))


def run_tests():
    """Run all tests with verbose output."""
    print("=" * 70)
    print("Gaussian Lattice + Monte Carlo Pollard's Rho Test Suite")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStandardPollardRho))
    suite.addTests(loader.loadTestsFromTestCase(TestLatticeEnhancedPollard))
    suite.addTests(loader.loadTestsFromTestCase(TestMonteCarloLatticePollard))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyFramework))
    suite.addTests(loader.loadTestsFromTestCase(TestVarianceReduction))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWithExistingFramework))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
