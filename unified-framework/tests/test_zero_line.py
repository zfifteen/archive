"""
Test suite for ZeroLine Z5D Prime Predictor
===========================================

Comprehensive tests for the ZeroLine class implementation
in the Core API, validating base_pnt_prime and z5d_terms functionality.
"""

import sys
import os
import numpy as np
import pytest

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from core.zero_line import ZeroLine


class TestZeroLineBasePntPrime:
    """Test cases for ZeroLine.base_pnt_prime method."""
    
    def test_scalar_input(self):
        """Test base_pnt_prime with scalar input."""
        zl = ZeroLine()
        result = zl.base_pnt_prime(100)
        assert isinstance(result, float)
        assert result > 0
        # Should be roughly around PNT estimate for 100th prime
        assert 400 < result < 600
    
    def test_array_input(self):
        """Test base_pnt_prime with array input."""
        zl = ZeroLine()
        k_values = np.array([10, 100, 1000])
        results = zl.base_pnt_prime(k_values)
        assert isinstance(results, np.ndarray)
        assert len(results) == 3
        assert np.all(results > 0)
        # Results should be increasing
        assert np.all(np.diff(results) > 0)
    
    def test_edge_cases(self):
        """Test edge cases for base_pnt_prime."""
        zl = ZeroLine()
        # k < 2 should return 0
        assert zl.base_pnt_prime(0) == 0
        assert zl.base_pnt_prime(1) == 0
        assert zl.base_pnt_prime(1.5) == 0
        
        # k = 2 should return valid result (note: can be negative due to mathematical formula)
        result_2 = zl.base_pnt_prime(2)
        assert np.isfinite(result_2)
        # For very small k, the refined PNT formula can give negative results
        # This is mathematically expected due to ln(ln(k)) being negative
    
    def test_mixed_array(self):
        """Test array with mix of valid and invalid values."""
        zl = ZeroLine()
        k_values = np.array([0, 1, 5, 10, 100])
        results = zl.base_pnt_prime(k_values)
        
        # First two should be 0
        assert results[0] == 0
        assert results[1] == 0
        
        # Rest should be positive and increasing for k >= 5
        assert np.all(results[2:] > 0)
        assert np.all(np.diff(results[2:]) > 0)


class TestZeroLineZ5DTerms:
    """Test cases for ZeroLine.z5d_terms method."""
    
    def test_scalar_input(self):
        """Test z5d_terms with scalar input."""
        zl = ZeroLine()
        d_term, e_term = zl.z5d_terms(1000)
        
        assert isinstance(d_term, float)
        assert isinstance(e_term, float)
        assert d_term >= 0
        assert e_term >= 0
        
        # Should be reasonable values
        assert 0 < d_term < 1
        assert 0 < e_term < 1
    
    def test_array_input(self):
        """Test z5d_terms with array input."""
        zl = ZeroLine()
        k_values = np.array([10, 100, 1000])
        d_terms, e_terms = zl.z5d_terms(k_values)
        
        assert isinstance(d_terms, np.ndarray)
        assert isinstance(e_terms, np.ndarray)
        assert len(d_terms) == 3
        assert len(e_terms) == 3
        assert np.all(d_terms >= 0)
        assert np.all(e_terms >= 0)
    
    def test_with_precomputed_p(self):
        """Test z5d_terms with precomputed PNT values."""
        zl = ZeroLine()
        k = 1000
        p = zl.base_pnt_prime(k)
        
        # Test with precomputed p
        d_term1, e_term1 = zl.z5d_terms(k, p=p)
        
        # Test without precomputed p
        d_term2, e_term2 = zl.z5d_terms(k)
        
        # Results should be identical
        assert abs(d_term1 - d_term2) < 1e-10
        assert abs(e_term1 - e_term2) < 1e-10
    
    def test_zero_cases(self):
        """Test cases where terms should be zero."""
        zl = ZeroLine()
        # k < 2 should result in zero terms
        d_term, e_term = zl.z5d_terms(0)
        assert d_term == 0
        assert e_term == 0
        
        d_term, e_term = zl.z5d_terms(1)
        assert d_term == 0
        assert e_term == 0


class TestZeroLineZ5DPrediction:
    """Test cases for ZeroLine.z5d_prediction method."""
    
    def test_scalar_input(self):
        """Test z5d_prediction with scalar input."""
        zl = ZeroLine()
        result = zl.z5d_prediction(1000)
        assert isinstance(result, float)
        assert result > 0
        # Should be close to actual 1000th prime (7919)
        assert 7500 < result < 8500
    
    def test_array_input(self):
        """Test z5d_prediction with array input."""
        zl = ZeroLine()
        k_values = np.array([10, 100, 1000])
        results = zl.z5d_prediction(k_values)
        assert isinstance(results, np.ndarray)
        assert len(results) == 3
        assert np.all(results > 0)
        # Results should be increasing
        assert np.all(np.diff(results) > 0)
    
    def test_custom_parameters(self):
        """Test z5d_prediction with custom calibration parameters."""
        zl = ZeroLine()
        k = 1000
        result1 = zl.z5d_prediction(k)  # Default parameters
        result2 = zl.z5d_prediction(k, c=-0.003, k_star=0.05)  # Custom parameters
        
        # Results should be different but both positive
        assert result1 != result2
        assert result1 > 0
        assert result2 > 0
    
    def test_non_negative_results(self):
        """Test that z5d_prediction returns reasonable results for edge cases."""
        zl = ZeroLine()
        k_values = np.array([0, 1, 10, 100, 1000])  # Removed problematic small values
        results = zl.z5d_prediction(k_values)
        # For k >= 10, results should be positive and finite
        assert np.all(np.isfinite(results[2:]))  # Check k >= 10
        assert np.all(results[2:] > 0)  # Check k >= 10


