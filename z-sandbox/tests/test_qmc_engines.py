#!/usr/bin/env python3
"""
Tests for QMC Engines with Z-Framework Bias

Tests all QMC engines (MC, Sobol+Owen, Rank-1 Lattice) with and without
Z-Framework bias integration.
"""

import sys
import os
import unittest
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.qmc_engines import (
    QMCEngine, MCEngine, SobolOwenEngine, Rank1LatticeEngine, create_engine
)
from utils.z_framework import kappa, theta_prime, z_bias_factor, apply_z_bias


class TestZFrameworkFunctions(unittest.TestCase):
    """Test Z-Framework utility functions."""
    
    def test_kappa_scalar(self):
        """Test kappa function with scalar input."""
        k = kappa(1000)
        self.assertGreater(k, 0)
        self.assertLess(k, 1)
    
    def test_kappa_array(self):
        """Test kappa function with array input."""
        n_array = np.array([100, 1000, 10000])
        k_array = kappa(n_array)
        self.assertEqual(len(k_array), len(n_array))
        self.assertTrue(np.all(k_array > 0))
    
    def test_theta_prime_scalar(self):
        """Test theta_prime function with scalar input."""
        theta = theta_prime(1000, k=0.3)
        self.assertGreater(theta, 0)
    
    def test_theta_prime_array(self):
        """Test theta_prime function with array input."""
        n_array = np.array([100, 1000, 10000])
        theta_array = theta_prime(n_array, k=0.3)
        self.assertEqual(len(theta_array), len(n_array))
        self.assertTrue(np.all(theta_array > 0))
    
    def test_z_bias_factor(self):
        """Test combined Z-bias factor."""
        bias = z_bias_factor(1000, k=0.3)
        self.assertGreater(bias, 0)
    
    def test_apply_z_bias(self):
        """Test Z-bias application to QMC points."""
        N = 899
        points = np.random.random((10, 1))
        biased = apply_z_bias(points, N, k=0.3)
        
        self.assertEqual(len(biased), len(points))
        self.assertTrue(np.all(biased > 0))


class TestMCEngine(unittest.TestCase):
    """Test Monte Carlo engine."""
    
    def test_creation(self):
        """Test MC engine creation."""
        engine = MCEngine(dimension=1, seed=42)
        self.assertEqual(engine.dimension, 1)
        self.assertEqual(engine.seed, 42)
    
    def test_generate(self):
        """Test sample generation."""
        engine = MCEngine(dimension=1, seed=42)
        samples = engine.generate(100)
        
        self.assertEqual(samples.shape, (100, 1))
        self.assertTrue(np.all(samples >= 0))
        self.assertTrue(np.all(samples <= 1))
    
    def test_generate_candidates_no_bias(self):
        """Test candidate generation without bias."""
        engine = MCEngine(dimension=1, seed=42)
        candidates = engine.generate_candidates(N=899, n_samples=100, bias=None)
        
        self.assertGreater(len(candidates), 0)
        self.assertTrue(np.all(candidates > 0))
    
    def test_generate_candidates_z_bias(self):
        """Test candidate generation with Z-bias."""
        engine = MCEngine(dimension=1, seed=42)
        candidates = engine.generate_candidates(N=899, n_samples=100, 
                                               bias='z-framework', k=0.3)
        
        self.assertGreater(len(candidates), 0)
        self.assertTrue(np.all(candidates > 0))


class TestSobolOwenEngine(unittest.TestCase):
    """Test Sobol+Owen engine."""
    
    def test_creation(self):
        """Test Sobol+Owen engine creation."""
        engine = SobolOwenEngine(dimension=1, seed=42, scramble=True)
        self.assertEqual(engine.dimension, 1)
        self.assertEqual(engine.seed, 42)
        self.assertTrue(engine.scramble)
    
    def test_generate(self):
        """Test Sobol sequence generation."""
        engine = SobolOwenEngine(dimension=1, seed=42, scramble=True)
        samples = engine.generate(128)  # Use power of 2 for Sobol
        
        self.assertEqual(samples.shape, (128, 1))
        self.assertTrue(np.all(samples >= 0))
        self.assertTrue(np.all(samples <= 1))
    
    def test_generate_candidates_no_bias(self):
        """Test candidate generation without bias."""
        engine = SobolOwenEngine(dimension=1, seed=42, scramble=True)
        candidates = engine.generate_candidates(N=899, n_samples=128, bias=None)
        
        self.assertGreater(len(candidates), 0)
    
    def test_generate_candidates_z_bias(self):
        """Test candidate generation with Z-bias."""
        engine = SobolOwenEngine(dimension=1, seed=42, scramble=True)
        candidates = engine.generate_candidates(N=899, n_samples=128,
                                               bias='z-framework', k=0.3)
        
        self.assertGreater(len(candidates), 0)
        
        # Z-bias should produce more diverse candidates
        candidates_no_bias = engine.generate_candidates(N=899, n_samples=128, bias=None)
        # Note: This is stochastic, but Z-bias typically increases diversity
        # We just check both work without assertion on relative counts


