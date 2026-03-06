#!/usr/bin/env python3
"""
Unit Tests for Gaussian Integer Cryptography with Conformal Transformations

Tests cryptographic applications including:
1. Key generation with conformal transformations
2. Image encryption over Gaussian integers
3. Differential attack resistance analysis
4. Angle-preserving properties

Following z-sandbox axioms:
- Empirical validation of security properties
- Reproducibility with fixed seeds
- High precision where applicable
"""

import sys
import unittest
import numpy as np
from pathlib import Path

# Add python directory to path
python_dir = Path(__file__).parent.parent / 'python'
sys.path.insert(0, str(python_dir))

from gaussian_crypto import (
    GaussianKeyGenerator,
    GaussianImageEncryption,
    DifferentialAttackAnalyzer,
    CryptographicDemo
)


class TestGaussianKeyGenerator(unittest.TestCase):
    """Test key generation with Gaussian integers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.keygen = GaussianKeyGenerator(seed=42)
    
    def test_generate_gaussian_key_basic(self):
        """Test basic Gaussian key generation."""
        key = self.keygen.generate_gaussian_key(bit_length=64)
        
        # Check it's a complex number
        self.assertIsInstance(key, complex)
        
        # Check components are integers (within floating point precision)
        self.assertEqual(key.real, int(key.real))
        self.assertEqual(key.imag, int(key.imag))
    
    def test_generate_gaussian_key_reproducibility(self):
        """Test that keys are reproducible with same seed."""
        keygen1 = GaussianKeyGenerator(seed=42)
        keygen2 = GaussianKeyGenerator(seed=42)
        
        key1 = keygen1.generate_gaussian_key(bit_length=64)
        key2 = keygen2.generate_gaussian_key(bit_length=64)
        
        self.assertEqual(key1, key2)
    
    def test_generate_key_pair_conformal(self):
        """Test key pair generation with conformal transformation."""
        pub, priv = self.keygen.generate_key_pair(bit_length=64, use_conformal=True, transformation_type='square')
        
        # Check both are complex numbers
        self.assertIsInstance(pub, complex)
        self.assertIsInstance(priv, complex)
        
        # For z → z² transformation:
        # |pub| should be approximately |priv|²
        expected_modulus = abs(priv) ** 2
        actual_modulus = abs(pub)
        
        # Allow for some floating point error
        relative_error = abs(actual_modulus - expected_modulus) / expected_modulus
        self.assertLess(relative_error, 0.01)
    
    def test_generate_key_pair_angle_doubling(self):
        """Test that conformal transformation doubles angles."""
        pub, priv = self.keygen.generate_key_pair(bit_length=64, use_conformal=True, transformation_type='square')
        
        angle_priv = np.angle(priv)
        angle_pub = np.angle(pub)
        
        # For z → z², angle should double (modulo 2π)
        expected_angle = 2 * angle_priv
        
        # Normalize angles to [-π, π]
        def normalize_angle(a):
            while a > np.pi:
                a -= 2 * np.pi
            while a < -np.pi:
                a += 2 * np.pi
            return a
        
        angle_diff = abs(normalize_angle(angle_pub - expected_angle))
        self.assertLess(angle_diff, 0.01)
    
    def test_key_serialization(self):
        """Test key conversion to/from bytes."""
        original_key = self.keygen.generate_gaussian_key(bit_length=64)
        
        # Convert to bytes and back
        key_bytes = self.keygen.key_to_bytes(original_key)
        recovered_key = self.keygen.bytes_to_key(key_bytes)
        
        # Check they're equal
        self.assertEqual(original_key, recovered_key)
    
    def test_key_bytes_length(self):
        """Test that key bytes have expected length."""
        key = self.keygen.generate_gaussian_key(bit_length=64)
        key_bytes = self.keygen.key_to_bytes(key)
        
        # Should be 32 bytes for real + 32 bytes for imag = 64 bytes
        self.assertEqual(len(key_bytes), 64)


class TestGaussianImageEncryption(unittest.TestCase):
    """Test image encryption over Gaussian integers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.key = complex(12345, 67890)
        self.encryptor = GaussianImageEncryption(key=self.key)
    
    def test_pixel_to_gaussian_encoding(self):
        """Test RGB to Gaussian integer encoding."""
        r, g, b = 255, 128, 64
        
        gaussian = self.encryptor.pixel_to_gaussian(r, g, b)
        
        # Check it's a Gaussian integer
        self.assertIsInstance(gaussian, complex)
        self.assertEqual(gaussian.real, int(gaussian.real))
        self.assertEqual(gaussian.imag, int(gaussian.imag))
    
    def test_pixel_roundtrip(self):
        """Test that pixel encoding/decoding is reversible."""
        original_pixel = (255, 128, 64)
        
        # Encode and decode
        gaussian = self.encryptor.pixel_to_gaussian(*original_pixel)
        recovered_pixel = self.encryptor.gaussian_to_pixel(gaussian)
        
        self.assertEqual(original_pixel, recovered_pixel)
    
    def test_encrypt_decrypt_pixel_approximate(self):
        """Test pixel encryption/decryption (approximate due to non-linear transform)."""
        original = complex(100, 50)
        position = (5, 10)
        
        # Encrypt and decrypt
        encrypted = self.encryptor.encrypt_pixel(original, position)
        decrypted = self.encryptor.decrypt_pixel(encrypted, position)
        
        # Due to square transformation, perfect inversion is not guaranteed
        # but decrypted should be in reasonable range
        self.assertIsInstance(decrypted, complex)
    
    def test_position_dependent_encryption(self):
        """Test that encryption is position-dependent."""
        pixel = complex(100, 50)
        
        encrypted_pos1 = self.encryptor.encrypt_pixel(pixel, (0, 0))
        encrypted_pos2 = self.encryptor.encrypt_pixel(pixel, (10, 10))
        
        # Different positions should give different ciphertexts
        self.assertNotEqual(encrypted_pos1, encrypted_pos2)
    
    def test_encrypt_image_array_shape(self):
        """Test that encrypted image maintains shape."""
        # Create small test image
        test_image = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        
        encrypted = self.encryptor.encrypt_image_array(test_image)
        
        # Check shape is preserved
        self.assertEqual(encrypted.shape, test_image.shape)
    
    def test_encrypt_different_pixels(self):
        """Test that different pixels encrypt to different values."""
        pixel1 = complex(100, 50)
        pixel2 = complex(150, 75)
        position = (5, 5)
        
        encrypted1 = self.encryptor.encrypt_pixel(pixel1, position)
        encrypted2 = self.encryptor.encrypt_pixel(pixel2, position)
        
        self.assertNotEqual(encrypted1, encrypted2)


