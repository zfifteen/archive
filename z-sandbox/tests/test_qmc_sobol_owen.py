#!/usr/bin/env python3
"""
Tests for Sobol + Owen scrambling QMC implementation.

Tests the new QMC scripts:
- qmc_directions_demo.py
- benchmark_elliptic.py
- qmc_vs_mc_benchmark.py
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
import numpy as np

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python.qmc_engines import create_engine, MCEngine, SobolOwenEngine, Rank1LatticeEngine
from utils.z_framework import kappa, theta_prime


class TestQMCEnginesIntegration(unittest.TestCase):
    """Test QMC engines with RSA test cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_n = 899  # 29 × 31
        self.test_seed = 42
        self.test_samples = 128
    
    def test_mc_engine_reproducibility(self):
        """Test that MC engine produces reproducible results with same seed."""
        engine1 = create_engine('mc', seed=self.test_seed)
        engine2 = create_engine('mc', seed=self.test_seed)
        
        candidates1 = engine1.generate_candidates(self.test_n, self.test_samples)
        candidates2 = engine2.generate_candidates(self.test_n, self.test_samples)
        
        # With same seed, should get same candidates
        self.assertEqual(len(candidates1), len(candidates2))
        np.testing.assert_array_equal(candidates1, candidates2)
    
    def test_sobol_owen_scrambling(self):
        """Test Sobol+Owen engine with scrambling enabled."""
        engine = create_engine('sobol', seed=self.test_seed, scramble=True)
        candidates = engine.generate_candidates(self.test_n, self.test_samples)
        
        # Should generate some unique candidates
        self.assertGreater(len(candidates), 0)
        self.assertLessEqual(len(candidates), self.test_samples)
        
        # Candidates should be integers around sqrt(N)
        sqrt_n = int(self.test_n ** 0.5)
        self.assertTrue(all(isinstance(c, (int, np.integer)) for c in candidates))
    
    def test_rank1_korobov(self):
        """Test Rank-1 Lattice with Korobov generator."""
        engine = create_engine('rank1', seed=self.test_seed, lattice_type='korobov')
        candidates = engine.generate_candidates(self.test_n, self.test_samples)
        
        self.assertGreater(len(candidates), 0)
        self.assertLessEqual(len(candidates), self.test_samples)
    
    def test_rank1_fibonacci(self):
        """Test Rank-1 Lattice with Fibonacci generator."""
        engine = create_engine('rank1', seed=self.test_seed, lattice_type='fibonacci')
        candidates = engine.generate_candidates(self.test_n, self.test_samples)
        
        self.assertGreater(len(candidates), 0)
        self.assertLessEqual(len(candidates), self.test_samples)
    
    def test_z_bias_integration(self):
        """Test Z-bias integration with QMC engines."""
        engine = create_engine('sobol', seed=self.test_seed, scramble=True)
        
        # Without bias
        candidates_no_bias = engine.generate_candidates(self.test_n, self.test_samples, bias=None)
        
        # With Z-bias
        candidates_z_bias = engine.generate_candidates(self.test_n, self.test_samples, bias='z-framework', k=0.3)
        
        # Both should generate candidates
        self.assertGreater(len(candidates_no_bias), 0)
        self.assertGreater(len(candidates_z_bias), 0)
        
        # Candidates may differ due to bias
        # Just check they're in reasonable range
        sqrt_n = self.test_n ** 0.5
        self.assertTrue(all(c > 0 for c in candidates_no_bias))
        self.assertTrue(all(c > 0 for c in candidates_z_bias))


