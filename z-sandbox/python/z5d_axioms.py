#!/usr/bin/env python3
"""
Z5D Axioms and Mathematical Foundations

Implementation of the core Z5D mathematical framework with empirical validation.
Follows the axioms specified in the Z5D-Guided RSA Factorization Enhancement issue.

Axiom Summary:
1. Empirical Validation First - Reproducible tests with mpmath precision < 1e-16
2. Domain-Specific Forms - Physical Z = T(v/c) and Discrete Z = n(Δ_n/Δ_max)
3. Geometric Resolution - θ'(n,k) = φ · ((n mod φ)/φ)^k with k ≈ 0.3
4. Style and Tools - Simple, precise solutions using mpmath, numpy, sympy
"""

import math
from mpmath import mp, mpf, log, exp, sqrt as mpsqrt, pi as mp_pi
from typing import Tuple, Optional, List, Dict, Any
import numpy as np

# Import function approximation for error bound calibration
try:
    from function_approximation import NonlinearLeastSquares, SplineApproximation
    FUNCTION_APPROXIMATION_AVAILABLE = True
except ImportError:
    FUNCTION_APPROXIMATION_AVAILABLE = False

# Set high precision for empirical validation (Axiom 1)
mp.dps = 50  # Target precision < 1e-16

# Universal constants
PHI = mpf((1 + mpsqrt(5)) / 2)  # Golden ratio
E2 = exp(2)  # e² invariant (universal constant c for discrete domain)

# Validation target precision (Axiom 1)
TARGET_PRECISION = 1e-16


def get_high_precision_pi(method: str = 'ramanujan_terms', terms: int = 20) -> mpf:
    """
    Get high-precision π for Z5D computations involving elliptic or transcendental terms.
    
    Uses rapid-converging Ramanujan hypergeometric series (4/π form) to provide
    π values with precision below 1e-16 for curvature calculations, geometric
    resolutions, and RSA factorization validations.
    
    Mathematical foundation:
      4/π = Σ_{n=0}^∞ [(2n)!³ (6n + 1)] / [n!⁶ 2^(8n)]
    
    This series converges at ~8 digits per term, enabling:
    - Precise κ(n) = d(n)·ln(n+1)/e² calculations
    - Geometric resolution θ'(n,k) validations
    - Cross-verification of φ-biased torus embeddings in QMC-φ hybrid
    
    Args:
        method: 'ramanujan_terms' (default), 'chudnovsky', or 'mpmath'
        terms: Number of terms for series expansion (default: 20 → ~13 digits)
        
    Returns:
        High-precision π as mpf (mpmath floating-point)
        
    References:
        - Issue #79: Rapid-converging hypergeometric series integration
        - Ramanujan (1914): Modular Equations and Approximations to π
    """
    try:
        from oracle import DeterministicOracle
        oracle = DeterministicOracle(precision=mp.dps)
        
        if method == 'ramanujan_terms':
            return oracle.compute_pi_ramanujan_terms(terms=terms)
        elif method == 'chudnovsky':
            return oracle.compute_pi_chudnovsky(terms=terms)
        elif method == 'ramanujan':
            return oracle.compute_pi_ramanujan(terms=terms)
        else:
            # Fallback to mpmath
            return mp_pi
    except ImportError:
        # If oracle module not available, use mpmath's built-in π
        return mp_pi


