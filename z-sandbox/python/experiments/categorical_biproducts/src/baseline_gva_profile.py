#!/usr/bin/env python3
"""
Baseline GVA Performance Profiler

Measures current GVA method performance on small semiprimes to establish
baseline metrics for comparison with categorical biproduct enhancement.

Mission Charter Compliance: See EXPERIMENT_REPORT.md for full charter elements.
"""

import sys
import os
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

# Add python/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "python"))

try:
    from mpmath import mp, mpf, sqrt, log, exp, power, frac
except ImportError:
    print("Error: mpmath not installed. Install with: pip install mpmath")
    sys.exit(1)

# High precision
mp.dps = 150

# Golden ratio
PHI = mpf((1 + sqrt(5)) / 2)


def embed_torus_baseline(n: int, dims: int = 5, k: float = 0.3) -> List[float]:
    """
    Baseline GVA torus embedding (monolithic).
    
    Args:
        n: Integer to embed
        dims: Number of torus dimensions
        k: Geometric resolution parameter
        
    Returns:
        List of d coordinates in [0, 1)
    """
    c = exp(2)  # e²
    x = mpf(n) / c
    coords = []
    
    for _ in range(dims):
        # θ'(x, k) = φ * ((x mod φ) / φ)^k
        x_mod = x % PHI
        x = PHI * power(x_mod / PHI, k)
        coords.append(float(frac(x)))
    
    return coords


def riemannian_distance_baseline(
    coords1: List[float], 
    coords2: List[float], 
    N: int
) -> float:
    """
    Baseline Riemannian distance with curvature κ(n).
    
    Args:
        coords1: First torus point
        coords2: Second torus point
        N: Modulus for curvature calculation
        
    Returns:
        Riemannian distance
    """
    # Discrete curvature: κ(n) = d(n) * ln(n+1) / e²
    # For simplicity, use κ(n) = 4 * ln(n+1) / e² (d(n) ≈ 4 typical)
    kappa = float(4 * log(mpf(N) + 1) / exp(2))
    
    total = 0.0
    for c1, c2 in zip(coords1, coords2):
        # Wraparound distance on torus
        d = min(abs(c1 - c2), 1.0 - abs(c1 - c2))
        # Riemannian metric: (d * (1 + κ*d))²
        total += (d * (1 + kappa * d)) ** 2
    
    return math.sqrt(total)


def per_dimension_variance(coords_list: List[List[float]]) -> List[float]:
    """
    Compute variance in each dimension.
    
    Args:
        coords_list: List of coordinate vectors
        
    Returns:
        List of per-dimension variances
    """
    coords_array = np.array(coords_list)
    return np.var(coords_array, axis=0).tolist()


def profile_gva_baseline(
    N: int,
    p_true: int,
    q_true: int,
    radius: int = 1000,
    dims: int = 5,
    k: float = 0.3,
    n_samples: int = 100
) -> Dict:
    """
    Profile baseline GVA on a known semiprime.
    
    Args:
        N: Semiprime to factor (N = p * q)
        p_true: True prime factor p
        q_true: True prime factor q
        radius: Search radius around sqrt(N)
        dims: Torus dimensions
        k: Geometric resolution parameter
        n_samples: Number of candidates to sample
        
    Returns:
        Dictionary of profiling metrics
    """
    sqrt_n = int(math.isqrt(N))
    
    # Embed true factors
    t_start_embed = time.perf_counter()
    p_coords = embed_torus_baseline(p_true, dims, k)
    q_coords = embed_torus_baseline(q_true, dims, k)
    t_embed_single = (time.perf_counter() - t_start_embed) / 2
    
    # Sample candidates around sqrt(N)
    np.random.seed(42)  # Reproducibility
    candidates = np.random.randint(
        max(2, sqrt_n - radius),
        sqrt_n + radius,
        size=n_samples
    )
    
    # Embed all candidates and measure time
    t_start_batch = time.perf_counter()
    candidate_coords = [embed_torus_baseline(int(c), dims, k) for c in candidates]
    t_embed_batch = time.perf_counter() - t_start_batch
    
    # Compute distances to true factors
    t_start_dist = time.perf_counter()
    distances_to_p = [
        riemannian_distance_baseline(c, p_coords, N) 
        for c in candidate_coords
    ]
    distances_to_q = [
        riemannian_distance_baseline(c, q_coords, N) 
        for c in candidate_coords
    ]
    t_distance_batch = time.perf_counter() - t_start_dist
    
    # Variance analysis
    variance_per_dim = per_dimension_variance(candidate_coords)
    total_variance = sum(variance_per_dim)
    
    # Find nearest candidates to true factors
    idx_nearest_p = int(np.argmin(distances_to_p))
    idx_nearest_q = int(np.argmin(distances_to_q))
    
    min_dist_p = distances_to_p[idx_nearest_p]
    min_dist_q = distances_to_q[idx_nearest_q]
    
    nearest_to_p = int(candidates[idx_nearest_p])
    nearest_to_q = int(candidates[idx_nearest_q])
    
    # Check if we found factors (within sample)
    found_p = (p_true in candidates)
    found_q = (q_true in candidates)
    
    return {
        "modulus": N,
        "p_true": p_true,
        "q_true": q_true,
        "sqrt_n": sqrt_n,
        "radius": radius,
        "dimensions": dims,
        "k_parameter": k,
        "n_samples": n_samples,
        "timing": {
            "embed_single_sec": t_embed_single,
            "embed_batch_sec": t_embed_batch,
            "embed_per_candidate_sec": t_embed_batch / n_samples,
            "distance_batch_sec": t_distance_batch,
            "distance_per_candidate_sec": t_distance_batch / n_samples,
            "total_sec": t_embed_batch + t_distance_batch
        },
        "variance": {
            "per_dimension": variance_per_dim,
            "total": total_variance,
            "mean": total_variance / dims,
            "max_dim": int(np.argmax(variance_per_dim)),
            "min_dim": int(np.argmin(variance_per_dim)),
            "dimension_ratio": max(variance_per_dim) / (min(variance_per_dim) + 1e-12)
        },
        "distances": {
            "min_to_p": min_dist_p,
            "min_to_q": min_dist_q,
            "nearest_candidate_to_p": nearest_to_p,
            "nearest_candidate_to_q": nearest_to_q,
            "p_error": abs(nearest_to_p - p_true),
            "q_error": abs(nearest_to_q - q_true),
            "mean_dist_to_p": float(np.mean(distances_to_p)),
            "std_dist_to_p": float(np.std(distances_to_p)),
            "mean_dist_to_q": float(np.mean(distances_to_q)),
            "std_dist_to_q": float(np.std(distances_to_q))
        },
        "found_factors": {
            "p_in_sample": found_p,
            "q_in_sample": found_q
        }
    }


