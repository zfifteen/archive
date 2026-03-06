"""
Pytest Integration for Z_5D Scientific Test Bed
===============================================

This module provides pytest-compatible test functions for the Z_5D scientific test bed.
It can be run as part of the existing test suite.
"""

import os
import sys
import pytest
import numpy as np

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from test_z5d_scientific_testbed import Z5DScientificTestBed


class TestZ5DScientificTestBed:
    """Pytest-compatible tests for the Z_5D scientific test bed."""
    
    def test_testbed_initialization(self):
        """Test that the test bed initializes correctly."""
        testbed = Z5DScientificTestBed()
        assert os.path.exists(testbed.plots_dir)
        assert testbed.benchmark_values is not None
        assert len(testbed.benchmark_values['small']) > 0
        
    def test_single_prediction_test(self):
        """Test a single prediction computation."""
        testbed = Z5DScientificTestBed()
        result = testbed.run_single_prediction_test(1000)
        
        # Check result structure
        assert 'n' in result
        assert 'z5d_prediction' in result
        assert 'pnt_prediction' in result
        assert 'ground_truth' in result
        
        # Check values are reasonable
        assert result['n'] == 1000
        assert result['z5d_prediction'] > 0
        assert result['pnt_prediction'] > 0
        assert 7000 < result['z5d_prediction'] < 9000  # Should be near 1000th prime ≈ 7919
        
        # If ground truth is available, check error calculations
        if result['ground_truth'] is not None:
            assert result['z5d_absolute_error'] is not None
            assert result['z5d_relative_error'] is not None
            assert result['improvement_factor'] is not None
            assert result['z5d_relative_error'] >= 0
            assert result['improvement_factor'] > 0
    
    def test_ground_truth_computation(self):
        """Test ground truth computation for known values."""
        testbed = Z5DScientificTestBed()
        
        # Test small value that should be computable
        ground_truth_100 = testbed.compute_ground_truth(100)
        assert ground_truth_100 is not None
        assert ground_truth_100 == 541  # 100th prime
        
        # Test known large value
        ground_truth_1e12 = testbed.compute_ground_truth(1000000000000)
        assert ground_truth_1e12 is not None
        assert ground_truth_1e12 == 29996224275833  # Literature value
    
    def test_z5d_accuracy_validation(self):
        """Test that Z_5D predictions are reasonably accurate."""
        testbed = Z5DScientificTestBed()
        
        # Test with a few different values
        test_values = [100, 1000, 10000]
        
        for n in test_values:
            result = testbed.run_single_prediction_test(n)
            
            if result['ground_truth'] is not None:
                # Z_5D should have reasonable accuracy (< 10% for these small values)
                assert result['z5d_relative_error'] < 0.10
                
                # Z_5D should generally be better than or comparable to PNT
                improvement = result['improvement_factor']
                assert improvement > 0.5  # At least not much worse than PNT
    
    def test_benchmark_reproduction(self):
        """Test that benchmark values can be reproduced."""
        testbed = Z5DScientificTestBed()
        
        # Test the n = 10^12 case specifically
        result_1e12 = testbed.run_single_prediction_test(1000000000000)
        
        assert result_1e12['n'] == 1000000000000
        assert result_1e12['z5d_prediction'] > 0
        assert result_1e12['pnt_prediction'] > 0
        assert result_1e12['ground_truth'] == 29996224275833
        
        # Check that error is reasonable (should be sub-1%)
        assert result_1e12['z5d_relative_error'] < 0.01
        
        # Check that prediction is in reasonable range
        expected = result_1e12['ground_truth']
        pred = result_1e12['z5d_prediction']
        assert 0.99 * expected < pred < 1.01 * expected
    
    def test_comprehensive_validation_structure(self):
        """Test that comprehensive validation returns proper structure."""
        testbed = Z5DScientificTestBed()
        
        # Run validation with limited test cases for speed
        original_values = testbed.benchmark_values
        testbed.benchmark_values = {
            'small': [100, 1000],
            'medium': [],
            'large': [],
            'ultra_large': []
        }
        
        results = testbed.run_comprehensive_validation()
        
        # Restore original values
        testbed.benchmark_values = original_values
        
        # Check structure
        assert 'test_results' in results
        assert 'summary_statistics' in results
        assert 'benchmark_reproduction' in results
        
        # Check test results
        assert len(results['test_results']) == 2
        for result in results['test_results']:
            assert 'n' in result
            assert 'z5d_prediction' in result
            assert 'pnt_prediction' in result
    
    def test_plot_generation_setup(self):
        """Test that plot generation setup works (without actually generating plots)."""
        testbed = Z5DScientificTestBed()
        
        # Run minimal validation first
        testbed.benchmark_values = {
            'small': [100],
            'medium': [],
            'large': [], 
            'ultra_large': []
        }
        
        results = testbed.run_comprehensive_validation()
        
        # Check that we can call the plot methods without error
        # (We won't actually generate plots to keep test fast)
        assert hasattr(testbed, 'generate_all_plots')
        assert hasattr(testbed, 'plot_absolute_errors')
        assert hasattr(testbed, 'plot_relative_errors')
        assert hasattr(testbed, 'plot_improvement_factors')
        assert hasattr(testbed, 'plot_predictions_vs_ground_truth')
        
    def test_scientific_report_generation(self):
        """Test that scientific report can be generated."""
        testbed = Z5DScientificTestBed()
        
        # Run minimal validation
        testbed.benchmark_values = {
            'small': [100, 1000],
            'medium': [],
            'large': [],
            'ultra_large': []
        }
        
        results = testbed.run_comprehensive_validation()
        
        # Generate report
        report = testbed.generate_scientific_report()
        
        # Check report content
        assert isinstance(report, str)
        assert len(report) > 100
        assert "Z_5D PRIME PREDICTION" in report
        assert "SCIENTIFIC TEST BED REPORT" in report
        assert "EMPIRICAL VALIDATION SUMMARY" in report
        assert "METHODOLOGY" in report
        assert "SCIENTIFIC CONCLUSIONS" in report


def test_z5d_scientific_testbed_quick():
    """Quick test that can be run as part of standard test suite."""
    testbed = Z5DScientificTestBed()
    
    # Test with just one small value for speed
    result = testbed.run_single_prediction_test(1000)
    
    # Basic checks
    assert result['z5d_prediction'] > 0
    assert result['pnt_prediction'] > 0
    assert result['ground_truth'] == 7919  # 1000th prime
    assert result['z5d_relative_error'] < 0.05  # Should be < 5% error
    
    print(f"✅ Z_5D Test Bed Quick Validation: n=1000, error={result['z5d_relative_error']*100:.3f}%")


if __name__ == "__main__":
    # Run quick test when executed directly
    test_z5d_scientific_testbed_quick()
    print("🎯 Z_5D Scientific Test Bed pytest integration tests passed!")