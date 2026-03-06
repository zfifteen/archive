#!/usr/bin/env python3
"""
Benchmark Elliptic - Distant Factor Testing for Large-Scale RSA

Tests QMC methods on distant-factor RSA semiprimes with focus on:
- L2 discrepancy measurement
- Adaptive sampling strategies
- Hit rate visualization for distant factors

Usage:
    python benchmark_elliptic.py --n RSA-155 --samples 5000 \\
        --adaptive True --output plots/rsa155_discrepancy.png
"""

import argparse
import json
import math
import sys
import os
import time
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from python.qmc_engines import create_engine
    from utils.z_framework import kappa, theta_prime
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from python.qmc_engines import create_engine
    from utils.z_framework import kappa, theta_prime


# RSA Challenge Numbers
RSA_CHALLENGES = {
    'RSA-100': 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654003799028144175876873365407865011234642762212276573866800211641966377,
    'RSA-129': 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989498159834210580143501940323646295439459,
    'RSA-155': 1094173864157052742180970732204035761200373294544920599091384213147634998428416754336308285688651323320627738013707,
    'RSA-576': 188198812920607963838697239461650439807163563379417382700763356422988859715234665485319060606504743045317388011303396716199692321205734031879550656996221305168759307650257059,
}


def compute_l2_discrepancy(samples: np.ndarray, N: int) -> float:
    """
    Compute L2 star discrepancy for samples relative to √N.
    
    The L2 discrepancy measures how uniformly distributed the samples
    are compared to a uniform distribution around √N.
    
    Args:
        samples: Array of candidate values
        N: RSA modulus
    
    Returns:
        L2 discrepancy value (lower is better)
    """
    sqrt_N = math.sqrt(N)
    n = len(samples)
    
    # Normalize samples to [0, 1]
    # Use adaptive range based on bit length
    bit_length = N.bit_length()
    if bit_length <= 64:
        spread = 0.15
    elif bit_length <= 128:
        spread = 0.10
    else:
        spread = 0.05
    
    lower_bound = sqrt_N * (1 - spread)
    upper_bound = sqrt_N * (1 + spread)
    
    # Normalize to [0, 1]
    normalized = (samples - lower_bound) / (upper_bound - lower_bound)
    normalized = np.clip(normalized, 0, 1)
    
    # Compute empirical CDF
    sorted_samples = np.sort(normalized)
    
    # L2 discrepancy calculation
    # D_n^2 = sum of squared differences between empirical and uniform CDF
    discrepancy_sum = 0.0
    for i, x in enumerate(sorted_samples):
        empirical_cdf = (i + 1) / n
        uniform_cdf = x
        discrepancy_sum += (empirical_cdf - uniform_cdf) ** 2
    
    l2_discrepancy = math.sqrt(discrepancy_sum / n)
    
    return l2_discrepancy


def adaptive_sampling(
    engine: Any,
    N: int,
    initial_samples: int,
    max_samples: int,
    target_discrepancy: float = 0.1
) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """
    Adaptive sampling strategy that adjusts sample count based on discrepancy.
    
    Args:
        engine: QMC engine
        N: RSA modulus
        initial_samples: Initial number of samples
        max_samples: Maximum samples to generate
        target_discrepancy: Target L2 discrepancy threshold
    
    Returns:
        Tuple of (final candidates, adaptation history)
    """
    history = []
    current_samples = initial_samples
    all_candidates = np.array([], dtype=int)
    
    while current_samples <= max_samples:
        # Generate candidates
        candidates = engine.generate_candidates(N, current_samples, bias=None)
        all_candidates = np.unique(np.concatenate([all_candidates, candidates]))
        
        # Compute discrepancy
        discrepancy = compute_l2_discrepancy(all_candidates, N)
        
        history.append({
            'iteration': len(history),
            'total_samples': len(all_candidates),
            'discrepancy': discrepancy
        })
        
        # Check if target reached
        if discrepancy <= target_discrepancy:
            print(f"  Target discrepancy {target_discrepancy} reached at {len(all_candidates)} samples")
            break
        
        # Increase sample count
        current_samples = int(current_samples * 1.5)
        if current_samples > max_samples:
            break
    
    return all_candidates, history


def benchmark_engines(
    N: int,
    n_samples: int,
    adaptive: bool = False,
    max_samples: int = 10000
) -> Dict[str, Any]:
    """
    Benchmark multiple QMC engines on distant-factor RSA.
    
    Args:
        N: RSA modulus
        n_samples: Initial number of samples
        adaptive: Whether to use adaptive sampling
        max_samples: Maximum samples for adaptive mode
    
    Returns:
        Benchmark results
    """
    print("=" * 60)
    print("Elliptic Benchmark - Distant Factor Testing")
    print("=" * 60)
    print(f"N: {N}")
    print(f"√N: {math.sqrt(N):.6e}")
    print(f"Bit length: {N.bit_length()}")
    print(f"Initial samples: {n_samples}")
    print(f"Adaptive: {adaptive}")
    print()
    
    engines = {
        'MC': create_engine('mc', seed=42),
        'Sobol+Owen': create_engine('sobol', seed=42, scramble=True),
        'Rank-1 Korobov': create_engine('rank1', seed=42, lattice_type='korobov'),
        'Rank-1 Fibonacci': create_engine('rank1', seed=42, lattice_type='fibonacci')
    }
    
    results = {}
    
    for name, engine in engines.items():
        print(f"Testing {name}...")
        start_time = time.time()
        
        if adaptive:
            candidates, history = adaptive_sampling(
                engine, N, n_samples, max_samples
            )
            final_discrepancy = history[-1]['discrepancy']
            adaptation_steps = len(history)
        else:
            candidates = engine.generate_candidates(N, n_samples, bias=None)
            final_discrepancy = compute_l2_discrepancy(candidates, N)
            history = None
            adaptation_steps = 1
        
        elapsed_time = time.time() - start_time
        
        # Compute statistics
        sqrt_N = math.sqrt(N)
        distances = np.abs(candidates - sqrt_N)
        
        results[name] = {
            'unique_count': len(candidates),
            'discrepancy': final_discrepancy,
            'mean_distance': float(np.mean(distances)),
            'std_distance': float(np.std(distances)),
            'min_distance': float(np.min(distances)),
            'time_seconds': elapsed_time,
            'adaptation_steps': adaptation_steps,
            'history': history
        }
        
        print(f"  Unique candidates: {len(candidates)}")
        print(f"  L2 discrepancy: {final_discrepancy:.6f}")
        print(f"  Mean distance from √N: {np.mean(distances):.6e}")
        print(f"  Time: {elapsed_time:.3f}s")
        print()
    
    return results


