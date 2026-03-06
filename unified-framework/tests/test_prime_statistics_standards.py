"""
Tests for Prime Statistics Standards (Issue #696)

Validates the implementation of k ≥ 10^5 requirements for robust statistical testing.
"""

import pytest
import warnings
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.params import (
    validate_k_statistical,
    validate_k_nth, 
    K_MIN_STATISTICAL_THRESHOLD,
    K_OPTIMAL_STATISTICAL_RANGE,
    STATISTICAL_TESTING_CONTEXTS
)


class TestPrimeStatisticsStandards:
    """Test suite for Prime Statistics Standards implementation."""
    
    def test_statistical_threshold_constant(self):
        """Test that the statistical threshold is set correctly."""
        assert K_MIN_STATISTICAL_THRESHOLD == 100000
        
    def test_optimal_range_constants(self):
        """Test that the optimal range is set correctly."""
        assert K_OPTIMAL_STATISTICAL_RANGE == [100000, 1000000]
        
    def test_statistical_contexts_defined(self):
        """Test that statistical testing contexts are properly defined."""
        expected_contexts = [
            "density_enhancement", "geodesic_clustering", "prime_gap_analysis",
            "z5d_validation", "bootstrap_confidence", "correlation_analysis"
        ]
        assert STATISTICAL_TESTING_CONTEXTS == expected_contexts
    
    def test_validate_k_statistical_valid_values(self):
        """Test validation passes for valid k values."""
        # Test exact threshold
        result = validate_k_statistical(100000, "density_enhancement")
        assert result == 100000
        
        # Test values in optimal range
        result = validate_k_statistical(500000, "z5d_validation")
        assert result == 500000
        
        result = validate_k_statistical(1000000, "bootstrap_confidence")
        assert result == 1000000
    
    def test_validate_k_statistical_warns_for_small_k(self):
        """Test that validation warns for k < 10^5."""
        with pytest.warns(UserWarning, match="Statistical Warning.*violates Prime Statistics Standards"):
            result = validate_k_statistical(1000, "density_enhancement")
            assert result == 1000  # Should still return the value
    
    def test_validate_k_statistical_warns_for_large_k(self):
        """Test that validation warns for k > optimal range."""
        with pytest.warns(UserWarning, match="exceeds optimal statistical range"):
            result = validate_k_statistical(10000000, "geodesic_clustering")
            assert result == 10000000  # Should still return the value
    
    def test_validate_k_statistical_strict_mode(self):
        """Test that strict mode raises errors for invalid k."""
        with pytest.raises(ValueError, match="violates Prime Statistics Standards"):
            validate_k_statistical(1000, "density_enhancement", strict=True)
    
    def test_validate_k_nth_with_statistical_context(self):
        """Test that k_nth validation applies statistical standards for statistical contexts."""
        # Should warn for statistical contexts with small k
        with pytest.warns(UserWarning, match="Statistical Warning"):
            result = validate_k_nth(1000, "density_enhancement")
            assert result == 1000
            
        # Should not warn for non-statistical contexts with small k
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = validate_k_nth(1000, "nth_prime")
            assert result == 1000
            # Filter out only statistical warnings  
            stat_warnings = [warning for warning in w if "Statistical Warning" in str(warning.message)]
            assert len(stat_warnings) == 0
    
    def test_validate_k_nth_non_statistical_context(self):
        """Test that non-statistical contexts don't trigger statistical validation."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = validate_k_nth(1000, "general_computation")
            assert result == 1000
            # Should not have statistical warnings for non-statistical context
            stat_warnings = [warning for warning in w if "Statistical Warning" in str(warning.message)]
            assert len(stat_warnings) == 0
    
    def test_all_statistical_contexts_trigger_validation(self):
        """Test that all defined statistical contexts trigger validation."""
        for context in STATISTICAL_TESTING_CONTEXTS:
            with pytest.warns(UserWarning, match="Statistical Warning"):
                validate_k_nth(1000, context)
    
    def test_warning_message_content(self):
        """Test that warning messages contain proper guidance."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_k_statistical(500, "density_enhancement")
            
            assert len(w) == 1
            warning_message = str(w[0].message)
            
            # Check that warning contains key information
            assert "low prime density" in warning_message
            assert "boundary effects" in warning_message
            assert "insufficient statistical power" in warning_message
            assert "100000" in warning_message
            assert "density_enhancement" in warning_message
    
    def test_context_parameter_usage(self):
        """Test that context parameter is properly used in messages."""
        test_context = "custom_analysis"
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_k_statistical(1000, test_context)
            
            warning_message = str(w[0].message)
            assert test_context in warning_message


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])