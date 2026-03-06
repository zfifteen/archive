#!/usr/bin/env python3
"""
Z Framework Utility Functions

Implements core Z Framework features for QMC bias:
- κ(n): Curvature weight for candidate normalization
- θ′(n,k): Phase-biased sampling with golden ratio modulation

Mathematical Definitions:
- κ(n) = d(n) * ln(n+1) / exp(2)
  where d(n) ≈ 1/ln(n) is prime density from PNT
  
- θ′(n,k) = φ * ((n mod φ) / φ)^k
  where φ = (1 + √5)/2 is the golden ratio
  and k ≈ 0.3 is recommended for distant-factor bias
"""

import math
from typing import Union
import numpy as np

# Constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618033988749
E2 = math.exp(2)  # e² ≈ 7.389056098931


def prime_density(n: Union[int, float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Prime density approximation d(n) ≈ 1/ln(n) from Prime Number Theorem.
    
    Args:
        n: Integer position or array of positions
        
    Returns:
        Approximate prime density at n
    """
    if isinstance(n, np.ndarray):
        # Vectorized version
        result = np.zeros_like(n, dtype=float)
        valid = n > 1
        result[valid] = 1.0 / np.log(n[valid])
        return result
    else:
        # Scalar version
        if n <= 1:
            return 0.0
        return 1.0 / math.log(n)


def kappa(n: Union[int, float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Curvature weight function: κ(n) = d(n) * ln(n+1) / e²
    
    Used for candidate normalization in QMC sampling.
    Provides geometric weighting based on discrete curvature.
    
    Args:
        n: Integer position or array of positions
        
    Returns:
        Curvature weight κ(n)
    """
    if isinstance(n, np.ndarray):
        # Vectorized version
        d_n = prime_density(n)
        log_term = np.log(n + 1)
        return d_n * log_term / E2
    else:
        # Scalar version
        if n < 0:
            return 0.0
        d_n = prime_density(n)
        log_term = math.log(n + 1)
        return d_n * log_term / E2


def theta_prime(n: Union[int, float, np.ndarray], k: float = 0.3) -> Union[float, np.ndarray]:
    """
    Geometric resolution: θ′(n,k) = φ * ((n mod φ) / φ)^k
    
    Phase-biased sampling function with golden ratio modulation.
    Recommended k ≈ 0.3 for distant-factor RSA semiprimes.
    
    Args:
        n: Integer position or array of positions
        k: Resolution exponent (default: 0.3 for distant factors)
        
    Returns:
        θ′(n,k) value for phase-biased sampling
    """
    if isinstance(n, np.ndarray):
        # Vectorized version
        n_mod_phi = n % PHI
        ratio = n_mod_phi / PHI
        ratio_pow = np.power(ratio, k)
        return PHI * ratio_pow
    else:
        # Scalar version
        n_mod_phi = n % PHI
        ratio = n_mod_phi / PHI
        ratio_pow = ratio ** k
        return PHI * ratio_pow


def z_bias_factor(n: Union[int, float, np.ndarray], k: float = 0.3) -> Union[float, np.ndarray]:
    """
    Combined Z-bias factor: (1 + κ(n)) * θ′(n,k)
    
    Combines curvature weight and phase-biased sampling for
    enhanced QMC candidate generation.
    
    Args:
        n: Integer position or array of positions
        k: Resolution exponent (default: 0.3)
        
    Returns:
        Combined bias factor for QMC sampling
    """
    kappa_n = kappa(n)
    theta_n = theta_prime(n, k)
    return (1.0 + kappa_n) * theta_n


def apply_z_bias(points: np.ndarray, N: int, k: float = 0.3) -> np.ndarray:
    """
    Apply Z-bias to QMC points for factorization sampling.
    
    Transforms uniform QMC points in [0,1]^d to biased samples
    around √N using Z Framework features.
    
    Args:
        points: QMC points in [0,1]^d, shape (n_samples, d)
        N: RSA modulus to factor
        k: Resolution exponent (default: 0.3)
        
    Returns:
        Biased candidate points around √N
    """
    # Handle large integers by using Python's integer power
    sqrt_N = float(N ** 0.5) if N > 2**53 else math.sqrt(N)
    
    # Scale points to candidates around √N
    # Use adaptive range based on N's bit length
    bit_length = N.bit_length()
    if bit_length <= 64:
        spread = 0.15  # 15% for small N
    elif bit_length <= 128:
        spread = 0.10  # 10% for medium N
    else:
        spread = 0.05  # 5% for large N
    
    # Transform [0,1] to [sqrt_N * (1-spread), sqrt_N * (1+spread)]
    candidates = sqrt_N * (1 - spread + 2 * spread * points[:, 0])
    
    # Apply Z-bias
    bias = z_bias_factor(candidates, k)
    
    # Normalize bias to avoid extreme values
    bias_normalized = bias / np.mean(bias)
    
    # Apply bias as multiplicative factor
    biased_candidates = candidates * bias_normalized
    
    return biased_candidates


if __name__ == "__main__":
    # Simple demonstration
    print("Z Framework Functions Demo")
    print("=" * 50)
    
    # Test with scalar values
    n_test = 1000
    print(f"\nTest n = {n_test}:")
    print(f"  d(n)     = {prime_density(n_test):.6e}")
    print(f"  κ(n)     = {kappa(n_test):.6e}")
    print(f"  θ'(n,0.3) = {theta_prime(n_test, 0.3):.6f}")
    print(f"  z_bias   = {z_bias_factor(n_test, 0.3):.6f}")
    
    # Test with array values
    n_array = np.array([100, 1000, 10000, 100000])
    print(f"\nVectorized test:")
    print(f"  n        = {n_array}")
    print(f"  κ(n)     = {kappa(n_array)}")
    print(f"  θ'(n,0.3) = {theta_prime(n_array, 0.3)}")
    
    # Test QMC bias application
    print(f"\nQMC bias application (N=RSA-129):")
    N_rsa129 = 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058980949815834421580093501940323646295439459
    points = np.random.random((5, 1))  # 5 sample points
    biased = apply_z_bias(points, N_rsa129, k=0.3)
    print(f"  Sample biased candidates: {biased[:3]}")
