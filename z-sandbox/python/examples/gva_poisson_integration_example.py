#!/usr/bin/env python3
"""
GVA-Poisson Integration Example

Demonstrates integration of Poisson summation duality analysis with
existing GVA (Geodesic Validation Assault) factorization framework.

This example shows how dual-domain arithmetic periodicity detection can
enhance factor search by pre-filtering candidates based on geometric
resonance in momentum space.

Usage:
    python python/examples/gva_poisson_integration_example.py
"""

import sys
import os
import numpy as np
from mpmath import mp, mpf, log, exp, sqrt as mpsqrt
import time

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from poisson_summation_duality import PoissonSummationDuality

# Set high precision
mp.dps = 100

# Universal constants
PHI = mpf((1 + mpsqrt(5)) / 2)
E2 = exp(2)


def gva_torus_embedding(n: int, dims: int = 7, k: float = 0.04) -> np.ndarray:
    """
    GVA-style torus geodesic embedding.
    
    Z = A(B / c) with c = e², iterative θ'(n, k) resolution.
    
    Args:
        n: Integer to embed
        dims: Torus dimensionality
        k: Geometric resolution parameter
        
    Returns:
        d-dimensional embedding on torus [0,1)^d
    """
    x = mpf(n) / E2
    coords = []
    
    for _ in range(dims):
        # θ'(n, k) geodesic resolution
        x = PHI * (x % 1.0)**mpf(k)
        coords.append(float(x % 1.0))
    
    return np.array(coords)


def classical_gva_factor_scan(N: int, search_radius: int = 1000) -> tuple:
    """
    Classical GVA factor search (baseline for comparison).
    
    Performs divisibility tests around sqrt(N) without Poisson enhancement.
    
    Args:
        N: Semiprime to factor
        search_radius: Number of candidates to test around sqrt(N)
        
    Returns:
        (found_factor, candidates_tested, time_elapsed)
    """
    sqrt_n = int(np.sqrt(N))
    start_time = time.time()
    
    candidates_tested = 0
    found_factor = None
    
    for candidate in range(max(2, sqrt_n - search_radius), sqrt_n + search_radius + 1):
        candidates_tested += 1
        
        if N % candidate == 0:
            found_factor = candidate
            break
    
    elapsed = time.time() - start_time
    
    return found_factor, candidates_tested, elapsed


def poisson_enhanced_gva_scan(N: int, search_radius: int = 1000, 
                              z_min: float = 2.0, top_k: int = 3) -> tuple:
    """
    Poisson-enhanced GVA factor search.
    
    Uses dual-domain periodicity detection to pre-filter candidates before
    performing expensive divisibility tests.
    
    Args:
        N: Semiprime to factor
        search_radius: Number of candidates for Poisson analysis
        z_min: Minimum z-score threshold for candidates
        top_k: Number of top peaks to always include
        
    Returns:
        (found_factor, candidates_tested, time_elapsed, poisson_candidates)
    """
    start_time = time.time()
    
    # Initialize Poisson duality framework
    poisson = PoissonSummationDuality(dims=7, precision_dps=50)
    
    # Define embedding function
    def embed_func(n: int) -> np.ndarray:
        return gva_torus_embedding(n, dims=7, k=0.04)
    
    # Detect arithmetic periodicities via Poisson duality
    periodicity_data = poisson.detect_arithmetic_periodicity(
        N, embed_func, num_samples=min(search_radius, 100)
    )
    
    # Get dual-domain factor candidates using z-score gate
    poisson_candidates = poisson.dual_domain_factor_heuristic(
        N, embed_func, z_min=z_min, top_k=top_k
    )
    
    # Note: With top_k guarantee, poisson_candidates should never be empty
    if not poisson_candidates:
        poisson_candidates = periodicity_data['peak_candidates']
    
    # Test Poisson-suggested candidates first
    found_factor = None
    candidates_tested = 0
    
    for candidate in poisson_candidates:
        candidates_tested += 1
        if N % candidate == 0:
            found_factor = candidate
            break
    
    # If not found in Poisson candidates, fall back to classical scan
    if found_factor is None:
        sqrt_n = int(np.sqrt(N))
        for candidate in range(max(2, sqrt_n - search_radius), 
                             sqrt_n + search_radius + 1):
            if candidate not in poisson_candidates:
                candidates_tested += 1
                if N % candidate == 0:
                    found_factor = candidate
                    break
    
    elapsed = time.time() - start_time
    
    return found_factor, candidates_tested, elapsed, poisson_candidates


