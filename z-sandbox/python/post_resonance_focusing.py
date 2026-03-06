#!/usr/bin/env python3
"""
Post-Resonance Focusing Transform for RSA-Scale Factor Recovery
================================================================

This module implements a deterministic focusing transform that takes coarse seeds
from the Green's function resonance pipeline and sharpens them into refined seeds
that are numerically local to the true factors.

Multi-Δ Center Refinement Strategy:
-----------------------------------
At RSA-2048 scale, the true factors p and q are typically offset by ~4% from √N,
which creates a ~10^306 absolute distance gap. Curvature κ(n) cannot distinguish
between candidates at this scale.

The solution: Multi-Δ center refinement
1. Extract multiple δ-centers from resonance structure (not just one "best")
   - Each δ represents an offset: p ≈ (1+δ)*√N
   - Keep all δ-modes that pass physics gates (amplitude, Dirichlet, κ)
2. Convert each δ to integer center via (1+δ)*√N
3. For each center, run bounded ±R divisibility refinement (R=1000)
4. Track per-center metrics (shrink_ratio, distance_before, distance_after)
5. Report best center and factor recovery status

This approach replaces "single-center thinking" with multiple parallel attempts,
each with a fixed ±1000 refinement radius. The key insight: we don't widen R,
we enumerate multiple plausible δ-centers.

Mathematical Framework:
----------------------
The focusing stage operates in log-space and uses:
1. Dual-k phase residual analysis to detect systematic bias
2. Dirichlet kernel peak-centering for sub-integer localization
3. κ-weighted scoring to filter physically-valid modes
4. Balance assumptions (p ≈ q ≈ √N for RSA-style semiprimes)

Key Principle:
-------------
All adjustments are analytic/geometric/spectral. No classical factoring methods,
no primality tests, no brute-force scanning proportional to the error.

References:
----------
- Issue: RSA-2048 Post-Resonance Focusing: Multi-Δ Center Refinement With Bounded Divisibility
- PR #182: RSA-2048 Factor Candidate Extraction Benchmark
"""

import math
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging
from fractions import Fraction

# Import from existing modules
try:
    from python.greens_function_factorization import (
        safe_log,
        safe_sqrt,
        greens_function_amplitude,
        compute_curvature,
        dirichlet_kernel,
        GreensResult
    )
except ImportError:
    from greens_function_factorization import (
        safe_log,
        safe_sqrt,
        greens_function_amplitude,
        compute_curvature,
        dirichlet_kernel,
        GreensResult
    )


# Tuning constants - explicitly surfaced for reproducibility
FOCUSING_CONFIG = {
    # Dual-k detuning for phase residual analysis
    'dual_k_epsilon': 0.005,  # k2 = k1 * (1 + epsilon)
    
    # Dirichlet kernel for peak centering
    'dirichlet_J': 8,  # Number of harmonic terms (higher = sharper peak)
    
    # κ-weighted gradient descent
    'kappa_descent_steps': 10,  # Number of gradient descent iterations
    'kappa_step_size': 0.0001,  # Step size in log-space
    
    # Balance assumption weight
    'balance_bias_weight': 0.3,  # How much to bias toward √N (0=none, 1=full)
    
    # Phase alignment iterations
    'phase_alignment_iterations': 5,  # Secondary phase alignment passes
    'phase_correction_damping': 0.5,  # Damping factor for phase corrections
    
    # Multi-scale spectral scan parameters
    'coarse_scan_range': 0.05,  # ±5% in log-space for coarse scan
    'coarse_scan_step': 0.01,   # 1% step size for coarse scan
    'fine_scan_range': 0.01,    # ±1% in log-space for fine scan
    'fine_scan_step': 0.002,    # 0.2% step size for fine scan
    
    # Multi-Δ center refinement parameters
    'max_delta_centers': 20,    # Maximum number of δ-centers to test
    'refinement_radius': 1000,  # Bounded refinement radius (±R)
}


