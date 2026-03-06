#!/usr/bin/env python3
"""
Discrepancy Test for QMC Sequences

Validates low-discrepancy property of Sobol+Owen sequences and compares
with MC baseline. Uses star discrepancy (D*) as quality metric.

Mathematical Definition:
- Star discrepancy: D*(P) = sup |empirical - uniform|
- Lower is better; Sobol should achieve O(log^d N / N)
- MC achieves O(1/√N) with high probability
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import numpy as np
from pathlib import Path
from typing import Tuple
import json

from python.qmc_engines import create_engine


def compute_star_discrepancy_1d(points: np.ndarray) -> float:
    """
    Compute star discrepancy for 1D point set.
    
    D*(P) = max_{t∈[0,1]} |#{p ≤ t}/N - t|
    
    Args:
        points: Array of points in [0, 1]
        
    Returns:
        Star discrepancy value
    """
    points = np.sort(points)
    n = len(points)
    
    # Compute empirical CDF differences
    discrepancies = []
    for i, p in enumerate(points):
        empirical = (i + 1) / n
        uniform = p
        discrepancies.append(abs(empirical - uniform))
    
    # Also check at 0
    if len(points) > 0:
        discrepancies.append(points[0])
    
    # And at 1
    if len(points) > 0:
        discrepancies.append(abs(1.0 - points[-1]))
    
    return max(discrepancies)


def koksma_hlawka_bound(discrepancy: float, variation: float) -> float:
    """
    Koksma-Hlawka bound for integration error.
    
    Error ≤ V(f) * D*(P) where:
    - V(f) is variation of integrand
    - D*(P) is star discrepancy
    
    Args:
        discrepancy: Star discrepancy of point set
        variation: Variation of function
        
    Returns:
        Error bound
    """
    return variation * discrepancy


def run_discrepancy_comparison(
    n_samples: int = 10000,
    n_replicates: int = 100,
    seed: int = 42,
    output_dir: Path = None
) -> dict:
    """
    Compare discrepancy of MC vs Sobol sequences.
    
    Args:
        n_samples: Number of samples per sequence
        n_replicates: Number of replicates
        seed: Random seed
        output_dir: Optional output directory
        
    Returns:
        Dictionary with discrepancy statistics
    """
    print("Discrepancy Comparison: MC vs Sobol+Owen")
    print("=" * 70)
    print(f"  Samples per sequence: {n_samples}")
    print(f"  Replicates: {n_replicates}")
    print()
    
    mc_discrepancies = []
    sobol_discrepancies = []
    
    for rep in range(n_replicates):
        # MC sequence
        mc_engine = create_engine('mc', dimension=1, seed=seed + rep)
        mc_points = mc_engine.generate(n_samples)[:, 0]
        mc_disc = compute_star_discrepancy_1d(mc_points)
        mc_discrepancies.append(mc_disc)
        
        # Sobol+Owen sequence
        sobol_engine = create_engine('sobol', dimension=1, seed=seed + rep, scramble=True)
        sobol_points = sobol_engine.generate(n_samples)[:, 0]
        sobol_disc = compute_star_discrepancy_1d(sobol_points)
        sobol_discrepancies.append(sobol_disc)
    
    mc_discrepancies = np.array(mc_discrepancies)
    sobol_discrepancies = np.array(sobol_discrepancies)
    
    # Compute statistics
    results = {
        'n_samples': n_samples,
        'n_replicates': n_replicates,
        'mc': {
            'mean': float(mc_discrepancies.mean()),
            'std': float(mc_discrepancies.std()),
            'min': float(mc_discrepancies.min()),
            'max': float(mc_discrepancies.max()),
            'theoretical_bound': 1.0 / np.sqrt(n_samples)  # O(1/√N)
        },
        'sobol': {
            'mean': float(sobol_discrepancies.mean()),
            'std': float(sobol_discrepancies.std()),
            'min': float(sobol_discrepancies.min()),
            'max': float(sobol_discrepancies.max()),
            'theoretical_bound': np.log(n_samples) / n_samples  # O(log N / N)
        },
        'ratio': float(sobol_discrepancies.mean() / mc_discrepancies.mean())
    }
    
    # Print results
    print("MC Discrepancy:")
    print(f"  Mean: {results['mc']['mean']:.6f}")
    print(f"  Std:  {results['mc']['std']:.6f}")
    print(f"  Theoretical O(1/√N): {results['mc']['theoretical_bound']:.6f}")
    print()
    
    print("Sobol+Owen Discrepancy:")
    print(f"  Mean: {results['sobol']['mean']:.6f}")
    print(f"  Std:  {results['sobol']['std']:.6f}")
    print(f"  Theoretical O(log N / N): {results['sobol']['theoretical_bound']:.6f}")
    print()
    
    print(f"Sobol/MC ratio: {results['ratio']:.4f}")
    print(f"Sobol improvement: {(1 - results['ratio']) * 100:.1f}%")
    
    # Save results
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "discrepancy_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved results to {output_dir / 'discrepancy_results.json'}")
    
    return results


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "results"
    
    # Run comparison
    results = run_discrepancy_comparison(
        n_samples=10000,
        n_replicates=100,
        seed=42,
        output_dir=output_dir
    )
    
    print("\n" + "=" * 70)
    print("Discrepancy test complete.")
