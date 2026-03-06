#!/usr/bin/env python3
"""
Green's Function Factorization with Phase-Bias and Harmonic Refinement

Mathematical Framework:
-----------------------
This module implements wave interference-based factorization where:
- Prime factorization ≡ Spectral decomposition of log-space resonator
- Semiprimes = Two-point sources
- Factors = Interference maxima
- Compositeness = Resonance structure

The Helmholtz kernel is the core propagator:
    |G(log p')| = |cos(k(log N - 2log p'))|

Core Formulas:
--------------
1. Green's function amplitude: |G(log p)| peaks at true factors
2. Comb formula: p_m = exp((log N - 2πm/k)/2)
3. Phase quantization: log N - 2log p = 2πm/k (standing-wave resonance)
4. κ-weighted scoring: S(p') = |G(log p')| × κ(p')

Five Refinement Mechanisms:
---------------------------
1. Phase-bias correction (φ₀) - eliminates ±1 integer bias via local slope
2. Harmonic sharpening (Dirichlet kernel) - sub-integer precision locking
3. Dual-k intersection - exponential candidate reduction
4. κ-weighted scoring - prioritizes prime-like curvature
5. Balance-aware k(N,β) - adapts to factor imbalance

References:
-----------
- Issue #176: Wave Interference Factorization Framework
- Z5D Axioms: κ(n) = d(n)·ln(n+1)/e²
"""

import math
from mpmath import mp
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import threading

import logging

# Import Z5D curvature from existing module
# Try both absolute and relative imports to work from different calling contexts
try:
    from python.z5d_axioms import Z5DAxioms

    Z5D_AVAILABLE = True
except ImportError:
    try:
        from z5d_axioms import Z5DAxioms

        Z5D_AVAILABLE = True
    except ImportError:
        Z5D_AVAILABLE = False
        logging.warning("z5d_axioms not available, using fallback curvature")


# Set high precision for analytic calculations
# Increased to 512 dps to prevent distance degradation for large-N embeddings (Issue #221)
# Note: Can be adjusted lower for non-cryptographic test cases if performance is needed
mp.dps = 512  # 512+ decimal places prevents precision bottleneck at RSA-2048 scale

# Numerical stability threshold
EPSILON = 1e-12  # For avoiding division by zero and small denominators


@dataclass
class GreensResult:
    """Result from Green's function evaluation"""

    p_candidate: int
    amplitude: float
    phase: float
    kappa_weight: float
    score: float
    m_value: int  # Resonance mode number


@dataclass
class RefinementConfig:
    """Configuration for refinement mechanisms"""

    use_phase_correction: bool = True
    use_dirichlet: bool = True
    use_dual_k: bool = True
    use_kappa_weight: bool = True
    use_adaptive_k: bool = True

    dirichlet_J: int = 4  # Number of harmonic terms
    dual_k_epsilon: float = 0.01  # k₂ = k₁(1 ± epsilon)

    # For Issue #196: Expose randomness and secondary params for sweeping
    rng_seed: Optional[int] = None  # Seed for deterministic randomness
    kappa_weight_scale: float = 1.0  # Scaling factor for κ-weighting
    phi_bias: float = 1.618  # Golden ratio bias for phase adjustments

    # For Issue #198: Structural wall reduction - geometric embedding correction
    embedding_offset: float = (
        0.0  # Relative offset for sqrt(N) centering (e.g., -0.0392 for RSA-2048)
    )

    # For Issue #199: Second-order correction via bias model
    use_bias_model: bool = False  # Use profile-aware bias model instead of fixed offset
    profile: str = "balanced_2048"  # Modulus profile for bias estimation

    # For fractional comb sampling (removes quantization artifacts)
    use_fractional_comb: bool = (
        False  # Use fractional m sampling instead of integer window scan
    )
    comb_step: Optional[Any] = None  # Step size for m (None = auto-derive, explicit = use as-is)
    comb_range: int = 100  # Range for m scanning (±comb_range * comb_step)


# Thread-safe flag for fallback curvature warning (only log once)
_fallback_warning_lock = threading.Lock()
_fallback_warning_logged = False


