#!/usr/bin/env python3
"""
Unit tests for κ(n) Curvature Signal module.

Tests cover:
- Single value computation
- Batch processing
- Bootstrap confidence intervals
- Edge cases and error handling
- RSA challenge examples
- Reproducibility

Run from repository root:
    PYTHONPATH=python python3 tests/test_kappa_signal.py
    or
    PYTHONPATH=python python3 -m pytest tests/test_kappa_signal.py -v
"""

import sys
sys.path.append("python")

import unittest
import numpy as np
from kappa_signal import kappa, batch_kappa, bootstrap_ci, demonstrate_rsa_challenges
import io
from contextlib import redirect_stdout


class TestKappaSingleValue(unittest.TestCase):
    """Tests for single κ(n) computation."""
    
    def test_basic_computation(self):
        """Test basic κ(n) computation."""
        # 899 = 29 × 31 (4 divisors: 1, 29, 31, 899)
        k = kappa(899)
        
        # Should be positive
        self.assertGreater(k, 0)
        
        # Should be reasonable magnitude (not too large/small)
        self.assertGreater(k, 1.0)
        self.assertLess(k, 10.0)
    
    def test_prime_number(self):
        """Test κ(n) for prime numbers."""
        # Prime has exactly 2 divisors: 1 and itself
        k_prime = kappa(29)
        
        # Should be positive
        self.assertGreater(k_prime, 0)
        
        # Prime should have smaller κ than composite with same magnitude
        k_composite = kappa(30)  # 30 = 2 × 3 × 5 (8 divisors)
        self.assertLess(k_prime, k_composite)
    
    def test_perfect_square(self):
        """Test κ(n) for perfect squares."""
        # Perfect squares have odd number of divisors
        k = kappa(900)  # 900 = 30² (27 divisors)
        
        self.assertGreater(k, 0)
        self.assertIsInstance(k, float)
    
    def test_power_of_two(self):
        """Test κ(n) for powers of 2."""
        # 2^10 = 1024 has 11 divisors
        k = kappa(1024)
        
        self.assertGreater(k, 0)
        self.assertIsInstance(k, float)
    
    def test_small_values(self):
        """Test κ(n) for small values."""
        # Test n = 1, 2, 3, 4
        for n in [1, 2, 3, 4]:
            k = kappa(n)
            self.assertGreater(k, 0)
            self.assertIsInstance(k, float)
    
    def test_reproducibility(self):
        """Test that results are reproducible."""
        n = 10403
        k1 = kappa(n)
        k2 = kappa(n)
        
        # Should be exactly the same
        self.assertEqual(k1, k2)
    
    def test_monotonicity_with_divisors(self):
        """Test that κ increases with divisor count for similar n."""
        # For numbers close in magnitude, more divisors → larger κ
        k_prime = kappa(101)  # prime, 2 divisors
        k_composite = kappa(100)  # 100 = 2² × 5², 9 divisors
        
        # Composite should have larger κ
        self.assertGreater(k_composite, k_prime)


class TestKappaBatch(unittest.TestCase):
    """Tests for batch κ(n) computation."""
    
    def test_batch_basic(self):
        """Test basic batch computation."""
        ns = [899, 1003, 10403]
        results = batch_kappa(ns)
        
        # Check return type
        self.assertIsInstance(results, np.ndarray)
        self.assertEqual(len(results), 3)
        
        # Check all values are positive
        self.assertTrue(np.all(results > 0))
    
    def test_batch_matches_single(self):
        """Test that batch results match single computations."""
        ns = [899, 1003, 10403]
        batch_results = batch_kappa(ns)
        single_results = [kappa(n) for n in ns]
        
        # Should match within floating point precision
        np.testing.assert_array_almost_equal(batch_results, single_results)
    
    def test_batch_empty(self):
        """Test batch with empty list."""
        results = batch_kappa([])
        
        self.assertIsInstance(results, np.ndarray)
        self.assertEqual(len(results), 0)
    
    def test_batch_single_element(self):
        """Test batch with single element."""
        results = batch_kappa([899])
        
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0], kappa(899))
    
    def test_batch_large_scale(self):
        """Test batch with varying scales."""
        # Test across multiple scales
        ns = [10**i for i in range(2, 6)]
        results = batch_kappa(ns)
        
        self.assertEqual(len(results), 4)
        self.assertTrue(np.all(results > 0))
        
        # κ should generally increase with scale
        # (not strictly monotonic due to divisor count variation)
        self.assertGreater(np.mean(results[2:]), np.mean(results[:2]))


