#!/usr/bin/env python3
"""
Test Suite for Z5D-RSA Experiment Implementation

Comprehensive test suite for validating the Z5D-RSA cryptographic scale experiment
implementation against requirements and target specifications.

Author: Z Framework Implementation Team
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from experiments.z5d_rsa_experiment import (
    RSACryptographicBenchmarkSuite,
    Z5DPredictorExecution,
    LopezTestMR,
    Z5DRSAExperiment,
    RSABenchmarkLevel,
    Z5DExperimentResult
)


class TestRSACryptographicBenchmarkSuite(unittest.TestCase):
    """Test RSA benchmark suite functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.suite = RSACryptographicBenchmarkSuite()
    
    def test_benchmark_levels_initialization(self):
        """Test that benchmark levels are properly initialized."""
        self.assertEqual(len(self.suite.levels), 4)
        
        level_names = [level.name for level in self.suite.levels]
        expected_names = ["RSA-512", "RSA-1024", "RSA-2048", "RSA-4096"]
        self.assertEqual(level_names, expected_names)
        
        # Check bit sizes
        bit_sizes = [level.bit_size for level in self.suite.levels]
        expected_sizes = [512, 1024, 2048, 4096]
        self.assertEqual(bit_sizes, expected_sizes)
    
    def test_target_k_values(self):
        """Test target k value calculation and retrieval."""
        # Test known levels
        rsa_512_k = self.suite.get_target_k("RSA-512")
        self.assertIsInstance(rsa_512_k, str)
        self.assertTrue(len(rsa_512_k) > 70)  # Should be around 10^77
        
        rsa_1024_k = self.suite.get_target_k("RSA-1024")
        self.assertTrue(len(rsa_1024_k) > 150)  # Should be around 10^154
        
        # Test invalid level
        with self.assertRaises(ValueError):
            self.suite.get_target_k("RSA-INVALID")
    
    def test_k_calculation_from_bits(self):
        """Test k value calculation from bit sizes."""
        # Test various bit sizes
        k_512 = self.suite.calculate_k_from_bits(512)
        k_1024 = self.suite.calculate_k_from_bits(1024)
        
        self.assertIsInstance(k_512, str)
        self.assertIsInstance(k_1024, str)
        
        # k_1024 should be much larger than k_512
        if k_512.replace('.', '').replace('e', '').replace('+', '').replace('-', '').isdigit():
            self.assertTrue(float(k_1024) > float(k_512))


class TestZ5DPredictorExecution(unittest.TestCase):
    """Test Z5D predictor execution engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = Z5DPredictorExecution(adaptive_precision=True)
    
    def test_small_scale_prediction(self):
        """Test Z5D prediction for small k values."""
        # Test with a manageable k value
        predicted_prime, exec_time, metrics = self.executor.execute_prediction("1000", "test")
        
        self.assertIsInstance(predicted_prime, str)
        self.assertIsInstance(exec_time, float)
        self.assertIsInstance(metrics, dict)
        
        # Should complete quickly for small k
        self.assertLess(exec_time, 1.0)
        
        # Should have reasonable length
        self.assertGreater(len(predicted_prime), 3)
        self.assertLess(len(predicted_prime), 1000)  # Should be reasonable for k=1000
    
    def test_prediction_metrics(self):
        """Test that prediction metrics are properly collected."""
        _, _, metrics = self.executor.execute_prediction("100", "test")
        
        expected_keys = ["k_magnitude", "precision_used", "memory_estimate", "algorithm", "calibration"]
        for key in expected_keys:
            self.assertIn(key, metrics)
        
        self.assertGreater(metrics["precision_used"], 0)
        self.assertGreater(metrics["memory_estimate"], 0)
    
    def test_invalid_k_handling(self):
        """Test handling of invalid k values."""
        with self.assertRaises(Exception):
            self.executor.execute_prediction("invalid", "test")


class TestLopezTestMR(unittest.TestCase):
    """Test Lopez Test Miller-Rabin implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.lopez_test = LopezTestMR(enable_z5d_witnesses=True)
    
    def test_small_prime_validation(self):
        """Test validation of small known primes."""
        # Test known primes
        primes = ["2", "3", "5", "7", "11", "13", "17", "19", "23"]
        
        for prime_str in primes:
            is_prime, metrics = self.lopez_test.validate_prime(prime_str)
            self.assertTrue(is_prime, f"Failed to recognize {prime_str} as prime")
            self.assertIsInstance(metrics, dict)
    
    def test_small_composite_detection(self):
        """Test detection of small composite numbers."""
        # Test known composites
        composites = ["4", "6", "8", "9", "10", "12", "14", "15", "16"]
        
        for composite_str in composites:
            is_prime, metrics = self.lopez_test.validate_prime(composite_str)
            self.assertFalse(is_prime, f"Incorrectly identified {composite_str} as prime")
    
    def test_edge_cases(self):
        """Test edge cases for validation."""
        # Test n < 2
        is_prime, metrics = self.lopez_test.validate_prime("1")
        self.assertFalse(is_prime)
        
        is_prime, metrics = self.lopez_test.validate_prime("0")
        self.assertFalse(is_prime)
        
        # Test n = 2
        is_prime, metrics = self.lopez_test.validate_prime("2")
        self.assertTrue(is_prime)
    
    def test_performance_stats_tracking(self):
        """Test that performance statistics are properly tracked."""
        initial_tests = self.lopez_test.performance_stats["total_tests"]
        
        self.lopez_test.validate_prime("17")
        
        self.assertEqual(
            self.lopez_test.performance_stats["total_tests"],
            initial_tests + 1
        )


