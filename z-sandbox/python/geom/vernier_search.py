#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vernier_search.py — Two-k vernier triangulation for cross-validation

Uses multiple k values to identify m candidates where BOTH produce
integer-resonant q̂ values, suppressing false positives via CRT-like intersection.

Usage:
    from python.geom.vernier_search import vernier_triangulation, score_intersection
"""

import mpmath as mp
from typing import List, Tuple
from .resonance_search import integer_resonance_objective


def score_intersection(m: mp.mpf, k1: float, k2: float, N: int, logN: mp.mpf) -> mp.mpf:
    """
    Score m by combining integer-resonance across two k values.
    
    Computes resonance for both k₁ and k₂; returns combined score.
    High score indicates m is consistent across both k values.
    
    Args:
        m: Fractional comb index
        k1: First wave number
        k2: Second wave number
        N: Target semiprime
        logN: log(N)
    
    Returns:
        combined_score: Sum of resonance scores (higher = better)
    """
    score1 = integer_resonance_objective(m, k1, N, logN)
    score2 = integer_resonance_objective(m, k2, N, logN)
    
    # Combined score (sum; could also use min or geometric mean)
    combined = score1 + score2
    return combined


def vernier_triangulation(N: int, k1: float, k2: float, 
                          m0: mp.mpf, window: mp.mpf,
                          coarse_step: float = 0.001,
                          threshold: float = 5.0,
                          top_k: int = 100,
                          dps: int = 1000) -> List[Tuple[mp.mpf, mp.mpf]]:
    """
    Two-k vernier triangulation: find m where both k₁ and k₂ show integer-resonance.
    
    Performs coarse sweep over [m0 - window, m0 + window] and identifies
    intersections where BOTH k values produce high resonance scores.
    
    Args:
        N: Target semiprime
        k1: First wave number (e.g., 0.29)
        k2: Second wave number (e.g., 0.31)
        m0: Central comb index
        window: Half-window for search
        coarse_step: Step size for coarse sweep (fixed for simplicity)
        threshold: Minimum combined score to consider (default 5.0)
        top_k: Return top K candidates by score
        dps: Decimal precision
    
    Returns:
        candidates: List of (m, combined_score), sorted by score (descending)
    
    Example:
        >>> candidates = vernier_triangulation(N, 0.29, 0.31, m0, win)
        >>> for m, score in candidates[:10]:
        ...     # Apply line search refinement, then check GCD
    """
    with mp.workdps(dps):
        N_mp = mp.mpf(N)
        logN = mp.log(N_mp)
        
        candidates = []
        
        # Coarse sweep over m
        m_start = m0 - window
        m_end = m0 + window
        m_current = m_start
        
        while m_current <= m_end:
            # Compute individual resonance scores
            score1 = integer_resonance_objective(m_current, k1, N, logN)
            score2 = integer_resonance_objective(m_current, k2, N, logN)
            
            # Combined score
            combined = score1 + score2
            
            # Only keep if both k values show decent resonance
            if score1 > threshold / 2 and score2 > threshold / 2:
                candidates.append((m_current, combined))
            
            m_current = m_current + mp.mpf(coarse_step)
        
        # Sort by combined score (descending)
        candidates.sort(key=lambda x: float(x[1]), reverse=True)
        
        # Return top K
        return candidates[:top_k]


def multi_k_consensus(N: int, k_values: List[float], m0: mp.mpf, window: mp.mpf,
                      coarse_step: float = 0.001, top_k: int = 50,
                      dps: int = 1000) -> List[Tuple[mp.mpf, mp.mpf]]:
    """
    Multi-k consensus search: generalization of vernier to 3+ k values.
    
    Identifies m where MOST k values agree on integer-resonance.
    
    Args:
        N: Target semiprime
        k_values: List of k values (e.g., [0.28, 0.29, 0.30, 0.31, 0.32])
        m0: Central index
        window: Half-window
        coarse_step: Step size
        top_k: Return top K
        dps: Precision
    
    Returns:
        candidates: List of (m, consensus_score)
    
    Note:
        Consensus score = sum of resonance scores across all k values.
    """
    with mp.workdps(dps):
        N_mp = mp.mpf(N)
        logN = mp.log(N_mp)
        
        candidates = []
        
        m_start = m0 - window
        m_end = m0 + window
        m_current = m_start
        
        while m_current <= m_end:
            # Score across all k values
            total_score = mp.mpf(0)
            for k in k_values:
                score = integer_resonance_objective(m_current, k, N, logN)
                total_score += score
            
            candidates.append((m_current, total_score))
            m_current = m_current + mp.mpf(coarse_step)
        
        # Sort by consensus score
        candidates.sort(key=lambda x: float(x[1]), reverse=True)
        
        return candidates[:top_k]


def log_vernier_results(candidates: List[Tuple[mp.mpf, mp.mpf]], 
                        k1: float, k2: float, N: int) -> None:
    """
    Log vernier triangulation results for reproducibility.
    
    Args:
        candidates: List of (m, score) from vernier
        k1: First k value
        k2: Second k value
        N: Target semiprime
    """
    print("=== Vernier Triangulation Results ===")
    print(f"N: {N} ({int(mp.log(mp.mpf(N))/mp.log(2))} bits)")
    print(f"k₁: {k1}, k₂: {k2}")
    print(f"Candidates found: {len(candidates)}\n")
    
    print("Top 10 candidates:")
    for i, (m, score) in enumerate(candidates[:10]):
        print(f"  {i+1:2d}. m = {mp.nstr(m, 12):>15s}, score = {mp.nstr(score, 10)}")


if __name__ == "__main__":
    # Smoke test
    mp.mp.dps = 200
    
    # Test on RSA-100
    RSA_100 = int("1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139")
    
    print("=== Vernier Search Smoke Test ===\n")
    
    # Parameters
    k1 = 0.29
    k2 = 0.31
    m0 = mp.mpf(0.0)
    window = mp.mpf(0.05)
    
    # Run vernier
    candidates = vernier_triangulation(RSA_100, k1, k2, m0, window, 
                                       coarse_step=0.002, threshold=3.0, 
                                       top_k=20, dps=200)
    
    log_vernier_results(candidates, k1, k2, RSA_100)
    
    # Test multi-k consensus
    print("\n=== Multi-k Consensus Test ===\n")
    k_values = [0.28, 0.29, 0.30, 0.31, 0.32]
    
    candidates_multi = multi_k_consensus(RSA_100, k_values, m0, window,
                                         coarse_step=0.002, top_k=10, dps=200)
    
    print(f"k values: {k_values}")
    print(f"Top 10 by consensus:\n")
    for i, (m, score) in enumerate(candidates_multi):
        print(f"  {i+1:2d}. m = {mp.nstr(m, 12):>15s}, score = {mp.nstr(score, 10)}")