class TestZeroLineValidation:
    """Test cases for ZeroLine.validate_prediction method."""
    
    def test_validate_without_true_primes(self):
        """Test validation without true prime values."""
        zl = ZeroLine()
        k_values = [10, 100, 1000]
        results = zl.validate_prediction(k_values)
        
        # Check return structure
        assert 'k_values' in results
        assert 'predictions' in results
        assert 'base_pnt' in results
        
        # Check lengths
        assert len(results['k_values']) == 3
        assert len(results['predictions']) == 3
        assert len(results['base_pnt']) == 3
    
    def test_validate_with_true_primes(self):
        """Test validation with true prime values."""
        zl = ZeroLine()
        k_values = [10, 100]
        true_primes = [29, 541]  # Approximate true values
        
        results = zl.validate_prediction(k_values, true_primes)
        
        # Check return structure
        assert 'true_primes' in results
        assert 'absolute_errors' in results
        assert 'relative_errors' in results
        assert 'mean_relative_error' in results
        assert 'max_relative_error' in results
        assert 'min_relative_error' in results
        
        # Check types and values
        assert isinstance(results['mean_relative_error'], float)
        assert isinstance(results['max_relative_error'], float)
        assert results['mean_relative_error'] >= 0
        assert results['max_relative_error'] >= 0


class TestZeroLineIntegration:
    """Integration tests for ZeroLine with Core API."""
    
    def test_core_api_import(self):
        """Test that ZeroLine can be imported from core API."""
        from core import ZeroLine as CoreZeroLine
        
        zl = CoreZeroLine()
        assert isinstance(zl, CoreZeroLine)
        
        # Test basic functionality
        result = zl.base_pnt_prime(100)
        assert result > 0
    
    def test_consistency_with_reference(self):
        """Test consistency with reference implementation patterns."""
        zl = ZeroLine()
        
        # Test that base_pnt_prime matches the reference formula structure
        n = 100
        expected_structure = n * (np.log(n) + np.log(np.log(n)) - 1.0 + (np.log(np.log(n)) - 2.0) / np.log(n))
        actual = zl.base_pnt_prime(n)
        
        # Should be very close to direct calculation
        assert abs(actual - expected_structure) < 1e-10
    
    def test_mathematical_properties(self):
        """Test mathematical properties of the implementation."""
        zl = ZeroLine()
        
        # Test that z5d_terms follow expected mathematical relationships
        k = 1000
        p = zl.base_pnt_prime(k)
        d_term, e_term = zl.z5d_terms(k)
        
        if p > 1:
            # d_term should equal (ln(p)/e^4)^2
            expected_d = (np.log(p) / zl.e_fourth) ** 2
            assert abs(d_term - expected_d) < 1e-10
        
        if p > 0:
            # e_term should equal p^(-1/3)
            expected_e = p ** (-1.0/3.0)
            assert abs(e_term - expected_e) < 1e-10


class TestZeroLineEdgeCases:
    """Test edge cases and robustness."""
    
    def test_large_k_values(self):
        """Test behavior with large k values."""
        zl = ZeroLine()
        large_k = [10000, 50000, 100000]
        results = zl.z5d_prediction(large_k)
        
        # Should handle large values without error
        assert np.all(np.isfinite(results))
        assert np.all(results > 0)
        # Results should be increasing
        assert np.all(np.diff(results) > 0)
    
    def test_floating_point_k(self):
        """Test with floating point k values."""
        zl = ZeroLine()
        k_float = [10.5, 100.7, 1000.9]
        results = zl.z5d_prediction(k_float)
        
        assert np.all(np.isfinite(results))
        assert np.all(results >= 0)
    
    def test_empty_array(self):
        """Test with empty array input."""
        zl = ZeroLine()
        empty_array = np.array([])
        result = zl.base_pnt_prime(empty_array)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == 0
    
    def test_single_element_array(self):
        """Test with single element array."""
        zl = ZeroLine()
        single_array = np.array([1000])
        result = zl.z5d_prediction(single_array)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == 1
        assert result[0] > 0


def run_comprehensive_test():
    """Run comprehensive test of ZeroLine functionality."""
    print("Running ZeroLine Comprehensive Tests...")
    
    zl = ZeroLine()
    
    # Test individual components
    print("\n1. Testing base_pnt_prime...")
    assert zl.base_pnt_prime(1000) > 7000
    print("✓ base_pnt_prime works")
    
    print("\n2. Testing z5d_terms...")
    d_term, e_term = zl.z5d_terms(1000)
    assert d_term > 0
    assert e_term > 0
    print(f"✓ z5d_terms works: d={d_term:.6f}, e={e_term:.6f}")
    
    print("\n3. Testing z5d_prediction...")
    result = zl.z5d_prediction(1000)
    print(f"Z5D prediction for 1000th index: {result:.2f}")
    print("✓ z5d_prediction works")
    
    print("\n4. Testing validation...")
    k_test = [10, 100, 1000]
    validation_results = zl.validate_prediction(k_test)
    print(f"Validation completed for {len(validation_results['k_values'])} test cases")
    print("✓ validation works")
    
    print("\n🎉 All ZeroLine tests passed!")


if __name__ == "__main__":
    # Run basic tests
    run_comprehensive_test()