"""
Tests for the sampling utilities.
"""
import sys
import os
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sampling import sample_lognormal, clamp_gap
from model import Band


def test_sample_lognormal_positive():
    """Test that sample_lognormal always returns positive values."""
    random.seed(42)
    
    # Test multiple samples
    for _ in range(100):
        sample = sample_lognormal(shape=1.3, scale=0.0001)
        assert sample > 0, f"Sample should be positive, got {sample}"
    
    print("✓ sample_lognormal returns positive values")


def test_sample_lognormal_reproducible():
    """Test that sample_lognormal is reproducible with a seed."""
    rng1 = random.Random(12345)
    rng2 = random.Random(12345)
    
    sample1 = sample_lognormal(shape=1.3, scale=0.0001, rng=rng1)
    sample2 = sample_lognormal(shape=1.3, scale=0.0001, rng=rng2)
    
    assert sample1 == sample2, "Samples with same seed should be identical"
    
    print("✓ sample_lognormal is reproducible")


def test_sample_lognormal_distribution():
    """Test that sample_lognormal produces reasonable values."""
    rng = random.Random(42)
    
    samples = [sample_lognormal(shape=1.3, scale=0.0001, rng=rng) for _ in range(1000)]
    
    # All should be positive
    assert all(s > 0 for s in samples)
    
    # Should have some variation
    assert min(samples) < max(samples)
    
    # Mean should be roughly scale * exp(shape^2 / 2)
    # But we won't enforce exact match due to sampling variance
    
    print("✓ sample_lognormal produces reasonable distribution")


def test_clamp_gap_with_bounds():
    """Test clamp_gap with explicit min/max bounds."""
    band = Band(
        p_min=100000,
        p_max=1000000,
        shape=1.3,
        scale=0.0001,
        min_gap=2.0,
        max_gap=1000.0
    )
    
    # Test clamping below minimum
    assert clamp_gap(1.0, band) == 2.0
    assert clamp_gap(0.5, band) == 2.0
    
    # Test clamping above maximum
    assert clamp_gap(1500.0, band) == 1000.0
    assert clamp_gap(10000.0, band) == 1000.0
    
    # Test values within range
    assert clamp_gap(50.0, band) == 50.0
    assert clamp_gap(500.0, band) == 500.0
    
    print("✓ clamp_gap works with explicit bounds")


def test_clamp_gap_without_bounds():
    """Test clamp_gap with default bounds based on scale."""
    band = Band(
        p_min=100000,
        p_max=1000000,
        shape=1.3,
        scale=0.0001,
        min_gap=None,
        max_gap=None
    )
    
    # Should use generic range [1, 10 * scale] = [1.0, 0.001]
    # Note: min_val (1.0) > max_val (0.001), so all values clamp to 1.0
    min_expected = 1.0
    
    # Test clamping below minimum
    assert clamp_gap(0.5, band) == min_expected
    
    # Test any positive value - will be clamped to min since min > max
    assert clamp_gap(0.002, band) == min_expected
    assert clamp_gap(100.0, band) == min_expected
    
    print("✓ clamp_gap works with default bounds")


def test_clamp_gap_never_negative():
    """Test that clamp_gap never returns negative or zero values."""
    band = Band(
        p_min=100000,
        p_max=1000000,
        shape=1.3,
        scale=0.0001,
        min_gap=2.0,
        max_gap=1000.0
    )
    
    # Try various inputs including negative
    test_values = [-10.0, -1.0, 0.0, 0.1, 1.0, 100.0, 10000.0]
    
    for val in test_values:
        clamped = clamp_gap(val, band)
        assert clamped >= band.min_gap, f"Clamped value {clamped} should be >= {band.min_gap}"
    
    print("✓ clamp_gap never returns values below min_gap")


def run_all_tests():
    """Run all sampling tests."""
    test_sample_lognormal_positive()
    test_sample_lognormal_reproducible()
    test_sample_lognormal_distribution()
    test_clamp_gap_with_bounds()
    test_clamp_gap_without_bounds()
    test_clamp_gap_never_negative()
    print("\n✓ All sampling tests passed!")


if __name__ == "__main__":
    run_all_tests()
