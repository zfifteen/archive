"""
Validation Tests

Tests implementation correctness against OEIS and PNT predictions.
"""

import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from prime_generator import generate_primes


def test_gap_calculation():
    """Verify gaps computed correctly."""
    primes = np.array([2, 3, 5, 7, 11, 13])
    gaps = np.diff(primes)
    expected = np.array([1, 2, 2, 4, 2])
    assert np.array_equal(gaps, expected), f"Gap calculation failed: {gaps}"
    print("✓ test_gap_calculation passed")


def test_log_gap_magnitude():
    """Verify log(gap) not log(p[n+1]/p[n])."""
    primes = np.array([997, 1009])  # gap = 12
    gap = primes[1] - primes[0]
    log_gap = np.log(gap)
    
    assert abs(log_gap - 2.485) < 0.001, f"log(gap) should be ~2.485, got {log_gap}"
    assert log_gap > 2.0, f"log(gap) should be ~2.5, not ~0.01"
    print("✓ test_log_gap_magnitude passed")


def test_oeis_maxgaps_1e6():
    """Validate against maximal gaps at 10^6."""
    print("\nGenerating primes up to 10^6...")
    primes = generate_primes(10**6)
    gaps = np.diff(primes)
    max_gap = int(np.max(gaps))
    max_gap_prime = int(primes[np.argmax(gaps)])
    
    # Actual maximal gap at 10^6 scale
    assert max_gap == 114, f"Max gap at 10^6 should be 114, got {max_gap}"
    assert max_gap_prime == 492113, f"Prime before max gap should be 492113, got {max_gap_prime}"
    print(f"✓ test_oeis_maxgaps_1e6 passed: max_gap={max_gap}, prime={max_gap_prime}")


def test_array_alignment():
    """Verify array lengths consistent."""
    primes = generate_primes(10**5)
    gaps = np.diff(primes)
    log_primes = np.log(primes[:-1])
    normalized = gaps / log_primes
    
    assert len(gaps) == len(primes) - 1, "Gap array length mismatch"
    assert len(log_primes) == len(gaps), "log_primes array length mismatch"
    assert len(normalized) == len(gaps), "normalized array length mismatch"
    print("✓ test_array_alignment passed")


def test_pnt_normalization():
    """Verify mean(gap/log(p)) ≈ 1."""
    primes = generate_primes(10**6)
    gaps = np.diff(primes)
    log_primes = np.log(primes[:-1])
    normalized = gaps / log_primes
    
    mean_normalized = np.mean(normalized)
    assert 0.9 < mean_normalized < 1.1, \
        f"mean(gap/log(p)) should be ~1.0, got {mean_normalized}"
    print(f"✓ test_pnt_normalization passed: mean={mean_normalized:.4f}")


def test_prime_counts():
    """Verify prime counts at known values."""
    test_values = [
        (10**6, 78498),
        (10**7, 664579),
    ]
    
    for limit, expected_count in test_values:
        print(f"\nTesting π({limit:,}) = {expected_count:,}...")
        primes = generate_primes(limit)
        actual_count = len(primes)
        assert actual_count == expected_count, \
            f"Prime count at {limit:,}: expected {expected_count:,}, got {actual_count:,}"
        print(f"✓ π({limit:,}) = {actual_count:,}")


def test_gap_properties():
    """Verify basic gap properties."""
    primes = generate_primes(10**5)
    gaps = np.diff(primes)
    
    # All gaps positive
    assert np.all(gaps > 0), "Found non-positive gaps"
    
    # First gap is 1 (2→3)
    assert gaps[0] == 1, f"First gap should be 1, got {gaps[0]}"
    
    # All other gaps should be even
    assert np.all(gaps[1:] % 2 == 0), "Found odd gaps after first"
    
    # Mode gap should be small (typically 2, 4, or 6)
    from scipy import stats as sp_stats
    mode_gap = sp_stats.mode(gaps, keepdims=True).mode[0]
    assert mode_gap in [2, 4, 6], f"Mode gap should be 2, 4, or 6, got {mode_gap}"
    
    print(f"✓ test_gap_properties passed (mode={mode_gap})")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Validation Tests")
    print("=" * 60)
    
    # Basic tests
    test_gap_calculation()
    test_log_gap_magnitude()
    test_array_alignment()
    
    # Property tests
    test_gap_properties()
    
    # Prime generation tests
    test_prime_counts()
    
    # OEIS validation
    test_oeis_maxgaps_1e6()
    
    # PNT validation
    test_pnt_normalization()
    
    print("\n" + "=" * 60)
    print("All validation tests passed! ✓")
    print("=" * 60)
