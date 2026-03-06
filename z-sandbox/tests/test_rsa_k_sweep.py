#!/usr/bin/env python3
"""
Test suite for RSA K-Sweep Tool
================================

Tests the RSA-2048 k-parameter sweep script to ensure it meets
all acceptance criteria from Issue #193.
"""

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import subprocess
import os
import re


class TestKSweepConfiguration:
    """Test k-sweep configuration and constants"""
    
    def test_uses_same_semiprime_as_benchmark(self):
        """Verify k-sweep uses same semiprime as rsa_factor_benchmark"""
        from python.examples import rsa_factor_benchmark
        
        assert rsa_k_sweep.N_TEST == rsa_factor_benchmark.N_TEST, \
            "K-sweep must use same N as benchmark"
        assert rsa_k_sweep.P_TRUE == rsa_factor_benchmark.P_TRUE, \
            "K-sweep must use same P_TRUE as benchmark"
        assert rsa_k_sweep.Q_TRUE == rsa_factor_benchmark.Q_TRUE, \
            "K-sweep must use same Q_TRUE as benchmark"
    
    def test_n_is_2048_bits(self):
        """Verify test semiprime is 2048 bits"""
        assert rsa_k_sweep.N_TEST.bit_length() == 2048, \
            "N_TEST must be exactly 2048 bits"
    
    def test_factors_are_1024_bits(self):
        """Verify factors are 1024 bits each"""
        assert rsa_k_sweep.P_TRUE.bit_length() == 1024, \
            "P_TRUE must be 1024 bits"
        assert rsa_k_sweep.Q_TRUE.bit_length() == 1024, \
            "Q_TRUE must be 1024 bits"
    
    def test_k_base_values_are_correct(self):
        """Verify k_base values match specification"""
        expected = [0.250, 0.260, 0.270, 0.280, 0.290,
                   0.300, 0.310, 0.320, 0.330, 0.340, 0.350]
        assert rsa_k_sweep.K_BASE_VALUES == expected, \
            "K_BASE_VALUES must match specification"
    
    def test_detune_offset_is_correct(self):
        """Verify detune offset is ±0.5%"""
        assert rsa_k_sweep.DETUNE_OFFSET == 0.005, \
            "DETUNE_OFFSET must be 0.005 (0.5%)"
    
    def test_has_deterministic_seed(self):
        """Verify script has deterministic seed constant"""
        assert hasattr(rsa_k_sweep, 'DETERMINISTIC_SEED'), \
            "Must have DETERMINISTIC_SEED constant"
        assert rsa_k_sweep.DETERMINISTIC_SEED == 1337, \
            "DETERMINISTIC_SEED should be 1337"


class TestDistanceComputation:
    """Test distance-to-truth computation"""
    
    def test_distance_to_exact_p(self):
        """Test distance when seed equals p_true"""
        seed = 12345
        p_true = 12345
        q_true = 67890
        
        result = rsa_k_sweep.compute_distance_to_truth(seed, p_true, q_true)
        
        assert result['abs_distance'] == 0
        assert result['rel_distance'] == 0
        assert result['closest_to'] == 'p'
    
    def test_distance_to_exact_q(self):
        """Test distance when seed equals q_true"""
        seed = 67890
        p_true = 12345
        q_true = 67890
        
        result = rsa_k_sweep.compute_distance_to_truth(seed, p_true, q_true)
        
        assert result['abs_distance'] == 0
        assert result['rel_distance'] == 0
        assert result['closest_to'] == 'q'
    
    def test_distance_closer_to_p(self):
        """Test distance when seed is closer to p_true"""
        seed = 12350
        p_true = 12345
        q_true = 67890
        
        result = rsa_k_sweep.compute_distance_to_truth(seed, p_true, q_true)
        
        assert result['abs_distance'] == 5
        assert result['closest_to'] == 'p'
        assert abs(result['rel_distance'] - (5 / p_true)) < 1e-10
    
    def test_distance_closer_to_q(self):
        """Test distance when seed is closer to q_true"""
        seed = 67885
        p_true = 12345
        q_true = 67890
        
        result = rsa_k_sweep.compute_distance_to_truth(seed, p_true, q_true)
        
        assert result['abs_distance'] == 5
        assert result['closest_to'] == 'q'
        assert abs(result['rel_distance'] - (5 / q_true)) < 1e-10


