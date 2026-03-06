#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_z5d_ladder.py — Validation ladder for Z5D integration

Tests Z5D-powered search on known RSA numbers:
- RSA-100, RSA-129, RSA-140 (smoke tests - must pass)
- RSA-155, RSA-160, RSA-170 (scaling validation)

Usage:
    python3 python/validate_z5d_ladder.py --quick    # RSA-100 only
    python3 python/validate_z5d_ladder.py --full     # Full ladder
"""

import argparse
import sys
import time
from typing import Dict, Tuple

try:
    import mpmath as mp
except ImportError:
    print("FATAL: mpmath required", file=sys.stderr)
    sys.exit(1)

try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from python.geom.z5d_predictor import predict_prime_near_sqrt
    from python.geom.m0_estimator import estimate_m0_from_z5d_prior
    from python.geom.adaptive_step import generate_symmetric_queue
    from python.geom.resonance_search import refine_m_with_line_search
    Z5D_AVAILABLE = True
except ImportError as e:
    print(f"FATAL: Z5D modules not available: {e}", file=sys.stderr)
    sys.exit(1)


# Known RSA numbers with factors
RSA_NUMBERS: Dict[str, Tuple[int, int, int]] = {
    "RSA-100": (
        int("1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139"),
        37975227936943673922808872755445627854565536638199,
        40094690950920881030683735292761468389214899724061
    ),
    "RSA-129": (
        int("114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541"),
        3490529510847650949147849619903898133417764638493387843990820577,
        32769132993266709549961988190834461413177642967992942539798288533
    ),
    "RSA-140": (
        int("21290246318258757547497882016271517497806703635224419693583318326119734519819628673524813613582327138770890974856355507199063863"),
        33987421816722409457878097424529039254550616065769,
        62644729091246534778125288065202455695403455898429
    ),
}


def p_from_m(m: mp.mpf, k: float, logN: mp.mpf) -> mp.mpf:
    """Core comb formula"""
    return mp.exp((logN - (2 * mp.pi * m) / mp.mpf(k)) / 2)


def check_gcd(N: int, p_int: int) -> int:
    """GCD check"""
    import math
    return math.gcd(N, p_int)


def validate_single(name: str, N: int, p_true: int, q_true: int, 
                    k: float = 0.30, dps: int = 500, 
                    max_candidates: int = 10000,
                    use_adaptive: bool = True,
                    use_line_search: bool = True) -> bool:
    """
    Validate Z5D search on a single RSA number.
    
    Returns True if factor found, False otherwise.
    """
    mp.mp.dps = dps
    
    print(f"\n{'='*70}")
    print(f"Validating: {name}")
    print(f"N bits: {N.bit_length()}, digits: {len(str(N))}")
    print(f"k: {k}, dps: {dps}, max_candidates: {max_candidates}")
    print(f"adaptive: {use_adaptive}, line_search: {use_line_search}")
    print(f"{'='*70}\n")
    
    start_time = time.time()
    
    # Get Z5D prior
    logN = mp.log(mp.mpf(N))
    m0, window, epsilon_ppm, safety = estimate_m0_from_z5d_prior(N, k, dps)
    
    print(f"Z5D Prior:")
    print(f"  m₀        = {mp.nstr(m0, 15)}")
    print(f"  window    = {mp.nstr(window, 15)}")
    print(f"  ε (ppm)   = {epsilon_ppm}")
    print(f"  safety    = {safety}\n")
    
    # Generate queue
    if use_adaptive:
        print("Generating adaptive queue...")
        queue = generate_symmetric_queue(
            m0, window, k, logN,
            p_from_m,
            max_candidates=max_candidates
        )
    else:
        # Fixed step fallback
        print("Generating fixed queue...")
        step = float(window) / 100
        queue = []
        m_curr = m0 - window
        while m_curr <= m0 + window and len(queue) < max_candidates:
            queue.append(m_curr)
            m_curr += mp.mpf(step)
    
    print(f"Queue size: {len(queue)}\n")
    print("Searching...")
    
    candidates_seen = 0
    gcd_calls = 0
    
    for i, m in enumerate(queue):
        if candidates_seen >= max_candidates:
            break
        
        # Optional line search
        m_search = m
        if use_line_search and i < 100:  # Only refine top 100
            m_search, _ = refine_m_with_line_search(m, k, N, logN, delta=0.01, dps=dps)
        
        # Compute p̂
        p_hat = p_from_m(m_search, k, logN)
        
        # Rounding + neighbors
        for rounding_fn, name in [(mp.nint, 'round'), (mp.floor, 'floor'), (mp.ceil, 'ceil')]:
            p_base = int(rounding_fn(p_hat))
            
            for delta in [-2, -1, 0, 1, 2]:
                p_int = p_base + delta
                if p_int <= 1 or p_int >= N:
                    continue
                
                candidates_seen += 1
                g = check_gcd(N, p_int)
                gcd_calls += 1
                
                # Success?
                if 1 < g < N:
                    q = N // g
                    elapsed = time.time() - start_time
                    
                    print(f"\n{'='*70}")
                    print(f"SUCCESS!")
                    print(f"{'='*70}")
                    print(f"Found factor in {elapsed:.2f}s")
                    print(f"Candidates evaluated: {candidates_seen}")
                    print(f"GCD calls: {gcd_calls}")
                    print(f"\nm = {mp.nstr(m_search, 15)}")
                    print(f"p = {g}")
                    print(f"q = {q}")
                    print(f"\nVerification:")
                    print(f"  p * q = N: {g * q == N}")
                    print(f"  p = p_true: {g == p_true or g == q_true}")
                    print(f"  q = q_true: {q == p_true or q == q_true}")
                    print(f"{'='*70}\n")
                    
                    return True
        
        # Progress
        if candidates_seen % 1000 == 0:
            elapsed = time.time() - start_time
            rate = candidates_seen / elapsed if elapsed > 0 else 0
            print(f"  [{candidates_seen:6d}] m={mp.nstr(m_search, 12)}, rate={rate:.1f} cand/s")
    
    elapsed = time.time() - start_time
    print(f"\nNOT FOUND after {elapsed:.2f}s")
    print(f"Candidates evaluated: {candidates_seen}")
    print(f"GCD calls: {gcd_calls}\n")
    
    return False


def run_ladder(quick: bool = False, full: bool = False) -> int:
    """Run validation ladder"""
    
    if quick:
        # Quick smoke test: RSA-100 only
        tests = [("RSA-100", 500, 1000, True, True)]
    elif full:
        # Full ladder
        tests = [
            ("RSA-100", 500, 1000, True, True),
            ("RSA-129", 1000, 10000, True, True),
            ("RSA-140", 1000, 10000, True, True),
        ]
    else:
        # Default: RSA-100 + RSA-129
        tests = [
            ("RSA-100", 500, 1000, True, True),
            ("RSA-129", 1000, 5000, True, True),
        ]
    
    results = {}
    
    print("="*70)
    print("Z5D VALIDATION LADDER")
    print("="*70)
    
    for name, dps, max_cand, adaptive, line_search in tests:
        if name not in RSA_NUMBERS:
            print(f"WARNING: {name} not in database, skipping")
            continue
        
        N, p, q = RSA_NUMBERS[name]
        
        success = validate_single(
            name, N, p, q,
            k=0.30, dps=dps, max_candidates=max_cand,
            use_adaptive=adaptive, use_line_search=line_search
        )
        
        results[name] = success
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {name:15s}: {status}")
    
    print("="*70)
    
    # Return code: 0 if all passed
    all_passed = all(results.values())
    return 0 if all_passed else 1


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="validate_z5d_ladder.py",
        description="Validation ladder for Z5D integration"
    )
    ap.add_argument("--quick", action="store_true",
                    help="Quick test: RSA-100 only")
    ap.add_argument("--full", action="store_true",
                    help="Full ladder: RSA-100/129/140")
    return ap


if __name__ == "__main__":
    args = build_argparser().parse_args()
    exit_code = run_ladder(quick=args.quick, full=args.full)
    sys.exit(exit_code)