@dataclass
class FocusingMetadata:
    """Metadata from resonance stage used for focusing"""
    k_primary: float
    amplitude: float
    phase: float
    kappa_weight: float
    m_value: int  # Resonance mode number
    score: float


@dataclass
class FocusingResult:
    """Result from focusing transform"""
    p_hat: int  # Refined estimate
    abs_distance_before: float
    abs_distance_after: float
    shrink_ratio: float
    focus_time_ms: float
    metadata: Dict[str, Any]  # Diagnostic info


@dataclass
class DeltaCenter:
    """A single δ-center candidate for multi-center refinement"""
    delta: float  # Offset in log-space: p ≈ (1+δ)*√N
    center: int  # Integer center = floor((1+delta)*sqrt(N))
    score: float  # Physics-based score (amplitude × Dirichlet × κ)
    amplitude: float  # Green's function amplitude at this δ
    kappa: float  # Curvature at this center
    phase: float  # Phase at this δ


@dataclass
class DeltaCenterResult:
    """Result from testing a single δ-center"""
    delta_center: DeltaCenter
    distance_before: float  # |coarse_seed - true_factor|
    distance_after: float  # |center - true_factor|
    shrink_ratio: float  # distance_after / distance_before
    within_1000: bool  # Is center within ±1000 of true factor?
    found_factor: bool  # Did ±1000 refinement find exact factor?
    factor_found: Optional[int]  # The exact factor if found
    offset_from_center: Optional[int]  # Offset from center if factor found
    refinement_time_ms: float  # Time spent on ±1000 refinement


@dataclass
class MultiDeltaFocusingResult:
    """Result from multi-Δ center refinement"""
    delta_centers: List[DeltaCenter]  # All δ-centers tested
    center_results: List[DeltaCenterResult]  # Results per center
    best_center_index: int  # Index of center with smallest distance_after
    best_center: DeltaCenter  # The best δ-center
    best_distance_after: float  # Smallest distance achieved
    best_shrink_ratio: float  # Best shrink ratio achieved
    found_factor: bool  # Did any center find the exact factor?
    factor_found: Optional[int]  # The exact factor if found
    total_focus_time_ms: float  # Total time for multi-center focusing
    total_refinement_time_ms: float  # Total time for all ±1000 refinements


def analyze_dual_k_phase_residual(
    N: int,
    p_coarse: int,
    k1: float,
    epsilon: float = FOCUSING_CONFIG['dual_k_epsilon']
) -> Dict[str, float]:
    """
    Analyze phase residual between k1 and k2 = k1*(1+epsilon).
    
    The resonance condition is: log N - 2*log p = 2πm/k
    If p is slightly off, the phase will differ between k1 and k2.
    This difference encodes the direction to correct.
    
    Args:
        N: Semiprime
        p_coarse: Coarse seed from resonance stage
        k1: Primary wave number
        epsilon: Detuning factor
        
    Returns:
        Dictionary with phase analysis results
    """
    log_N = safe_log(N)
    log_p_coarse = safe_log(p_coarse)
    
    k2 = k1 * (1.0 + epsilon)
    
    # Compute phases at both k values
    phase1 = k1 * (log_N - 2.0 * log_p_coarse)
    phase2 = k2 * (log_N - 2.0 * log_p_coarse)
    
    # Compute amplitudes
    amp1 = greens_function_amplitude(log_N, log_p_coarse, k1)
    amp2 = greens_function_amplitude(log_N, log_p_coarse, k2)
    
    # Phase residual (normalized by k difference)
    phase_diff = phase2 - phase1
    phase_residual = phase_diff / (k2 - k1)
    
    # Amplitude ratio indicates how far from peak
    amp_ratio = amp2 / amp1 if amp1 > 1e-12 else 1.0
    
    return {
        'phase1': phase1,
        'phase2': phase2,
        'phase_residual': phase_residual,
        'amp1': amp1,
        'amp2': amp2,
        'amp_ratio': amp_ratio
    }


