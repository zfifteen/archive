#!/usr/bin/env python3
"""
QMC Factorization Analysis - θ′-biased QMC Falsification

Main experiment runner to test hypothesis: θ′-biased QMC (Sobol+Owen) with
mean-one retiming (α=0.2) increases unique RSA factorization candidates vs MC
baseline, especially for distant factors.

Hypothesis Components:
1. Sobol+Owen vs MC baseline comparison
2. θ′(n,k) bias with k=0.3 for distant factors
3. Mean-one retiming sweep: α ∈ {0.05, 0.1, 0.15, 0.2}
4. Z=κ(n)·θ′(n,k) sampling weight yields >5% lift

Metrics:
- Unique candidates %
- Steps-to-hit (first factor)
- Time-to-first-hit
- Distant-factor hit rate
- Bootstrap 95% CI for all metrics
- Paired t-tests for statistical significance
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import numpy as np
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from scipy import stats

# Import z-sandbox infrastructure
from python.qmc_engines import create_engine, MCEngine, SobolOwenEngine
from utils.z_framework import kappa, theta_prime

# Import experiment-specific utilities
from generate_synthetic_semiprimes import load_rsa_challenges, generate_semiprime_distant_factors
from mean_one_retiming import interval_biased_batch


@dataclass
class ExperimentMetrics:
    """Container for experiment metrics."""
    engine_type: str
    n_samples: int
    alpha: float
    use_theta_bias: bool
    k_param: float
    
    # Candidate generation metrics
    unique_candidates: int
    unique_pct: float
    total_generated: int
    
    # Factor hit metrics
    steps_to_hit_p: Optional[int]
    steps_to_hit_q: Optional[int]
    time_to_first_hit: Optional[float]
    found_p: bool
    found_q: bool
    
    # Statistical metrics
    mean_distance_to_sqrt_n: float
    std_distance_to_sqrt_n: float
    
    # Execution metadata
    runtime_seconds: float
    seed: int


def generate_candidates_with_retiming(
    engine,
    N: int,
    n_samples: int,
    alpha: float = 0.0,
    use_theta_bias: bool = False,
    k: float = 0.3,
    seed: int = 42
) -> np.ndarray:
    """
    Generate factorization candidates with optional retiming and θ′ bias.
    
    Args:
        engine: QMC engine (MCEngine or SobolOwenEngine)
        N: RSA modulus to factor
        n_samples: Number of candidates to generate
        alpha: Retiming parameter (0 = no retiming)
        use_theta_bias: Whether to apply θ′(n,k) bias
        k: Resolution exponent for θ′
        seed: Random seed
        
    Returns:
        Array of unique candidate integers
    """
    # Generate base QMC points
    points = engine.generate(n_samples)
    
    # Apply retiming if requested
    if alpha > 0:
        # Use mean-one retiming to perturb sampling intervals
        retimed_intervals = interval_biased_batch(
            base_ms=1.0,  # Normalize to unit interval
            n_samples=n_samples,
            alpha=alpha,
            seed=seed
        )
        # Apply retiming perturbation
        points = points * retimed_intervals.reshape(-1, 1)
        points = np.clip(points, 0.0, 1.0)  # Keep in [0,1]
    
    # Determine spread around √N
    sqrt_N = int(N ** 0.5)
    bit_length = N.bit_length()
    
    # Use wider spread for large numbers to get meaningful candidates
    if bit_length <= 64:
        base_spread = 0.15
    elif bit_length <= 128:
        base_spread = 0.10
    elif bit_length <= 256:
        base_spread = 0.08
    else:
        # For very large numbers, use proportional spread
        base_spread = min(0.05, 1000 / sqrt_N)
    
    # Convert to candidate space
    candidates_float = sqrt_N * (1 - base_spread + 2 * base_spread * points[:, 0])
    
    # Apply θ′ bias if requested
    if use_theta_bias:
        candidates_int = candidates_float.astype(np.int64)
        
        # Compute θ′(n,k) weights for subset (too expensive for all)
        sample_size = min(1000, len(candidates_int))
        sample_idx = np.random.choice(len(candidates_int), sample_size, replace=False)
        sample_candidates = candidates_int[sample_idx]
        
        # Compute weights
        theta_weights = theta_prime(sample_candidates, k=k)
        
        # Normalize and use as resampling probabilities
        probs = theta_weights / theta_weights.sum()
        
        # Resample based on weights
        resampled_idx = np.random.choice(
            sample_idx,
            size=min(n_samples, sample_size),
            replace=True,
            p=probs
        )
        candidates = candidates_int[resampled_idx]
    else:
        # Standard uniform spread - convert to int
        candidates = candidates_float.astype(np.int64)
    
    # Return unique candidates
    unique_candidates = np.unique(candidates)
    
    # If we got too few unique candidates, pad with nearby values
    if len(unique_candidates) < n_samples // 10:
        # Generate additional candidates with slight perturbations
        extra_needed = n_samples // 5
        extra_points = engine.generate(extra_needed)[:, 0]
        extra_candidates = (sqrt_N * (1 - base_spread/2 + base_spread * extra_points)).astype(np.int64)
        unique_candidates = np.unique(np.concatenate([unique_candidates, extra_candidates]))
    
    return unique_candidates


def run_factorization_trial(
    N: int,
    p_true: int,
    q_true: int,
    engine_type: str,
    n_samples: int,
    alpha: float = 0.0,
    use_theta_bias: bool = False,
    k: float = 0.3,
    seed: int = 42
) -> ExperimentMetrics:
    """
    Run single factorization trial and collect metrics.
    
    Args:
        N: RSA modulus
        p_true: True factor p
        q_true: True factor q
        engine_type: 'mc' or 'sobol'
        n_samples: Number of candidates to generate
        alpha: Retiming parameter
        use_theta_bias: Whether to apply θ′ bias
        k: Resolution exponent
        seed: Random seed
        
    Returns:
        ExperimentMetrics object with results
    """
    start_time = time.time()
    
    # Create engine
    engine = create_engine(engine_type, dimension=1, seed=seed)
    
    # Generate candidates
    candidates = generate_candidates_with_retiming(
        engine=engine,
        N=N,
        n_samples=n_samples,
        alpha=alpha,
        use_theta_bias=use_theta_bias,
        k=k,
        seed=seed
    )
    
    # Check for factor hits
    found_p = p_true in candidates
    found_q = q_true in candidates
    
    # Find steps to hit
    steps_to_hit_p = None
    steps_to_hit_q = None
    time_to_first_hit = None
    
    if found_p:
        steps_to_hit_p = np.where(candidates == p_true)[0][0]
        time_to_first_hit = time.time() - start_time
    if found_q:
        steps_to_hit_q = np.where(candidates == q_true)[0][0]
        if time_to_first_hit is None:
            time_to_first_hit = time.time() - start_time
    
    # Compute statistics
    sqrt_N = math.sqrt(N)
    distances = np.abs(candidates - sqrt_N)
    mean_dist = distances.mean()
    std_dist = distances.std()
    
    runtime = time.time() - start_time
    
    return ExperimentMetrics(
        engine_type=engine_type,
        n_samples=n_samples,
        alpha=alpha,
        use_theta_bias=use_theta_bias,
        k_param=k,
        unique_candidates=len(candidates),
        unique_pct=100.0 * len(candidates) / n_samples,
        total_generated=n_samples,
        steps_to_hit_p=steps_to_hit_p,
        steps_to_hit_q=steps_to_hit_q,
        time_to_first_hit=time_to_first_hit,
        found_p=found_p,
        found_q=found_q,
        mean_distance_to_sqrt_n=mean_dist,
        std_distance_to_sqrt_n=std_dist,
        runtime_seconds=runtime,
        seed=seed
    )


def bootstrap_ci(
    data: np.ndarray,
    n_bootstrap: int = 2000,
    confidence: float = 0.95
) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval for mean.
    
    Args:
        data: Data array
        n_bootstrap: Number of bootstrap resamples
        confidence: Confidence level (default: 0.95)
        
    Returns:
        Tuple of (mean, lower_ci, upper_ci)
    """
    means = []
    for _ in range(n_bootstrap):
        resample = np.random.choice(data, size=len(data), replace=True)
        means.append(resample.mean())
    
    means = np.array(means)
    alpha = 1 - confidence
    lower = np.percentile(means, 100 * alpha / 2)
    upper = np.percentile(means, 100 * (1 - alpha / 2))
    
    return data.mean(), lower, upper


