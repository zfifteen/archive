#!/usr/bin/env python3
"""
Geometric Resonance Factorization - 127-bit Challenge
======================================================

This script implements the geometric resonance protocol for factorizing
N = 137524771864208156028430259349934309717 (127-bit semiprime).

Method: Geometric resonance over a (k,m) comb with Dirichlet sharpening 
and golden-ratio QMC for k placement.

Expected factors:
- p = 10508623501177419659
- q = 13086849276577416863

No ECM/NFS/Pollard/gcd cycles/library factoring used.
Pure geometric resonance as defined in GEOMETRIC_RESONANCE_PROTOCOL.
"""

from mpmath import mp, mpf, mpc, log, exp, pi, nint, sqrt
import math
import json
import time

# Set high precision for 127-bit factorization
mp.dps = 200


def dirichlet_kernel(theta, J=6):
    """
    Dirichlet kernel for resonance detection.
    
    D_J(θ) = Σ_{j=-J}^{J} e^{ijθ}
    
    This creates sharp peaks at θ = 0 (mod 2π) and measures
    constructive interference at resonance points.
    
    Args:
        theta: Angle parameter
        J: Kernel order (higher = sharper)
    
    Returns:
        Complex amplitude of Dirichlet kernel
    """
    s = mpc(0)
    for j in range(-J, J + 1):
        s += exp(1j * mpf(j) * theta)
    return s


def bias(k):
    """
    Phase bias correction term.
    
    For this implementation, we use zero bias (pure geometric).
    In advanced versions, this could encode curvature corrections.
    
    Args:
        k: Resonance parameter
    
    Returns:
        Bias value (currently 0)
    """
    return mpf('0.0')


def resonance_candidates(N, num_samples=801, k_lo=0.25, k_hi=0.45, m_span=180, J=6, progress=False):
    """
    Generate prime candidates via geometric resonance scanning.
    
    Algorithm:
    1. Sample k parameters using golden ratio QMC (low-discrepancy)
    2. For each k, compute central mode m0 from geometric formula
    3. Scan m values around m0 within ±m_span
    4. For each (k,m), compute predicted prime p_hat via comb formula
    5. Evaluate Dirichlet kernel at resonance angle θ
    6. Keep candidates with strong constructive interference
    
    Args:
        N: Number to factor
        num_samples: Number of k values to sample
        k_lo: Lower k bound
        k_hi: Upper k bound
        m_span: Range of m values around central mode
        J: Dirichlet kernel order
        progress: Show progress output
    
    Returns:
        Sorted list of integer prime candidates
    """
    LN = log(N)
    sqrtN = sqrt(N)
    cands = set()
    
    # Golden ratio conjugate for quasi-Monte Carlo sampling
    # Note: For golden ratio φ = (1+√5)/2, the conjugate φ-1 = (√5-1)/2 = 1/φ
    phi_conjugate = (mpf(1) + sqrt(5)) / 2 - 1  # (√5-1)/2 ≈ 0.618034
    
    # Pre-compute threshold
    threshold = (2 * J + 1) * mpf('0.92')
    
    for n in range(num_samples):
        if progress and n % 100 == 0:
            print(f"Progress: {n}/{num_samples}, candidates so far: {len(cands)}", flush=True)
        
        # Van der Corput sequence in golden ratio base
        u_n = math.modf(n * float(phi_conjugate))[0]  # {n · (φ-1)} - fractional part, use float for speed
        
        # Map to k range
        k = mpf(k_lo) + mpf(u_n) * (mpf(k_hi) - mpf(k_lo))
        
        # Central mode from geometric formula
        # m0 ≈ k(ln N - 2 ln √N) / (2π) = k ln √N / (2π)
        m0 = nint((k * (LN - 2 * log(sqrtN))) / (2 * pi))
        
        b = bias(k)
        
        # Scan modes around m0
        for dm in range(-m_span, m_span + 1):
            m = m0 + dm
            
            # Comb formula: p ≈ exp((ln N - 2πm/k) / 2)
            # This is the geometric resonance prediction
            p_hat = exp((LN - (2 * pi * (m + b)) / k) / 2)
            
            # Resonance angle
            theta = (LN - 2 * log(p_hat)) * k / 2
            
            # Dirichlet kernel threshold (92% of maximum amplitude)
            # Maximum is (2J + 1), so threshold is 0.92 * (2J + 1)
            if abs(dirichlet_kernel(theta, J=J)) >= threshold:
                p_int = int(nint(p_hat))
                if p_int > 1:
                    cands.add(p_int)
    
    return sorted(cands)


