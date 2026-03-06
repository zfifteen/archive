#!/usr/bin/env python3
"""
Instrumented Green's Function Factorization for Structural Wall Analysis

This module extends greens_function_factorization.py with detailed logging
and measurement of each transform stage to identify sources of systematic bias.

Used for Issue #198: STRUCTURAL_WALL_REDUCTION_PHASE
"""

import math
from mpmath import mp
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import logging

# Import base functionality
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from python.greens_function_factorization import (
        GreensResult,
        RefinementConfig,
        compute_curvature,
        safe_log,
        safe_sqrt,
        greens_function_amplitude,
        comb_formula,
        phase_bias_correction,
        dirichlet_kernel,
        estimate_k_optimal,
        EPSILON
    )
except ImportError:
    from greens_function_factorization import (
        GreensResult,
        RefinementConfig,
        compute_curvature,
        safe_log,
        safe_sqrt,
        greens_function_amplitude,
        comb_formula,
        phase_bias_correction,
        dirichlet_kernel,
        estimate_k_optimal,
        EPSILON
    )

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class StageMetrics:
    """Metrics for a single pipeline stage"""
    stage_name: str
    input_candidates: List[int]
    output_candidates: List[int]
    best_input_rel_error: float
    best_output_rel_error: float
    error_delta: float  # How much this stage changed the error
    distortion_contribution: float  # Absolute contribution to total error


@dataclass
class InstrumentedResult:
    """Extended result with per-stage instrumentation"""
    candidates: List[GreensResult]
    k_used: float
    found_factor: bool
    exact_factors: List[Tuple[int, int]]
    N: int
    stage_metrics: List[StageMetrics]
    p_true: Optional[int] = None
    q_true: Optional[int] = None


def compute_rel_error(candidate: int, p_true: int, q_true: int) -> float:
    """
    Compute relative error to closest true factor.
    
    Args:
        candidate: Candidate factor value
        p_true: True smaller factor
        q_true: True larger factor
        
    Returns:
        Relative error to closest factor
    """
    dist_p = abs(candidate - p_true)
    dist_q = abs(candidate - q_true)
    
    if dist_p < dist_q:
        return dist_p / p_true
    else:
        return dist_q / q_true


def find_best_candidate_error(candidates: List[int], p_true: int, q_true: int) -> float:
    """
    Find the best (minimum) relative error among candidates.
    
    Args:
        candidates: List of candidate values
        p_true: True smaller factor
        q_true: True larger factor
        
    Returns:
        Minimum relative error found
    """
    if not candidates:
        return float('inf')
    
    return min(compute_rel_error(c, p_true, q_true) for c in candidates)


def instrumented_geometric_embedding(
    N: int,
    k: float,
    window_size: int,
    p_true: Optional[int] = None,
    q_true: Optional[int] = None
) -> Tuple[List[int], StageMetrics]:
    """
    Stage 1: Geometric embedding - map N to log-space search window.
    
    This stage determines the search region around sqrt(N).
    
    Args:
        N: Semiprime to factor
        k: Wave number parameter
        window_size: Search window size
        p_true: True smaller factor (for error measurement)
        q_true: True larger factor (for error measurement)
        
    Returns:
        Tuple of (candidate positions, stage metrics)
    """
    log_N = safe_log(N)
    sqrt_N = safe_sqrt(N)
    
    # Generate candidate positions in window
    p_min = max(2, sqrt_N - window_size)
    p_max = sqrt_N + window_size
    
    candidates = list(range(p_min, p_max + 1))
    
    # Measure error if ground truth provided
    if p_true and q_true:
        input_error = float('inf')  # No input to this stage
        output_error = find_best_candidate_error(candidates, p_true, q_true)
        error_delta = output_error
        
        metrics = StageMetrics(
            stage_name="geometric_embedding",
            input_candidates=[],
            output_candidates=candidates[:10],  # Sample for logging
            best_input_rel_error=input_error,
            best_output_rel_error=output_error,
            error_delta=error_delta,
            distortion_contribution=output_error
        )
    else:
        metrics = StageMetrics(
            stage_name="geometric_embedding",
            input_candidates=[],
            output_candidates=candidates[:10],
            best_input_rel_error=float('inf'),
            best_output_rel_error=0.0,
            error_delta=0.0,
            distortion_contribution=0.0
        )
    
    return candidates, metrics