class TestKVariantAggregation:
    """Test k_base group aggregation"""
    
    def test_aggregation_with_seeds(self):
        """Test aggregation when all variants return seeds"""
        k_base = 0.300
        
        seeds_base = [
            {'p_prime': 100, 'p_prime_bits': 7, 'abs_distance': 10,
             'rel_distance': 0.1, 'confidence': 0.8, 'k_source': 'k_base'}
        ]
        seeds_plus = [
            {'p_prime': 105, 'p_prime_bits': 7, 'abs_distance': 5,
             'rel_distance': 0.05, 'confidence': 0.9, 'k_source': 'k_plus'}
        ]
        seeds_minus = [
            {'p_prime': 95, 'p_prime_bits': 7, 'abs_distance': 15,
             'rel_distance': 0.15, 'confidence': 0.7, 'k_source': 'k_minus'}
        ]
        
        result = rsa_k_sweep.aggregate_k_base_group(
            k_base, seeds_base, seeds_plus, seeds_minus
        )
        
        # Best should be from k_plus (smallest rel_distance)
        assert result['k_base'] == k_base
        assert result['best_rel_distance'] == 0.05
        assert result['best_seed_source'] == 'k_plus'
        assert result['num_seeds_total'] == 3
        assert 'determinism_info' in result
    
    def test_aggregation_with_no_seeds(self):
        """Test aggregation when no seeds are returned"""
        k_base = 0.300
        
        result = rsa_k_sweep.aggregate_k_base_group(
            k_base, [], [], []
        )
        
        assert result['k_base'] == k_base
        assert result['best_rel_distance'] is None
        assert result['best_seed_source'] is None
        assert result['num_seeds_total'] == 0
        assert 'determinism_info' in result


class TestKSweepExecution:
    """Test k-sweep execution and output"""
    
    @pytest.mark.slow
    def test_k_sweep_runs_without_error(self):
        """Test that k-sweep runs to completion without errors"""
        try:
            report = rsa_k_sweep.run_k_sweep()
            assert report is not None
            assert isinstance(report, dict)
        except Exception as e:
            pytest.fail(f"K-sweep raised unexpected exception: {e}")
    
    def test_k_sweep_returns_required_fields(self, monkeypatch):
        """Test that k-sweep report has all required fields"""
        # Use small test case to speed up test
        monkeypatch.setattr(rsa_k_sweep, 'N_TEST', 143)
        monkeypatch.setattr(rsa_k_sweep, 'P_TRUE', 11)
        monkeypatch.setattr(rsa_k_sweep, 'Q_TRUE', 13)
        monkeypatch.setattr(rsa_k_sweep, 'K_BASE_VALUES', [0.300, 0.310])
        monkeypatch.setattr(rsa_k_sweep, 'MAX_CANDIDATES', 5)
        
        report = rsa_k_sweep.run_k_sweep()
        
        # Check top-level required fields
        required_top_level = [
            'N_bits',
            'global_best_k_base',
            'global_best_source',
            'global_best_abs_distance',
            'global_best_rel_distance',
            'results'
        ]
        
        for key in required_top_level:
            assert key in report, f"Missing required field: {key}"
        
        # Check that results is a list
        assert isinstance(report['results'], list)
        assert len(report['results']) == 2  # We set 2 k_base values
        
        # Check each result has required fields
        for result in report['results']:
            required_result_fields = [
                'k_base',
                'k_plus',
                'k_minus',
                'best_abs_distance',
                'best_rel_distance',
                'best_seed_bits',
                'best_seed_confidence',
                'best_seed_source',
                'num_seeds_total',
                'determinism_info'
            ]
            
            for key in required_result_fields:
                assert key in result, f"Missing required result field: {key}"
    
    def test_k_sweep_evaluates_all_k_base_values(self, monkeypatch):
        """Test that all k_base values are evaluated"""
        monkeypatch.setattr(rsa_k_sweep, 'N_TEST', 143)
        monkeypatch.setattr(rsa_k_sweep, 'P_TRUE', 11)
        monkeypatch.setattr(rsa_k_sweep, 'Q_TRUE', 13)
        monkeypatch.setattr(rsa_k_sweep, 'MAX_CANDIDATES', 5)
        
        # Original has 11 k values
        original_k_values = rsa_k_sweep.K_BASE_VALUES
        
        report = rsa_k_sweep.run_k_sweep()
        
        # Should have one result per k_base
        assert len(report['results']) == len(original_k_values)
        
        # Extract k_base values from results
        result_k_values = [r['k_base'] for r in report['results']]
        
        # Should match the configured K_BASE_VALUES
        assert result_k_values == original_k_values
    
    def test_k_plus_and_k_minus_computed_correctly(self, monkeypatch):
        """Test that k_plus and k_minus are computed with correct detune"""
        monkeypatch.setattr(rsa_k_sweep, 'N_TEST', 143)
        monkeypatch.setattr(rsa_k_sweep, 'P_TRUE', 11)
        monkeypatch.setattr(rsa_k_sweep, 'Q_TRUE', 13)
        monkeypatch.setattr(rsa_k_sweep, 'K_BASE_VALUES', [0.300])
        monkeypatch.setattr(rsa_k_sweep, 'MAX_CANDIDATES', 5)
        
        report = rsa_k_sweep.run_k_sweep()
        
        result = report['results'][0]
        k_base = result['k_base']
        k_plus = result['k_plus']
        k_minus = result['k_minus']
        
        # Check that detune is applied correctly
        assert abs(k_plus - k_base * 1.005) < 1e-10
        assert abs(k_minus - k_base * 0.995) < 1e-10


