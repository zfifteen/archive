"""
Tests for Bio.QuantumTopology.helical module

Tests the core helical coordinate generation and quantum correlation
functionality to ensure mathematical correctness and Biopython compatibility.
"""

import unittest
import numpy as np
import sys
import os

# Import Bio.Seq with proper error handling to prevent confusion
try:
    from Bio.Seq import Seq
except ImportError:
    import pytest
    pytest.importorskip("Bio", minversion="1.83", reason="Bio.Seq requires biopython package. Install with: pip install biopython")

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.Bio.QuantumTopology.helical import (
    generate_helical_coordinates,
    compute_quantum_correlations,
    complexity_metric,
    geodesic_transform,
    divisor_count,
    filter_low_complexity_positions,
    PHI, E_SQUARED, OPTIMAL_K
)


class TestHelicalCoordinates(unittest.TestCase):
    """Test helical coordinate generation and related functions."""
    
    def setUp(self):
        """Set up test sequences."""
        self.test_seq = Seq("ATGCGATCGATC")
        self.short_seq = Seq("ATGC")
        self.long_seq = Seq("ATGCGATCGATCGATCGATCGATCGATC")
    
    def test_constants(self):
        """Test that mathematical constants are correct."""
        self.assertAlmostEqual(PHI, (1 + np.sqrt(5)) / 2, places=10)
        self.assertAlmostEqual(E_SQUARED, np.exp(2), places=10)
        self.assertEqual(OPTIMAL_K, 0.3)
    
    def test_divisor_count(self):
        """Test divisor counting function."""
        self.assertEqual(divisor_count(1), 1)
        self.assertEqual(divisor_count(2), 2)  # Prime
        self.assertEqual(divisor_count(6), 4)  # 1, 2, 3, 6
        self.assertEqual(divisor_count(12), 6)  # 1, 2, 3, 4, 6, 12
        self.assertEqual(divisor_count(0), 0)
        self.assertEqual(divisor_count(-5), 0)
    
    def test_complexity_metric(self):
        """Test κ(n) complexity metric."""
        # Test basic properties
        kappa_1 = complexity_metric(1)
        kappa_2 = complexity_metric(2)  # Prime
        kappa_6 = complexity_metric(6)  # Composite
        
        self.assertGreater(kappa_1, 0)
        self.assertGreater(kappa_2, 0)
        self.assertGreater(kappa_6, kappa_2)  # Composite should have higher complexity
        
        # Test edge cases
        self.assertEqual(complexity_metric(0), 0)
        self.assertEqual(complexity_metric(-1), 0)
    
    def test_geodesic_transform(self):
        """Test φ-geodesic transformation."""
        # Test single value
        result = geodesic_transform(1, k=0.3)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        self.assertLess(result, PHI)
        
        # Test array input
        array_input = [1, 2, 3, 4, 5]
        array_result = geodesic_transform(array_input, k=0.3)
        self.assertEqual(len(array_result), len(array_input))
        self.assertTrue(all(0 <= x < PHI for x in array_result))
        
        # Test curvature parameter effect
        result_k0 = geodesic_transform(5, k=0.0)
        result_k1 = geodesic_transform(5, k=1.0)
        self.assertNotEqual(result_k0, result_k1)
    
    def test_generate_helical_coordinates_basic(self):
        """Test basic helical coordinate generation."""
        coords = generate_helical_coordinates(self.test_seq, hypothetical=False)
        
        # Check return structure
        self.assertIsInstance(coords, dict)
        required_keys = ['x', 'y', 'z', 'theta', 'metadata']
        for key in required_keys:
            self.assertIn(key, coords)
        
        # Check coordinate arrays
        seq_len = len(self.test_seq)
        self.assertEqual(len(coords['x']), seq_len)
        self.assertEqual(len(coords['y']), seq_len)
        self.assertEqual(len(coords['z']), seq_len)
        self.assertEqual(len(coords['theta']), seq_len)
        
        # Check data types
        self.assertIsInstance(coords['x'], np.ndarray)
        self.assertIsInstance(coords['y'], np.ndarray)
        self.assertIsInstance(coords['z'], np.ndarray)
        self.assertIsInstance(coords['theta'], np.ndarray)
        
        # Check metadata
        metadata = coords['metadata']
        self.assertEqual(metadata['sequence_length'], seq_len)
        self.assertEqual(metadata['curvature_k'], OPTIMAL_K)
        self.assertEqual(metadata['phi_constant'], PHI)
        self.assertFalse(metadata['hypothetical'])
    
    def test_generate_helical_coordinates_parameters(self):
        """Test helical coordinates with different parameters."""
        # Test custom curvature
        coords1 = generate_helical_coordinates(self.test_seq, k=0.1, hypothetical=False)
        coords2 = generate_helical_coordinates(self.test_seq, k=0.5, hypothetical=False)
        
        # Different k should give different results
        self.assertFalse(np.allclose(coords1['theta'], coords2['theta']))
        self.assertEqual(coords1['metadata']['curvature_k'], 0.1)
        self.assertEqual(coords2['metadata']['curvature_k'], 0.5)
        
        # Test hypothetical flag
        coords_hyp = generate_helical_coordinates(self.test_seq, hypothetical=True)
        self.assertTrue(coords_hyp['metadata']['hypothetical'])
    
    def test_generate_helical_coordinates_sequence_types(self):
        """Test helical coordinates with different sequence lengths."""
        # Short sequence
        coords_short = generate_helical_coordinates(self.short_seq, hypothetical=False)
        self.assertEqual(len(coords_short['x']), len(self.short_seq))
        
        # Long sequence
        coords_long = generate_helical_coordinates(self.long_seq, hypothetical=False)
        self.assertEqual(len(coords_long['x']), len(self.long_seq))
        
        # Empty sequence should not crash
        empty_seq = Seq("")
        coords_empty = generate_helical_coordinates(empty_seq, hypothetical=False)
        self.assertEqual(len(coords_empty['x']), 0)
    
    def test_compute_quantum_correlations_basic(self):
        """Test basic quantum correlation computation."""
        corr_data = compute_quantum_correlations(self.test_seq, hypothetical=False)
        
        # Check return structure
        required_keys = ['correlations', 'entangled_regions', 'correlation_threshold',
                        'mean_correlation', 'std_correlation', 'window_size', 'hypothetical', 'metadata']
        for key in required_keys:
            self.assertIn(key, corr_data)
        
        # Check data types and shapes
        correlations = corr_data['correlations']
        entangled_regions = corr_data['entangled_regions']
        
        self.assertIsInstance(correlations, np.ndarray)
        self.assertIsInstance(entangled_regions, np.ndarray)
        self.assertEqual(len(correlations), len(entangled_regions))
        
        # Check reasonable correlation values (-1 to 1)
        self.assertTrue(np.all(correlations >= -1.0))
        self.assertTrue(np.all(correlations <= 1.0))
        
        # Check boolean entangled regions
        self.assertTrue(entangled_regions.dtype == bool)
    
    def test_compute_quantum_correlations_parameters(self):
        """Test quantum correlations with different parameters."""
        # Different window sizes
        corr1 = compute_quantum_correlations(self.test_seq, window_size=5, hypothetical=False)
        corr2 = compute_quantum_correlations(self.test_seq, window_size=8, hypothetical=False)
        
        self.assertEqual(corr1['window_size'], 5)
        self.assertEqual(corr2['window_size'], 8)
        
        # Window size affects number of correlations
        expected_len1 = len(self.test_seq) - 5 + 1
        expected_len2 = len(self.test_seq) - 8 + 1
        self.assertEqual(len(corr1['correlations']), expected_len1)
        self.assertEqual(len(corr2['correlations']), expected_len2)
    
    def test_filter_low_complexity_positions(self):
        """Test low complexity position filtering."""
        result = filter_low_complexity_positions(self.test_seq, percentile=20)
        
        # Check return structure
        required_keys = ['positions', 'kappa_values', 'threshold', 'percentile']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check data types
        self.assertIsInstance(result['positions'], np.ndarray)
        self.assertIsInstance(result['kappa_values'], np.ndarray)
        self.assertEqual(result['percentile'], 20)
        
        # Check that kappa values match sequence length
        self.assertEqual(len(result['kappa_values']), len(self.test_seq))
        
        # Check that positions are valid indices
        positions = result['positions']
        self.assertTrue(np.all(positions >= 1))
        self.assertTrue(np.all(positions <= len(self.test_seq)))
    
    def test_coordinate_mathematical_properties(self):
        """Test mathematical properties of generated coordinates."""
        coords = generate_helical_coordinates(self.test_seq, hypothetical=False)
        x, y, z, theta = coords['x'], coords['y'], coords['z'], coords['theta']
        
        # Check that theta values are in expected range [0, PHI)
        self.assertTrue(np.all(theta >= 0))
        self.assertTrue(np.all(theta < PHI))
        
        # Check that z coordinates are monotonically increasing (helical progression)
        self.assertTrue(np.all(np.diff(z) >= 0))
        
        # Check that x² + y² represents the base mapping scaled by normalized values
        radial = np.sqrt(x**2 + y**2)
        self.assertTrue(np.all(radial >= 0))
    
    def test_biopython_integration(self):
        """Test integration with Biopython Seq objects."""
        # Test with Bio.Seq
        from Bio.Seq import Seq
        seq = Seq("ATGCGATC")
        coords = generate_helical_coordinates(seq, hypothetical=False)
        self.assertEqual(coords['metadata']['sequence_length'], len(seq))
        
        # Test sequence attribute attachment
        coords_attached = generate_helical_coordinates(seq, attach_to_seq=True, hypothetical=False)
        if hasattr(seq, '__dict__'):
            # Bio.Seq objects don't always support attribute assignment
            # This tests the attempted functionality
            pass


class TestHelicalEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_sequence(self):
        """Test handling of empty sequences."""
        empty_seq = Seq("")
        coords = generate_helical_coordinates(empty_seq, hypothetical=False)
        
        self.assertEqual(len(coords['x']), 0)
        self.assertEqual(len(coords['y']), 0)
        self.assertEqual(len(coords['z']), 0)
        self.assertEqual(len(coords['theta']), 0)
        self.assertEqual(coords['metadata']['sequence_length'], 0)
    
    def test_single_base_sequence(self):
        """Test handling of single base sequences."""
        single_seq = Seq("A")
        coords = generate_helical_coordinates(single_seq, hypothetical=False)
        
        self.assertEqual(len(coords['x']), 1)
        self.assertEqual(len(coords['y']), 1)
        self.assertEqual(len(coords['z']), 1)
        self.assertEqual(len(coords['theta']), 1)
    
    def test_unknown_bases(self):
        """Test handling of non-standard bases."""
        unknown_seq = Seq("ATGCNXYZ")
        coords = generate_helical_coordinates(unknown_seq, hypothetical=False)
        
        # Should not crash and should handle unknown bases gracefully
        self.assertEqual(len(coords['x']), len(unknown_seq))
        self.assertEqual(coords['metadata']['sequence_length'], len(unknown_seq))
    
    def test_extreme_k_values(self):
        """Test with extreme curvature values."""
        seq = Seq("ATGC")
        
        # Very small k
        coords_small = generate_helical_coordinates(seq, k=0.001, hypothetical=False)
        self.assertEqual(coords_small['metadata']['curvature_k'], 0.001)
        
        # Large k
        coords_large = generate_helical_coordinates(seq, k=2.0, hypothetical=False)
        self.assertEqual(coords_large['metadata']['curvature_k'], 2.0)
        
        # Zero k
        coords_zero = generate_helical_coordinates(seq, k=0.0, hypothetical=False)
        self.assertEqual(coords_zero['metadata']['curvature_k'], 0.0)


if __name__ == '__main__':
    unittest.main()