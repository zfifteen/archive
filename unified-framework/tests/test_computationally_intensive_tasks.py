#!/usr/bin/env python3
"""
Test Suite for Computationally Intensive Research Tasks
=====================================================

Comprehensive tests for the 4 computationally intensive tasks:
1. Zeta Zero Expansion (1000+ Zeros)
2. Asymptotic Extrapolation to 10^12
3. Lorentz Analogy Frame Shift Analysis
4. Error Oscillation CSV Generation (1000 Bands)

Test Environment:
- Python 3.9+, NumPy, SciPy, Matplotlib, mpmath
- Multi-core CPU/GPU support
- High-precision arithmetic validation
"""

import sys
import os
import pytest
import numpy as np
import pandas as pd
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from statistical.computationally_intensive_tasks import ComputationallyIntensiveTasks


class TestComputationallyIntensiveTasks:
    """Test suite for computationally intensive research tasks."""
    
    @pytest.fixture(scope="class")
    def processor(self):
        """Create processor instance for testing."""
        return ComputationallyIntensiveTasks(precision_dps=25, num_cores=2)  # Reduced for testing
    
    def test_initialization(self, processor):
        """Test processor initialization."""
        assert processor.precision_dps == 25
        assert processor.num_cores == 2
        assert len(processor.extended_zeros) > 0
        assert processor.z5d_predictor is not None
        
    def test_zeta_zeros_loading(self, processor):
        """Test zeta zeros loading and computation."""
        zeros = processor.extended_zeros
        assert len(zeros) >= 500
        assert all(isinstance(z, (int, float)) for z in zeros)
        assert all(z > 0 for z in zeros)  # All imaginary parts should be positive
        
    def test_zeta_oscillation_single_value(self, processor):
        """Test zeta oscillation computation for single value."""
        # Use first 10 zeros for faster testing
        test_zeros = processor.extended_zeros[:10]
        result = processor.zeta_oscillation(100.0, test_zeros, amp=1.0)
        
        assert isinstance(result, (int, float))
        assert not np.isnan(result)
        assert not np.isinf(result)
        
    def test_zeta_oscillation_array(self, processor):
        """Test zeta oscillation computation for array of values."""
        test_zeros = processor.extended_zeros[:10]
        x_values = np.array([100.0, 1000.0, 10000.0])
        results = processor.zeta_oscillation(x_values, test_zeros, amp=1.0)
        
        assert len(results) == len(x_values)
        assert all(isinstance(r, (int, float)) for r in results)
        assert all(not np.isnan(r) for r in results)
        
    def test_z5d_prime_zeta(self, processor):
        """Test enhanced Z5D prime prediction."""
        x_values = np.array([1000.0, 10000.0, 100000.0])
        c, k_star, zeta_amp = 1.0, 0.3, -1000.0
        
        predictions = processor.z5d_prime_zeta(x_values, c, k_star, zeta_amp)
        
        assert len(predictions) == len(x_values)
        assert all(p > 0 for p in predictions)  # Should predict positive prime counts
        assert all(not np.isnan(p) for p in predictions)
        
    def test_task1_zeta_expansion_small(self, processor):
        """Test Task 1 with reduced parameters for testing."""
        # Use smaller range for testing
        x_range = np.logspace(7, 9, 10)  # 10 points instead of 1000
        initial_params = [1.0, 0.3, -1000.0]
        
        start_time = time.time()
        results = processor.task1_zeta_expansion(x_range=x_range, initial_params=initial_params)
        elapsed = time.time() - start_time
        
        # Validate results structure
        assert 'error' not in results, f"Task 1 failed: {results.get('error')}"
        assert 'fitted_parameters' in results
        assert 'metrics' in results
        assert 'performance' in results
        
        # Validate fitted parameters
        params = results['fitted_parameters']
        assert 'c' in params
        assert 'k_star' in params
        assert 'zeta_amp' in params
        
        # Validate metrics
        metrics = results['metrics']
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert 'mre' in metrics
        assert all(v >= 0 for v in metrics.values())
        
        # Performance check (should complete within reasonable time)
        assert elapsed < 60, f"Task 1 took too long: {elapsed:.2f} seconds"
        
        print(f"✓ Task 1 test completed in {elapsed:.2f} seconds")
        
    def test_task2_asymptotic_extrapolation_small(self, processor):
        """Test Task 2 with reduced parameters."""
        k_range = np.logspace(7, 10, 10)  # Smaller range for testing
        
        start_time = time.time()
        results = processor.task2_asymptotic_extrapolation(k_range=k_range)
        elapsed = time.time() - start_time
        
        # Validate results structure
        assert 'error' not in results, f"Task 2 failed: {results.get('error')}"
        assert 'fitted_parameters' in results
        assert 'extrapolation_metrics' in results
        assert 'k_12_validation' in results
        
        # Validate extrapolation metrics
        metrics = results['extrapolation_metrics']
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert metrics['mse'] >= 0
        assert metrics['mae'] >= 0
        
        # Performance check
        assert elapsed < 60, f"Task 2 took too long: {elapsed:.2f} seconds"
        
        print(f"✓ Task 2 test completed in {elapsed:.2f} seconds")
        
    def test_task3_lorentz_analogy_small(self, processor):
        """Test Task 3 with reduced parameters."""
        n_range = np.logspace(5, 6, 100)  # Smaller range for testing
        
        start_time = time.time()
        results = processor.task3_lorentz_analogy(n_range=n_range)
        elapsed = time.time() - start_time
        
        # Validate results structure
        assert 'error' not in results, f"Task 3 failed: {results.get('error')}"
        assert 'frame_shifts' in results
        assert 'correlations' in results
        assert 'prime_analysis' in results
        
        # Validate frame shifts
        frame_shifts = results['frame_shifts']
        assert 'delta_n' in frame_shifts
        assert 'dilated_shifts' in frame_shifts
        assert len(frame_shifts['delta_n']) == len(n_range)
        
        # Validate correlations
        correlations = results['correlations']
        assert 'dilated_shifts_prime_density' in correlations
        corr_data = correlations['dilated_shifts_prime_density']
        assert 'correlation' in corr_data
        assert 'p_value' in corr_data
        assert isinstance(corr_data['correlation'], (int, float))
        assert -1 <= corr_data['correlation'] <= 1
        
        # Performance check
        assert elapsed < 60, f"Task 3 took too long: {elapsed:.2f} seconds"
        
        print(f"✓ Task 3 test completed in {elapsed:.2f} seconds")
        
    def test_riemann_r_approximation(self, processor):
        """Test Riemann R function approximation."""
        test_values = [100.0, 1000.0, 10000.0]
        
        for x in test_values:
            result = processor.riemann_r_approximation(x)
            assert isinstance(result, (int, float))
            assert result > 0  # Should be positive
            assert not np.isnan(result)
            assert not np.isinf(result)
            
            # Rough sanity check: R(x) should be close to x/ln(x)
            expected_order = x / np.log(x)
            assert 0.5 * expected_order < result < 2.0 * expected_order
            
    def test_task4_csv_generation_small(self, processor):
        """Test Task 4 with reduced parameters."""
        output_file = 'test_error_oscillations.csv'
        num_bands = 10  # Much smaller for testing
        
        start_time = time.time()
        results = processor.task4_error_oscillation_csv(output_file=output_file, num_bands=num_bands)
        elapsed = time.time() - start_time
        
        # Validate results structure
        assert 'error' not in results, f"Task 4 failed: {results.get('error')}"
        assert 'csv_file' in results
        assert 'error_statistics' in results
        assert 'performance' in results
        
        # Check that CSV was created
        csv_path = results['csv_file']
        assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
        
        # Validate CSV content
        df = pd.read_csv(csv_path)
        assert len(df) == num_bands
        assert 'band' in df.columns
        assert 'predicted' in df.columns
        assert 'true' in df.columns
        assert 'error_percent' in df.columns
        
        # Validate data types and ranges
        assert all(df['band'] > 0)
        assert all(df['predicted'] > 0)
        assert all(df['true'] > 0)
        assert all(np.isfinite(df['error_percent']))
        
        # Performance check
        assert elapsed < 60, f"Task 4 took too long: {elapsed:.2f} seconds"
        
        # Cleanup
        if os.path.exists(csv_path):
            os.remove(csv_path)
            
        print(f"✓ Task 4 test completed in {elapsed:.2f} seconds")
        
    def test_integration_all_tasks_small(self, processor):
        """Integration test: run all tasks with small parameters."""
        # Override the run_all_tasks method to use smaller parameters
        print("Running integration test with reduced parameters...")
        
        start_time = time.time()
        
        # Run individual tasks with small parameters
        task1_results = processor.task1_zeta_expansion(
            x_range=np.logspace(7, 8, 5),
            initial_params=[1.0, 0.3, -1000.0]
        )
        
        task2_results = processor.task2_asymptotic_extrapolation(
            k_range=np.logspace(7, 9, 5)
        )
        
        task3_results = processor.task3_lorentz_analogy(
            n_range=np.logspace(5, 6, 50)
        )
        
        task4_results = processor.task4_error_oscillation_csv(
            output_file='integration_test.csv',
            num_bands=5
        )
        
        elapsed = time.time() - start_time
        
        # Validate all tasks completed successfully
        assert 'error' not in task1_results
        assert 'error' not in task2_results
        assert 'error' not in task3_results
        assert 'error' not in task4_results
        
        # Cleanup
        csv_path = task4_results.get('csv_file')
        if csv_path and os.path.exists(csv_path):
            os.remove(csv_path)
            
        print(f"✓ Integration test completed in {elapsed:.2f} seconds")
        
        # Performance check for overall integration
        assert elapsed < 300, f"Integration test took too long: {elapsed:.2f} seconds"