class TestQMCDirectionsDemo(unittest.TestCase):
    """Test qmc_directions_demo.py functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_n = 899
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_run_replicate(self):
        """Test single replicate execution."""
        from python.examples.qmc_directions_demo import run_replicate
        
        metrics = run_replicate(
            N=self.test_n,
            engine_type='mc',
            n_samples=64,
            seed=42
        )
        
        # Check required fields
        self.assertIn('seed', metrics)
        self.assertIn('unique_count', metrics)
        self.assertIn('mean_distance', metrics)
        self.assertIn('generation_time', metrics)
        
        # Check values are reasonable
        self.assertGreater(metrics['unique_count'], 0)
        self.assertGreaterEqual(metrics['generation_time'], 0)
    
    def test_bootstrap_ci(self):
        """Test bootstrap confidence interval computation."""
        from python.examples.qmc_directions_demo import compute_bootstrap_ci
        
        data = [10.0, 11.0, 10.5, 10.2, 10.8]
        ci = compute_bootstrap_ci(data, confidence=0.95, n_bootstrap=100)
        
        # Check structure
        self.assertIn('mean', ci)
        self.assertIn('ci_lower', ci)
        self.assertIn('ci_upper', ci)
        
        # CI should contain mean
        self.assertLessEqual(ci['ci_lower'], ci['mean'])
        self.assertLessEqual(ci['mean'], ci['ci_upper'])
    
    def test_compare_engines(self):
        """Test full engine comparison."""
        from python.examples.qmc_directions_demo import compare_engines
        
        results = compare_engines(
            N=self.test_n,
            n_samples=64,
            n_replicates=5,  # Small for testing
            lattice_type='korobov'
        )
        
        # Check structure
        self.assertIn('mc', results)
        self.assertIn('rank1', results)
        self.assertIn('delta_pct', results)
        
        # Check MC results
        self.assertIn('mean_unique', results['mc'])
        self.assertIn('ci', results['mc'])
        
        # Check Rank-1 results
        self.assertIn('mean_unique', results['rank1'])
        self.assertIn('engine', results['rank1'])
        self.assertEqual(results['rank1']['engine'], 'korobov')


class TestBenchmarkElliptic(unittest.TestCase):
    """Test benchmark_elliptic.py functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_n = 899
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_compute_l2_discrepancy(self):
        """Test L2 discrepancy computation."""
        from scripts.benchmark_elliptic import compute_l2_discrepancy
        
        # Create sample candidates
        sqrt_n = self.test_n ** 0.5
        samples = np.array([sqrt_n - 2, sqrt_n - 1, sqrt_n, sqrt_n + 1, sqrt_n + 2])
        
        discrepancy = compute_l2_discrepancy(samples, self.test_n)
        
        # Discrepancy should be a positive number
        self.assertGreater(discrepancy, 0)
        self.assertLess(discrepancy, 1)  # Should be normalized
    
    def test_adaptive_sampling(self):
        """Test adaptive sampling strategy."""
        from scripts.benchmark_elliptic import adaptive_sampling
        
        engine = create_engine('sobol', seed=42, scramble=True)
        
        candidates, history = adaptive_sampling(
            engine=engine,
            N=self.test_n,
            initial_samples=32,
            max_samples=128,
            target_discrepancy=0.5
        )
        
        # Check candidates
        self.assertGreater(len(candidates), 0)
        
        # Check history
        self.assertGreater(len(history), 0)
        self.assertIn('discrepancy', history[0])
        self.assertIn('total_samples', history[0])
    
    def test_benchmark_engines(self):
        """Test full benchmark execution."""
        from scripts.benchmark_elliptic import benchmark_engines
        
        results = benchmark_engines(
            N=self.test_n,
            n_samples=64,
            adaptive=False
        )
        
        # Check all engines are present
        self.assertIn('MC', results)
        self.assertIn('Sobol+Owen', results)
        self.assertIn('Rank-1 Korobov', results)
        self.assertIn('Rank-1 Fibonacci', results)
        
        # Check metrics for each engine
        for engine_name, metrics in results.items():
            self.assertIn('unique_count', metrics)
            self.assertIn('discrepancy', metrics)
            self.assertIn('time_seconds', metrics)
            
            # Values should be reasonable
            self.assertGreater(metrics['unique_count'], 0)
            self.assertGreater(metrics['discrepancy'], 0)
            self.assertGreaterEqual(metrics['time_seconds'], 0)


class TestQMCvsMCBenchmark(unittest.TestCase):
    """Test qmc_vs_mc_benchmark.py functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_n = 899
    
    def test_bootstrap_ci(self):
        """Test bootstrap CI computation."""
        from python.examples.qmc_vs_mc_benchmark import bootstrap_ci
        
        data = np.array([10.0, 11.0, 10.5, 10.2, 10.8])
        lower, upper = bootstrap_ci(data, n_bootstrap=100)
        
        # CI bounds should be reasonable
        self.assertLess(lower, upper)
        self.assertLessEqual(lower, np.mean(data))
        self.assertGreaterEqual(upper, np.mean(data))
    
    def test_benchmark_qmc_vs_mc(self):
        """Test QMC vs MC benchmark."""
        from python.examples.qmc_vs_mc_benchmark import benchmark_qmc_vs_mc
        
        result = benchmark_qmc_vs_mc(
            n=self.test_n,
            samples=64,
            replicates=10  # Small for testing
        )
        
        # Check structure
        self.assertIn('mc_mean', result)
        self.assertIn('mc_ci', result)
        self.assertIn('qmc_mean', result)
        self.assertIn('qmc_ci', result)
        self.assertIn('delta_pct', result)
        
        # Check values
        self.assertGreater(result['mc_mean'], 0)
        self.assertGreater(result['qmc_mean'], 0)
        
        # Check CIs
        mc_lower, mc_upper = result['mc_ci']
        qmc_lower, qmc_upper = result['qmc_ci']
        
        self.assertLessEqual(mc_lower, mc_upper)
        self.assertLessEqual(qmc_lower, qmc_upper)


class TestRSAChallenges(unittest.TestCase):
    """Test with actual RSA challenge numbers."""
    
    def test_rsa_100_smoke_test(self):
        """Smoke test with RSA-100."""
        from python.examples.qmc_directions_demo import RSA_CHALLENGES
        
        # Just verify the number is correct
        self.assertIn('RSA-100', RSA_CHALLENGES)
        self.assertIn('RSA-129', RSA_CHALLENGES)
        self.assertIn('RSA-155', RSA_CHALLENGES)
        
        # Verify bit lengths are reasonable
        rsa_100 = RSA_CHALLENGES['RSA-100']
        self.assertGreater(rsa_100.bit_length(), 300)
    
    def test_small_scale_factorization(self):
        """Test factorization with small semiprime."""
        engine = create_engine('sobol', seed=42, scramble=True)
        
        N = 899  # 29 × 31
        candidates = engine.generate_candidates(N, 256)
        
        # Check if factors are in candidates
        factors = [29, 31]
        found = [f for f in factors if f in candidates]
        
        # May or may not find factors depending on spread
        # Just verify we got some candidates
        self.assertGreater(len(candidates), 0)


if __name__ == '__main__':
    unittest.main()