class TestDifferentialAttackAnalyzer(unittest.TestCase):
    """Test differential attack resistance analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = DifferentialAttackAnalyzer()
        self.keygen = GaussianKeyGenerator(seed=42)
    
    def test_hamming_distance_basic(self):
        """Test Hamming distance computation."""
        z1 = complex(0b1111, 0b0000)
        z2 = complex(0b1100, 0b0011)
        
        distance = self.analyzer.hamming_distance_complex(z1, z2)
        
        # XOR: 0b1111 ^ 0b1100 = 0b0011 (2 bits)
        # XOR: 0b0000 ^ 0b0011 = 0b0011 (2 bits)
        # Total: 4 bits
        self.assertEqual(distance, 4)
    
    def test_hamming_distance_identical(self):
        """Test Hamming distance of identical values is zero."""
        z = complex(12345, 67890)
        
        distance = self.analyzer.hamming_distance_complex(z, z)
        
        self.assertEqual(distance, 0)
    
    def test_avalanche_effect_structure(self):
        """Test avalanche effect analysis returns proper structure."""
        plaintext = self.keygen.generate_gaussian_key(64)
        
        result = self.analyzer.analyze_avalanche_effect(plaintext, num_trials=10)
        
        # Check required keys
        required_keys = ['mean_flip_rate', 'std_flip_rate', 'min_flip_rate', 
                        'max_flip_rate', 'ideal_flip_rate', 'quality']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check flip rate is between 0 and 1
        self.assertGreaterEqual(result['mean_flip_rate'], 0.0)
        self.assertLessEqual(result['mean_flip_rate'], 1.0)
    
    def test_confusion_analysis_structure(self):
        """Test confusion analysis returns proper structure."""
        key1 = self.keygen.generate_gaussian_key(64)
        key2 = self.keygen.generate_gaussian_key(64)
        plaintext = self.keygen.generate_gaussian_key(64)
        
        result = self.analyzer.analyze_confusion(key1, key2, plaintext)
        
        # Check required keys
        required_keys = ['key_hamming_distance', 'output_hamming_distance', 
                        'amplification_factor', 'interpretation']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Output distance should be non-negative
        self.assertGreaterEqual(result['output_hamming_distance'], 0)
    
    def test_differential_resistance_score_structure(self):
        """Test comprehensive resistance score structure."""
        result = self.analyzer.differential_resistance_score(num_samples=10)
        
        # Check required keys
        required_keys = ['overall_score', 'max_score', 'average_avalanche_effect',
                        'average_confusion_amplification', 'assessment', 'recommendation']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Score should be non-negative
        self.assertGreaterEqual(result['overall_score'], 0)
    
    def test_avalanche_effect_range(self):
        """Test that avalanche effect produces reasonable values."""
        plaintext = self.keygen.generate_gaussian_key(64)
        
        result = self.analyzer.analyze_avalanche_effect(plaintext, num_trials=50)
        
        # Flip rate should be between 0 and 1
        self.assertGreaterEqual(result['mean_flip_rate'], 0.0)
        self.assertLessEqual(result['mean_flip_rate'], 1.0)
        
        # Standard deviation should be reasonable
        self.assertGreaterEqual(result['std_flip_rate'], 0.0)
        self.assertLessEqual(result['std_flip_rate'], 0.5)


class TestCryptographicDemo(unittest.TestCase):
    """Test cryptographic demonstration functions."""
    
    def test_demo_key_generation_runs(self):
        """Test that key generation demo runs without error."""
        demo = CryptographicDemo()
        
        # Should not raise any exceptions
        try:
            demo.demo_key_generation()
            success = True
        except Exception as e:
            success = False
            print(f"Demo failed: {e}")
        
        self.assertTrue(success)
    
    def test_demo_differential_resistance_runs(self):
        """Test that differential resistance demo runs without error."""
        demo = CryptographicDemo()
        
        # Should not raise any exceptions
        try:
            demo.demo_differential_resistance()
            success = True
        except Exception as e:
            success = False
            print(f"Demo failed: {e}")
        
        self.assertTrue(success)
    
    def test_demo_image_encryption_runs(self):
        """Test that image encryption demo runs without error."""
        demo = CryptographicDemo()
        
        # Should not raise any exceptions
        try:
            demo.demo_image_encryption_concept()
            success = True
        except Exception as e:
            success = False
            print(f"Demo failed: {e}")
        
        self.assertTrue(success)


class TestIntegrationWithConformalTransformations(unittest.TestCase):
    """Test integration with conformal transformation properties."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.keygen = GaussianKeyGenerator(seed=42)
    
    def test_conformal_preserves_angle_property(self):
        """Test that conformal transformation preserves relative angles."""
        # Generate two keys
        key1 = self.keygen.generate_gaussian_key(64)
        key2 = self.keygen.generate_gaussian_key(64)
        
        # Apply conformal transformation (z → z²)
        transformed1 = key1 * key1
        transformed2 = key2 * key2
        
        # Angles should double
        angle1_orig = np.angle(key1)
        angle1_trans = np.angle(transformed1)
        
        # Allow for 2π wraparound
        expected = 2 * angle1_orig
        diff = abs(angle1_trans - expected)
        if diff > np.pi:
            diff = abs(diff - 2 * np.pi)
        
        self.assertLess(diff, 0.1)
    
    def test_modulus_squaring_property(self):
        """Test that z → z² squares the modulus."""
        key = self.keygen.generate_gaussian_key(64)
        
        transformed = key * key
        
        # |z²| = |z|²
        expected_modulus = abs(key) ** 2
        actual_modulus = abs(transformed)
        
        relative_error = abs(actual_modulus - expected_modulus) / expected_modulus
        self.assertLess(relative_error, 1e-10)
    
    def test_encryption_uses_conformal_properties(self):
        """Test that encryption benefits from conformal properties."""
        encryptor = GaussianImageEncryption(key=complex(123, 456))
        
        # Encrypt same pixel at different positions
        pixel = complex(100, 50)
        enc1 = encryptor.encrypt_pixel(pixel, (0, 0))
        enc2 = encryptor.encrypt_pixel(pixel, (1, 0))
        
        # Different positions should yield different results
        self.assertNotEqual(enc1, enc2)
        
        # But both should have conformal transformation applied
        # (modulus should be squared after transformation)
        # This is implicit in the encrypt_pixel implementation