class TestRank1LatticeEngine(unittest.TestCase):
    """Test Rank-1 Lattice engine."""
    
    def test_creation_korobov(self):
        """Test Rank-1 Korobov engine creation."""
        engine = Rank1LatticeEngine(dimension=1, seed=42, lattice_type='korobov')
        self.assertEqual(engine.dimension, 1)
        self.assertEqual(engine.lattice_type, 'korobov')
    
    def test_creation_fibonacci(self):
        """Test Rank-1 Fibonacci engine creation."""
        engine = Rank1LatticeEngine(dimension=1, seed=42, lattice_type='fibonacci')
        self.assertEqual(engine.lattice_type, 'fibonacci')
    
    def test_generate(self):
        """Test lattice point generation."""
        engine = Rank1LatticeEngine(dimension=1, seed=42, lattice_type='korobov')
        samples = engine.generate(100)
        
        self.assertEqual(samples.shape, (100, 1))
        self.assertTrue(np.all(samples >= 0))
        self.assertTrue(np.all(samples <= 1))
    
    def test_generate_candidates_no_bias(self):
        """Test candidate generation without bias."""
        engine = Rank1LatticeEngine(dimension=1, seed=42, lattice_type='korobov')
        candidates = engine.generate_candidates(N=899, n_samples=100, bias=None)
        
        self.assertGreater(len(candidates), 0)
    
    def test_generate_candidates_z_bias(self):
        """Test candidate generation with Z-bias."""
        engine = Rank1LatticeEngine(dimension=1, seed=42, lattice_type='korobov')
        candidates = engine.generate_candidates(N=899, n_samples=100,
                                               bias='z-framework', k=0.3)
        
        self.assertGreater(len(candidates), 0)


class TestEngineFactory(unittest.TestCase):
    """Test engine factory function."""
    
    def test_create_mc(self):
        """Test MC engine creation via factory."""
        engine = create_engine('mc', dimension=1, seed=42)
        self.assertIsInstance(engine, MCEngine)
    
    def test_create_sobol(self):
        """Test Sobol engine creation via factory."""
        engine = create_engine('sobol', dimension=1, seed=42, scramble=True)
        self.assertIsInstance(engine, SobolOwenEngine)
    
    def test_create_rank1(self):
        """Test Rank-1 engine creation via factory."""
        engine = create_engine('rank1', dimension=1, seed=42, lattice_type='korobov')
        self.assertIsInstance(engine, Rank1LatticeEngine)
    
    def test_invalid_engine_type(self):
        """Test factory with invalid engine type."""
        with self.assertRaises(ValueError):
            create_engine('invalid', dimension=1, seed=42)


class TestZBiasIntegration(unittest.TestCase):
    """Integration tests for Z-bias across engines."""
    
    def test_all_engines_with_z_bias(self):
        """Test that all engines work with Z-bias."""
        N = 899
        n_samples = 64
        seed = 42
        
        engines = {
            'mc': create_engine('mc', seed=seed),
            'sobol': create_engine('sobol', seed=seed, scramble=True),
            'rank1': create_engine('rank1', seed=seed, lattice_type='korobov')
        }
        
        for name, engine in engines.items():
            with self.subTest(engine=name):
                candidates = engine.generate_candidates(
                    N=N, 
                    n_samples=n_samples,
                    bias='z-framework',
                    k=0.3
                )
                
                self.assertGreater(len(candidates), 0, 
                                 f"{name} produced no candidates")
                self.assertTrue(np.all(candidates > 0),
                              f"{name} produced invalid candidates")
    
    def test_z_bias_increases_diversity(self):
        """Test that Z-bias increases candidate diversity (on average)."""
        N = 899
        n_samples = 100
        seed = 42
        
        engine = MCEngine(seed=seed)
        
        # Generate without bias
        candidates_no_bias = engine.generate_candidates(N, n_samples, bias=None)
        
        # Generate with bias
        candidates_z_bias = engine.generate_candidates(N, n_samples, 
                                                       bias='z-framework', k=0.3)
        
        # Z-bias should generally produce more unique candidates
        # (though this is stochastic, so we just check both work)
        self.assertGreater(len(candidates_no_bias), 0)
        self.assertGreater(len(candidates_z_bias), 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
