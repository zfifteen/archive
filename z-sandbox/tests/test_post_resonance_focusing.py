#!/usr/bin/env python3
"""
Unit tests for post-resonance focusing transform.

These tests verify that the focusing transform executes correctly and
produces deterministic results, even though it may not achieve significant
distance reduction at RSA-2048 scale.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from python.post_resonance_focusing import (
    focus_seed,
    focus_seed_with_metrics,
    FocusingMetadata,
    FOCUSING_CONFIG,
    analyze_dual_k_phase_residual,
    dirichlet_peak_centering,
    apply_balance_bias,
    iterative_phase_alignment,
    extract_delta_centers,
    bounded_refinement_single_center,
    multi_delta_focusing,
    DeltaCenter,
    MultiDeltaFocusingResult
)


def test_focusing_config_exists():
    """Test that focusing configuration is properly defined"""
    assert 'dual_k_epsilon' in FOCUSING_CONFIG
    assert 'dirichlet_J' in FOCUSING_CONFIG
    assert 'kappa_descent_steps' in FOCUSING_CONFIG
    assert 'phase_alignment_iterations' in FOCUSING_CONFIG
    
    # Check multi-Δ center parameters
    assert 'max_delta_centers' in FOCUSING_CONFIG
    assert 'refinement_radius' in FOCUSING_CONFIG
    
    # Check values are reasonable
    assert 0 < FOCUSING_CONFIG['dual_k_epsilon'] < 0.1
    assert FOCUSING_CONFIG['dirichlet_J'] > 0
    assert FOCUSING_CONFIG['kappa_descent_steps'] > 0
    assert FOCUSING_CONFIG['max_delta_centers'] > 0
    assert FOCUSING_CONFIG['refinement_radius'] > 0


def test_focus_seed_deterministic():
    """Test that focus_seed produces deterministic results"""
    # Small test case
    N = 143  # 11 × 13
    seed = 12  # Close to √143 ≈ 11.96
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=0.95,
        phase=0.1,
        kappa_weight=0.15,
        m_value=0,
        score=0.14
    )
    
    # Run focusing twice
    result1 = focus_seed(seed, N, metadata)
    result2 = focus_seed(seed, N, metadata)
    
    # Should be deterministic
    assert result1 == result2
    
    # Should be a valid candidate
    assert result1 > 0
    assert result1 < N


def test_focus_seed_with_metrics_small():
    """Test focusing with metrics on a small semiprime"""
    N = 899  # 29 × 31
    seed = 30  # At √899 ≈ 29.98
    true_factor = 29
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=0.98,
        phase=0.05,
        kappa_weight=0.16,
        m_value=0,
        score=0.15
    )
    
    result = focus_seed_with_metrics(seed, N, metadata, true_factor=true_factor)
    
    # Check result structure
    assert result.p_hat > 0
    assert result.focus_time_ms >= 0
    assert result.abs_distance_before >= 0
    assert result.abs_distance_after >= 0
    assert result.shrink_ratio >= 0


def test_analyze_dual_k_phase_residual():
    """Test dual-k phase residual analysis"""
    N = 899
    p = 30
    k = 0.3
    
    analysis = analyze_dual_k_phase_residual(N, p, k, epsilon=0.005)
    
    # Check that analysis contains expected keys
    assert 'phase1' in analysis
    assert 'phase2' in analysis
    assert 'phase_residual' in analysis
    assert 'amp1' in analysis
    assert 'amp2' in analysis
    assert 'amp_ratio' in analysis
    
    # Check values are reasonable
    assert isinstance(analysis['phase1'], float)
    assert isinstance(analysis['amp1'], float)
    assert 0 <= analysis['amp1'] <= 1
    assert 0 <= analysis['amp2'] <= 1


def test_dirichlet_peak_centering():
    """Test Dirichlet kernel peak centering"""
    N = 899
    p = 30
    k = 0.3
    
    peak_info = dirichlet_peak_centering(N, p, k, J=8)
    
    # Check structure
    assert 'peak_offset' in peak_info
    assert 'weighted_amps' in peak_info
    
    # Peak offset should be small (sub-integer)
    assert abs(peak_info['peak_offset']) < 100
    
    # Should have 3 weighted amplitudes (p-1, p, p+1)
    assert len(peak_info['weighted_amps']) == 3


def test_apply_balance_bias():
    """Test balance bias application"""
    N = 899
    p = 25  # Below √N
    
    # Apply strong bias toward √N
    p_adjusted = apply_balance_bias(N, p, weight=0.8)
    
    # Should move toward √N ≈ 30
    assert p_adjusted > p
    assert p_adjusted <= 30


def test_iterative_phase_alignment():
    """Test iterative phase alignment"""
    N = 899
    p = 28
    k = 0.3
    
    p_aligned = iterative_phase_alignment(N, p, k, iterations=5, damping=0.5)
    
    # Should return a valid value
    assert p_aligned > 0
    assert p_aligned < N


def test_focus_seed_valid_range():
    """Test that focused seeds stay in valid range"""
    N = 10403  # 101 × 103
    k = 0.3
    
    # Test various starting seeds
    seeds = [50, 100, 102, 150]
    
    for seed in seeds:
        metadata = FocusingMetadata(
            k_primary=k,
            amplitude=0.95,
            phase=0.0,
            kappa_weight=0.14,
            m_value=0,
            score=0.13
        )
        
        p_hat = focus_seed(seed, N, metadata)
        
        # Must be in valid range
        assert p_hat >= 2
        assert p_hat < N


def test_focusing_respects_config():
    """Test that custom config is respected"""
    N = 899
    seed = 30
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=0.98,
        phase=0.05,
        kappa_weight=0.16,
        m_value=0,
        score=0.15
    )
    
    # Custom config with different parameters
    custom_config = FOCUSING_CONFIG.copy()
    custom_config['phase_alignment_iterations'] = 10
    
    # Should not raise errors
    result = focus_seed(seed, N, metadata, config=custom_config)
    assert result > 0


@pytest.mark.slow
def test_focus_seed_large_scale():
    """Test focusing on a larger semiprime (slow test)"""
    # 128-bit semiprime
    N = 270164157901532283278324889598637815083  # ≈ 2^128
    seed = 16437980447078730072630448311121927  # ≈ √N
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=1.0,
        phase=0.0,
        kappa_weight=0.13,
        m_value=0,
        score=0.13
    )
    
    import time
    start = time.perf_counter()
    result = focus_seed(seed, N, metadata)
    elapsed = time.perf_counter() - start
    
    # Should complete reasonably fast
    assert elapsed < 1.0  # Less than 1 second
    assert result > 0
    assert result < N


def test_extract_delta_centers_small():
    """Test extraction of multiple δ-centers"""
    N = 899  # 29 × 31
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=0.98,
        phase=0.05,
        kappa_weight=0.16,
        m_value=0,
        score=0.15
    )
    
    # Extract δ-centers
    delta_centers = extract_delta_centers(N, metadata, max_centers=10)
    
    # Should return multiple centers
    assert len(delta_centers) > 0
    assert len(delta_centers) <= 10
    
    # Each center should be valid
    for dc in delta_centers:
        assert isinstance(dc, DeltaCenter)
        assert dc.center > 0
        assert dc.center < N
        assert dc.score >= 0
        assert -1.0 <= dc.delta <= 1.0  # Reasonable δ range
    
    # Centers should be sorted by score (descending)
    scores = [dc.score for dc in delta_centers]
    assert scores == sorted(scores, reverse=True)


def test_bounded_refinement_single_center():
    """Test bounded refinement around a single center"""
    N = 899  # 29 × 31
    center = 29  # True factor
    
    # Should find exact factor at center
    found, factor, offset = bounded_refinement_single_center(N, center, radius=10)
    assert found
    assert factor == 29 or factor == 31
    assert abs(offset) <= 10
    
    # Test with center slightly off
    center = 30  # One away from 29
    found, factor, offset = bounded_refinement_single_center(N, center, radius=10)
    assert found
    assert factor == 29 or factor == 31
    assert abs(offset) <= 10
    
    # Test with center too far away
    center = 50  # Too far from factors
    found, factor, offset = bounded_refinement_single_center(N, center, radius=5)
    assert not found
    assert factor is None
    assert offset is None


def test_multi_delta_focusing_small():
    """Test multi-Δ center focusing on a small semiprime"""
    N = 899  # 29 × 31, √N ≈ 30
    seed = 30
    true_factor = 29
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=0.98,
        phase=0.05,
        kappa_weight=0.16,
        m_value=0,
        score=0.15
    )
    
    # Apply multi-Δ focusing
    result = multi_delta_focusing(
        seed=seed,
        N=N,
        metadata=metadata,
        true_factor=true_factor,
        refinement_radius=10,
        max_centers=10
    )
    
    # Check result structure
    assert isinstance(result, MultiDeltaFocusingResult)
    assert len(result.delta_centers) > 0
    assert len(result.center_results) == len(result.delta_centers)
    assert result.best_center_index >= 0
    assert result.best_center_index < len(result.delta_centers)
    assert result.total_focus_time_ms >= 0
    assert result.total_refinement_time_ms >= 0
    
    # Check best center
    assert result.best_center is not None
    assert result.best_distance_after >= 0
    assert result.best_shrink_ratio >= 0
    
    # For this small case, should find the factor
    assert result.found_factor
    assert result.factor_found in [29, 31]


def test_multi_delta_focusing_deterministic():
    """Test that multi-Δ focusing is deterministic"""
    N = 899
    seed = 30
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=0.98,
        phase=0.05,
        kappa_weight=0.16,
        m_value=0,
        score=0.15
    )
    
    # Run twice with same inputs
    result1 = multi_delta_focusing(seed, N, metadata, refinement_radius=10, max_centers=5)
    result2 = multi_delta_focusing(seed, N, metadata, refinement_radius=10, max_centers=5)
    
    # Should produce identical results
    assert len(result1.delta_centers) == len(result2.delta_centers)
    
    for dc1, dc2 in zip(result1.delta_centers, result2.delta_centers):
        assert dc1.delta == dc2.delta
        assert dc1.center == dc2.center
        assert dc1.score == dc2.score
    
    assert result1.found_factor == result2.found_factor
    if result1.found_factor:
        assert result1.factor_found == result2.factor_found


def test_multi_delta_focusing_reports_shrink_ratio():
    """Test that multi-Δ focusing computes shrink ratios correctly"""
    N = 10403  # 101 × 103, √N ≈ 102
    seed = 102
    true_factor = 101
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=0.95,
        phase=0.0,
        kappa_weight=0.14,
        m_value=0,
        score=0.13
    )
    
    result = multi_delta_focusing(
        seed=seed,
        N=N,
        metadata=metadata,
        true_factor=true_factor,
        refinement_radius=10,
        max_centers=10
    )
    
    # Check that all center results have valid metrics
    for cr in result.center_results:
        assert cr.distance_before >= 0
        assert cr.distance_after >= 0
        assert cr.shrink_ratio >= 0
        
        # Shrink ratio should be distance_after / distance_before
        if cr.distance_before > 0:
            expected_ratio = cr.distance_after / cr.distance_before
            assert abs(cr.shrink_ratio - expected_ratio) < 1e-9
    
    # Best result should have smallest distance_after
    best_distance = min(cr.distance_after for cr in result.center_results)
    assert result.best_distance_after == best_distance


def test_multi_delta_focusing_config_respected():
    """Test that multi-Δ focusing respects custom config"""
    N = 899
    seed = 30
    k = 0.3
    
    metadata = FocusingMetadata(
        k_primary=k,
        amplitude=0.98,
        phase=0.05,
        kappa_weight=0.16,
        m_value=0,
        score=0.15
    )
    
    # Custom config with different scan range
    custom_config = FOCUSING_CONFIG.copy()
    custom_config['coarse_scan_range'] = 0.02  # ±2% instead of ±5%
    custom_config['coarse_scan_step'] = 0.01   # 1% steps
    
    result = multi_delta_focusing(
        seed=seed,
        N=N,
        metadata=metadata,
        config=custom_config,
        refinement_radius=10,
        max_centers=5
    )
    
    # Should execute without errors
    assert isinstance(result, MultiDeltaFocusingResult)
    assert len(result.delta_centers) > 0
    
    # With narrower scan range, should have fewer centers
    # (2% range / 1% step = 5 steps, so at most 5 centers)
    assert len(result.delta_centers) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