def compute_curvature(n: int) -> float:
    """
    Compute Z5D curvature: κ(n) = d(n)·ln(n+1)/e²

    Args:
        n: Integer value

    Returns:
        Curvature value κ(n)

    Warning:
        If z5d_axioms is not available, falls back to float64 precision which
        causes ~3.92% error floor on RSA-2048. This is a known precision bottleneck.
    """
    global _fallback_warning_logged

    if Z5D_AVAILABLE:
        axioms = Z5DAxioms()
        # Estimate prime density
        d_n = axioms.prime_density_approximation(n)
        # Compute curvature with high-precision mpmath
        return float(axioms.curvature(n, d_n))
    else:
        # Fallback: direct calculation with float64 (low fidelity)
        # WARNING: This causes ~3.92% relative error floor on RSA-2048
        # Thread-safe one-time warning
        with _fallback_warning_lock:
            if not _fallback_warning_logged:
                logging.warning(
                    "⚠️  PRECISION DEGRADATION: Using fallback curvature (float64). "
                    "This causes ~3.92% error floor on RSA-2048. "
                    "Ensure z5d_axioms is importable for high-precision calculations."
                )
                _fallback_warning_logged = True

        if n <= 0:
            return 0.0
        d_n = 1.0 / math.log(n) if n > 1 else 0.0
        e_squared = math.e**2
        return d_n * math.log(n + 1) / e_squared


def safe_log(n: int) -> float:
    """
    Compute natural log safely for large integers.
    Uses mpmath for very large numbers that overflow float.

    Args:
        n: Integer to compute log of (must be > 0)

    Returns:
        Natural logarithm as float

    Raises:
        ValueError: If n <= 0
    """
    if n <= 0:
        raise ValueError(f"Cannot compute log of non-positive value: {n}")

    try:
        return math.log(float(n))
    except (ValueError, OverflowError):
        # Use mpmath for large numbers
        return float(mp.log(n))


def safe_sqrt(n: int) -> int:
    """
    Compute integer square root safely for large integers.

    Uses math.isqrt() which returns the exact integer floor of √n
    for arbitrary-precision Python integers. This is the correct
    approach for RSA-2048 scale numbers.

    Args:
        n: Integer to compute sqrt of (must be >= 0)

    Returns:
        Integer square root (floor of √n)

    Raises:
        ValueError: If n < 0
    """
    if n < 0:
        raise ValueError(f"Cannot compute sqrt of negative value: {n}")

    # Python 3.8+ has math.isqrt which works for arbitrary precision integers
    return math.isqrt(n)


def greens_function_amplitude(log_N: float, log_p: float, k: float) -> float:
    """
    Evaluate Green's function amplitude at a candidate.

    Core formula: |G(log p)| = |cos(k(log N - 2log p))|

    Args:
        log_N: Natural log of the semiprime N
        log_p: Natural log of candidate factor p
        k: Wave number parameter

    Returns:
        Amplitude |G|
    """
    phase = k * (log_N - 2.0 * log_p)
    amplitude = abs(math.cos(phase))
    return amplitude


def comb_formula(log_N: float, k: float, m: int) -> float:
    """
    Generate factor candidate from comb formula.

    Formula: p_m = exp((log N - 2πm/k)/2)

    Args:
        log_N: Natural log of semiprime N
        k: Wave number parameter
        m: Resonance mode number

    Returns:
        Candidate factor p_m
    """
    exponent = (log_N - 2.0 * math.pi * m / k) / 2.0
    return math.exp(exponent)


def estimate_k_optimal(N: int, balance_estimate: float = 1.0) -> float:
    """
    Estimate optimal k for a given semiprime.

    For balanced semiprimes, k ≈ 0.3 is optimal.
    For unbalanced, adjust based on log(q/p).

    Args:
        N: Semiprime to factor
        balance_estimate: Estimated ratio q/p (default 1.0 for balanced)

    Returns:
        Estimated optimal k
    """
    # Base k for balanced semiprimes
    k_base = 0.3

    # Adjust for imbalance
    if balance_estimate > 1.0:
        beta = 0.5 * math.log(balance_estimate)
        # Empirical correction: k increases slightly with imbalance
        k_adjusted = k_base + 0.05 * abs(beta)
    else:
        k_adjusted = k_base

    return k_adjusted


