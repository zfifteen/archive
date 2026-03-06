"""
Test Suite for Hybrid Prime Identification Function
==================================================

Comprehensive tests for the Z Framework hybrid prime identification implementation,
validating composite filtering, sieve functionality, and end-to-end performance.

Author: Z Framework Team
"""

import unittest
import sys
import os
import math
import logging

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.hybrid_prime_identification import (
    hybrid_prime_identification,
    compute_dzs_attributes,
    sieve_eratosthenes
)
from core.dzs_composite_filter import is_composite_via_dzs, DiscreteZetaShiftEnhanced


class TestHybridPrimeIdentification(unittest.TestCase):
    """Test cases for hybrid prime identification functionality."""
    
    def setUp(self):
        """Set up test logging."""
        logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    def test_is_composite_via_dzs_basic(self):
        """Test basic composite filtering with known values."""
        # Test case that should trigger composite filter (high b value)
        composite_attrs = DiscreteZetaShiftAttributes(
            b=8.0,  # Above threshold of 7.421869961235438
            c=7.389, z=1000.0, D=1.0, E=5.0, F=0.01, G=10.0,
            H=0.001, I=1.0, J=0.001, K=50.0, L=0.0001, M=1.0, N=0.0001, O=8000.0
        )
        
        self.assertTrue(is_composite_via_dzs(composite_attrs))
        
        # Test case that should not trigger filter (prime-like values)
        prime_attrs = DiscreteZetaShiftAttributes(
            b=3.0,  # Below threshold
            c=7.389, z=1000.0, D=1.0, E=5.0, F=0.01, G=10.0,
            H=0.001, I=1.0, J=0.001, K=50.0, L=0.0001, M=1.0, N=0.0001, O=8000.0
        )
        
        self.assertFalse(is_composite_via_dzs(prime_attrs))
    
    def test_is_composite_via_dzs_e_threshold(self):
        """Test E threshold filtering specifically."""
        # E < 1.9911567147873084 should trigger composite
        low_e_attrs = DiscreteZetaShiftAttributes(
            b=3.0, c=7.389, z=1000.0, D=1.0, 
            E=1.5,  # Below threshold
            F=0.01, G=10.0, H=0.001, I=1.0, J=0.001, K=50.0, L=0.0001, M=1.0, N=0.0001, O=8000.0
        )
        
        self.assertTrue(is_composite_via_dzs(low_e_attrs))
        
        # E >= threshold should not trigger this rule
        high_e_attrs = DiscreteZetaShiftAttributes(
            b=3.0, c=7.389, z=1000.0, D=1.0,
            E=3.0,  # Above threshold  
            F=0.01, G=10.0, H=0.001, I=1.0, J=0.001, K=50.0, L=0.0001, M=1.0, N=0.0001, O=8000.0
        )
        
        self.assertFalse(is_composite_via_dzs(high_e_attrs))
    
    def test_sieve_eratosthenes(self):
        """Test traditional sieve functionality."""
        # Test with small range including known primes
        candidates = [97, 98, 99, 100, 101]
        primes = sieve_eratosthenes(candidates)
        expected = [97, 101]  # Known primes in range
        self.assertEqual(primes, expected)
        
        # Test with empty list
        self.assertEqual(sieve_eratosthenes([]), [])
        
        # Test with no primes
        composites = [4, 6, 8, 9, 10]
        self.assertEqual(sieve_eratosthenes(composites), [])
    
    def test_compute_dzs_attributes(self):
        """Test DZS attribute computation."""
        # Test with a small prime
        attrs = compute_dzs_attributes(7)
        self.assertIsInstance(attrs, DiscreteZetaShiftAttributes)
        self.assertIsInstance(attrs.b, float)
        self.assertIsInstance(attrs.E, float)
        
        # Verify we get reasonable values (not inf or nan)
        self.assertFalse(math.isinf(attrs.b))
        self.assertFalse(math.isnan(attrs.b))
        self.assertFalse(math.isinf(attrs.E))
        self.assertFalse(math.isnan(attrs.E))
    
    def test_hybrid_prime_identification_small_k(self):
        """Test hybrid function with small k value."""
        # Test k=10 (10th prime is 29)
        result = hybrid_prime_identification(10, error_rate=0.01)
        
        # Verify return structure
        self.assertIn('predicted_prime', result)
        self.assertIn('range', result)
        self.assertIn('filtered_candidates_count', result)
        self.assertIn('is_extrapolation', result)
        self.assertIn('metrics', result)
        
        # Check types
        self.assertIsInstance(result['predicted_prime'], (int, type(None)))
        self.assertIsInstance(result['range'], tuple)
        self.assertIsInstance(result['filtered_candidates_count'], int)
        self.assertIsInstance(result['is_extrapolation'], bool)
        self.assertIsInstance(result['metrics'], dict)
        
        # For k=10, should not be extrapolation
        self.assertFalse(result['is_extrapolation'])
        
        # Should find a prime
        self.assertIsNotNone(result['predicted_prime'])
        
        # Prime should be reasonable (near 29)
        if result['predicted_prime']:
            self.assertTrue(20 <= result['predicted_prime'] <= 40)
    
    def test_hybrid_prime_identification_medium_k(self):
        """Test hybrid function with medium k value (k=100)."""
        # 100th prime is 541
        result = hybrid_prime_identification(100, error_rate=0.005)
        
        self.assertIsNotNone(result['predicted_prime'])
        self.assertFalse(result['is_extrapolation'])
        
        # Should be reasonably close to 541
        if result['predicted_prime']:
            self.assertTrue(500 <= result['predicted_prime'] <= 600)
    
    def test_hybrid_extrapolation_flag(self):
        """Test extrapolation flag for large k."""
        # k > 10^12 should trigger extrapolation
        k_large = 10**13
        result = hybrid_prime_identification(k_large, error_rate=0.001)
        
        self.assertTrue(result['is_extrapolation'])
        # Error rate should be scaled up for extrapolations
        self.assertGreaterEqual(result['uncertainty_bound'], 0.02)
    
    def test_error_handling(self):
        """Test error handling for edge cases."""
        # Test k=0 (should handle gracefully)
        result = hybrid_prime_identification(0)
        self.assertIsNotNone(result)  # Should not crash
        
        # Test k=1 (first prime is 2)
        result = hybrid_prime_identification(1)
        self.assertIsNotNone(result)
        if result['predicted_prime']:
            self.assertEqual(result['predicted_prime'], 2)
    
    def test_metrics_collection(self):
        """Test that performance metrics are collected properly."""
        result = hybrid_prime_identification(50)
        
        metrics = result['metrics']
        self.assertIn('total_time', metrics)
        self.assertIn('dzs_filter_time', metrics)
        self.assertIn('sieve_time', metrics)
        self.assertIn('filter_rate', metrics)
        
        # Times should be non-negative
        self.assertGreaterEqual(metrics['total_time'], 0)
        self.assertGreaterEqual(metrics['dzs_filter_time'], 0)
        self.assertGreaterEqual(metrics['sieve_time'], 0)
        
        # Filter rate should be between 0 and 1
        self.assertTrue(0 <= metrics['filter_rate'] <= 1)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for end-to-end scenarios."""
    
    def test_known_prime_validation(self):
        """Test against known k-th primes for validation."""
        known_cases = [
            (10, 29),   # 10th prime
            (25, 97),   # 25th prime  
            (50, 229),  # 50th prime
        ]
        
        for k, expected_prime in known_cases:
            with self.subTest(k=k):
                result = hybrid_prime_identification(k, error_rate=0.02)
                
                # Should find a prime
                self.assertIsNotNone(result['predicted_prime'], 
                                   f"Failed to find prime for k={k}")
                
                # Should be reasonably close to expected
                predicted = result['predicted_prime']
                if predicted:
                    deviation = abs(predicted - expected_prime) / expected_prime
                    self.assertLess(deviation, 0.1, 
                                  f"k={k}: predicted {predicted} vs expected {expected_prime}")
    
    def test_performance_benchmarks(self):
        """Test performance meets requirements."""
        # Test that function completes in reasonable time
        import time
        
        start_time = time.time()
        result = hybrid_prime_identification(1000, log_diagnostics=False)
        elapsed = time.time() - start_time
        
        # Should complete within 10 seconds for k=1000
        self.assertLess(elapsed, 10.0, "Performance requirement not met")
        
        # Should have reasonable filter rate (expect ~15-20% retention)
        filter_rate = result['metrics']['filter_rate']
        self.assertTrue(0.7 <= filter_rate <= 0.95, 
                       f"Filter rate {filter_rate} outside expected range")


if __name__ == '__main__':
    # Configure test output
    unittest.main(verbosity=2)