def instrumented_interference_computation(
    N: int,
    k: float,
    candidate_positions: List[int],
    config: RefinementConfig,
    p_true: Optional[int] = None,
    q_true: Optional[int] = None
) -> Tuple[List[GreensResult], StageMetrics]:
    """
    Stage 2: Interference computation - evaluate Green's function amplitude.
    
    This computes |G(log p)| = |cos(k(log N - 2log p))| for each candidate.
    
    Args:
        N: Semiprime
        k: Wave number
        candidate_positions: Positions to evaluate
        config: Refinement configuration
        p_true: True smaller factor (for error measurement)
        q_true: True larger factor (for error measurement)
        
    Returns:
        Tuple of (results with amplitudes, stage metrics)
    """
    log_N = safe_log(N)
    results = []
    
    for p in candidate_positions:
        if p <= 1:
            continue
            
        log_p = safe_log(p)
        
        # Basic Green's function amplitude
        amplitude = greens_function_amplitude(log_N, log_p, k)
        
        # Compute phase
        phase = k * (log_N - 2.0 * log_p)
        
        # Estimate resonance mode m
        m = int(round((log_N - 2.0 * log_p) * k / (2.0 * math.pi)))
        
        results.append(GreensResult(
            p_candidate=p,
            amplitude=amplitude,
            phase=phase,
            kappa_weight=1.0,  # Not computed yet
            score=amplitude,  # Just amplitude for now
            m_value=m
        ))
    
    # Sort by amplitude
    results.sort(key=lambda r: r.amplitude, reverse=True)
    
    # Measure error
    input_candidates = candidate_positions
    output_candidates = [r.p_candidate for r in results]
    
    if p_true and q_true:
        input_error = find_best_candidate_error(input_candidates, p_true, q_true)
        output_error = find_best_candidate_error(output_candidates, p_true, q_true)
        error_delta = output_error - input_error
        
        metrics = StageMetrics(
            stage_name="interference_computation",
            input_candidates=input_candidates[:10],
            output_candidates=output_candidates[:10],
            best_input_rel_error=input_error,
            best_output_rel_error=output_error,
            error_delta=error_delta,
            distortion_contribution=abs(error_delta)
        )
    else:
        metrics = StageMetrics(
            stage_name="interference_computation",
            input_candidates=input_candidates[:10],
            output_candidates=output_candidates[:10],
            best_input_rel_error=0.0,
            best_output_rel_error=0.0,
            error_delta=0.0,
            distortion_contribution=0.0
        )
    
    return results, metrics


def instrumented_phase_correction(
    results: List[GreensResult],
    N: int,
    k: float,
    p_true: Optional[int] = None,
    q_true: Optional[int] = None
) -> Tuple[List[GreensResult], StageMetrics]:
    """
    Stage 3: Phase bias correction.
    
    Applies phase-bias correction to refine candidates.
    
    Args:
        results: Initial results
        N: Semiprime
        k: Wave number
        p_true: True smaller factor (for error measurement)
        q_true: True larger factor (for error measurement)
        
    Returns:
        Tuple of (corrected results, stage metrics)
    """
    log_N = safe_log(N)
    corrected_results = []
    
    input_candidates = [r.p_candidate for r in results]
    
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
            log_p_corrected = (log_N - phase_corrected / k) / 2.0
            p_corrected = int(round(math.exp(log_p_corrected)))
            
            # Only add if it's different and valid
            if p_corrected != p and p_corrected > 1:
                # Re-evaluate at corrected position
                log_p_new = safe_log(p_corrected)
                amplitude_new = greens_function_amplitude(log_N, log_p_new, k)
                
                corrected_results.append(GreensResult(
                    p_candidate=p_corrected,
                    amplitude=amplitude_new,
                    phase=k * (log_N - 2.0 * log_p_new),
                    kappa_weight=1.0,
                    score=amplitude_new,
                    m_value=res.m_value
                ))
    
    # Merge original and corrected
    all_results = results + corrected_results
    all_results.sort(key=lambda r: r.amplitude, reverse=True)
    
    output_candidates = [r.p_candidate for r in all_results]
    
    # Measure error
    if p_true and q_true:
        input_error = find_best_candidate_error(input_candidates, p_true, q_true)
        output_error = find_best_candidate_error(output_candidates, p_true, q_true)
        error_delta = output_error - input_error
        
        metrics = StageMetrics(
            stage_name="phase_correction",
            input_candidates=input_candidates[:10],
            output_candidates=output_candidates[:10],
            best_input_rel_error=input_error,
            best_output_rel_error=output_error,
            error_delta=error_delta,
            distortion_contribution=abs(error_delta)
        )
    else:
        metrics = StageMetrics(
            stage_name="phase_correction",
            input_candidates=input_candidates[:10],
            output_candidates=output_candidates[:10],
            best_input_rel_error=0.0,
            best_output_rel_error=0.0,
            error_delta=0.0,
            distortion_contribution=0.0
        )
    
    return all_results, metrics