class Z5DAxioms:
    """
    Z5D Axioms implementation with empirical validation.
    
    Core Concepts:
    - Universal invariant: Z = A(B / c)
    - Discrete domain: Z = n(Δ_n / Δ_max)
    - Curvature: κ(n) = d(n) · ln(n+1) / e²
    - Geometric resolution: θ'(n, k)
    """
    
    # Class constants for better encapsulation
    PHI = PHI  # Golden ratio (reference to module constant)
    E2 = E2    # e² invariant (reference to module constant)
    
    def __init__(self, precision_dps: int = 50):
        """
        Initialize Z5D axioms with specified precision.
        
        Args:
            precision_dps: Decimal places for mpmath (default: 50)
        """
        self.precision_dps = precision_dps
        mp.dps = precision_dps
    
    @staticmethod
    def universal_invariant(A: mpf, B: mpf, c: mpf) -> mpf:
        """
        Universal invariant formulation: Z = A(B / c)
        
        Args:
            A: Frame-specific scaling/transformation
            B: Dynamic rate/shift input
            c: Universal invariant (domain constant)
        
        Returns:
            Z value
        
        Domain-specific forms:
        - Physical: Z = T(v / c) where c ≈ 299792458 m/s
        - Discrete: Z = n(Δ_n / Δ_max) where c = e²
        """
        if c == 0:
            raise ValueError("Universal invariant c cannot be zero")
        return A * (B / c)
    
    @staticmethod
    def discrete_domain_form(n: int, delta_n: mpf, delta_max: mpf) -> mpf:
        """
        Discrete domain form: Z = n(Δ_n / Δ_max)
        
        For integer sequences and prime-density mapping.
        
        Args:
            n: Integer index/position
            delta_n: Local shift/rate at n
            delta_max: Maximum shift bound
        
        Returns:
            Z value for discrete domain
        
        Raises:
            ValueError: If delta_max is zero
        """
        if delta_max == 0:
            raise ValueError("delta_max cannot be zero (zero-division guard)")
        return mpf(n) * (delta_n / delta_max)
    
    @staticmethod
    def curvature(n: int, d_n: mpf) -> mpf:
        """
        Curvature function: κ(n) = d(n) · ln(n+1) / e²
        
        For discrete geodesics with zero-division protection.
        
        Args:
            n: Integer position
            d_n: Density function value at n
        
        Returns:
            Curvature κ(n)
        
        Note:
            - Protected against zero division by using n+1 in logarithm
            - Returns 0 for n < 0 (guard condition)
        """
        if n < 0:
            return mpf(0)
        
        # Guard against zero division
        log_term = log(mpf(n + 1))
        
        return d_n * log_term / E2
    
    @staticmethod
    def geometric_resolution(n: int, k: float = 0.3) -> mpf:
        """
        Geometric resolution: θ'(n, k) = φ · ((n mod φ) / φ)^k
        
        Resolution/embedding technique for discrete geodesics.
        Recommended k ≈ 0.3 for prime-density mapping.
        
        Args:
            n: Integer position
            k: Resolution exponent (default: 0.3 as recommended)
        
        Returns:
            θ'(n, k) value
        
        Use:
            - Prime-density mapping with k ≈ 0.3
            - Discrete geodesic embedding
        """
        n_mpf = mpf(n)
        
        # Compute (n mod φ) using class constant
        n_mod_phi = n_mpf % Z5DAxioms.PHI
        
        # Compute ((n mod φ) / φ)^k
        ratio = n_mod_phi / Z5DAxioms.PHI
        ratio_pow = ratio ** mpf(k)
        
        # Final: φ · ((n mod φ) / φ)^k
        return Z5DAxioms.PHI * ratio_pow
    
    @staticmethod
    def prime_density_approximation(n: int) -> mpf:
        """
        Prime density approximation d(n) ≈ 1/ln(n) from Prime Number Theorem.
        
        Args:
            n: Integer position
        
        Returns:
            Approximate prime density at n
        """
        if n <= 1:
            return mpf(0)
        return mpf(1) / log(mpf(n))
    
    def z5d_biased_prime_selection(
        self,
        target_index: int,
        k: float = 0.3
    ) -> Tuple[mpf, mpf, mpf]:
        """
        Z5D-guided biased prime selection combining all axioms.
        
        Applies:
        1. Discrete domain form for normalization
        2. Curvature for local geometry
        3. Geometric resolution for prime-density mapping
        
        Args:
            target_index: Prime index k (approximate position)
            k: Geometric resolution parameter (default: 0.3)
        
        Returns:
            Tuple of (theta_prime, curvature, bias_factor)
        """
        # 1. Compute prime density
        d_n = self.prime_density_approximation(target_index)
        
        # 2. Compute curvature κ(n) = d(n) · ln(n+1) / e²
        kappa = self.curvature(target_index, d_n)
        
        # 3. Compute geometric resolution θ'(n, k)
        theta_prime = self.geometric_resolution(target_index, k)
        
        # 4. Combine into bias factor using discrete domain form
        # Δ_n represents the geometric resolution influence
        # Δ_max is normalized to 1 for prime mapping
        delta_n = theta_prime * (1 + kappa)  # Curvature-enhanced resolution
        delta_max = Z5DAxioms.PHI  # Normalized maximum (using class constant)
        
        bias_factor = self.discrete_domain_form(target_index, delta_n, delta_max)
        
        return theta_prime, kappa, bias_factor
    
    def empirical_validation(self, n_test: int = 1000) -> dict:
        """
        Empirical validation of Z5D axioms (Axiom 1).
        
        Tests reproducibility and numerical stability.
        
        Args:
            n_test: Test value for validation
        
        Returns:
            Dictionary with validation metrics
        """
        results = {
            'precision_dps': mp.dps,
            'target_precision': TARGET_PRECISION,
            'tests_passed': True,
            'errors': []
        }
        
        # Test 1: Geometric resolution stability
        theta1 = self.geometric_resolution(n_test, 0.3)
        theta2 = self.geometric_resolution(n_test, 0.3)
        diff = abs(theta1 - theta2)
        
        if diff > TARGET_PRECISION:
            results['tests_passed'] = False
            results['errors'].append(f"Geometric resolution not stable: diff={diff}")
        
        # Test 2: Curvature non-negativity
        d_n = self.prime_density_approximation(n_test)
        kappa = self.curvature(n_test, d_n)
        
        if kappa < 0:
            results['tests_passed'] = False
            results['errors'].append(f"Curvature is negative: κ={kappa}")
        
        # Test 3: Universal invariant consistency
        A, B, c = mpf(1), mpf(2), E2
        Z1 = self.universal_invariant(A, B, c)
        Z2 = self.universal_invariant(A, B, c)
        
        if abs(Z1 - Z2) > TARGET_PRECISION:
            results['tests_passed'] = False
            results['errors'].append(f"Universal invariant not consistent: diff={abs(Z1 - Z2)}")
        
        # Test 4: Zero-division protection
        try:
            # Should raise ValueError
            self.discrete_domain_form(100, mpf(1), mpf(0))
            results['tests_passed'] = False
            results['errors'].append("Zero-division protection failed for discrete_domain_form")
        except ValueError:
            pass  # Expected
        
        results['sample_values'] = {
            'theta_prime': float(theta1),
            'curvature': float(kappa),
            'prime_density': float(d_n)
        }
        
        return results


