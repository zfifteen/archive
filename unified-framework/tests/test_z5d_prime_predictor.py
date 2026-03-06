"""
Tests for Z5D Prime Predictor module.

These tests validate the core functionality, accuracy, and performance
of the Z5D prime prediction framework.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from z5d import (
    predict_prime,
    predict_prime_fast,
    predict_nth_prime,
    benchmark_prediction,
    get_prediction_stats,
)


class TestBasicPrediction:
    """Test basic prime prediction functionality."""
    
    def test_predict_small_primes(self):
        """Test prediction of small primes."""
        # Allow for some error on small primes
        result = predict_prime(10)
        assert 25 <= result <= 35, f"Expected ~29, got {result}"
        
        result = predict_prime(100)
        assert 530 <= result <= 550, f"Expected ~541, got {result}"
    
    def test_predict_medium_primes(self):
        """Test prediction of medium-scale primes."""
        result = predict_prime(10**5)
        expected = 1299709
        error_ppm = abs(result - expected) / expected * 1e6
        assert error_ppm < 100, f"Error too large: {error_ppm} ppm"
    
    def test_predict_large_primes(self):
        """Test prediction of large primes."""
        result = predict_prime(10**6)
        expected = 15485863
        error_ppm = abs(result - expected) / expected * 1e6
        assert error_ppm < 200, f"Error too large: {error_ppm} ppm"
    
    def test_predict_returns_integer(self):
        """Ensure prediction returns integer type."""
        result = predict_prime(1000)
        assert isinstance(result, int), f"Expected int, got {type(result)}"
    
    def test_predict_positive(self):
        """Ensure predictions are positive."""
        for n in [10, 100, 1000, 10000]:
            result = predict_prime(n)
            assert result > 0, f"Expected positive result for n={n}"


class TestFastPrediction:
    """Test fast approximation mode."""
    
    def test_fast_mode_returns_integer(self):
        """Fast mode should return integer."""
        result = predict_prime_fast(1000)
        assert isinstance(result, int)
    
    def test_fast_mode_reasonable_accuracy(self):
        """Fast mode should be reasonably accurate."""
        result = predict_prime_fast(10**5)
        expected = 1299709
        # Fast mode has lower accuracy, allow 5% error
        error_pct = abs(result - expected) / expected * 100
        assert error_pct < 5, f"Fast mode error too large: {error_pct}%"


class TestBenchmarking:
    """Test benchmarking functionality."""
    
    def test_benchmark_returns_dict(self):
        """Benchmark should return dictionary with expected keys."""
        result = benchmark_prediction(1000, iterations=3)
        assert isinstance(result, dict)
        assert 'mean_ms' in result
        assert 'median_ms' in result
        assert 'min_ms' in result
        assert 'max_ms' in result
    
    def test_benchmark_positive_times(self):
        """Benchmark times should be positive."""
        result = benchmark_prediction(10000, iterations=3)
        assert result['mean_ms'] > 0
        assert result['median_ms'] > 0
        assert result['min_ms'] > 0
    
    def test_benchmark_reasonable_times(self):
        """Benchmark times should be reasonable (< 10ms)."""
        result = benchmark_prediction(10**6, iterations=3)
        assert result['median_ms'] < 10, f"Too slow: {result['median_ms']} ms"


class TestPredictionStats:
    """Test get_prediction_stats functionality."""
    
    def test_stats_returns_dict(self):
        """get_prediction_stats should return dictionary."""
        result = get_prediction_stats(1000)
        assert isinstance(result, dict)
    
    def test_stats_contains_basic_info(self):
        """Stats should contain n, predicted, and runtime."""
        result = get_prediction_stats(1000)
        assert 'n' in result
        assert 'predicted' in result
        assert 'runtime_ms' in result
        assert result['n'] == 1000
        assert isinstance(result['predicted'], int)
        assert result['runtime_ms'] > 0
    
    def test_stats_contains_accuracy_for_known(self):
        """Stats should include accuracy for known primes."""
        result = get_prediction_stats(10**5)
        assert 'actual' in result
        assert 'error_ppm' in result
        assert 'relative_error_pct' in result
        assert result['actual'] == 1299709


class TestAccuracy:
    """Test accuracy characteristics across scales."""
    
    def test_accuracy_medium_scale(self):
        """Test accuracy at medium scale (10^5)."""
        stats = get_prediction_stats(10**5)
        # Should be under 10 ppm
        assert stats['error_ppm'] < 10, f"Error: {stats['error_ppm']} ppm"
    
    def test_accuracy_large_scale(self):
        """Test accuracy at large scale (10^6)."""
        stats = get_prediction_stats(10**6)
        # Should be under 200 ppm
        assert stats['error_ppm'] < 200, f"Error: {stats['error_ppm']} ppm"
    
    def test_accuracy_very_large_scale(self):
        """Test accuracy at very large scale (10^7)."""
        stats = get_prediction_stats(10**7)
        # Should be under 50 ppm
        assert stats['error_ppm'] < 50, f"Error: {stats['error_ppm']} ppm"
    
    def test_error_decreases_with_scale(self):
        """Error should generally decrease as n increases."""
        errors = []
        for k in [6, 7, 8]:
            stats = get_prediction_stats(10**k)
            errors.append(stats['error_ppm'])
        
        # Most errors should decrease
        # (allow for some variation due to discrete effects)
        decreasing_count = sum(1 for i in range(len(errors)-1) 
                              if errors[i] >= errors[i+1])
        assert decreasing_count >= 1, "Error should generally decrease"


class TestKnownValues:
    """Test against known prime values."""
    
    KNOWN_PRIMES = {
        10**3: 7919,
        10**4: 104729,
        10**5: 1299709,
        10**6: 15485863,
        10**7: 179424673,
        10**8: 2038074743,
    }
    
    @pytest.mark.parametrize("n,expected", list(KNOWN_PRIMES.items()))
    def test_known_values(self, n, expected):
        """Test prediction against known exact values."""
        result = predict_prime(n)
        error_ppm = abs(result - expected) / expected * 1e6
        
        # Different tolerance for different scales
        if n <= 10**4:
            max_error = 1000  # Allow 0.1% error for small n
        elif n <= 10**6:
            max_error = 200   # Allow 200 ppm for medium n
        else:
            max_error = 50    # Allow 50 ppm for large n
        
        assert error_ppm < max_error, \
            f"n={n}: predicted={result}, expected={expected}, error={error_ppm:.2f} ppm"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_small_n(self):
        """Test with very small n values."""
        result = predict_prime(1)
        assert result > 0, "Should return positive value for n=1"
    
    def test_power_of_ten(self):
        """Test specifically with powers of 10."""
        for k in range(3, 8):
            result = predict_prime(10**k)
            assert result > 0
            assert isinstance(result, int)
    
    def test_large_scale_performance(self):
        """Test that large scales still perform well."""
        import time
        n = 10**15
        t0 = time.perf_counter()
        result = predict_prime(n)
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000
        
        assert elapsed_ms < 10, f"Too slow for n=10^15: {elapsed_ms} ms"
        assert result > 0


def test_module_imports():
    """Test that all expected functions are importable."""
    from z5d import predict_prime
    from z5d import predict_prime_fast
    from z5d import predict_nth_prime
    from z5d import benchmark_prediction
    from z5d import get_prediction_stats
    
    assert callable(predict_prime)
    assert callable(predict_prime_fast)
    assert callable(predict_nth_prime)
    assert callable(benchmark_prediction)
    assert callable(get_prediction_stats)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
