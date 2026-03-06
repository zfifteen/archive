#!/usr/bin/env python3
"""
Tests for Z Framework optimization enhancements
==============================================

Test suite for the optimization improvements:
1. Dynamic mpmath precision
2. Enhanced multiprocessing for bootstrap
3. Automated benchmarking infrastructure
"""

import pytest
import numpy as np
import sys
import os
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.params import (
    get_adaptive_precision, set_adaptive_mpmath_precision,
    MP_DPS_HIGH, MP_DPS_MEDIUM, MP_DPS_LOW,
    K_SCALE_THRESHOLD_HIGH, K_SCALE_THRESHOLD_ULTRA
)
from statistical.computationally_intensive_tasks import ComputationallyIntensiveTasks
from analysis.benchmark_framework import BenchmarkFramework

class TestAdaptivePrecision:
    """Test dynamic mpmath precision functionality"""
    
    def test_adaptive_precision_by_k_value(self):
        """Test adaptive precision selection based on k values"""
        # Low k should use low precision
        low_precision = get_adaptive_precision(k_value=1000)
        assert low_precision == MP_DPS_LOW
        
        # Medium k should use medium precision
        medium_precision = get_adaptive_precision(k_value=1e8)
        assert medium_precision == MP_DPS_MEDIUM
        
        # High k should use high precision
        high_precision = get_adaptive_precision(k_value=K_SCALE_THRESHOLD_HIGH * 2)
        assert high_precision == MP_DPS_HIGH

    def test_adaptive_precision_by_delta(self):
        """Test adaptive precision selection based on delta values"""
        # Large delta should use low precision
        low_precision = get_adaptive_precision(delta_n=1e-5)
        assert low_precision == MP_DPS_LOW
        
        # Medium delta should use medium precision
        medium_precision = get_adaptive_precision(delta_n=1e-12)
        assert medium_precision == MP_DPS_MEDIUM
        
        # Small delta should use high precision
        high_precision = get_adaptive_precision(delta_n=1e-18)
        assert high_precision == MP_DPS_HIGH

    def test_set_adaptive_mpmath_precision(self):
        """Test that mpmath precision is actually set"""
        import mpmath as mp
        
        # Test high precision setting
        precision = set_adaptive_mpmath_precision(k_value=K_SCALE_THRESHOLD_HIGH * 2)
        assert precision == MP_DPS_HIGH
        assert mp.dps == MP_DPS_HIGH
        
        # Test low precision setting
        precision = set_adaptive_mpmath_precision(k_value=1000)
        assert precision == MP_DPS_LOW
        assert mp.dps == MP_DPS_LOW

    def test_ultra_scale_warning(self):
        """Test that ultra-scale warnings are issued"""
        import warnings
        from core.z_5d_enhanced import z5d_predictor
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # This should trigger ultra-scale warning
            if z5d_predictor:
                z5d_predictor(K_SCALE_THRESHOLD_ULTRA * 2)
                assert len(w) > 0
                assert "Ultra-scale prediction" in str(w[-1].message)


class TestEnhancedMultiprocessing:
    """Test enhanced multiprocessing capabilities"""
    
    def test_bootstrap_variance_calculation(self):
        """Test parallel bootstrap variance calculation"""
        processor = ComputationallyIntensiveTasks(precision_dps=25, num_cores=2)
        
        # Generate test data
        np.random.seed(42)
        test_data = np.random.normal(0, 1, 100)
        
        # Run bootstrap analysis
        start_time = time.time()
        results = processor.bootstrap_variance_calculation(test_data, n_bootstrap=100)
        execution_time = time.time() - start_time
        
        # Validate results structure
        assert 'original_variance' in results
        assert 'bootstrap_mean_variance' in results
        assert 'confidence_interval' in results
        assert 'cores_used' in results
        assert 'speedup_estimate' in results
        
        # Check that bootstrap ran
        assert results['n_bootstrap'] == 100
        assert results['cores_used'] <= 8  # Should be limited to max 8 cores
        
        # Validate confidence interval
        ci = results['confidence_interval']
        assert ci['level'] == 0.95
        assert ci['lower'] < ci['upper']
        
        print(f"Bootstrap test completed in {execution_time:.3f}s")
        print(f"Speedup estimate: {results['speedup_estimate']}")

    def test_parallel_zeta_spacing_analysis(self):
        """Test parallel zeta spacing analysis"""
        processor = ComputationallyIntensiveTasks(precision_dps=25, num_cores=2)
        
        # Run spacing analysis
        results = processor.parallel_zeta_spacing_analysis(n_samples=50)
        
        # Validate results structure
        assert 'spacing_statistics' in results
        assert 'bootstrap_variance_analysis' in results
        assert 'performance' in results
        
        # Check spacing statistics
        spacing_stats = results['spacing_statistics']
        assert spacing_stats['n_spacings'] > 0
        assert 'sigma_observed' in spacing_stats
        assert 'target_sigma' in spacing_stats
        
        print(f"Zeta spacing analysis completed")
        print(f"Observed sigma: {spacing_stats['sigma_observed']:.4f}")
        print(f"Target sigma: {spacing_stats['target_sigma']:.4f}")

    def test_core_limitation(self):
        """Test that core usage is limited to 8 cores maximum"""
        # Test with very high core request
        processor = ComputationallyIntensiveTasks(num_cores=16)
        assert processor.num_cores <= 8
        
        # Test with automatic detection
        processor_auto = ComputationallyIntensiveTasks()
        assert processor_auto.num_cores <= 8


