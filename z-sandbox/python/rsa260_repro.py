#!/usr/bin/env python3
"""
RSA-260 Geometric Factorization Runner

This script implements geometric factorization for RSA-260 with strict requirements:
1. Center fixed at log(N)/2 (never shifted by bias)
2. High precision: mpmath with dps≥1000
3. Fractional m sampling around m₀ (not integer-m)
4. Distance-based ranking: |log(p) - center|
5. Deterministic PRP test (Miller-Rabin)
6. Full parameter logging

RSA-260 Canonical Value:
22112825529529666435281085255026230927612089502470015394413748319128822941402001986512729726569746599085900330031400051170742204560859276357953757185954298838958709229238491006703034124620545784566413664540684214361293017694020846391065875914794251435144458199

References:
- https://en.wikipedia.org/wiki/RSA_numbers
- Issue: Locked on RSA-260
"""

import sys
import os
import argparse
import time
from datetime import datetime
from mpmath import mp, mpf, log as mplog, exp as mpexp, pi as mp_pi
from typing import List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import geometric modules
try:
    from python.geom.m0_estimator import estimate_m0_balanced, get_resonance_metadata
except ImportError:
    from geom.m0_estimator import estimate_m0_balanced, get_resonance_metadata


# RSA-260 canonical value (260 decimal digits, 862 bits)
RSA_260 = int(
    "22112825529529666435281085255026230927612089502470015394413748319128822941"
    "40200198651272972656974659908590033003140005117074220456085927635795375718"
    "59542988389587092292384910067030341246205457845664136645406842143612930176"
    "94020846391065875914794251435144458199"
)


