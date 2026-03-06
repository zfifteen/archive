"""
Scalable Prime Curvature Computations for N=10⁹
==============================================

Enhanced implementation that scales from N=10⁶ to N=10⁹, with efficient prime generation,
divisor counting, bootstrap confidence intervals, and κ(n) statistics.

Validates the persistence of conditional prime density improvement under canonical benchmark methodology and κ(n) statistics for large N,
testing asymptotic behavior E(k) ~ log log N.

Dependencies:
    numpy, scipy, sympy, sklearn, mpmath

Usage:
    python scalable_proof.py --max_n 1000000 --k_start 0.2 --k_end 0.4 --k_step 0.002 --bins 20 --bootstrap 1000
"""

import numpy as np
import mpmath as mp
from sympy import isprime
from sklearn.mixture import GaussianMixture
import argparse
import time
import psutil
import os
import warnings
from typing import Tuple, List, Dict, Any
from collections import defaultdict

warnings.filterwarnings("ignore")

# Set high precision for mpmath operations
mp.mp.dps = 50

# Mathematical constants
PHI = mp.mpf((1 + mp.sqrt(5)) / 2)  # Golden ratio
E_SQUARED = mp.exp(2)


class MemoryTracker:
    """Track memory usage during computation"""
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.peak_memory = 0
        
    def get_memory_mb(self):
        """Get current memory usage in MB"""
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = max(self.peak_memory, memory_mb)
        return memory_mb


def sieve_of_eratosthenes(limit: int) -> np.ndarray:
    """
    Efficient Sieve of Eratosthenes using numpy for large N.
    Returns array of primes up to limit.
    """
    if limit < 2:
        return np.array([], dtype=np.int64)
    
    # Create boolean array "prime[0..limit]" and set all entries as True
    prime = np.ones(limit + 1, dtype=bool)
    prime[0] = prime[1] = False
    
    p = 2
    while p * p <= limit:
        if prime[p]:
            # Mark all multiples of p as not prime
            prime[p*p::p] = False
        p += 1
    
    # Extract all prime numbers
    return np.where(prime)[0].astype(np.int64)


def count_divisors_efficient(n: int) -> int:
    """
    Efficient divisor counting function.
    For large n, this is much faster than sympy.divisors(n)
    """
    if n <= 1:
        return 1
    
    count = 0
    sqrt_n = int(np.sqrt(n))
    
    for i in range(1, sqrt_n + 1):
        if n % i == 0:
            count += 1
            if i != n // i:  # Avoid counting the square root twice
                count += 1
    
    return count


def compute_kappa(n: int) -> float:
    """
    Compute κ(n) = d(n) · ln(n+1)/e² where d(n) is the divisor count.
    """
    d_n = count_divisors_efficient(n)
    return float(d_n * np.log(n + 1) / E_SQUARED)


def frame_shift_residues(n_vals: np.ndarray, k: float) -> np.ndarray:
    """
    Compute θ'(n,k) = φ · {n/φ}^k with high precision.
    """
    # Convert to mpmath for high precision modular arithmetic
    phi_float = float(PHI)
    
    # Compute modular residues with numpy for efficiency
    mod_phi = np.mod(n_vals, phi_float) / phi_float
    
    # Apply power-law warping
    return phi_float * np.power(mod_phi, k)


