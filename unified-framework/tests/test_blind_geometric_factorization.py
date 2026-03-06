"""
Tests for Blind Geometric Factorization Experiment

These tests validate the PR-123/969 scaling infrastructure and
the blind factorization search for small semiprimes.
"""

import pytest
import math

from experiments.blind_geometric_factorization.scaling_params import (
    compute_threshold,
    compute_k_shift,
    compute_sample_count,
    compute_precision,
    get_scaling_params,
    GATE_127_PARAMS
)
from experiments.blind_geometric_factorization.resonance_scoring import (
    theta_prime,
    curvature_contribution,
    compute_resonance_score,
    verify_factor,
    PHI
)
from experiments.blind_geometric_factorization.blind_factorizer import (
    BlindGeometricFactorizer,
    factor_semiprime_blind,
    TEST_SEMIPRIMES
)


class TestScalingParams:
    """Tests for PR-123/969 scaling parameter calculations."""
    
    def test_threshold_decreases_with_bit_length(self):
        """Threshold T(N) should decrease as bit length increases."""
        t_32 = compute_threshold(32)
        t_64 = compute_threshold(64)
        t_127 = compute_threshold(127)
        
        assert t_32 > t_64 > t_127
    
    def test_k_shift_increases_with_bit_length(self):
        """k-shift k(N) should increase as bit length increases."""
        k_32 = compute_k_shift(32)
        k_64 = compute_k_shift(64)
        k_127 = compute_k_shift(127)
        
        assert k_32 < k_64 < k_127
    
    def test_sample_count_scales_linearly(self):
        """Sample count should scale linearly with bit length."""
        s_60 = compute_sample_count(60)
        s_120 = compute_sample_count(120)
        
        # Should be approximately 2x
        assert abs(s_120 / s_60 - 2.0) < 0.1
    
    def test_gate_127_params_match_reference(self):
        """Computed Gate-127 params should match reference values."""
        N_127 = 137524771864208156028430259349934309717
        params = get_scaling_params(N_127)
        
        # Should match within floating point tolerance
        assert abs(params.threshold - GATE_127_PARAMS.threshold) < 0.001
        assert abs(params.k_shift - GATE_127_PARAMS.k_shift) < 0.001
        assert params.sample_count == GATE_127_PARAMS.sample_count
        assert params.precision == GATE_127_PARAMS.precision
    
    def test_invalid_bit_length_raises(self):
        """Should raise ValueError for non-positive bit lengths."""
        with pytest.raises(ValueError):
            compute_threshold(0)
        with pytest.raises(ValueError):
            compute_k_shift(-1)


class TestResonanceScoring:
    """Tests for resonance scoring calculations."""
    
    def test_theta_prime_in_range(self):
        """θ' should be in [0, φ] range."""
        for x in [3, 5, 7, 100, 1000000]:
            theta = theta_prime(x)
            assert 0 <= theta <= PHI
    
    def test_curvature_positive(self):
        """Curvature should be positive for x > 0."""
        for x in [1, 10, 100, 1000000]:
            curv = curvature_contribution(x)
            assert curv > 0
    
    def test_resonance_score_in_range(self):
        """Resonance score should be in [0, 1] range."""
        N = 35
        sqrt_N = math.sqrt(N)
        
        for candidate in [3, 5, 7]:
            score = compute_resonance_score(candidate, N, sqrt_N, 0.35)
            assert 0 <= score <= 1
    
    def test_verify_factor_finds_factors(self):
        """verify_factor should correctly identify factors."""
        N = 35  # 5 × 7
        
        result = verify_factor(5, N)
        assert result == (5, 7)
        
        result = verify_factor(7, N)
        assert result == (5, 7)
        
        result = verify_factor(3, N)
        assert result is None


class TestBlindFactorizer:
    """Tests for blind geometric factorization."""
    
    def test_tiny_semiprime(self):
        """Should factor tiny semiprime (35 = 5 × 7)."""
        data = TEST_SEMIPRIMES["tiny"]
        result = factor_semiprime_blind(data["N"], max_iterations=100, verbose=False)
        
        assert result.success
        assert result.p * result.q == data["N"]
        assert {result.p, result.q} == {data["p"], data["q"]}
    
    def test_small_16bit_semiprime(self):
        """Should factor small 16-bit semiprime."""
        data = TEST_SEMIPRIMES["small_16bit"]
        result = factor_semiprime_blind(data["N"], max_iterations=100, verbose=False)
        
        assert result.success
        assert result.p * result.q == data["N"]
        assert {result.p, result.q} == {data["p"], data["q"]}
    
    def test_medium_32bit_semiprime(self):
        """Should factor medium 32-bit semiprime."""
        data = TEST_SEMIPRIMES["medium_32bit"]
        result = factor_semiprime_blind(data["N"], max_iterations=100, verbose=False)
        
        assert result.success
        assert result.p * result.q == data["N"]
        assert {result.p, result.q} == {data["p"], data["q"]}
    
    def test_larger_48bit_semiprime(self):
        """Should factor 48-bit semiprime with sufficient iterations."""
        data = TEST_SEMIPRIMES["larger_48bit"]
        result = factor_semiprime_blind(data["N"], max_iterations=100, verbose=False)
        
        assert result.success
        assert result.p * result.q == data["N"]
        assert {result.p, result.q} == {data["p"], data["q"]}
    
    def test_complexity_estimate(self):
        """Complexity estimate should be reasonable."""
        data = TEST_SEMIPRIMES["gate_127"]
        factorizer = BlindGeometricFactorizer(data["N"], verbose=False)
        complexity = factorizer.estimate_search_complexity()
        
        # Gate-127 should NOT be feasible
        assert not complexity["feasible"]
        assert complexity["worst_case_operations"] > 10**18
    
    def test_result_to_dict(self):
        """FactorizationResult.to_dict should produce valid dict."""
        data = TEST_SEMIPRIMES["tiny"]
        result = factor_semiprime_blind(data["N"], max_iterations=100, verbose=False)
        
        d = result.to_dict()
        assert "N" in d
        assert "success" in d
        assert "p" in d
        assert "q" in d
        assert d["success"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