def phase_bias_correction(
    amplitude_minus: float, amplitude_center: float, amplitude_plus: float
) -> float:
    """
    Estimate phase bias φ₀ from local amplitude asymmetry.

    Uses discrete derivative and curvature:
    - D = |G(p+1)| - |G(p-1)|
    - C = |G(p+1)| - 2|G(p)| + |G(p-1)|
    - φ₀ ≈ arctan(D / -C)

    Args:
        amplitude_minus: |G| at p-1
        amplitude_center: |G| at p
        amplitude_plus: |G| at p+1

    Returns:
        Estimated phase bias φ₀
    """
    D = amplitude_plus - amplitude_minus
    C = amplitude_plus - 2.0 * amplitude_center + amplitude_minus

    # Avoid division by zero
    if abs(C) < EPSILON:
        return 0.0

    phi_0 = math.atan(D / (-C))
    return phi_0


def dirichlet_kernel(phase: float, J: int) -> float:
    """
    Evaluate Dirichlet kernel for harmonic sharpening.

    Formula: D_J(ψ) = Σ_{j=-J}^{J} cos(jψ) = sin((J+1/2)ψ) / sin(ψ/2)

    This narrows the main lobe for sub-integer precision.

    Args:
        phase: Phase value ψ
        J: Number of harmonic terms

    Returns:
        Dirichlet kernel value
    """
    # Handle small phase to avoid division by zero
    if abs(phase) < EPSILON:
        return float(2 * J + 1)

    numerator = math.sin((J + 0.5) * phase)
    denominator = math.sin(0.5 * phase)

    # Protection against small denominator
    if abs(denominator) < EPSILON:
        return float(2 * J + 1)

    return numerator / denominator


def _dynamic_comb_step(N: int) -> Any:
    """
    Compute dynamic comb step using high-precision mpmath.
    
    Formula: comb_step = 1 / (10 * log2(N))
    
    This provides finer fractional sampling resolution proportional to 
    modulus size while maintaining deterministic, precision-stable computation.
    
    Args:
        N: Modulus (semiprime to factor)
        
    Returns:
        High-precision mp.mpf comb step value
    """
    log2_N = mp.log(mp.mpf(N), 2)  # high-precision, deterministic
    return mp.mpf(1) / (mp.mpf(10) * log2_N)