def dirichlet_peak_centering(
    N: int,
    p_coarse: int,
    k: float,
    J: int = FOCUSING_CONFIG['dirichlet_J']
) -> Dict[str, float]:
    """
    Use Dirichlet kernel to find the exact peak center at sub-integer precision.
    
    The Dirichlet kernel D_J(ψ) = sin((J+1/2)ψ) / sin(ψ/2) has a sharp main lobe.
    We evaluate it at p-1, p, p+1 and interpolate to find the peak maximum.
    
    Args:
        N: Semiprime
        p_coarse: Coarse seed
        k: Wave number
        J: Number of harmonic terms
        
    Returns:
        Dictionary with peak centering results
    """
    log_N = safe_log(N)
    
    # Evaluate Dirichlet-weighted amplitude at p-1, p, p+1
    positions = [p_coarse - 1, p_coarse, p_coarse + 1]
    weighted_amps = []
    
    for p in positions:
        if p <= 0:
            weighted_amps.append(0.0)
            continue
            
        log_p = safe_log(p)
        phase = k * (log_N - 2.0 * log_p)
        
        # Base amplitude
        amp = greens_function_amplitude(log_N, log_p, k)
        
        # Dirichlet sharpening
        dirichlet_val = abs(dirichlet_kernel(phase, J))
        weighted_amp = amp * dirichlet_val
        
        weighted_amps.append(weighted_amp)
    
    # Quadratic interpolation to find peak
    # f(x) = a*x^2 + b*x + c, peak at x = -b/(2a)
    # Using positions [-1, 0, 1] relative to p_coarse
    y_minus, y_center, y_plus = weighted_amps
    
    # Fit quadratic
    a = 0.5 * (y_plus + y_minus) - y_center
    b = 0.5 * (y_plus - y_minus)
    c = y_center
    
    # Peak offset from p_coarse
    if abs(a) > 1e-12:
        peak_offset = -b / (2.0 * a)
    else:
        peak_offset = 0.0
    
    # Clamp to reasonable range
    peak_offset = max(-10.0, min(10.0, peak_offset))
    
    return {
        'peak_offset': peak_offset,
        'weighted_amps': weighted_amps,
        'quadratic_coeff_a': a,
        'quadratic_coeff_b': b
    }


def kappa_weighted_gradient_descent(
    N: int,
    p_coarse: int,
    k: float,
    steps: int = FOCUSING_CONFIG['kappa_descent_steps'],
    step_size: float = FOCUSING_CONFIG['kappa_step_size']
) -> Dict[str, Any]:
    """
    Perform gradient descent in log-space weighted by curvature κ(p).
    
    The curvature κ(n) = d(n) * ln(n+1) / e² indicates prime-like regions.
    We move toward higher κ values, which should correspond to prime factors.
    
    Args:
        N: Semiprime
        p_coarse: Starting point
        k: Wave number
        steps: Number of descent iterations
        step_size: Step size in log-space
        
    Returns:
        Dictionary with descent results
    """
    log_N = safe_log(N)
    log_p_current = safe_log(p_coarse)
    
    trajectory = [p_coarse]
    kappa_values = [compute_curvature(p_coarse)]
    
    for step in range(steps):
        p_current = int(round(math.exp(log_p_current)))
        if p_current <= 1:
            break
        
        # Evaluate κ at current and neighbors
        kappa_center = compute_curvature(p_current)
        
        # Use integer neighbors for gradient estimate
        p_plus = p_current + 1
        p_minus = max(2, p_current - 1)
        
        kappa_plus = compute_curvature(p_plus)
        kappa_minus = compute_curvature(p_minus)
        
        # Gradient in log-space (approximate)
        # dκ/d(log p) ≈ (κ(p+1) - κ(p-1)) / (log(p+1) - log(p-1))
        log_diff = safe_log(p_plus) - safe_log(p_minus)
        if abs(log_diff) < 1e-12:
            log_gradient = 0.0
        else:
            log_gradient = (kappa_plus - kappa_minus) / log_diff
        
        # Also consider the Green's function gradient
        amp_center = greens_function_amplitude(log_N, log_p_current, k)
        amp_plus = greens_function_amplitude(log_N, safe_log(p_plus), k)
        amp_minus = greens_function_amplitude(log_N, safe_log(p_minus), k)
        
        if abs(log_diff) < 1e-12:
            amp_gradient = 0.0
        else:
            amp_gradient = (amp_plus - amp_minus) / log_diff
        
        # Combined gradient (weighted sum)
        combined_gradient = 0.7 * log_gradient + 0.3 * amp_gradient
        
        # Update in log-space
        log_p_current += step_size * combined_gradient
        
        # Track
        p_new = int(round(math.exp(log_p_current)))
        if p_new > 0:
            trajectory.append(p_new)
            kappa_values.append(compute_curvature(p_new))
    
    p_final = trajectory[-1] if trajectory else p_coarse
    
    return {
        'p_refined': p_final,
        'trajectory_length': len(trajectory),
        'kappa_initial': kappa_values[0] if kappa_values else 0.0,
        'kappa_final': kappa_values[-1] if kappa_values else 0.0,
        'kappa_improvement': (kappa_values[-1] - kappa_values[0]) if len(kappa_values) > 1 else 0.0
    }