def instrumented_dirichlet_sharpening(
    results: List[GreensResult],
    config: RefinementConfig,
    p_true: Optional[int] = None,
    q_true: Optional[int] = None
) -> Tuple[List[GreensResult], StageMetrics]:
    """
    Stage 4: Dirichlet kernel sharpening.
    
    Applies Dirichlet kernel to sharpen resonance peaks.
    
    Args:
        results: Results to sharpen
        config: Refinement configuration
        p_true: True smaller factor (for error measurement)
        q_true: True larger factor (for error measurement)
        
    Returns:
        Tuple of (sharpened results, stage metrics)
    """
    input_candidates = [r.p_candidate for r in results]
    
    # Apply Dirichlet sharpening
    sharpened_results = []
    for res in results:
        dirichlet_factor = abs(dirichlet_kernel(res.phase, config.dirichlet_J))
        # Normalize to keep amplitudes comparable
        dirichlet_factor = dirichlet_factor / (2 * config.dirichlet_J + 1)
        
        sharpened_amplitude = res.amplitude * dirichlet_factor
        
        sharpened_results.append(GreensResult(
            p_candidate=res.p_candidate,
            amplitude=sharpened_amplitude,
            phase=res.phase,
            kappa_weight=res.kappa_weight,
            score=sharpened_amplitude,  # Will be updated with kappa later
            m_value=res.m_value
        ))
    
    # Sort by sharpened amplitude
    sharpened_results.sort(key=lambda r: r.amplitude, reverse=True)
    
    output_candidates = [r.p_candidate for r in sharpened_results]
    
    # Measure error
    if p_true and q_true:
        input_error = find_best_candidate_error(input_candidates, p_true, q_true)
        output_error = find_best_candidate_error(output_candidates, p_true, q_true)
        error_delta = output_error - input_error
        
        metrics = StageMetrics(
            stage_name="dirichlet_sharpening",
            input_candidates=input_candidates[:10],
            output_candidates=output_candidates[:10],
            best_input_rel_error=input_error,
            best_output_rel_error=output_error,
            error_delta=error_delta,
            distortion_contribution=abs(error_delta)
        )
    else:
        metrics = StageMetrics(
            stage_name="dirichlet_sharpening",
            input_candidates=input_candidates[:10],
            output_candidates=output_candidates[:10],
            best_input_rel_error=0.0,
            best_output_rel_error=0.0,
            error_delta=0.0,
            distortion_contribution=0.0
        )
    
    return sharpened_results, metrics


def instrumented_kappa_weighting(
    results: List[GreensResult],
    p_true: Optional[int] = None,
    q_true: Optional[int] = None
) -> Tuple[List[GreensResult], StageMetrics]:
    """
    Stage 5: κ-weighting.
    
    Applies Z5D curvature weighting to score candidates.
    
    Args:
        results: Results to weight
        p_true: True smaller factor (for error measurement)
        q_true: True larger factor (for error measurement)
        
    Returns:
        Tuple of (weighted results, stage metrics)
    """
    input_candidates = [r.p_candidate for r in results]
    
    # Apply kappa weighting
    weighted_results = []
    for res in results:
        kappa_weight = compute_curvature(res.p_candidate)
        final_score = res.amplitude * kappa_weight
        
        weighted_results.append(GreensResult(
            p_candidate=res.p_candidate,
            amplitude=res.amplitude,
            phase=res.phase,
            kappa_weight=kappa_weight,
            score=final_score,
            m_value=res.m_value
        ))
    
    # Sort by final score
    weighted_results.sort(key=lambda r: r.score, reverse=True)
    
    output_candidates = [r.p_candidate for r in weighted_results]
    
    # Measure error
    if p_true and q_true:
        input_error = find_best_candidate_error(input_candidates, p_true, q_true)
        output_error = find_best_candidate_error(output_candidates, p_true, q_true)
        error_delta = output_error - input_error
        
        metrics = StageMetrics(
            stage_name="kappa_weighting",
            input_candidates=input_candidates[:10],
            output_candidates=output_candidates[:10],
            best_input_rel_error=input_error,
            best_output_rel_error=output_error,
            error_delta=error_delta,
            distortion_contribution=abs(error_delta)
        )
    else:
        metrics = StageMetrics(
            stage_name="kappa_weighting",
            input_candidates=input_candidates[:10],
            output_candidates=output_candidates[:10],
            best_input_rel_error=0.0,
            best_output_rel_error=0.0,
            error_delta=0.0,
            distortion_contribution=0.0
        )
    
    return weighted_results, metrics


