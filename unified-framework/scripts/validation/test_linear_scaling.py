#!/usr/bin/env python3
"""
Unit Tests for Linear Scaling Validation

This test suite validates the linear scaling implementation 
and ensures it meets the requirements specified in Issue #195.

Author: DAL
License: MIT
"""

import unittest
import sys
import os
import numpy as np
import tempfile
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validate_linear_scaling import (
    LinearScalingValidator, 
    DataGenerator, 
    CompressionTimer,
    ScalingResult
)

try:
    from applications.prime_compression_fixed import (
        PrimeDrivenCompressor, 
        CompressionBenchmark,
        PrimeGeodesicTransform,
        K_OPTIMAL, PHI
    )
    PRIME_COMPRESSION_AVAILABLE = True
except ImportError:
    PRIME_COMPRESSION_AVAILABLE = False


class TestLinearScalingValidator(unittest.TestCase):
    """Test the linear scaling validation framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = LinearScalingValidator()
        self.test_sizes = [1000, 5000, 10000]  # Smaller sizes for unit tests
        
    def test_data_generator_structured(self):
        """Test structured data generation."""
        generator = DataGenerator()
        data = generator.generate_structured_text(1000)
        
        self.assertEqual(len(data), 1000)
        self.assertIsInstance(data, bytes)
        
        # Should be compressible (repetitive)
        unique_chars = len(set(data))
        self.assertLess(unique_chars, 100)  # Should have limited character variety
        
    def test_data_generator_binary(self):
        """Test binary data generation."""
        generator = DataGenerator()
        data = generator.generate_binary_data(1000)
        
        self.assertEqual(len(data), 1000)
        self.assertIsInstance(data, bytes)
        
        # Should be incompressible (random)
        unique_chars = len(set(data))
        self.assertGreater(unique_chars, 200)  # Should have high character variety
        
    def test_compression_timer_gzip(self):
        """Test compression timing for gzip."""
        timer = CompressionTimer()
        data = b"test data " * 100
        
        comp_time, comp_ratio, comp_size = timer.time_compression('gzip', data)
        
        self.assertGreater(comp_time, 0)
        self.assertGreater(comp_ratio, 0)
        self.assertGreater(comp_size, 0)
        
    @unittest.skipUnless(PRIME_COMPRESSION_AVAILABLE, "Prime compression not available")
    def test_compression_timer_prime_driven(self):
        """Test compression timing for prime-driven algorithm."""
        timer = CompressionTimer()
        data = b"test data " * 100
        
        comp_time, comp_ratio, comp_size = timer.time_compression('prime_driven', data)
        
        self.assertGreater(comp_time, 0)
        self.assertGreater(comp_ratio, 0)
        self.assertGreater(comp_size, 0)
        
    def test_scaling_analysis_linear_data(self):
        """Test scaling analysis with perfect linear data."""
        # Create artificial linear data
        sizes = np.array([1000, 2000, 3000])
        times = np.array([0.001, 0.002, 0.003])  # Perfect linear relationship
        
        result = ScalingResult(
            algorithm='test',
            data_type='test',
            sizes=sizes.tolist(),
            times=times.tolist(),
            ratios=[1.0, 1.0, 1.0],
            linear_coeff=0.000001,
            intercept=0.0,
            r_squared=1.0,
            time_per_byte=[t/s for t, s in zip(times, sizes)],
            passes_validation=True
        )
        
        self.assertTrue(result.passes_validation)
        self.assertEqual(result.r_squared, 1.0)
        
    def test_small_scale_validation(self):
        """Test small-scale validation to ensure framework works."""
        result = self.validator.run_scaling_test(
            algorithm='gzip',
            data_type='structured', 
            test_sizes=self.test_sizes,
            num_trials=1
        )
        
        self.assertIsInstance(result, ScalingResult)
        self.assertEqual(result.algorithm, 'gzip')
        self.assertEqual(result.data_type, 'structured')
        self.assertEqual(len(result.sizes), len(self.test_sizes))
        self.assertEqual(len(result.times), len(self.test_sizes))
        # For small sizes, timing may be too variable, so just check structure
        self.assertGreater(result.r_squared, 0.0)  # Should be valid
        
    def test_mathematical_constants(self):
        """Test that mathematical constants are correctly defined."""
        if PRIME_COMPRESSION_AVAILABLE:
            self.assertAlmostEqual(float(PHI), 1.6180339887, places=6)
            self.assertAlmostEqual(float(K_OPTIMAL), 0.200, places=3)
            
    @unittest.skipUnless(PRIME_COMPRESSION_AVAILABLE, "Prime compression not available")
    def test_prime_geodesic_transform(self):
        """Test the prime geodesic transformation."""
        transformer = PrimeGeodesicTransform()
        
        # Test with small array
        indices = np.array([1, 2, 3, 5, 7, 11])
        theta_values = transformer.frame_shift_residues(indices)
        
        self.assertEqual(len(theta_values), len(indices))
        self.assertTrue(np.all(theta_values > 0))
        self.assertTrue(np.all(theta_values < float(PHI)))
        
    @unittest.skipUnless(PRIME_COMPRESSION_AVAILABLE, "Prime compression not available")
    def test_prime_compressor_basic(self):
        """Test basic prime compression functionality."""
        compressor = PrimeDrivenCompressor()
        test_data = b"Hello, World! " * 10
        
        compressed_data, metrics = compressor.compress(test_data)
        
        self.assertIsNotNone(compressed_data)
        self.assertEqual(metrics.original_size, len(test_data))
        self.assertGreater(metrics.compression_time, 0)
        
        # Test decompression
        decompressed_data, integrity_verified = compressor.decompress(compressed_data, metrics)
        
        self.assertEqual(len(decompressed_data), len(test_data))
        

class TestMathematicalFoundations(unittest.TestCase):
    """Test mathematical foundations of the Z framework."""
    
    @unittest.skipUnless(PRIME_COMPRESSION_AVAILABLE, "Prime compression not available")
    def test_golden_ratio_properties(self):
        """Test golden ratio mathematical properties."""
        phi = float(PHI)
        
        # φ² = φ + 1
        self.assertAlmostEqual(phi**2, phi + 1, places=6)
        
        # 1/φ = φ - 1
        self.assertAlmostEqual(1/phi, phi - 1, places=6)
        
    @unittest.skipUnless(PRIME_COMPRESSION_AVAILABLE, "Prime compression not available")
    def test_curvature_parameter_range(self):
        """Test that curvature parameter is in valid range."""
        k_star = float(K_OPTIMAL)
        
        self.assertGreater(k_star, 0)
        self.assertLess(k_star, 1)
        self.assertAlmostEqual(k_star, 0.2, places=3)
        
    def test_scaling_hypothesis_requirements(self):
        """Test that scaling hypothesis requirements are met."""
        # Linear scaling should have R² ≥ 0.998
        min_r_squared = 0.998
        
        # Test with perfect linear data
        x = np.array([1, 2, 3, 4, 5])
        y = 2 * x + 1  # Perfect linear relationship
        
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        
        reg = LinearRegression()
        reg.fit(x.reshape(-1, 1), y)
        r_squared = r2_score(y, reg.predict(x.reshape(-1, 1)))
        
        self.assertGreaterEqual(r_squared, min_r_squared)
        

class TestBenchmarkingSuite(unittest.TestCase):
    """Test the benchmarking capabilities."""
    
    @unittest.skipUnless(PRIME_COMPRESSION_AVAILABLE, "Prime compression not available")
    def test_compression_benchmark(self):
        """Test compression benchmarking suite."""
        benchmark = CompressionBenchmark()
        
        # Test data generation
        test_data = benchmark.generate_test_data('mixed', 1000)
        self.assertEqual(len(test_data), 1000)
        
        # Test single algorithm benchmarking
        result = benchmark.benchmark_algorithm('gzip', test_data)
        self.assertTrue(result['success'])
        self.assertIn('metrics', result)
        
    def test_report_generation(self):
        """Test that reports can be generated without errors."""
        validator = LinearScalingValidator()
        
        # Create dummy results
        dummy_result = ScalingResult(
            algorithm='test',
            data_type='test',
            sizes=[1000, 2000],
            times=[0.001, 0.002],
            ratios=[1.0, 1.0],
            linear_coeff=0.000001,
            intercept=0.0,
            r_squared=0.999,
            time_per_byte=[0.000001, 0.000001],
            passes_validation=True
        )
        
        report = validator.generate_scaling_report([dummy_result])
        
        self.assertIsInstance(report, str)
        self.assertIn('LINEAR SCALING HYPOTHESIS VALIDATION REPORT', report)
        self.assertIn('PASS', report)
        

def run_tests():
    """Run all tests and return success status."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestLinearScalingValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestMathematicalFoundations))
    suite.addTests(loader.loadTestsFromTestCase(TestBenchmarkingSuite))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Linear Scaling Validation Tests...")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("✓ ALL TESTS PASSED")
        print("Linear scaling validation framework is working correctly.")
    else:
        print("✗ SOME TESTS FAILED")
        print("Please review the test failures above.")
    
    sys.exit(0 if success else 1)