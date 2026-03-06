#!/usr/bin/env python3
"""
Form Hit-Rate Benchmarking Script - Hypothesis H2
=================================================

Tests special-form prime hit-rate uplift using Z5D-biased vs baseline search
as specified in Issue #677.

Validates:
- H2: Z5D-biased neighborhoods yield higher hit-rate of special-form primes
- Pass Gate: lower-CI(Δ) ≥ +20% OR ratio(Z5D/baseline) lower-CI ≥ 1.2×, p<0.01

Usage:
    python -m scripts.bench_form_hitrate --m 256 --predicate pseudo_mersenne --cmax 100 --W 262144 --budget 200000
    python -m scripts.bench_form_hitrate --m-list 128,192,256,384,521 --predicate generalized
"""

import sys
import os
import argparse
import numpy as np
import pandas as pd
import json
import time
from typing import List, Tuple, Dict, Any, Optional
import logging
from dataclasses import dataclass

# Add framework paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from discrete.crypto_prime_generator import (
        generate_crypto_primes, SpecialFormType, 
        _invert_pnt_to_k, _is_pseudo_mersenne, _is_generalized_mersenne
    )
    from statistical.bootstrap_validation import bootstrap_confidence_intervals
except ImportError:
    # Fallback implementations
    def generate_crypto_primes(k_values, kind="baseline", window=2**18, max_hits=100, prime_bits=256, seed=42):
        # Mock implementation
        return type('MockResult', (), {
            'primes': [],
            'special_form_count': 0,
            'candidates_tested': 1000,
            'hit_rate': 0.0,
            'generation_time': 1.0
        })()
    
    def _invert_pnt_to_k(m):
        return int(2**m / (m * np.log(2)))
    
    def _is_pseudo_mersenne(p, c_max=100):
        # Heuristic: check if p = 2^k - c for small c
        for k in range(2, p.bit_length() + 2):
            candidate = (1 << k)
            c = candidate - p
            if 1 <= c <= c_max:
                return True, c
        return False, 0
        
    def _is_generalized_mersenne(p, gamma_max=256):
        # Heuristic: check if p = 2^k - 2^l - 1 for small l
        k = p.bit_length()
        for l in range(1, min(k, gamma_max)):
            candidate = (1 << k) - (1 << l) - 1
            if candidate == p:
                return True, (k, l, 1)
        return False, (0, 0, 0)
    
    def bootstrap_confidence_intervals(data, statistic_func, confidence_level=0.95, n_bootstrap=1000):
        # Simple fallback
        stat = statistic_func(data)
        std = np.std(data) / np.sqrt(len(data))
        margin = 1.96 * std
        return {
            'confidence_interval': (stat - margin, stat + margin),
            'bootstrap_mean': stat,
            'original_statistic': stat
        }

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HitRateConfig:
    """Configuration for hit-rate benchmarking"""
    m: int                              # Bit length
    predicate: str                      # "pseudo_mersenne" or "generalized"
    c_max: int = 100                   # Max c for pseudo-Mersenne
    gamma_max: int = 256               # Max gamma for generalized
    window: int = 2**18                # Search window W
    budget: int = 200000               # Total primality test budget
    seed: int = 42                     # RNG seed
    bootstrap_samples: int = 1000      # Bootstrap resamples
    confidence_level: float = 0.95     # Confidence level