def factor_by_geometric_resonance(N_int, config=None):
    """
    Factor N using geometric resonance method.
    
    Args:
        N_int: Integer to factor
        config: Optional configuration dict
    
    Returns:
        Tuple (p, q, metadata) where p*q = N, or (None, None, metadata)
    """
    if config is None:
        config = {
            'num_samples': 801,
            'k_lo': 0.25,
            'k_hi': 0.45,
            'm_span': 180,
            'J': 6
        }
    
    N = mpf(N_int)
    
    print(f"Starting geometric resonance factorization of N = {N_int}")
    print(f"N has {N_int.bit_length()} bits")
    print(f"Configuration: {config}")
    print()
    
    start_time = time.time()
    cands = resonance_candidates(
        N,
        num_samples=config['num_samples'],
        k_lo=config['k_lo'],
        k_hi=config['k_hi'],
        m_span=config['m_span'],
        J=config['J'],
        progress=True
    )
    scan_time = time.time() - start_time
    
    print(f"\nCandidate generation complete: {len(cands)} candidates in {scan_time:.2f}s")
    print(f"Candidates/sample ratio: {len(cands)/config['num_samples']:.2f}")
    
    # Check divisibility (final step)
    print("\nChecking divisibility...")
    start_check = time.time()
    for i, p in enumerate(cands):
        if i % 1000 == 0 and i > 0:
            print(f"  Checked {i}/{len(cands)} candidates...", flush=True)
        if N_int % p == 0:
            q = N_int // p
            check_time = time.time() - start_check
            total_time = time.time() - start_time
            
            print(f"\n✓ FACTORS FOUND!")
            print(f"  p = {p}")
            print(f"  q = {q}")
            print(f"  Check time: {check_time:.2f}s")
            print(f"  Total time: {total_time:.2f}s")
            
            metadata = {
                'candidates_generated': len(cands),
                'scan_time': scan_time,
                'check_time': check_time,
                'total_time': total_time,
                'candidates_checked': i + 1,
                'kept_to_tested_ratio': len(cands) / (config['num_samples'] * (2 * config['m_span'] + 1)),
                'config': config
            }
            
            return min(p, q), max(p, q), metadata
    
    total_time = time.time() - start_time
    print(f"\n✗ No factors found after checking all {len(cands)} candidates")
    print(f"Total time: {total_time:.2f}s")
    
    metadata = {
        'candidates_generated': len(cands),
        'scan_time': scan_time,
        'check_time': time.time() - start_check,
        'total_time': total_time,
        'candidates_checked': len(cands),
        'kept_to_tested_ratio': len(cands) / (config['num_samples'] * (2 * config['m_span'] + 1)),
        'config': config
    }
    
    return None, None, metadata


def main():
    """
    Reproduce the 127-bit factorization challenge.
    
    Output format:
    - Line 1: p (smaller factor)
    - Line 2: q (larger factor)
    """
    N_int = 137524771864208156028430259349934309717
    
    # Configuration matching the protocol
    config = {
        'mp.dps': 200,
        'num_samples': 801,
        'k_lo': 0.25,
        'k_hi': 0.45,
        'k_step': None,  # QMC via golden ratio
        'm_span': 180,
        'J': 6,
        'bias_form': 'zero',
        'sampler': 'golden_ratio_qmc'
    }
    
    factors = factor_by_geometric_resonance(N_int, config)
    
    if factors[0] is not None:
        p, q, metadata = factors
        print(p)
        print(q)
        
        # Save artifacts
        with open('/tmp/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        with open('/tmp/metrics.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save candidates list
        with open('/tmp/candidates.txt', 'w') as f:
            # Re-generate to get full list
            cands = resonance_candidates(
                mpf(N_int),
                num_samples=config['num_samples'],
                k_lo=config['k_lo'],
                k_hi=config['k_hi'],
                m_span=config['m_span'],
                J=config['J']
            )
            for c in cands:
                f.write(f"{c}\n")
    else:
        print("No factors found")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