def compare_methods(test_cases: list):
    """
    Compare classical GVA vs. Poisson-enhanced GVA on test semiprimes.
    
    Args:
        test_cases: List of (N, expected_factor_1, expected_factor_2) tuples
    """
    print("=" * 80)
    print("GVA-Poisson Integration Benchmark")
    print("=" * 80)
    print()
    
    results = []
    
    for N, p, q in test_cases:
        print(f"\nTest Case: N = {N} = {p} × {q}")
        print("-" * 80)
        
        # Classical GVA
        print("\nClassical GVA (baseline):")
        classical_factor, classical_tests, classical_time = classical_gva_factor_scan(
            N, search_radius=100
        )
        print(f"  Factor found: {classical_factor}")
        print(f"  Candidates tested: {classical_tests}")
        print(f"  Time: {classical_time:.4f}s")
        
        # Poisson-enhanced GVA with z-score gate
        print("\nPoisson-Enhanced GVA (z-score gate):")
        poisson_factor, poisson_tests, poisson_time, poisson_cands = \
            poisson_enhanced_gva_scan(N, search_radius=100, z_min=2.0, top_k=3)
        print(f"  Factor found: {poisson_factor}")
        print(f"  Poisson candidates suggested: {len(poisson_cands)}")
        print(f"  Candidates tested: {poisson_tests}")
        print(f"  Time: {poisson_time:.4f}s")
        
        # Analysis
        if classical_factor == poisson_factor:
            print("\n  ✓ Both methods found the same factor")
        
        if poisson_tests < classical_tests:
            reduction = (1 - poisson_tests / classical_tests) * 100
            print(f"  ✓ Poisson reduced candidates by {reduction:.1f}%")
        elif poisson_tests > classical_tests:
            increase = (poisson_tests / classical_tests - 1) * 100
            print(f"  ✗ Poisson increased candidates by {increase:.1f}% (overhead)")
        
        # Check if true factors were in Poisson candidates
        if p in poisson_cands or q in poisson_cands:
            print(f"  ✓ True factor detected in Poisson candidates!")
        
        results.append({
            'N': N,
            'classical_tests': classical_tests,
            'poisson_tests': poisson_tests,
            'classical_time': classical_time,
            'poisson_time': poisson_time,
            'poisson_candidates': len(poisson_cands),
            'factor_found': classical_factor == poisson_factor
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    
    avg_classical_tests = np.mean([r['classical_tests'] for r in results])
    avg_poisson_tests = np.mean([r['poisson_tests'] for r in results])
    avg_reduction = (1 - avg_poisson_tests / avg_classical_tests) * 100
    
    print(f"\nAverage candidates tested:")
    print(f"  Classical GVA: {avg_classical_tests:.0f}")
    print(f"  Poisson-Enhanced: {avg_poisson_tests:.0f}")
    print(f"  Average reduction: {avg_reduction:.1f}%")
    
    success_rate = sum(1 for r in results if r['factor_found']) / len(results) * 100
    print(f"\nFactor matching success rate: {success_rate:.0f}%")
    
    print("\nNote: Timing includes Poisson analysis overhead (~200ms).")
    print("      For larger search spaces, overhead amortizes with candidate reduction.")


def demo_periodicity_visualization(N: int):
    """
    Visualize duality ratio spectrum showing arithmetic periodicities.
    
    Args:
        N: Semiprime to analyze
    """
    print("\n" + "=" * 80)
    print(f"Duality Ratio Spectrum for N = {N}")
    print("=" * 80)
    
    poisson = PoissonSummationDuality(dims=7, precision_dps=50)
    
    def embed_func(n: int) -> np.ndarray:
        return gva_torus_embedding(n, dims=7, k=0.04)
    
    periodicity_data = poisson.detect_arithmetic_periodicity(
        N, embed_func, num_samples=20
    )
    
    print("\nCandidate  | Duality Ratio | Peak?")
    print("-" * 45)
    
    for i, (cand, ratio) in enumerate(zip(periodicity_data['candidates'],
                                          periodicity_data['duality_ratios'])):
        is_peak = "★" if i in periodicity_data['peak_indices'] else " "
        is_factor = "✓" if N % cand == 0 else " "
        print(f"{cand:8d}   | {ratio:12.6f}  | {is_peak}  {is_factor}")
    
    print("\nLegend: ★ = Peak detected, ✓ = True factor")
    print(f"\nMean ratio: {periodicity_data['mean_ratio']:.6f}")
    print(f"Std ratio:  {periodicity_data['std_ratio']:.6f}")
    print(f"Peaks found: {len(periodicity_data['peak_indices'])}")


def demo_calibration(test_cases: list):
    """
    Demonstrate calibration harness for tuning z_min and top_k parameters.
    
    Args:
        test_cases: List of (N, p, q) tuples for calibration
    """
    print("\n" + "=" * 80)
    print("Calibration Harness Demo")
    print("=" * 80)
    
    poisson = PoissonSummationDuality(dims=7, precision_dps=50)
    
    def embed_func(n: int) -> np.ndarray:
        return gva_torus_embedding(n, dims=7, k=0.04)
    
    # Run calibration
    calibration_results = poisson.calibrate_heuristic(
        test_cases,
        embed_func,
        z_min_range=np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0]),
        top_k_range=[1, 2, 3, 5]
    )
    
    # Show parameter sweep results
    print("\n" + "=" * 80)
    print("Parameter Sweep Results (Top 5 configurations)")
    print("=" * 80)
    
    # Sort by score
    param_stats = calibration_results['param_stats']
    sorted_params = sorted(param_stats.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
    
    print(f"\n{'z_min':>8} {'top_k':>8} {'Hit Rate':>12} {'Avg Candidates':>15} {'Score':>10}")
    print("-" * 65)
    for (z_min, top_k), stats in sorted_params:
        print(f"{z_min:8.2f} {top_k:8d} {stats['avg_hit_rate']:11.2%} {stats['avg_candidates']:15.1f} {stats['score']:10.4f}")
    
    print(f"\nRecommended: z_min={calibration_results['optimal_z_min']:.2f}, "
          f"top_k={calibration_results['optimal_top_k']}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GVA-Poisson Integration Example")
    print("Demonstrating Dual-Domain Factor Detection Enhancement")
    print("=" * 80)
    
    # Test cases: small semiprimes for demonstration
    test_cases = [
        (15, 3, 5),      # 3 × 5
        (21, 3, 7),      # 3 × 7
        (35, 5, 7),      # 5 × 7
        (77, 7, 11),     # 7 × 11
    ]
    
    # Compare classical vs. Poisson-enhanced GVA
    compare_methods(test_cases)
    
    # Visualize periodicity spectrum for one case
    demo_periodicity_visualization(21)
    
    # Run calibration demo
    demo_calibration(test_cases)
    
    print("\n" + "=" * 80)
    print("Integration Example Complete")
    print("=" * 80)
    print("\nKey Insights:")
    print("  1. Poisson duality exposes arithmetic periodicities in torus embeddings")
    print("  2. Z-score gate pre-filters candidates based on anomalous duality ratios")
    print("  3. Top-K guarantee ensures non-empty candidate lists")
    print("  4. Calibration harness enables data-driven parameter tuning")
    print("  5. Integration with GVA requires no changes to embedding function")
    print("\nFuture Enhancements:")
    print("  - Multi-scale Poisson analysis for robust detection")
    print("  - Adaptive z_min/top_k based on N magnitude")
    print("  - GPU acceleration for spatial/momentum transforms")
    print("  - Validation on cryptographic-scale RSA numbers")
    print("=" * 80)