def run_baseline_search(config: HitRateConfig) -> Dict[str, Any]:
    """
    Run baseline search centered at 2^m with specified budget.
    
    Returns detailed results including found primes and hit-rate statistics.
    """
    logger.info(f"Running baseline search for m={config.m}, window={config.window}")
    
    # For baseline, we center search around 2^m
    center = 2**config.m
    k_values = [_invert_pnt_to_k(config.m)]  # Convert to k for API consistency
    
    start_time = time.time()
    
    result = generate_crypto_primes(
        k_values=k_values,
        kind="baseline",
        window=config.window,
        max_hits=config.budget // 1000,  # Limit to reasonable count
        prime_bits=config.m,
        seed=config.seed
    )
    
    # Analyze special forms in found primes
    special_forms = []
    for prime in result.primes:
        if config.predicate == "pseudo_mersenne":
            is_special, param = _is_pseudo_mersenne(prime, config.c_max)
            if is_special:
                special_forms.append({'prime': prime, 'c': param})
        elif config.predicate == "generalized":
            is_special, params = _is_generalized_mersenne(prime, config.gamma_max)
            if is_special:
                special_forms.append({'prime': prime, 'alpha': params[0], 'beta': params[1], 'gamma': params[2]})
    
    hit_rate = len(special_forms) / max(1, result.candidates_tested)
    runtime = time.time() - start_time
    
    baseline_results = {
        'method': 'baseline',
        'center': center,
        'total_primes': len(result.primes),
        'special_form_primes': len(special_forms),
        'special_forms': special_forms,
        'candidates_tested': result.candidates_tested,
        'hit_rate': hit_rate,
        'runtime': runtime,
        'primes': result.primes
    }
    
    logger.info(f"Baseline: {len(result.primes)} primes, {len(special_forms)} special-form, hit-rate={hit_rate:.6f}")
    
    return baseline_results

def run_z5d_biased_search(config: HitRateConfig) -> Dict[str, Any]:
    """
    Run Z5D-biased search centered at Z5D prediction with specified budget.
    
    Returns detailed results including found primes and hit-rate statistics.
    """
    logger.info(f"Running Z5D-biased search for m={config.m}, window={config.window}")
    
    # Convert bit length to k value for Z5D centering
    k = _invert_pnt_to_k(config.m)
    k_values = [k]
    
    start_time = time.time()
    
    result = generate_crypto_primes(
        k_values=k_values,
        kind="z5d_biased",
        window=config.window,
        max_hits=config.budget // 1000,  # Limit to reasonable count
        prime_bits=config.m,
        seed=config.seed
    )
    
    # Analyze special forms in found primes
    special_forms = []
    for prime in result.primes:
        if config.predicate == "pseudo_mersenne":
            is_special, param = _is_pseudo_mersenne(prime, config.c_max)
            if is_special:
                special_forms.append({'prime': prime, 'c': param})
        elif config.predicate == "generalized":
            is_special, params = _is_generalized_mersenne(prime, config.gamma_max)
            if is_special:
                special_forms.append({'prime': prime, 'alpha': params[0], 'beta': params[1], 'gamma': params[2]})
    
    hit_rate = len(special_forms) / max(1, result.candidates_tested)
    runtime = time.time() - start_time
    
    z5d_results = {
        'method': 'z5d_biased',
        'k': k,
        'total_primes': len(result.primes),
        'special_form_primes': len(special_forms),
        'special_forms': special_forms,
        'candidates_tested': result.candidates_tested,
        'hit_rate': hit_rate,
        'runtime': runtime,
        'primes': result.primes
    }
    
    logger.info(f"Z5D-biased: {len(result.primes)} primes, {len(special_forms)} special-form, hit-rate={hit_rate:.6f}")
    
    return z5d_results