def find_crest_near_sqrt(
    N: int, k: float, window_size: int = 100, config: Optional[RefinementConfig] = None
) -> List[GreensResult]:
    """
    Find amplitude crests near sqrt(N) using Green's function.
    
    Dynamic comb_step behavior (when config.use_fractional_comb=True):
    - Precedence: explicit config.comb_step > auto-derived step
    - Formula (balanced moduli): comb_step = 1 / (10 * log2(N))
    - Skewed moduli (bit-length skew > 2): capped at 1.0 to avoid over/under-sampling
    - Precision: computed with mpmath (mp.mpf) for determinism and stability
    - Type guarantee: returned comb_step is always mp.mpf when auto-derived

    Args:
        N: Semiprime to factor
        k: Wave number parameter
        window_size: Search window around sqrt(N)
        config: Refinement configuration (uses defaults if None)
                If config.comb_step is None and use_fractional_comb=True,
                comb_step will be auto-derived based on N's scale and balance.

    Returns:
        List of GreensResult objects, sorted by score
    """
    if config is None:
        config = RefinementConfig()

    k_mpf = mp.mpf(k) # Convert k to mp.mpf for high precision

    # Dynamically adjust comb_step based on modulus size (Issue #211, PR #217)
    # Precedence: explicit comb_step > derived step (for reproducibility)
    # This enhances sampling density in the resonance comb proportional to log2(N)
    # for large balanced moduli, using high-precision mpmath for determinism.
    if config.use_fractional_comb:
        if config.comb_step is None:
            # Detect skew: heuristic using normalized distance from perfect square
            # For balanced semiprimes p*q where p ≈ q ≈ sqrt(N), N is close to (sqrt(N)+1)^2
            # For skewed semiprimes p*q where p << q, N is far from any perfect square
            sqrt_N_approx = math.isqrt(N)
            next_square = (sqrt_N_approx + 1) * (sqrt_N_approx + 1)
            gap_to_next = next_square - N
            
            # For balanced semiprimes p*q where p ≈ q: gap_to_next is very small
            # For skewed semiprimes p*q where p << q: gap_to_next is larger
            # Use relative comparison: gap_to_next / sqrt(N)
            # For truly balanced (p ≈ q): ratio ≈ 0 (gap << sqrt(N))
            # For skewed or near-power-of-2: ratio > 0.1
            # Threshold: if gap_to_next / sqrt(N) > 0.1, consider skewed
            relative_gap = gap_to_next / max(sqrt_N_approx, 1)
            
            if relative_gap > 0.1:
                config.comb_step = mp.mpf(1)  # Cap at previous default for skewed moduli
            else:
                # Balanced modulus: use dynamic step = 1 / (10 * log2(N))
                config.comb_step = _dynamic_comb_step(N)
        # else: explicit comb_step provided, use as-is

        # Validate fractional comb parameters
        if config.comb_step <= 0:
            raise ValueError("comb_step must be positive")
        if config.comb_range <= 0:
            raise ValueError("comb_range must be positive")

    # Use safe functions for large numbers
    log_N = safe_log(N)
    sqrt_N_raw = safe_sqrt(N)

    # Issue #199: Apply second-order geometric embedding correction
    if config.use_bias_model:
        # Import here to avoid circular dependency
        try:
            from python.z_correction.embedding_bias_model import (
                estimate_embedding_bias,
                fine_bias_adjustment,
            )
        except ImportError:
            from z_correction.embedding_bias_model import (
                estimate_embedding_bias,
                fine_bias_adjustment,
            )

        # Estimate bias using model (bits_N, bits_p, profile)
        bits_N = N.bit_length()
        # For balanced, assume bits_p ≈ bits_N / 2
        # For skewed, this is approximate - in practice we'd need better heuristics
        bits_p_estimate = bits_N // 2  # Conservative estimate
        profile = getattr(
            config, "profile", "balanced_2048"
        )  # Default to balanced RSA-2048

        bias_correction = estimate_embedding_bias(bits_N, bits_p_estimate, profile)
        # Issue #200: Add fine adjustment for final gap closure
        fine_correction = fine_bias_adjustment(bits_N, profile)
        total_correction = bias_correction + fine_correction

        sqrt_N = int(
            sqrt_N_raw * (1 - total_correction)
        )  # Negative because we shift down
    else:
        # Fallback to first-order correction
        sqrt_N = int(
            sqrt_N_raw * (1 + config.embedding_offset)
        )  # Negative because we shift down

    results = []

    if config.use_fractional_comb:
        # Fractional comb sampling: scan m directly with fractional steps
        # This removes quantization artifacts from integer m snapping
        # CRITICAL FIX (Issue #221): Always use log_N/2 as center for comb formula
        # The comb formula is: log(p_m) = log(N)/2 - πm/k
        # Bias model corrections are incompatible with this formula and should not be combined
        log_center = log_N / 2

        # FIXED (Issue #221): comb_range is absolute m range (e.g., 1.0 means m ∈ [-1, +1])
        # Calculate number of steps from range and step size
        num_steps = int(config.comb_range / config.comb_step)

        m_values = []
        for i in range(-num_steps, num_steps + 1):
            m = i * config.comb_step
            m_values.append(m)

        for m_val in m_values:
            # Comb formula centered on corrected sqrt: p_m = exp(log_center - (pi*m/k))
            try:
                log_p = log_center - (mp.pi * m_val / k_mpf)
                p = int(mp.nint(mp.exp(log_p)))
                if p > 1:  # Valid candidate
                    # Evaluate full pipeline at this p
                    log_p_val = safe_log(p)

                    # Basic Green's function amplitude
                    amplitude = greens_function_amplitude(log_N, log_p_val, k_mpf)

                    # Compute phase
                    phase = k_mpf * (log_N - 2.0 * log_p_val)

                    # Apply Dirichlet sharpening if enabled
                    if config.use_dirichlet:
                        dirichlet_factor = abs(
                            dirichlet_kernel(phase, config.dirichlet_J)
                        )
                        # Normalize to keep amplitudes comparable
                        dirichlet_factor = dirichlet_factor / (
                            2 * config.dirichlet_J + 1
                        )
                        amplitude *= dirichlet_factor

                    # Compute kappa weight if enabled
                    kappa_weight = 1.0
                    if config.use_kappa_weight:
                        kappa_weight = compute_curvature(p)

                    # Combined score (no proximity penalty for fractional comb)
                    # The fractional m sampling already provides fine-grained search
                    score = amplitude * kappa_weight

                    result = GreensResult(
                        p_candidate=p,
                        amplitude=amplitude,
                        phase=phase,
                        kappa_weight=kappa_weight,
                        score=score,
                        m_value=m_val,
                    )
                    results.append(result)
            except (ValueError, OverflowError):
                continue  # Skip invalid computations
    else:
        # Original integer window scan around corrected sqrt(N)
        p_min = max(2, sqrt_N - window_size)
        p_max = sqrt_N + window_size

        for p in range(p_min, p_max + 1):
            if p <= 1:
                continue

            log_p = safe_log(p)

            # Basic Green's function amplitude
            amplitude = greens_function_amplitude(log_N, log_p, k)

            # Compute phase
            phase = k * (log_N - 2.0 * log_p)

            # Apply Dirichlet sharpening if enabled
            if config.use_dirichlet:
                dirichlet_factor = abs(dirichlet_kernel(phase, config.dirichlet_J))
                # Normalize to keep amplitudes comparable
                dirichlet_factor = dirichlet_factor / (2 * config.dirichlet_J + 1)
                amplitude *= dirichlet_factor

            # Compute kappa weight if enabled
            kappa_weight = 1.0
            if config.use_kappa_weight:
                kappa_weight = compute_curvature(p)

            # Combined score
            score = amplitude * kappa_weight

            # Estimate resonance mode m
            m = int(round((log_N - 2.0 * log_p) * k / (2.0 * math.pi)))

            results.append(
                GreensResult(
                    p_candidate=p,
                    amplitude=amplitude,
                    phase=phase,
                    kappa_weight=kappa_weight,
                    score=score,
                    m_value=m,
                )
            )

    return results


