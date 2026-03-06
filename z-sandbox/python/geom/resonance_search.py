#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resonance_search.py — Integer-resonance objective with dependency-free line search

Maximizes integer proximity of q̂ = N/p̂(m) to refine m before GCD checks.
Uses pure-Python Brent/golden-section search with mpmath.

Usage:
    from python.geom.resonance_search import integer_resonance_objective, brent_maximize
"""

import mpmath as mp
from typing import Callable, Tuple


def integer_resonance_objective(m: mp.mpf, k: float, N: int, logN: mp.mpf) -> mp.mpf:
    """
    Compute integer-resonance score for m: higher score = q̂ closer to integer.
    
    Objective: g(m) = -log(dist(N/p̂(m), ℤ))
    
    Maximizing g(m) finds m where q̂ = N/p̂(m) is nearest an integer,
    which corresponds to p̂ being a potential factor.
    
    Args:
        m: Fractional comb index
        k: Comb wave number
        N: Target semiprime
        logN: log(N) (precomputed)
    
    Returns:
        score: -log(distance to nearest integer), or large value if dist < 1e-100
    
    Note:
        Use this as objective for line search; peak indicates best m.
    """
    # Compute p̂(m)
    p_hat = mp.exp((logN - (2 * mp.pi * m) / mp.mpf(k)) / 2)
    
    # Compute q̂ = N / p̂
    N_mp = mp.mpf(N)
    q_hat = N_mp / p_hat
    
    # Distance to nearest integer
    q_nearest = mp.nint(q_hat)
    dist = mp.fabs(q_hat - q_nearest)
    
    # Avoid log(0); return large score for exact hits
    if dist < mp.mpf(1e-100):
        return mp.mpf(100.0)
    
    # Score: higher is better
    score = -mp.log(dist)
    return score


def golden_section_maximize(f: Callable[[mp.mpf], mp.mpf], 
                             a: mp.mpf, b: mp.mpf,
                             tol: float = 1e-10, max_iter: int = 100) -> Tuple[mp.mpf, mp.mpf]:
    """
    Golden-section search for maximizing f on [a, b].
    
    Pure-Python implementation using mpmath for high precision.
    
    Args:
        f: Objective function to maximize
        a: Left bound
        b: Right bound
        tol: Convergence tolerance
        max_iter: Maximum iterations
    
    Returns:
        (x_max, f_max): Location and value of maximum
    """
    phi = (mp.sqrt(5) - 1) / 2  # Golden ratio conjugate
    
    # Initial bracketing
    x1 = b - phi * (b - a)
    x2 = a + phi * (b - a)
    f1 = f(x1)
    f2 = f(x2)
    
    for _ in range(max_iter):
        if mp.fabs(b - a) < tol:
            break
        
        if f1 > f2:
            # Maximum in [a, x2]
            b = x2
            x2 = x1
            f2 = f1
            x1 = b - phi * (b - a)
            f1 = f(x1)
        else:
            # Maximum in [x1, b]
            a = x1
            x1 = x2
            f1 = f2
            x2 = a + phi * (b - a)
            f2 = f(x2)
    
    # Return best point
    if f1 > f2:
        return x1, f1
    else:
        return x2, f2


def brent_maximize(f: Callable[[mp.mpf], mp.mpf],
                   a: mp.mpf, b: mp.mpf,
                   tol: float = 1e-10, max_iter: int = 100) -> Tuple[mp.mpf, mp.mpf]:
    """
    Brent's method for maximizing f on [a, b] without derivatives.
    
    Combines golden-section with parabolic interpolation for faster convergence.
    Pure-Python implementation using mpmath.
    
    Args:
        f: Objective function to maximize (must be unimodal on [a, b])
        a: Left bound
        b: Right bound
        tol: Convergence tolerance
        max_iter: Maximum iterations
    
    Returns:
        (x_max, f_max): Location and value of maximum
    
    Note:
        For non-unimodal functions, falls back to golden-section.
    """
    phi = (3 - mp.sqrt(5)) / 2  # For golden section fallback
    
    # Initialize
    x = w = v = a + phi * (b - a)
    fx = fw = fv = f(x)
    
    d = e = b - a
    
    for _ in range(max_iter):
        m = (a + b) / 2
        tol1 = tol * mp.fabs(x) + tol
        tol2 = 2 * tol1
        
        # Check convergence
        if mp.fabs(x - m) <= tol2 - (b - a) / 2:
            return x, fx
        
        # Try parabolic interpolation
        if mp.fabs(e) > tol1:
            # Fit parabola through (w, fw), (v, fv), (x, fx)
            r = (x - w) * (fx - fv)
            q = (x - v) * (fx - fw)
            p = (x - v) * q - (x - w) * r
            q = 2 * (q - r)
            
            if q > 0:
                p = -p
            else:
                q = -q
            
            etemp = e
            e = d
            
            # Check if parabolic step is acceptable
            if mp.fabs(p) < mp.fabs(q * etemp / 2) and p > q * (a - x) and p < q * (b - x):
                d = p / q
                u = x + d
                
                # Don't evaluate too close to bounds
                if u - a < tol2 or b - u < tol2:
                    d = tol1 if x < m else -tol1
            else:
                # Golden section step
                e = (a - x) if x >= m else (b - x)
                d = phi * e
        else:
            # Golden section step
            e = (a - x) if x >= m else (b - x)
            d = phi * e
        
        # Evaluate at new point
        u = x + d if mp.fabs(d) >= tol1 else x + (tol1 if d > 0 else -tol1)
        fu = f(u)
        
        # Update bracketing
        if fu >= fx:
            if u < x:
                b = x
            else:
                a = x
            v, fv = w, fw
            w, fw = x, fx
            x, fx = u, fu
        else:
            if u < x:
                a = u
            else:
                b = u
            
            if fu >= fw or w == x:
                v, fv = w, fw
                w, fw = u, fu
            elif fu >= fv or v == x or v == w:
                v, fv = u, fu
    
    return x, fx


def refine_m_with_line_search(m_initial: mp.mpf, k: float, N: int, logN: mp.mpf,
                               delta: float = 0.01, dps: int = 1000) -> Tuple[mp.mpf, mp.mpf]:
    """
    Refine m using line search to maximize integer-resonance.
    
    Searches [m_initial - delta, m_initial + delta] for m that maximizes
    -log(dist(N/p̂(m), ℤ)).
    
    Args:
        m_initial: Seed m from coarse sweep
        k: Comb parameter
        N: Target semiprime
        logN: log(N)
        delta: Search radius (default 0.01)
        dps: Precision
    
    Returns:
        (m_refined, score): Refined m and resonance score
    
    Example:
        >>> m_seed = mp.mpf(0.005)
        >>> m_refined, score = refine_m_with_line_search(m_seed, k, N, logN)
        >>> # Now check gcd(N, round(p̂(m_refined)))
    """
    with mp.workdps(dps):
        # Define objective as function of m only
        def objective(m: mp.mpf) -> mp.mpf:
            return integer_resonance_objective(m, k, N, logN)
        
        # Bounds
        a = m_initial - mp.mpf(delta)
        b = m_initial + mp.mpf(delta)
        
        # Line search (Brent is faster than golden-section for smooth objectives)
        m_refined, score = brent_maximize(objective, a, b, tol=1e-12, max_iter=200)
        
        return m_refined, score


if __name__ == "__main__":
    # Smoke test
    mp.mp.dps = 200
    
    # Test on RSA-100
    RSA_100 = int("1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139")
    logN = mp.log(mp.mpf(RSA_100))
    k = 0.30
    
    print("=== Resonance Search Smoke Test ===")
    print(f"N: RSA-100 (330 bits)")
    print(f"k: {k}\n")
    
    # Test objective at a few m values
    print("Resonance scores at various m:")
    for m_test in [mp.mpf(x) for x in [-0.02, -0.01, 0.0, 0.01, 0.02]]:
        score = integer_resonance_objective(m_test, k, RSA_100, logN)
        print(f"  m = {mp.nstr(m_test, 8):>12s}: score = {mp.nstr(score, 10)}")
    
    # Line search refinement
    print("\nLine search refinement:")
    m_initial = mp.mpf(0.0)
    m_refined, score_refined = refine_m_with_line_search(m_initial, k, RSA_100, logN, delta=0.05)
    
    print(f"  m_initial = {mp.nstr(m_initial, 10)}")
    print(f"  m_refined = {mp.nstr(m_refined, 10)}")
    print(f"  score_refined = {mp.nstr(score_refined, 10)}")
    
    # Check p̂ and q̂ at refined m
    p_hat = mp.exp((logN - (2 * mp.pi * m_refined) / mp.mpf(k)) / 2)
    q_hat = mp.mpf(RSA_100) / p_hat
    q_nearest = int(mp.nint(q_hat))
    dist = mp.fabs(q_hat - mp.mpf(q_nearest))
    
    print(f"\nAt refined m:")
    print(f"  p̂ = {mp.nstr(p_hat, 20)}")
    print(f"  q̂ = {mp.nstr(q_hat, 20)}")
    print(f"  nearest q = {q_nearest}")
    print(f"  dist to int = {mp.nstr(dist, 15)}")
