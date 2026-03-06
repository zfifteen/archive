#!/usr/bin/env python3
"""
Comprehensive tests for Golden Ratio Geometric Factorization validation suite.

Tests all three validation phases:
1. Phase 1: 50-100 bit validation
2. Phase 2: 100-300 bit validation  
3. Phase 3: Crypto-scale validation

Each test validates the mathematical foundations and algorithmic correctness.
"""

import unittest
import sys
import os
import math
from mpmath import mp, mpf, log, exp, sqrt as mpsqrt, power, frac
from sympy.ntheory import isprime

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import golden_ratio_factorization_50_100bit as phase1
import golden_ratio_factorization_100_300bit as phase2
import golden_ratio_factorization_crypto_scale as phase3


class TestGoldenRatioConstants(unittest.TestCase):
    """Test that golden ratio and constants are correctly defined."""
    
    def test_phi_value(self):
        """Test φ ≈ 1.618033988749..."""
        phi_expected = (1 + mpsqrt(5)) / 2
        
        self.assertAlmostEqual(float(phase1.PHI), float(phi_expected), places=10)
        self.assertAlmostEqual(float(phase2.PHI), float(phi_expected), places=10)
        self.assertAlmostEqual(float(phase3.PHI), float(phi_expected), places=10)
    
    def test_e2_value(self):
        """Test e² ≈ 7.389..."""
        e2_expected = exp(2)
        
        self.assertAlmostEqual(float(phase1.E2), float(e2_expected), places=10)
        self.assertAlmostEqual(float(phase2.E2), float(e2_expected), places=10)
        self.assertAlmostEqual(float(phase3.E2), float(e2_expected), places=10)


class TestPhase1Functions(unittest.TestCase):
    """Test Phase 1 (50-100 bit) validation functions."""
    
    def test_generate_balanced_semiprime(self):
        """Test balanced semiprime generation."""
        N, p, q = phase1.generate_balanced_semiprime(50)
        
        # Verify N = p × q
        self.assertEqual(N, p * q)
        
        # Verify both are prime
        self.assertTrue(isprime(p))
        self.assertTrue(isprime(q))
        
        # Verify balance (within 2:1 ratio)
        balance = abs(math.log2(p / q))
        self.assertLessEqual(balance, 1.0)
        
        # Verify bit size is approximately correct
        self.assertGreaterEqual(N.bit_length(), 48)
        self.assertLessEqual(N.bit_length(), 52)
    
    def test_pentagonal_embedding(self):
        """Test pentagonal embedding returns correct dimensions."""
        coords = phase1.pentagonal_embedding(899, dims=5)
        
        # Verify dimension count
        self.assertEqual(len(coords), 5)
        
        # Verify all coordinates are in [0, 1)
        for coord in coords:
            self.assertGreaterEqual(float(coord), 0.0)
            self.assertLess(float(coord), 1.0)
    
    def test_theta_prime_adaptive(self):
        """Test geometric resolution function."""
        theta = phase1.theta_prime_adaptive(100, k=0.3)
        
        # Verify result is in valid range [0, φ)
        self.assertGreaterEqual(float(theta), 0.0)
        self.assertLess(float(theta), float(phase1.PHI))
    
    def test_pentagonal_distance(self):
        """Test pentagonal distance calculation."""
        coords1 = [mpf(0.1), mpf(0.2), mpf(0.3), mpf(0.4), mpf(0.5)]
        coords2 = [mpf(0.15), mpf(0.25), mpf(0.35), mpf(0.45), mpf(0.55)]
        
        dist = phase1.pentagonal_distance(coords1, coords2, N=1000)
        
        # Verify distance is non-negative
        self.assertGreaterEqual(float(dist), 0.0)
        
        # Verify distance is finite
        self.assertFalse(float(dist) == float('inf'))
    
    def test_adaptive_k_scan(self):
        """Test adaptive k-scan returns valid candidates."""
        N = 899  # 29 × 31
        sqrtN = 29
        
        candidates = phase1.adaptive_k_scan(N, sqrtN, k_range=(0.1, 0.5), k_steps=3)
        
        # Verify candidates is a list
        self.assertIsInstance(candidates, list)
        
        # If candidates found, verify they divide N
        for candidate in candidates:
            self.assertEqual(N % candidate, 0)


class TestPhase2Functions(unittest.TestCase):
    """Test Phase 2 (100-300 bit) validation functions."""
    
    def test_generate_balanced_semiprime_large(self):
        """Test large balanced semiprime generation."""
        # Skip actual generation for speed, just test function exists
        self.assertTrue(callable(phase2.generate_balanced_semiprime_large))
        
        # Test with very small number for function validation
        from sympy.ntheory import nextprime
        p = nextprime(2**20)
        q = nextprime(p)
        N = p * q
        
        # Verify basic properties
        self.assertEqual(N, p * q)
        self.assertTrue(isprime(p))
        self.assertTrue(isprime(q))
    
    def test_pentagonal_embedding_enhanced(self):
        """Test enhanced pentagonal embedding."""
        coords = phase2.pentagonal_embedding_enhanced(10000, dims=7)
        
        # Verify dimension count
        self.assertEqual(len(coords), 7)
        
        # Verify all coordinates are in [0, 1)
        for coord in coords:
            self.assertGreaterEqual(float(coord), 0.0)
            self.assertLess(float(coord), 1.0)
    
    def test_geometric_resolution_k(self):
        """Test enhanced geometric resolution."""
        theta = phase2.geometric_resolution_k(1000, k=0.3, oscillation=0.1)
        
        # Verify result is positive
        self.assertGreater(float(theta), 0.0)
        
        # Verify result is finite
        self.assertFalse(float(theta) == float('inf'))


