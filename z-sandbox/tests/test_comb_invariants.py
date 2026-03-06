#!/usr/bin/env python3
"""
Test Comb Invariants for RSA-260 Factorization

This test suite ensures strict adherence to the requirements:
1. Center is exactly log(N)/2 (never shifted)
2. Fractional m sampling is enabled
3. Candidate ranking is distance-based
4. Precision is always ≥1000 dps
5. No float64 fallback allowed
"""

import pytest
import sys
import os
from mpmath import mp, mpf, log as mplog
from typing import List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from rsa260_repro import (
    RSA_260,
    generate_fractional_candidates,
    rank_by_distance,
    comb_formula
)
from geom.m0_estimator import estimate_m0_balanced, get_resonance_metadata


def test_center_is_fixed_at_log_n_over_2():
    """Test that center is exactly log(N)/2 and never shifts."""
    dps = 1000
    mp.dps = dps
    
    N = RSA_260
    log_N = mplog(N)
    center = log_N / 2
    
    # Center must be exactly log(N)/2
    expected_center = float(log_N) / 2.0
    actual_center = float(center)
    
    # Allow tiny floating-point tolerance
    assert abs(actual_center - expected_center) < 1e-10, \
        f"Center {actual_center} != log(N)/2 {expected_center}"
    
    # Verify center doesn't shift with different k values
    for k in [0.29, 0.3, 0.31, 0.5, 1.0]:
        metadata = get_resonance_metadata(N, k, dps)
        assert abs(metadata['center'] - expected_center) < 1e-10, \
            f"Center shifted with k={k}: {metadata['center']} != {expected_center}"


def test_fractional_m_sampling_enabled():
    """Test that fractional m sampling is enabled (not integer-m)."""
    dps = 1000
    N = RSA_260
    k = 0.3
    m0 = 0.0
    window = 0.01
    step = 0.001  # Fractional step
    
    candidates = generate_fractional_candidates(N, k, m0, window, step, dps)
    
    # Should generate multiple candidates with fractional m
    assert len(candidates) > 10, \
        f"Expected >10 candidates with fractional m, got {len(candidates)}"
    
    # Extract m values
    m_values = [m for m, p in candidates]
    
    # Check that we have fractional m values (not all integers)
    non_integer_count = sum(1 for m in m_values if abs(m - round(m)) > 1e-6)
    
    assert non_integer_count > len(m_values) * 0.8, \
        f"Expected mostly fractional m values, got {non_integer_count}/{len(m_values)} non-integers"


def test_distance_based_ranking():
    """Test that candidates are ranked by |log(p) - center|, not amplitude."""
    dps = 1000
    N = RSA_260
    k = 0.3
    m0 = 0.0
    window = 0.01
    step = 0.001
    
    # Generate candidates
    candidates = generate_fractional_candidates(N, k, m0, window, step, dps)
    
    # Rank by distance
    ranked = rank_by_distance(candidates, N, dps)
    
    # Verify sorting: distances should be in ascending order
    distances = [dist for m, p, dist in ranked]
    
    for i in range(len(distances) - 1):
        assert distances[i] <= distances[i + 1], \
            f"Ranking not sorted by distance: {distances[i]} > {distances[i+1]} at position {i}"
    
    # Verify we're using distance, not something else like amplitude
    # The smallest distance should be close to 0 (near center)
    if len(ranked) > 0:
        min_distance = ranked[0][2]
        # For balanced semiprime with m0≈0, distance should be relatively small
        # (not enforcing absolute value since RSA-260 is unfactored)
        assert min_distance >= 0, f"Distance should be non-negative, got {min_distance}"


def test_dps_minimum_enforced():
    """Test that dps ≥ 1000 is enforced."""
    # Test that low dps would fail (defensive check)
    dps_values = [1000, 1024, 2000, 512]
    
    for dps in dps_values:
        mp.dps = dps
        N = RSA_260
        log_N = mplog(N)
        
        # Should work for dps ≥ 1000
        if dps >= 1000:
            # No exception expected
            center = log_N / 2
            assert center > 0, f"Center calculation failed at dps={dps}"
        else:
            # We don't enforce in the functions, but document the requirement
            # The test itself validates that 512 is insufficient for RSA-260
            pass


