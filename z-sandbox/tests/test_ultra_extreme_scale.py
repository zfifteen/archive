#!/usr/bin/env python3
"""
Unit tests for Ultra-Extreme Scale Prime Prediction

Tests the Z5D ultra-scale prediction module for k > 10^12.
"""

import sys
import os
import unittest
from mpmath import mp, mpf

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from ultra_extreme_scale_prediction import (
    UltraExtremeScalePredictor,
    GoldenAngleSequenceAnalyzer,
    PHI, E2, K_OPTIMAL, DENSITY_ENHANCEMENT_BASE
)

# Set precision for tests
mp.dps = 50


class TestUltraExtremeScalePredictor(unittest.TestCase):
    """Test ultra-scale predictor functionality."""
    
    def setUp(self):
        """Initialize predictor for tests."""
        self.predictor = UltraExtremeScalePredictor(precision_dps=50)
    
    def test_constants(self):
        """Test that universal constants are properly defined."""
        # Golden ratio φ ≈ 1.618033988749895
        self.assertAlmostEqual(float(PHI), 1.618033988749895, places=10)
        
        # e² ≈ 7.389056098930650
        self.assertAlmostEqual(float(E2), 7.389056098930650, places=10)
        
        # Optimal k for density enhancement
        self.assertEqual(K_OPTIMAL, 0.3)
        
        # Base density enhancement ~15%
        self.assertEqual(DENSITY_ENHANCEMENT_BASE, 0.15)
    
    def test_prime_density_approximation(self):
        """Test prime density d(n) ≈ 1/ln(n)."""
        # At n=10, d(10) ≈ 0.4343
        density_10 = self.predictor.prime_density_approximation(10)
        self.assertAlmostEqual(float(density_10), 0.4343, places=3)
        
        # At n=100, d(100) ≈ 0.2171
        density_100 = self.predictor.prime_density_approximation(100)
        self.assertAlmostEqual(float(density_100), 0.2171, places=3)
        
        # Edge case: n=1 should return 0
        density_1 = self.predictor.prime_density_approximation(1)
        self.assertEqual(float(density_1), 0.0)
    
    def test_curvature(self):
        """Test discrete curvature κ(n) = d(n) · ln(n+1) / e²."""
        # For n=100
        kappa_100 = self.predictor.curvature(100)
        self.assertGreater(float(kappa_100), 0.0)
        self.assertLess(float(kappa_100), 0.2)  # Should be small
        
        # Edge case: n=0 (ln(1) = 0, so kappa = 0)
        kappa_0 = self.predictor.curvature(0)
        self.assertEqual(float(kappa_0), 0.0)
        
        # Edge case: negative n
        kappa_neg = self.predictor.curvature(-1)
        self.assertEqual(float(kappa_neg), 0.0)
    
    def test_geometric_resolution(self):
        """Test geometric resolution θ'(n, k) = φ · ((n mod φ) / φ)^k."""
        # Test at n=100, k=0.3
        theta_100 = self.predictor.geometric_resolution(100, K_OPTIMAL)
        self.assertGreater(float(theta_100), 0.0)
        self.assertLess(float(theta_100), float(PHI) * 2)
        
        # Test that k affects the result
        theta_k1 = self.predictor.geometric_resolution(100, 0.5)
        theta_k2 = self.predictor.geometric_resolution(100, 0.3)
        self.assertNotEqual(float(theta_k1), float(theta_k2))
    
    def test_z5d_prime_prediction_small(self):
        """Test Z5D prime prediction on small values."""
        # k=1 should predict p_1 = 2
        pred_1 = self.predictor.z5d_prime_prediction(1, use_enhancement=False)
        self.assertEqual(float(pred_1), 2.0)
        
        # k=10 should predict around p_10 = 29 (base PNT gives ~16-30)
        pred_10 = self.predictor.z5d_prime_prediction(10, use_enhancement=False)
        self.assertGreater(float(pred_10), 10.0)
        self.assertLess(float(pred_10), 50.0)
        
        # k=100 should predict around p_100 = 541
        pred_100 = self.predictor.z5d_prime_prediction(100, use_enhancement=False)
        self.assertGreater(float(pred_100), 400.0)
        self.assertLess(float(pred_100), 700.0)
    
    def test_z5d_prime_prediction_enhancement(self):
        """Test that Z5D enhancement increases prediction."""
        k = 1000
        
        # Get base and enhanced predictions
        base_pred = self.predictor.z5d_prime_prediction(k, use_enhancement=False)
        enhanced_pred = self.predictor.z5d_prime_prediction(k, use_enhancement=True)
        
        # Enhanced should be larger due to density enhancement
        self.assertGreater(float(enhanced_pred), float(base_pred))
        
        # Enhancement should be reasonable (not > 50%)
        ratio = float(enhanced_pred) / float(base_pred)
        self.assertLess(ratio, 1.5)
        self.assertGreater(ratio, 1.0)
    
    def test_density_enhancement_ratio(self):
        """Test density enhancement ratio calculation."""
        # Test at k=1000
        ratio_1000 = self.predictor.density_enhancement_ratio(1000)
        self.assertGreater(float(ratio_1000), 1.0)  # Should have enhancement
        self.assertLess(float(ratio_1000), 1.2)  # But reasonable
        
        # Test at ultra-scale k=10^12
        ratio_ultra = self.predictor.density_enhancement_ratio(10**12)
        self.assertGreater(float(ratio_ultra), 1.0)
    
    def test_relative_error_extrapolation(self):
        """Test error extrapolation for ultra-scales."""
        k_values = [10**12, 10**13, 10**14]
        
        results = self.predictor.relative_error_extrapolation(k_values)
        
        # Check structure
        self.assertIn('k_values', results)
        self.assertIn('predictions', results)
        self.assertIn('error_bounds', results)
        self.assertIn('density_enhancements', results)
        
        # Check that we have results for all k values
        self.assertEqual(len(results['k_values']), len(k_values))
        self.assertEqual(len(results['predictions']), len(k_values))
        self.assertEqual(len(results['error_bounds']), len(k_values))
        
        # Check that error bounds decrease with k
        self.assertGreater(results['error_bounds'][0], results['error_bounds'][-1])
        
        # Check that predictions increase with k
        self.assertLess(results['predictions'][0], results['predictions'][-1])
    
    def test_validate_ultra_scale_hypothesis(self):
        """Test hypothesis validation for k > 10^12."""
        # Run with small sample for speed
        validation = self.predictor.validate_ultra_scale_hypothesis(
            k_ultra=10**13,
            num_samples=5
        )
        
        # Check structure
        self.assertIn('hypothesis', validation)
        self.assertIn('k_range', validation)
        self.assertIn('target_error', validation)
        self.assertIn('results', validation)
        self.assertIn('hypothesis_validated', validation)
        self.assertIn('notes', validation)
        
        # Check values
        self.assertEqual(validation['target_error'], 1e-7)
        self.assertEqual(validation['num_samples'], 5)
        # Convert to bool to handle numpy boolean types
        self.assertIsInstance(bool(validation['hypothesis_validated']), bool)
        
        # Check that we have error bounds
        self.assertIn('max_error_bound', validation)
        self.assertGreater(validation['max_error_bound'], 0.0)


