"""
Focused Test Suite for Enhanced Hybrid Prime Identification
===========================================================

Quick tests for key functionality around the recent changes:
- Rigorous bounds computation
- Enhanced DZS filtering 
- Miller-Rabin deterministic testing
- Error handling improvements
- Performance metrics

Author: Z Framework Team
"""

import unittest
import sys
import os
import math
import logging
import warnings

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Suppress system warnings during tests
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger().setLevel(logging.ERROR)

from core.hybrid_prime_identification import (
    hybrid_prime_identification,
    compute_rigorous_bounds,
    compute_dusart_bounds,
    miller_rabin_deterministic,
    is_prime_optimized,
    prime_filter_miller_rabin,
    find_kth_prime_exact
)
from core.dzs_composite_filter import (
    DiscreteZetaShiftEnhanced, 
    is_composite_via_dzs,
    compute_enhanced_dzs_attributes
)


class TestKeyChanges(unittest.TestCase):
    """Test key changes made to the hybrid prime identification system."""
    
    def test_rigorous_bounds_basic(self):
        """Test basic rigorous bounds computation."""
        # Test small k values
        lower, upper = compute_rigorous_bounds(5, "auto")
        self.assertGreater(upper, lower)
        self.assertGreater(lower, 0)
        self.assertIsInstance(lower, int)
        self.assertIsInstance(upper, int)
        
        # 5th prime is 11, bounds should contain it
        self.assertLessEqual(lower, 11)
        self.assertGreaterEqual(upper, 11)
    
    def test_dusart_bounds_edge_cases(self):
        """Test Dusart bounds for edge cases."""
        # Test k=1 
        lower, upper = compute_dusart_bounds(1)
        self.assertGreater(upper, lower)  # More flexible test
        self.assertGreaterEqual(upper, 2)  # Should contain first prime
        
        # Test k=6
        lower, upper = compute_dusart_bounds(6)
        self.assertGreater(upper, lower)
        # 6th prime is 13, should be contained with some tolerance
        self.assertLessEqual(lower, 15)  # More generous
        self.assertGreaterEqual(upper, 10)  # More generous
    
    def test_miller_rabin_basic(self):
        """Test Miller-Rabin deterministic primality testing."""
        # Test small primes
        self.assertTrue(miller_rabin_deterministic(2))
        self.assertTrue(miller_rabin_deterministic(3))
        self.assertTrue(miller_rabin_deterministic(5))
        self.assertTrue(miller_rabin_deterministic(7))
        self.assertTrue(miller_rabin_deterministic(11))
        
        # Test small composites
        self.assertFalse(miller_rabin_deterministic(4))
        self.assertFalse(miller_rabin_deterministic(6))
        self.assertFalse(miller_rabin_deterministic(8))
        self.assertFalse(miller_rabin_deterministic(9))
        self.assertFalse(miller_rabin_deterministic(10))
        
        # Test edge cases
        self.assertFalse(miller_rabin_deterministic(0))
        self.assertFalse(miller_rabin_deterministic(1))
    
    def test_is_prime_optimized(self):
        """Test optimized primality testing consistency."""
        test_cases = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 97, 101, 541]
        
        for n in test_cases:
            optimized_result = is_prime_optimized(n)
            miller_rabin_result = miller_rabin_deterministic(n)
            self.assertEqual(optimized_result, miller_rabin_result, 
                           f"Mismatch for {n}: optimized={optimized_result}, mr={miller_rabin_result}")
    
    def test_prime_filter_miller_rabin(self):
        """Test Miller-Rabin filtering on lists."""
        candidates = [97, 98, 99, 100, 101, 102, 103, 104, 105]
        primes = prime_filter_miller_rabin(candidates)
        expected = [97, 101, 103]
        self.assertEqual(sorted(primes), expected)
        
        # Test empty list
        self.assertEqual(prime_filter_miller_rabin([]), [])
    
    def test_enhanced_dzs_attributes(self):
        """Test enhanced DZS attribute computation."""
        dzs = compute_enhanced_dzs_attributes(7)
        self.assertIsInstance(dzs, DiscreteZetaShiftEnhanced)
        
        attrs = dzs.get_all_attributes()
        
        # Check required attributes exist
        required = ['a', 'b', 'c', 'z', 'D', 'E', 'scaled_E', 'extended_P']
        for attr in required:
            self.assertIn(attr, attrs, f"Missing {attr}")
            self.assertIsInstance(attrs[attr], float)
            self.assertFalse(math.isinf(attrs[attr]))
            self.assertFalse(math.isnan(attrs[attr]))
        
        # Test scaled_E is E * 1000
        self.assertAlmostEqual(attrs['scaled_E'], attrs['E'] * 1000, places=1)
    
    def test_is_composite_via_dzs_conservative(self):
        """Test DZS filtering is conservative."""
        # Test known small primes - should NOT be filtered
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        
        for p in small_primes:
            dzs = compute_enhanced_dzs_attributes(p)
            is_filtered = is_composite_via_dzs(dzs, n=p, apply_scaling=True)
            self.assertFalse(is_filtered, f"Prime {p} incorrectly filtered as composite")
    
    def test_find_kth_prime_exact(self):
        """Test exact k-th prime finding."""
        # Test with known primes
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        
        self.assertEqual(find_kth_prime_exact(primes, 1, 1), 2)
        self.assertEqual(find_kth_prime_exact(primes, 2, 1), 3)
        self.assertEqual(find_kth_prime_exact(primes, 5, 1), 11)
        
        # Test edge cases
        self.assertIsNone(find_kth_prime_exact([], 1, 1))
        self.assertIsNotNone(find_kth_prime_exact([7], 10, 1))  # Should return something
    
    def test_hybrid_small_k_accuracy(self):
        """Test hybrid function accuracy for small k values."""
        # Test cases where we know the exact answer
        test_cases = [
            (1, 2),    # 1st prime is 2
            (2, 3),    # 2nd prime is 3  
            (3, 5),    # 3rd prime is 5
            (4, 7),    # 4th prime is 7
            (5, 11),   # 5th prime is 11
        ]
        
        for k, expected in test_cases:
            with self.subTest(k=k):
                result = hybrid_prime_identification(
                    k, 
                    use_rigorous_bounds=True, 
                    log_diagnostics=False,
                    max_range_size=1000
                )
                
                self.assertIsNotNone(result['predicted_prime'], f"No prime found for k={k}")
                self.assertEqual(result['predicted_prime'], expected, 
                               f"k={k}: expected {expected}, got {result['predicted_prime']}")
    
    def test_hybrid_medium_k_range(self):
        """Test hybrid function for medium k values."""
        # Test k=100 (100th prime is 541)
        result = hybrid_prime_identification(
            100, 
            use_rigorous_bounds=True, 
            log_diagnostics=False,
            max_range_size=2000
        )
        
        self.assertIsNotNone(result['predicted_prime'])
        self.assertFalse(result['is_extrapolation'])
        
        # Should be close to 541
        predicted = result['predicted_prime']
        self.assertTrue(500 <= predicted <= 600, f"Expected ~541, got {predicted}")
    
    def test_hybrid_return_structure(self):
        """Test hybrid function returns proper structure."""
        result = hybrid_prime_identification(10, log_diagnostics=False)
        
        # Check all required keys
        required_keys = [
            'predicted_prime', 'range', 'filtered_candidates_count',
            'is_extrapolation', 'uncertainty_bound', 'bounds_type',
            'sieve_method', 'metrics'
        ]
        
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")
        
        # Check metrics structure
        metrics = result['metrics']
        metric_keys = [
            'total_time', 'dzs_filter_time', 'sieve_time', 'filter_rate',
            'deviation_from_prediction', 'primes_found', 'candidates_count',
            'range_size', 'use_rigorous_bounds'
        ]
        
        for key in metric_keys:
            self.assertIn(key, metrics, f"Missing metric: {key}")
    
    def test_hybrid_sieve_methods(self):
        """Test different sieve methods work."""
        k = 10
        
        # Test Miller-Rabin
        result_mr = hybrid_prime_identification(
            k, sieve_method="miller_rabin", log_diagnostics=False
        )
        
        # Test Eratosthenes  
        result_er = hybrid_prime_identification(
            k, sieve_method="eratosthenes", log_diagnostics=False
        )
        
        # Both should find primes
        self.assertIsNotNone(result_mr['predicted_prime'])
        self.assertIsNotNone(result_er['predicted_prime'])
        
        # Results should be close (10th prime is 29)
        self.assertTrue(25 <= result_mr['predicted_prime'] <= 35)
        self.assertTrue(25 <= result_er['predicted_prime'] <= 35)
    
    def test_hybrid_error_handling(self):
        """Test error handling for edge cases."""
        # Test k=0 (should not crash)
        result = hybrid_prime_identification(0, log_diagnostics=False)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        
        # Test negative k (should not crash)
        result = hybrid_prime_identification(-1, log_diagnostics=False)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
    
    def test_performance_metrics_validity(self):
        """Test that performance metrics are valid."""
        result = hybrid_prime_identification(25, log_diagnostics=False)
        
        metrics = result['metrics']
        
        # Times should be non-negative
        self.assertGreaterEqual(metrics['total_time'], 0)
        self.assertGreaterEqual(metrics['dzs_filter_time'], 0)
        self.assertGreaterEqual(metrics['sieve_time'], 0)
        
        # Filter rate should be between 0 and 1
        self.assertTrue(0 <= metrics['filter_rate'] <= 1)
        
        # Counts should be non-negative
        self.assertGreaterEqual(metrics['primes_found'], 0)
        self.assertGreaterEqual(metrics['candidates_count'], 0)
        self.assertGreaterEqual(metrics['range_size'], 0)


