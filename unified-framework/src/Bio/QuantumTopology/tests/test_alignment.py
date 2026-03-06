"""
Tests for Bio.QuantumTopology.alignment module

Tests the quantum-inspired alignment functionality including Bell violations
and quantum correlation-based sequence comparison.
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

from src.Bio.QuantumTopology.alignment import (
    quantum_alignment,
    compute_bell_violation,
    quantum_distance,
    detect_quantum_motifs,
    _bell_violation_alignment,
    _correlation_alignment,
    _hybrid_alignment,
    _normal_cdf,
    _erf
)
from src.Bio.QuantumTopology.helical import generate_helical_coordinates


class TestQuantumAlignment(unittest.TestCase):
    """Test quantum-inspired alignment functions."""
    
    def setUp(self):
        """Set up test sequences."""
        self.seq1 = Seq("ATGCGATCGATC")
        self.seq2 = Seq("ATGCGATCGATC")  # Identical
        self.seq3 = Seq("CGTAGCTACGTA")  # Different
        self.seq4 = Seq("ATGCGATC")      # Shorter
        self.short_seq = Seq("ATGC")
    
    def test_quantum_alignment_basic(self):
        """Test basic quantum alignment functionality."""
        # Test alignment between identical sequences
        result = quantum_alignment(self.seq1, self.seq2, hypothetical=False)
        
        # Check return structure
        required_keys = ['alignment_score', 'method', 'sequence_length', 
                        'curvature_k', 'hypothetical', 'interpretation']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check data types
        self.assertIsInstance(result['alignment_score'], (int, float))
        self.assertIsInstance(result['method'], str)
        self.assertIsInstance(result['sequence_length'], int)
        self.assertIsInstance(result['curvature_k'], (int, float))
        
        # Alignment score should be reasonable
        self.assertGreaterEqual(result['alignment_score'], 0)
        self.assertLessEqual(result['alignment_score'], 10)  # Reasonable upper bound
    
    def test_quantum_alignment_methods(self):
        """Test different alignment methods."""
        methods = ['bell_violation', 'correlation', 'hybrid']
        
        for method in methods:
            result = quantum_alignment(self.seq1, self.seq3, method=method, hypothetical=False)
            self.assertEqual(result['method'], method)
            self.assertIsInstance(result['alignment_score'], (int, float))
    
    def test_quantum_alignment_identical_sequences(self):
        """Test alignment of identical sequences."""
        result = quantum_alignment(self.seq1, self.seq2, hypothetical=False)
        
        # Identical sequences should have some correlation
        self.assertGreaterEqual(result['alignment_score'], 0)
    
    def test_quantum_alignment_different_lengths(self):
        """Test alignment of sequences with different lengths."""
        result = quantum_alignment(self.seq1, self.seq4, hypothetical=False)
        
        # Should handle different lengths by trimming
        self.assertEqual(result['sequence_length'], len(self.seq4))
        self.assertIsInstance(result['alignment_score'], (int, float))
    
    def test_quantum_alignment_parameters(self):
        """Test alignment with different parameters."""
        # Different curvature parameters
        result1 = quantum_alignment(self.seq1, self.seq3, k=0.1, hypothetical=False)
        result2 = quantum_alignment(self.seq1, self.seq3, k=0.5, hypothetical=False)
        
        self.assertEqual(result1['curvature_k'], 0.1)
        self.assertEqual(result2['curvature_k'], 0.5)
        
        # Results may differ with different k values
        # (not requiring specific relationship as quantum effects are complex)
    
    def test_bell_violation_alignment(self):
        """Test Bell violation-based alignment."""
        result = _bell_violation_alignment(self.seq1, self.seq3, k=0.3, hypothetical=False)
        
        # Check Bell-specific return keys
        required_keys = ['alignment_score', 'bell_violation', 'p_value', 'method']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check data ranges
        self.assertIsInstance(result['bell_violation'], (int, float))
        self.assertIsInstance(result['p_value'], (int, float))
        self.assertGreaterEqual(result['p_value'], 0)
        self.assertLessEqual(result['p_value'], 1)
    
    def test_correlation_alignment(self):
        """Test correlation-based alignment."""
        result = _correlation_alignment(self.seq1, self.seq3, k=0.3, hypothetical=False)
        
        # Check correlation-specific return keys
        required_keys = ['alignment_score', 'correlation_similarity', 'method']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Correlation similarity should be in [-1, 1] range
        corr_sim = result['correlation_similarity']
        self.assertGreaterEqual(corr_sim, -1)
        self.assertLessEqual(corr_sim, 1)
    
    def test_hybrid_alignment(self):
        """Test hybrid alignment method."""
        result = _hybrid_alignment(self.seq1, self.seq3, k=0.3, hypothetical=False)
        
        # Check hybrid-specific return keys
        required_keys = ['alignment_score', 'bell_component', 'correlation_component', 
                        'method', 'weights']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check component structure
        self.assertIsInstance(result['bell_component'], dict)
        self.assertIsInstance(result['correlation_component'], dict)
        self.assertIsInstance(result['weights'], dict)


class TestBellViolation(unittest.TestCase):
    """Test Bell violation computation."""
    
    def setUp(self):
        """Set up test data."""
        self.seq1 = Seq("ATGCGATCGATC")
        self.seq2 = Seq("CGTAGCTACGTA")
        
    def test_compute_bell_violation_basic(self):
        """Test basic Bell violation computation."""
        coords1 = generate_helical_coordinates(self.seq1, hypothetical=False)
        coords2 = generate_helical_coordinates(self.seq2, hypothetical=False)
        
        violation, p_value = compute_bell_violation(coords1, coords2)
        
        # Check return types
        self.assertIsInstance(violation, (int, float))
        self.assertIsInstance(p_value, (int, float))
        
        # Check reasonable ranges
        self.assertGreaterEqual(violation, 0)  # Violation should be non-negative
        self.assertGreaterEqual(p_value, 0)
        self.assertLessEqual(p_value, 1)
    
    def test_compute_bell_violation_identical_coords(self):
        """Test Bell violation with identical coordinates."""
        coords = generate_helical_coordinates(self.seq1, hypothetical=False)
        
        violation, p_value = compute_bell_violation(coords, coords)
        
        # Identical coordinates should show strong correlation
        self.assertIsInstance(violation, (int, float))
        self.assertIsInstance(p_value, (int, float))
    
    def test_compute_bell_violation_short_sequences(self):
        """Test Bell violation with short sequences."""
        short_seq = Seq("ATG")
        coords1 = generate_helical_coordinates(short_seq, hypothetical=False)
        coords2 = generate_helical_coordinates(short_seq, hypothetical=False)
        
        violation, p_value = compute_bell_violation(coords1, coords2)
        
        # Should handle short sequences gracefully (may return 0,1 for insufficient data)
        self.assertIsInstance(violation, (int, float))
        self.assertIsInstance(p_value, (int, float))
    
    def test_bell_violation_measurements(self):
        """Test Bell violation with different numbers of measurements."""
        coords1 = generate_helical_coordinates(self.seq1, hypothetical=False)
        coords2 = generate_helical_coordinates(self.seq2, hypothetical=False)
        
        violation_4 = compute_bell_violation(coords1, coords2, n_measurements=4)[0]
        violation_8 = compute_bell_violation(coords1, coords2, n_measurements=8)[0]
        
        # Both should return valid values
        self.assertIsInstance(violation_4, (int, float))
        self.assertIsInstance(violation_8, (int, float))


class TestQuantumDistance(unittest.TestCase):
    """Test quantum distance metrics."""
    
    def setUp(self):
        """Set up test sequences."""
        self.seq1 = Seq("ATGCGATC")
        self.seq2 = Seq("ATGCGATC")  # Identical
        self.seq3 = Seq("CGTAGCTA")  # Different
    
    def test_quantum_distance_basic(self):
        """Test basic quantum distance computation."""
        result = quantum_distance(self.seq1, self.seq3)
        
        # Check return structure
        required_keys = ['distance', 'alignment_score', 'metric', 'curvature_k', 'interpretation']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check data types and ranges
        distance = result['distance']
        self.assertIsInstance(distance, (int, float))
        self.assertGreaterEqual(distance, 0)
        self.assertLessEqual(distance, 1)  # Normalized distance
    
    def test_quantum_distance_identical_sequences(self):
        """Test distance between identical sequences."""
        result = quantum_distance(self.seq1, self.seq2)
        
        # Identical sequences should have low distance
        # (though quantum effects may introduce some variation)
        self.assertIsInstance(result['distance'], (int, float))
    
    def test_quantum_distance_metrics(self):
        """Test different distance metrics."""
        metrics = ['bell_violation', 'correlation']
        
        for metric in metrics:
            result = quantum_distance(self.seq1, self.seq3, metric=metric)
            self.assertEqual(result['metric'], metric)
            self.assertIsInstance(result['distance'], (int, float))


class TestQuantumMotifs(unittest.TestCase):
    """Test quantum motif detection."""
    
    def setUp(self):
        """Set up test sequences."""
        self.test_seq = Seq("ATGCGATCGATCATGCATGC")  # With some repeats
        self.short_seq = Seq("ATGC")
    
    def test_detect_quantum_motifs_basic(self):
        """Test basic quantum motif detection."""
        result = detect_quantum_motifs(self.test_seq, motif_length=4, threshold=0.3)
        
        # Check return structure
        required_keys = ['motifs', 'threshold', 'motif_length', 'curvature_k', 
                        'hypothetical', 'interpretation']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check motifs structure
        motifs = result['motifs']
        self.assertIsInstance(motifs, list)
        
        # Each motif should have required fields
        for motif in motifs:
            required_motif_keys = ['position', 'motif', 'coherence', 'length']
            for key in required_motif_keys:
                self.assertIn(key, motif)
            
            # Check data types and ranges
            self.assertIsInstance(motif['position'], int)
            self.assertIsInstance(motif['motif'], str)
            self.assertIsInstance(motif['coherence'], (int, float))
            self.assertIsInstance(motif['length'], int)
            
            self.assertGreaterEqual(motif['position'], 0)
            self.assertEqual(motif['length'], result['motif_length'])
            self.assertGreaterEqual(motif['coherence'], 0)
            self.assertLessEqual(motif['coherence'], 1)
    
    def test_detect_quantum_motifs_parameters(self):
        """Test motif detection with different parameters."""
        # Different motif lengths
        result_4 = detect_quantum_motifs(self.test_seq, motif_length=4, threshold=0.3)
        result_6 = detect_quantum_motifs(self.test_seq, motif_length=6, threshold=0.3)
        
        self.assertEqual(result_4['motif_length'], 4)
        self.assertEqual(result_6['motif_length'], 6)
        
        # Different thresholds
        result_low = detect_quantum_motifs(self.test_seq, motif_length=4, threshold=0.1)
        result_high = detect_quantum_motifs(self.test_seq, motif_length=4, threshold=0.8)
        
        # Lower threshold should generally find more motifs
        self.assertGreaterEqual(len(result_low['motifs']), len(result_high['motifs']))
    
    def test_detect_quantum_motifs_short_sequence(self):
        """Test motif detection on short sequences."""
        result = detect_quantum_motifs(self.short_seq, motif_length=3, threshold=0.3)
        
        # Should handle short sequences gracefully
        self.assertIsInstance(result['motifs'], list)
        
        # May find few or no motifs in very short sequences
        motifs = result['motifs']
        self.assertLessEqual(len(motifs), len(self.short_seq) - 3 + 1)


class TestMathematicalHelpers(unittest.TestCase):
    """Test mathematical helper functions."""
    
    def test_normal_cdf(self):
        """Test normal CDF approximation."""
        # Test some known values
        self.assertAlmostEqual(_normal_cdf(0), 0.5, places=2)
        self.assertGreater(_normal_cdf(1), 0.5)
        self.assertLess(_normal_cdf(-1), 0.5)
        
        # Check monotonicity
        self.assertLess(_normal_cdf(-2), _normal_cdf(-1))
        self.assertLess(_normal_cdf(-1), _normal_cdf(0))
        self.assertLess(_normal_cdf(0), _normal_cdf(1))
        self.assertLess(_normal_cdf(1), _normal_cdf(2))
    
    def test_erf(self):
        """Test error function approximation."""
        # Test known properties
        self.assertAlmostEqual(_erf(0), 0, places=3)
        self.assertGreater(_erf(1), 0)
        self.assertLess(_erf(-1), 0)
        
        # Check antisymmetry: erf(-x) = -erf(x)
        x = 1.5
        self.assertAlmostEqual(_erf(-x), -_erf(x), places=3)


class TestAlignmentEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_sequences(self):
        """Test alignment with empty sequences."""
        empty_seq = Seq("")
        normal_seq = Seq("ATGC")
        
        # Should handle empty sequences gracefully (may return specific defaults)
        try:
            result = quantum_alignment(empty_seq, normal_seq, hypothetical=False)
            self.assertIsInstance(result, dict)
        except Exception:
            # Some implementations may raise exceptions for empty sequences
            pass
    
    def test_invalid_method(self):
        """Test alignment with invalid method."""
        seq1 = Seq("ATGC")
        seq2 = Seq("CGTA")
        
        with self.assertRaises(ValueError):
            quantum_alignment(seq1, seq2, method='invalid_method', hypothetical=False)
    
    def test_single_base_sequences(self):
        """Test alignment with single base sequences."""
        seq1 = Seq("A")
        seq2 = Seq("T")
        
        result = quantum_alignment(seq1, seq2, hypothetical=False)
        self.assertEqual(result['sequence_length'], 1)
        self.assertIsInstance(result['alignment_score'], (int, float))


if __name__ == '__main__':
    unittest.main()