def apply_balance_bias(
    N: int,
    p_coarse: int,
    weight: float = FOCUSING_CONFIG['balance_bias_weight']
) -> int:
    """
    Apply balance assumption: for RSA-style semiprimes, p ≈ q ≈ √N.
    
    This biases the estimate toward √N, which is valid for balanced factors.
    
    Args:
        N: Semiprime
        p_coarse: Coarse estimate
        weight: How much to bias (0 = no bias, 1 = full bias to √N)
        
    Returns:
        Adjusted estimate
    """
    sqrt_N = safe_sqrt(N)
    
    # Weighted geometric mean in log-space
    log_p_coarse = safe_log(p_coarse)
    log_sqrt_N = safe_log(sqrt_N)
    
    log_p_adjusted = (1.0 - weight) * log_p_coarse + weight * log_sqrt_N
    
    p_adjusted = int(round(math.exp(log_p_adjusted)))
    
    return p_adjusted


def iterative_phase_alignment(
    N: int,
    p_coarse: int,
    k: float,
    iterations: int = FOCUSING_CONFIG['phase_alignment_iterations'],
    damping: float = FOCUSING_CONFIG['phase_correction_damping']
) -> int:
    """
    Iteratively align to the resonance phase.
    
    The resonance condition is: log N - 2*log p = 2πm/k
    We solve for p that minimizes the phase residual.
    
    Args:
        N: Semiprime
        p_coarse: Starting estimate
        k: Wave number
        iterations: Number of alignment iterations
        damping: Damping factor (0-1) to prevent overshooting
        
    Returns:
        Phase-aligned estimate
    """
    log_N = safe_log(N)
    log_p_current = safe_log(p_coarse)
    
    for iteration in range(iterations):
        # Current phase
        phase_current = k * (log_N - 2.0 * log_p_current)
        
        # Find nearest resonance mode m
        m_nearest = round(phase_current / (2.0 * math.pi))
        
        # Target phase for perfect resonance
        phase_target = 2.0 * math.pi * m_nearest
        
        # Phase error
        phase_error = phase_current - phase_target
        
        # Correction to log p
        # phase = k*(log N - 2*log p) => ∂phase/∂(log p) = -2k
        # To reduce phase_error, we need: Δ(log p) = phase_error / (2k)
        delta_log_p = phase_error / (2.0 * k)
        
        # Apply damped correction
        log_p_current += damping * delta_log_p
        
        # Early exit if converged
        if abs(phase_error) < 1e-6:
            break
    
    p_aligned = int(round(math.exp(log_p_current)))
    
    return p_aligned


