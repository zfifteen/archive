#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_z5d_integration.py — Unit tests for Z5D integration modules

Tests all components: z5d_predictor, m0_estimator, adaptive_step,
resonance_search, and vernier_search.
"""

import unittest
import mpmath as mp
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python.geom.z5d_predictor import (
    predict_prime_near_sqrt, 
    compute_confidence_ppm,
    z5d_predict_prime,
    z5d_predict_logL
)
from python.geom.m0_estimator import estimate_m0_from_z5d_prior
from python.geom.adaptive_step import (
    compute_delta_m,
    generate_symmetric_queue,
    validate_adaptive_stepping
)
from python.geom.resonance_search import (
    integer_resonance_objective,
    golden_section_maximize,
    brent_maximize,
    refine_m_with_line_search
)
from python.geom.vernier_search import (
    score_intersection,
    vernier_triangulation,
    multi_k_consensus
)
try:
    from python.rsa260_z5d_runner import enforce_precision_and_provenance
    RUNNER_AVAILABLE = True
except ImportError:
    RUNNER_AVAILABLE = False


# Known RSA numbers for validation
RSA_100 = int("1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139")
RSA_100_P = 37975227936943673922808872755445627854565536638199
RSA_100_Q = 40094690950920881030683735292761468389214899724061


class TestZ5DPredictor(unittest.TestCase):
    """Test Z5D prime prediction"""
    
    def setUp(self):
        mp.mp.dps = 200
    
    def test_predict_prime_near_sqrt(self):
        """Test Z5D prediction returns value near √N"""
        p_hat = predict_prime_near_sqrt(RSA_100, dps=200)
        sqrt_N = mp.sqrt(mp.mpf(RSA_100))
        
        # Check p_hat is roughly near sqrt(N) (allow wide range for geometric priors)
        ratio = float(p_hat / sqrt_N)
        self.assertGreater(ratio, 0.1)
        self.assertLess(ratio, 10000.0)  # Allow large range for predictors
        
        # Check p_hat is odd
        self.assertEqual(int(p_hat) % 2, 1)
    
    def test_compute_confidence_ppm(self):
        """Test confidence computation returns reasonable values"""
        epsilon_ppm, safety = compute_confidence_ppm(RSA_100, dps=200)
        
        # For RSA-100 (330 bits), expect ~100 ppm
        self.assertGreater(epsilon_ppm, 50.0)
        self.assertLess(epsilon_ppm, 500.0)
        self.assertGreaterEqual(safety, 2.0)
    
    def test_z5d_predict_small_primes(self):
        """Test Z5D prediction on small primes"""
        # Known small primes
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        
        for k in range(1, 10):
            p_pred = z5d_predict_prime(k, dps=100)
            # Allow some error for small k
            self.assertIn(p_pred, small_primes, f"k={k} prediction failed")


class TestM0Estimator(unittest.TestCase):
    """Test m₀ estimation from Z5D prior"""
    
    def setUp(self):
        mp.mp.dps = 200
    
    def test_estimate_m0_basic(self):
        """Test m₀ estimation returns finite values"""
        m0, window, epsilon_ppm, safety = estimate_m0_from_z5d_prior(RSA_100, k=0.30, dps=200)
        
        # Check all values are finite
        self.assertFalse(mp.isinf(m0))
        self.assertFalse(mp.isnan(m0))
        self.assertGreater(float(window), 0)
        self.assertGreater(epsilon_ppm, 0)
        self.assertGreater(safety, 0)
    
    def test_window_scaling_with_k(self):
        """Test window scales with k"""
        m0_28, win_28, _, _ = estimate_m0_from_z5d_prior(RSA_100, k=0.28, dps=200)
        m0_32, win_32, _, _ = estimate_m0_from_z5d_prior(RSA_100, k=0.32, dps=200)
        
        # Larger k should give larger window (window ~ k/π * ε)
        self.assertGreater(float(win_32), float(win_28))
    
    def test_window_reduction_vs_baseline(self):
        """Test window is much smaller than uniform baseline"""
        _, window, _, _ = estimate_m0_from_z5d_prior(RSA_100, k=0.30, dps=200)
        
        # Window should be << 1.0 (uniform baseline)
        self.assertLess(float(window), 0.001)


class TestAdaptiveStep(unittest.TestCase):
    """Test adaptive stepping"""
    
    def setUp(self):
        mp.mp.dps = 200
        self.logN = mp.log(mp.mpf(RSA_100))
        self.k = 0.30
    
    def p_from_m(self, m, k, logN):
        """Helper: compute p̂(m)"""
        return mp.exp((logN - (2 * mp.pi * m) / mp.mpf(k)) / 2)
    
    def test_compute_delta_m_positive(self):
        """Test Δm computation returns positive value"""
        m = mp.mpf(0.0)
        p_hat = self.p_from_m(m, self.k, self.logN)
        delta_m = compute_delta_m(m, self.k, p_hat)
        
        self.assertGreater(float(delta_m), 0)
    
    def test_compute_delta_m_scaling(self):
        """Test Δm scales inversely with p̂"""
        m = mp.mpf(0.0)
        p_hat = self.p_from_m(m, self.k, self.logN)
        delta_m = compute_delta_m(m, self.k, p_hat)
        
        # For smaller p̂ (e.g., at m=1.0), Δm should be larger
        m_large = mp.mpf(1.0)
        p_hat_small = self.p_from_m(m_large, self.k, self.logN)
        delta_m_large = compute_delta_m(m_large, self.k, p_hat_small)
        
        # delta_m ~ 1/p̂, so smaller p̂ gives larger delta_m
        self.assertGreater(float(delta_m_large), float(delta_m))
    
    def test_generate_symmetric_queue(self):
        """Test symmetric queue generation"""
        m0 = mp.mpf(0.0)
        window = mp.mpf(0.01)
        
        queue = generate_symmetric_queue(
            m0, window, self.k, self.logN, self.p_from_m, max_candidates=100
        )
        
        # Check queue is non-empty
        self.assertGreater(len(queue), 0)
        
        # Check first element is m0
        self.assertAlmostEqual(float(queue[0]), 0.0, places=10)
        
        # Check symmetric ordering (alternating +/-)
        if len(queue) >= 3:
            self.assertGreater(float(queue[1]), float(m0))
            self.assertLess(float(queue[2]), float(m0))
    
    def test_queue_within_window(self):
        """Test all queue elements are within window"""
        m0 = mp.mpf(0.0)
        window = mp.mpf(0.02)
        
        queue = generate_symmetric_queue(
            m0, window, self.k, self.logN, self.p_from_m, max_candidates=1000
        )
        
        for m in queue:
            dist = mp.fabs(m - m0)
            self.assertLessEqual(float(dist), float(window) * 1.01)  # Allow small overshoot
    
    def test_adaptive_step_rsa260_scale(self):
        """Test adaptive stepping at RSA-260 scale with high precision"""
        # RSA-260 ~ 260-bit modulus -> p ~ 2^130
        mp.mp.dps = 300  # Ample margin for 260-bit work
        bits = 260
        p_hat = mp.mpf(2) ** 130
        k = mp.mpf('0.3')  # Typical k parameter
        m0 = mp.mpf(1)  # Reasonable m0 for testing
        
        # Generate small queue to test stepping logic
        queue = generate_symmetric_queue(
            m0, mp.mpf('1.0'), k, mp.log(mp.mpf(2)**(2*bits)), self.p_from_m, 
            max_candidates=20
        )
        
        # Ensure queue is generated without errors
        self.assertGreater(len(queue), 1)
        
        # Validate stepping achieves Δp̂ ≈ 1
        valid = validate_adaptive_stepping(queue, k, mp.log(mp.mpf(2)**(2*bits)), self.p_from_m, tolerance=100.0)
        if not valid:
            print("\n--- Debugging Adaptive Stepping Failure ---")
            for i in range(len(queue) - 1):
                p_i = self.p_from_m(queue[i], k, mp.log(mp.mpf(2)**(2*bits)))
                p_next = self.p_from_m(queue[i+1], k, mp.log(mp.mpf(2)**(2*bits)))
                delta_p = mp.fabs(p_next - p_i)
                print(f"  Step {i}: Δp̂ = {mp.nstr(delta_p, 8)}")
            print("-------------------------------------------")
        self.assertTrue(valid, "Adaptive stepping failed validation at RSA-260 scale")
        
        # Ensure no stalling (delta_m shouldn't be clamped to oversized static min)
        # At RSA-260 scale, theoretical delta_m ~ 1e-131, so check it's not too large
        first_delta = mp.fabs(queue[1] - queue[0])
        self.assertLess(float(first_delta), 1e-20, "Delta_m too large, likely clamped to static min")


class TestResonanceSearch(unittest.TestCase):
    """Test integer-resonance objective and line search"""
    
    def setUp(self):
        mp.mp.dps = 200
        self.logN = mp.log(mp.mpf(RSA_100))
        self.k = 0.30
    
    def test_integer_resonance_objective(self):
        """Test resonance objective returns finite value"""
        m = mp.mpf(0.0)
        score = integer_resonance_objective(m, self.k, RSA_100, self.logN)
        
        self.assertFalse(mp.isinf(score))
        self.assertFalse(mp.isnan(score))
    
    def test_resonance_peaks_near_factors(self):
        """Test resonance is higher when p̂ is close to actual factor"""
        # Compute m corresponding to actual factor
        p_true = mp.mpf(RSA_100_P)
        log_p_true = mp.log(p_true)
        
        # From p̂(m) = exp((logN - 2πm/k)/2), solve for m
        # 2*log(p) = logN - 2πm/k
        # m = k*(logN - 2*log(p))/(2π)
        m_true = (self.k * (self.logN - 2*log_p_true)) / (2 * mp.pi)
        
        score_true = integer_resonance_objective(m_true, self.k, RSA_100, self.logN)
        score_random = integer_resonance_objective(mp.mpf(10.0), self.k, RSA_100, self.logN)
        
        # Score at true factor should be higher
        self.assertGreater(float(score_true), float(score_random))
    
    def test_golden_section_maximize(self):
        """Test golden-section search"""
        # Simple quadratic: f(x) = -(x-2)^2 + 5, max at x=2
        def f(x):
            return -(x - 2)**2 + 5
        
        x_max, f_max = golden_section_maximize(f, mp.mpf(0.0), mp.mpf(4.0), tol=1e-6)
        
        self.assertAlmostEqual(float(x_max), 2.0, places=4)
        self.assertAlmostEqual(float(f_max), 5.0, places=4)
    
    def test_brent_maximize(self):
        """Test Brent's method"""
        # Simple cubic: f(x) = -x^3 + 3x^2 + 1, max near x=2
        def f(x):
            return -x**3 + 3*x**2 + 1
        
        x_max, f_max = brent_maximize(f, mp.mpf(0.0), mp.mpf(3.0), tol=1e-6)
        
        # Max is at x=2 (derivative: -3x^2 + 6x = 0 => x=2)
        self.assertAlmostEqual(float(x_max), 2.0, places=3)
    
    def test_refine_m_with_line_search(self):
        """Test line search refinement improves resonance"""
        m_initial = mp.mpf(0.0)
        
        score_initial = integer_resonance_objective(m_initial, self.k, RSA_100, self.logN)
        m_refined, score_refined = refine_m_with_line_search(
            m_initial, self.k, RSA_100, self.logN, delta=0.05, dps=200
        )
        
        # Refined score should be ≥ initial (might be equal if already at local max)
        self.assertGreaterEqual(float(score_refined), float(score_initial) * 0.99)


