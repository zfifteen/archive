#!/usr/bin/env python3
"""
Geodesic Utilities for Z5D Factorization Ladder

Implements geodesic embeddings θ'(n,k) = φ · ((n mod φ)/φ)^k and curvature κ(n) = d(n) · ln(n+1) / e²
"""

import mpmath as mp
import math

mp.dps = 50

phi = mp.mpf((1 + mp.sqrt(5)) / 2)
e = mp.e

def divisor_function(n):
    """
    Compute the number of divisors d(n)
    """
    if n == 1:
        return 1
    count = 2  # 1 and n
    sqrt_n = int(mp.sqrt(n)) + 1
    for i in range(2, sqrt_n):
        if n % i == 0:
            if i == n // i:
                count += 1
            else:
                count += 2
    return count

def theta_prime(n, k=0.3):
    """
    Compute geodesic resolution θ'(n,k) = φ · ((n mod φ)/φ)^k
    """
    mod_phi = mp.fmod(n, phi)
    ratio = mod_phi / phi
    return phi * mp.power(ratio, k)

def kappa(n):
    """
    Compute curvature κ(n) = d(n) · ln(n+1) / e²
    """
    d_n = divisor_function(n)
    ln_term = mp.log(mp.mpf(n) + 1)
    return d_n * ln_term / (e ** 2)

def z_invariant(n, delta_max):
    """
    Compute Z invariant Z = n(Δ_n / Δ_max) with Δ_n = [d(n) - 3]^2
    """
    d_n = divisor_function(n)
    delta_n = (d_n - 3) ** 2
    return n * (delta_n / delta_max)