def factorize_greens_instrumented(
    N: int,
    k: Optional[float] = None,
    config: Optional[RefinementConfig] = None,
    max_candidates: int = 100,
    p_true: Optional[int] = None,
    q_true: Optional[int] = None,
    verbose: bool = False
) -> InstrumentedResult:
    """
    Main factorization function with per-stage instrumentation.
    
    This function instruments each stage of the resonance pipeline to
    measure error contribution and identify systematic biases.
    
    Args:
        N: Semiprime to factor
        k: Wave number (auto-estimated if None)
        config: Refinement configuration (uses defaults if None)
        max_candidates: Maximum candidates to return
        p_true: True smaller factor (for error measurement)
        q_true: True larger factor (for error measurement)
        verbose: Whether to print detailed stage metrics
        
    Returns:
        InstrumentedResult with candidates and stage metrics
    """
    if config is None:
        config = RefinementConfig()
    
    # Estimate k if not provided
    if k is None:
        k = estimate_k_optimal(N)
    
    stage_metrics = []
    
    # Stage 1: Geometric embedding
    candidate_positions, metrics1 = instrumented_geometric_embedding(
        N, k, window_size=500, p_true=p_true, q_true=q_true
    )
    stage_metrics.append(metrics1)
    
    # Stage 2: Interference computation
    results, metrics2 = instrumented_interference_computation(
        N, k, candidate_positions, config, p_true=p_true, q_true=q_true
    )
    stage_metrics.append(metrics2)
    
    # Stage 3: Phase correction (if enabled)
    if config.use_phase_correction:
        results, metrics3 = instrumented_phase_correction(
            results, N, k, p_true=p_true, q_true=q_true
        )
        stage_metrics.append(metrics3)
    
    # Stage 4: Dirichlet sharpening (if enabled)
    if config.use_dirichlet:
        results, metrics4 = instrumented_dirichlet_sharpening(
            results, config, p_true=p_true, q_true=q_true
        )
        stage_metrics.append(metrics4)
    
    # Stage 5: κ-weighting (if enabled)
    if config.use_kappa_weight:
        results, metrics5 = instrumented_kappa_weighting(
            results, p_true=p_true, q_true=q_true
        )
        stage_metrics.append(metrics5)
    
    # Print stage summary if verbose
    if verbose and p_true and q_true:
        logger.info("\n" + "=" * 80)
        logger.info("STAGE-BY-STAGE ANALYSIS")
        logger.info("=" * 80)
        for m in stage_metrics:
            logger.info(f"\nStage: {m.stage_name}")
            logger.info(f"  Input best rel_error:  {m.best_input_rel_error:.6e}")
            logger.info(f"  Output best rel_error: {m.best_output_rel_error:.6e}")
            logger.info(f"  Error delta:           {m.error_delta:+.6e}")
            logger.info(f"  Distortion contrib:    {m.distortion_contribution:.6e}")
        
        logger.info("\n" + "=" * 80)
        logger.info("DISTORTION SUMMARY")
        logger.info("=" * 80)
        total_distortion = sum(m.distortion_contribution for m in stage_metrics)
        for m in stage_metrics:
            pct = (m.distortion_contribution / total_distortion * 100) if total_distortion > 0 else 0
            logger.info(f"  {m.stage_name:25s}: {m.distortion_contribution:10.6e} ({pct:5.1f}%)")
    
    # Check for exact factors
    exact_factors = []
    found_factor = False
    
    for res in results[:max_candidates]:
        p = res.p_candidate
        if N % p == 0:
            q = N // p
            exact_factors.append((p, q))
            found_factor = True
            break
    
    return InstrumentedResult(
        candidates=results[:max_candidates],
        k_used=k,
        found_factor=found_factor,
        exact_factors=exact_factors,
        N=N,
        stage_metrics=stage_metrics,
        p_true=p_true,
        q_true=q_true
    )


if __name__ == "__main__":
    # Quick test on a small example
    print("Instrumented Green's Function Factorization")
    print("=" * 80)
    
    # Small test case
    N_test = 143
    p_test = 11
    q_test = 13
    
    print(f"\nTest case: N={N_test}, p={p_test}, q={q_test}")
    
    result = factorize_greens_instrumented(
        N_test,
        k=0.3,
        max_candidates=10,
        p_true=p_test,
        q_true=q_test,
        verbose=True
    )
    
    print(f"\nTop 5 candidates:")
    for i, cand in enumerate(result.candidates[:5]):
        marker = "✓" if cand.p_candidate in [p_test, q_test] else " "
        rel_err = compute_rel_error(cand.p_candidate, p_test, q_test)
        print(f"  {marker} {i+1}. p={cand.p_candidate}, score={cand.score:.6f}, rel_err={rel_err:.6e}")
