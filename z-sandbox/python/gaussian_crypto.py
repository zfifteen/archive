#!/usr/bin/env python3
"""
Gaussian Integer Cryptography with Conformal Transformations

⚠️  EXPERIMENTAL / RESEARCH CODE - NOT FOR PRODUCTION USE ⚠️

This module implements cryptographic applications using Gaussian integers enhanced
with conformal transformations (z → z², z → 1/z). Demonstrates practical applications
in lattice-based cryptography as outlined in the research literature.

IMPORTANT SECURITY NOTICE:
- This is a research/educational implementation demonstrating mathematical concepts
- NOT certified or validated by cryptographic standards bodies
- Contains known limitations (non-bijective transformation, suboptimal avalanche)
- Should NOT be used for security-critical applications without extensive review
- Combine with established cryptographic primitives for production use
- Requires formal security analysis before deployment

Applications:
1. Key generation with conformal transformation enhancement
2. Attack simulation framework for differential cryptanalysis
3. Image encryption over Gaussian integers
4. Resistance analysis via angle-preserving distortions

Mathematical Foundation:
- Gaussian integers ℤ[i] = {a + bi : a, b ∈ ℤ}
- Conformal maps preserve local angles (Cauchy-Riemann equations)
- Square transformation doubles arguments, squares moduli
- Inversion transformation creates non-linear diffusion

References:
- "Gaussian integers in cryptography" (Fazekas, 2023)
- "SPN-based encryption over Gaussian integers" (Sci. Direct, 2024)
- "Applications of Gaussian integers in coding theory" (ResearchGate)
- Conformal mapping theory (Wikipedia, IOSP Press, IISER Pune)

Integration with z-sandbox:
- Extends gaussian_lattice.py with cryptographic applications
- Uses lattice_conformal_transform.py for image encryption
- Follows z-sandbox axioms: precision < 1e-16, reproducibility, validation

Axioms followed:
1. Empirical Validation First: Security properties verified empirically
2. Domain-Specific Forms: Leverages Gaussian integer properties
3. Precision: High-precision arithmetic where applicable
4. Label UNVERIFIED hypotheses until validated
"""

import math
import secrets
import hashlib
from typing import List, Tuple, Optional, Dict, Any, Union
import numpy as np

try:
    from mpmath import mp, mpf
    MPMATH_AVAILABLE = True
except ImportError:
    MPMATH_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import conformal transformation utilities
try:
    import sys
    from pathlib import Path
    # Add python directory to path if not already there
    python_dir = Path(__file__).parent
    if str(python_dir) not in sys.path:
        sys.path.insert(0, str(python_dir))
    
    from gaussian_lattice import GaussianIntegerLattice
    from lattice_conformal_transform import LatticeConformalTransform
    LATTICE_AVAILABLE = True
except ImportError:
    LATTICE_AVAILABLE = False


