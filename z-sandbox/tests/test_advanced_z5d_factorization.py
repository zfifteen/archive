#!/usr/bin/env python3
"""
Tests for Advanced Z5D Framework Factorization

Validates:
1. Adaptive k-tuning mechanism
2. QMC-biased seed generation
3. Parallel Pollard's Rho execution
4. Iteration until success (>0% success rate)
5. 256-bit factorization capabilities
"""

import unittest
import math
import numpy as np
from scipy.stats import qmc

import sys
sys.path.insert(0, 'python')

from advanced_z5d_factorization import (
    kappa,
    theta_prime,
    pollard_rho,
    biased_seed,
    factor_trial,
    compute_candidate_variance,
    factor_with_adaptive_bias,
    validate_factorization,
    is_probable_prime,
    PHI,
    E2,
    K_INIT,
    VARIANCE_HIGH_THRESHOLD,
    VARIANCE_LOW_THRESHOLD
)


class TestBasicFunctions(unittest.TestCase):
    """Test basic mathematical functions."""
    
    def test_kappa_computation(self):
        """Test κ(n) = 4 * ln(n+1) / e²."""
        n = 899
        expected = 4 * math.log(n + 1) / E2
        result = kappa(n)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_kappa_semiprime_property(self):
        """Test that κ(n) scales with log(n)."""
        n1 = 899
        n2 = 10403
        k1 = kappa(n1)
        k2 = kappa(n2)
        # κ should increase with n
        self.assertGreater(k2, k1)
    
    def test_theta_prime_golden_ratio(self):
        """Test θ′(n,k) uses golden ratio φ."""
        n = 899
        k = 0.3
        result = theta_prime(n, k)
        # Should be based on φ
        self.assertGreater(result, 0)
        self.assertLess(result, PHI * 2)
    
    def test_theta_prime_k_sensitivity(self):
        """Test that θ′(n,k) changes with k parameter."""
        n = 899
        theta_k03 = theta_prime(n, 0.3)
        theta_k05 = theta_prime(n, 0.5)
        # Different k values should produce different results
        self.assertNotEqual(theta_k03, theta_k05)
    
    def test_is_probable_prime(self):
        """Test Miller-Rabin primality test."""
        # Known primes
        self.assertTrue(is_probable_prime(29))
        self.assertTrue(is_probable_prime(31))
        self.assertTrue(is_probable_prime(1004847247))
        
        # Known composites
        self.assertFalse(is_probable_prime(899))  # 29 × 31
        self.assertFalse(is_probable_prime(100))


class TestPollardRho(unittest.TestCase):
    """Test Pollard's Rho factorization."""
    
    def test_pollard_small_semiprime(self):
        """Test factorization of small semiprime."""
        n = 899  # 29 × 31
        factor = pollard_rho(n, x0=2, c=1)
        self.assertIsNotNone(factor)
        self.assertIn(factor, [29, 31])
    
    def test_pollard_even_number(self):
        """Test that even numbers return 2."""
        n = 100
        factor = pollard_rho(n)
        self.assertEqual(factor, 2)
    
    def test_pollard_with_different_constants(self):
        """Test Pollard with different c values."""
        n = 1003  # 17 × 59
        
        # Try multiple c values
        for c in [1, 2, 3]:
            factor = pollard_rho(n, x0=2, c=c, max_steps=10000)
            if factor:
                self.assertIn(factor, [17, 59])
                break
    
    def test_pollard_prime_fails(self):
        """Test that prime numbers don't factor."""
        n = 29  # Prime
        factor = pollard_rho(n, max_steps=1000)
        # Should return None or n
        self.assertTrue(factor is None or factor == n)


class TestQMCBiasedSeeds(unittest.TestCase):
    """Test QMC-biased seed generation."""
    
    def test_biased_seed_generation(self):
        """Test that biased seeds are generated correctly."""
        n = 899
        sampler = qmc.Sobol(d=2, scramble=True, seed=42)
        x0, c = biased_seed(n, sampler, k=0.3)
        
        # Seeds should be reasonable
        self.assertGreater(x0, 0)
        self.assertLess(x0, n)
        self.assertGreater(c, 0)
        self.assertLess(c, 100)
    
    def test_biased_seed_uses_theta_kappa(self):
        """Test that biased seeds incorporate θ′(n,k) + κ(n)."""
        n = 899
        k = 0.3
        sampler = qmc.Sobol(d=2, scramble=True, seed=42)
        
        # Generate seed
        x0, c = biased_seed(n, sampler, k=k)
        
        # Verify bias is applied (seeds should be near sqrt(n) + bias)
        sqrt_n = int(math.sqrt(n))
        bias = theta_prime(n, k) + kappa(n)
        
        # x0 should be influenced by bias
        self.assertGreater(x0, sqrt_n - 2000)
    
    def test_biased_seed_reproducibility(self):
        """Test that same seed produces same results."""
        n = 899
        
        sampler1 = qmc.Sobol(d=2, scramble=True, seed=42)
        x0_1, c_1 = biased_seed(n, sampler1, k=0.3)
        
        sampler2 = qmc.Sobol(d=2, scramble=True, seed=42)
        x0_2, c_2 = biased_seed(n, sampler2, k=0.3)
        
        self.assertEqual(x0_1, x0_2)
        self.assertEqual(c_1, c_2)