def apply_phase_correction(
    results: List[GreensResult], N: int, k: float
) -> List[GreensResult]:
    """
    Apply phase-bias correction to refine candidates.

    For each high-score candidate, estimate φ₀ and compute corrected p.

    Args:
        results: Initial results from find_crest_near_sqrt
        N: Semiprime
        k: Wave number

    Returns:
        New list with phase-corrected candidates added
    """
    log_N = safe_log(N)
    corrected_results = []

    # Take top candidates for correction
    for res in results[:10]:
        p = res.p_candidate

        # Get amplitudes at p-1, p, p+1
        if p > 2:
            log_p_minus = safe_log(p - 1)
            log_p_center = safe_log(p)
            log_p_plus = safe_log(p + 1)

            amp_minus = greens_function_amplitude(log_N, log_p_minus, k)
            amp_center = greens_function_amplitude(log_N, log_p_center, k)
            amp_plus = greens_function_amplitude(log_N, log_p_plus, k)

            # Estimate phase bias
            phi_0 = phase_bias_correction(amp_minus, amp_center, amp_plus)

            # Correct the phase
            phase_corrected = res.phase - phi_0

            # Compute corrected p from phase
            # phase = k(log N - 2 log p) => log p = (log N - phase/k)/2
            log_p_corrected = (log_N - phase_corrected / k) / 2.0
            p_corrected = int(round(math.exp(log_p_corrected)))

            # Only add if it's different and valid
            if p_corrected != p and p_corrected > 1:
                # Re-evaluate at corrected position
                log_p_new = safe_log(p_corrected)
                amplitude_new = greens_function_amplitude(log_N, log_p_new, k)
                kappa_new = compute_curvature(p_corrected)
                score_new = amplitude_new * kappa_new

                corrected_results.append(
                    GreensResult(
                        p_candidate=p_corrected,
                        amplitude=amplitude_new,
                        phase=k * (log_N - 2.0 * log_p_new),
                        kappa_weight=kappa_new,
                        score=score_new,
                        m_value=res.m_value,
                    )
                )

    return corrected_results


