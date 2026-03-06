#!/usr/bin/env python3
"""
Test suite for Z5DHarness as specified in issue #638.

This test validates the exact interface and functionality requested
in the problem statement for the Z5DHarness class.
"""

import unittest
import numpy as np
import sys
import os
import warnings

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from applications.z5d_harness import Z5DHarness
    HARNESS_AVAILABLE = True
except ImportError as e:
    HARNESS_AVAILABLE = False
    print(f"Warning: Z5DHarness not available: {e}")


class TestZ5DHarness(unittest.TestCase):
    """Test cases for Z5DHarness class as specified in issue #638."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not HARNESS_AVAILABLE:
            self.skipTest("Z5DHarness not available")
        
        # Suppress warnings for cleaner test output
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        
        # Initialize harness instances for different modes
        self.harness_vectorized = Z5DHarness(mode='vectorized')
        self.harness_hybrid = Z5DHarness(mode='hybrid', threshold=1e6)
        self.harness_scalar = Z5DHarness(mode='scalar')
    
    def test_harness_initialization(self):
        """Test Z5DHarness initialization with different configurations."""
        # Test default initialization
        harness = Z5DHarness()
        self.assertEqual(harness.mode, 'vectorized')
        self.assertEqual(harness.threshold, 1e6)
        
        # Test custom initialization
        harness_custom = Z5DHarness(mode='hybrid', threshold=5e5)
        self.assertEqual(harness_custom.mode, 'hybrid')
        self.assertEqual(harness_custom.threshold, 5e5)
        
        # Test scalar mode
        harness_scalar = Z5DHarness(mode='scalar')
        self.assertEqual(harness_scalar.mode, 'scalar')
    
    def test_z5d_prime_scalar_input(self):
        """Test z5d_prime method with scalar input."""
        k = 1000.0
        result = self.harness_vectorized.z5d_prime(k)
        
        # Check result is reasonable
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        # The 1000th prime is 7919, so Z5D should be in reasonable range
        self.assertGreater(result, 5000)
        self.assertLess(result, 15000)
    
    def test_z5d_prime_array_input(self):
        """Test z5d_prime method with array input."""
        k_values = np.array([100, 500, 1000])
        result = self.harness_vectorized.z5d_prime(k_values)
        
        # Check result shape and properties
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), 3)
        self.assertTrue(np.all(result > 0))
        # Results should be monotonically increasing
        self.assertTrue(np.all(np.diff(result) > 0))
    
    def test_z5d_prime_modes_consistency(self):
        """Test that different modes produce consistent results."""
        k_values = np.array([100, 500])
        
        result_vectorized = self.harness_vectorized.z5d_prime(k_values)
        result_hybrid = self.harness_hybrid.z5d_prime(k_values)
        result_scalar = self.harness_scalar.z5d_prime(k_values)
        
        # Results should be close but may differ slightly due to precision
        np.testing.assert_allclose(result_vectorized, result_hybrid, rtol=1e-3)
        np.testing.assert_allclose(result_vectorized, result_scalar, rtol=1e-3)
    
    def test_z5d_prime_edge_cases(self):
        """Test z5d_prime with edge cases."""
        # Test with k < 16 (should return 0)
        small_k = np.array([1, 5, 10])
        result = self.harness_vectorized.z5d_prime(small_k)
        self.assertTrue(np.all(result == 0))
        
        # Test with single large value
        large_k = 1e7
        result = self.harness_scalar.z5d_prime(large_k)
        self.assertGreater(result, 0)
    
    def test_crypto_metrics(self):
        """Test crypto_metrics method."""
        # Test with default batch size
        metrics = self.harness_vectorized.crypto_metrics()
        
        # Check required keys
        required_keys = ['ks', 'chi2', 'mi', 'auc']
        for key in required_keys:
            self.assertIn(key, metrics)
        
        # Check value types and ranges
        self.assertIsInstance(metrics['ks'], (float, np.floating))
        self.assertIsInstance(metrics['chi2'], (float, np.floating))
        self.assertIsInstance(metrics['mi'], (float, np.floating))
        # AUC might be NaN due to single class
        
        # KS statistic should be non-negative
        self.assertGreaterEqual(metrics['ks'], 0)
        
        # Chi-squared should be non-negative
        self.assertGreaterEqual(metrics['chi2'], 0)
        
        # Test with custom batch size
        small_metrics = self.harness_vectorized.crypto_metrics(batch_size=100)
        self.assertEqual(len(small_metrics), len(required_keys))
    
    def test_bio_metrics(self):
        """Test bio_metrics method."""
        # Test with default number of sequences
        correlation = self.harness_vectorized.bio_metrics()
        
        # Check result type and range
        self.assertIsInstance(correlation, (float, np.floating))
        # Correlation should be between -1 and 1
        self.assertGreaterEqual(correlation, -1.0)
        self.assertLessEqual(correlation, 1.0)
        
        # Test with custom number of sequences
        small_correlation = self.harness_vectorized.bio_metrics(num_seqs=20)
        self.assertIsInstance(small_correlation, (float, np.floating))
        self.assertGreaterEqual(small_correlation, -1.0)
        self.assertLessEqual(small_correlation, 1.0)
    
    def test_hybrid_mode_threshold_behavior(self):
        """Test hybrid mode threshold switching behavior."""
        # Create harness with low threshold
        low_threshold_harness = Z5DHarness(mode='hybrid', threshold=100)
        
        # Test with values below and above threshold
        low_k = np.array([10])  # Below mask threshold (< 16)
        med_k = np.array([50])  # Above mask threshold, below switching threshold
        high_k = np.array([1000])  # Above switching threshold
        
        result_low = low_threshold_harness.z5d_prime(low_k)
        result_med = low_threshold_harness.z5d_prime(med_k)
        result_high = low_threshold_harness.z5d_prime(high_k)
        
        # Low k should return 0 (below mask threshold of 16)
        self.assertEqual(result_low[0], 0)
        # Medium and high should return valid results
        self.assertGreater(result_med[0], 0)
        self.assertGreater(result_high[0], 0)
    
    def test_performance_characteristics(self):
        """Test basic performance characteristics."""
        import time
        
        # Test vectorized mode performance
        k_values = np.arange(100, 1100)  # 1000 values
        
        start_time = time.time()
        result = self.harness_vectorized.z5d_prime(k_values)
        vectorized_time = time.time() - start_time
        
        # Test scalar mode performance
        start_time = time.time()
        scalar_results = []
        for k in k_values[:100]:  # Only test subset for scalar to avoid timeout
            scalar_results.append(self.harness_scalar.z5d_prime(k))
        scalar_time = time.time() - start_time
        
        # Vectorized should generally be faster for large arrays
        # (though this may not always hold for small arrays due to overhead)
        self.assertGreater(len(result), 0)
        self.assertEqual(len(scalar_results), 100)
        
        print(f"Vectorized time for 1000 values: {vectorized_time:.6f}s")
        print(f"Scalar time for 100 values: {scalar_time:.6f}s")
    
    def test_interface_compliance(self):
        """Test that the interface matches the problem statement exactly."""
        # Test exact method signatures from problem statement
        harness = Z5DHarness(mode='vectorized', threshold=1e6)
        
        # Test z5d_prime method
        self.assertTrue(hasattr(harness, 'z5d_prime'))
        self.assertTrue(callable(harness.z5d_prime))
        
        # Test crypto_metrics method
        self.assertTrue(hasattr(harness, 'crypto_metrics'))
        self.assertTrue(callable(harness.crypto_metrics))
        crypto_result = harness.crypto_metrics(batch_size=1000)
        self.assertIsInstance(crypto_result, dict)
        
        # Test bio_metrics method
        self.assertTrue(hasattr(harness, 'bio_metrics'))
        self.assertTrue(callable(harness.bio_metrics))
        bio_result = harness.bio_metrics(num_seqs=100)
        self.assertIsInstance(bio_result, (float, np.floating))


class TestZ5DHarnessIntegration(unittest.TestCase):
    """Integration tests for Z5DHarness with broader ecosystem."""
    
    def test_example_usage_from_problem_statement(self):
        """Test the exact example usage from the problem statement."""
        if not HARNESS_AVAILABLE:
            self.skipTest("Z5DHarness not available")
        
        # Suppress warnings for cleaner output
        warnings.filterwarnings("ignore")
        
        # Example usage from problem statement
        harness = Z5DHarness(mode='vectorized')
        crypto_met = harness.crypto_metrics()
        bio_r = harness.bio_metrics()
        
        # Verify results are returned
        self.assertIsInstance(crypto_met, dict)
        self.assertIsInstance(bio_r, (float, np.floating))
        
        # Print results as in the example
        print("Crypto metrics:", crypto_met)
        print("Bio correlation:", bio_r)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)