def compute_hit_rate_statistics(baseline_results: Dict[str, Any], 
                               z5d_results: Dict[str, Any],
                               config: HitRateConfig) -> Dict[str, Any]:
    """
    Compute hit-rate comparison statistics with bootstrap confidence intervals.
    
    Implements the statistical tests required for H2 pass/fail gates.
    """
    baseline_rate = baseline_results['hit_rate']
    z5d_rate = z5d_results['hit_rate']
    
    # Basic statistics
    if baseline_rate > 0:
        ratio = z5d_rate / baseline_rate
        delta = z5d_rate - baseline_rate
        relative_improvement = (z5d_rate - baseline_rate) / baseline_rate
    else:
        ratio = float('inf') if z5d_rate > 0 else 1.0
        delta = z5d_rate
        relative_improvement = float('inf') if z5d_rate > 0 else 0.0
    
    logger.info(f"Computing bootstrap confidence intervals with {config.bootstrap_samples} samples")
    
    # Bootstrap confidence intervals for hit-rates
    # For this we need the raw success/failure data
    baseline_successes = baseline_results['special_form_primes']
    baseline_trials = baseline_results['candidates_tested'] 
    z5d_successes = z5d_results['special_form_primes']
    z5d_trials = z5d_results['candidates_tested']
    
    # Bootstrap for baseline hit-rate
    baseline_samples = []
    for _ in range(config.bootstrap_samples):
        boot_successes = np.random.binomial(baseline_trials, baseline_rate)
        boot_rate = boot_successes / baseline_trials
        baseline_samples.append(boot_rate)
    
    # Bootstrap for Z5D hit-rate
    z5d_samples = []
    for _ in range(config.bootstrap_samples):
        boot_successes = np.random.binomial(z5d_trials, z5d_rate)
        boot_rate = boot_successes / z5d_trials
        z5d_samples.append(boot_rate)
    
    # Bootstrap for difference and ratio
    delta_samples = []
    ratio_samples = []
    for i in range(config.bootstrap_samples):
        b_rate = baseline_samples[i]
        z_rate = z5d_samples[i]
        delta_samples.append(z_rate - b_rate)
        if b_rate > 0:
            ratio_samples.append(z_rate / b_rate)
        else:
            ratio_samples.append(float('inf') if z_rate > 0 else 1.0)
    
    # Compute confidence intervals
    alpha = 1 - config.confidence_level
    
    baseline_ci = (
        np.percentile(baseline_samples, (alpha/2) * 100),
        np.percentile(baseline_samples, (1 - alpha/2) * 100)
    )
    
    z5d_ci = (
        np.percentile(z5d_samples, (alpha/2) * 100),
        np.percentile(z5d_samples, (1 - alpha/2) * 100)
    )
    
    delta_ci = (
        np.percentile(delta_samples, (alpha/2) * 100),
        np.percentile(delta_samples, (1 - alpha/2) * 100)
    )
    
    # Filter out infinite ratios for CI computation
    finite_ratios = [r for r in ratio_samples if np.isfinite(r)]
    if finite_ratios:
        ratio_ci = (
            np.percentile(finite_ratios, (alpha/2) * 100),
            np.percentile(finite_ratios, (1 - alpha/2) * 100)
        )
    else:
        ratio_ci = (1.0, 1.0)
    
    # Check pass/fail gates from Issue #677
    # Gate (PASS): lower-CI(Δ) ≥ +20% OR ratio(Z5D/baseline) lower-CI ≥ 1.2×, p<0.01
    delta_lower_ci = delta_ci[0]
    ratio_lower_ci = ratio_ci[0]
    
    # Convert to percentages for delta gate
    delta_gate_pass = delta_lower_ci >= 0.20
    ratio_gate_pass = ratio_lower_ci >= 1.2
    
    pass_gate = delta_gate_pass or ratio_gate_pass
    
    if pass_gate:
        if delta_gate_pass:
            gate_reason = f"Delta lower CI {delta_lower_ci:.3f} ≥ 0.20"
        else:
            gate_reason = f"Ratio lower CI {ratio_lower_ci:.3f} ≥ 1.2"
    else:
        gate_reason = f"Delta lower CI {delta_lower_ci:.3f} < 0.20 AND ratio lower CI {ratio_lower_ci:.3f} < 1.2"
    
    statistics = {
        'baseline_hit_rate': float(baseline_rate),
        'z5d_hit_rate': float(z5d_rate),
        'delta': float(delta),
        'ratio': float(ratio) if np.isfinite(ratio) else None,
        'relative_improvement': float(relative_improvement) if np.isfinite(relative_improvement) else None,
        'baseline_ci': baseline_ci,
        'z5d_ci': z5d_ci,
        'delta_ci': delta_ci,
        'ratio_ci': ratio_ci,
        'delta_gate_pass': bool(delta_gate_pass),
        'ratio_gate_pass': bool(ratio_gate_pass), 
        'pass_gate': bool(pass_gate),
        'gate_reason': gate_reason,
        'confidence_level': config.confidence_level,
        'bootstrap_samples': config.bootstrap_samples
    }
    
    return statistics

