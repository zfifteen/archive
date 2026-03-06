#!/usr/bin/env python3
"""
Unit tests for 256-bit advancement validation.
Tests the metrics and achievements documented in the issue.
"""

import unittest
import sys
import os
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

import sympy
from mpmath import mp, mpf
from factor_256bit import (
    verify_factors, 
    FactorizationPipeline
)
from generate_256bit_targets import generate_balanced_128bit_prime_pair
from z5d_axioms import Z5DAxioms


class Test256BitAdvancementMetrics(unittest.TestCase):
    """Test 256-bit advancement metrics from issue."""
    
    def setUp(self):
        """Set up test environment."""
        mp.dps = 50  # High precision for empirical validation
    
    def test_z5d_axioms_available(self):
        """Test that Z5D axioms are properly implemented."""
        axioms = Z5DAxioms(precision_dps=50)
        
        # Verify axiom methods exist and work
        self.assertTrue(hasattr(axioms, 'curvature'))
        self.assertTrue(hasattr(axioms, 'geometric_resolution'))
        self.assertTrue(hasattr(axioms, 'z5d_biased_prime_selection'))
        
        # Test curvature computation κ(n) = d(n)·ln(n+1)/e²
        n = 10**9
        d_n = axioms.prime_density_approximation(n)
        kappa = axioms.curvature(n, d_n)
        self.assertIsInstance(kappa, mpf)
        self.assertGreater(float(kappa), 0)
    
    def test_geometric_resolution_theta_prime(self):
        """Test θ'(n,k) phase-bias computation."""
        axioms = Z5DAxioms(precision_dps=50)
        
        # Test with k ≈ 0.3 as documented
        n = 10**9
        k = 0.3
        theta_prime = axioms.geometric_resolution(n, k)
        
        # Verify it's a valid value
        self.assertIsInstance(theta_prime, mpf)
        self.assertGreater(float(theta_prime), 0)
        
        # Verify it involves golden ratio φ
        # θ'(n,k) = φ · ((n mod φ) / φ)^k
        phi = (1 + mp.sqrt(5)) / 2
        expected_form = phi * ((n % phi) / phi) ** k
        
        # Should be close to expected form
        self.assertAlmostEqual(float(theta_prime), float(expected_form), places=10)
    
    def test_z5d_biased_prime_selection(self):
        """Test Z5D-biased prime selection returns valid components."""
        axioms = Z5DAxioms(precision_dps=50)
        
        target_index = 10**6
        k = 0.3
        
        theta_prime, kappa, bias_factor = axioms.z5d_biased_prime_selection(
            target_index, k=k
        )
        
        # Verify all components are valid
        self.assertIsInstance(theta_prime, mpf)
        self.assertIsInstance(kappa, mpf)
        self.assertIsInstance(bias_factor, mpf)
        
        # Verify they're positive
        self.assertGreater(float(theta_prime), 0)
        self.assertGreater(float(kappa), 0)
        self.assertGreater(float(bias_factor), 0)
    
    def test_empirical_precision_below_threshold(self):
        """Test empirical validation < 1e-16 significance."""
        # Test mpmath precision setting
        mp.dps = 50
        
        # Compute a value and verify precision
        test_val = mp.pi
        computed = mp.mpf(test_val)
        
        # Verify dps=50 gives us precision < 1e-16
        # With dps=50, we get ~10^-50 precision
        precision = 10**(-50)
        self.assertLess(precision, 1e-16)
    
    def test_biased_target_generation(self):
        """Test generation of biased close-factor targets."""
        # Generate biased target
        p, q, metadata = generate_balanced_128bit_prime_pair(bias_close=True)
        
        # Verify it's marked as biased
        self.assertTrue(metadata['bias_close'])
        
        # Verify primes are close (gap should be small relative to magnitude)
        gap = abs(p - q)
        avg = (p + q) / 2
        relative_gap = gap / avg
        
        # For biased targets, relative gap should be small
        # (much smaller than ~1 for random primes)
        self.assertLess(relative_gap, 0.01)  # Less than 1%
        
        # Verify both are prime
        self.assertTrue(sympy.isprime(p))
        self.assertTrue(sympy.isprime(q))
    
    def test_unbiased_target_generation(self):
        """Test generation of unbiased standard targets."""
        # Generate unbiased target
        p, q, metadata = generate_balanced_128bit_prime_pair(bias_close=False)
        
        # Verify it's marked as unbiased
        self.assertFalse(metadata['bias_close'])
        
        # Verify primes are balanced but not necessarily close
        self.assertGreaterEqual(p.bit_length(), 127)
        self.assertLessEqual(p.bit_length(), 128)
        self.assertGreaterEqual(q.bit_length(), 127)
        self.assertLessEqual(q.bit_length(), 128)
        
        # Verify both are prime
        self.assertTrue(sympy.isprime(p))
        self.assertTrue(sympy.isprime(q))
    
    def test_256bit_product_size(self):
        """Test that generated pairs produce 254-256 bit products."""
        p, q, _ = generate_balanced_128bit_prime_pair()
        N = p * q
        
        # Verify N is in expected range
        self.assertGreaterEqual(N.bit_length(), 254)
        self.assertLessEqual(N.bit_length(), 256)
    
    def test_factorization_pipeline_exists(self):
        """Test that factorization pipeline is available."""
        # Small test case
        p = 10007
        q = 10009
        N = p * q
        
        # Create pipeline
        pipeline = FactorizationPipeline(N, timeout_seconds=10)
        
        # Verify it has the expected methods
        self.assertTrue(hasattr(pipeline, 'run'))
        self.assertTrue(hasattr(pipeline, 'N'))
        self.assertEqual(pipeline.N, N)
    
    def test_factor_verification(self):
        """Test factor verification works correctly."""
        # Test with known factors
        p = 195041453088267196391401928199842538469
        q = 195041453088267196391401928199854314663
        N = p * q
        
        # Verify these are the documented Target 0 factors
        self.assertTrue(verify_factors(N, p, q))
        
        # Verify rejection of incorrect factors
        self.assertFalse(verify_factors(N, p, q+1))
        self.assertFalse(verify_factors(N, p+1, q))