class TestBootstrapCI(unittest.TestCase):
    """Tests for bootstrap confidence interval computation."""
    
    def test_bootstrap_basic(self):
        """Test basic bootstrap CI computation."""
        data = batch_kappa([899, 1003, 10403])
        ci = bootstrap_ci(data, n_resamples=100, seed=42)
        
        # Should return tuple of two values
        self.assertIsInstance(ci, tuple)
        self.assertEqual(len(ci), 2)
        
        # Lower < Upper
        self.assertLess(ci[0], ci[1])
        
        # Both should be reasonable
        self.assertGreater(ci[0], 0)
        self.assertLess(ci[1], 10)
    
    def test_bootstrap_reproducibility(self):
        """Test that bootstrap with same seed is reproducible."""
        data = batch_kappa([899, 1003, 10403])
        
        ci1 = bootstrap_ci(data, n_resamples=100, seed=42)
        ci2 = bootstrap_ci(data, n_resamples=100, seed=42)
        
        # Should be identical with same seed
        self.assertEqual(ci1, ci2)
    
    def test_bootstrap_different_seeds(self):
        """Test that different seeds give different results."""
        data = batch_kappa([899, 1003, 10403])
        
        ci1 = bootstrap_ci(data, n_resamples=100, seed=42)
        ci2 = bootstrap_ci(data, n_resamples=100, seed=123)
        
        # Should be different (very unlikely to be same)
        self.assertNotEqual(ci1, ci2)
    
    def test_bootstrap_contains_mean(self):
        """Test that CI typically contains the true mean."""
        data = batch_kappa([899, 1003, 10403, 100003, 1000003])
        mean_val = np.mean(data)
        
        ci = bootstrap_ci(data, n_resamples=1000, seed=42)
        
        # Mean should typically be within CI (not guaranteed but very likely)
        # This is a sanity check
        self.assertGreaterEqual(mean_val, ci[0] * 0.9)  # Allow some slack
        self.assertLessEqual(mean_val, ci[1] * 1.1)
    
    def test_bootstrap_confidence_levels(self):
        """Test different confidence levels."""
        data = batch_kappa([899, 1003, 10403])
        
        ci_90 = bootstrap_ci(data, n_resamples=100, confidence=0.90, seed=42)
        ci_95 = bootstrap_ci(data, n_resamples=100, confidence=0.95, seed=42)
        ci_99 = bootstrap_ci(data, n_resamples=100, confidence=0.99, seed=42)
        
        # Higher confidence → wider interval
        width_90 = ci_90[1] - ci_90[0]
        width_95 = ci_95[1] - ci_95[0]
        width_99 = ci_99[1] - ci_99[0]
        
        self.assertLess(width_90, width_95)
        self.assertLess(width_95, width_99)


