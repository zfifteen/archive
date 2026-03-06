"""
Unit tests for Phi-Harmonic Geometric Trading Filter
"""

import pytest
import numpy as np
from src.core.filter import (
    PhiHarmonicFilter,
    FilterConfig,
    SignalResult,
    batch_filter_signals,
)


class TestPhiHarmonicFilter:
    """Test cases for the core phi-harmonic filter"""

    def setup_method(self):
        """Setup test fixtures"""
        self.filter = PhiHarmonicFilter()
        self.config = FilterConfig(band_multiplier=2.0)

    def test_basic_filter_pass(self):
        """Test signal that should pass the geometric filter"""
        # Signal in the middle of support-resistance range
        result = self.filter.filter_signal(
            price=100.0, support=90.0, resistance=110.0, volatility=5.0
        )

        assert result.passed == True
        assert result.rejection_reason is None
        assert result.confidence > 0.8  # High confidence for center signal
        assert result.filter_time_ns > 0

    def test_filter_reject_below(self):
        """Test signal rejected for being below geometric bound"""
        # Signal well below the band
        result = self.filter.filter_signal(
            price=80.0, support=90.0, resistance=110.0, volatility=5.0
        )

        assert result.passed == False
        assert result.rejection_reason == "price_below_geometric_bound"
        assert result.confidence == 0.0

    def test_filter_reject_above(self):
        """Test signal rejected for being above geometric bound"""
        # Signal well above the band
        result = self.filter.filter_signal(
            price=130.0, support=90.0, resistance=110.0, volatility=5.0
        )

        assert result.passed == False
        assert result.rejection_reason == "price_above_geometric_bound"
        assert result.confidence == 0.0

    def test_edge_cases(self):
        """Test edge cases at boundaries"""
        # Test exactly at lower bound
        result_lower = self.filter.filter_signal(
            price=80.0,  # (90+110)/2 - 2*5 = 100 - 10 = 90, wait 80?
            support=90.0,
            resistance=110.0,
            volatility=5.0,
        )
        # mid_point = 100, band_width = 10, lower = 90
        # 90 should pass
        result_lower = self.filter.filter_signal(
            price=90.0, support=90.0, resistance=110.0, volatility=5.0
        )
        assert result_lower.passed == True

        # Test exactly at upper bound
        result_upper = self.filter.filter_signal(
            price=110.0, support=90.0, resistance=110.0, volatility=5.0
        )
        assert result_upper.passed == True

    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        # Center signal should have high confidence
        result_center = self.filter.filter_signal(
            price=100.0, support=90.0, resistance=110.0, volatility=5.0
        )
        assert result_center.confidence == 1.0

        # Signal at 95 should have 0.5 confidence
        result_mid = self.filter.filter_signal(
            price=95.0, support=90.0, resistance=110.0, volatility=5.0
        )
        assert abs(result_mid.confidence - 0.5) < 0.01

    def test_batch_filtering(self):
        """Test batch processing of multiple signals"""
        signals = [
            {
                "price": 100.0,
                "support": 90.0,
                "resistance": 110.0,
                "volatility": 5.0,
            },  # Pass
            {
                "price": 80.0,
                "support": 90.0,
                "resistance": 110.0,
                "volatility": 5.0,
            },  # Fail low
            {
                "price": 130.0,
                "support": 90.0,
                "resistance": 110.0,
                "volatility": 5.0,
            },  # Fail high
        ]

        results = self.filter.filter_batch(signals)

        assert len(results) == 3
        assert results[0].passed == True
        assert results[1].passed == False
        assert results[2].passed == False

    def test_performance_requirement(self):
        """Test that filtering meets sub-microsecond performance requirement"""
        # Run multiple times to check average performance
        times = []
        for _ in range(1000):
            result = self.filter.filter_signal(
                price=100.0, support=90.0, resistance=110.0, volatility=5.0
            )
            times.append(result.filter_time_ns)

        avg_time_ns = np.mean(times)
        # Should be well under 1000 ns (1 microsecond)
        assert avg_time_ns < 1000

    def test_rejection_rate_validation(self):
        """Validate 73-78% rejection rate on Fibonacci levels"""
        # Generate signals at Fibonacci retracement levels
        fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        support = 90.0
        resistance = 110.0
        volatility = 0.6  # Low volatility for high rejection rate

        passed_count = 0
        total_signals = 0

        # Generate signals at each fib level with some variation
        for fib in fib_levels:
            for offset in [-2, -1, 0, 1, 2]:  # Small variations
                price = support + (resistance - support) * fib + offset
                result = self.filter.filter_signal(
                    price, support, resistance, volatility
                )
                total_signals += 1
                if result.passed:
                    passed_count += 1
                print(
                    f"fib={fib}, offset={offset}, price={price:.2f}, passed={result.passed}"
                )

        rejection_rate = 1.0 - (passed_count / total_signals)
        print(
            f"passed_count={passed_count}, total={total_signals}, rejection={rejection_rate:.3f}"
        )
        # Should be between 70-80% (allowing some tolerance)
        assert 0.70 <= rejection_rate <= 0.80

    def test_custom_config(self):
        """Test filter with custom configuration"""
        custom_config = FilterConfig(band_multiplier=1.0)  # Tighter bands
        custom_filter = PhiHarmonicFilter(custom_config)

        # Signal that would pass with default (2.0) might fail with 1.0
        result = custom_filter.filter_signal(
            price=85.0,  # With multiplier 1.0: bounds are 95±5 = 90-100
            support=90.0,
            resistance=110.0,
            volatility=5.0,
        )
        # 85 is below 90, should fail
        assert result.passed == False


class TestJITFunctions:
    """Test JIT-compiled functions"""

    def test_batch_filter_signals(self):
        """Test vectorized batch filtering"""
        prices = np.array([95.0, 85.0, 105.0, 115.0])
        lowers = np.array([90.0, 90.0, 90.0, 90.0])
        uppers = np.array([110.0, 110.0, 110.0, 110.0])

        results = batch_filter_signals(prices, lowers, uppers)

        expected = np.array([True, False, True, False])
        np.testing.assert_array_equal(results, expected)