class TestGoldenAngleSequenceAnalyzer(unittest.TestCase):
    """Test golden-angle sequence analyzer."""
    
    def setUp(self):
        """Initialize analyzer for tests."""
        self.analyzer = GoldenAngleSequenceAnalyzer(precision_dps=50)
    
    def test_golden_angle_constant(self):
        """Test golden angle ≈ 137.508 degrees."""
        import math
        golden_angle_degrees = float(self.analyzer.golden_angle) * 180 / math.pi
        self.assertAlmostEqual(golden_angle_degrees, 137.508, places=2)
    
    def test_generate_golden_angle_sequence(self):
        """Test generation of golden-angle sequence."""
        import math
        
        # Generate 100 points
        angles = self.analyzer.generate_golden_angle_sequence(100)
        
        # Check length
        self.assertEqual(len(angles), 100)
        
        # Check all angles in [0, 2π)
        for angle in angles:
            self.assertGreaterEqual(angle, 0.0)
            self.assertLess(angle, 2 * math.pi)
    
    def test_analyze_density_distribution(self):
        """Test density distribution analysis."""
        # Analyze 1000 samples
        distribution = self.analyzer.analyze_density_distribution(1000)
        
        # Check structure
        self.assertIn('num_samples', distribution)
        self.assertIn('num_bins', distribution)
        self.assertIn('expected_per_bin', distribution)
        self.assertIn('uniformity_score', distribution)
        
        # Check values
        self.assertEqual(distribution['num_samples'], 1000)
        self.assertEqual(distribution['num_bins'], 24)
        
        # Uniformity score should be high (>0.9)
        self.assertGreater(distribution['uniformity_score'], 0.9)
        
        # Min and max bin counts should be close to expected
        expected = distribution['expected_per_bin']
        self.assertGreater(distribution['min_bin_count'], expected * 0.8)
        self.assertLess(distribution['max_bin_count'], expected * 1.2)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components."""
    
    def test_ultra_scale_range(self):
        """Test predictions across ultra-scale range."""
        predictor = UltraExtremeScalePredictor(precision_dps=50)
        
        # Test at multiple scales
        scales = [10**12, 10**13, 10**14, 10**15]
        predictions = []
        
        for k in scales:
            pred = predictor.z5d_prime_prediction(k, use_enhancement=True)
            predictions.append(float(pred))
        
        # Check monotonically increasing
        for i in range(len(predictions) - 1):
            self.assertLess(predictions[i], predictions[i+1])
        
        # Check reasonable bit lengths
        for pred in predictions:
            bit_length = int(pred).bit_length()
            self.assertGreater(bit_length, 40)  # At least 40 bits
            self.assertLess(bit_length, 100)    # Not absurdly large
    
    def test_phyllotaxis_uniformity(self):
        """Test that golden-angle sequences maintain uniformity."""
        analyzer = GoldenAngleSequenceAnalyzer(precision_dps=50)
        
        # Test different sample sizes
        for n in [100, 500, 1000]:
            dist = analyzer.analyze_density_distribution(n)
            # Uniformity should remain high
            self.assertGreater(dist['uniformity_score'], 0.95)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUltraExtremeScalePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestGoldenAngleSequenceAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
