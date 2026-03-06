#!/usr/bin/env python3
"""
QMC Directions Demo - Rank-1 Lattice (Korobov/Fibonacci) for RSA-129

Demonstrates variance reduction using rank-1 lattice methods
(Korobov and Fibonacci generators) for distant-factor RSA semiprimes.

Usage:
    python qmc_directions_demo.py --n RSA-129 --replicates 1000 \\
        --engine rank1_korobov --output results_rsa129.json
"""

import argparse
import json
import math
import sys
import os
import time
from typing import Dict, Any, List
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from qmc_engines import create_engine
    from utils.z_framework import kappa, theta_prime
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from python.qmc_engines import create_engine
    from utils.z_framework import kappa, theta_prime


# RSA Challenge Numbers
RSA_CHALLENGES = {
    'RSA-100': 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654003799028144175876873365407865011234642762212276573866800211641966377,
    'RSA-129': 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989498159834210580143501940323646295439459,
    'RSA-155': 1094173864157052742180970732204035761200373294544920599091384213147634998428416754336308285688651323320627738013707,
    'RSA-576': 188198812920607963838697239461650439807163563379417382700763356422988859715234665485319060606504743045317388011303396716199692321205734031879550656996221305168759307650257059,
}


def run_replicate(
    N: int,
    engine_type: str,
    n_samples: int,
    seed: int,
    lattice_type: str = 'korobov'
) -> Dict[str, Any]:
    """
    Run a single replicate with specified engine.
    
    Args:
        N: RSA modulus
        engine_type: 'rank1' or 'mc'
        n_samples: Number of samples
        seed: Random seed
        lattice_type: 'korobov' or 'fibonacci'
    
    Returns:
        Metrics dictionary
    """
    start_time = time.time()
    
    # Create engine
    if engine_type == 'rank1':
        engine = create_engine('rank1', dimension=1, seed=seed, lattice_type=lattice_type)
    else:
        engine = create_engine('mc', dimension=1, seed=seed)
    
    # Generate candidates
    candidates = engine.generate_candidates(N, n_samples, bias=None)
    generation_time = time.time() - start_time
    
    # Calculate metrics
    sqrt_N = math.sqrt(N)
    distances = np.abs(candidates - sqrt_N)
    
    metrics = {
        'seed': seed,
        'unique_count': len(candidates),
        'mean_distance': float(np.mean(distances)),
        'std_distance': float(np.std(distances)),
        'min_distance': float(np.min(distances)),
        'max_distance': float(np.max(distances)),
        'generation_time': generation_time,
    }
    
    return metrics


def run_benchmark(
    N: int,
    engine_type: str,
    n_samples: int,
    n_replicates: int,
    lattice_type: str = 'korobov',
    base_seed: int = 42
) -> Dict[str, Any]:
    """
    Run benchmark with multiple replicates.
    
    Args:
        N: RSA modulus
        engine_type: 'rank1' or 'mc'
        n_samples: Number of samples per replicate
        n_replicates: Number of replicates
        lattice_type: 'korobov' or 'fibonacci'
        base_seed: Base random seed
    
    Returns:
        Benchmark results
    """
    print(f"Running {n_replicates} replicates with {engine_type} engine...")
    
    replicates = []
    for i in range(n_replicates):
        seed = base_seed + i
        metrics = run_replicate(N, engine_type, n_samples, seed, lattice_type)
        replicates.append(metrics)
        
        if (i + 1) % max(1, n_replicates // 10) == 0:
            print(f"  Progress: {i+1}/{n_replicates}")
    
    # Aggregate statistics
    unique_counts = [r['unique_count'] for r in replicates]
    mean_distances = [r['mean_distance'] for r in replicates]
    
    results = {
        'engine': engine_type,
        'lattice_type': lattice_type if engine_type == 'rank1' else None,
        'n_samples': n_samples,
        'n_replicates': n_replicates,
        'mean_unique_count': float(np.mean(unique_counts)),
        'std_unique_count': float(np.std(unique_counts)),
        'mean_distance': float(np.mean(mean_distances)),
        'std_distance': float(np.std(mean_distances)),
        'replicates': replicates
    }
    
    return results


def compute_bootstrap_ci(data: List[float], confidence: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, float]:
    """
    Compute bootstrap confidence interval.
    
    Args:
        data: List of values
        confidence: Confidence level (default: 0.95)
        n_bootstrap: Number of bootstrap samples
    
    Returns:
        Dictionary with mean and CI bounds
    """
    data_array = np.array(data)
    n = len(data_array)
    
    # Bootstrap resampling
    bootstrap_means = []
    rng = np.random.RandomState(42)
    for _ in range(n_bootstrap):
        sample = rng.choice(data_array, size=n, replace=True)
        bootstrap_means.append(np.mean(sample))
    
    # Compute percentiles
    alpha = 1 - confidence
    lower = np.percentile(bootstrap_means, 100 * alpha / 2)
    upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))
    
    return {
        'mean': float(np.mean(data_array)),
        'ci_lower': float(lower),
        'ci_upper': float(upper),
        'confidence': confidence
    }