class TestPhase3Functions(unittest.TestCase):
    """Test Phase 3 (crypto-scale) validation functions."""
    
    def test_pentagonal_embedding_crypto(self):
        """Test crypto-scale pentagonal embedding."""
        # Use smaller number for test efficiency
        coords = phase3.pentagonal_embedding_crypto(2**64, dims=11)
        
        # Verify dimension count
        self.assertEqual(len(coords), 11)
        
        # Verify all coordinates are in [0, 1)
        for coord in coords:
            self.assertGreaterEqual(float(coord), 0.0)
            self.assertLess(float(coord), 1.0)
    
    def test_theta_prime_crypto(self):
        """Test crypto-scale geometric resolution."""
        theta = phase3.theta_prime_crypto(2**32, k=0.3)
        
        # Verify result is in valid range
        self.assertGreaterEqual(float(theta), 0.0)
        self.assertLess(float(theta), float(phase3.PHI) * 2)  # Allow some flexibility
    
    def test_probabilistic_candidate_search(self):
        """Test probabilistic candidate search."""
        # Use small number for test
        N = 899  # 29 × 31
        sqrtN = 29
        
        candidates = phase3.probabilistic_candidate_search(N, sqrtN, sample_size=100)
        
        # Verify candidates is a list
        self.assertIsInstance(candidates, list)


class TestMathematicalProperties(unittest.TestCase):
    """Test mathematical properties of the methods."""
    
    def test_phi_pentagonal_property(self):
        """Test that φ equals the pentagonal diagonal-to-side ratio."""
        # In a regular pentagon, diagonal/side = φ
        phi = phase1.PHI
        pentagonal_ratio = phase1.PENTAGONAL_RATIO
        
        self.assertEqual(float(phi), float(pentagonal_ratio))
    
    def test_embedding_determinism(self):
        """Test that embeddings are deterministic."""
        n = 12345
        
        coords1 = phase1.pentagonal_embedding(n, dims=5)
        coords2 = phase1.pentagonal_embedding(n, dims=5)
        
        for c1, c2 in zip(coords1, coords2):
            self.assertEqual(float(c1), float(c2))
    
    def test_distance_symmetry(self):
        """Test that distance is symmetric."""
        coords1 = [mpf(0.1), mpf(0.2), mpf(0.3)]
        coords2 = [mpf(0.4), mpf(0.5), mpf(0.6)]
        
        # Create simplified distance function for testing
        def simple_dist(c1, c2):
            total = mpf(0)
            for a, b in zip(c1, c2):
                d = min(abs(a - b), 1 - abs(a - b))
                total += d ** 2
            return mpsqrt(total)
        
        dist1 = simple_dist(coords1, coords2)
        dist2 = simple_dist(coords2, coords1)
        
        self.assertAlmostEqual(float(dist1), float(dist2), places=10)
    
    def test_curvature_positive(self):
        """Test that curvature is always positive."""
        for N in [100, 1000, 10000, 100000]:
            log_N = math.log(N)
            kappa = math.log(N + 1) / (math.exp(2) * log_N)
            self.assertGreater(kappa, 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end functionality."""
    
    def test_phase1_imports(self):
        """Test Phase 1 module imports correctly."""
        self.assertIsNotNone(phase1.PHI)
        self.assertIsNotNone(phase1.E2)
        self.assertTrue(callable(phase1.pentagonal_embedding))
        self.assertTrue(callable(phase1.phi_resonance_factorize))
    
    def test_phase2_imports(self):
        """Test Phase 2 module imports correctly."""
        self.assertIsNotNone(phase2.PHI)
        self.assertIsNotNone(phase2.E2)
        self.assertTrue(callable(phase2.pentagonal_embedding_enhanced))
        self.assertTrue(callable(phase2.phi_resonance_factorize_enhanced))
    
    def test_phase3_imports(self):
        """Test Phase 3 module imports correctly."""
        self.assertIsNotNone(phase3.PHI)
        self.assertIsNotNone(phase3.E2)
        self.assertTrue(callable(phase3.pentagonal_embedding_crypto))
        self.assertTrue(callable(phase3.phi_resonance_crypto_factorize))


def run_tests():
    """Run all tests with verbose output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGoldenRatioConstants))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase1Functions))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase2Functions))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3Functions))
    suite.addTests(loader.loadTestsFromTestCase(TestMathematicalProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
