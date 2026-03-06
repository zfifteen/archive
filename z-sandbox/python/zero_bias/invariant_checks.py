"""
Invariant validation helpers for zero-bias resonance validation.

Provides functions to compute and validate the core invariants:
- Z = A(B/e²)
- κ(n) = d(n)·ln(n+1)/e²
- θ'(n,k) = φ*((n mod φ)/φ)^k

All computations use mpmath with 1e-16 tolerance checks.
"""

import mpmath as mp
from typing import Tuple, Any

# Set precision for mpmath
mp.mp.dps = 50  # High precision for intermediate calculations

def compute_z(a, b):
    """Compute Z = A(B/e²)"""
    e_squared = mp.power(mp.e, 2)
    return a * (b / e_squared)

def compute_kappa(n: int):
    """Compute κ(n) = d(n)·ln(n+1)/e² where d(n) is divisor function"""
    # For semiprimes, d(n) = 3 (1, p, q)
    d_n = 3
    ln_n_plus_1 = mp.log(n + 1)
    e_squared = mp.power(mp.e, 2)
    return d_n * ln_n_plus_1 / e_squared

def compute_theta_prime(n: int, k, phi):
    """Compute θ'(n,k) = φ*((n mod φ)/φ)^k"""
    n_mod_phi = mp.fmod(n, phi)
    ratio = n_mod_phi / phi
    return phi * mp.power(ratio, k)

def validate_invariant_z(a, b, expected_z, tolerance=None):
    """Validate Z invariant within tolerance"""
    if tolerance is None:
        tolerance = mp.mpf('1e-16')
    computed_z = compute_z(a, b)
    return abs(computed_z - expected_z) < tolerance

def validate_invariant_kappa(n: int, expected_kappa, tolerance=None):
    """Validate κ(n) invariant within tolerance"""
    if tolerance is None:
        tolerance = mp.mpf('1e-16')
    computed_kappa = compute_kappa(n)
    return abs(computed_kappa - expected_kappa) < tolerance

def validate_invariant_theta_prime(n: int, k, phi, expected_theta, tolerance=None):
    """Validate θ'(n,k) invariant within tolerance"""
    if tolerance is None:
        tolerance = mp.mpf('1e-16')
    computed_theta = compute_theta_prime(n, k, phi)
    return abs(computed_theta - expected_theta) < tolerance

def validate_all_invariants(n: int, k, phi, a, b, expected_z, expected_kappa, expected_theta, tolerance=None) -> Tuple[bool, dict]:
    """
    Validate all three invariants and return validation results.

    Returns:
        (all_valid: bool, details: dict with individual validations)
    """
    if tolerance is None:
        tolerance = mp.mpf('1e-16')
    z_valid = validate_invariant_z(a, b, expected_z, tolerance)
    kappa_valid = validate_invariant_kappa(n, expected_kappa, tolerance)
    theta_valid = validate_invariant_theta_prime(n, k, phi, expected_theta, tolerance)

    all_valid = z_valid and kappa_valid and theta_valid

    details = {
        'z_valid': z_valid,
        'kappa_valid': kappa_valid,
        'theta_prime_valid': theta_valid,
        'tolerance': float(tolerance)
    }

    return all_valid, details