def compare_engines(
    N: int,
    n_samples: int,
    n_replicates: int,
    lattice_type: str = 'korobov',
    base_seed: int = 42
) -> Dict[str, Any]:
    """
    Compare MC vs Rank-1 Lattice engines.
    
    Args:
        N: RSA modulus
        n_samples: Number of samples
        n_replicates: Number of replicates
        lattice_type: 'korobov' or 'fibonacci'
        base_seed: Base random seed
    
    Returns:
        Comparison results
    """
    print("=" * 60)
    print("QMC Directions Comparison: MC vs Rank-1 Lattice")
    print("=" * 60)
    print(f"N: {N}")
    print(f"Samples: {n_samples}")
    print(f"Replicates: {n_replicates}")
    print(f"Lattice type: {lattice_type}")
    print()
    
    # Run MC baseline
    print("Running Monte Carlo baseline...")
    mc_results = run_benchmark(N, 'mc', n_samples, n_replicates, base_seed=base_seed)
    print()
    
    # Run Rank-1 Lattice
    print(f"Running Rank-1 Lattice ({lattice_type})...")
    rank1_results = run_benchmark(N, 'rank1', n_samples, n_replicates, lattice_type, base_seed)
    print()
    
    # Compute bootstrap CIs
    mc_unique_counts = [r['unique_count'] for r in mc_results['replicates']]
    rank1_unique_counts = [r['unique_count'] for r in rank1_results['replicates']]
    
    mc_ci = compute_bootstrap_ci(mc_unique_counts)
    rank1_ci = compute_bootstrap_ci(rank1_unique_counts)
    
    # Compute deltas
    delta_unique = (rank1_ci['mean'] - mc_ci['mean']) / mc_ci['mean'] * 100
    
    # Compile comparison
    comparison = {
        'N': str(N),
        'samples': n_samples,
        'replicates': n_replicates,
        'mc': {
            'mean_unique': mc_ci['mean'],
            'ci': [mc_ci['ci_lower'], mc_ci['ci_upper']],
            'mean_distance': mc_results['mean_distance']
        },
        'rank1': {
            'engine': lattice_type,
            'mean_unique': rank1_ci['mean'],
            'ci': [rank1_ci['ci_lower'], rank1_ci['ci_upper']],
            'mean_distance': rank1_results['mean_distance']
        },
        'delta_pct': delta_unique,
        'mc_results': mc_results,
        'rank1_results': rank1_results
    }
    
    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"MC Mean Unique: {mc_ci['mean']:.1f} [CI: {mc_ci['ci_lower']:.1f}, {mc_ci['ci_upper']:.1f}]")
    print(f"Rank-1 Mean Unique: {rank1_ci['mean']:.1f} [CI: {rank1_ci['ci_lower']:.1f}, {rank1_ci['ci_upper']:.1f}]")
    print(f"Δ%: {delta_unique:+.2f}%")
    print(f"MC Mean Distance: {mc_results['mean_distance']:.2e}")
    print(f"Rank-1 Mean Distance: {rank1_results['mean_distance']:.2e}")
    print("=" * 60)
    
    return comparison


def main():
    parser = argparse.ArgumentParser(
        description='QMC Directions Demo - Rank-1 Lattice for RSA Factorization'
    )
    
    parser.add_argument('--n', type=str, default='RSA-129',
                       help='RSA challenge name or custom integer')
    parser.add_argument('--replicates', type=int, default=100,
                       help='Number of replicates (default: 100)')
    parser.add_argument('--engine', type=str, default='rank1_korobov',
                       choices=['rank1_korobov', 'rank1_fibonacci', 'both'],
                       help='Engine type (default: rank1_korobov)')
    parser.add_argument('--samples', type=int, default=256,
                       help='Number of samples per replicate (default: 256)')
    parser.add_argument('--output', type=str, default='results_qmc_directions.json',
                       help='Output JSON file (default: results_qmc_directions.json)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Base random seed (default: 42)')
    
    args = parser.parse_args()
    
    # Parse N
    if args.n in RSA_CHALLENGES:
        N = RSA_CHALLENGES[args.n]
        print(f"Using RSA challenge: {args.n}")
    else:
        try:
            N = int(args.n)
            print(f"Using custom N: {N}")
        except ValueError:
            print(f"Error: Invalid N value: {args.n}", file=sys.stderr)
            sys.exit(1)
    
    # Determine lattice type
    if args.engine == 'rank1_korobov':
        lattice_type = 'korobov'
    elif args.engine == 'rank1_fibonacci':
        lattice_type = 'fibonacci'
    else:
        lattice_type = 'korobov'  # Default for 'both'
    
    # Run comparison
    results = compare_engines(
        N=N,
        n_samples=args.samples,
        n_replicates=args.replicates,
        lattice_type=lattice_type,
        base_seed=args.seed
    )
    
    # Save to JSON
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