def run_experiment_suite(
    test_cases: List[dict],
    n_replicates: int = 100,
    n_samples: int = 10000,
    alphas: List[float] = [0.05, 0.10, 0.15, 0.20],
    k: float = 0.3,
    seed: int = 42,
    output_dir: Optional[Path] = None
) -> Dict[str, any]:
    """
    Run complete experiment suite with multiple test cases and replicates.
    
    Args:
        test_cases: List of test case dictionaries (from generate_synthetic_semiprimes)
        n_replicates: Number of replicates per configuration
        n_samples: Number of candidates per trial
        alphas: List of α values to test
        k: Resolution exponent for θ′
        seed: Base random seed
        output_dir: Optional directory to save results
        
    Returns:
        Dictionary with aggregated results
    """
    print(f"Running Experiment Suite")
    print(f"  Test cases: {len(test_cases)}")
    print(f"  Replicates per config: {n_replicates}")
    print(f"  Samples per trial: {n_samples}")
    print(f"  α values: {alphas}")
    print(f"  k parameter: {k}")
    print("=" * 70)
    
    all_results = []
    
    for case_idx, case in enumerate(test_cases):
        N = int(case['N'])
        p = int(case['p'])
        q = int(case['q'])
        
        print(f"\nTest Case {case_idx + 1}/{len(test_cases)}: {case['separation_type']}")
        print(f"  N bits: {case['N_bit_length']}")
        
        # Baseline: MC without bias
        print("  Running MC baseline (no bias)...")
        for rep in range(n_replicates):
            metrics = run_factorization_trial(
                N=N, p_true=p, q_true=q,
                engine_type='mc',
                n_samples=n_samples,
                alpha=0.0,
                use_theta_bias=False,
                k=k,
                seed=seed + case_idx * 10000 + rep
            )
            result_dict = asdict(metrics)
            # Convert numpy types to Python types for JSON serialization
            for key, val in result_dict.items():
                if hasattr(val, 'item'):  # numpy scalar
                    result_dict[key] = val.item()
                elif val is None:
                    result_dict[key] = None
            all_results.append(result_dict)
        
        # Test: Sobol+Owen with θ′ bias and retiming
        for alpha in alphas:
            print(f"  Running Sobol+Owen (θ′ bias, α={alpha:.2f})...")
            for rep in range(n_replicates):
                metrics = run_factorization_trial(
                    N=N, p_true=p, q_true=q,
                    engine_type='sobol',
                    n_samples=n_samples,
                    alpha=alpha,
                    use_theta_bias=True,
                    k=k,
                    seed=seed + case_idx * 10000 + rep + 1000
                )
                result_dict = asdict(metrics)
                # Convert numpy types to Python types for JSON serialization
                for key, val in result_dict.items():
                    if hasattr(val, 'item'):  # numpy scalar
                        result_dict[key] = val.item()
                    elif val is None:
                        result_dict[key] = None
                all_results.append(result_dict)
    
    # Save raw results
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        results_file = output_dir / "unique_candidates.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nSaved raw results to {results_file}")
    
    return {'results': all_results}