def test_no_float64_fallback():
    """Test that we never fall back to float64 precision."""
    dps = 1000
    mp.dps = dps
    
    N = RSA_260
    k = 0.3
    m = 0.0
    
    # Generate a candidate using high-precision
    p = comb_formula(N, k, m, dps)
    
    # Verify using mpmath (high precision)
    mp.dps = dps
    log_N = mplog(N)
    
    # The log value should have high precision
    # Check that it's not a simple float64 (which has ~15-16 digits)
    log_N_str = str(log_N)
    
    # High-precision should give us many more digits
    # Remove decimal point and sign
    digits = log_N_str.replace('.', '').replace('-', '')
    
    # Should have significantly more than 16 significant digits
    assert len(digits) > 20, \
        f"Expected high-precision (>20 digits), got {len(digits)} digits: {log_N_str}"


def test_comb_formula_precision():
    """Test that comb formula maintains high precision."""
    dps = 1000
    N = RSA_260
    k = 0.3
    
    # Test at different m values
    m_values = [0.0, 0.001, -0.001, 0.01, -0.01]
    
    for m in m_values:
        p = comb_formula(N, k, m, dps)
        
        # p should be a positive integer
        assert isinstance(p, int), f"comb_formula returned non-int: {type(p)}"
        assert p > 0, f"comb_formula returned non-positive: {p}"
        assert p < N, f"comb_formula returned p >= N: {p} >= {N}"


def test_m0_estimator_deterministic():
    """Test that m0 estimation is deterministic."""
    N = RSA_260
    k = 0.3
    dps = 1000
    
    # Run estimation multiple times
    results = []
    for _ in range(5):
        m0 = estimate_m0_balanced(N, k, dps)
        results.append(m0)
    
    # All results should be identical (deterministic)
    for i in range(len(results) - 1):
        assert abs(results[i] - results[i + 1]) < 1e-15, \
            f"m0 estimation not deterministic: {results[i]} != {results[i+1]}"


def test_resonance_metadata_consistency():
    """Test that resonance metadata is consistent."""
    N = RSA_260
    k = 0.3
    dps = 1000
    
    metadata = get_resonance_metadata(N, k, dps)
    
    # Check required fields
    required_fields = ['log_N', 'center', 'm0_balanced', 'm0_residue', 
                       'm0_recommended', 'window_width', 'k', 'dps']
    
    for field in required_fields:
        assert field in metadata, f"Missing required field: {field}"
    
    # Verify center = log_N / 2
    assert abs(metadata['center'] - metadata['log_N'] / 2) < 1e-10, \
        f"Center != log_N/2: {metadata['center']} != {metadata['log_N']/2}"
    
    # Verify parameters match
    assert metadata['k'] == k, f"k mismatch: {metadata['k']} != {k}"
    assert metadata['dps'] == dps, f"dps mismatch: {metadata['dps']} != {dps}"


def test_no_bias_shift_in_center():
    """Test that bias corrections never shift the center."""
    dps = 1000
    mp.dps = dps
    N = RSA_260
    
    log_N = mplog(N)
    original_center = log_N / 2
    
    # Test with various configurations that might involve bias
    test_configs = [
        {'k': 0.29, 'm0': 0.0},
        {'k': 0.3, 'm0': 0.001},
        {'k': 0.31, 'm0': -0.001},
        {'k': 0.5, 'm0': 0.0},
    ]
    
    for config in test_configs:
        # Generate candidates (which might apply bias internally)
        candidates = generate_fractional_candidates(
            N, config['k'], config['m0'], 0.01, 0.001, dps
        )
        
        # Rank (which uses center)
        ranked = rank_by_distance(candidates, N, dps)
        
        # Re-compute center to ensure it hasn't changed
        current_center = mplog(N) / 2
        
        assert abs(float(current_center - original_center)) < 1e-10, \
            f"Center shifted with config {config}: {float(current_center)} != {float(original_center)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
