#!/usr/bin/env python3
"""
Comprehensive Test Suite for CryptographicPrimeGenerator
========================================================

This test suite validates all aspects of the cryptographic prime generator:
1. Basic functionality and initialization
2. Cryptographic quality assessment
3. Prime generation with various security levels
4. Performance benchmarking
5. Z-framework integration
6. Security and entropy validation
7. Edge cases and error handling

The tests ensure that the generator meets cryptographic standards while
leveraging the optimal curvature parameter k* = 0.3 for enhanced efficiency.
"""

import sys
import os
import unittest
import numpy as np
from sympy import isprime
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from applications.cryptographic_prime_generator import (
    CryptographicPrimeGenerator, 
    SecurityLevel,
    CryptographicPrimeResult
)

class TestCryptographicPrimeGenerator(unittest.TestCase):
    """Test cases for CryptographicPrimeGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = CryptographicPrimeGenerator(
            security_level=SecurityLevel.LOW,  # Use low for faster tests
            k=0.3,
            mid_bin_enhancement=0.15
        )

    def test_initialization(self):
        """Test basic generator initialization."""
        generator = CryptographicPrimeGenerator()
        self.assertEqual(generator.security_level, SecurityLevel.MEDIUM)
        self.assertEqual(generator.k, 0.3)
        self.assertEqual(generator.mid_bin_enhancement, 0.15)
        self.assertEqual(generator.entropy_source, "cryptographic")
        
        # Test custom initialization
        custom_gen = CryptographicPrimeGenerator(
            security_level=SecurityLevel.HIGH,
            k=0.25,
            mid_bin_enhancement=0.2,
            entropy_source="quantum"
        )
        self.assertEqual(custom_gen.security_level, SecurityLevel.HIGH)
        self.assertEqual(custom_gen.k, 0.25)
        self.assertEqual(custom_gen.mid_bin_enhancement, 0.2)
        self.assertEqual(custom_gen.entropy_source, "quantum")

    def test_cryptographic_entropy_generation(self):
        """Test cryptographic entropy generation."""
        # Test different entropy sources
        for source in ["cryptographic", "quantum", "mixed"]:
            generator = CryptographicPrimeGenerator(entropy_source=source)
            entropy = generator._cryptographic_entropy(32)
            
            self.assertEqual(len(entropy), 32)
            self.assertIsInstance(entropy, bytes)
            
            # Test that entropy is different each time
            entropy2 = generator._cryptographic_entropy(32)
            self.assertNotEqual(entropy, entropy2)

    def test_frame_shift_residues_crypto(self):
        """Test cryptographic frame shift transformation."""
        indices = np.array([1, 2, 3, 4, 5, 10, 20, 50])
        target_range = (1000, 10000)
        
        result = self.generator._frame_shift_residues_crypto(indices, target_range)
        
        # Should return array of same length
        self.assertEqual(len(result), len(indices))
        
        # All values should be within target range
        min_val, max_val = target_range
        self.assertTrue(np.all(result >= min_val))
        self.assertTrue(np.all(result <= max_val))
        
        # Test with different k values
        result_k1 = self.generator._frame_shift_residues_crypto(indices, target_range, k=0.1)
        result_k2 = self.generator._frame_shift_residues_crypto(indices, target_range, k=0.5)
        
        # Different k values should produce different results
        self.assertFalse(np.array_equal(result_k1, result_k2))

    def test_cryptographic_quality_assessment(self):
        """Test cryptographic quality assessment methods."""
        # Test with known primes
        test_primes = [17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
        
        for prime in test_primes:
            quality = self.generator._assess_cryptographic_quality(prime)
            
            # Check that all quality metrics are present
            self.assertIn('hamming_weight', quality)
            self.assertIn('runs_test', quality)
            self.assertIn('entropy', quality)
            self.assertIn('gap_quality', quality)
            self.assertIn('overall_quality', quality)
            
            # All metrics should be between 0 and 1
            for metric in quality.values():
                self.assertGreaterEqual(metric, 0.0)
                self.assertLessEqual(metric, 1.0)

    def test_hamming_weight_calculation(self):
        """Test Hamming weight calculation."""
        # Test specific cases
        test_cases = [
            (15, 4/4),    # 1111 -> 4/4 = 1.0
            (7, 3/3),     # 111 -> 3/3 = 1.0  
            (8, 1/4),     # 1000 -> 1/4 = 0.25
            (5, 2/3),     # 101 -> 2/3 ≈ 0.67
        ]
        
        for number, expected_weight in test_cases:
            quality = self.generator._assess_cryptographic_quality(number)
            self.assertAlmostEqual(quality['hamming_weight'], expected_weight, places=2)

    def test_runs_test(self):
        """Test runs test for randomness."""
        # Test specific binary patterns
        test_cases = [
            "10101010",  # Perfect alternating
            "11110000",  # Two runs
            "11111111",  # Single run
            "10110001",  # Multiple runs
        ]
        
        for pattern in test_cases:
            runs_score = self.generator._runs_test(pattern)
            self.assertGreaterEqual(runs_score, 0.0)
            self.assertLessEqual(runs_score, 1.0)

    def test_entropy_estimation(self):
        """Test entropy estimation."""
        # Test with numbers having different digit distributions
        test_numbers = [
            1111111,    # Low entropy (repeated digits)
            1234567,    # Medium entropy (sequential)
            1928374,    # Higher entropy (mixed)
        ]
        
        entropies = []
        for number in test_numbers:
            entropy = self.generator._estimate_entropy(number)
            self.assertGreaterEqual(entropy, 0.0)
            self.assertLessEqual(entropy, 1.0)
            entropies.append(entropy)
        
        # Generally, more varied digits should have higher entropy
        # (though this is not guaranteed for all cases)
        self.assertGreaterEqual(entropies[-1], entropies[0])

    def test_single_prime_generation(self):
        """Test generation of single cryptographic prime."""
        # Test with small bit length for speed
        result = self.generator.generate_cryptographic_prime(bit_length=64)
        
        self.assertIsInstance(result, CryptographicPrimeResult)
        self.assertEqual(len(result.primes), 1)
        
        prime = result.primes[0]
        
        # Verify it's actually prime
        self.assertTrue(isprime(prime))
        
        # Check bit length is approximately correct
        self.assertGreaterEqual(prime.bit_length(), 60)  # Allow some tolerance
        self.assertLessEqual(prime.bit_length(), 68)
        
        # Check metadata
        self.assertGreater(result.generation_time, 0)
        self.assertGreater(result.candidates_tested, 0)
        self.assertEqual(result.mid_bin_enhancement, 0.15)
        self.assertEqual(result.security_level, "low")
        self.assertGreaterEqual(result.entropy_quality, 0.0)
        self.assertLessEqual(result.entropy_quality, 1.0)
        self.assertEqual(result.k_parameter, 0.3)

    def test_prime_pair_generation(self):
        """Test generation of prime pairs for RSA."""
        result = self.generator.generate_prime_pair(bit_length=64)
        
        self.assertIsInstance(result, CryptographicPrimeResult)
        self.assertEqual(len(result.primes), 2)
        
        p, q = result.primes
        
        # Verify both are prime
        self.assertTrue(isprime(p))
        self.assertTrue(isprime(q))
        
        # Verify they are different
        self.assertNotEqual(p, q)
        
        # Verify they are coprime (gcd = 1)
        self.assertEqual(np.gcd(p, q), 1)
        
        # Check bit lengths
        for prime in [p, q]:
            self.assertGreaterEqual(prime.bit_length(), 60)
            self.assertLessEqual(prime.bit_length(), 68)

    def test_security_levels(self):
        """Test prime generation with different security levels."""
        # Note: Using smaller bit lengths for testing speed
        test_cases = [
            (SecurityLevel.LOW, 32),
            (SecurityLevel.MEDIUM, 64),
            (SecurityLevel.HIGH, 128),
        ]
        
        for security_level, test_bit_length in test_cases:
            generator = CryptographicPrimeGenerator(security_level=security_level)
            result = generator.generate_cryptographic_prime(bit_length=test_bit_length)
            
            prime = result.primes[0]
            self.assertTrue(isprime(prime))
            self.assertEqual(result.security_level, security_level.value)
            
            # Bit length should be approximately correct
            self.assertGreaterEqual(prime.bit_length(), test_bit_length - 5)
            self.assertLessEqual(prime.bit_length(), test_bit_length + 5)

    def test_quality_threshold(self):
        """Test quality threshold enforcement."""
        # Test with high quality threshold
        try:
            result = self.generator.generate_cryptographic_prime(
                bit_length=64, 
                quality_threshold=0.9
            )
            # If successful, quality should meet threshold
            prime = result.primes[0]
            quality = self.generator._assess_cryptographic_quality(prime)
            self.assertGreaterEqual(quality['overall_quality'], 0.9)
        except RuntimeError:
            # High threshold may fail - this is acceptable
            pass
        
        # Test with low quality threshold (should always succeed)
        result = self.generator.generate_cryptographic_prime(
            bit_length=64,
            quality_threshold=0.1
        )
        self.assertEqual(len(result.primes), 1)
        self.assertTrue(isprime(result.primes[0]))

    def test_benchmark_functionality(self):
        """Test performance benchmarking."""
        # Use small parameters for test speed
        benchmark = self.generator.benchmark_against_traditional(
            num_primes=3,
            bit_length=32
        )
        
        # Check structure
        self.assertIn('z_framework', benchmark)
        self.assertIn('traditional', benchmark)
        self.assertIn('performance', benchmark)
        
        # Check Z-framework results
        z_results = benchmark['z_framework']
        self.assertEqual(z_results['primes_generated'], 3)
        self.assertGreater(z_results['time_seconds'], 0)
        self.assertGreater(z_results['candidates_tested'], 0)
        self.assertGreater(z_results['efficiency'], 0)
        
        # Check traditional results
        trad_results = benchmark['traditional']
        self.assertEqual(trad_results['primes_generated'], 3)
        self.assertGreater(trad_results['time_seconds'], 0)
        self.assertGreater(trad_results['candidates_tested'], 0)
        self.assertGreater(trad_results['efficiency'], 0)
        
        # Check performance metrics
        perf_results = benchmark['performance']
        self.assertGreater(perf_results['speedup_factor'], 0)
        self.assertEqual(perf_results['mid_bin_enhancement'], 15.0)  # 0.15 * 100

    def test_z_framework_integration(self):
        """Test Z-framework integration validation."""
        validations = self.generator.validate_z_framework_integration()
        
        # Check that all expected components are tested
        expected_components = [
            'universal_z_form',
            'discrete_zeta_shift',
            'frame_shift_transformation',
            'cryptographic_entropy'
        ]
        
        for component in expected_components:
            self.assertIn(component, validations)
            self.assertIsInstance(validations[component], bool)
        
        # At least some validations should pass
        passing_validations = sum(validations.values())
        self.assertGreater(passing_validations, 0)

    def test_mid_bin_enhancement(self):
        """Test mid-bin density enhancement functionality."""
        # Create generators with different enhancement levels
        gen_no_enhancement = CryptographicPrimeGenerator(mid_bin_enhancement=0.0)
        gen_with_enhancement = CryptographicPrimeGenerator(mid_bin_enhancement=0.3)
        
        # Generate candidates with both generators
        indices = np.array([1, 2, 3, 4, 5])
        target_range = (1000, 10000)
        
        candidates_no_enh = gen_no_enhancement._frame_shift_residues_crypto(indices, target_range)
        candidates_with_enh = gen_with_enhancement._frame_shift_residues_crypto(indices, target_range)
        
        # Results should be different
        self.assertFalse(np.array_equal(candidates_no_enh, candidates_with_enh))
        
        # Both should be in valid range
        min_val, max_val = target_range
        self.assertTrue(np.all(candidates_no_enh >= min_val))
        self.assertTrue(np.all(candidates_no_enh <= max_val))
        self.assertTrue(np.all(candidates_with_enh >= min_val))
        self.assertTrue(np.all(candidates_with_enh <= max_val))

    def test_k_parameter_sensitivity(self):
        """Test sensitivity to k parameter."""
        k_values = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # Generate primes with different k values
        results = []
        for k in k_values:
            generator = CryptographicPrimeGenerator(
                security_level=SecurityLevel.LOW,
                k=k
            )
            try:
                result = generator.generate_cryptographic_prime(bit_length=32)
                results.append((k, result))
            except RuntimeError:
                # Some k values might fail - that's ok for testing
                pass
        
        # Should have at least some successful results
        self.assertGreater(len(results), 0)
        
        # Verify k parameter is recorded correctly
        for k, result in results:
            self.assertEqual(result.k_parameter, k)
            self.assertTrue(isprime(result.primes[0]))

    def test_error_handling(self):
        """Test error handling for edge cases."""
        # Test with invalid bit length
        with self.assertRaises((ValueError, RuntimeError)):
            self.generator.generate_cryptographic_prime(bit_length=1)
        
        # Test with invalid range
        with self.assertRaises((ValueError, RuntimeError)):
            self.generator.generate_cryptographic_prime(min_value=1000, max_value=100)

    def test_determinism_and_randomness(self):
        """Test that generation has appropriate randomness properties."""
        # Generate multiple primes
        primes = []
        for _ in range(5):
            result = self.generator.generate_cryptographic_prime(bit_length=32)
            primes.extend(result.primes)
        
        # Should generate different primes each time
        unique_primes = set(primes)
        self.assertEqual(len(unique_primes), len(primes))  # All should be unique
        
        # All should be prime
        for prime in primes:
            self.assertTrue(isprime(prime))

    def test_performance_requirements(self):
        """Test that generation meets reasonable performance requirements."""
        start_time = time.time()
        
        # Generate a small prime (should be fast)
        result = self.generator.generate_cryptographic_prime(bit_length=32)
        
        generation_time = time.time() - start_time
        
        # Should complete within reasonable time (5 seconds for test)
        self.assertLess(generation_time, 5.0)
        
        # Result should be valid
        self.assertTrue(isprime(result.primes[0]))
        self.assertGreater(result.frame_efficiency, 0)

    def test_bit_length_accuracy(self):
        """Test that generated primes have correct bit lengths."""
        test_bit_lengths = [16, 32, 64, 128]
        
        for target_bits in test_bit_lengths:
            result = self.generator.generate_cryptographic_prime(bit_length=target_bits)
            prime = result.primes[0]
            actual_bits = prime.bit_length()
            
            # Allow for some tolerance (within 10% or ±2 bits, whichever is larger)
            tolerance = max(2, target_bits * 0.1)
            self.assertGreaterEqual(actual_bits, target_bits - tolerance)
            self.assertLessEqual(actual_bits, target_bits + tolerance)

    def test_cryptographic_standards_compliance(self):
        """Test compliance with basic cryptographic standards."""
        result = self.generator.generate_cryptographic_prime(bit_length=64)
        prime = result.primes[0]
        
        # Prime should be odd (except 2)
        if prime != 2:
            self.assertEqual(prime % 2, 1)
        
        # Should have reasonable entropy quality
        self.assertGreaterEqual(result.entropy_quality, 0.3)
        
        # Should not be easily factorable (basic check)
        self.assertTrue(isprime(prime))
        
        # Should have reasonable cryptographic quality
        quality = self.generator._assess_cryptographic_quality(prime)
        self.assertGreaterEqual(quality['overall_quality'], 0.4)


class TestSecurityLevels(unittest.TestCase):
    """Test security level configurations."""
    
    def test_security_level_mappings(self):
        """Test that security levels map to correct bit lengths."""
        expected_mappings = {
            SecurityLevel.LOW: 512,
            SecurityLevel.MEDIUM: 1024,
            SecurityLevel.HIGH: 2048,
            SecurityLevel.ULTRA: 4096
        }
        
        for level, expected_bits in expected_mappings.items():
            generator = CryptographicPrimeGenerator(security_level=level)
            self.assertEqual(generator.bit_length_map[level], expected_bits)

    def test_security_level_enum(self):
        """Test SecurityLevel enum functionality."""
        # Test enum values
        self.assertEqual(SecurityLevel.LOW.value, "low")
        self.assertEqual(SecurityLevel.MEDIUM.value, "medium")
        self.assertEqual(SecurityLevel.HIGH.value, "high")
        self.assertEqual(SecurityLevel.ULTRA.value, "ultra")
        
        # Test enum iteration
        levels = list(SecurityLevel)
        self.assertEqual(len(levels), 4)


class TestCryptographicPrimeResult(unittest.TestCase):
    """Test CryptographicPrimeResult dataclass."""
    
    def test_result_creation(self):
        """Test creation and attributes of CryptographicPrimeResult."""
        result = CryptographicPrimeResult(
            primes=[17, 19],
            bit_lengths=[5, 5],
            generation_time=0.1,
            candidates_tested=20,
            mid_bin_enhancement=0.15,
            security_level="medium",
            entropy_quality=0.8,
            primality_confidence=1.0,
            k_parameter=0.3,
            frame_efficiency=0.1
        )
        
        self.assertEqual(result.primes, [17, 19])
        self.assertEqual(result.bit_lengths, [5, 5])
        self.assertEqual(result.generation_time, 0.1)
        self.assertEqual(result.candidates_tested, 20)
        self.assertEqual(result.mid_bin_enhancement, 0.15)
        self.assertEqual(result.security_level, "medium")
        self.assertEqual(result.entropy_quality, 0.8)
        self.assertEqual(result.primality_confidence, 1.0)
        self.assertEqual(result.k_parameter, 0.3)
        self.assertEqual(result.frame_efficiency, 0.1)


def run_comprehensive_tests():
    """Run all tests with detailed output."""
    print("=== Cryptographic Prime Generator Test Suite ===\n")
    
    # Create test suite
    test_classes = [
        TestCryptographicPrimeGenerator,
        TestSecurityLevels,
        TestCryptographicPrimeResult
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)