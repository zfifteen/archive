#!/usr/bin/env python3
"""
Eigenvalue Multiplicity Experiment: GVA with Spectral Pruning

This experiment tests whether eigenvalue multiplicity bounds can improve GVA's
geodesic factorization by pruning search spaces using divisor-function constraints.

Hypothesis to Falsify:
    Multiplicity-bounded pruning (r_n(k) ≤ d(k)) correlates with factor proximity
    in GVA's geodesic embedding and improves success rate or runtime.

Experiment Design:
    1. Baseline GVA on 64-bit and 128-bit balanced semiprimes
    2. Modified GVA with multiplicity-based candidate pruning
    3. Compare: success rate, search space size, runtime

Key Question:
    Does spectral structure provide actionable information for factorization,
    or is this connection purely mathematical curiosity?
"""

import sys
import os
import math
import time
import random
import json
import csv
from typing import Tuple, List, Dict, Optional
from datetime import datetime
import multiprocessing
from functools import partial

import sympy as sp
import mpmath as mp
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from eigenvalue_calculator import EigenvalueMultiplicityCalculator

mp.mp.dps = 100


class GVAWithSpectralPruning:
    """GVA factorization with optional eigenvalue multiplicity pruning."""
    
    def __init__(self, dimension: int = 7, use_spectral_pruning: bool = False,
                 multiplicity_threshold: Optional[int] = None):
        """
        Initialize GVA with optional spectral pruning.
        
        Args:
            dimension: Torus embedding dimension (default 7)
            use_spectral_pruning: Enable multiplicity-based pruning
            multiplicity_threshold: Prune candidates with r_n(k) > threshold (None = auto)
        """
        self.dimension = dimension
        self.use_spectral_pruning = use_spectral_pruning
        self.multiplicity_threshold = multiplicity_threshold
        self.calc = EigenvalueMultiplicityCalculator(dimension=dimension)
        
        # Statistics
        self.stats = {
            'candidates_generated': 0,
            'candidates_pruned_spectral': 0,
            'candidates_tested_divisibility': 0,
            'candidates_passed_geometry': 0
        }
    
    @staticmethod
    def is_prime_robust(n: int) -> bool:
        """Robust primality check."""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        return sp.isprime(n)
    
    def embed_torus_geodesic(self, n: int, k: float = 0.04) -> List[float]:
        """
        Torus geodesic embedding for GVA.
        Z = A(B / c) with c = e², iterative θ'(n, k)
        
        Args:
            n: Integer to embed
            k: Resolution parameter (default 0.04 for 64-bit)
            
        Returns:
            List of coordinates on [0,1)^dims
        """
        phi = mp.mpf((1 + mp.sqrt(5)) / 2)
        c = mp.exp(2)
        x = mp.mpf(n) / c
        coords = []
        for _ in range(self.dimension):
            x = phi * mp.power(mp.frac(x / phi), k)
            coords.append(float(mp.frac(x)))
        return coords
    
    def riemannian_distance(self, coords1: List[float], coords2: List[float], N: int) -> float:
        """
        Riemannian distance on torus with curvature.
        κ(n) = 4 · ln(n+1) / e²
        
        Args:
            coords1, coords2: Torus coordinates
            N: Reference integer for curvature
            
        Returns:
            Riemannian distance
        """
        kappa = 4 * math.log(N + 1) / math.exp(2)
        total = 0.0
        for c1, c2 in zip(coords1, coords2):
            d = min(abs(c1 - c2), 1 - abs(c1 - c2))
            total += (d * (1 + kappa * d)) ** 2
        return math.sqrt(total)
    
    def adaptive_threshold(self, N: int) -> float:
        """Adaptive ε = 0.12 / (1 + κ) * 10"""
        kappa = 4 * math.log(N + 1) / math.exp(2)
        return 0.12 / (1 + kappa) * 10
    
    def should_prune_candidate(self, candidate: int, N: int) -> bool:
        """
        Determine if candidate should be pruned based on spectral multiplicity.
        
        Hypothesis: Candidates with high eigenvalue multiplicity r_n(k) are
        less likely to be factors because they correspond to "overcrowded"
        regions of the spectral lattice.
        
        Args:
            candidate: Potential factor
            N: Semiprime to factor
            
        Returns:
            True if candidate should be pruned
        """
        if not self.use_spectral_pruning:
            return False
        
        # Compute lattice norm for candidate
        # In GVA, we're looking for p where p ≈ sqrt(N)
        # The lattice point corresponds to (p, q) where p*q = N
        # We use the divisor count as a proxy for multiplicity
        
        d_candidate = int(self.calc.divisor_function(candidate))
        
        # Auto-threshold: prune if divisor count exceeds median + 2*std
        if self.multiplicity_threshold is None:
            # Dynamic threshold based on sqrt(N) divisor statistics
            sqrtN = int(math.sqrt(N))
            sample_divisors = [int(self.calc.divisor_function(sqrtN + d)) 
                              for d in range(-100, 101, 10)]
            mean_div = float(np.mean(sample_divisors))
            std_div = float(np.std(sample_divisors))
            threshold = mean_div + 2 * std_div
        else:
            threshold = self.multiplicity_threshold
        
        return d_candidate > threshold
    
    def factorize(self, N: int, R: int = 100000, k_param: float = 0.04,
                  verbose: bool = False) -> Tuple[Optional[int], Optional[int], float, Dict]:
        """
        Factor N using GVA with optional spectral pruning.
        
        Args:
            N: Semiprime to factor
            R: Search radius around sqrt(N)
            k_param: Resolution parameter for embedding
            verbose: Print progress
            
        Returns:
            (p, q, distance, stats) where p*q = N or (None, None, 0.0, stats)
        """
        if self.is_prime_robust(N):
            return None, None, 0.0, self.stats
        
        if verbose:
            print(f"GVA Factorization: N = {N} ({N.bit_length()} bits)")
            print(f"Spectral Pruning: {self.use_spectral_pruning}")
        
        sqrtN = int(math.sqrt(N))
        emb_N = self.embed_torus_geodesic(N, k=k_param)
        epsilon = self.adaptive_threshold(N)
        
        # Reset statistics
        self.stats = {
            'candidates_generated': 0,
            'candidates_pruned_spectral': 0,
            'candidates_tested_divisibility': 0,
            'candidates_passed_geometry': 0
        }
        
        # Pre-compute pruning threshold once (not per candidate)
        if self.use_spectral_pruning:
            if self.multiplicity_threshold is None:
                # Dynamic threshold based on sqrt(N) divisor statistics
                sample_divisors = [int(self.calc.divisor_function(sqrtN + d)) 
                                  for d in range(-100, 101, 10)]
                mean_div = float(np.mean(sample_divisors))
                std_div = float(np.std(sample_divisors))
                pruning_threshold = mean_div + 2 * std_div
            else:
                pruning_threshold = self.multiplicity_threshold
        else:
            pruning_threshold = float('inf')  # No pruning
        
        # Search candidates around sqrt(N)
        for d in range(-R, R + 1):
            p = sqrtN + d
            self.stats['candidates_generated'] += 1
            
            if p <= 1 or p >= N:
                continue
            
            # Spectral pruning (if enabled)
            if self.use_spectral_pruning:
                d_candidate = int(self.calc.divisor_function(p))
                if d_candidate > pruning_threshold:
                    self.stats['candidates_pruned_spectral'] += 1
                    continue
            
            # Classical divisibility test
            self.stats['candidates_tested_divisibility'] += 1
            if N % p != 0:
                continue
            
            q = N // p
            
            # Primality and balance checks
            if not self.is_prime_robust(p) or not self.is_prime_robust(q):
                continue
            
            # Balance check: |log2(p/q)| ≤ 1
            if abs(math.log2(p / q)) > 1:
                continue
            
            # Geometric validation
            emb_p = self.embed_torus_geodesic(p, k=k_param)
            dist = self.riemannian_distance(emb_N, emb_p, N)
            
            if dist < epsilon:
                self.stats['candidates_passed_geometry'] += 1
                if verbose:
                    print(f"SUCCESS: {p} × {q} = {N}")
                    print(f"Distance: {dist:.6f}, Threshold: {epsilon:.6f}")
                return p, q, dist, self.stats.copy()
        
        if verbose:
            print("No factors found")
        return None, None, 0.0, self.stats.copy()