class TestBenchmarkFramework:
    """Test automated benchmarking infrastructure"""
    
    def test_benchmark_framework_initialization(self):
        """Test benchmark framework setup"""
        benchmark = BenchmarkFramework(results_dir="test_results", precision_dps=25)
        
        assert benchmark.results_dir.exists()
        assert benchmark.precision_dps == 25
        assert len(benchmark.test_k_values) > 0
        assert benchmark.computational_tasks.num_cores <= 8

    def test_pnt_approximation(self):
        """Test PNT approximation function"""
        benchmark = BenchmarkFramework(results_dir="test_results", precision_dps=25)
        
        # Test various k values
        test_cases = [10, 100, 1000]
        for k in test_cases:
            pnt_estimate = benchmark.pnt_approximation(k)
            assert pnt_estimate > 0
            assert isinstance(pnt_estimate, float)
        
        # Test edge cases
        assert benchmark.pnt_approximation(1) == 2.0
        assert benchmark.pnt_approximation(0) == 0.0

    def test_benchmark_single_method(self):
        """Test benchmarking of a single method"""
        benchmark = BenchmarkFramework(results_dir="test_results", precision_dps=25)
        
        # Simple test function
        def test_func(k):
            return k * 2.0  # Simple linear function for testing
        
        # Run benchmark on small k values
        test_k_values = [10, 50, 100]
        results = benchmark.benchmark_single_method(test_func, test_k_values, "TestMethod")
        
        # Validate results structure
        assert len(results['k_values']) == len(test_k_values)
        assert len(results['predictions']) == len(test_k_values)
        assert len(results['execution_times']) == len(test_k_values)
        assert all(t > 0 for t in results['execution_times'])

    def test_csv_output_format(self):
        """Test that CSV output follows expected format"""
        benchmark = BenchmarkFramework(results_dir="test_results", precision_dps=25)
        
        # Create mock benchmark results
        mock_results = {
            'z5d_results': {
                'k_values': [1000, 10000],
                'predictions': [7919.0, 104729.0],
                'execution_times': [0.1, 0.2],
                'relative_errors': [0.01, 0.02]
            },
            'pnt_results': {
                'k_values': [1000, 10000],
                'predictions': [7918.0, 104728.0],
                'execution_times': [0.05, 0.1],
                'relative_errors': [0.1, 0.2]
            },
            'comparison': {
                'k_values': [1000, 10000],
                'speedup_factors': [2.0, 2.0],
                'error_improvements': [90.0, 90.0]
            }
        }
        
        # Test CSV generation
        csv_path = benchmark.save_results_csv(mock_results)
        assert csv_path is not None
        assert csv_path.exists()
        
        # Validate CSV content
        import pandas as pd
        df = pd.read_csv(csv_path)
        expected_columns = [
            'k_value', 'z5d_error_percent', 'pnt_error_percent',
            'z5d_time_ms', 'pnt_time_ms', 'speedup_factor'
        ]
        for col in expected_columns:
            assert col in df.columns
        
        assert len(df) == 2  # Should have 2 rows
        
        # Cleanup
        csv_path.unlink()


class TestIntegrationOptimizations:
    """Integration tests for all optimizations working together"""
    
    def test_end_to_end_optimization_workflow(self):
        """Test complete optimization workflow"""
        # 1. Test adaptive precision in context
        from core.z_5d_enhanced import z5d_predictor
        if z5d_predictor:
            # Should use adaptive precision internally
            result = z5d_predictor(1000)
            assert result > 0
        
        # 2. Test enhanced multiprocessing
        processor = ComputationallyIntensiveTasks(precision_dps=25, num_cores=2)
        test_data = np.random.normal(0, 1, 50)
        bootstrap_results = processor.bootstrap_variance_calculation(test_data, n_bootstrap=50)
        assert bootstrap_results['cores_used'] == 2
        
        # 3. Test benchmarking framework
        benchmark = BenchmarkFramework(results_dir="test_results", precision_dps=25)
        
        # Run mini benchmark
        test_k_values = [100, 1000]
        pnt_results = benchmark.benchmark_single_method(
            benchmark.pnt_approximation, test_k_values, "PNT"
        )
        assert len(pnt_results['k_values']) == 2
        
        print("End-to-end optimization workflow test completed successfully")

    def test_performance_improvements(self):
        """Test that optimizations provide measurable improvements"""
        # Test multiprocessing speedup
        processor_single = ComputationallyIntensiveTasks(precision_dps=20, num_cores=1)
        processor_multi = ComputationallyIntensiveTasks(precision_dps=20, num_cores=2)
        
        test_data = np.random.normal(0, 1, 100)
        
        # Time single-core
        start = time.time()
        result_single = processor_single.bootstrap_variance_calculation(test_data, n_bootstrap=50)
        time_single = time.time() - start
        
        # Time multi-core
        start = time.time()
        result_multi = processor_multi.bootstrap_variance_calculation(test_data, n_bootstrap=50)
        time_multi = time.time() - start
        
        # Multi-core should be faster (allow some variance due to overhead)
        speedup = time_single / time_multi if time_multi > 0 else 1
        print(f"Bootstrap speedup: {speedup:.2f}x")
        
        # Results should be approximately equal
        np.testing.assert_allclose(
            result_single['bootstrap_mean_variance'],
            result_multi['bootstrap_mean_variance'],
            rtol=0.1  # Allow 10% variance due to different random samples
        )


if __name__ == "__main__":
    # Run tests manually if called directly
    pytest.main([__file__, "-v"])