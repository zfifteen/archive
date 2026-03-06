#!/usr/bin/env python3
"""
Tests for SHA-256 Pattern Analyzer
===================================

Comprehensive test suite for the SHA-256 cryptographic pattern detection implementation
using the Z Framework's discrete domain analysis.
"""

import unittest
import hashlib
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/runner/work/unified-framework/unified-framework')

from src.core.sha256_pattern_analyzer import SHA256PatternAnalyzer
from src.core.domain import DiscreteZetaShift, E_SQUARED
import mpmath as mp

class TestSHA256PatternAnalyzer(unittest.TestCase):
    """Test suite for SHA256PatternAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = SHA256PatternAnalyzer()
        self.test_data = "test_input_string"
        self.test_sequence_length = 5
    
    def test_initialization(self):
        """Test proper initialization of SHA256PatternAnalyzer."""
        analyzer = SHA256PatternAnalyzer()
        self.assertIsNotNone(analyzer.delta_max)
        self.assertEqual(analyzer.hash_sequence, [])
        self.assertEqual(analyzer.integer_sequence, [])
        self.assertEqual(analyzer.discrete_derivatives, [])
        self.assertEqual(analyzer.zeta_shifts, [])
        
        # Test custom delta_max
        custom_analyzer = SHA256PatternAnalyzer(delta_max=10.0)
        self.assertEqual(custom_analyzer.delta_max, 10.0)
    
    def test_sha256_to_integer(self):
        """Test SHA-256 hash to integer conversion."""
        # Test with string input
        result = self.analyzer.sha256_to_integer("test")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, 2**256)
        
        # Test with bytes input
        result_bytes = self.analyzer.sha256_to_integer(b"test")
        self.assertEqual(result, result_bytes)
        
        # Test deterministic behavior
        result1 = self.analyzer.sha256_to_integer("identical_input")
        result2 = self.analyzer.sha256_to_integer("identical_input")
        self.assertEqual(result1, result2)
        
        # Test different inputs produce different outputs
        result_a = self.analyzer.sha256_to_integer("input_a")
        result_b = self.analyzer.sha256_to_integer("input_b")
        self.assertNotEqual(result_a, result_b)
    
    def test_generate_hash_sequence(self):
        """Test generation of hash sequences."""
        sequence = self.analyzer.generate_hash_sequence(self.test_data, self.test_sequence_length)
        
        # Verify sequence properties
        self.assertEqual(len(sequence), self.test_sequence_length)
        self.assertEqual(len(self.analyzer.hash_sequence), self.test_sequence_length)
        self.assertEqual(len(self.analyzer.integer_sequence), self.test_sequence_length)
        
        # Verify all elements are integers in valid range
        for val in sequence:
            self.assertIsInstance(val, int)
            self.assertGreaterEqual(val, 0)
            self.assertLess(val, 2**256)
        
        # Verify sequence is deterministic
        sequence2 = self.analyzer.generate_hash_sequence(self.test_data, self.test_sequence_length)
        self.assertEqual(sequence, sequence2)
    
    def test_compute_discrete_derivatives(self):
        """Test computation of discrete derivatives."""
        # Generate test sequence
        self.analyzer.generate_hash_sequence(self.test_data, self.test_sequence_length)
        
        # Compute derivatives
        derivatives = self.analyzer.compute_discrete_derivatives()
        
        # Verify derivative properties
        self.assertEqual(len(derivatives), self.test_sequence_length - 1)
        self.assertEqual(len(self.analyzer.discrete_derivatives), self.test_sequence_length - 1)
        
        # Verify derivative computation
        for i, derivative in enumerate(derivatives):
            expected = self.analyzer.integer_sequence[i + 1] - self.analyzer.integer_sequence[i]
            self.assertEqual(derivative, expected)
        
        # Test with custom sequence
        custom_sequence = [100, 150, 120, 200]
        custom_derivatives = self.analyzer.compute_discrete_derivatives(custom_sequence)
        expected_derivatives = [50, -30, 80]
        self.assertEqual(custom_derivatives, expected_derivatives)
        
        # Test error handling
        with self.assertRaises(ValueError):
            self.analyzer.compute_discrete_derivatives([100])  # Single element
    
    def test_map_to_discrete_zeta_shifts(self):
        """Test mapping derivatives to DiscreteZetaShift objects."""
        # Generate test data
        self.analyzer.generate_hash_sequence(self.test_data, self.test_sequence_length)
        self.analyzer.compute_discrete_derivatives()
        
        # Map to zeta shifts
        zeta_shifts = self.analyzer.map_to_discrete_zeta_shifts()
        
        # Verify mapping properties
        expected_length = self.test_sequence_length - 1
        self.assertEqual(len(zeta_shifts), expected_length)
        self.assertEqual(len(self.analyzer.zeta_shifts), expected_length)
        
        # Verify all objects are DiscreteZetaShift instances
        for dzs in zeta_shifts:
            self.assertIsInstance(dzs, DiscreteZetaShift)
            
            # Verify parameters match specification (a=256, b=e, c=e²)
            self.assertEqual(float(dzs.c), float(E_SQUARED))
        
        # Test error handling
        empty_analyzer = SHA256PatternAnalyzer()
        with self.assertRaises(ValueError):
            empty_analyzer.map_to_discrete_zeta_shifts()
    
    def test_extract_pattern_attributes(self):
        """Test extraction of pattern attributes from zeta shifts."""
        # Generate test data and map to zeta shifts
        self.analyzer.generate_hash_sequence(self.test_data, self.test_sequence_length)
        self.analyzer.compute_discrete_derivatives()
        self.analyzer.map_to_discrete_zeta_shifts()
        
        # Extract attributes
        attributes_list = self.analyzer.extract_pattern_attributes()
        
        # Verify attribute extraction
        expected_length = self.test_sequence_length - 1
        self.assertEqual(len(attributes_list), expected_length)
        
        # Verify each attribute dictionary
        for attrs in attributes_list:
            self.assertIsInstance(attrs, dict)
            
            # Check required keys from UniversalZetaShift
            required_keys = ['a', 'b', 'c', 'z', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
            for key in required_keys:
                self.assertIn(key, attrs)
            
            # Check SHA-256 specific attributes
            self.assertIn('bit_length', attrs)
            self.assertEqual(attrs['bit_length'], 256)
            self.assertIn('delta_max', attrs)
            self.assertEqual(attrs['delta_max'], self.analyzer.delta_max)
        
        # Test error handling
        empty_analyzer = SHA256PatternAnalyzer()
        with self.assertRaises(ValueError):
            empty_analyzer.extract_pattern_attributes()
    
    def test_compute_curvature_patterns(self):
        """Test curvature-based pattern detection computation."""
        # Generate complete analysis data
        self.analyzer.generate_hash_sequence(self.test_data, self.test_sequence_length)
        self.analyzer.compute_discrete_derivatives()
        self.analyzer.map_to_discrete_zeta_shifts()
        attributes_list = self.analyzer.extract_pattern_attributes()
        
        # Compute curvature patterns
        pattern_metrics = self.analyzer.compute_curvature_patterns(attributes_list)
        
        # Verify metrics structure
        required_metrics = [
            'num_samples', 'curvature_mean', 'curvature_std', 'curvature_min', 'curvature_max',
            'bounded_curvature_mean', 'bounded_curvature_std', 'low_curvature_ratio', 'pattern_detected'
        ]
        for metric in required_metrics:
            self.assertIn(metric, pattern_metrics)
        
        # Verify sample count
        expected_samples = self.test_sequence_length - 1
        self.assertEqual(pattern_metrics['num_samples'], expected_samples)
        
        # Verify pattern detection is boolean
        self.assertIsInstance(pattern_metrics['pattern_detected'], bool)
        
        # Test error handling
        with self.assertRaises(ValueError):
            self.analyzer.compute_curvature_patterns([])
    
    def test_analyze_sequence(self):
        """Test complete sequence analysis."""
        results = self.analyzer.analyze_sequence(self.test_data, self.test_sequence_length)
        
        # Verify results structure
        required_keys = [
            'base_data', 'sequence_length', 'hash_sequence', 'integer_sequence',
            'discrete_derivatives', 'derivative_stats', 'zeta_attributes',
            'pattern_metrics', 'framework_parameters'
        ]
        for key in required_keys:
            self.assertIn(key, results)
        
        # Verify data consistency
        self.assertEqual(results['base_data'], self.test_data)
        self.assertEqual(results['sequence_length'], self.test_sequence_length)
        self.assertEqual(len(results['hash_sequence']), self.test_sequence_length)
        self.assertEqual(len(results['integer_sequence']), self.test_sequence_length)
        self.assertEqual(len(results['discrete_derivatives']), self.test_sequence_length - 1)
        
        # Verify framework parameters
        params = results['framework_parameters']
        self.assertEqual(params['a'], 256)
        self.assertEqual(params['b'], float(mp.e))
        self.assertEqual(params['c'], float(E_SQUARED))
        
        # Verify derivative statistics
        derivative_stats = results['derivative_stats']
        self.assertIn('mean', derivative_stats)
        self.assertIn('std', derivative_stats)
        self.assertIn('min', derivative_stats)
        self.assertIn('max', derivative_stats)
    
    def test_detect_differential_patterns(self):
        """Test differential cryptanalysis pattern detection."""
        # Test with multiple variants
        variants = [
            "test_input_1",
            "test_input_2", 
            "test_input_3"
        ]
        
        results = self.analyzer.detect_differential_patterns(variants, sequence_length=3)
        
        # Verify results structure
        self.assertIn('variant_results', results)
        self.assertIn('differential_metrics', results)
        self.assertIn('analysis_summary', results)
        
        # Verify variant results
        variant_results = results['variant_results']
        self.assertEqual(len(variant_results), len(variants))
        
        for i, result in enumerate(variant_results):
            self.assertEqual(result['base_data'], variants[i])
            self.assertEqual(result['sequence_length'], 3)
        
        # Verify differential metrics
        diff_metrics = results['differential_metrics']
        required_diff_keys = [
            'num_variants', 'curvature_variance_across_variants',
            'pattern_consistency', 'non_random_behavior_detected'
        ]
        for key in required_diff_keys:
            self.assertIn(key, diff_metrics)
        
        self.assertEqual(diff_metrics['num_variants'], len(variants))
        self.assertIsInstance(diff_metrics['non_random_behavior_detected'], bool)
        
        # Verify analysis summary
        summary = results['analysis_summary']
        self.assertEqual(summary['framework'], 'Z Framework Discrete Domain')
        self.assertEqual(summary['method'], 'SHA-256 Discrete Derivative Analysis')
        self.assertEqual(summary['parameters'], 'a=256, b=e, c=e²')
    
    def test_sha256_avalanche_effect(self):
        """Test that small input changes produce large hash differences (avalanche effect)."""
        # Test similar inputs
        input1 = "test_string"
        input2 = "test_string_modified"
        
        hash1 = self.analyzer.sha256_to_integer(input1)
        hash2 = self.analyzer.sha256_to_integer(input2)
        
        # Calculate Hamming distance (bit differences)
        xor_result = hash1 ^ hash2
        hamming_distance = bin(xor_result).count('1')
        
        # SHA-256 should have good avalanche effect (roughly 50% bit difference)
        # For 256 bits, we expect significant difference
        self.assertGreater(hamming_distance, 50)  # At least 50 bits different
    
    def test_framework_integration_parameters(self):
        """Test that the analyzer correctly integrates with Z Framework parameters."""
        # Verify the problem statement requirements
        # "instantiating DiscreteZetaShift objects with parameters derived from 
        #  the bit length (a=256) and logarithmic invariants (b=e, c=e²)"
        
        self.analyzer.generate_hash_sequence("test", 3)
        self.analyzer.compute_discrete_derivatives()
        zeta_shifts = self.analyzer.map_to_discrete_zeta_shifts()
        
        # Check the first zeta shift object
        dzs = zeta_shifts[0]
        
        # Verify parameters match specification
        # Note: DiscreteZetaShift uses n as first parameter, not a directly
        # but the framework should use the specified constants
        self.assertEqual(float(dzs.c), float(E_SQUARED))  # c = e²
        
        # Verify bit length is correctly handled in attributes
        attrs = self.analyzer.extract_pattern_attributes()
        for attr in attrs:
            self.assertEqual(attr['bit_length'], 256)


class TestSHA256IntegrationWithZFramework(unittest.TestCase):
    """Integration tests with the broader Z Framework."""
    
    def test_curvature_computation_integration(self):
        """Test that curvature computations work correctly with SHA-256 data."""
        analyzer = SHA256PatternAnalyzer()
        
        # Analyze a sequence
        results = analyzer.analyze_sequence("cryptographic_test_data", sequence_length=4)
        
        # Verify curvature-based pattern metrics are computed
        pattern_metrics = results['pattern_metrics']
        
        # Should have curvature statistics
        self.assertIsNotNone(pattern_metrics.get('curvature_mean'))
        self.assertIsNotNone(pattern_metrics.get('curvature_std'))
        
        # Pattern detection should be a boolean result
        self.assertIsInstance(pattern_metrics['pattern_detected'], bool)
    
    def test_zeta_chain_unfolding_integration(self):
        """Test integration with zeta chain unfolding as mentioned in problem statement."""
        analyzer = SHA256PatternAnalyzer()
        
        # Generate sequence and derivatives
        analyzer.generate_hash_sequence("zeta_chain_test", 5)
        analyzer.compute_discrete_derivatives()
        zeta_shifts = analyzer.map_to_discrete_zeta_shifts()
        
        # Verify that zeta shifts support chain operations
        for dzs in zeta_shifts:
            # Should have attributes needed for zeta chain analysis
            attrs = dzs.attributes
            
            # Verify key zeta attributes are present (D through O)
            zeta_attrs = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
            for attr in zeta_attrs:
                self.assertIn(attr, attrs)
                self.assertIsNotNone(attrs[attr])


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)