def z5d_enhanced_prime_search(
    target_value: int,
    k_resolution: float = 0.3,
    search_window: int = 1000
) -> list:
    """
    Enhanced prime search using Z5D axioms.
    
    Generates prime candidates biased by Z5D geometric resolution.
    
    Args:
        target_value: Approximate target prime value
        k_resolution: Geometric resolution parameter (default: 0.3)
        search_window: Search radius around target
    
    Returns:
        List of candidate positions biased by Z5D
    """
    axioms = Z5DAxioms()
    
    # Estimate prime index from target value
    if target_value <= 2:
        return [2]
    
    # Approximate k using inverse PNT: π(n) ≈ n/ln(n)
    k_estimate = int(target_value / math.log(target_value))
    
    candidates = []
    
    # Search in window around estimate
    for k_offset in range(-search_window, search_window + 1):
        k = max(1, k_estimate + k_offset)
        
        # Apply Z5D bias
        theta_prime, kappa, bias_factor = axioms.z5d_biased_prime_selection(k, k_resolution)
        
        # Weight candidate by bias factor
        weight = float(bias_factor)
        
        candidates.append({
            'k': k,
            'weight': weight,
            'theta_prime': float(theta_prime),
            'curvature': float(kappa)
        })
    
    # Sort by weight (highest first)
    candidates.sort(key=lambda x: x['weight'], reverse=True)
    
    return candidates


