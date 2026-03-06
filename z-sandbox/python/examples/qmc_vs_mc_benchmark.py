#!/usr/bin/env python3
"""
Minimal Runnable: QMC vs MC Benchmark

Demonstrates variance reduction using Sobol+Owen scrambling vs Monte Carlo
for RSA factorization candidate generation. Includes bootstrap confidence intervals.

This is the minimal example from the issue description, integrated with
the existing QMC engines framework.
"""

import sys
import os
import numpy as np
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from qmc_engines import create_engine
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from python.qmc_engines import create_engine


def bootstrap_ci(data: np.ndarray, n_bootstrap: int = 1000, confidence: float = 0.95) -> tuple:
    """
    Compute bootstrap confidence interval for the mean.
    
    Args:
        data: Array of values
        n_bootstrap: Number of bootstrap samples
        confidence: Confidence level (default: 0.95)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    n = len(data)
    bootstrap_means = []
    
    rng = np.random.RandomState(42)
    for _ in range(n_bootstrap):
        sample = rng.choice(data, size=n, replace=True)
        bootstrap_means.append(np.mean(sample))
    
    alpha = 1 - confidence
    lower = np.percentile(bootstrap_means, 100 * alpha / 2)
    upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))
    
    return lower, upper


def benchmark_qmc_vs_mc(n: int, samples: int = 256, replicates: int = 16) -> Dict[str, Any]:
    """
    Benchmark QMC (Sobol+Owen) vs MC for RSA factorization candidates.
    
    Args:
        n: RSA modulus to factor
        samples: Number of samples per replicate
        replicates: Number of replicates for statistics
    
    Returns:
        Dictionary with benchmark results including means, CIs, and delta
    """
    mc_unique = []
    qmc_unique = []
    
    for i in range(replicates):
        seed = 42 + i
        
        # Monte Carlo baseline
        mc_engine = create_engine('mc', seed=seed)
        mc_candidates = mc_engine.generate_candidates(n, samples)
        mc_unique.append(len(mc_candidates))
        
        # QMC with Sobol+Owen scrambling
        qmc_engine = create_engine('sobol', seed=seed, scramble=True)
        qmc_candidates = qmc_engine.generate_candidates(n, samples)
        qmc_unique.append(len(qmc_candidates))
    
    # Convert to numpy arrays
    mc_unique = np.array(mc_unique)
    qmc_unique = np.array(qmc_unique)
    
    # Compute statistics
    mc_mean = np.mean(mc_unique)
    qmc_mean = np.mean(qmc_unique)
    delta = (qmc_mean - mc_mean) / mc_mean * 100
    
    # Bootstrap CIs
    mc_ci_lower, mc_ci_upper = bootstrap_ci(mc_unique)
    qmc_ci_lower, qmc_ci_upper = bootstrap_ci(qmc_unique)
    
    return {
        'mc_mean': mc_mean,
        'mc_ci': (mc_ci_lower, mc_ci_upper),
        'qmc_mean': qmc_mean,
        'qmc_ci': (qmc_ci_lower, qmc_ci_upper),
        'delta_pct': delta
    }


def main():
    print("=" * 60)
    print("Minimal QMC vs MC Benchmark")
    print("=" * 60)
    print()
    
    # Use a more manageable test case
    # 899 = 29 × 31 (balanced semiprime for demonstration)
    N = 899
    
    print(f"Test Case: N = {N} (29 × 31)")
    print(f"√N ≈ {int(N**0.5)}")
    print()
    
    # Run benchmark with power-of-2 samples for optimal Sobol properties
    print("Running benchmark with 100 replicates, 256 samples each...")
    result = benchmark_qmc_vs_mc(N, samples=256, replicates=100)
    
    # Display results
    print()
    print("Results:")
    print("-" * 60)
    print(f"MC Mean Unique Candidates:  {result['mc_mean']:.1f}")
    print(f"  95% CI: [{result['mc_ci'][0]:.1f}, {result['mc_ci'][1]:.1f}]")
    print()
    print(f"QMC Mean Unique Candidates: {result['qmc_mean']:.1f}")
    print(f"  95% CI: [{result['qmc_ci'][0]:.1f}, {result['qmc_ci'][1]:.1f}]")
    print()
    print(f"Improvement: {result['delta_pct']:+.2f}%")
    print()
    
    # Interpretation
    print("=" * 60)
    print("Interpretation:")
    print("-" * 60)
    if result['delta_pct'] > 0:
        print(f"✓ QMC (Sobol+Owen) generates {result['delta_pct']:.1f}% more unique")
        print("  candidates than standard Monte Carlo.")
        print()
        print("  This demonstrates variance reduction through low-discrepancy")
        print("  sequences, leading to better coverage of the search space.")
    else:
        print(f"✗ QMC did not show improvement ({result['delta_pct']:.1f}%)")
        print("  Note: Results may vary based on N's structure and sample size.")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    result = main()