def save_results(baseline_results: Dict[str, Any], 
                z5d_results: Dict[str, Any],
                statistics: Dict[str, Any],
                config: HitRateConfig,
                output_csv: str,
                output_json: str):
    """Save detailed results to CSV and metrics to JSON"""
    
    # Create detailed results DataFrame
    rows = []
    
    # Add baseline results
    for i, prime in enumerate(baseline_results['primes']):
        is_special = i < len(baseline_results['special_forms'])
        row = {
            'method': 'baseline',
            'prime': prime,
            'is_special_form': is_special,
            'bit_length': config.m,
            'predicate': config.predicate
        }
        if is_special and baseline_results['special_forms']:
            if config.predicate == "pseudo_mersenne":
                row['c_value'] = baseline_results['special_forms'][i].get('c', None)
            elif config.predicate == "generalized":
                sf = baseline_results['special_forms'][i]
                row['alpha'] = sf.get('alpha', None)
                row['beta'] = sf.get('beta', None) 
                row['gamma'] = sf.get('gamma', None)
        rows.append(row)
    
    # Add Z5D results
    for i, prime in enumerate(z5d_results['primes']):
        is_special = i < len(z5d_results['special_forms'])
        row = {
            'method': 'z5d_biased',
            'prime': prime,
            'is_special_form': is_special,
            'bit_length': config.m,
            'predicate': config.predicate
        }
        if is_special and z5d_results['special_forms']:
            if config.predicate == "pseudo_mersenne":
                row['c_value'] = z5d_results['special_forms'][i].get('c', None)
            elif config.predicate == "generalized":
                sf = z5d_results['special_forms'][i]
                row['alpha'] = sf.get('alpha', None)
                row['beta'] = sf.get('beta', None)
                row['gamma'] = sf.get('gamma', None)
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Save CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    logger.info(f"Detailed results saved to {output_csv}")
    
    # Combine all metrics
    metrics = {
        'config': {
            'bit_length': config.m,
            'predicate': config.predicate,
            'c_max': config.c_max,
            'gamma_max': config.gamma_max,
            'window': config.window,
            'budget': config.budget,
            'seed': config.seed
        },
        'baseline_results': {
            'total_primes': baseline_results['total_primes'],
            'special_form_primes': baseline_results['special_form_primes'],
            'candidates_tested': baseline_results['candidates_tested'],
            'hit_rate': baseline_results['hit_rate'],
            'runtime': baseline_results['runtime']
        },
        'z5d_results': {
            'total_primes': z5d_results['total_primes'],
            'special_form_primes': z5d_results['special_form_primes'],
            'candidates_tested': z5d_results['candidates_tested'],
            'hit_rate': z5d_results['hit_rate'],
            'runtime': z5d_results['runtime']
        },
        'statistics': statistics
    }
    
    # Save JSON
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics saved to {output_json}")