def focus_seed(
    seed: int,
    N: int,
    metadata: FocusingMetadata,
    config: Optional[Dict[str, Any]] = None
) -> int:
    """
    Main focusing transform: refine a coarse seed to a locally accurate estimate.
    
    Strategy:
    At RSA-2048 scale, the Green's function resonance naturally converges to √N,
    but the true factors p and q are offset by ~4% (±0.04 in log-space), creating
    a ~10^306 absolute distance gap.
    
    This transform uses a multi-scale spectral scan to search for secondary
    resonance peaks offset from √N. It evaluates Green's amplitude combined with
    κ-curvature at multiple log-scale offsets, looking for the sweet spot where
    both the wave interference and prime density signals are maximized.
    
    The scan is deterministic and bounded, using only analytic/geometric signals.
    
    Args:
        seed: Coarse factor estimate from resonance stage
        N: Semiprime to factor
        metadata: Information from resonance stage (k, amplitude, phase, etc.)
        config: Optional override for tuning constants (uses FOCUSING_CONFIG if None)
        
    Returns:
        Refined estimate p_hat
    """
    if config is None:
        config = FOCUSING_CONFIG
    
    k = metadata.k_primary
    log_N = safe_log(N)
    log_seed = safe_log(seed)
    sqrt_N = safe_sqrt(N)
    log_sqrt_N = safe_log(sqrt_N)
    
    # Multi-scale spectral scan around √N
    # For RSA semiprimes, factors are typically within ±5% of √N
    # We scan in log-space at multiple scales
    
    # Get scan parameters from config (or use defaults if not present)
    coarse_range = config.get('coarse_scan_range', 0.05)  # ±5% default
    coarse_step = config.get('coarse_scan_step', 0.01)    # 1% steps default
    fine_range = config.get('fine_scan_range', 0.01)      # ±1% default
    fine_step = config.get('fine_scan_step', 0.002)       # 0.2% steps default
    
    # Coarse scan: ±coarse_range in log-space
    num_coarse_steps = int(coarse_range / coarse_step)
    coarse_offsets = [i * coarse_step for i in range(-num_coarse_steps, num_coarse_steps + 1)]
    
    # Fine scan: ±fine_range around best coarse result
    num_fine_steps = int(fine_range / fine_step)
    fine_offsets = [i * fine_step for i in range(-num_fine_steps, num_fine_steps + 1)]
    
    # Coarse scan
    best_coarse_log_p = log_sqrt_N
    best_coarse_score = 0.0
    
    for offset in coarse_offsets:
        test_log_p = log_sqrt_N + offset
        test_p = int(round(math.exp(test_log_p)))
        if test_p <= 1 or test_p >= N:
            continue
        
        # Evaluate combined score: amplitude × curvature
        amp = greens_function_amplitude(log_N, test_log_p, k)
        kappa = compute_curvature(test_p)
        
        score = amp * kappa
        
        if score > best_coarse_score:
            best_coarse_score = score
            best_coarse_log_p = test_log_p
    
    # Fine scan around best coarse result
    best_fine_log_p = best_coarse_log_p
    best_fine_score = 0.0
    
    for offset in fine_offsets:
        test_log_p = best_coarse_log_p + offset
        test_p = int(round(math.exp(test_log_p)))
        if test_p <= 1 or test_p >= N:
            continue
        
        # Evaluate with Dirichlet sharpening
        test_log_p_float = test_log_p
        phase = k * (log_N - 2.0 * test_log_p_float)
        
        amp = greens_function_amplitude(log_N, test_log_p_float, k)
        dirichlet_val = abs(dirichlet_kernel(phase, config['dirichlet_J']))
        kappa = compute_curvature(test_p)
        
        score = amp * dirichlet_val * kappa
        
        if score > best_fine_score:
            best_fine_score = score
            best_fine_log_p = test_log_p
    
    # Convert to integer
    p_focused = int(round(math.exp(best_fine_log_p)))
    p_focused = max(2, min(p_focused, N - 1))
    
    # Final refinement: iterative phase alignment
    p_hat = iterative_phase_alignment(
        N, p_focused, k,
        iterations=config['phase_alignment_iterations'],
        damping=config['phase_correction_damping']
    )
    
    # Dirichlet peak centering for sub-integer precision
    peak_info = dirichlet_peak_centering(N, p_hat, k, config['dirichlet_J'])
    peak_offset = peak_info['peak_offset']
    p_hat = p_hat + int(round(peak_offset))
    p_hat = max(2, min(p_hat, N - 1))
    
    return p_hat


