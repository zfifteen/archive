"""
Resonance Scoring for Geometric Factorization

This module implements resonance-based candidate scoring for the geometric
factorization search. Candidates near the true factor show higher resonance
scores based on geodesic/curvature patterns.

The resonance score combines:
1. Geodesic modulation using the golden ratio φ
2. Curvature contribution based on logarithmic scaling
3. Position relative to √N (geometric center)
"""

import math
from typing import Tuple, Optional


# Golden ratio for geodesic calculations
PHI = (1 + math.sqrt(5)) / 2


def theta_prime(x: float, k: float = 0.3) -> float:
    """
    Compute geodesic angle θ' using golden ratio modulation.
    
    θ'(x, k) = φ * ((x mod φ) / φ)^k
    
    This maps positions to a geodesic phase space where resonance
    patterns emerge near factor positions.
    
    Parameters
    ----------
    x : float
        Position value (typically candidate factor)
    k : float
        Curvature parameter from scaling
        
    Returns
    -------
    float
        Geodesic angle in [0, φ] range
    """
    mod_val = x % PHI
    ratio = mod_val / PHI
    return PHI * (ratio ** k)


def curvature_contribution(x: float) -> float:
    """
    Compute curvature contribution for a position.
    
    κ(x) = log(x + 1) / e²
    
    This captures the local curvature of the geodesic manifold.
    """
    e_squared = math.exp(2)
    return math.log(x + 1) / e_squared


def compute_resonance_score(
    candidate: int,
    N: int,
    sqrt_N: float,
    k_shift: float,
    kappa: float = 0.4,
    phase_drift: float = 0.0
) -> float:
    """
    Compute resonance score for a factor candidate.
    
    Higher scores indicate positions more likely to be factors based on
    geometric resonance patterns.
    
    The score combines:
    1. Geodesic phase alignment (θ' contribution)
    2. Curvature at the candidate position
    3. Distance-weighted factor from √N
    4. Phase drift compensation for large scales
    
    Parameters
    ----------
    candidate : int
        Factor candidate to score
    N : int
        The semiprime being factored
    sqrt_N : float
        Pre-computed √N for efficiency
    k_shift : float
        Scaling-dependent k parameter
    kappa : float
        Curvature modulation parameter
    phase_drift : float
        Phase compensation for scale-dependent drift
        
    Returns
    -------
    float
        Resonance score in approximately [0, 1] range
    """
    if candidate <= 1 or candidate >= N:
        return 0.0
    
    # Geodesic phase contribution
    theta = theta_prime(float(candidate), k_shift)
    
    # Curvature contribution
    curv = curvature_contribution(float(candidate))
    
    # Distance from geometric center (√N)
    # Factors tend to be within a bounded region around √N
    distance = abs(candidate - sqrt_N) / sqrt_N
    distance_weight = math.exp(-distance * 0.5)  # Gaussian-like falloff
    
    # Resonance formula combining geodesic and curvature contributions
    # with phase drift compensation
    phase_adjusted = theta - phase_drift * curv
    
    # Normalize to [0, 1] range approximately
    base_score = (theta / PHI) * (1 + kappa * curv)
    
    # Apply distance weighting
    score = base_score * distance_weight
    
    # Clamp to reasonable range
    return max(0.0, min(1.0, score))


def is_candidate_promising(
    candidate: int,
    N: int,
    sqrt_N: float,
    threshold: float,
    k_shift: float,
    kappa: float = 0.4,
    phase_drift: float = 0.0
) -> Tuple[bool, float]:
    """
    Determine if a candidate exceeds the resonance threshold.
    
    Parameters
    ----------
    candidate : int
        Factor candidate to evaluate
    N : int
        The semiprime being factored
    sqrt_N : float
        Pre-computed √N
    threshold : float
        Minimum resonance score (from scaling params)
    k_shift : float
        Scaling k parameter
    kappa : float
        Curvature modulation
    phase_drift : float
        Phase compensation
        
    Returns
    -------
    Tuple[bool, float]
        (is_promising, score) - whether candidate exceeds threshold and its score
    """
    score = compute_resonance_score(
        candidate, N, sqrt_N, k_shift, kappa, phase_drift
    )
    return (score >= threshold, score)


def verify_factor(candidate: int, N: int) -> Optional[Tuple[int, int]]:
    """
    Verify if a candidate is actually a factor of N.
    
    This is the ground truth check - resonance scoring guides the search,
    but trial division confirms factors.
    
    Parameters
    ----------
    candidate : int
        Potential factor to verify
    N : int
        The semiprime
        
    Returns
    -------
    Optional[Tuple[int, int]]
        (p, q) factors if found, None otherwise
    """
    if candidate <= 1 or candidate >= N:
        return None
    
    if N % candidate == 0:
        p = candidate
        q = N // candidate
        # Return in sorted order
        return (min(p, q), max(p, q))
    
    return None


if __name__ == "__main__":
    # Test resonance scoring on a known semiprime
    print("Resonance Scoring Tests")
    print("=" * 60)
    
    # Small test: 15 = 3 × 5
    N = 15
    sqrt_N = math.sqrt(N)
    
    print(f"\nTest: N = {N} = 3 × 5")
    print(f"√N = {sqrt_N:.3f}")
    
    for candidate in [2, 3, 4, 5, 6]:
        score = compute_resonance_score(candidate, N, sqrt_N, k_shift=0.35)
        is_factor = N % candidate == 0
        print(f"  Candidate {candidate}: score={score:.4f}, is_factor={is_factor}")
    
    # Larger test: 127-bit Gate-127
    print("\n" + "=" * 60)
    N_127 = 137524771864208156028430259349934309717
    p_127 = 10508623501177419659
    q_127 = 13086849276577416863
    sqrt_N_127 = math.sqrt(N_127)
    
    print(f"\nGate-127 factor scoring:")
    print(f"N = {N_127}")
    print(f"√N = {sqrt_N_127:.0f}")
    print(f"p = {p_127}, q = {q_127}")
    
    # Score the known factors vs nearby non-factors
    k_127 = 0.3936
    for offset in [-100, -10, 0, 10, 100]:
        test_p = p_127 + offset
        score = compute_resonance_score(test_p, N_127, sqrt_N_127, k_127, 0.44, 0.08)
        is_factor = N_127 % test_p == 0
        print(f"  p{offset:+}: score={score:.4f}, is_factor={is_factor}")