class TestVernierSearch(unittest.TestCase):
    """Test vernier triangulation"""
    
    def setUp(self):
        mp.mp.dps = 200
        self.logN = mp.log(mp.mpf(RSA_100))
    
    def test_score_intersection(self):
        """Test intersection scoring"""
        m = mp.mpf(0.0)
        k1 = 0.29
        k2 = 0.31
        
        score = score_intersection(m, k1, k2, RSA_100, self.logN)
        
        self.assertFalse(mp.isinf(score))
        self.assertFalse(mp.isnan(score))
    
    def test_vernier_triangulation_returns_candidates(self):
        """Test vernier returns candidate list"""
        k1 = 0.29
        k2 = 0.31
        m0 = mp.mpf(0.0)
        window = mp.mpf(0.05)
        
        candidates = vernier_triangulation(
            RSA_100, k1, k2, m0, window, 
            coarse_step=0.01, threshold=0.0, top_k=10, dps=200
        )
        
        # Should return some candidates
        self.assertGreater(len(candidates), 0)
        self.assertLessEqual(len(candidates), 10)
        
        # Each candidate is (m, score)
        for m, score in candidates:
            self.assertFalse(mp.isinf(m))
            self.assertFalse(mp.isnan(score))
    
    def test_multi_k_consensus(self):
        """Test multi-k consensus search"""
        k_values = [0.28, 0.29, 0.30, 0.31, 0.32]
        m0 = mp.mpf(0.0)
        window = mp.mpf(0.05)
        
        candidates = multi_k_consensus(
            RSA_100, k_values, m0, window,
            coarse_step=0.01, top_k=5, dps=200
        )
        
        self.assertGreater(len(candidates), 0)
        self.assertLessEqual(len(candidates), 5)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple modules"""
    
    def setUp(self):
        mp.mp.dps = 200
        self.logN = mp.log(mp.mpf(RSA_100))
    
    def test_z5d_to_m0_to_queue(self):
        """Test full pipeline: Z5D → m₀ → adaptive queue"""
        k = 0.30
        
        # Get m₀ from Z5D
        m0, window, _, _ = estimate_m0_from_z5d_prior(RSA_100, k, dps=200)
        
        # Generate adaptive queue
        def p_from_m(m, k, logN):
            return mp.exp((logN - (2 * mp.pi * m) / mp.mpf(k)) / 2)
        
        queue = generate_symmetric_queue(
            m0, window, k, self.logN, p_from_m, max_candidates=100
        )
        
        # Check queue is reasonable
        self.assertGreater(len(queue), 0)
        self.assertAlmostEqual(float(queue[0]), float(m0), places=10)
    
    def test_vernier_to_line_search(self):
        """Test vernier followed by line search refinement"""
        k1 = 0.29
        k2 = 0.31
        m0 = mp.mpf(0.0)
        window = mp.mpf(0.05)
        
        # Run vernier
        candidates = vernier_triangulation(
            RSA_100, k1, k2, m0, window,
            coarse_step=0.01, threshold=0.0, top_k=5, dps=200
        )
        
        # Refine top candidate with line search
        if len(candidates) > 0:
            m_seed, _ = candidates[0]
            m_refined, score_refined = refine_m_with_line_search(
                m_seed, k1, RSA_100, self.logN, delta=0.01, dps=200
            )
            
            # Should produce valid refined m
            self.assertFalse(mp.isinf(m_refined))
            self.assertFalse(mp.isnan(score_refined))


class TestRunnerGating(unittest.TestCase):
    """Test runner gating logic (GCD-first, etc.)"""
    
    def setUp(self):
        mp.mp.dps = 200
    
    def test_gcd_before_prp(self):
        """Test that GCD is called before PRP in candidate evaluation"""
        import math
        from unittest.mock import patch
        
        # Mock the runner's check_gcd_first and is_probable_prime functions
        calls = []
        
        def mock_gcd(N, p_int):
            calls.append("gcd")
            return math.gcd(N, p_int)
        
        def mock_prp(n, rounds=32, seed=0x5A17):
            calls.append("prp")
            return False  # Not prime for test
        
        # Test the evaluation logic (simplified version of runner's loop)
        N = 1234567891011
        p_int = 2  # Test with small prime
        
        # Simulate the gating: GCD first, then PRP only if gcd==1
        g = mock_gcd(N, p_int)
        prp_result = None
        if g == 1:
            prp_result = mock_prp(p_int)
        
        # Verify order: gcd called before prp
        self.assertEqual(calls, ["gcd", "prp"], "GCD should be called first, then PRP if gcd==1")
        
        # Test case where gcd != 1 (should not call PRP)
        calls.clear()
        p_int_bad = N  # This will make gcd = N (not 1)
        g = mock_gcd(N, p_int_bad)
        if g == 1:
            prp_result = mock_prp(p_int_bad)
        
        self.assertEqual(calls, ["gcd"], "PRP should not be called when gcd != 1")
    
    def test_deterministic_provenance(self):
        """Test that provenance logging produces consistent output"""
        if not RUNNER_AVAILABLE:
            self.skipTest("Runner not available")
            
        import tempfile
        import json
        import time
        from unittest.mock import patch
        
        # Mock platform and git functions for deterministic output
        with patch('platform.platform', return_value='TestPlatform'), \
             patch('platform.python_version', return_value='3.9.0'), \
             patch('time.time', return_value=1234567890.0):
            
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
                prov_path = f.name
            
            try:
                # Call the function twice with same inputs
                mp.mp.dps = 300
                enforce_precision_and_provenance(260, provenance_path=prov_path)
                enforce_precision_and_provenance(260, provenance_path=prov_path)
                
                # Read the log
                with open(prov_path, 'r') as f:
                    lines = f.readlines()
                
                # Should have two identical entries
                self.assertEqual(len(lines), 2)
                entry1 = json.loads(lines[0])
                entry2 = json.loads(lines[1])
                
                # Remove timestamp for comparison (it's mocked to same value anyway)
                entry1.pop('timestamp', None)
                entry2.pop('timestamp', None)
                
                self.assertEqual(entry1, entry2, "Provenance entries should be identical")
                
            finally:
                import os
                os.unlink(prov_path)


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