def generate_balanced_semiprime(bits: int, seed: int) -> Tuple[int, int, int]:
    """Generate balanced semiprime N = p * q with p ≈ q."""
    random.seed(seed)
    half_bits = bits // 2
    base = 2 ** half_bits
    offset = random.randint(0, 10 ** (half_bits // 10))
    p = sp.nextprime(base + offset)
    q = sp.nextprime(base + offset + random.randint(1, 10 ** (half_bits // 20)))
    N = int(p) * int(q)
    return N, int(p), int(q)


def run_single_trial(args: Tuple[int, int, bool, int]) -> Dict:
    """Run single factorization trial (for parallel execution)."""
    trial_id, bits, use_pruning, seed = args
    
    N, true_p, true_q = generate_balanced_semiprime(bits, seed)
    
    # Adjust parameters by bit size
    if bits <= 64:
        R = 100000
        k_param = 0.04
    else:  # 128-bit
        R = 100000
        k_param = 0.06
    
    gva = GVAWithSpectralPruning(dimension=7, use_spectral_pruning=use_pruning)
    
    start_time = time.time()
    found_p, found_q, dist, stats = gva.factorize(N, R=R, k_param=k_param, verbose=False)
    elapsed = time.time() - start_time
    
    success = (found_p is not None and {found_p, found_q} == {true_p, true_q})
    
    return {
        'trial_id': trial_id,
        'bits': bits,
        'N': N,
        'true_p': true_p,
        'true_q': true_q,
        'found_p': found_p,
        'found_q': found_q,
        'success': success,
        'distance': dist,
        'elapsed_seconds': elapsed,
        'use_pruning': use_pruning,
        **stats
    }


def run_experiment(num_trials: int = 25, bits_list: List[int] = [64, 128],
                   output_dir: str = './results') -> Dict:
    """
    Run comparative experiment: GVA baseline vs. GVA with spectral pruning.
    
    Args:
        num_trials: Number of trials per configuration
        bits_list: List of bit sizes to test
        output_dir: Directory for results
        
    Returns:
        Dictionary with aggregated results
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("=" * 70)
    print("EIGENVALUE MULTIPLICITY SPECTRAL BOUNDS EXPERIMENT")
    print("=" * 70)
    print(f"Trials per config: {num_trials}")
    print(f"Bit sizes: {bits_list}")
    print(f"Configurations: Baseline GVA, GVA+SpectralPruning")
    print("=" * 70)
    print()
    
    all_results = []
    
    for bits in bits_list:
        for use_pruning in [False, True]:
            config_name = f"{bits}bit_{'pruned' if use_pruning else 'baseline'}"
            print(f"\n{'=' * 70}")
            print(f"Running: {config_name}")
            print(f"{'=' * 70}")
            
            # Prepare trial arguments
            trial_args = [(i, bits, use_pruning, 42 + i) for i in range(num_trials)]
            
            # Run trials in parallel
            with multiprocessing.Pool(processes=min(4, multiprocessing.cpu_count())) as pool:
                results = pool.map(run_single_trial, trial_args)
            
            # Aggregate statistics
            successes = sum(1 for r in results if r['success'])
            success_rate = successes / num_trials * 100
            avg_time = np.mean([r['elapsed_seconds'] for r in results])
            
            # Pruning statistics (only for pruned variant)
            if use_pruning:
                avg_pruned = np.mean([r['candidates_pruned_spectral'] for r in results])
                avg_tested = np.mean([r['candidates_tested_divisibility'] for r in results])
                prune_ratio = avg_pruned / (avg_pruned + avg_tested) * 100 if (avg_pruned + avg_tested) > 0 else 0
            else:
                avg_pruned = 0
                avg_tested = np.mean([r['candidates_tested_divisibility'] for r in results])
                prune_ratio = 0
            
            print(f"\nResults for {config_name}:")
            print(f"  Success Rate: {successes}/{num_trials} ({success_rate:.1f}%)")
            print(f"  Average Time: {avg_time:.2f}s")
            print(f"  Avg Candidates Tested: {avg_tested:.0f}")
            if use_pruning:
                print(f"  Avg Candidates Pruned: {avg_pruned:.0f}")
                print(f"  Prune Ratio: {prune_ratio:.1f}%")
            
            # Save individual trial results
            csv_filename = os.path.join(output_dir, f'{config_name}_{timestamp}.csv')
            with open(csv_filename, 'w', newline='') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            
            all_results.extend(results)
    
    # Save aggregated summary
    summary = {
        'timestamp': timestamp,
        'num_trials': num_trials,
        'bits_list': bits_list,
        'results': all_results
    }
    
    summary_filename = os.path.join(output_dir, f'summary_{timestamp}.json')
    with open(summary_filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print("EXPERIMENT COMPLETE")
    print(f"Results saved to: {output_dir}")
    print(f"{'=' * 70}\n")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run eigenvalue multiplicity experiment')
    parser.add_argument('--trials', type=int, default=25, help='Number of trials per config')
    parser.add_argument('--bits', type=int, nargs='+', default=[64], help='Bit sizes to test')
    parser.add_argument('--output', type=str, default='./results', help='Output directory')
    
    args = parser.parse_args()
    
    result = run_experiment(
        num_trials=args.trials,
        bits_list=args.bits,
        output_dir=args.output
    )