def generate_report(results: Dict[str, Any], N: int) -> str:
    """
    Generate text report of benchmark results.
    
    Args:
        results: Benchmark results
        N: RSA modulus
    
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 60)
    report.append("ELLIPTIC BENCHMARK REPORT")
    report.append("=" * 60)
    report.append(f"N: {N}")
    report.append(f"Bit length: {N.bit_length()}")
    report.append("")
    
    # Sort by discrepancy (lower is better)
    sorted_engines = sorted(results.items(), key=lambda x: x[1]['discrepancy'])
    
    report.append("Results (sorted by L2 discrepancy):")
    report.append("-" * 60)
    
    for name, metrics in sorted_engines:
        report.append(f"\n{name}:")
        report.append(f"  Unique candidates: {metrics['unique_count']}")
        report.append(f"  L2 discrepancy: {metrics['discrepancy']:.6f}")
        report.append(f"  Mean distance: {metrics['mean_distance']:.6e}")
        report.append(f"  Time: {metrics['time_seconds']:.3f}s")
        if metrics.get('adaptation_steps', 1) > 1:
            report.append(f"  Adaptation steps: {metrics['adaptation_steps']}")
    
    report.append("")
    report.append("=" * 60)
    
    # Comparison with baseline (MC)
    if 'MC' in results:
        mc_disc = results['MC']['discrepancy']
        report.append("\nImprovement over MC baseline:")
        report.append("-" * 60)
        for name, metrics in results.items():
            if name != 'MC':
                improvement = (mc_disc - metrics['discrepancy']) / mc_disc * 100
                report.append(f"  {name}: {improvement:+.2f}%")
    
    report.append("=" * 60)
    
    return "\n".join(report)


def save_plot(results: Dict[str, Any], output_file: str, N: int):
    """
    Save discrepancy plot to file.
    
    Args:
        results: Benchmark results
        output_file: Output file path
        N: RSA modulus
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not available, skipping plot generation")
        return
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Discrepancy comparison
    engines = list(results.keys())
    discrepancies = [results[e]['discrepancy'] for e in engines]
    
    ax1.bar(engines, discrepancies, color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12'])
    ax1.set_ylabel('L2 Discrepancy')
    ax1.set_title(f'L2 Discrepancy Comparison\n(N bit length: {N.bit_length()})')
    ax1.tick_params(axis='x', rotation=15)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Unique candidates
    unique_counts = [results[e]['unique_count'] for e in engines]
    
    ax2.bar(engines, unique_counts, color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12'])
    ax2.set_ylabel('Unique Candidates')
    ax2.set_title('Unique Candidate Count Comparison')
    ax2.tick_params(axis='x', rotation=15)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Ensure directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description='Benchmark Elliptic - Distant Factor Testing for RSA'
    )
    
    parser.add_argument('--n', type=str, default='RSA-155',
                       help='RSA challenge name or custom integer')
    parser.add_argument('--samples', type=int, default=1000,
                       help='Number of samples (default: 1000)')
    parser.add_argument('--adaptive', type=str, default='False',
                       choices=['True', 'False'],
                       help='Use adaptive sampling (default: False)')
    parser.add_argument('--max-samples', type=int, default=10000,
                       help='Max samples for adaptive mode (default: 10000)')
    parser.add_argument('--output', type=str, default='plots/elliptic_benchmark.png',
                       help='Output plot file (default: plots/elliptic_benchmark.png)')
    parser.add_argument('--json', type=str, default=None,
                       help='Optional JSON output file for raw results')
    
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
    
    # Parse adaptive flag
    adaptive = (args.adaptive == 'True')
    
    # Run benchmark
    results = benchmark_engines(
        N=N,
        n_samples=args.samples,
        adaptive=adaptive,
        max_samples=args.max_samples
    )
    
    # Generate and print report
    report = generate_report(results, N)
    print(report)
    
    # Save plot
    save_plot(results, args.output, N)
    
    # Save JSON if requested
    if args.json:
        output_dir = os.path.dirname(args.json)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Convert numpy types to native Python types for JSON serialization
        json_results = {}
        for engine, metrics in results.items():
            json_results[engine] = {
                k: (v if not isinstance(v, (np.integer, np.floating)) else float(v))
                for k, v in metrics.items()
            }
        
        with open(args.json, 'w') as f:
            json.dump({
                'N': str(N),
                'bit_length': N.bit_length(),
                'results': json_results
            }, f, indent=2)
        
        print(f"JSON results saved to: {args.json}")


if __name__ == "__main__":
    main()