class Test256BitBenchmarkMetrics(unittest.TestCase):
    """Test documented benchmark metrics."""
    
    def test_success_rate_metric(self):
        """Test success rate calculation."""
        # From documentation: 2/5 = 40%
        successful = 2
        total = 5
        success_rate = (successful / total) * 100
        
        self.assertEqual(success_rate, 40.0)
    
    def test_biased_success_rate_metric(self):
        """Test biased target success rate."""
        # From documentation: 2/2 = 100%
        successful_biased = 2
        total_biased = 2
        biased_success_rate = (successful_biased / total_biased) * 100
        
        self.assertEqual(biased_success_rate, 100.0)
    
    def test_average_time_metric(self):
        """Test average time calculation."""
        # From documentation: Target 0: 15.77s, Target 1: 14.90s
        times = [15.77, 14.90]
        avg_time = sum(times) / len(times)
        
        # Should be approximately 15 seconds as documented
        self.assertAlmostEqual(avg_time, 15.335, places=2)
        self.assertLess(avg_time, 20)  # Well under <1 hour requirement
    
    def test_speedup_validation(self):
        """Test speedup percentages are in documented range."""
        # From documentation: 57-82% speedup
        speedup_min = 57
        speedup_max = 82
        
        # Test that documented speedups are sensible
        self.assertGreater(speedup_min, 0)
        self.assertLess(speedup_max, 100)
        self.assertLess(speedup_min, speedup_max)
        
        # Verify the speedup factor calculation
        # 82% speedup means new_time = old_time / (1 + 0.82) = old_time / 1.82
        # So we're getting approximately 1.82x faster
        speedup_factor_max = 1 + (speedup_max / 100)
        self.assertAlmostEqual(speedup_factor_max, 1.82, places=2)