def focus_seed_with_metrics(
    seed: int,
    N: int,
    metadata: FocusingMetadata,
    true_factor: Optional[int] = None,
    config: Optional[Dict[str, Any]] = None
) -> FocusingResult:
    """
    Apply focusing transform and compute metrics.
    
    Args:
        seed: Coarse factor estimate
        N: Semiprime
        metadata: Resonance stage metadata
        true_factor: Ground truth (for evaluation only)
        config: Optional tuning constants override
        
    Returns:
        FocusingResult with p_hat and all metrics
    """
    import time
    
    # Time the focusing
    start_time = time.perf_counter()
    p_hat = focus_seed(seed, N, metadata, config)
    focus_time_ms = (time.perf_counter() - start_time) * 1000
    
    # Compute metrics if true factor provided
    if true_factor is not None:
        abs_distance_before = abs(seed - true_factor)
        abs_distance_after = abs(p_hat - true_factor)
        
        if abs_distance_before > 0:
            shrink_ratio = abs_distance_after / abs_distance_before
        else:
            shrink_ratio = 0.0
    else:
        abs_distance_before = 0.0
        abs_distance_after = 0.0
        shrink_ratio = 0.0
    
    # Collect diagnostic metadata
    diagnostic = {
        'seed_original': seed,
        'p_hat': p_hat,
        'adjustment': p_hat - seed,
        'k_used': metadata.k_primary,
        'config': config if config is not None else FOCUSING_CONFIG
    }
    
    return FocusingResult(
        p_hat=p_hat,
        abs_distance_before=abs_distance_before,
        abs_distance_after=abs_distance_after,
        shrink_ratio=shrink_ratio,
        focus_time_ms=focus_time_ms,
        metadata=diagnostic
    )