class TestMethodologyCompliance:
    """Test that k-sweep follows required methodology"""
    
    def test_no_refinement_imports(self):
        """Verify script doesn't import or call refinement"""
        # Check that bounded_local_refinement is not imported
        assert not hasattr(rsa_k_sweep, 'bounded_local_refinement'), \
            "K-sweep must not import or use refinement"
    
    def test_no_classical_factorization_imports(self):
        """Verify no classical factorization methods are imported"""
        # The script should only import factorize_greens
        import inspect
        source = inspect.getsource(rsa_k_sweep)
        
        # Check for forbidden import statements using regex
        forbidden_import_patterns = [
            r'^\s*import\s+pollard',
            r'^\s*from\s+.*pollard',
            r'^\s*import\s+rho',
            r'^\s*from\s+.*rho',
            r'^\s*import\s+ecm',
            r'^\s*from\s+.*ecm',
            r'^\s*import\s+gnfs',
            r'^\s*from\s+.*gnfs',
            r'^\s*import\s+miller_rabin',
            r'^\s*from\s+.*miller_rabin',
            r'^\s*import\s+trial_division',
            r'^\s*from\s+.*trial_division',
        ]
        for pattern in forbidden_import_patterns:
            assert not re.search(pattern, source, re.MULTILINE | re.IGNORECASE), \
                f"K-sweep must not import forbidden classical method: {pattern}"
    
    def test_uses_python_int_for_large_numbers(self):
        """Verify large integers are Python ints, not numpy"""
        # Check that N_TEST, P_TRUE, Q_TRUE are Python ints
        assert isinstance(rsa_k_sweep.N_TEST, int)
        assert isinstance(rsa_k_sweep.P_TRUE, int)
        assert isinstance(rsa_k_sweep.Q_TRUE, int)
    
    def test_determinism_info_in_results(self):
        """Verify determinism info is tracked in output"""
        # Quick test with small case
        k_base = 0.300
        result = rsa_k_sweep.aggregate_k_base_group(k_base, [], [], [])
        
        assert 'determinism_info' in result
        assert 'seed' in result['determinism_info']
        assert 'detune_offset' in result['determinism_info']


class TestPhaseSeparation:
    """Test that phases are properly separated for methodological purity"""

    def test_pure_resonance_phase_marked(self):
        """Test that pure resonance scripts declare their phase"""
        # Check rsa_k_sweep.py has PHASE marker
        k_sweep_path = os.path.join(os.path.dirname(__file__), '..', 'python', 'examples', 'rsa_k_sweep.py')
        with open(k_sweep_path, 'r') as f:
            source = f.read()
        # Should not have FINISHER_ASSISTED
        assert 'PHASE = "FINISHER_ASSISTED"' not in source
        # Could have PURE_RESONANCE or none, but check for methodological comments
        assert 'pure resonance' in source.lower() or 'no refinement' in source.lower()

    def test_finisher_phase_marked(self):
        """Test that finisher script declares its phase"""
        finisher_path = os.path.join(os.path.dirname(__file__), '..', 'python', 'examples', 'rsa_seed_refine_window.py')
        with open(finisher_path, 'r') as f:
            source = f.read()
        assert 'PHASE = "FINISHER_ASSISTED"' in source

    def test_no_refinement_in_pure_scripts(self):
        """Test that pure resonance scripts don't have refinement logic"""
        k_sweep_path = os.path.join(os.path.dirname(__file__), '..', 'python', 'examples', 'rsa_k_sweep.py')
        with open(k_sweep_path, 'r') as f:
            source = f.read()
        # Should not have N % candidate or divisibility checks
        forbidden_patterns = [
            r'N\s*%\s*candidate',
            r'divisibility',
            r'range\(.*radius',
            r'±1000'
        ]
        for pattern in forbidden_patterns:
            assert not re.search(pattern, source, re.IGNORECASE), f"Pure script contains refinement pattern: {pattern}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
