#!/usr/bin/env python3
"""
Baseline Profiler: θ′(n,k)-biased Sobol sequences for RSA factorization

Profiles standard QMC sampling without Cranley-Patterson rotations.
Establishes baseline variance and timing metrics for comparison.

Author: Z-Sandbox Agent
Date: 2025-11-19
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'utils'))

import numpy as np
import json
import time
from typing import Dict, List, Tuple
from qmc_engines import SobolOwenEngine
from z_framework import theta_prime, kappa

# RSA Challenge Numbers (named challenges only)
RSA_CHALLENGES = {
    'RSA-100': {
        'N': 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139,
        'p': 37975227936943673922808872755445627854565536638199,
        'q': 40094690950920881030683735292761468389214899724061,
        'bits': 330
    },
    'RSA-129': {
        'N': 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541,
        'p': 3490529510847650949147849619903898133417764638493387843990820577,
        'q': 32769132993266709549961988190834461413177642967992942539798288533,
        'bits': 426
    },
    'RSA-155': {
        'N': 1094173864157052742180970732204035761200373294544920599091384213147635041906079937988,
        'p': 102639592829741105772054196573991675900716567808038066803341933521790711307779,
        'q': 106603488380168454820927220360012878679207958575989291522270608237193062808643,
        'bits': 512
    }
}


def compute_candidate_variance(
    candidates: np.ndarray,
    true_factors: Tuple[int, int],
    N: int
) -> Dict[str, float]:
    """
    Compute variance metrics for factorization candidates.
    
    Args:
        candidates: Array of candidate values
        true_factors: (p, q) true factors
        N: RSA modulus
        
    Returns:
        Dictionary of variance metrics
    """
    p, q = true_factors
    sqrt_N = float(N ** 0.5)  # Use Python's power for big integers
    
    # Distance from true factors
    dist_p = np.abs(candidates - p)
    dist_q = np.abs(candidates - q)
    dist_min = np.minimum(dist_p, dist_q)
    
    # Normalized distance (relative to √N)
    norm_dist = dist_min / sqrt_N
    
    # Variance metrics
    return {
        'variance': float(np.var(norm_dist)),
        'std_dev': float(np.std(norm_dist)),
        'mean_dist': float(np.mean(norm_dist)),
        'min_dist': float(np.min(norm_dist)),
        'max_dist': float(np.max(norm_dist)),
        'median_dist': float(np.median(norm_dist)),
        'spread': float(np.max(candidates) - np.min(candidates))
    }


def profile_baseline(
    challenge_name: str,
    n_trials: int = 30,
    n_candidates: int = 1000,
    k: float = 0.3,
    seed: int = 42
) -> Dict:
    """
    Profile baseline θ′(n,k)-biased Sobol sampling.
    
    Args:
        challenge_name: Name of RSA challenge ('RSA-100', 'RSA-129', 'RSA-155')
        n_trials: Number of independent trials
        n_candidates: Candidates per trial
        k: Resolution exponent for θ′(n,k)
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary of profiling results
    """
    if challenge_name not in RSA_CHALLENGES:
        raise ValueError(f"Unknown challenge: {challenge_name}")
    
    challenge = RSA_CHALLENGES[challenge_name]
    N = challenge['N']
    p, q = challenge['p'], challenge['q']
    
    print(f"\n{'='*70}")
    print(f"Baseline Profiling: {challenge_name}")
    print(f"{'='*70}")
    print(f"N = {N}")
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"Bits: {challenge['bits']}")
    print(f"Trials: {n_trials}, Candidates/trial: {n_candidates}, k={k}, seed={seed}")
    print()
    
    # Storage for results
    trial_results = []
    timings = []
    
    # Run trials
    for trial_idx in range(n_trials):
        trial_seed = seed + trial_idx
        np.random.seed(trial_seed)
        
        # Create Sobol engine
        engine = SobolOwenEngine(dimension=1, seed=trial_seed, scramble=True)
        
        # Generate candidates with θ′(n,k) bias
        start_time = time.perf_counter()
        candidates = engine.generate_candidates(
            N=N,
            n_samples=n_candidates,
            bias='z-framework',
            k=k
        )
        elapsed = time.perf_counter() - start_time
        
        # Compute variance metrics
        metrics = compute_candidate_variance(candidates, (p, q), N)
        metrics['trial'] = trial_idx
        metrics['n_candidates'] = len(candidates)
        metrics['timing_sec'] = elapsed
        
        trial_results.append(metrics)
        timings.append(elapsed)
        
        if (trial_idx + 1) % 10 == 0:
            print(f"  Trial {trial_idx + 1}/{n_trials} complete")
    
    # Aggregate statistics
    variances = [r['variance'] for r in trial_results]
    mean_variance = np.mean(variances)
    std_variance = np.std(variances)
    
    # Bootstrap 95% CI for variance
    n_bootstrap = 2000
    bootstrap_vars = []
    rng = np.random.RandomState(seed)
    for _ in range(n_bootstrap):
        resample = rng.choice(variances, size=len(variances), replace=True)
        bootstrap_vars.append(np.mean(resample))
    
    ci_lower = np.percentile(bootstrap_vars, 2.5)
    ci_upper = np.percentile(bootstrap_vars, 97.5)
    
    print(f"\n{'='*70}")
    print("BASELINE RESULTS")
    print(f"{'='*70}")
    print(f"Mean Variance: {mean_variance:.6e} ± {std_variance:.6e}")
    print(f"95% CI: [{ci_lower:.6e}, {ci_upper:.6e}]")
    print(f"Mean Timing: {np.mean(timings):.4f}s ± {np.std(timings):.4f}s")
    print(f"Median Timing: {np.median(timings):.4f}s")
    print()
    
    # Return complete results
    return {
        'challenge': challenge_name,
        'configuration': {
            'n_trials': n_trials,
            'n_candidates': n_candidates,
            'k': k,
            'seed': seed,
            'engine': 'SobolOwenEngine',
            'scramble': True,
            'bias': 'z-framework'
        },
        'rsa_challenge': {
            'N': str(N),
            'p': str(p),
            'q': str(q),
            'bits': challenge['bits']
        },
        'statistics': {
            'mean_variance': mean_variance,
            'std_variance': std_variance,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'median_variance': float(np.median(variances)),
            'min_variance': float(np.min(variances)),
            'max_variance': float(np.max(variances))
        },
        'timing': {
            'mean_sec': float(np.mean(timings)),
            'std_sec': float(np.std(timings)),
            'median_sec': float(np.median(timings)),
            'min_sec': float(np.min(timings)),
            'max_sec': float(np.max(timings))
        },
        'trials': trial_results
    }


def main():
    """Run baseline profiling on all RSA challenges."""
    results = {}
    
    for challenge_name in ['RSA-100', 'RSA-129', 'RSA-155']:
        try:
            result = profile_baseline(
                challenge_name=challenge_name,
                n_trials=30,
                n_candidates=1000,
                k=0.3,
                seed=42
            )
            results[challenge_name] = result
            
            # Save individual result
            output_file = f"../results/baseline_{challenge_name.lower()}.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✓ Saved: {output_file}\n")
            
        except Exception as e:
            print(f"✗ Error profiling {challenge_name}: {e}\n")
            results[challenge_name] = {'error': str(e)}
    
    # Save combined results
    combined_file = "../results/baseline_all.json"
    with open(combined_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ All results saved to: {combined_file}")


if __name__ == "__main__":
    main()
