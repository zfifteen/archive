#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
adaptive_step.py — Sensitivity-aware adaptive Δm for fractional comb search

Computes step size Δm such that each step changes p̂(m) by approximately ±1 integer,
preventing exponential overshooting in high-sensitivity regimes.

Usage:
    from python.geom.adaptive_step import compute_delta_m, generate_symmetric_queue
"""

import mpmath as mp
from typing import List, Callable


def compute_delta_m(m: mp.mpf, k: float, p_hat: mp.mpf, 
                    delta_m_min: float = 1e-200, delta_m_max: float = 1.0) -> mp.mpf:
    """
    Compute adaptive step size Δm for local m such that p̂ changes by ~1 integer.
    
    From sensitivity analysis:
        |∂p̂/∂m| = (π/k) · p̂
    
    For Δp̂ ≈ 1 integer:
        Δm ≈ k / (π · p̂)
    
    Clamps Δm within [delta_m_min, delta_m_max] for numerical stability.
    
    Args:
        m: Current fractional comb index
        k: Comb wave number
        p_hat: Candidate p̂(m) value
        delta_m_min: Minimum allowed step (prevents stalling)
        delta_m_max: Maximum allowed step (prevents jumps)
    
    Returns:
        Δm: Adaptive step size
    
    Note:
        Call this at each m to get local step; cumulative error stays bounded.
    """
    k_mp = mp.mpf(k)
    
    # Theoretical Δm for Δp̂ = 1
    delta_m_theory = k_mp / (mp.pi * p_hat)
    
    # Dynamic floor: fraction of theoretical sensitivity (adjust factor if needed)
    delta_m_floor = mp.mpf('0.1') * delta_m_theory
    
    # Ensure provided min/max are mp.mpf
    delta_m_min_mp = mp.mpf(delta_m_min)
    delta_m_max_mp = mp.mpf(delta_m_max)
    
    # Raise the floor to not exceed provided static min
    delta_m_min_mp = max(delta_m_min_mp, delta_m_floor)
    
    # Clamp entirely in mpmath (no float conversions)
    delta_m_clamped = max(delta_m_min_mp, min(delta_m_max_mp, delta_m_theory))
    
    return delta_m_clamped


def generate_symmetric_queue(m0: mp.mpf, window: mp.mpf, k: float, logN: mp.mpf, 
                              p_from_m_fn: Callable[[mp.mpf, float, mp.mpf], mp.mpf],
                              delta_m_min: float = 1e-200, delta_m_max: float = 1.0,
                              max_candidates: int = 100000) -> List[mp.mpf]:
    """
    Generate symmetric search queue around m₀ with adaptive stepping.
    
    Order: m₀, m₀+Δ₁, m₀-Δ₁, m₀+Δ₁+Δ₂, m₀-Δ₁-Δ₂, ...
    
    Each step Δᵢ is computed adaptively based on local sensitivity,
    ensuring deterministic, reproducible ordering while preventing overshooting.
    
    Args:
        m0: Central comb index (from Z5D prior)
        window: Half-window for search (±window)
        k: Comb wave number
        logN: log(N) for p̂(m) computation
        p_from_m_fn: Function p̂(m, k, logN) -> p̂
        delta_m_min: Minimum step size
        delta_m_max: Maximum step size
        max_candidates: Budget limit (stops early if exceeded)
    
    Returns:
        queue: List of m values in symmetric order
    
    Example:
        >>> from python.geom.adaptive_step import generate_symmetric_queue
        >>> queue = generate_symmetric_queue(m0, win, k, logN, p_from_m)
        >>> for m in queue[:10]:  # Evaluate top 10
        ...     p_hat = p_from_m(m, k, logN)
        ...     check_candidate(p_hat)
    """
    queue = [m0]
    m_pos = m0
    m_neg = m0
    
    candidate_count = 1
    
    while candidate_count < max_candidates:
        # Positive side
        if m_pos < m0 + window:
            p_hat_pos = p_from_m_fn(m_pos, k, logN)
            delta_pos = compute_delta_m(m_pos, k, p_hat_pos, delta_m_min, delta_m_max)
            m_pos = m_pos + delta_pos
            
            if m_pos <= m0 + window:
                queue.append(m_pos)
                candidate_count += 1
        
        # Negative side
        if m_neg > m0 - window:
            p_hat_neg = p_from_m_fn(m_neg, k, logN)
            delta_neg = compute_delta_m(m_neg, k, p_hat_neg, delta_m_min, delta_m_max)
            m_neg = m_neg - delta_neg
            
            if m_neg >= m0 - window:
                queue.append(m_neg)
                candidate_count += 1
        
        # Exit if both sides exhausted
        if m_pos >= m0 + window and m_neg <= m0 - window:
            break
    
    return queue


def validate_adaptive_stepping(queue: List[mp.mpf], k: float, logN: mp.mpf,
                                p_from_m_fn: Callable[[mp.mpf, float, mp.mpf], mp.mpf],
                                tolerance: float = 5.0) -> bool:
    """
    Validate that adaptive stepping achieves Δp̂ ≈ 1 across the queue.
    
    Checks that consecutive p̂ values differ by approximately 1 integer
    (within tolerance factor).
    
    Args:
        queue: Generated m queue
        k: Comb parameter
        logN: log(N)
        p_from_m_fn: Function p̂(m, k, logN) -> p̂
        tolerance: Allowed deviation (e.g., 5.0 means Δp ∈ [1/5, 5])
    
    Returns:
        valid: True if ≥95% of steps satisfy |Δp̂| ∈ [1/tolerance, tolerance]
    """
    if len(queue) < 2:
        return True
    
    valid_steps = 0
    total_steps = 0
    
    for i in range(len(queue) - 1):
        p_i = p_from_m_fn(queue[i], k, logN)
        p_next = p_from_m_fn(queue[i+1], k, logN)
        delta_p = mp.fabs(p_next - p_i)
        
        # Check if Δp̂ is roughly 1 (within tolerance)
        if delta_p >= 1.0 / tolerance and delta_p <= tolerance:
            valid_steps += 1
        total_steps += 1
    
    success_rate = valid_steps / total_steps if total_steps > 0 else 0.0
    return success_rate >= 0.95


if __name__ == "__main__":
    # Smoke test
    mp.mp.dps = 100
    
    # Define p_from_m for testing
    def p_from_m(m: mp.mpf, k: float, logN: mp.mpf) -> mp.mpf:
        return mp.exp((logN - (2 * mp.pi * m) / mp.mpf(k)) / 2)
    
    # Test parameters (RSA-100 scale)
    RSA_100 = int("1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139")
    logN = mp.log(mp.mpf(RSA_100))
    k = 0.30
    m0 = mp.mpf(0.0)
    window = mp.mpf(0.01)
    
    print("=== Adaptive Step Smoke Test ===")
    print(f"N (RSA-100), k={k}, m₀={m0}, window={window}\n")
    
    # Generate queue
    queue = generate_symmetric_queue(m0, window, k, logN, p_from_m, max_candidates=100)
    
    print(f"Generated {len(queue)} candidates")
    print(f"First 5: {[mp.nstr(m, 10) for m in queue[:5]]}")
    print(f"Last 5:  {[mp.nstr(m, 10) for m in queue[-5:]]}")
    
    # Validate stepping
    valid = validate_adaptive_stepping(queue, k, logN, p_from_m, tolerance=10.0)
    print(f"\nAdaptive stepping valid: {valid}")
    
    # Sample Δp̂ values
    print("\nSample Δp̂ values (should be ~1):")
    for i in range(min(5, len(queue) - 1)):
        p_i = p_from_m(queue[i], k, logN)
        p_next = p_from_m(queue[i+1], k, logN)
        delta_p = mp.fabs(p_next - p_i)
        print(f"  Step {i}: Δp̂ = {mp.nstr(delta_p, 8)}")