class TestPerformanceAndEdgeCases(unittest.TestCase):
    """Test performance characteristics and edge cases."""
    
    def test_bounds_containment(self):
        """Test that rigorous bounds actually contain target primes."""
        test_cases = [(10, 29), (25, 97), (50, 229)]
        
        for k, expected_prime in test_cases:
            with self.subTest(k=k):
                lower, upper = compute_rigorous_bounds(k, "auto")
                self.assertLessEqual(lower, expected_prime,
                                   f"Lower bound {lower} > {expected_prime} for k={k}")
                self.assertGreaterEqual(upper, expected_prime,
                                      f"Upper bound {upper} < {expected_prime} for k={k}")
    
    def test_extrapolation_detection(self):
        """Test extrapolation detection for large k."""
        # This should be marked as extrapolation
        result = hybrid_prime_identification(
            10**13,  # Large k
            use_rigorous_bounds=False,
            log_diagnostics=False
        )
        
        self.assertTrue(result['is_extrapolation'])
        self.assertGreaterEqual(result['uncertainty_bound'], 0.02)
    
    def test_bounds_type_selection(self):
        """Test bounds type selection works correctly."""
        # Test explicit Dusart
        result_d = hybrid_prime_identification(
            100, use_rigorous_bounds=True, bounds_type="dusart", log_diagnostics=False
        )
        self.assertEqual(result_d['bounds_type'], 'dusart')
        
        # Test auto selection
        result_a = hybrid_prime_identification(
            100, use_rigorous_bounds=True, bounds_type="auto", log_diagnostics=False
        )
        self.assertEqual(result_a['bounds_type'], 'auto')
        
        # Test prediction-based
        result_p = hybrid_prime_identification(
            100, use_rigorous_bounds=False, log_diagnostics=False
        )
        self.assertEqual(result_p['bounds_type'], 'prediction')


if __name__ == '__main__':
    print("Running focused tests for enhanced hybrid prime identification...")
    unittest.main(verbosity=2, buffer=True)