class TestPerformanceValidation:
    """Performance validation tests."""
    
    def test_parallel_processing(self):
        """Test that parallel processing works."""
        processor_single = ComputationallyIntensiveTasks(precision_dps=25, num_cores=1)
        processor_multi = ComputationallyIntensiveTasks(precision_dps=25, num_cores=2)
        
        test_zeros = processor_single.extended_zeros[:20]
        x_values = np.array([1000.0, 10000.0])
        
        # Time single-core
        start = time.time()
        result_single = processor_single.zeta_oscillation(x_values, test_zeros)
        time_single = time.time() - start
        
        # Time multi-core
        start = time.time()
        result_multi = processor_multi.zeta_oscillation(x_values, test_zeros)
        time_multi = time.time() - start
        
        # Results should be approximately equal
        np.testing.assert_allclose(result_single, result_multi, rtol=1e-10)
        
        print(f"Single-core: {time_single:.4f}s, Multi-core: {time_multi:.4f}s")
        
    def test_precision_stability(self):
        """Test numerical stability at different precisions."""
        precisions = [25, 50]
        results = {}
        
        for dps in precisions:
            processor = ComputationallyIntensiveTasks(precision_dps=dps, num_cores=1)
            test_zeros = processor.extended_zeros[:10]
            
            result = processor.zeta_oscillation(1000.0, test_zeros)
            results[dps] = result
            
        # Results should be stable across precisions
        assert abs(results[25] - results[50]) / abs(results[50]) < 0.01  # Within 1%
        
    def test_memory_usage(self):
        """Test memory usage for large computations."""
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Measure initial memory
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run computation
        processor = ComputationallyIntensiveTasks(precision_dps=25, num_cores=1)
        _ = processor.task3_lorentz_analogy(n_range=np.logspace(5, 6, 1000))
        
        # Measure peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.1f} MB -> {peak_memory:.1f} MB (+{memory_increase:.1f} MB)")
        
        # Should not use excessive memory (< 1GB increase)
        assert memory_increase < 1000, f"Excessive memory usage: {memory_increase:.1f} MB"