class TestZ5DRSAExperiment(unittest.TestCase):
    """Test the main Z5D-RSA experiment controller."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.experiment = Z5DRSAExperiment(
            output_dir=self.temp_dir,
            enable_detailed_logging=False
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_experiment_initialization(self):
        """Test experiment initialization."""
        self.assertIsInstance(self.experiment.benchmark_suite, RSACryptographicBenchmarkSuite)
        self.assertIsInstance(self.experiment.z5d_executor, Z5DPredictorExecution)
        self.assertIsInstance(self.experiment.lopez_test, LopezTestMR)
        
        # Output directory should exist
        self.assertTrue(Path(self.temp_dir).exists())
    
    def test_single_experiment_run(self):
        """Test running a single experiment level."""
        # Create a test level with small k
        test_level = RSABenchmarkLevel(
            name="TEST-SMALL",
            bit_size=16,  # Very small for testing
            target_k="100",  # Small k for quick testing
            description="Test level",
            security_level="Test"
        )
        
        result = self.experiment._run_single_experiment(test_level)
        
        self.assertIsInstance(result, Z5DExperimentResult)
        self.assertEqual(result.level.name, "TEST-SMALL")
        
        if result.success:
            self.assertGreater(len(result.predicted_prime), 0)
            self.assertGreater(result.execution_time, 0)
    
    def test_results_analysis(self):
        """Test results analysis functionality."""
        # Create mock results
        test_level = RSABenchmarkLevel("TEST", 512, "1000", "Test", "Test")
        mock_result = Z5DExperimentResult(
            level=test_level,
            predicted_prime="12345",
            execution_time=0.1,
            prediction_error=None,
            verification_result=True,
            lopez_test_rounds=5,
            speedup_factor=None,
            memory_usage=100.0,
            precision_used=50,
            success=True
        )
        
        self.experiment.results = [mock_result]
        analysis = self.experiment._analyze_results(1.0)
        
        self.assertIn("experiment_metadata", analysis)
        self.assertIn("performance_metrics", analysis)
        self.assertIn("target_compliance", analysis)
        self.assertIn("detailed_results", analysis)
        
        # Check metadata
        meta = analysis["experiment_metadata"]
        self.assertEqual(meta["total_time"], 1.0)
        self.assertEqual(meta["successful_tests"], 1)
        self.assertEqual(meta["failed_tests"], 0)
    
    def test_results_saving(self):
        """Test that results are properly saved to files."""
        # Create minimal analysis data
        analysis = {
            "experiment_metadata": {
                "test": True,
                "total_time": 1.0,
                "levels_tested": ["TEST"],
                "successful_tests": 1,
                "failed_tests": 0,
                "mpmath_available": True,
                "precision_mode": "High"
            },
            "performance_metrics": {
                "mean_time": 0.1,
                "mean_execution_time": 0.1,
                "max_execution_time": 0.1,
                "min_execution_time": 0.1,
                "verification_success_rate": 1.0,
                "total_lopez_rounds": 5
            },
            "target_compliance": {
                "speed_target_met": True,
                "verification_target_met": True,
                "false_negatives": 0,
                "prediction_accuracy": "TBD",
                "speedup_factor": "TBD"
            },
            "detailed_results": []
        }
        
        self.experiment._save_results(analysis)
        
        # Check that files were created
        json_file = Path(self.temp_dir) / "z5d_rsa_experiment_results.json"
        report_file = Path(self.temp_dir) / "z5d_rsa_experiment_report.md"
        
        self.assertTrue(json_file.exists())
        self.assertTrue(report_file.exists())
        
        # Check file contents
        with open(json_file) as f:
            import json
            data = json.load(f)
            self.assertIn("experiment_metadata", data)
        
        with open(report_file) as f:
            content = f.read()
            self.assertIn("# Z5D-RSA Experiment Results", content)


class TestExperimentIntegration(unittest.TestCase):
    """Integration tests for the complete experiment."""
    
    def test_validation_mode(self):
        """Test implementation validation mode."""
        # This essentially tests what the CLI validation does
        try:
            suite = RSACryptographicBenchmarkSuite()
            executor = Z5DPredictorExecution()
            lopez = LopezTestMR()
            
            # Basic functionality tests
            self.assertEqual(len(suite.levels), 4)
            result = executor.execute_prediction("100", "test")
            self.assertEqual(len(result), 3)
            
            is_prime, metrics = lopez.validate_prime("17")
            self.assertTrue(is_prime)
            
            validation_passed = True
        except Exception as e:
            validation_passed = False
            print(f"Validation failed: {e}")
        
        self.assertTrue(validation_passed, "Implementation validation should pass")
    
    def test_quick_experiment_mode(self):
        """Test quick experiment mode with minimal computation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            experiment = Z5DRSAExperiment(output_dir=temp_dir, enable_detailed_logging=False)
            
            # Override to use smaller test values
            experiment.benchmark_suite.levels = [
                RSABenchmarkLevel("TEST-QUICK", 16, "50", "Quick test", "Test")
            ]
            
            try:
                results = experiment.run_full_experiment(target_levels=["TEST-QUICK"])
                
                self.assertIsInstance(results, dict)
                self.assertIn("experiment_metadata", results)
                self.assertIn("performance_metrics", results)
                self.assertIn("target_compliance", results)
                
                # Should have processed one test
                self.assertEqual(len(results["detailed_results"]), 1)
                
            except Exception as e:
                self.fail(f"Quick experiment mode failed: {e}")


def main():
    """Run the test suite."""
    # Set up test discovery
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(main())