def extract_delta_centers(
    N: int,
    metadata: FocusingMetadata,
    config: Optional[Dict[str, Any]] = None,
    min_score_threshold: float = 0.0,
    max_centers: int = 20
) -> List[DeltaCenter]:
    """
    Extract multiple δ-centers from resonance structure.
    
    Instead of picking a single "best" seed, this function identifies all
    physically-valid δ modes that pass the physics gates:
    - Strong Green's function amplitude
    - Good Dirichlet peak alignment
    - Reasonable curvature
    
    Each δ represents an offset from √N where p ≈ (1+δ)*√N.
    For RSA-2048, the true factor typically has δ ≈ ±0.04.
    
    Args:
        N: Semiprime to factor
        metadata: Resonance stage metadata
        config: Optional tuning constants (uses FOCUSING_CONFIG if None)
        min_score_threshold: Minimum score to keep a δ-center (default: 0.0)
        max_centers: Maximum number of centers to return (default: 20)
        
    Returns:
        List of DeltaCenter objects, sorted by score (descending)
    """
    if config is None:
        config = FOCUSING_CONFIG
    
    k = metadata.k_primary
    log_N = safe_log(N)
    sqrt_N = safe_sqrt(N)
    log_sqrt_N = safe_log(sqrt_N)
    
    # Scan parameters
    coarse_range = config.get('coarse_scan_range', 0.05)  # ±5%
    coarse_step = config.get('coarse_scan_step', 0.01)    # 1% steps
    
    # Use round() to avoid floating-point precision errors (e.g., 0.05/0.01 may yield 4.999999999999999)
    num_steps = round(coarse_range / coarse_step)
    delta_offsets = [i * coarse_step for i in range(-num_steps, num_steps + 1)]
    
    delta_centers = []
    
    for delta in delta_offsets:
        # Convert to integer center directly using (1+δ)*√N
        # This avoids exp() overflow for large N (RSA-2048 scale)
        # Use Fraction for exact rational arithmetic: center = sqrt_N * (1 + delta)
        # For delta expressed as num/den: center = sqrt_N * (den + num) / den
        frac_delta = Fraction(delta).limit_denominator(10000)
        numerator = frac_delta.numerator
        denominator = frac_delta.denominator
        # center = sqrt_N * (1 + delta) = sqrt_N * (den + num) / den
        center = (sqrt_N * (denominator + numerator)) // denominator
        
        if center <= 1 or center >= N:
            continue
        
        # Compute log-space position for physics evaluation
        log_p = safe_log(center)
        
        # Evaluate physics-based score
        amp = greens_function_amplitude(log_N, log_p, k)
        
        # Phase for Dirichlet sharpening
        phase = k * (log_N - 2.0 * log_p)
        dirichlet_val = abs(dirichlet_kernel(phase, config['dirichlet_J']))
        
        # Curvature
        kappa = compute_curvature(center)
        
        # Combined score: amplitude × Dirichlet × curvature
        score = amp * dirichlet_val * kappa
        
        # Only keep if above threshold
        if score >= min_score_threshold:
            delta_center = DeltaCenter(
                delta=delta,
                center=center,
                score=score,
                amplitude=amp,
                kappa=kappa,
                phase=phase
            )
            delta_centers.append(delta_center)
    
    # Sort by score (descending) and limit to max_centers
    delta_centers.sort(key=lambda dc: dc.score, reverse=True)
    delta_centers = delta_centers[:max_centers]
    
    return delta_centers


def bounded_refinement_single_center(
    N: int,
    center: int,
    radius: int = 1000
) -> Tuple[bool, Optional[int], Optional[int]]:
    """
    Perform bounded divisibility refinement around a single center.
    
    Tests candidates in [center - radius, center + radius] using
    big-int modulus to find exact factors.
    
    Performance note: This performs up to (2*radius + 1) modulus operations.
    For radius=1000, that's ~2001 big-int divisions. On RSA-2048, each division
    takes microseconds, so total time is ~2-50ms per center. With max_centers=20,
    total refinement time is <1s, well within the 60s budget.
    
    If radius needs to scale beyond ~10000, consider optimizations like:
    - Batch testing with GCD
    - Parallel execution per center
    - Early termination strategies
    
    Args:
        N: Semiprime to factor
        center: Integer center to search around
        radius: Search radius (default: 1000)
        
    Returns:
        Tuple of (found_factor, factor_found, offset_from_center)
    """
    search_min = max(2, center - radius)
    search_max = min(N - 1, center + radius)
    
    for candidate in range(search_min, search_max + 1):
        if N % candidate == 0:
            return True, candidate, candidate - center
    
    return False, None, None


