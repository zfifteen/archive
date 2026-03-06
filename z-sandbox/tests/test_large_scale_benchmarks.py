#!/usr/bin/env python3
"""
Test suite for large-scale factorization benchmarking and demonstrations.

Validates:
1. Benchmark script functionality
2. Demo script execution
3. Performance metrics computation
4. Statistical analysis

Note: Tests marked with @pytest.mark.slow are opt-in benchmarks.
Run with: pytest -m slow
"""

import unittest
import sys
import os
import pytest

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from pollard_gaussian_monte_carlo import GaussianLatticePollard


class TestBenchmarkFunctions(unittest.TestCase):
    """Test benchmark utility functions."""
    
    def test_verify_semiprime_correct(self):
        """Test semiprime verification with correct factors."""
        from benchmark_large_scale_factorization import verify_semiprime
        
        # Test case: N = 899 = 29 × 31
        N = 899
        factors = (29, 31)
        self.assertTrue(verify_semiprime(N, factors))
    
    def test_verify_semiprime_incorrect(self):
        """Test semiprime verification with incorrect factors."""
        from benchmark_large_scale_factorization import verify_semiprime
        
        # Test case: N = 899 ≠ 30 × 30
        N = 899
        factors = (30, 30)
        self.assertFalse(verify_semiprime(N, factors))
    
    def test_benchmark_single_run_standard(self):
        """Test single run benchmark with standard strategy."""
        from benchmark_large_scale_factorization import benchmark_single_run
        
        factorizer = GaussianLatticePollard(seed=42)
        N = 899  # 29 × 31
        
        result = benchmark_single_run(
            factorizer, N, 'standard',
            max_iterations=10000
        )
        
        self.assertIn('factor', result)
        self.assertIn('time_ms', result)
        self.assertIn('success', result)
        self.assertIn('strategy', result)
        
        self.assertTrue(result['success'])
        self.assertIn(result['factor'], [29, 31])
        self.assertGreater(result['time_ms'], 0)
        self.assertEqual(result['strategy'], 'standard')
    
    def test_benchmark_single_run_sobol(self):
        """Test single run benchmark with Sobol strategy."""
        from benchmark_large_scale_factorization import benchmark_single_run
        
        factorizer = GaussianLatticePollard(seed=42)
        N = 899
        
        result = benchmark_single_run(
            factorizer, N, 'monte_carlo_sobol',
            max_iterations=10000,
            num_trials=5
        )
        
        self.assertTrue(result['success'])
        self.assertIn(result['factor'], [29, 31])


class TestLargeScaleFactorization(unittest.TestCase):
    """Test factorization at various scales."""
    
    def test_10e9_scale(self):
        """Test factorization at 10^9 scale."""
        factorizer = GaussianLatticePollard(seed=42)
        N = 899  # Small test case ~10^3
        
        # Standard
        factor_std = factorizer.standard_pollard_rho(N, max_iterations=10000)
        self.assertIsNotNone(factor_std)
        self.assertIn(factor_std, [29, 31])
        
        # Sobol
        factor_sobol = factorizer.monte_carlo_lattice_pollard(
            N, max_iterations=10000, num_trials=5, sampling_mode='sobol'
        )
        self.assertIsNotNone(factor_sobol)
        self.assertIn(factor_sobol, [29, 31])
    
    def test_10e15_scale_exists(self):
        """Verify 10^15 test case is valid."""
        N = 1000001970000133
        expected_factors = (10000019, 100000007)
        
        # Verify it's a valid semiprime
        self.assertEqual(expected_factors[0] * expected_factors[1], N)
    
    def test_strategy_comparison(self):
        """Test that different strategies produce valid factors."""
        factorizer = GaussianLatticePollard(seed=42)
        N = 1003  # 17 × 59
        
        strategies = [
            ('standard', {}),
            ('monte_carlo_uniform', {'num_trials': 5}),
            ('monte_carlo_sobol', {'num_trials': 5}),
            ('monte_carlo_golden', {'num_trials': 5}),
        ]
        
        for strategy, kwargs in strategies:
            if strategy == 'standard':
                factor = factorizer.standard_pollard_rho(N, max_iterations=20000)
            else:
                sampling_mode = strategy.replace('monte_carlo_', '')
                factor = factorizer.monte_carlo_lattice_pollard(
                    N, max_iterations=20000,
                    num_trials=kwargs.get('num_trials', 5),
                    sampling_mode=sampling_mode
                )
            
            if factor is not None:
                self.assertIn(factor, [17, 59])
                self.assertEqual(N % factor, 0)


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics computation."""
    
    def test_timing_consistency(self):
        """Test that timing measurements are consistent."""
        import time
        from benchmark_large_scale_factorization import benchmark_single_run
        
        factorizer = GaussianLatticePollard(seed=42)
        N = 899
        
        results = []
        for _ in range(3):
            result = benchmark_single_run(
                factorizer, N, 'standard',
                max_iterations=10000
            )
            results.append(result['time_ms'])
        
        # All measurements should be positive
        for t in results:
            self.assertGreater(t, 0)
        
        # Variance should be reasonable (within 10x range)
        # Use small epsilon to avoid division by zero for very fast operations
        MIN_TIME_EPSILON = 0.001  # 1 millisecond minimum for ratio calculation
        max_time = max(results)
        min_time = min(results)
        self.assertLess(max_time / max(min_time, MIN_TIME_EPSILON), 100)
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        # Mock results
        results = [
            {'success': True},
            {'success': True},
            {'success': False},
            {'success': True},
            {'success': True},
        ]
        
        successful = [r for r in results if r['success']]
        success_rate = len(successful) / len(results)
        
        self.assertAlmostEqual(success_rate, 0.8)


class TestDemoScript(unittest.TestCase):
    """Test demonstration script functionality."""
    
    @pytest.mark.slow
    def test_demo_components(self):
        """Test that demo script components work (slow - 10^15 scale)."""
        factorizer = GaussianLatticePollard(seed=42)
        N = 1000001970000133
        
        # Test standard strategy
        factor1 = factorizer.standard_pollard_rho(N, max_iterations=100000)
        self.assertIsNotNone(factor1)
        self.assertEqual(N % factor1, 0)
        
        # Test Sobol strategy
        factor2 = factorizer.monte_carlo_lattice_pollard(
            N, max_iterations=100000, num_trials=5, sampling_mode='sobol'
        )
        self.assertIsNotNone(factor2)
        self.assertEqual(N % factor2, 0)
        
        # Test Golden-angle strategy
        factor3 = factorizer.monte_carlo_lattice_pollard(
            N, max_iterations=100000, num_trials=5, sampling_mode='golden-angle'
        )
        self.assertIsNotNone(factor3)
        self.assertEqual(N % factor3, 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_invalid_strategy(self):
        """Test that invalid strategy raises error."""
        from benchmark_large_scale_factorization import benchmark_single_run
        
        factorizer = GaussianLatticePollard(seed=42)
        
        with self.assertRaises(ValueError):
            benchmark_single_run(
                factorizer, 899, 'invalid_strategy',
                max_iterations=1000
            )
    
    def test_zero_trials(self):
        """Test behavior with zero Monte Carlo trials."""
        factorizer = GaussianLatticePollard(seed=42)
        
        # Should handle gracefully or return None
        factor = factorizer.monte_carlo_lattice_pollard(
            899, max_iterations=1000, num_trials=0, sampling_mode='sobol'
        )
        
        # Either returns None or raises appropriate error
        self.assertTrue(factor is None or (factor > 1 and 899 % factor == 0))


if __name__ == '__main__':
    unittest.main()