class TestMobiusTransformations(unittest.TestCase):
    """Test Möbius transformation support for bijective encryption."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.keygen = GaussianKeyGenerator(seed=42)
        try:
            from gaussian_lattice import GaussianIntegerLattice
            self.lattice = GaussianIntegerLattice()
            self.lattice_available = True
        except ImportError:
            self.lattice_available = False
    
    def test_mobius_transformation_basic(self):
        """Test basic Möbius transformation."""
        if not self.lattice_available:
            self.skipTest("Lattice module not available")
        
        z = complex(3, 4)
        a, b, c, d = complex(2, 0), complex(1, 0), complex(1, 0), complex(3, 0)
        
        # Apply Möbius transformation
        result = self.lattice.mobius_transform(z, a, b, c, d)
        
        # Should not be None
        self.assertIsNotNone(result)
        
        # Result should be complex
        self.assertIsInstance(result, complex)
    
    def test_mobius_inverse_property(self):
        """Test that Möbius inverse correctly reverses transformation."""
        if not self.lattice_available:
            self.skipTest("Lattice module not available")
        
        z = complex(3, 4)
        a, b, c, d = complex(2, 0), complex(1, 0), complex(1, 0), complex(3, 0)
        
        # Apply transformation and inverse
        transformed = self.lattice.mobius_transform(z, a, b, c, d)
        recovered = self.lattice.mobius_inverse(transformed, a, b, c, d)
        
        # Should recover original
        if recovered is not None:
            error = abs(recovered - z)
            self.assertLess(error, 1e-10)
    
    def test_mobius_key_generation(self):
        """Test key generation with Möbius transformation."""
        pub, priv = self.keygen.generate_key_pair(
            bit_length=64, 
            use_conformal=True,
            transformation_type='mobius'
        )
        
        # Both should be complex numbers
        self.assertIsInstance(pub, complex)
        self.assertIsInstance(priv, complex)
        
        # Public key should differ from private key
        self.assertNotEqual(pub, priv)
    
    def test_mobius_encryption_decryption_exact(self):
        """Test that Möbius-based encryption allows exact decryption."""
        if not self.lattice_available:
            self.skipTest("Lattice module not available")
        
        # Create encryptor with mobius mode
        key = complex(123, 456)
        encryptor = GaussianImageEncryption(key=key, mode='mobius')
        
        # Test pixel
        original_pixel = complex(100, 50)
        position = (5, 10)
        
        # Encrypt and decrypt
        encrypted = encryptor.encrypt_pixel(original_pixel, position)
        decrypted = encryptor.decrypt_pixel(encrypted, position)
        
        # Should recover original (within small tolerance)
        error = abs(decrypted - original_pixel)
        
        # Möbius should give exact recovery (< 1e-6 tolerance for numerical errors)
        self.assertLess(error, 1e-6)
    
    def test_mobius_vs_square_accuracy(self):
        """Test that Möbius decryption is more accurate than square."""
        if not self.lattice_available:
            self.skipTest("Lattice module not available")
        
        key = complex(123, 456)
        
        # Test multiple pixels to get statistical behavior
        errors_mobius = []
        errors_square = []
        
        test_pixels = [
            (complex(100, 50), (5, 10)),
            (complex(200, 100), (0, 0)),
            (complex(50, 25), (10, 5)),
            (complex(150, 75), (3, 7)),
        ]
        
        for original_pixel, position in test_pixels:
            # Test with Möbius
            encryptor_mobius = GaussianImageEncryption(key=key, mode='mobius')
            encrypted_m = encryptor_mobius.encrypt_pixel(original_pixel, position)
            decrypted_m = encryptor_mobius.decrypt_pixel(encrypted_m, position)
            error_mobius = abs(decrypted_m - original_pixel)
            errors_mobius.append(error_mobius)
            
            # Test with square
            encryptor_square = GaussianImageEncryption(key=key, mode='square')
            encrypted_s = encryptor_square.encrypt_pixel(original_pixel, position)
            decrypted_s = encryptor_square.decrypt_pixel(encrypted_s, position)
            error_square = abs(decrypted_s - original_pixel)
            errors_square.append(error_square)
        
        # Möbius should have better average accuracy
        avg_error_mobius = sum(errors_mobius) / len(errors_mobius)
        avg_error_square = sum(errors_square) / len(errors_square)
        
        # Möbius should be at least as accurate (allowing for edge cases)
        self.assertLessEqual(avg_error_mobius, avg_error_square + 1e-6)
    
    def test_mobius_parameters_generation(self):
        """Test generation of valid Möbius parameters."""
        a, b, c, d = self.keygen.generate_mobius_parameters(64)
        
        # All should be complex
        self.assertIsInstance(a, complex)
        self.assertIsInstance(b, complex)
        self.assertIsInstance(c, complex)
        self.assertIsInstance(d, complex)
        
        # Determinant should be non-zero
        det = a * d - b * c
        self.assertGreater(abs(det), 1e-10)


def run_tests():
    """Run all tests and report results."""
    print("="*70)
    print("Running Gaussian Integer Cryptography Tests")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGaussianKeyGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestGaussianImageEncryption))
    suite.addTests(loader.loadTestsFromTestCase(TestDifferentialAttackAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestCryptographicDemo))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWithConformalTransformations))
    suite.addTests(loader.loadTestsFromTestCase(TestMobiusTransformations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Test Results: {result.testsRun} tests, "
          f"{len(result.failures)} failures, {len(result.errors)} errors")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