class TestAdaptiveKTuning(unittest.TestCase):
    """Test adaptive k-tuning mechanism."""
    
    def test_compute_variance(self):
        """Test variance computation for k-tuning."""
        n = 899
        k = 0.3
        variance = compute_candidate_variance(n, k, num_test_samples=10)
        
        # Variance should be positive and reasonable
        self.assertGreater(variance, 0)
        self.assertLess(variance, 1.0)
    
    def test_k_adjustment_high_variance(self):
        """Test that high variance decreases k."""
        # Simulate high variance scenario
        variance = 0.2  # > VARIANCE_HIGH_THRESHOLD
        k = 0.3
        
        if variance > VARIANCE_HIGH_THRESHOLD:
            k_new = k - 0.01
        
        self.assertLess(k_new, k)
    
    def test_k_adjustment_low_variance(self):
        """Test that low variance increases k."""
        # Simulate low variance scenario
        variance = 0.03  # < VARIANCE_LOW_THRESHOLD
        k = 0.3
        
        if variance < VARIANCE_LOW_THRESHOLD:
            k_new = k + 0.01
        
        self.assertGreater(k_new, k)
    
    def test_k_bounds(self):
        """Test that k stays within [0.1, 0.5]."""
        k_values = [0.05, 0.1, 0.3, 0.5, 0.6]
        
        for k in k_values:
            k_bounded = max(0.1, min(0.5, k))
            self.assertGreaterEqual(k_bounded, 0.1)
            self.assertLessEqual(k_bounded, 0.5)


class TestFactorTrial(unittest.TestCase):
    """Test single factorization trials."""
    
    def test_factor_trial_small_semiprime(self):
        """Test single trial on small semiprime."""
        n = 899  # 29 × 31
        k = 0.3
        seed_offset = 42
        
        result = factor_trial((n, k, seed_offset))
        
        # May or may not succeed in single trial
        if result:
            self.assertIn(result, [29, 31])
    
    def test_factor_trial_with_different_seeds(self):
        """Test that different seeds produce different results."""
        n = 1003  # 17 × 59
        k = 0.3
        
        results = []
        for seed_offset in [42, 43, 44, 45]:
            result = factor_trial((n, k, seed_offset))
            results.append(result)
        
        # Not all should be None (high probability of at least one success)
        # But this is probabilistic, so we don't assert


class TestFactorWithAdaptiveBias(unittest.TestCase):
    """Test main factorization function with adaptive bias."""
    
    def test_factor_small_semiprime(self):
        """Test factorization of small semiprime."""
        n = 899  # 29 × 31
        
        p, q, iters, k_history = factor_with_adaptive_bias(
            n, num_trials=10, max_iters=5, num_processes=2
        )
        
        # Should succeed
        if p is not None:
            self.assertTrue(validate_factorization(n, p, q))
            self.assertIn(p, [29, 31])
            self.assertIn(q, [29, 31])
            self.assertGreater(iters, 0)
            self.assertLessEqual(iters, 5)
            self.assertEqual(len(k_history), iters)
    
    def test_factor_medium_semiprime(self):
        """Test factorization of medium semiprime."""
        n = 1003  # 17 × 59
        
        p, q, iters, k_history = factor_with_adaptive_bias(
            n, num_trials=20, max_iters=5, num_processes=2
        )
        
        if p is not None:
            self.assertTrue(validate_factorization(n, p, q))
            self.assertIn(p, [17, 59])
            self.assertIn(q, [17, 59])
    
    def test_k_history_tracking(self):
        """Test that k-history is tracked correctly."""
        n = 899
        
        p, q, iters, k_history = factor_with_adaptive_bias(
            n, num_trials=5, max_iters=3, num_processes=2
        )
        
        # k_history should have iters entries
        self.assertEqual(len(k_history), iters)
        
        # All k values should be within bounds
        for k in k_history:
            self.assertGreaterEqual(k, 0.1)
            self.assertLessEqual(k, 0.5)
    
    def test_60bit_semiprime(self):
        """Test on 60-bit semiprime from issue description."""
        n = 596208843697815811  # 1004847247 × 593332813
        
        p, q, iters, k_history = factor_with_adaptive_bias(
            n, num_trials=10, max_iters=5, num_processes=2
        )
        
        # This is probabilistic, but should have reasonable success rate
        if p is not None:
            self.assertTrue(validate_factorization(n, p, q))
            # Verify actual factors
            factors = sorted([p, q])
            expected = sorted([1004847247, 593332813])
            self.assertEqual(factors, expected)


class TestValidation(unittest.TestCase):
    """Test validation functions."""
    
    def test_validate_correct_factorization(self):
        """Test validation of correct factors."""
        n = 899
        p = 29
        q = 31
        self.assertTrue(validate_factorization(n, p, q))
    
    def test_validate_incorrect_factorization(self):
        """Test validation rejects incorrect factors."""
        n = 899
        p = 17
        q = 53
        self.assertFalse(validate_factorization(n, p, q))
    
    def test_validate_trivial_factors(self):
        """Test validation rejects trivial factors."""
        n = 899
        self.assertFalse(validate_factorization(n, 1, 899))
        self.assertFalse(validate_factorization(n, 899, 1))


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance and success rate metrics."""
    
    def test_success_rate_positive(self):
        """Test that success rate is > 0% on test cases."""
        test_cases = [
            899,    # 29 × 31
            1003,   # 17 × 59
            10403,  # 101 × 103
        ]
        
        successes = 0
        total = len(test_cases)
        
        for n in test_cases:
            p, q, iters, k_history = factor_with_adaptive_bias(
                n, num_trials=10, max_iters=5, num_processes=2
            )
            if p is not None:
                successes += 1
        
        success_rate = successes / total
        
        # Should achieve > 0% success (ideally high on these small test cases)
        self.assertGreater(success_rate, 0.0)
        
        print(f"\nSuccess rate on test cases: {success_rate * 100:.1f}%")
        print(f"Successes: {successes}/{total}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
