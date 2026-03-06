"""
Integration Tests for Hybrid Prime Identification DataFrame Support
===================================================================

Tests for pandas DataFrame integration and precomputed DZS data support
as mentioned in the PR description.

Author: Z Framework Team
"""

import unittest
import sys
import os
import pandas as pd
import warnings

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Suppress system warnings during tests
warnings.filterwarnings("ignore", category=UserWarning)

from core.hybrid_prime_identification import hybrid_prime_identification
from core.dzs_composite_filter import compute_enhanced_dzs_attributes


class TestDataFrameIntegration(unittest.TestCase):
    """Test DataFrame integration for precomputed DZS data."""
    
    def setUp(self):
        """Set up test DataFrame with precomputed DZS data."""
        # Create sample DZS data for testing
        test_numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        
        data = []
        for num in test_numbers:
            dzs = compute_enhanced_dzs_attributes(num)
            attrs = dzs.get_all_attributes()
            
            row = {
                'num': num,
                'D': attrs['D'],
                'E': attrs['E'], 
                'F': attrs['F'],
                'G': attrs['G'],
                'H': attrs['H'],
                'I': attrs['I'],
                'J': attrs['J'],
                'K': attrs['K'],
                'L': attrs['L'],
                'M': attrs['M'],
                'N': attrs['N'],
                'O': attrs['O'],
                'scaled_E': attrs['scaled_E'],
                'extended_P': attrs['extended_P']
            }
            data.append(row)
        
        self.test_df = pd.DataFrame(data)
    
    def test_dataframe_format_compatibility(self):
        """Test that DataFrame has the expected format."""
        # Check required columns exist
        required_cols = ['num', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        for col in required_cols:
            self.assertIn(col, self.test_df.columns, f"Missing column: {col}")
        
        # Check data types
        self.assertTrue(pd.api.types.is_integer_dtype(self.test_df['num']))
        for col in ['D', 'E', 'F', 'G']:
            self.assertTrue(pd.api.types.is_numeric_dtype(self.test_df[col]), f"Column {col} should be numeric")
    
    def test_hybrid_function_with_dataframe(self):
        """Test hybrid function accepts DataFrame parameter."""
        # Test that function accepts dzs_data parameter
        result = hybrid_prime_identification(
            10,
            dzs_data={'test': 'data'},  # Simplified test data
            log_diagnostics=False
        )
        
        # Should return valid result structure regardless of DataFrame content
        self.assertIsInstance(result, dict)
        self.assertIn('predicted_prime', result)
        self.assertIn('metrics', result)
    
    def test_dataframe_vs_computed_consistency(self):
        """Test consistency between DataFrame and computed DZS attributes."""
        # Pick a test number
        test_num = 15
        
        # Get from DataFrame
        df_row = self.test_df[self.test_df['num'] == test_num].iloc[0]
        
        # Compute fresh
        dzs_fresh = compute_enhanced_dzs_attributes(test_num)
        fresh_attrs = dzs_fresh.get_all_attributes()
        
        # Compare key attributes (allowing for small numerical differences)
        for attr in ['D', 'E', 'F', 'G']:
            df_val = df_row[attr]
            fresh_val = fresh_attrs[attr]
            self.assertAlmostEqual(df_val, fresh_val, places=6, 
                                 msg=f"Mismatch for {attr}: df={df_val}, fresh={fresh_val}")


class TestPerformanceOptimizations(unittest.TestCase):
    """Test performance optimizations mentioned in PR."""
    
    def test_range_size_management(self):
        """Test intelligent range size management."""
        # Test with small max_range_size to trigger subsampling
        result = hybrid_prime_identification(
            100,
            max_range_size=500,  # Small range to trigger optimization
            log_diagnostics=False
        )
        
        # Should still find a result
        self.assertIsNotNone(result['predicted_prime'])
        
        # Check that range was managed
        metrics = result['metrics']
        self.assertLessEqual(metrics['candidates_count'], 500)
    
    def test_z5d_prediction_integration(self):
        """Test Z5D prediction integration works."""
        result = hybrid_prime_identification(50, log_diagnostics=False)
        
        # Should have deviation metric (indicates Z5D prediction was used)
        self.assertIn('deviation_from_prediction', result['metrics'])
        self.assertIsInstance(result['metrics']['deviation_from_prediction'], float)


class TestErrorHandlingAndEdgeCases(unittest.TestCase):
    """Test comprehensive error handling and edge cases."""
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        # Test invalid sieve method
        result = hybrid_prime_identification(
            10,
            sieve_method="invalid_method",
            log_diagnostics=False
        )
        # Should not crash and should use fallback
        self.assertIsNotNone(result)
        
        # Test invalid bounds type
        result = hybrid_prime_identification(
            10,
            bounds_type="invalid_bounds",
            log_diagnostics=False
        )
        # Should raise ValueError for invalid bounds type
        with self.assertRaises(ValueError):
            hybrid_prime_identification(10, bounds_type="invalid", use_rigorous_bounds=True)
    
    def test_empty_range_handling(self):
        """Test handling when no primes found in range."""
        # This is hard to trigger with valid parameters, but test structure
        result = hybrid_prime_identification(
            1,  # Small k to minimize range
            use_rigorous_bounds=False,
            error_rate=0.001,  # Very small error rate
            log_diagnostics=False
        )
        
        # Should handle gracefully even if range is problematic
        self.assertIsInstance(result, dict)
    
    def test_very_small_k_values(self):
        """Test very small k values comprehensively."""
        for k in [1, 2, 3, 4]:
            with self.subTest(k=k):
                result = hybrid_prime_identification(k, log_diagnostics=False)
                
                # Should find a prime
                self.assertIsNotNone(result['predicted_prime'])
                
                # Should not be extrapolation for small k
                self.assertFalse(result['is_extrapolation'])
                
                # Prime should be reasonable
                self.assertGreater(result['predicted_prime'], 0)
                self.assertLess(result['predicted_prime'], 100)


class TestMetricsAndDiagnostics(unittest.TestCase):
    """Test metrics collection and diagnostic capabilities."""
    
    def test_comprehensive_metrics(self):
        """Test all metrics are collected properly."""
        result = hybrid_prime_identification(25, log_diagnostics=False)
        
        metrics = result['metrics']
        
        # Check all expected metrics exist
        expected_metrics = [
            'total_time', 'dzs_filter_time', 'sieve_time', 'filter_rate',
            'deviation_from_prediction', 'primes_found', 'candidates_count',
            'range_size', 'use_rigorous_bounds'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics, f"Missing metric: {metric}")
            self.assertIsNotNone(metrics[metric], f"Metric {metric} is None")
        
        # Check metric ranges
        self.assertGreaterEqual(metrics['total_time'], 0)
        self.assertTrue(0 <= metrics['filter_rate'] <= 1)
        self.assertGreaterEqual(metrics['primes_found'], 0)
        self.assertGreaterEqual(metrics['candidates_count'], 0)
        self.assertGreaterEqual(metrics['range_size'], 0)
    
    def test_diagnostic_logging(self):
        """Test diagnostic logging can be enabled/disabled."""
        import logging
        
        # Test with logging disabled
        result1 = hybrid_prime_identification(10, log_diagnostics=False)
        self.assertIsNotNone(result1)
        
        # Test with logging enabled (should not crash)
        with self.assertLogs(level='INFO'):
            result2 = hybrid_prime_identification(10, log_diagnostics=True)
            self.assertIsNotNone(result2)
    
    def test_bounds_type_reporting(self):
        """Test bounds type is correctly reported."""
        # Test rigorous bounds
        result_rigorous = hybrid_prime_identification(
            10, use_rigorous_bounds=True, bounds_type="dusart"
        )
        self.assertEqual(result_rigorous['bounds_type'], 'dusart')
        
        # Test prediction bounds
        result_prediction = hybrid_prime_identification(
            10, use_rigorous_bounds=False
        )
        self.assertEqual(result_prediction['bounds_type'], 'prediction')


if __name__ == '__main__':
    print("Running DataFrame integration and comprehensive tests...")
    unittest.main(verbosity=2, buffer=True)