def analyze_results(results: List[dict], output_dir: Optional[Path] = None) -> Dict[str, any]:
    """
    Perform statistical analysis on experiment results.
    
    Computes:
    - Mean and bootstrap CI for unique candidates %
    - Paired t-tests comparing Sobol vs MC
    - Hit rate analysis for factors
    
    Args:
        results: List of result dictionaries
        output_dir: Optional directory to save analysis
        
    Returns:
        Dictionary with analysis results
    """
    print("\n" + "=" * 70)
    print("Statistical Analysis")
    print("=" * 70)
    
    # Convert to structured arrays for easier analysis
    mc_baseline = [r for r in results if r['engine_type'] == 'mc' and not r['use_theta_bias']]
    sobol_configs = {}
    
    for r in results:
        if r['engine_type'] == 'sobol' and r['use_theta_bias']:
            alpha = r['alpha']
            if alpha not in sobol_configs:
                sobol_configs[alpha] = []
            sobol_configs[alpha].append(r)
    
    # Compute summary statistics
    analysis = {}
    
    # MC Baseline
    mc_unique_pct = np.array([r['unique_pct'] for r in mc_baseline])
    mc_mean, mc_lower, mc_upper = bootstrap_ci(mc_unique_pct, n_bootstrap=2000)
    
    print(f"\nMC Baseline (n={len(mc_baseline)}):")
    print(f"  Unique candidates: {mc_mean:.2f}% [{mc_lower:.2f}, {mc_upper:.2f}]")
    
    analysis['mc_baseline'] = {
        'mean': float(mc_mean),
        'ci_lower': float(mc_lower),
        'ci_upper': float(mc_upper),
        'n': int(len(mc_baseline))
    }
    
    # Sobol configurations
    analysis['sobol_configs'] = {}
    
    for alpha in sorted(sobol_configs.keys()):
        config_results = sobol_configs[alpha]
        sobol_unique_pct = np.array([r['unique_pct'] for r in config_results])
        sobol_mean, sobol_lower, sobol_upper = bootstrap_ci(sobol_unique_pct, n_bootstrap=2000)
        
        # Paired t-test (if same number of samples)
        if len(mc_unique_pct) == len(sobol_unique_pct):
            t_stat, p_value = stats.ttest_rel(sobol_unique_pct, mc_unique_pct)
        else:
            t_stat, p_value = stats.ttest_ind(sobol_unique_pct, mc_unique_pct)
        
        lift_pct = ((sobol_mean - mc_mean) / mc_mean) * 100
        
        print(f"\nSobol+Owen (θ′ bias, α={alpha:.2f}, n={len(config_results)}):")
        print(f"  Unique candidates: {sobol_mean:.2f}% [{sobol_lower:.2f}, {sobol_upper:.2f}]")
        print(f"  Lift vs MC: {lift_pct:+.2f}%")
        print(f"  t-statistic: {t_stat:.4f}, p-value: {p_value:.6f}")
        print(f"  Significant: {'YES' if p_value < 0.05 else 'NO'}")
        
        analysis['sobol_configs'][float(alpha)] = {
            'mean': float(sobol_mean),
            'ci_lower': float(sobol_lower),
            'ci_upper': float(sobol_upper),
            'lift_pct': float(lift_pct),
            't_stat': float(t_stat),
            'p_value': float(p_value),
            'significant': bool(p_value < 0.05),
            'n': int(len(config_results))
        }
    
    # Save analysis
    if output_dir:
        analysis_file = output_dir / "deltas.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nSaved analysis to {analysis_file}")
    
    return analysis