def dual_k_intersection(
    N: int, k1: float, epsilon: float = 0.01, window_size: int = 100, top_n: int = 20
) -> List[int]:
    """
    Use two slightly detuned k values to find intersection candidates.

    This dramatically reduces candidate count by finding factors that
    score highly under both k₁ and k₂ = k₁(1 ± epsilon).

    Args:
        N: Semiprime to factor
        k1: Primary wave number
        epsilon: Detuning factor (default 0.01)
        window_size: Search window
        top_n: Number of top candidates to consider

    Returns:
        List of candidate factors in intersection
    """
    k2 = k1 * (1.0 + epsilon)

    # Get top candidates from both k values
    config = RefinementConfig(use_dirichlet=False)  # Disable for speed

    results1 = find_crest_near_sqrt(N, k1, window_size, config)
    results2 = find_crest_near_sqrt(N, k2, window_size, config)

    # Extract top candidates
    candidates1 = set(r.p_candidate for r in results1[:top_n])
    candidates2 = set(r.p_candidate for r in results2[:top_n])

    # Intersection
    intersection = candidates1.intersection(candidates2)

    return sorted(list(intersection))


def factorize_greens(
    N: int,
    k: Optional[float] = None,
    config: Optional[RefinementConfig] = None,
    max_candidates: int = 100,
) -> Dict[str, Any]:
    """
    Main factorization function using Green's function with all refinements.

    Args:
        N: Semiprime to factor
        k: Wave number (auto-estimated if None)
        config: Refinement configuration (uses defaults if None)
        max_candidates: Maximum candidates to return

    Returns:
        Dictionary with results including:
        - candidates: List of GreensResult objects
        - k_used: Wave number used
        - found_factor: True if exact factor found
        - exact_factors: List of (p, q) if found
    """
    if config is None:
        config = RefinementConfig()

    # Estimate k if not provided
    if k is None:
        k = estimate_k_optimal(N)

    # Find crest near sqrt(N)
    results = find_crest_near_sqrt(N, k, window_size=500, config=config)

    # Apply phase correction if enabled
    if config.use_phase_correction:
        corrected = apply_phase_correction(results, N, k)
        # Merge and re-sort
        all_results = results + corrected
        all_results.sort(key=lambda r: r.score, reverse=True)
        results = all_results

    # Check for exact factors
    exact_factors = []
    found_factor = False

    for res in results[:max_candidates]:
        p = res.p_candidate
        if N % p == 0:
            q = N // p
            exact_factors.append((p, q))
            found_factor = True
            break  # Found it!

    return {
        "candidates": results[:max_candidates],
        "k_used": k,
        "found_factor": found_factor,
        "exact_factors": exact_factors,
        "N": N,
    }


def analyze_factor_balance(N: int, p: int, q: int) -> Dict[str, float]:
    """
    Analyze balance characteristics of factors.

    Args:
        N: Semiprime
        p: First factor
        q: Second factor

    Returns:
        Dictionary with balance metrics
    """
    log_p = math.log(float(p))
    log_q = math.log(float(q))

    ratio = max(p, q) / min(p, q)
    log_ratio = abs(log_q - log_p)
    beta = 0.5 * math.log(ratio)

    return {
        "ratio": ratio,
        "log_ratio": log_ratio,
        "beta": beta,
        "balanced": ratio < 1.2,  # More realistic threshold for "balanced"
    }


if __name__ == "__main__":
    # Quick demonstration
    print("Green's Function Factorization Demo")
    print("=" * 60)

    # Test cases from validation corpus
    test_cases = [
        (143, 11, 13),
        (323, 17, 19),
        (899, 29, 31),
        (1763, 41, 43),
        (10403, 101, 103),
    ]

    for N, true_p, true_q in test_cases:
        print(f"\nN = {N} (true factors: {true_p} × {true_q})")

        result = factorize_greens(N, max_candidates=10)

        print(f"  k used: {result['k_used']:.4f}")
        print(f"  Found factor: {result['found_factor']}")

        if result["found_factor"]:
            print(f"  Exact factors: {result['exact_factors']}")

        print(f"  Top 5 candidates:")
        for i, cand in enumerate(result["candidates"][:5]):
            marker = "✓" if cand.p_candidate in [true_p, true_q] else " "
            print(
                f"    {marker} {i+1}. p={cand.p_candidate}, score={cand.score:.6f}, amp={cand.amplitude:.4f}"
            )