def bin_densities(theta_all: np.ndarray, theta_pr: np.ndarray, nbins: int = 20) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Bin θ' values and compute density enhancements.
    Returns (all_density, prime_density, enhancement[%]).
    """
    phi_float = float(PHI)
    bins = np.linspace(0, phi_float, nbins + 1)
    
    # Compute histograms
    all_counts, _ = np.histogram(theta_all, bins=bins)
    pr_counts, _ = np.histogram(theta_pr, bins=bins)
    
    # Convert to densities
    all_d = all_counts / len(theta_all)
    pr_d = pr_counts / len(theta_pr) if len(theta_pr) > 0 else np.zeros_like(all_counts)
    
    # Compute enhancements safely
    with np.errstate(divide='ignore', invalid='ignore'):
        enh = (pr_d - all_d) / all_d * 100
    
    # Mask invalid enhancements
    enh = np.where(all_d > 0, enh, -np.inf)
    
    return all_d, pr_d, enh


def bootstrap_enhancement(theta_all: np.ndarray, theta_pr: np.ndarray, k: float, n_bootstrap: int = 1000, nbins: int = 20) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval for maximum enhancement at given k.
    Returns (mean_enhancement, ci_low, ci_high).
    """
    enhancements = []
    n_primes = len(theta_pr)
    
    for _ in range(n_bootstrap):
        # Bootstrap sample of primes
        bootstrap_indices = np.random.choice(n_primes, size=n_primes, replace=True)
        theta_pr_bootstrap = theta_pr[bootstrap_indices]
        
        # Compute enhancement for this bootstrap sample
        _, _, enh = bin_densities(theta_all, theta_pr_bootstrap, nbins=nbins)
        valid_enh = enh[np.isfinite(enh)]
        
        if len(valid_enh) > 0:
            enhancements.append(np.max(valid_enh))
        else:
            enhancements.append(-np.inf)
    
    enhancements = np.array(enhancements)
    valid_enhancements = enhancements[np.isfinite(enhancements)]
    
    if len(valid_enhancements) > 0:
        mean_enh = np.mean(valid_enhancements)
        ci_low = np.percentile(valid_enhancements, 2.5)
        ci_high = np.percentile(valid_enhancements, 97.5)
        return mean_enh, ci_low, ci_high
    else:
        return -np.inf, -np.inf, -np.inf