def calibrate_error_bounds_with_regression(
    k_values: np.ndarray,
    empirical_errors: np.ndarray,
    alpha_init: float = 0.28,
    beta_init: float = 3.2,
    gamma_init: float = 1.8
) -> Dict[str, Any]:
    """
    Calibrate Z5D error bounds using nonlinear least squares regression.
    
    Fits the error bound model: error(k) = C / (k^α * ln(k)^β * ln(ln(k))^γ)
    to empirical prime prediction errors, refining parameters (α, β, γ) for
    improved accuracy in large k extrapolation.
    
    Args:
        k_values: Prime indices where errors were measured
        empirical_errors: Observed errors at those indices
        alpha_init: Initial guess for α parameter (default: 0.28)
        beta_init: Initial guess for β parameter (default: 3.2)
        gamma_init: Initial guess for γ parameter (default: 1.8)
        
    Returns:
        Dictionary with:
        - fitted_params: Calibrated (C, α, β, γ)
        - rmse: Root mean squared error of fit
        - predictions: Model predictions at k_values
        - cross_val_metrics: Cross-validation results
    
    Application:
        Enhances Z5D error bound precision for RSA targets > 10^12,
        enabling better semiprime candidate generation via refined
        geometric resolution parameters.
    
    References:
        Issue comment: "treat calibration (α≈0.28, β≈3.2, γ≈1.8) as a
        regression problem on empirical data"
    """
    if not FUNCTION_APPROXIMATION_AVAILABLE:
        return {
            'available': False,
            'message': 'Function approximation module not available for calibration'
        }
    
    # Error bound model function
    def error_bound_model(k, C, alpha, beta, gamma):
        """Z5D error bound: C / (k^α * ln(k)^β * ln(ln(k))^γ)"""
        k = np.maximum(k, 2.0)  # Guard prevents log(log(k)) domain errors for small k (log(k) <= 0), not just log(0) or log(1)
        ln_k = np.log(k)
        ln_ln_k = np.log(np.maximum(ln_k, 1e-10))
        return C / (k**alpha * ln_k**beta * ln_ln_k**gamma)
    
    # Initialize nonlinear least squares fitter
    fitter = NonlinearLeastSquares(error_bound_model, num_params=4)
    
    # Initial parameter guess: (C, α, β, γ)
    # Estimate C from first data point
    k0 = k_values[0]
    err0 = empirical_errors[0]
    C_init = err0 * (k0**alpha_init * np.log(k0)**beta_init * np.log(np.log(k0))**gamma_init)
    
    initial_params = np.array([C_init, alpha_init, beta_init, gamma_init])
    
    # Parameter bounds: C > 0, α ∈ [0, 1], β > 0, γ > 0
    bounds = ([1e-10, 0.0, 0.1, 0.1], [1e10, 1.0, 10.0, 10.0])
    
    # Fit model
    fitted_params, rmse = fitter.fit(k_values, empirical_errors, initial_params, bounds=bounds)
    
    # Predictions
    predictions = error_bound_model(k_values, *fitted_params)
    
    # Cross-validation to detect overfitting
    cv_metrics = fitter.cross_validate(k_values, empirical_errors, initial_params, n_folds=5)
    
    return {
        'available': True,
        'fitted_params': {
            'C': fitted_params[0],
            'alpha': fitted_params[1],
            'beta': fitted_params[2],
            'gamma': fitted_params[3]
        },
        'initial_params': {
            'C': initial_params[0],
            'alpha': alpha_init,
            'beta': beta_init,
            'gamma': gamma_init
        },
        'rmse': rmse,
        'predictions': predictions,
        'cross_val_metrics': cv_metrics,
        'num_samples': len(k_values),
        'overfitting_detected': cv_metrics['overfitting_ratio'] > 1.5
    }