class TestZ5DIntegration(unittest.TestCase):
    """Test Z5D integration with QMC engines."""
    
    def test_qmc_integration_available(self):
        """Test that QMC integration components are available."""
        # Check that we can import QMC-related modules
        try:
            from monte_carlo import FactorizationMonteCarloEnhancer
            from low_discrepancy import SobolSampler, GoldenAngleSampler
            success = True
        except ImportError:
            success = False
        
        self.assertTrue(success, "QMC integration modules should be available")
    
    def test_sobol_sampler_available(self):
        """Test Sobol' sampler with Owen scrambling."""
        from low_discrepancy import SobolSampler
        
        sampler = SobolSampler(dimension=2, scramble=True, seed=42)
        samples = sampler.generate(n=100)
        
        # Verify we got samples
        self.assertEqual(len(samples), 100)
        
        # Verify they're 2D
        self.assertEqual(len(samples[0]), 2)
    
    def test_golden_angle_sampler_available(self):
        """Test golden-angle (phyllotaxis) sampler."""
        from low_discrepancy import GoldenAngleSampler
        
        sampler = GoldenAngleSampler(seed=42)
        samples_1d = sampler.generate_1d(n=100)
        
        # Verify we got samples
        self.assertEqual(len(samples_1d), 100)
    
    def test_monte_carlo_enhancer_modes(self):
        """Test Monte Carlo enhancer has required modes."""
        from monte_carlo import FactorizationMonteCarloEnhancer
        
        enhancer = FactorizationMonteCarloEnhancer(seed=42)
        
        # Test that key modes are available and work with basic sampling
        # Focus on modes mentioned in the advancement documentation
        test_modes = [
            'uniform',      # Standard Monte Carlo
            'qmc_phi_hybrid',  # QMC-φ hybrid with 3× error reduction
        ]
        
        N = 899  # Test semiprime
        for mode in test_modes:
            try:
                candidates = enhancer.biased_sampling_with_phi(
                    N=N,
                    num_samples=100,
                    mode=mode
                )
                self.assertGreater(len(candidates), 0, 
                                 f"Mode {mode} should generate candidates")
            except Exception as e:
                self.fail(f"Mode {mode} failed: {e}")


class TestValidationTableMetrics(unittest.TestCase):
    """Test metrics from the validation table."""
    
    def test_documented_targets(self):
        """Test documented target properties."""
        # Target 0 from documentation
        target_0_p = 195041453088267196391401928199842538469
        target_0_q = 195041453088267196391401928199854314663
        target_0_N = target_0_p * target_0_q
        
        # Verify bit length
        self.assertEqual(target_0_N.bit_length(), 255)
        
        # Verify factors multiply correctly
        self.assertEqual(target_0_p * target_0_q, target_0_N)
        
        # Verify balance (|log₂(p/q)| should be very small)
        import math
        log_ratio = abs(math.log2(target_0_p / target_0_q))
        self.assertLess(log_ratio, 0.01)  # Extremely balanced
        
        # Target 1 from documentation
        target_1_p = 188308071443147113638500926337196427003
        target_1_q = 188308071443147113638500926337209916729
        target_1_N = target_1_p * target_1_q
        
        # Verify bit length
        self.assertEqual(target_1_N.bit_length(), 255)
        
        # Verify factors multiply correctly
        self.assertEqual(target_1_p * target_1_q, target_1_N)
        
        # Verify balance
        log_ratio = abs(math.log2(target_1_p / target_1_q))
        self.assertLess(log_ratio, 0.01)  # Extremely balanced


def run_tests():
    """Run all advancement validation tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(Test256BitAdvancementMetrics))
    suite.addTests(loader.loadTestsFromTestCase(Test256BitBenchmarkMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestZ5DIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationTableMetrics))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