def run_comprehensive_tests():
    """Run comprehensive test suite."""
    print("=" * 60)
    print("COMPUTATIONALLY INTENSIVE TASKS - TEST SUITE")
    print("=" * 60)
    
    # Create processor for manual testing
    processor = ComputationallyIntensiveTasks(precision_dps=25, num_cores=2)
    
    print(f"Test environment:")
    print(f"  Precision: {processor.precision_dps} decimal places")
    print(f"  CPU cores: {processor.num_cores}")
    print(f"  Zeta zeros: {len(processor.extended_zeros)}")
    print()
    
    # Manual test execution with detailed output
    test_suite = TestComputationallyIntensiveTasks()
    
    tests = [
        ("Initialization", lambda: test_suite.test_initialization(processor)),
        ("Zeta Zeros Loading", lambda: test_suite.test_zeta_zeros_loading(processor)),
        ("Zeta Oscillation Single", lambda: test_suite.test_zeta_oscillation_single_value(processor)),
        ("Zeta Oscillation Array", lambda: test_suite.test_zeta_oscillation_array(processor)),
        ("Z5D Prime Zeta", lambda: test_suite.test_z5d_prime_zeta(processor)),
        ("Task 1 (Small)", lambda: test_suite.test_task1_zeta_expansion_small(processor)),
        ("Task 2 (Small)", lambda: test_suite.test_task2_asymptotic_extrapolation_small(processor)),
        ("Task 3 (Small)", lambda: test_suite.test_task3_lorentz_analogy_small(processor)),
        ("Riemann R", lambda: test_suite.test_riemann_r_approximation(processor)),
        ("Task 4 (Small)", lambda: test_suite.test_task4_csv_generation_small(processor)),
        ("Integration Test", lambda: test_suite.test_integration_all_tasks_small(processor)),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            test_func()
            print(f"  ✓ {test_name} passed")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test_name} failed: {e}")
            
    print()
    print("=" * 60)
    print(f"TEST RESULTS: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! Ready for production runs.")
    else:
        print("⚠ Some tests failed. Review implementation before production.")
        
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)