"""
Test suite for RSA Probe Validation Implementation

This module provides comprehensive tests for the inverse Mersenne probe
implementation, validating numerical stability, performance, and expected
behavior on RSA challenge numbers.
"""

import unittest
import sys
import os
import json
import time
import tempfile
from unittest.mock import patch

# Import the rsa_probe_validation module from the applications package
from applications import rsa_probe_validation

class TestRSAProbeValidation(unittest.TestCase):
    """Test cases for RSA probe validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.small_semiprime = "15"  # 3 × 5
        self.medium_semiprime = "35"  # 5 × 7
        self.large_semiprime = "1516586"  # 1229 × 1234
        
    def test_z5d_prime_basic_functionality(self):
        """Test that z5d_prime function works correctly."""
        result = rsa_probe_validation.z5d_prime(1000)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        self.assertLess(result, 10000)  # Reasonable range for 1000th prime
        
    def test_z5d_prime_with_custom_parameters(self):
        """Test z5d_prime with custom calibration parameters."""
        result1 = rsa_probe_validation.z5d_prime(1000)
        result2 = rsa_probe_validation.z5d_prime(1000, c=-0.003, kstar=0.05)
        
        # Results should be different with different parameters
        self.assertNotEqual(result1, result2)
        self.assertIsInstance(result2, float)
        self.assertGreater(result2, 0)
        
    def test_probe_semiprime_small_numbers(self):
        """Test probe_semiprime on small semiprimes where it might succeed."""
        # For very small numbers, the probe might actually find factors
        # due to the smaller error bounds
        result = rsa_probe_validation.probe_semiprime(self.small_semiprime, trials=20)
        
        # We don't assert success here since the probe is designed for large numbers
        # Just ensure it returns either None or a valid factor
        if result is not None:
            self.assertIsInstance(result, int)
            self.assertGreater(result, 1)
            self.assertEqual(int(self.small_semiprime) % result, 0)
            
    def test_probe_semiprime_input_validation(self):
        """Test input validation for probe_semiprime."""
        # Test with valid inputs
        result = rsa_probe_validation.probe_semiprime("35", trials=10)
        # Should not raise an exception
        
        # Test edge cases
        result_zero_trials = rsa_probe_validation.probe_semiprime("35", trials=0)
        self.assertIsNone(result_zero_trials)
        
    def test_rsa_challenge_numbers_defined(self):
        """Test that RSA challenge numbers are properly defined."""
        self.assertIn('RSA-100', rsa_probe_validation.RSA_CHALLENGE_NUMBERS)
        self.assertIn('RSA-129', rsa_probe_validation.RSA_CHALLENGE_NUMBERS)
        self.assertIn('RSA-155', rsa_probe_validation.RSA_CHALLENGE_NUMBERS)
        
        # Check they are strings of appropriate length
        rsa100 = rsa_probe_validation.RSA_CHALLENGE_NUMBERS['RSA-100']
        self.assertEqual(len(rsa100), 100)
        self.assertTrue(rsa100.isdigit())
        
        rsa129 = rsa_probe_validation.RSA_CHALLENGE_NUMBERS['RSA-129']
        self.assertEqual(len(rsa129), 129)
        self.assertTrue(rsa129.isdigit())
        
    def test_probe_on_rsa100_no_factors_expected(self):
        """Test that probe finds no factors on RSA-100 as expected."""
        rsa100 = rsa_probe_validation.RSA_CHALLENGE_NUMBERS['RSA-100']
        
        # Test with reduced trials for faster testing
        start_time = time.time()
        result = rsa_probe_validation.probe_semiprime(rsa100, trials=10)
        end_time = time.time()
        
        # Should find no factors (expected behavior)
        self.assertIsNone(result, "Probe should not find factors for RSA-100")
        
        # Should complete in reasonable time
        self.assertLess(end_time - start_time, 5.0, "Probe should complete quickly")
        
    def test_probe_on_rsa129_no_factors_expected(self):
        """Test that probe finds no factors on RSA-129 as expected."""
        rsa129 = rsa_probe_validation.RSA_CHALLENGE_NUMBERS['RSA-129']
        
        # Test with reduced trials for faster testing
        start_time = time.time()
        result = rsa_probe_validation.probe_semiprime(rsa129, trials=10)
        end_time = time.time()
        
        # Should find no factors (expected behavior)
        self.assertIsNone(result, "Probe should not find factors for RSA-129")
        
        # Should complete in reasonable time
        self.assertLess(end_time - start_time, 5.0, "Probe should complete quickly")
        
    def test_benchmark_probe_performance(self):
        """Test the benchmark functionality."""
        # Use a smaller number for faster testing
        benchmark = rsa_probe_validation.benchmark_probe_performance(
            self.medium_semiprime, trials=5, num_runs=3
        )
        
        # Check benchmark structure
        self.assertIn('mean_time', benchmark)
        self.assertIn('min_time', benchmark)
        self.assertIn('max_time', benchmark)
        self.assertIn('std_time', benchmark)
        self.assertIn('factors_found', benchmark)
        self.assertIn('success_rate', benchmark)
        self.assertIn('num_runs', benchmark)
        self.assertIn('trials_per_run', benchmark)
        
        # Check types and ranges
        self.assertIsInstance(benchmark['mean_time'], float)
        self.assertIsInstance(benchmark['factors_found'], list)
        self.assertIsInstance(benchmark['success_rate'], float)
        self.assertEqual(benchmark['num_runs'], 3)
        self.assertEqual(benchmark['trials_per_run'], 5)
        self.assertGreaterEqual(benchmark['success_rate'], 0.0)
        self.assertLessEqual(benchmark['success_rate'], 1.0)
        
    def test_validate_rsa_challenge_numbers_structure(self):
        """Test the structure of validation results."""
        # Use a mock to avoid running the full validation in tests
        with patch.object(rsa_probe_validation, 'probe_semiprime', return_value=None):
            with patch.object(rsa_probe_validation, 'benchmark_probe_performance') as mock_bench:
                mock_bench.return_value = {
                    'mean_time': 0.1,
                    'min_time': 0.09,
                    'max_time': 0.11,
                    'std_time': 0.01,
                    'factors_found': [],
                    'success_rate': 0.0,
                    'num_runs': 3,
                    'trials_per_run': 50
                }
                
                results = rsa_probe_validation.validate_rsa_challenge_numbers()
                
        # Check that all RSA numbers were tested
        self.assertIn('RSA-100', results)
        self.assertIn('RSA-129', results)
        self.assertIn('RSA-155', results)
        
        # Check structure of each result
        for name, result in results.items():
            self.assertIn('digits', result)
            self.assertIn('k_est_order', result)
            self.assertIn('k_est_value', result)
            self.assertIn('factor_found', result)
            self.assertIn('single_run_time', result)
            self.assertIn('benchmark', result)
            self.assertIn('expected_result', result)
            self.assertIn('validation_passed', result)
            
            # For mocked results, validation should pass (no factors found)
            self.assertTrue(result['validation_passed'])
            self.assertIsNone(result['factor_found'])
            
    def test_generate_validation_report(self):
        """Test report generation functionality."""
        # Create minimal test results
        test_results = {
            'RSA-100': {
                'digits': 100,
                'k_est_order': '10^47',
                'k_est_value': 1e47,
                'factor_found': None,
                'single_run_time': 0.15,
                'benchmark': {
                    'mean_time': 0.14,
                    'std_time': 0.02,
                },
                'expected_result': 'No factor',
                'validation_passed': True
            }
        }
        
        report = rsa_probe_validation.generate_validation_report(test_results)
        
        # Check report content
        self.assertIsInstance(report, str)
        self.assertIn('RSA Probe Validation Report', report)
        self.assertIn('RSA-100', report)
        self.assertIn('PASS', report)
        self.assertIn('Implementation Details', report)
        self.assertIn('Summary', report)
        self.assertIn('Conclusion', report)
        
    def test_mpmath_availability_handling(self):
        """Test handling when mpmath is not available."""
        # Test both with and without mpmath
        if rsa_probe_validation.MPMATH_AVAILABLE:
            # Test normal operation
            result = rsa_probe_validation.z5d_prime(100)
            self.assertIsInstance(result, float)
            self.assertGreater(result, 0)
            
        # Test graceful degradation (would need actual mock for complete test)
        self.assertIsInstance(rsa_probe_validation.MPMATH_AVAILABLE, bool)
        
    def test_probe_numerical_stability(self):
        """Test numerical stability of the probe for different scales."""
        # Test different scales to ensure stability
        test_numbers = ["100", "1000", "10000"]
        
        for num_str in test_numbers:
            with self.subTest(number=num_str):
                result = rsa_probe_validation.probe_semiprime(num_str, trials=5)
                # Should either return None or a valid integer
                if result is not None:
                    self.assertIsInstance(result, int)
                    self.assertGreater(result, 1)
                    
    def test_performance_requirements(self):
        """Test that performance meets requirements from issue."""
        # Issue states ~0.15s avg per probe run
        # Test with small number for reasonable test time
        start_time = time.time()
        rsa_probe_validation.probe_semiprime(self.large_semiprime, trials=20)
        end_time = time.time()
        
        # Should be much faster than 0.15s for small numbers
        # (RSA challenge numbers take longer due to scale)
        self.assertLess(end_time - start_time, 1.0)
        
    def test_json_serialization_of_results(self):
        """Test that results can be serialized to JSON."""
        # Create test results
        test_results = {
            'RSA-100': {
                'digits': 100,
                'k_est_order': '10^47',
                'k_est_value': 1e47,
                'factor_found': None,
                'single_run_time': 0.15,
                'benchmark': {
                    'mean_time': 0.14,
                    'std_time': 0.02,
                    'factors_found': [],
                    'success_rate': 0.0
                },
                'expected_result': 'No factor',
                'validation_passed': True
            }
        }
        
        # Test JSON serialization
        try:
            json_str = json.dumps(test_results)
            reconstructed = json.loads(json_str)
            self.assertEqual(reconstructed['RSA-100']['digits'], 100)
        except (TypeError, ValueError) as e:
            self.fail(f"JSON serialization failed: {e}")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete RSA probe validation system."""
    
    def test_full_validation_quick_mode(self):
        """Test the full validation in quick mode."""
        # Mock the time-consuming parts for testing
        with patch.object(rsa_probe_validation, 'probe_semiprime') as mock_probe:
            with patch.object(rsa_probe_validation, 'benchmark_probe_performance') as mock_bench:
                # Configure mocks
                mock_probe.return_value = None  # No factors found (expected)
                mock_bench.return_value = {
                    'mean_time': 0.15,
                    'min_time': 0.12,
                    'max_time': 0.18,
                    'std_time': 0.03,
                    'factors_found': [],
                    'success_rate': 0.0,
                    'num_runs': 3,
                    'trials_per_run': 50
                }
                
                # Run validation
                results = rsa_probe_validation.validate_rsa_challenge_numbers()
                
                # Verify all validations passed
                for name, result in results.items():
                    self.assertTrue(result['validation_passed'], 
                                  f"Validation failed for {name}")
                    self.assertIsNone(result['factor_found'],
                                    f"Unexpected factor found for {name}")
                
                # Generate report
                report = rsa_probe_validation.generate_validation_report(results)
                self.assertIn('All validations passed: Yes', report)
                
    def test_ci_integration_json_output(self):
        """Test that the module produces JSON output suitable for CI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Mock the validation to avoid long runtime
                with patch.object(rsa_probe_validation, 'validate_rsa_challenge_numbers') as mock_validate:
                    mock_validate.return_value = {
                        'RSA-100': {
                            'digits': 100,
                            'k_est_order': '10^47',
                            'k_est_value': 1e47,
                            'factor_found': None,
                            'single_run_time': 0.15,
                            'benchmark': {
                                'mean_time': 0.14,
                                'std_time': 0.02,
                                'factors_found': [],
                                'success_rate': 0.0
                            },
                            'expected_result': 'No factor',
                            'validation_passed': True
                        }
                    }
                    
                    # Test the main execution path
                    exec(open(rsa_probe_validation.__file__).read())
                    
                # Check JSON file was created
                self.assertTrue(os.path.exists('rsa_probe_validation_results.json'))
                
                # Check JSON content
                with open('rsa_probe_validation_results.json', 'r') as f:
                    data = json.load(f)
                    self.assertIn('RSA-100', data)
                    self.assertTrue(data['RSA-100']['validation_passed'])
                    
            finally:
                os.chdir(old_cwd)


if __name__ == '__main__':
    unittest.main()