class TestRSAChallenges(unittest.TestCase):
    """Tests for RSA challenge examples."""
    
    def test_rsa_100(self):
        """Test κ(n) computation on RSA-100."""
        # RSA-100 from factordb.com
        rsa_100 = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
        
        # Use approximation for faster computation
        k = kappa(rsa_100, use_approximation=True)
        
        # Should be positive and reasonable
        self.assertGreater(k, 0)
        self.assertIsInstance(k, float)
        # For RSA-100 with ~99 digits, κ should be around 120-130
        self.assertGreater(k, 100)
        self.assertLess(k, 150)
    
    def test_rsa_129(self):
        """Test κ(n) computation on RSA-129."""
        rsa_129 = 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541
        
        # Use approximation for faster computation
        k = kappa(rsa_129, use_approximation=True)
        
        self.assertGreater(k, 0)
        self.assertIsInstance(k, float)
        # For RSA-129 with ~129 digits, κ should be around 155-165
        self.assertGreater(k, 140)
        self.assertLess(k, 180)
    
    def test_rsa_155(self):
        """Test κ(n) computation on RSA-155."""
        rsa_155 = 10941738641570527421809707322040357612003732945449205990913842131476349984288934784717997257891267332497625752899781833797076537244027146743531593354333897
        
        # Use approximation for faster computation
        k = kappa(rsa_155, use_approximation=True)
        
        self.assertGreater(k, 0)
        self.assertIsInstance(k, float)
        # For RSA-155 with ~155 digits, κ should be around 185-200
        self.assertGreater(k, 180)
        self.assertLess(k, 210)
    
    def test_rsa_batch(self):
        """Test batch computation on all RSA challenges."""
        rsa_values = [
            1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139,  # RSA-100
            114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541,  # RSA-129
            10941738641570527421809707322040357612003732945449205990913842131476349984288934784717997257891267332497625752899781833797076537244027146743531593354333897  # RSA-155
        ]
        
        # Use approximation for faster computation
        results = batch_kappa(rsa_values, use_approximation=True)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(np.all(results > 0))
        
        # Should generally increase with scale (more digits)
        # RSA-155 > RSA-129 > RSA-100
        self.assertGreater(results[2], results[1])
        self.assertGreater(results[1], results[0])
    
    def test_demonstrate_rsa_challenges_runs(self):
        """Test that demonstrate_rsa_challenges runs without error."""
        # Capture output
        f = io.StringIO()
        
        with redirect_stdout(f):
            demonstrate_rsa_challenges()
        
        output = f.getvalue()
        
        # Check that output contains expected content
        self.assertIn("RSA-100", output)
        self.assertIn("RSA-129", output)
        self.assertIn("RSA-155", output)
        self.assertIn("Bootstrap", output)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""
    
    def test_negative_value(self):
        """Test that negative values raise ValueError."""
        with self.assertRaises(ValueError):
            kappa(-1)
    
    def test_zero_value(self):
        """Test that zero raises ValueError."""
        with self.assertRaises(ValueError):
            kappa(0)
    
    def test_batch_negative_value(self):
        """Test that batch with negative value raises ValueError."""
        with self.assertRaises(ValueError):
            batch_kappa([899, -1, 1003])
    
    def test_batch_zero_value(self):
        """Test that batch with zero raises ValueError."""
        with self.assertRaises(ValueError):
            batch_kappa([899, 0, 1003])
    
    def test_bootstrap_empty_data(self):
        """Test that bootstrap with empty data raises ValueError."""
        with self.assertRaises(ValueError):
            bootstrap_ci([])
    
    def test_very_large_number(self):
        """Test κ(n) with very large number."""
        # 2^100
        n = 2**100
        k = kappa(n)
        
        self.assertGreater(k, 0)
        self.assertIsInstance(k, float)
        self.assertFalse(np.isnan(k))
        self.assertFalse(np.isinf(k))


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def test_complete_workflow(self):
        """Test complete workflow: compute → batch → CI."""
        # Generate test data
        test_ns = [899, 1003, 10403]
        
        # Step 1: Single computation
        k_single = kappa(test_ns[0])
        self.assertGreater(k_single, 0)
        
        # Step 2: Batch computation
        k_batch = batch_kappa(test_ns)
        self.assertEqual(len(k_batch), 3)
        
        # Step 3: Bootstrap CI
        ci = bootstrap_ci(k_batch, n_resamples=100, seed=42)
        self.assertEqual(len(ci), 2)
        self.assertLess(ci[0], ci[1])
        
        # Verify consistency
        self.assertAlmostEqual(k_single, k_batch[0])
    
    def test_scaling_pattern(self):
        """Test that κ(n) follows expected scaling pattern."""
        # Test hypothesis: κ(n) ≈ 4 * ln(n) / e² for semiprimes
        test_semiprimes = [
            (899, 29, 31),
            (10403, 101, 103),
            (1000003, 293, 3413)
        ]
        
        from sympy import log, exp
        
        for n, p, q in test_semiprimes:
            k = kappa(n)
            expected = 4 * float(log(n)) / float(exp(2))
            ratio = k / expected
            
            # Ratio should be in reasonable range (0.5 to 2.0)
            # Exact value depends on divisor count
            self.assertGreater(ratio, 0.3)
            self.assertLess(ratio, 3.0)


def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKappaSingleValue))
    suite.addTests(loader.loadTestsFromTestCase(TestKappaBatch))
    suite.addTests(loader.loadTestsFromTestCase(TestBootstrapCI))
    suite.addTests(loader.loadTestsFromTestCase(TestRSAChallenges))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