def generate_test_semiprimes() -> List[Tuple[int, int, int]]:
    """
    Generate test semiprimes for profiling.
    
    Returns:
        List of (N, p, q) tuples
    """
    test_cases = [
        # 64-bit balanced semiprimes (from test suite)
        (15347627614375828701, 3919199423, 3916429453),
        (18446736050711510819, 4294948663, 4294941307),
        
        # 80-bit (smaller for faster testing)
        (1208907267445695453279, 34778071079, 34756162171),
        
        # 96-bit
        (79226642649640146386194717763, 281419970353, 281530802053),
    ]
    return test_cases


def main():
    """Run baseline GVA profiling on test semiprimes."""
    print("=" * 80)
    print("Baseline GVA Performance Profiler")
    print("=" * 80)
    print()
    
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    test_cases = generate_test_semiprimes()
    all_results = []
    
    for i, (N, p, q) in enumerate(test_cases):
        bit_length = N.bit_length()
        print(f"Test Case {i+1}: {bit_length}-bit semiprime")
        print(f"  N = {N}")
        print(f"  p = {p}")
        print(f"  q = {q}")
        print()
        
        # Profile with multiple dimension counts
        for dims in [5, 7]:
            print(f"  Profiling with dims={dims}...")
            
            result = profile_gva_baseline(
                N=N,
                p_true=p,
                q_true=q,
                radius=10000,
                dims=dims,
                k=0.3,
                n_samples=1000
            )
            result["test_case"] = i + 1
            result["bit_length"] = bit_length
            all_results.append(result)
            
            # Print summary
            print(f"    Embedding: {result['timing']['embed_per_candidate_sec']*1e6:.2f} µs/candidate")
            print(f"    Distance:  {result['timing']['distance_per_candidate_sec']*1e6:.2f} µs/candidate")
            print(f"    Variance:  Total={result['variance']['total']:.6f}, Ratio={result['variance']['dimension_ratio']:.2f}")
            print(f"    Min dist to p: {result['distances']['min_to_p']:.6f}")
            print(f"    Min dist to q: {result['distances']['min_to_q']:.6f}")
            print()
    
    # Save results
    output_file = results_dir / "baseline_profile.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    print()
    
    # Summary statistics
    print("=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    
    for dims in [5, 7]:
        dims_results = [r for r in all_results if r['dimensions'] == dims]
        if not dims_results:
            continue
            
        embed_times = [r['timing']['embed_per_candidate_sec'] * 1e6 for r in dims_results]
        dist_times = [r['timing']['distance_per_candidate_sec'] * 1e6 for r in dims_results]
        variances = [r['variance']['total'] for r in dims_results]
        var_ratios = [r['variance']['dimension_ratio'] for r in dims_results]
        
        print(f"\nDimensions: {dims}")
        print(f"  Embed time:  {np.mean(embed_times):.2f} ± {np.std(embed_times):.2f} µs")
        print(f"  Dist time:   {np.mean(dist_times):.2f} ± {np.std(dist_times):.2f} µs")
        print(f"  Variance:    {np.mean(variances):.6f} ± {np.std(variances):.6f}")
        print(f"  Var ratio:   {np.mean(var_ratios):.2f} ± {np.std(var_ratios):.2f}")
    
    print()
    print("Baseline profiling complete.")


if __name__ == "__main__":
    main()