def miller_rabin_deterministic(n: int, rounds: int = 32) -> bool:
    """
    Deterministic Miller-Rabin primality test.
    
    Uses first `rounds` primes as witnesses for determinism.
    For n < 3,317,044,064,679,887,385,961,981, using witnesses
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] is sufficient.
    
    Args:
        n: Number to test
        rounds: Number of rounds (uses first `rounds` primes)
        
    Returns:
        True if probably prime, False if composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # First 32 primes for deterministic testing
    witnesses = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
        59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131
    ]
    witnesses = witnesses[:min(rounds, len(witnesses))]
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Test with each witness
    for a in witnesses:
        if a >= n:
            continue
            
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
            
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        
        if composite:
            return False
    
    return True


def comb_formula(N: int, k: float, m: float, dps: int) -> int:
    """
    Comb formula: p_m = exp((log N - 2πm/k)/2)
    
    Args:
        N: Semiprime
        k: Wave number
        m: Fractional comb index
        dps: Decimal precision
        
    Returns:
        Candidate factor (as integer)
    """
    original_dps = mp.dps
    mp.dps = dps
    
    try:
        log_N = mplog(N)
        phase = 2 * mp_pi * m / k
        log_p = (log_N - phase) / 2
        p = mpexp(log_p)
        return int(p)
    finally:
        mp.dps = original_dps


def generate_fractional_candidates(
    N: int,
    k: float,
    m0: float,
    window: float,
    step: float,
    dps: int
) -> List[Tuple[float, int]]:
    """
    Generate candidates using fractional m sampling.
    
    Args:
        N: Semiprime
        k: Wave number
        m0: Center m value
        window: Window width (±window from m0)
        step: Step size for m
        dps: Decimal precision
        
    Returns:
        List of (m_value, candidate) tuples
    """
    candidates = []
    m = m0 - window
    
    while m <= m0 + window:
        try:
            p = comb_formula(N, k, m, dps)
            if p > 1 and p < N:
                candidates.append((m, p))
        except (ValueError, OverflowError):
            pass
        m += step
    
    return candidates


def rank_by_distance(
    candidates: List[Tuple[float, int]],
    N: int,
    dps: int
) -> List[Tuple[float, int, float]]:
    """
    Rank candidates by distance from center: |log(p) - log(N)/2|
    
    Args:
        candidates: List of (m, p) tuples
        N: Semiprime
        dps: Decimal precision
        
    Returns:
        List of (m, p, distance) tuples, sorted by distance (ascending)
    """
    original_dps = mp.dps
    mp.dps = dps
    
    try:
        log_N = mplog(N)
        center = log_N / 2
        
        ranked = []
        for m, p in candidates:
            log_p = mplog(p)
            distance = abs(float(log_p - center))
            ranked.append((m, p, distance))
        
        # Sort by distance (smallest first)
        ranked.sort(key=lambda x: x[2])
        return ranked
        
    finally:
        mp.dps = original_dps


def check_exact_division(N: int, p: int) -> Optional[int]:
    """
    Check if p divides N exactly.
    
    Args:
        N: Semiprime
        p: Candidate factor
        
    Returns:
        q if p*q == N, else None
    """
    if p <= 1 or p >= N:
        return None
    
    q, remainder = divmod(N, p)
    if remainder == 0 and p * q == N:
        return q
    return None


def run_rsa260_factorization(
    N: int = RSA_260,
    dps: int = 1000,
    k: float = 0.3,
    m0: Optional[float] = None,
    window: float = 0.05,
    step: float = 0.0001,
    neighbor_radius: int = 2,
    prp_rounds: int = 32,
    verbose: bool = True
) -> dict:
    """
    Run RSA-260 factorization with geometric methods.
    
    Args:
        N: Semiprime to factor (default: RSA-260)
        dps: Decimal precision (≥1000)
        k: Wave number parameter
        m0: Center m value (None = auto-estimate)
        window: Window width for m sampling
        step: Step size for fractional m
        neighbor_radius: Check ±neighbor_radius around candidates
        prp_rounds: Miller-Rabin rounds for PRP test
        verbose: Print progress
        
    Returns:
        Results dictionary
    """
    start_time = time.time()
    
    # Set precision
    original_dps = mp.dps
    mp.dps = dps
    
    try:
        # Log parameters
        log_N = mplog(N)
        center = log_N / 2
        
        if verbose:
            print("=" * 80)
            print("RSA-260 Geometric Factorization")
            print("=" * 80)
            print(f"Timestamp: {datetime.now().isoformat()}")
            print(f"N (bits): {N.bit_length()}")
            print(f"N (digits): {len(str(N))}")
            print(f"\nParameters:")
            print(f"  dps: {dps}")
            print(f"  k: {k}")
            print(f"  log(N): {float(log_N):.10f}")
            print(f"  center (log(N)/2): {float(center):.10f}")
        
        # Estimate m0 if not provided
        if m0 is None:
            m0 = estimate_m0_balanced(N, k, dps)
            if verbose:
                metadata = get_resonance_metadata(N, k, dps)
                print(f"\nResonance Analysis:")
                print(f"  m0 (balanced): {metadata['m0_balanced']:.6f}")
                print(f"  m0 (residue): {metadata['m0_residue']:.6f}")
                print(f"  m0 (recommended): {metadata['m0_recommended']:.6f}")
                print(f"  window: ±{metadata['window_width']:.6f}")
        
        if verbose:
            print(f"\nSampling Configuration:")
            print(f"  m0: {m0:.6f}")
            print(f"  window: ±{window}")
            print(f"  step: {step}")
            print(f"  expected_samples: {int(2 * window / step)}")
            print(f"  neighbor_radius: ±{neighbor_radius}")
            print(f"  prp_rounds: {prp_rounds}")
        
        # Generate candidates
        if verbose:
            print("\nGenerating fractional-m candidates...")
        candidates = generate_fractional_candidates(N, k, m0, window, step, dps)
        if verbose:
            print(f"  Generated {len(candidates)} candidates")
        
        # Rank by distance
        if verbose:
            print("\nRanking by distance from center...")
        ranked = rank_by_distance(candidates, N, dps)
        if verbose:
            print(f"  Top 10 by distance:")
            for i, (m, p, dist) in enumerate(ranked[:10]):
                print(f"    {i+1}. m={m:.6f}, p={p}, distance={dist:.6e}")
        
        # Test candidates
        if verbose:
            print("\nTesting candidates (PRP + exact division)...")
        
        tested = 0
        for m, p, dist in ranked:
            # Test p and neighbors
            for offset in range(-neighbor_radius, neighbor_radius + 1):
                p_test = p + offset
                if p_test <= 1 or p_test >= N:
                    continue
                
                tested += 1
                
                # PRP test
                if not miller_rabin_deterministic(p_test, prp_rounds):
                    continue
                
                # Exact division
                q = check_exact_division(N, p_test)
                if q is not None:
                    elapsed = time.time() - start_time
                    if verbose:
                        print(f"\n{'='*80}")
                        print("SUCCESS!")
                        print(f"{'='*80}")
                        print(f"p = {p_test}")
                        print(f"q = {q}")
                        print(f"Verification: p * q = {p_test * q}")
                        print(f"Match: {p_test * q == N}")
                        print(f"\nDiscovery:")
                        print(f"  m = {m:.6f}")
                        print(f"  offset = {offset}")
                        print(f"  distance = {dist:.6e}")
                        print(f"  tested = {tested}")
                        print(f"  elapsed = {elapsed:.2f}s")
                    
                    return {
                        'success': True,
                        'p': p_test,
                        'q': q,
                        'm': m,
                        'offset': offset,
                        'distance': dist,
                        'tested': tested,
                        'elapsed': elapsed,
                        'dps': dps,
                        'k': k,
                        'center': float(center)
                    }
        
        # No factor found
        elapsed = time.time() - start_time
        if verbose:
            print(f"\nNo factor found. Tested {tested} candidates in {elapsed:.2f}s")
        
        return {
            'success': False,
            'tested': tested,
            'elapsed': elapsed,
            'dps': dps,
            'k': k,
            'center': float(center)
        }
        
    finally:
        mp.dps = original_dps


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='RSA-260 Geometric Factorization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rsa260_repro.py --dps 1000 --k 0.3 --window 0.05 --step 0.0001
  python rsa260_repro.py --dps 2000 --k 0.29 --m0 0.0 --window 0.1 --step 0.00001
        """
    )
    
    parser.add_argument('--dps', type=int, default=1000,
                        help='Decimal precision (≥1000, default: 1000)')
    parser.add_argument('--k', type=float, default=0.3,
                        help='Wave number parameter (default: 0.3)')
    parser.add_argument('--m0', type=float, default=None,
                        help='Center m value (default: auto-estimate)')
    parser.add_argument('--window', type=float, default=0.05,
                        help='Window width for m sampling (default: 0.05)')
    parser.add_argument('--step', type=float, default=0.0001,
                        help='Step size for fractional m (default: 0.0001)')
    parser.add_argument('--neighbor_radius', type=int, default=2,
                        help='Check ±radius around candidates (default: 2)')
    parser.add_argument('--prp_rounds', type=int, default=32,
                        help='Miller-Rabin rounds (default: 32)')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    
    args = parser.parse_args()
    
    # Validate
    if args.dps < 1000:
        print("Error: dps must be ≥1000 for RSA-260")
        sys.exit(1)
    
    # Run
    result = run_rsa260_factorization(
        N=RSA_260,
        dps=args.dps,
        k=args.k,
        m0=args.m0,
        window=args.window,
        step=args.step,
        neighbor_radius=args.neighbor_radius,
        prp_rounds=args.prp_rounds,
        verbose=not args.quiet
    )
    
    # Exit code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