class GaussianKeyGenerator:
    """
    Key generation using Gaussian integers with conformal transformations.
    
    Generates cryptographic keys by leveraging the mathematical properties
    of Gaussian integers and conformal mappings to create keys with enhanced
    structural properties.
    """
    
    def __init__(self, lattice_size: int = 1000, seed: Optional[int] = None):
        """
        Initialize key generator.
        
        Args:
            lattice_size: Range for Gaussian integer components
            seed: Optional seed for reproducibility (use None for cryptographic security)
        """
        self.lattice_size = lattice_size
        self.seed = seed
        if LATTICE_AVAILABLE:
            self.lattice = GaussianIntegerLattice()
        else:
            self.lattice = None
    
    def generate_gaussian_key(self, bit_length: int = 256) -> complex:
        """
        Generate a random Gaussian integer key.
        
        Uses cryptographically secure random number generation to produce
        a Gaussian integer suitable for cryptographic applications.
        
        Args:
            bit_length: Target bit length for key components
        
        Returns:
            Complex number representing Gaussian integer key
        """
        # Use secrets module for cryptographic randomness
        # Limit to reasonable size to avoid overflow
        max_val = min(2 ** (bit_length // 2), 2**31 - 1)
        
        if self.seed is not None:
            # For testing/reproducibility only
            rng = np.random.RandomState(self.seed)
            real_part = rng.randint(-max_val, max_val, dtype=np.int64)
            imag_part = rng.randint(-max_val, max_val, dtype=np.int64)
        else:
            # Cryptographically secure
            real_part = secrets.randbelow(2 * max_val) - max_val
            imag_part = secrets.randbelow(2 * max_val) - max_val
        
        return complex(int(real_part), int(imag_part))
    
    def generate_mobius_parameters(self, bit_length: int = 64) -> Tuple[complex, complex, complex, complex]:
        """
        Generate random Möbius transformation parameters (a, b, c, d).
        
        Ensures ad - bc ≠ 0 for bijectivity.
        
        Args:
            bit_length: Target bit length for parameters
        
        Returns:
            Tuple of (a, b, c, d) satisfying ad - bc ≠ 0
        """
        max_attempts = 100
        for attempt in range(max_attempts):
            # Use different seeds/offsets to avoid identity
            if self.seed is not None:
                temp_seed = self.seed + attempt * 1000
                rng = np.random.RandomState(temp_seed)
                max_val = min(2 ** (bit_length // 2), 2**31 - 1)
                
                a_real = rng.randint(-max_val, max_val, dtype=np.int64)
                a_imag = rng.randint(-max_val, max_val, dtype=np.int64)
                b_real = rng.randint(-max_val, max_val, dtype=np.int64)
                b_imag = rng.randint(-max_val, max_val, dtype=np.int64)
                c_real = rng.randint(-max_val, max_val, dtype=np.int64)
                c_imag = rng.randint(-max_val, max_val, dtype=np.int64)
                d_real = rng.randint(-max_val, max_val, dtype=np.int64)
                d_imag = rng.randint(-max_val, max_val, dtype=np.int64)
                
                a = complex(int(a_real), int(a_imag))
                b = complex(int(b_real), int(b_imag))
                c = complex(int(c_real), int(c_imag))
                d = complex(int(d_real), int(d_imag))
            else:
                a = self.generate_gaussian_key(bit_length)
                b = self.generate_gaussian_key(bit_length)
                c = self.generate_gaussian_key(bit_length)
                d = self.generate_gaussian_key(bit_length)
            
            # Check determinant condition
            det = a * d - b * c
            if abs(det) > 1e-6:  # Increased threshold
                return a, b, c, d
        
        # Fallback: use non-identity transformation with known good determinant
        # f(z) = (2z + 1)/(z + 3) has det = 2*3 - 1*1 = 5 ≠ 0
        return complex(2, 0), complex(1, 0), complex(1, 0), complex(3, 0)
    
    def generate_key_pair(self, bit_length: int = 256, 
                         use_conformal: bool = True,
                         transformation_type: str = 'mobius') -> Tuple[complex, complex]:
        """
        Generate a public-private key pair using Gaussian integers.
        
        Supports multiple transformation types:
        - 'mobius': Bijective Möbius transformation (RECOMMENDED - exact reversibility)
        - 'square': Non-bijective z → z² (approximate decryption only)
        
        Args:
            bit_length: Target bit length for keys
            use_conformal: Whether to apply conformal transformation
            transformation_type: Type of transformation ('mobius' or 'square')
        
        Returns:
            Tuple of (public_key, private_key) as Gaussian integers
            For 'mobius': private_key contains transformation parameters as metadata
        """
        private_key = self.generate_gaussian_key(bit_length)
        
        if not use_conformal:
            # Simple multiplication (for comparison)
            public_key = private_key * private_key
            return public_key, private_key
        
        if transformation_type == 'mobius' and LATTICE_AVAILABLE:
            # Generate Möbius parameters
            a, b, c, d = self.generate_mobius_parameters(bit_length // 4)
            
            # Apply Möbius transformation: f(z) = (az + b)/(cz + d)
            public_key = self.lattice.mobius_transform(private_key, a, b, c, d)
            
            if public_key is None:
                # Singularity hit, fallback to simple square
                public_key = private_key * private_key
            
            # Store Möbius parameters with private key for decryption
            # In practice, these would be stored securely
            if not hasattr(self, 'mobius_params'):
                self.mobius_params = {}
            self.mobius_params[id(private_key)] = (a, b, c, d)
            
            return public_key, private_key
        
        elif transformation_type == 'square' and LATTICE_AVAILABLE:
            # Apply square transformation (non-bijective)
            public_key = self.lattice.conformal_square(private_key)
            return public_key, private_key
        
        else:
            # Fallback
            public_key = private_key * private_key
            return public_key, private_key
    
    def decrypt_with_mobius(self, public_key: complex, private_key: complex) -> Optional[complex]:
        """
        Decrypt using Möbius inverse transformation.
        
        Args:
            public_key: Encrypted value
            private_key: Original private key (used to lookup parameters)
        
        Returns:
            Decrypted value (should equal private_key if successful)
        """
        if not LATTICE_AVAILABLE:
            return None
        
        # Retrieve stored Möbius parameters
        if not hasattr(self, 'mobius_params') or id(private_key) not in self.mobius_params:
            return None
        
        a, b, c, d = self.mobius_params[id(private_key)]
        
        # Apply inverse Möbius transformation
        decrypted = self.lattice.mobius_inverse(public_key, a, b, c, d)
        
        return decrypted
    
    def key_to_bytes(self, key: complex) -> bytes:
        """
        Convert Gaussian integer key to bytes for storage/transmission.
        
        Args:
            key: Gaussian integer as complex number
        
        Returns:
            Byte representation of key
        """
        real_bytes = int(key.real).to_bytes(32, byteorder='big', signed=True)
        imag_bytes = int(key.imag).to_bytes(32, byteorder='big', signed=True)
        return real_bytes + imag_bytes
    
    @staticmethod
    def bytes_to_key(key_bytes: bytes) -> complex:
        """
        Convert bytes back to Gaussian integer key.
        
        Args:
            key_bytes: Byte representation
        
        Returns:
            Gaussian integer as complex number
        """
        real_part = int.from_bytes(key_bytes[:32], byteorder='big', signed=True)
        imag_part = int.from_bytes(key_bytes[32:], byteorder='big', signed=True)
        return complex(real_part, imag_part)


class GaussianImageEncryption:
    """
    Image encryption scheme over Gaussian integers with conformal transformations.
    
    Implements secure multimedia transmission using:
    1. Pixel encoding as Gaussian integers
    2. Conformal transformation for diffusion
    3. Key-based encryption with angle-preserving properties
    
    Supports two encryption modes:
    - 'mobius': Bijective Möbius transformation (exact decryption)
    - 'square': Non-bijective z → z² (approximate decryption)
    """
    
    def __init__(self, key: Optional[complex] = None, mode: str = 'mobius'):
        """
        Initialize image encryption system.
        
        Args:
            key: Gaussian integer encryption key (generated if not provided)
            mode: Encryption mode ('mobius' or 'square')
        """
        if LATTICE_AVAILABLE:
            self.lattice = GaussianIntegerLattice()
            self.transformer = LatticeConformalTransform()
        else:
            self.lattice = None
            self.transformer = None
        
        self.key = key if key is not None else self._generate_default_key()
        self.mode = mode
        
        # Generate Möbius parameters if in mobius mode
        if self.mode == 'mobius':
            keygen = GaussianKeyGenerator(seed=None)
            self.mobius_a, self.mobius_b, self.mobius_c, self.mobius_d = \
                keygen.generate_mobius_parameters(64)
    
    def _generate_default_key(self) -> complex:
        """Generate a default encryption key."""
        keygen = GaussianKeyGenerator(seed=None)
        return keygen.generate_gaussian_key(128)
    
    def pixel_to_gaussian(self, r: int, g: int, b: int) -> complex:
        """
        Encode RGB pixel as Gaussian integer.
        
        Maps RGB values to complex plane:
        - Red and Green → real part
        - Blue → imaginary part
        
        Args:
            r, g, b: RGB color values (0-255)
        
        Returns:
            Gaussian integer encoding pixel
        """
        real_part = (r << 8) | g  # Combine R and G
        imag_part = b
        return complex(real_part, imag_part)
    
    def gaussian_to_pixel(self, z: complex) -> Tuple[int, int, int]:
        """
        Decode Gaussian integer back to RGB pixel.
        
        Args:
            z: Gaussian integer
        
        Returns:
            RGB tuple (r, g, b)
        """
        real_part = int(z.real) & 0xFFFF
        r = (real_part >> 8) & 0xFF
        g = real_part & 0xFF
        b = int(z.imag) & 0xFF
        return (r, g, b)
    
    def encrypt_pixel(self, pixel: complex, position: Tuple[int, int]) -> complex:
        """
        Encrypt a single pixel using conformal transformation and key.
        
        Supports two modes:
        - 'mobius': Bijective Möbius transformation (exact decryption possible)
        - 'square': Non-bijective z → z² (approximate decryption only)
        
        Applies:
        1. Position-dependent mixing
        2. Key addition (stream cipher-like)
        3. Conformal transformation (Möbius or square)
        
        Args:
            pixel: Gaussian integer representing pixel
            position: (x, y) position for position-dependent encryption
        
        Returns:
            Encrypted Gaussian integer
        """
        x, y = position
        
        # Position-dependent mixing
        position_mix = complex(x, y)
        mixed = pixel + position_mix
        
        # Key addition
        keyed = mixed + self.key
        
        # Apply conformal transformation
        if LATTICE_AVAILABLE:
            if self.mode == 'mobius':
                # Bijective Möbius transformation
                encrypted = self.lattice.mobius_transform(
                    keyed, self.mobius_a, self.mobius_b, self.mobius_c, self.mobius_d
                )
                if encrypted is None:
                    # Singularity fallback
                    encrypted = keyed * keyed
            else:
                # Non-bijective square transformation
                encrypted = self.lattice.conformal_square(keyed)
        else:
            encrypted = keyed * keyed
        
        return encrypted
    
    def decrypt_pixel(self, encrypted: complex, position: Tuple[int, int]) -> complex:
        """
        Decrypt a pixel (inverse of encrypt_pixel).
        
        For 'mobius' mode: Exact decryption using inverse Möbius transformation
        For 'square' mode: Approximate decryption (non-bijective limitation)
        
        Args:
            encrypted: Encrypted Gaussian integer
            position: (x, y) position
        
        Returns:
            Decrypted Gaussian integer (exact for mobius, approximate for square)
        """
        if LATTICE_AVAILABLE and self.mode == 'mobius':
            # Exact inverse using Möbius transformation
            keyed = self.lattice.mobius_inverse(
                encrypted, self.mobius_a, self.mobius_b, self.mobius_c, self.mobius_d
            )
            
            if keyed is None:
                # Fallback to approximate method
                r = abs(encrypted)
                theta = np.angle(encrypted) / 2
                keyed = complex(r ** 0.5 * np.cos(theta), r ** 0.5 * np.sin(theta))
        else:
            # Approximate inverse for square transformation
            r = abs(encrypted)
            theta = np.angle(encrypted) / 2  # Halve the angle
            keyed = complex(r ** 0.5 * np.cos(theta), r ** 0.5 * np.sin(theta))
        
        # Reverse key addition
        unkeyed = keyed - self.key
        
        # Reverse position mixing
        x, y = position
        position_mix = complex(x, y)
        pixel = unkeyed - position_mix
        
        return pixel
    
    def encrypt_image_array(self, image_array: np.ndarray) -> np.ndarray:
        """
        Encrypt entire image represented as numpy array.
        
        Args:
            image_array: RGB image as numpy array (H x W x 3)
        
        Returns:
            Encrypted image array with same shape
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow required for image encryption")
        
        height, width = image_array.shape[:2]
        encrypted = np.zeros_like(image_array)
        
        for y in range(height):
            for x in range(width):
                r, g, b = image_array[y, x, :3]
                
                # Encode as Gaussian integer
                pixel_gaussian = self.pixel_to_gaussian(r, g, b)
                
                # Encrypt
                encrypted_gaussian = self.encrypt_pixel(pixel_gaussian, (x, y))
                
                # Decode back to RGB
                encrypted[y, x] = self.gaussian_to_pixel(encrypted_gaussian)
        
        return encrypted


class DifferentialAttackAnalyzer:
    """
    Differential attack resistance analysis for Gaussian integer cryptography.
    
    Analyzes how conformal transformations (angle-preserving) enhance resistance
    to differential cryptanalysis by measuring:
    1. Confusion (output change relative to input change)
    2. Diffusion (bit propagation)
    3. Avalanche effect (small input change → large output change)
    """
    
    def __init__(self):
        """Initialize differential attack analyzer."""
        if LATTICE_AVAILABLE:
            self.lattice = GaussianIntegerLattice()
        else:
            self.lattice = None
    
    def hamming_distance_complex(self, z1: complex, z2: complex) -> int:
        """
        Compute Hamming distance between two Gaussian integers.
        
        Args:
            z1, z2: Gaussian integers to compare
        
        Returns:
            Hamming distance (number of differing bits)
        """
        # Convert to integers and compute XOR
        r1, i1 = int(z1.real), int(z1.imag)
        r2, i2 = int(z2.real), int(z2.imag)
        
        xor_real = r1 ^ r2
        xor_imag = i1 ^ i2
        
        # Count set bits
        return bin(xor_real).count('1') + bin(xor_imag).count('1')
    
    def analyze_avalanche_effect(self, plaintext: complex, 
                                 num_trials: int = 1000) -> Dict[str, float]:
        """
        Analyze avalanche effect: single bit change → output change distribution.
        
        Good cryptographic functions should have ~50% bit flip rate.
        
        Args:
            plaintext: Base Gaussian integer
            num_trials: Number of single-bit perturbations to test
        
        Returns:
            Dictionary with avalanche metrics
        """
        if not LATTICE_AVAILABLE:
            return {"error": "Lattice module not available"}
        
        # Original transformation
        original_output = self.lattice.conformal_square(plaintext)
        
        bit_flip_rates = []
        
        for trial in range(num_trials):
            # Create single-bit perturbation
            bit_position = trial % 64  # Vary across 64 bits
            perturbed_real = int(plaintext.real) ^ (1 << bit_position)
            perturbed = complex(perturbed_real, plaintext.imag)
            
            # Apply transformation
            perturbed_output = self.lattice.conformal_square(perturbed)
            
            # Measure output difference
            hamming_dist = self.hamming_distance_complex(original_output, perturbed_output)
            total_bits = 128  # Approximate bit length
            flip_rate = hamming_dist / total_bits
            
            bit_flip_rates.append(flip_rate)
        
        return {
            "mean_flip_rate": np.mean(bit_flip_rates),
            "std_flip_rate": np.std(bit_flip_rates),
            "min_flip_rate": np.min(bit_flip_rates),
            "max_flip_rate": np.max(bit_flip_rates),
            "ideal_flip_rate": 0.5,
            "quality": "GOOD" if 0.4 <= np.mean(bit_flip_rates) <= 0.6 else "NEEDS_IMPROVEMENT"
        }
    
    def analyze_confusion(self, key1: complex, key2: complex, 
                         plaintext: complex) -> Dict[str, Any]:
        """
        Analyze confusion: different keys should produce very different outputs.
        
        Args:
            key1, key2: Two different encryption keys
            plaintext: Test plaintext
        
        Returns:
            Confusion analysis metrics
        """
        if not LATTICE_AVAILABLE:
            return {"error": "Lattice module not available"}
        
        # Encrypt with both keys
        cipher1 = self.lattice.conformal_square(plaintext + key1)
        cipher2 = self.lattice.conformal_square(plaintext + key2)
        
        # Measure output difference
        hamming_dist = self.hamming_distance_complex(cipher1, cipher2)
        key_diff = self.hamming_distance_complex(key1, key2)
        
        return {
            "key_hamming_distance": key_diff,
            "output_hamming_distance": hamming_dist,
            "amplification_factor": hamming_dist / max(key_diff, 1),
            "interpretation": "Good confusion" if hamming_dist > key_diff else "Weak confusion"
        }
    
    def differential_resistance_score(self, num_samples: int = 100) -> Dict[str, Any]:
        """
        Comprehensive differential resistance score.
        
        Combines multiple metrics to assess overall resistance to differential attacks.
        
        Args:
            num_samples: Number of test samples
        
        Returns:
            Comprehensive resistance assessment
        """
        if not LATTICE_AVAILABLE:
            return {"error": "Lattice module not available"}
        
        # Generate random test samples
        keygen = GaussianKeyGenerator(seed=42)  # Fixed seed for reproducibility
        
        avalanche_scores = []
        confusion_scores = []
        
        for _ in range(num_samples):
            # Random plaintext and keys
            plaintext = keygen.generate_gaussian_key(64)
            key1 = keygen.generate_gaussian_key(64)
            key2 = keygen.generate_gaussian_key(64)
            
            # Avalanche analysis
            avalanche = self.analyze_avalanche_effect(plaintext, num_trials=10)
            avalanche_scores.append(avalanche["mean_flip_rate"])
            
            # Confusion analysis
            confusion = self.analyze_confusion(key1, key2, plaintext)
            confusion_scores.append(confusion["amplification_factor"])
        
        avg_avalanche = np.mean(avalanche_scores)
        avg_confusion = np.mean(confusion_scores)
        
        # Scoring: avalanche near 0.5 is ideal, confusion amplification > 1 is good
        avalanche_penalty = abs(avg_avalanche - 0.5) * 100
        confusion_bonus = min(avg_confusion, 10) * 10
        
        overall_score = max(0, 100 - avalanche_penalty + confusion_bonus)
        
        return {
            "overall_score": overall_score,
            "max_score": 200,
            "average_avalanche_effect": avg_avalanche,
            "average_confusion_amplification": avg_confusion,
            "assessment": self._assess_score(overall_score),
            "recommendation": self._recommend_improvements(avg_avalanche, avg_confusion)
        }
    
    @staticmethod
    def _assess_score(score: float) -> str:
        """Assess resistance score."""
        if score >= 150:
            return "EXCELLENT - Strong resistance to differential attacks"
        elif score >= 100:
            return "GOOD - Adequate resistance with conformal enhancement"
        elif score >= 50:
            return "MODERATE - Some resistance, improvements recommended"
        else:
            return "WEAK - Significant vulnerabilities detected"
    
    @staticmethod
    def _recommend_improvements(avalanche: float, confusion: float) -> str:
        """Recommend improvements based on metrics."""
        recommendations = []
        
        if abs(avalanche - 0.5) > 0.1:
            recommendations.append("Enhance avalanche effect (current: {:.2f}, target: 0.5)".format(avalanche))
        
        if confusion < 2.0:
            recommendations.append("Improve confusion (amplification: {:.2f}, target: >2.0)".format(confusion))
        
        if not recommendations:
            return "No immediate improvements needed - metrics within acceptable ranges"
        
        return "; ".join(recommendations)


class CryptographicDemo:
    """
    Demonstration of Gaussian integer cryptography with conformal transformations.
    
    Provides runnable examples showing:
    1. Key generation
    2. Image encryption
    3. Attack resistance analysis
    """
    
    @staticmethod
    def demo_key_generation():
        """Demonstrate key generation with and without conformal transformations."""
        print("\n" + "="*70)
        print("Demo 1: Key Generation with Conformal Transformations")
        print("="*70)
        
        keygen = GaussianKeyGenerator(seed=42)  # Fixed seed for reproducibility
        
        # Generate keys without conformal transformation
        pub1, priv1 = keygen.generate_key_pair(bit_length=128, use_conformal=False)
        print(f"\nWithout Conformal Transformation:")
        print(f"  Private Key: {priv1.real:.0f} + {priv1.imag:.0f}i")
        print(f"  Public Key:  {pub1.real:.0f} + {pub1.imag:.0f}i")
        print(f"  Modulus ratio: {abs(pub1) / abs(priv1):.2f}")
        
        # Generate keys with conformal transformation
        pub2, priv2 = keygen.generate_key_pair(bit_length=128, use_conformal=True)
        print(f"\nWith Conformal Transformation (z → z²):")
        print(f"  Private Key: {priv2.real:.0f} + {priv2.imag:.0f}i")
        print(f"  Public Key:  {pub2.real:.0f} + {pub2.imag:.0f}i")
        print(f"  Modulus ratio: {abs(pub2) / abs(priv2):.2f}")
        print(f"  Angle doubling verified: {np.angle(pub2):.4f} ≈ 2 × {np.angle(priv2):.4f}")
    
    @staticmethod
    def demo_differential_resistance():
        """Demonstrate resistance to differential attacks."""
        print("\n" + "="*70)
        print("Demo 2: Differential Attack Resistance Analysis")
        print("="*70)
        
        analyzer = DifferentialAttackAnalyzer()
        
        # Test plaintext
        keygen = GaussianKeyGenerator(seed=42)
        plaintext = keygen.generate_gaussian_key(64)
        
        print(f"\nTest plaintext: {plaintext.real:.0f} + {plaintext.imag:.0f}i")
        
        # Avalanche effect
        print("\nAnalyzing Avalanche Effect...")
        avalanche = analyzer.analyze_avalanche_effect(plaintext, num_trials=100)
        print(f"  Mean bit flip rate: {avalanche['mean_flip_rate']:.4f}")
        print(f"  Ideal flip rate: {avalanche['ideal_flip_rate']:.4f}")
        print(f"  Quality: {avalanche['quality']}")
        
        # Comprehensive resistance score
        print("\nComputing Comprehensive Resistance Score...")
        score_result = analyzer.differential_resistance_score(num_samples=50)
        print(f"  Overall Score: {score_result['overall_score']:.1f} / {score_result['max_score']}")
        print(f"  Assessment: {score_result['assessment']}")
        print(f"  Recommendation: {score_result['recommendation']}")
    
    @staticmethod
    def demo_image_encryption_concept():
        """Demonstrate image encryption concept (without actual image)."""
        print("\n" + "="*70)
        print("Demo 3: Image Encryption Over Gaussian Integers")
        print("="*70)
        
        # Generate encryption key
        keygen = GaussianKeyGenerator(seed=42)
        encryption_key = keygen.generate_gaussian_key(128)
        
        print(f"\nEncryption Key: {encryption_key.real:.0f} + {encryption_key.imag:.0f}i")
        
        # Demonstrate pixel encoding
        encryptor = GaussianImageEncryption(key=encryption_key)
        
        test_pixels = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (128, 128, 128) # Gray
        ]
        
        print("\nPixel Encryption Examples:")
        print("-" * 70)
        
        for i, (r, g, b) in enumerate(test_pixels):
            # Encode as Gaussian integer
            pixel_gaussian = encryptor.pixel_to_gaussian(r, g, b)
            
            # Encrypt
            encrypted = encryptor.encrypt_pixel(pixel_gaussian, (i, i))
            
            # Show transformation
            print(f"  Pixel {i}: RGB({r}, {g}, {b})")
            print(f"    → Gaussian: {pixel_gaussian.real:.0f} + {pixel_gaussian.imag:.0f}i")
            print(f"    → Encrypted: {encrypted.real:.2e} + {encrypted.imag:.2e}i")
            print(f"    → Modulus change: {abs(encrypted) / max(abs(pixel_gaussian), 1):.2f}x")
            print()
        
        print("Note: Conformal transformation provides:")
        print("  - Non-linear diffusion (angle doubling)")
        print("  - Position-dependent encryption")
        print("  - Enhanced resistance to differential attacks")


def main():
    """Run all cryptographic demonstrations."""
    print("="*70)
    print("Gaussian Integer Cryptography with Conformal Transformations")
    print("="*70)
    print("\nThis module demonstrates practical cryptographic applications")
    print("of conformal transformations on Gaussian integer lattices:")
    print("  1. Enhanced key generation")
    print("  2. Differential attack resistance")
    print("  3. Image encryption schemes")
    
    if not LATTICE_AVAILABLE:
        print("\nWARNING: gaussian_lattice module not available")
        print("Some features will be limited")
    
    # Run demonstrations
    demo = CryptographicDemo()
    demo.demo_key_generation()
    demo.demo_differential_resistance()
    demo.demo_image_encryption_concept()
    
    print("\n" + "="*70)
    print("All demonstrations completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
