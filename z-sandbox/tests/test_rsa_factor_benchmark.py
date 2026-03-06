#!/usr/bin/env python3
"""
Test suite for RSA Factor Benchmark
====================================

Tests the RSA-2048 factor candidate extraction benchmark script
to ensure it meets all acceptance criteria.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from python.examples import rsa_factor_benchmark


class TestBenchmarkConfiguration:
    """Test benchmark configuration and constants"""
    
    def test_test_semiprime_is_2048_bits(self):
        """Verify test semiprime is 2048 bits"""
        assert rsa_factor_benchmark.N_TEST.bit_length() == 2048, \
            "N_TEST must be exactly 2048 bits"
    
    def test_factors_are_1024_bits(self):
        """Verify factors are ~1024 bits each"""
        assert rsa_factor_benchmark.P_TRUE.bit_length() == 1024, \
            "P_TRUE must be 1024 bits"
        assert rsa_factor_benchmark.Q_TRUE.bit_length() == 1024, \
            "Q_TRUE must be 1024 bits"
    
    def test_factors_multiply_to_n(self):
        """Verify p × q = N"""
        assert rsa_factor_benchmark.P_TRUE * rsa_factor_benchmark.Q_TRUE == rsa_factor_benchmark.N_TEST, \
            "P_TRUE × Q_TRUE must equal N_TEST"
    
    def test_refinement_radius_is_1000(self):
        """Verify refinement radius is fixed at 1000"""
        assert rsa_factor_benchmark.REFINEMENT_RADIUS == 1000, \
            "REFINEMENT_RADIUS must be 1000"
    
    def test_time_budget_is_60_seconds(self):
        """Verify time budget is 60 seconds"""
        assert rsa_factor_benchmark.TIME_BUDGET_MS == 60000, \
            "TIME_BUDGET_MS must be 60000 (60 seconds)"


class TestDistanceMetrics:
    """Test distance metric computation"""
    
    def test_distance_metrics_exact_match(self):
        """Test distance metrics for exact match"""
        seed = 12345
        true_factor = 12345
        
        metrics = rsa_factor_benchmark.compute_distance_metrics(seed, true_factor)
        
        assert metrics['abs_distance'] == 0, "Exact match should have zero distance"
        assert metrics['rel_distance'] == 0, "Exact match should have zero relative distance"
    
    def test_distance_metrics_positive_offset(self):
        """Test distance metrics for positive offset"""
        seed = 12350
        true_factor = 12345
        
        metrics = rsa_factor_benchmark.compute_distance_metrics(seed, true_factor)
        
        assert metrics['abs_distance'] == 5
        assert abs(metrics['rel_distance'] - (5 / 12345)) < 1e-10
    
    def test_distance_metrics_negative_offset(self):
        """Test distance metrics for negative offset"""
        seed = 12340
        true_factor = 12345
        
        metrics = rsa_factor_benchmark.compute_distance_metrics(seed, true_factor)
        
        assert metrics['abs_distance'] == 5
        assert abs(metrics['rel_distance'] - (5 / 12345)) < 1e-10


class TestBoundedRefinement:
    """Test bounded local refinement"""
    
    def test_refinement_finds_exact_factor(self):
        """Test that refinement finds exact factor within window"""
        # Use small test case: 143 = 11 × 13
        N = 143
        seeds = [12]  # Near factor 11
        radius = 2
        
        result = rsa_factor_benchmark.bounded_local_refinement(N, seeds, radius)
        
        assert result['found_factor'] is True, "Should find factor 11 within ±2 of seed 12"
        assert result['factor_found'] in [11, 13], "Found factor should be 11 or 13"
        assert result['seed_index_found'] == 0, "Should be found from first seed"
    
    def test_refinement_respects_radius(self):
        """Test that refinement only searches within specified radius"""
        # Use case where factor is outside radius
        N = 143
        seeds = [5]  # Factor 11 is more than 3 away
        radius = 3
        
        result = rsa_factor_benchmark.bounded_local_refinement(N, seeds, radius)
        
        assert result['found_factor'] is False, "Should not find factor outside radius"
        # Should check range [5-3, 5+3] = [2, 8] inclusive = 7 candidates (2,3,4,5,6,7,8)
        assert result['candidates_checked'] == 7
    
    def test_refinement_counts_candidates_correctly(self):
        """Test that candidate count is accurate"""
        N = 143
        seeds = [10, 20]
        radius = 5
        
        result = rsa_factor_benchmark.bounded_local_refinement(N, seeds, radius)
        
        # First seed: 10-5=5 to 10+5=15, but found factor 11 early
        # Should stop at first seed since factor is found
        assert result['found_factor'] is True
        assert result['candidates_checked'] <= (2 * radius + 1)  # Max for one seed


class TestBenchmarkIntegration:
    """Integration tests for full benchmark"""
    
    @pytest.mark.slow
    def test_benchmark_runs_without_error(self):
        """Test that benchmark runs to completion without errors"""
        # This is a basic smoke test - the actual 2048-bit run takes time
        try:
            results = rsa_factor_benchmark.run_benchmark()
            assert results is not None
            assert 'N_bits' in results
        except Exception as e:
            pytest.fail(f"Benchmark raised unexpected exception: {e}")
    
    def test_benchmark_returns_required_metrics(self, monkeypatch):
        """Test that benchmark returns all required metrics"""
        # Use monkeypatch to temporarily override module constants for testing
        monkeypatch.setattr(rsa_factor_benchmark, 'N_TEST', 143)
        monkeypatch.setattr(rsa_factor_benchmark, 'P_TRUE', 11)
        monkeypatch.setattr(rsa_factor_benchmark, 'Q_TRUE', 13)
        monkeypatch.setattr(rsa_factor_benchmark, 'MAX_SEEDS', 5)
        
        results = rsa_factor_benchmark.run_benchmark()
        
        # Check all required metrics exist
        required_keys = [
            'N_bits',
            'num_seeds',
            'k_used',
            'seed_gen_time_ms',
            'refine_time_ms',
            'total_time_ms',
            'within_time_budget',
            'found_factor',
            'candidates_checked',
            'refinement_radius',
            'seed_metrics'
        ]
        
        for key in required_keys:
            assert key in results, f"Missing required metric: {key}"
        
        # Check that seed_metrics is a list with entries
        assert isinstance(results['seed_metrics'], list)
        assert len(results['seed_metrics']) > 0
        
        # Each seed metric should have required fields
        for seed_metric in results['seed_metrics']:
            assert 'seed_index' in seed_metric
            assert 'p_candidate' in seed_metric
            assert 'abs_distance' in seed_metric
            assert 'rel_distance' in seed_metric
            assert 'score' in seed_metric


class TestMethodologyCompliance:
    """Test that benchmark follows required methodology"""
    
    def test_no_ground_truth_in_seed_generation(self):
        """Verify seed generation doesn't use ground truth factors"""
        # This is verified by code inspection - the factorize_greens
        # function only receives N, not p or q
        
        # We can at least verify P_TRUE and Q_TRUE are not imported
        # into the greens_function_factorization module
        from python import greens_function_factorization
        
        assert not hasattr(greens_function_factorization, 'P_TRUE')
        assert not hasattr(greens_function_factorization, 'Q_TRUE')
    
    def test_bounded_refinement_only(self):
        """Verify only bounded refinement is used (no trial division)"""
        # Test that refinement function has fixed radius
        N = 143
        seeds = [10]
        radius = 5
        
        result = rsa_factor_benchmark.bounded_local_refinement(N, seeds, radius)
        
        # Candidates checked should be bounded by radius
        max_possible = (2 * radius + 1) * len(seeds)
        assert result['candidates_checked'] <= max_possible, \
            "Refinement checked too many candidates (possible trial division)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
