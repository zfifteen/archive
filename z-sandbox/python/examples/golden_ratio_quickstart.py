#!/usr/bin/env python3
"""
Quick Start Example: Golden Ratio Geometric Factorization

This example demonstrates the key concepts of the validation suite
without running the full validation ladder.
"""

import sys
import os
# Add project root to path (go up two levels from python/examples/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python import golden_ratio_factorization_50_100bit as phase1
from mpmath import mp

# Set display precision
mp.dps = 50


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_constants():
    """Demonstrate mathematical constants."""
    print_header("Mathematical Constants")
    print(f"\nGolden Ratio (φ):")
    print(f"  φ = (1 + √5) / 2")
    print(f"  φ ≈ {float(phase1.PHI):.15f}")
    print(f"\ne² Invariant:")
    print(f"  e² ≈ {float(phase1.E2):.15f}")
    print(f"\nPentagonal Property:")
    print(f"  In a regular pentagon, diagonal/side = φ")
    print(f"  Pentagonal ratio = {float(phase1.PENTAGONAL_RATIO):.15f}")


def demo_embedding():
    """Demonstrate pentagonal embedding."""
    print_header("Pentagonal Embedding")
    
    N = 899  # 29 × 31
    print(f"\nExample: N = {N} = 29 × 31")
    
    coords = phase1.pentagonal_embedding(N, dims=5)
    print(f"\n5-Dimensional Pentagonal Embedding:")
    for i, coord in enumerate(coords):
        print(f"  Dimension {i+1}: {float(coord):.6f}")
    
    print(f"\nEmbedding uses φⁿ scaling:")
    print(f"  θ(n) = φⁿ · frac(n / (e² · φⁿ))")


def demo_geometric_resolution():
    """Demonstrate geometric resolution function."""
    print_header("Geometric Resolution θ'(n, k)")
    
    N = 899
    print(f"\nExample: N = {N}")
    print(f"\nθ'(n, k) = φ · ((n mod φ) / φ)^k")
    print(f"\nOptimal k ≈ 0.3 for ~15% prime density enhancement")
    print(f"\nTesting different k values:")
    
    for k in [0.1, 0.2, 0.3, 0.4, 0.5]:
        theta = phase1.theta_prime_adaptive(N, k)
        print(f"  k = {k:.1f}: θ'({N}, {k:.1f}) = {float(theta):.6f}")


def demo_pentagonal_distance():
    """Demonstrate pentagonal distance calculation."""
    print_header("Pentagonal Distance")
    
    N = 899
    p = 29
    
    print(f"\nCalculating distance between N={N} and factor p={p}")
    
    emb_N = phase1.pentagonal_embedding(N)
    emb_p = phase1.pentagonal_embedding(p)
    
    dist = phase1.pentagonal_distance(emb_N, emb_p, N)
    
    print(f"\nDistance metric includes:")
    print(f"  - Torus topology (wraparound in [0,1))")
    print(f"  - φ-weighting by dimension")
    print(f"  - Curvature κ(N) = ln(N+1) / (e² · ln(N))")
    print(f"\nPentagonal distance: {float(dist):.6f}")


def demo_k_scan():
    """Demonstrate adaptive k-scan."""
    print_header("Adaptive k-Scan")
    
    N = 899
    sqrtN = 29
    
    print(f"\nAdaptive k-scan explores multiple k values")
    print(f"to find optimal geometric resolution.")
    print(f"\nExample: N = {N}, √N = {sqrtN}")
    print(f"\nScanning k ∈ [0.1, 0.5] with 5 steps...")
    
    candidates = phase1.adaptive_k_scan(N, sqrtN, k_range=(0.1, 0.5), k_steps=5)
    
    if candidates:
        print(f"\nFound {len(candidates)} candidate(s):")
        for c in candidates[:5]:  # Show first 5
            print(f"  {c}")
    else:
        print(f"\nNo candidates found in this quick scan.")
    
    print(f"\nIn full validation, candidates are verified using")
    print(f"pentagonal distance and primality tests.")


def main():
    """Run quick start demonstration."""
    print("\n" + "=" * 70)
    print("  Golden Ratio Geometric Factorization")
    print("  Quick Start Demonstration")
    print("=" * 70)
    print("\nThis demo shows the key concepts without running")
    print("the full validation ladder.")
    
    demo_constants()
    demo_embedding()
    demo_geometric_resolution()
    demo_pentagonal_distance()
    demo_k_scan()
    
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Run validation tests:")
    print("     python3 tests/test_golden_ratio_factorization.py")
    print("\n  2. Run Phase 1 validation (50-100 bits):")
    print("     python3 python/golden_ratio_factorization_50_100bit.py")
    print("\n  3. Run master validation suite:")
    print("     python3 python/golden_ratio_factorization_master.py")
    print("\n  4. Read the complete guide:")
    print("     cat GOLDEN_RATIO_VALIDATION_GUIDE.md")
    print("\nFor Discussion #18:")
    print("  https://github.com/zfifteen/z-sandbox/discussions/18")
    print()


if __name__ == "__main__":
    main()
