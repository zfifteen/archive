#!/usr/bin/env python3
"""
Comprehensive tests for enhanced hybrid prime identification functionality.

Tests the enhanced Z Framework hybrid prime identification system with:
- Rigorous bounds (Dusart/Axler)
- Deterministic Miller-Rabin primality testing
- Enhanced DiscreteZetaShift filtering
- Performance optimizations for large k values
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.hybrid_prime_identification import (
    hybrid_prime_identification,
    miller_rabin_deterministic,
    is_prime_optimized,
    compute_rigorous_bounds,
    compute_dusart_bounds,
    compute_axler_bounds,
    find_kth_prime_exact,
    prime_filter_miller_rabin
)


class TestHybridPrimeIdentificationEnhanced(unittest.TestCase):
    """Test suite for enhanced hybrid prime identification"""

    def test_miller_rabin_deterministic(self):
        """Test deterministic Miller-Rabin primality testing"""
        # Test known primes
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        for p in primes:
            self.assertTrue(miller_rabin_deterministic(p), f"{p} should be prime")
        
        # Test known composites
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28]
        for c in composites:
            self.assertFalse(miller_rabin_deterministic(c), f"{c} should be composite")
        
        # Test larger primes
        large_primes = [1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061]
        for p in large_primes:
            self.assertTrue(miller_rabin_deterministic(p), f"{p} should be prime")

    def test_is_prime_optimized(self):
        """Test optimized primality testing"""
        # Should match Miller-Rabin results
        test_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 17, 1009, 1013, 1024]
        for n in test_numbers:
            mr_result = miller_rabin_deterministic(n)
            opt_result = is_prime_optimized(n)
            self.assertEqual(mr_result, opt_result, f"Results should match for {n}")

    def test_rigorous_bounds(self):
        """Test rigorous bounds computation"""
        test_cases = [
            {'k': 100, 'expected_prime': 541},
            {'k': 500, 'expected_prime': 3571},
            {'k': 1000, 'expected_prime': 7919},
        ]
        
        for case in test_cases:
            k = case['k']
            expected = case['expected_prime']
            
            # Test Dusart bounds
            lower_d, upper_d = compute_dusart_bounds(k)
            self.assertLess(lower_d, expected, f"Dusart lower bound should be < {expected} for k={k}")
            self.assertGreater(upper_d, expected, f"Dusart upper bound should be > {expected} for k={k}")
            
            # Test rigorous bounds (auto selection)
            lower, upper = compute_rigorous_bounds(k, "auto")
            self.assertLess(lower, expected, f"Auto bounds lower should be < {expected} for k={k}")
            self.assertGreater(upper, expected, f"Auto bounds upper should be > {expected} for k={k}")
            self.assertIsInstance(lower, int, "Lower bound should be integer")
            self.assertIsInstance(upper, int, "Upper bound should be integer")

    def test_kth_prime_selection(self):
        """Test exact k-th prime selection logic"""
        # Generate some primes in a range
        primes_415_552 = [419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547]
        
        # Test selection for k=100 (100th prime is 541)
        selected = find_kth_prime_exact(primes_415_552, 100, 415)
        self.assertEqual(selected, 541, "Should select 541 as the 100th prime")
        
        # Test edge cases
        self.assertIsNone(find_kth_prime_exact([], 100, 415), "Should return None for empty list")
        self.assertEqual(find_kth_prime_exact([541], 100, 415), 541, "Should return single prime")

    def test_hybrid_function_accuracy(self):
        """Test hybrid function accuracy with known k-th primes"""
        test_cases = [
            {'k': 100, 'expected_prime': 541},
            {'k': 500, 'expected_prime': 3571},
        ]
        
        for case in test_cases:
            k = case['k']
            expected = case['expected_prime']
            
            with self.subTest(k=k):
                result = hybrid_prime_identification(
                    k,
                    use_rigorous_bounds=True,
                    bounds_type="auto",
                    sieve_method="miller_rabin",
                    log_diagnostics=False,
                    max_range_size=10000
                )
                
                # Check result structure
                self.assertIsInstance(result, dict, "Result should be a dictionary")
                self.assertIn('predicted_prime', result, "Result should contain predicted_prime")
                self.assertIn('metrics', result, "Result should contain metrics")
                
                # Check accuracy
                predicted = result['predicted_prime']
                self.assertEqual(predicted, expected, f"Should find correct {k}-th prime: {expected}")
                
                # Check metadata
                self.assertEqual(result['bounds_type'], 'auto', "Should use auto bounds")
                self.assertEqual(result['sieve_method'], 'miller_rabin', "Should use Miller-Rabin")
                self.assertTrue(result['metrics']['use_rigorous_bounds'], "Should use rigorous bounds")

    def test_hybrid_function_performance_modes(self):
        """Test different performance modes of hybrid function"""
        k = 100
        expected = 541
        
        # Test rigorous bounds mode
        result_rigorous = hybrid_prime_identification(
            k,
            use_rigorous_bounds=True,
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=1000
        )
        self.assertEqual(result_rigorous['predicted_prime'], expected, "Rigorous mode should be accurate")
        
        # Test prediction-based mode (fallback)
        result_prediction = hybrid_prime_identification(
            k,
            use_rigorous_bounds=False,
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=1000
        )
        # Prediction mode might not be as accurate, but should return a result
        self.assertIsNotNone(result_prediction['predicted_prime'], "Prediction mode should return a result")

    def test_bounds_types(self):
        """Test different bounds types"""
        k = 1000
        
        # Test Dusart bounds
        result_dusart = hybrid_prime_identification(
            k,
            use_rigorous_bounds=True,
            bounds_type="dusart",
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=5000
        )
        self.assertEqual(result_dusart['bounds_type'], 'dusart', "Should use Dusart bounds")
        
        # Test auto bounds selection
        result_auto = hybrid_prime_identification(
            k,
            use_rigorous_bounds=True,
            bounds_type="auto",
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=5000
        )
        self.assertEqual(result_auto['bounds_type'], 'auto', "Should use auto bounds selection")

    def test_performance_metrics(self):
        """Test that performance metrics are collected properly"""
        result = hybrid_prime_identification(
            100,
            use_rigorous_bounds=True,
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=1000
        )
        
        metrics = result['metrics']
        
        # Check that all expected metrics are present
        expected_metrics = [
            'total_time', 'dzs_filter_time', 'sieve_time', 'filter_rate',
            'deviation_from_prediction', 'primes_found', 'candidates_count',
            'range_size', 'use_rigorous_bounds'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics, f"Metric {metric} should be present")
        
        # Check metric types and ranges
        self.assertGreater(metrics['total_time'], 0, "Total time should be positive")
        self.assertGreaterEqual(metrics['filter_rate'], 0, "Filter rate should be non-negative")
        self.assertLessEqual(metrics['filter_rate'], 1, "Filter rate should be <= 1")
        self.assertGreater(metrics['primes_found'], 0, "Should find at least one prime")

    def test_error_handling(self):
        """Test error handling for edge cases"""
        # Test with very small k
        result_small = hybrid_prime_identification(
            1,
            use_rigorous_bounds=True,
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=100
        )
        self.assertEqual(result_small['predicted_prime'], 2, "First prime should be 2")
        
        # Test with k=2
        result_k2 = hybrid_prime_identification(
            2,
            use_rigorous_bounds=True,
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=100
        )
        self.assertEqual(result_k2['predicted_prime'], 3, "Second prime should be 3")


class TestPerformanceComparison(unittest.TestCase):
    """Performance comparison tests"""

    def test_miller_rabin_vs_traditional(self):
        """Compare Miller-Rabin vs traditional primality testing"""
        import time
        
        candidates = list(range(1000, 1100))
        
        # Test Miller-Rabin
        start_time = time.time()
        mr_primes = prime_filter_miller_rabin(candidates)
        mr_time = time.time() - start_time
        
        # Test traditional (using is_prime_optimized which falls back to trial division for small numbers)
        start_time = time.time()
        traditional_primes = [c for c in candidates if is_prime_optimized(c)]
        traditional_time = time.time() - start_time
        
        # Results should be the same
        self.assertEqual(set(mr_primes), set(traditional_primes), "Results should be identical")
        
        # Miller-Rabin should be reasonable (not necessarily faster for small numbers)
        self.assertGreater(mr_time, 0, "Miller-Rabin time should be measurable")
        self.assertGreater(traditional_time, 0, "Traditional time should be measurable")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)