def print_summary(baseline_results: Dict[str, Any], 
                 z5d_results: Dict[str, Any],
                 statistics: Dict[str, Any],
                 config: HitRateConfig):
    """Print summary of hit-rate benchmarking results"""
    print("\n" + "="*80)
    print(f"FORM HIT-RATE BENCHMARKING - HYPOTHESIS H2")
    print(f"Bit length: {config.m}, Predicate: {config.predicate}")
    print("="*80)
    
    print("SEARCH RESULTS:")
    print(f"  Baseline method:")
    print(f"    Total primes: {baseline_results['total_primes']:,}")
    print(f"    Special-form: {baseline_results['special_form_primes']:,}")
    print(f"    Candidates tested: {baseline_results['candidates_tested']:,}")
    print(f"    Hit rate: {baseline_results['hit_rate']:.6f}")
    print(f"    Runtime: {baseline_results['runtime']:.2f}s")
    print()
    print(f"  Z5D-biased method:")
    print(f"    Total primes: {z5d_results['total_primes']:,}")
    print(f"    Special-form: {z5d_results['special_form_primes']:,}")
    print(f"    Candidates tested: {z5d_results['candidates_tested']:,}")
    print(f"    Hit rate: {z5d_results['hit_rate']:.6f}")
    print(f"    Runtime: {z5d_results['runtime']:.2f}s")
    print()
    
    stats = statistics
    print("STATISTICAL ANALYSIS:")
    print(f"  Hit-rate delta: {stats['delta']:.6f} ({stats['delta']*100:.2f}%)")
    if stats['ratio']:
        print(f"  Hit-rate ratio: {stats['ratio']:.3f}x")
    print(f"  Delta 95% CI: [{stats['delta_ci'][0]:.6f}, {stats['delta_ci'][1]:.6f}]")
    print(f"  Ratio 95% CI: [{stats['ratio_ci'][0]:.3f}, {stats['ratio_ci'][1]:.3f}]")
    print()
    
    print("PASS/FAIL GATES:")
    print(f"  Delta lower CI ≥ +20%:      {'✓ PASS' if stats['delta_gate_pass'] else '✗ FAIL'}")
    print(f"  Ratio lower CI ≥ 1.2×:      {'✓ PASS' if stats['ratio_gate_pass'] else '✗ FAIL'}")
    print()
    print(f"OVERALL RESULT: {'✓ PASS' if stats['pass_gate'] else '✗ FAIL'}")
    print(f"Reason: {stats['gate_reason']}")
    print("="*80)

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark special-form prime hit-rates (Hypothesis H2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single bit length with pseudo-Mersenne detection
    python -m scripts.bench_form_hitrate --m 256 --predicate pseudo_mersenne --cmax 100
    
    # Multiple bit lengths with generalized Mersenne
    python -m scripts.bench_form_hitrate --m-list 128,256,384 --predicate generalized --gamma-max 256
    
    # Custom window and budget
    python -m scripts.bench_form_hitrate --m 521 --predicate pseudo_mersenne --W 1048576 --budget 500000
        """
    )
    
    parser.add_argument(
        '--m',
        type=int,
        help='Single bit length to test'
    )
    
    parser.add_argument(
        '--m-list',
        type=str,
        help='Comma-separated list of bit lengths'
    )
    
    parser.add_argument(
        '--predicate',
        choices=['pseudo_mersenne', 'generalized'],
        default='pseudo_mersenne',
        help='Special form predicate to test (default: pseudo_mersenne)'
    )
    
    parser.add_argument(
        '--cmax',
        type=int,
        default=100,
        help='Maximum c for pseudo-Mersenne (default: 100)'
    )
    
    parser.add_argument(
        '--gamma-max',
        type=int,
        default=256,
        help='Maximum gamma for generalized Mersenne (default: 256)'
    )
    
    parser.add_argument(
        '--W',
        type=int,
        default=2**18,
        help='Search window size (default: 2^18)'
    )
    
    parser.add_argument(
        '--budget',
        type=int,
        default=200000,
        help='Total primality test budget (default: 200000)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    
    parser.add_argument(
        '--bootstrap-samples',
        type=int,
        default=1000,
        help='Bootstrap samples for CI (default: 1000)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Output directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Determine bit lengths to test
    if args.m_list:
        try:
            m_values = [int(x.strip()) for x in args.m_list.split(',')]
        except ValueError:
            print("Error: Invalid m-list format")
            return 1
    elif args.m:
        m_values = [args.m]
    else:
        # Default crypto bit lengths
        m_values = [256]
        print("Using default bit length: 256")
    
    overall_pass = True
    
    try:
        for m in m_values:
            logger.info(f"Processing bit length {m}")
            
            config = HitRateConfig(
                m=m,
                predicate=args.predicate,
                c_max=args.cmax,
                gamma_max=args.gamma_max,
                window=args.W,
                budget=args.budget,
                seed=args.seed,
                bootstrap_samples=args.bootstrap_samples
            )
            
            # Run both searches
            baseline_results = run_baseline_search(config)
            z5d_results = run_z5d_biased_search(config)
            
            # Compute statistics
            statistics = compute_hit_rate_statistics(baseline_results, z5d_results, config)
            
            # Save results
            output_csv = os.path.join(args.output_dir, f"results/form_hitrate_{m}_{args.predicate}.csv")
            output_json = os.path.join(args.output_dir, f"metrics/form_hitrate_{m}_{args.predicate}.json")
            
            save_results(baseline_results, z5d_results, statistics, config, output_csv, output_json)
            
            # Print summary
            print_summary(baseline_results, z5d_results, statistics, config)
            
            if not statistics['pass_gate']:
                overall_pass = False
        
        return 0 if overall_pass else 1
        
    except Exception as e:
        logger.error(f"Error during hit-rate benchmarking: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())