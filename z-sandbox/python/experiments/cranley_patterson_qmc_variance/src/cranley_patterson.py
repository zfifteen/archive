#!/usr/bin/env python3
"""
Cranley-Patterson Rotation for QMC Variance Reduction

Implements Cranley-Patterson rotations (random shifts modulo 1) applied to
θ′(n,k)-biased Sobol sequences. Tests two variants:
1. CP-Static: Single random rotation per trial
2. CP-Adaptive: κ(n)-guided rotation selection

Mathematical Background:
- Cranley-Patterson: u'_i = (u_i + r) mod 1, where r ~ U[0,1]^d
- Reduces variance by randomizing low-discrepancy patterns
- Commonly used in QMC integration for variance estimation

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
from typing import Dict, List, Tuple, Optional
from qmc_engines import SobolOwenEngine
from z_framework import theta_prime, kappa

# Import RSA challenges from baseline
from baseline_profile import RSA_CHALLENGES, compute_candidate_variance


class CranleyPattersonEngine:
    """
    Sobol engine with Cranley-Patterson rotation.
    
    Applies random shifts to Sobol sequences: u'_i = (u_i + r) mod 1
    """
    
    def __init__(
        self,
        dimension: int = 1,
        seed: Optional[int] = None,
        rotation_type: str = 'static',
        N: Optional[int] = None
    ):
        """
        Initialize Cranley-Patterson engine.
        
        Args:
            dimension: Dimensionality of sampling space
            seed: Random seed for reproducibility
            rotation_type: 'static' (single random) or 'adaptive' (κ-guided)
            N: RSA modulus (required for adaptive rotation)
        """
        self.dimension = dimension
        self.seed = seed
        self.rotation_type = rotation_type
        self.N = N
        
        # Create base Sobol engine
        self.sobol = SobolOwenEngine(dimension=dimension, seed=seed, scramble=True)
        
        # Initialize rotation vector
        if rotation_type == 'static':
            rng = np.random.RandomState(seed)
            self.rotation = rng.uniform(0, 1, size=dimension)
        elif rotation_type == 'adaptive':
            if N is None:
                raise ValueError("N required for adaptive rotation")
            self.rotation = self._compute_adaptive_rotation()
        else:
            raise ValueError(f"Unknown rotation type: {rotation_type}")
    
    def _compute_adaptive_rotation(self) -> np.ndarray:
        """
        Compute κ(n)-guided rotation vector.
        
        Uses curvature signal to bias rotation towards high-curvature regions.
        """
        sqrt_N = float(self.N ** 0.5) if self.N > 2**53 else np.sqrt(self.N)
        
        # Sample κ(n) around √N
        n_samples = 1000
        rng = np.random.RandomState(self.seed)
        sample_points = sqrt_N * (0.9 + 0.2 * rng.uniform(0, 1, n_samples))
        kappa_values = kappa(sample_points)
        
        # Normalize to [0,1] for rotation
        kappa_min = np.min(kappa_values)
        kappa_max = np.max(kappa_values)
        
        if kappa_max > kappa_min:
            kappa_norm = (kappa_values - kappa_min) / (kappa_max - kappa_min)
        else:
            kappa_norm = np.ones_like(kappa_values) * 0.5
        
        # Use mean of high-curvature regions as rotation
        high_curvature_mask = kappa_norm > np.percentile(kappa_norm, 75)
        rotation_value = np.mean(kappa_norm[high_curvature_mask])
        
        return np.array([rotation_value] * self.dimension)
    
    def generate(self, n_samples: int) -> np.ndarray:
        """
        Generate Cranley-Patterson rotated Sobol points.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Rotated points in [0,1]^d
        """
        # Generate base Sobol points
        points = self.sobol.generate(n_samples)
        
        # Apply Cranley-Patterson rotation
        rotated = (points + self.rotation) % 1.0
        
        return rotated
    
    def generate_candidates(
        self,
        N: int,
        n_samples: int,
        bias: Optional[str] = 'z-framework',
        k: float = 0.3
    ) -> np.ndarray:
        """
        Generate CP-rotated factorization candidates.
        
        Args:
            N: RSA modulus
            n_samples: Number of candidates
            bias: Bias type ('z-framework' or None)
            k: Resolution exponent for θ′(n,k)
            
        Returns:
            Array of candidate integers
        """
        # Generate rotated QMC points
        points = self.generate(n_samples)
        
        # Apply Z-bias (reuse logic from base engine)
        from z_framework import apply_z_bias
        
        if bias == 'z-framework':
            candidates = apply_z_bias(points, N, k)
        else:
            # Standard scaling around √N
            sqrt_N = float(N ** 0.5) if N > 2**53 else np.sqrt(N)
            bit_length = N.bit_length()
            
            if bit_length <= 64:
                spread = 0.15
            elif bit_length <= 128:
                spread = 0.10
            else:
                spread = 0.05
            
            candidates = sqrt_N * (1 - spread + 2 * spread * points[:, 0])
        
        # Convert to integers and ensure uniqueness
        # For large RSA numbers, use Python integers to avoid overflow
        if N > 2**63:
            # Use object dtype for large integers
            candidates_int = [int(x) for x in candidates]
            candidates = np.array(sorted(set(candidates_int)))
        else:
            candidates = np.unique(candidates.astype(int))
        
        return candidates


def profile_cranley_patterson(
    challenge_name: str,
    rotation_type: str = 'static',
    n_trials: int = 30,
    n_candidates: int = 1000,
    k: float = 0.3,
    seed: int = 42
) -> Dict:
    """
    Profile Cranley-Patterson rotated QMC sampling.
    
    Args:
        challenge_name: Name of RSA challenge
        rotation_type: 'static' or 'adaptive'
        n_trials: Number of independent trials
        n_candidates: Candidates per trial
        k: Resolution exponent for θ′(n,k)
        seed: Random seed
        
    Returns:
        Dictionary of profiling results
    """
    if challenge_name not in RSA_CHALLENGES:
        raise ValueError(f"Unknown challenge: {challenge_name}")
    
    challenge = RSA_CHALLENGES[challenge_name]
    N = challenge['N']
    p, q = challenge['p'], challenge['q']
    
    print(f"\n{'='*70}")
    print(f"Cranley-Patterson Profiling: {challenge_name} ({rotation_type.upper()})")
    print(f"{'='*70}")
    print(f"N = {N}")
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"Bits: {challenge['bits']}")
    print(f"Rotation: {rotation_type}, Trials: {n_trials}, Candidates/trial: {n_candidates}")
    print(f"k={k}, seed={seed}")
    print()
    
    # Storage for results
    trial_results = []
    timings = []
    
    # Run trials
    for trial_idx in range(n_trials):
        trial_seed = seed + trial_idx
        np.random.seed(trial_seed)
        
        # Create CP engine
        engine = CranleyPattersonEngine(
            dimension=1,
            seed=trial_seed,
            rotation_type=rotation_type,
            N=N
        )
        
        # Generate candidates
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
        metrics['rotation'] = engine.rotation.tolist()
        
        trial_results.append(metrics)
        timings.append(elapsed)
        
        if (trial_idx + 1) % 10 == 0:
            print(f"  Trial {trial_idx + 1}/{n_trials} complete")
    
    # Aggregate statistics
    variances = [r['variance'] for r in trial_results]
    mean_variance = np.mean(variances)
    std_variance = np.std(variances)
    
    # Bootstrap 95% CI
    n_bootstrap = 2000
    bootstrap_vars = []
    rng = np.random.RandomState(seed)
    for _ in range(n_bootstrap):
        resample = rng.choice(variances, size=len(variances), replace=True)
        bootstrap_vars.append(np.mean(resample))
    
    ci_lower = np.percentile(bootstrap_vars, 2.5)
    ci_upper = np.percentile(bootstrap_vars, 97.5)
    
    print(f"\n{'='*70}")
    print(f"CRANLEY-PATTERSON ({rotation_type.upper()}) RESULTS")
    print(f"{'='*70}")
    print(f"Mean Variance: {mean_variance:.6e} ± {std_variance:.6e}")
    print(f"95% CI: [{ci_lower:.6e}, {ci_upper:.6e}]")
    print(f"Mean Timing: {np.mean(timings):.4f}s ± {np.std(timings):.4f}s")
    print(f"Median Timing: {np.median(timings):.4f}s")
    print()
    
    return {
        'challenge': challenge_name,
        'configuration': {
            'n_trials': n_trials,
            'n_candidates': n_candidates,
            'k': k,
            'seed': seed,
            'engine': 'CranleyPattersonEngine',
            'rotation_type': rotation_type,
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
    """Run Cranley-Patterson profiling on all RSA challenges."""
    results = {}
    
    for challenge_name in ['RSA-100', 'RSA-129', 'RSA-155']:
        for rotation_type in ['static', 'adaptive']:
            key = f"{challenge_name}_{rotation_type}"
            
            try:
                result = profile_cranley_patterson(
                    challenge_name=challenge_name,
                    rotation_type=rotation_type,
                    n_trials=30,
                    n_candidates=1000,
                    k=0.3,
                    seed=42
                )
                results[key] = result
                
                # Save individual result
                output_file = f"../results/cp_{rotation_type}_{challenge_name.lower()}.json"
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"✓ Saved: {output_file}\n")
                
            except Exception as e:
                print(f"✗ Error profiling {key}: {e}\n")
                results[key] = {'error': str(e)}
    
    # Save combined results
    combined_file = "../results/cranley_patterson_all.json"
    with open(combined_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ All results saved to: {combined_file}")


if __name__ == "__main__":
    main()