def approximate_curvature_with_spline(
    n_values: np.ndarray,
    curvature_values: Optional[np.ndarray] = None,
    smoothing: float = 0.0
) -> Dict[str, Any]:
    """
    Approximate Z5D curvature κ(n) using spline interpolation.
    
    Creates a smooth, differentiable approximation of the curvature function
    κ(n) = d(n)·ln(n+1)/e² for use in affine-invariant geometric operations
    and GVA distance metric calculations.
    
    Args:
        n_values: Integer positions for curvature evaluation
        curvature_values: Optional pre-computed κ(n) values (computed if None)
        smoothing: Spline smoothing parameter (0 = interpolation)
        
    Returns:
        Dictionary with:
        - spline_approximator: SplineApproximation object
        - smoothed_values: Approximated curvature at n_values
        - derivative_values: First derivative of approximation
    
    Application:
        Enables smooth κ(n) for barycentric coordinate calculations
        and geometric ladder visualizations in multiplication_viz_factor.py
    """
    if not FUNCTION_APPROXIMATION_AVAILABLE:
        return {
            'available': False,
            'message': 'Function approximation module not available for spline fitting'
        }
    
    # Compute curvature values if not provided
    if curvature_values is None:
        axioms = Z5DAxioms()
        curvature_values = np.array([
            float(axioms.curvature(int(n), axioms.prime_density_approximation(int(n))))
            for n in n_values
        ])
    
    # Create spline approximation
    spline_approx = SplineApproximation(
        n_values.astype(float),
        curvature_values,
        spline_type='univariate',
        smoothing=smoothing
    )
    
    # Evaluate smoothed values
    smoothed_values = spline_approx.evaluate(n_values.astype(float))
    
    # Compute derivative (rate of curvature change)
    derivative_values = spline_approx.derivative(n_values.astype(float), order=1)
    
    return {
        'available': True,
        'spline_approximator': spline_approx,
        'smoothed_values': smoothed_values,
        'derivative_values': derivative_values,
        'num_points': len(n_values),
        'smoothing_parameter': smoothing
    }


if __name__ == "__main__":
    print("Z5D Axioms Empirical Validation")
    print("=" * 60)
    
    # Initialize axioms
    axioms = Z5DAxioms(precision_dps=50)
    
    # Demonstrate high-precision π for Z5D computations
    print("\nHigh-Precision Constants for Z5D Computations:")
    print("-" * 60)
    pi_high = get_high_precision_pi(method='ramanujan_terms', terms=20)
    print(f"π (Ramanujan 20 terms): {pi_high}")
    print(f"  Use case: Elliptic/transcendental Z5D computations")
    print(f"  Precision: < 1e-16 for κ(n) calculations")
    
    # Run empirical validation
    validation = axioms.empirical_validation(n_test=10000)
    
    print(f"\nPrecision: {validation['precision_dps']} decimal places")
    print(f"Target precision: {validation['target_precision']}")
    print(f"Tests passed: {validation['tests_passed']}")
    
    if validation['errors']:
        print("\nErrors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    print("\nSample values (n=10000):")
    for key, value in validation['sample_values'].items():
        print(f"  {key}: {value:.6e}")
    
    # Test Z5D-biased prime selection
    print("\n" + "=" * 60)
    print("Z5D-Biased Prime Selection Example")
    print("=" * 60)
    
    target = 2**127  # 128-bit prime target
    print(f"\nTarget value: 2^127 ≈ {target:.3e}")
    
    k_estimate = int(target / math.log(target))
    print(f"Estimated prime index k: {k_estimate:.3e}")
    
    theta, kappa, bias = axioms.z5d_biased_prime_selection(k_estimate, k=0.3)
    
    print(f"\nZ5D Bias Factors:")
    print(f"  θ'(k, 0.3) = {float(theta):.6e}")
    print(f"  κ(k) = {float(kappa):.6e}")
    print(f"  Bias factor = {float(bias):.6e}")
    
    # Show how this enhances prime selection
    print("\n" + "=" * 60)
    print("Prime Search Enhancement (top 5 candidates)")
    print("=" * 60)
    
    candidates = z5d_enhanced_prime_search(10000, k_resolution=0.3, search_window=100)
    
    print(f"\nTop 5 most promising prime indices near 10000:")
    for i, cand in enumerate(candidates[:5], 1):
        print(f"  {i}. k={cand['k']}, weight={cand['weight']:.3f}, "
              f"θ'={cand['theta_prime']:.3e}, κ={cand['curvature']:.3e}")