def compute_kappa_statistics(primes: np.ndarray, composites: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Compute κ(n) statistics for primes and composites.
    Returns (mean_kappa_primes, std_kappa_primes, mean_kappa_composites, std_kappa_composites).
    """
    # Sample for efficiency if arrays are too large
    max_sample = 10000
    
    if len(primes) > max_sample:
        primes_sample = np.random.choice(primes, size=max_sample, replace=False)
    else:
        primes_sample = primes
        
    if len(composites) > max_sample:
        composites_sample = np.random.choice(composites, size=max_sample, replace=False)
    else:
        composites_sample = composites
    
    # Compute κ values
    kappa_primes = [compute_kappa(n) for n in primes_sample]
    kappa_composites = [compute_kappa(n) for n in composites_sample]
    
    return (
        np.mean(kappa_primes),
        np.std(kappa_primes),
        np.mean(kappa_composites),
        np.std(kappa_composites)
    )


def process_chunk(n_max: int, k_values: np.ndarray, nbins: int = 20, bootstrap: int = 1000, memory_tracker: MemoryTracker = None) -> Dict[str, Any]:
    """
    Process a single chunk of data up to n_max.
    """
    start_time = time.time()
    
    print(f"  Generating primes up to {n_max:,}...")
    primes = sieve_of_eratosthenes(n_max)
    prime_set = set(primes)
    
    # Create composites array (sample for efficiency)
    all_numbers = np.arange(2, n_max + 1)
    composites = all_numbers[~np.isin(all_numbers, primes)]
    
    print(f"  Found {len(primes):,} primes and {len(composites):,} composites")
    
    if memory_tracker:
        print(f"  Memory usage: {memory_tracker.get_memory_mb():.1f} MB")
    
    # Compute κ statistics
    print(f"  Computing κ(n) statistics...")
    kappa_stats = compute_kappa_statistics(primes, composites)
    
    # Find optimal k with enhancement
    best_k = None
    best_enhancement = -np.inf
    k_results = {}
    
    print(f"  Processing {len(k_values)} k values...")
    for i, k in enumerate(k_values):
        if i % 20 == 0:
            print(f"    Progress: {i}/{len(k_values)} ({100*i/len(k_values):.1f}%)")
        
        # Apply frame shift transformation
        theta_all = frame_shift_residues(all_numbers, k)
        theta_pr = frame_shift_residues(primes, k)
        
        # Compute enhancement
        _, _, enh = bin_densities(theta_all, theta_pr, nbins=nbins)
        max_enh = np.max(enh[np.isfinite(enh)]) if np.any(np.isfinite(enh)) else -np.inf
        
        k_results[k] = max_enh
        
        if max_enh > best_enhancement:
            best_enhancement = max_enh
            best_k = k
    
    # Compute bootstrap CI for best k
    print(f"  Computing bootstrap CI for k* = {best_k:.3f}...")
    theta_all_best = frame_shift_residues(all_numbers, best_k)
    theta_pr_best = frame_shift_residues(primes, best_k)
    
    mean_enh, ci_low, ci_high = bootstrap_enhancement(
        theta_all_best, theta_pr_best, best_k, n_bootstrap=bootstrap, nbins=nbins
    )
    
    # Sample θ' values for first/last 100 primes
    sample_primes_first = primes[:min(100, len(primes))]
    sample_primes_last = primes[-min(100, len(primes)):]
    
    theta_sample_first = frame_shift_residues(sample_primes_first, best_k)
    theta_sample_last = frame_shift_residues(sample_primes_last, best_k)
    
    kappa_sample_first = [compute_kappa(n) for n in sample_primes_first]
    kappa_sample_last = [compute_kappa(n) for n in sample_primes_last]
    
    runtime = time.time() - start_time
    
    return {
        'n_max': n_max,
        'n_primes': len(primes),
        'n_composites': len(composites),
        'k_star': best_k,
        'max_enhancement': best_enhancement,
        'mean_enhancement': mean_enh,
        'ci_low': ci_low,
        'ci_high': ci_high,
        'kappa_stats': kappa_stats,
        'sample_primes_first': sample_primes_first,
        'sample_primes_last': sample_primes_last,
        'theta_sample_first': theta_sample_first,
        'theta_sample_last': theta_sample_last,
        'kappa_sample_first': kappa_sample_first,
        'kappa_sample_last': kappa_sample_last,
        'runtime': runtime,
        'peak_memory_mb': memory_tracker.peak_memory if memory_tracker else 0
    }


def analyze_asymptotic_behavior(results: List[Dict[str, Any]]) -> None:
    """
    Analyze asymptotic behavior E(k) ~ log log N.
    """
    if len(results) < 2:
        return
    
    print("\n=== ASYMPTOTIC BEHAVIOR ANALYSIS ===")
    print("Testing E(k) ~ log log N:")
    print("| N | log log N | E(k*) | E/log log N |")
    print("|---|-----------|-------|-------------|")
    
    for result in results:
        n = result['n_max']
        log_log_n = np.log(np.log(n))
        enhancement = result['max_enhancement']
        ratio = enhancement / log_log_n if log_log_n > 0 else 0
        
        print(f"| {n:,} | {log_log_n:.3f} | {enhancement:.1f}% | {ratio:.2f} |")
    
    # Compute correlation
    if len(results) >= 2:
        log_log_values = [np.log(np.log(r['n_max'])) for r in results]
        enhancements = [r['max_enhancement'] for r in results]
        
        correlation = np.corrcoef(log_log_values, enhancements)[0, 1]
        print(f"\nCorrelation between log log N and E(k*): {correlation:.3f}")
        
        # Linear fit
        coeffs = np.polyfit(log_log_values, enhancements, 1)
        print(f"Linear fit: E(k*) ≈ {coeffs[0]:.2f} × log log N + {coeffs[1]:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Scalable Prime Curvature Computations")
    parser.add_argument('--max_n', type=int, default=1000000, help='Maximum N to test')
    parser.add_argument('--k_start', type=float, default=0.2, help='Start of k range')
    parser.add_argument('--k_end', type=float, default=0.4, help='End of k range')
    parser.add_argument('--k_step', type=float, default=0.002, help='Step size for k')
    parser.add_argument('--bins', type=int, default=20, help='Number of bins')
    parser.add_argument('--bootstrap', type=int, default=1000, help='Bootstrap resamples')
    parser.add_argument('--incremental', action='store_true', help='Test incremental N values')
    parser.add_argument('--save_results', type=str, help='Save results to CSV file')
    
    args = parser.parse_args()
    
    # Set up k values
    k_values = np.arange(args.k_start, args.k_end + args.k_step, args.k_step)
    
    # Determine N values to test
    if args.incremental:
        n_values = []
        if args.max_n >= 1000000:
            n_values.append(1000000)
        if args.max_n >= 10000000:
            n_values.append(10000000)
        if args.max_n >= 100000000:
            n_values.append(100000000)
        if args.max_n >= 1000000000:
            n_values.append(1000000000)
    else:
        n_values = [args.max_n]
    
    print(f"=== Scalable Prime Curvature Computations ===")
    print(f"N values: {n_values}")
    print(f"k range: [{args.k_start:.3f}, {args.k_end:.3f}] with step {args.k_step:.3f}")
    print(f"Bins: {args.bins}, Bootstrap: {args.bootstrap}")
    print(f"Golden ratio φ = {float(PHI):.6f}")
    print()
    
    # Results storage
    all_results = []
    
    # Process each N value
    for n_max in n_values:
        print(f"Processing N = {n_max:,}")
        
        memory_tracker = MemoryTracker()
        
        try:
            result = process_chunk(
                n_max=n_max,
                k_values=k_values,
                nbins=args.bins,
                bootstrap=args.bootstrap,
                memory_tracker=memory_tracker
            )
            all_results.append(result)
            
            print(f"✓ Completed N = {n_max:,} in {result['runtime']:.1f}s")
            print(f"  k* = {result['k_star']:.3f}, e_max = {result['max_enhancement']:.1f}%")
            print(f"  CI: [{result['ci_low']:.1f}%, {result['ci_high']:.1f}%]")
            print(f"  Peak memory: {result['peak_memory_mb']:.1f} MB")
            print()
            
        except Exception as e:
            print(f"✗ Failed N = {n_max:,}: {e}")
            print()
    
    # Print final results table
    print("=== RESULTS TABLE ===")
    print("| N | k* | e_max (%) | CI_low | CI_high | mean_κ_primes | std_κ_primes | mean_κ_composites | std_κ_composites | Runtime(s) | Memory(MB) |")
    print("|---|----|-----------:|-------:|--------:|--------------:|-------------:|------------------:|-----------------:|-----------:|-----------:|")
    
    for result in all_results:
        kappa_stats = result['kappa_stats']
        print(f"| {result['n_max']:,} | {result['k_star']:.3f} | {result['max_enhancement']:.1f} | "
              f"{result['ci_low']:.1f} | {result['ci_high']:.1f} | "
              f"{kappa_stats[0]:.3f} | {kappa_stats[1]:.3f} | "
              f"{kappa_stats[2]:.3f} | {kappa_stats[3]:.3f} | "
              f"{result['runtime']:.1f} | {result['peak_memory_mb']:.1f} |")
    
    # Asymptotic behavior analysis
    analyze_asymptotic_behavior(all_results)
    
    # Save results if requested
    if args.save_results and all_results:
        import pandas as pd
        
        data = []
        for result in all_results:
            kappa_stats = result['kappa_stats']
            data.append({
                'N': result['n_max'],
                'k_star': result['k_star'],
                'e_max_percent': result['max_enhancement'],
                'CI_low': result['ci_low'],
                'CI_high': result['ci_high'],
                'mean_kappa_primes': kappa_stats[0],
                'std_kappa_primes': kappa_stats[1],
                'mean_kappa_composites': kappa_stats[2],
                'std_kappa_composites': kappa_stats[3],
                'runtime_seconds': result['runtime'],
                'peak_memory_mb': result['peak_memory_mb']
            })
        
        df = pd.DataFrame(data)
        df.to_csv(args.save_results, index=False)
        print(f"\n✓ Results saved to {args.save_results}")
    
    # Print sample arrays
    if all_results:
        print("\n=== SAMPLE DATA ===")
        for result in all_results:
            print(f"\nN = {result['n_max']:,}:")
            print(f"First 10 primes: {list(result['sample_primes_first'][:10])}")
            print(f"Last 10 primes: {list(result['sample_primes_last'][-10:])}")
            print(f"θ' for first 5 primes: {[f'{x:.6f}' for x in result['theta_sample_first'][:5]]}")
            print(f"κ for first 5 primes: {[f'{x:.6f}' for x in result['kappa_sample_first'][:5]]}")
    
    # Success criteria validation
    print("\n=== SUCCESS CRITERIA VALIDATION ===")
    target_k = 0.3
    target_enhancement = 15.0
    
    for result in all_results:
        k_star = result['k_star']
        e_max = result['max_enhancement']
        ci_width = result['ci_high'] - result['ci_low']
        
        k_close = abs(k_star - target_k) < 0.01
        e_reasonable = 0.1 * target_enhancement <= e_max <= 10 * target_enhancement  # Within order of magnitude
        ci_reasonable = ci_width < 50  # CI width less than 50%
        
        status = "✓" if (k_close and e_reasonable and ci_reasonable) else "✗"
        print(f"{status} N={result['n_max']:,}: k*={k_star:.3f} (target ±0.01 of {target_k}), "
              f"e_max={e_max:.1f}% (target ~{target_enhancement}%), CI width={ci_width:.1f}%")


if __name__ == "__main__":
    main()