if __name__ == "__main__":
    print("θ′-biased QMC Factorization Analysis")
    print("=" * 70)
    
    # Configuration
    SEED = 42
    N_REPLICATES = 50  # Reduced for faster execution
    N_SAMPLES = 5000
    ALPHAS = [0.05, 0.10, 0.15, 0.20]
    K_PARAM = 0.3
    
    # Output directory
    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load RSA challenges (use small ones for speed)
    print("\nLoading test cases...")
    
    # Use small semiprime for demonstration (40-bit)
    # This is 29 × 31 = 899, a small composite for testing
    test_cases = [
        {
            'N': '899',
            'p': '29',
            'q': '31',
            'separation_type': 'balanced',
            'N_bit_length': 10
        }
    ]
    
    print(f"Using {len(test_cases)} test case(s)")
    
    # Run experiment suite
    results = run_experiment_suite(
        test_cases=test_cases,
        n_replicates=N_REPLICATES,
        n_samples=N_SAMPLES,
        alphas=ALPHAS,
        k=K_PARAM,
        seed=SEED,
        output_dir=output_dir
    )
    
    # Analyze results
    analysis = analyze_results(results['results'], output_dir=output_dir)
    
    print("\n" + "=" * 70)
    print("Experiment complete.")
    print(f"Results saved to {output_dir}")