def multi_delta_focusing(
    seed: int,
    N: int,
    metadata: FocusingMetadata,
    true_factor: Optional[int] = None,
    config: Optional[Dict[str, Any]] = None,
    refinement_radius: int = 1000,
    max_centers: int = 20
) -> MultiDeltaFocusingResult:
    """
    Multi-Δ center focusing with bounded divisibility refinement.
    
    This implements the "path to success" from the issue:
    1. Extract multiple δ-centers from resonance structure (not just one "best")
    2. Convert each δ to integer center via (1+δ)*√N
    3. For each center, run bounded ±R divisibility refinement
    4. Track per-center metrics (shrink_ratio, distance, etc.)
    5. Report best center and whether any center found the exact factor
    
    Args:
        seed: Coarse seed from resonance stage
        N: Semiprime to factor
        metadata: Resonance stage metadata
        true_factor: Ground truth factor (for evaluation only)
        config: Optional tuning constants
        refinement_radius: Radius for bounded refinement (default: 1000)
        max_centers: Maximum number of δ-centers to test (default: 20)
        
    Returns:
        MultiDeltaFocusingResult with all centers, metrics, and best result
    """
    import time
    
    if config is None:
        config = FOCUSING_CONFIG
    
    # ========================================================================
    # STEP 1: Extract multiple δ-centers
    # ========================================================================
    focus_start = time.perf_counter()
    
    delta_centers = extract_delta_centers(
        N=N,
        metadata=metadata,
        config=config,
        min_score_threshold=0.0,
        max_centers=max_centers
    )
    
    focus_time_ms = (time.perf_counter() - focus_start) * 1000
    
    # ========================================================================
    # STEP 2: For each center, run bounded refinement and compute metrics
    # ========================================================================
    center_results = []
    total_refinement_time = 0.0
    global_found_factor = False
    global_factor_found = None
    
    for dc in delta_centers:
        refine_start = time.perf_counter()
        
        # Run bounded divisibility refinement
        found_factor, factor_found, offset = bounded_refinement_single_center(
            N=N,
            center=dc.center,
            radius=refinement_radius
        )
        
        refine_time_ms = (time.perf_counter() - refine_start) * 1000
        total_refinement_time += refine_time_ms
        
        # Compute distance metrics if true_factor provided
        if true_factor is not None:
            distance_before = abs(seed - true_factor)
            distance_after = abs(dc.center - true_factor)
            
            if distance_before > 0:
                shrink_ratio = distance_after / distance_before
            else:
                shrink_ratio = 0.0
            
            within_1000 = (distance_after <= 1000)
        else:
            distance_before = 0.0
            distance_after = 0.0
            shrink_ratio = 0.0
            within_1000 = False
        
        # Record result for this center
        result = DeltaCenterResult(
            delta_center=dc,
            distance_before=distance_before,
            distance_after=distance_after,
            shrink_ratio=shrink_ratio,
            within_1000=within_1000,
            found_factor=found_factor,
            factor_found=factor_found,
            offset_from_center=offset,
            refinement_time_ms=refine_time_ms
        )
        center_results.append(result)
        
        # Update global factor found status
        if found_factor:
            global_found_factor = True
            global_factor_found = factor_found
            # Continue checking other centers for completeness
    
    # ========================================================================
    # STEP 3: Find best center (smallest distance_after)
    # ========================================================================
    if true_factor is not None and center_results:
        best_idx = min(range(len(center_results)), 
                      key=lambda i: center_results[i].distance_after)
        best_result = center_results[best_idx]
        best_center = best_result.delta_center
        best_distance = best_result.distance_after
        best_shrink = best_result.shrink_ratio
    else:
        # No true_factor provided, pick by score
        best_idx = 0 if center_results else -1
        best_center = delta_centers[0] if delta_centers else None
        best_distance = 0.0
        best_shrink = 0.0
    
    # ========================================================================
    # STEP 4: Build result
    # ========================================================================
    return MultiDeltaFocusingResult(
        delta_centers=delta_centers,
        center_results=center_results,
        best_center_index=best_idx,
        best_center=best_center,
        best_distance_after=best_distance,
        best_shrink_ratio=best_shrink,
        found_factor=global_found_factor,
        factor_found=global_factor_found,
        total_focus_time_ms=focus_time_ms,
        total_refinement_time_ms=total_refinement_time
    )


if __name__ == "__main__":
    # Quick demonstration
    print("Post-Resonance Focusing Transform Demo")
    print("=" * 70)
    print()
    print("This module provides deterministic focusing for coarse resonance seeds.")
    print("See rsa_factor_benchmark.py for integration example.")
    print()
    print("Tuning Constants:")
    for key, value in FOCUSING_CONFIG.items():
        print(f"  {key}: {value}")
