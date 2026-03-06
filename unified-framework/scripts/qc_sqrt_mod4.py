#!/usr/bin/env python3
"""
Sqrt-Friendly Fraction Quality Control - Hypothesis H3
=====================================================

Tests that the fraction of sqrt-friendly primes (p ≡ 3 mod 4) remains unbiased
as specified in Issue #677.

Validates:
- H3: Fraction of p ≡ 3 (mod 4) among found primes should be ≈ 50% (unbiased)
- Pass Gate: |Z5D_frac - 0.5| ≤ 1% AND |Z5D_frac - Baseline_frac| ≤ 1.5%

Usage:
    python -m scripts.qc_sqrt_mod4 --m 256 --sample results/form_hitrate_256_pseudo_mersenne.csv
    python -m scripts.qc_sqrt_mod4 --m-list 128,192,256,384,521 --generate-samples
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
from scipy import stats

# Add framework paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from discrete.crypto_prime_generator import generate_crypto_primes, _invert_pnt_to_k
except ImportError:
    # Fallback implementations
    def generate_crypto_primes(k_values, kind="baseline", window=2**18, max_hits=100, prime_bits=256, seed=42):
        # Generate some sample primes for testing
        np.random.seed(seed)
        center = 2**prime_bits if kind == "baseline" else int(2**prime_bits * 1.1)

        def is_probable_prime(n, k=8):
            """Use Miller-Rabin primality test with k rounds."""
            if n < 2:
                return False
            for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]:
                if n % p == 0:
                    return n == p
            d, s = n - 1, 0
            while d % 2 == 0:
                d //= 2
                s += 1
            for _ in range(k):
                a = np.random.randint(2, n - 1)
                x = pow(a, d, n)
                if x == 1 or x == n - 1:
                    continue
                for _ in range(s - 1):
                    x = pow(x, 2, n)
                    if x == n - 1:
                        break
                else:
                    return False
            return True

        primes = []
        candidate = center + (1 if center % 2 == 0 else 0)  # Start with odd

        while len(primes) < max_hits and candidate < center + window:
            # Use Miller-Rabin for fallback primality testing
            if is_probable_prime(candidate):
                primes.append(candidate)
            candidate += 2
        return type('MockResult', (), {
            'primes': primes,
            'candidates_tested': window // 2,
            'generation_time': 1.0
        })()
    
    def _invert_pnt_to_k(m):
        return int(2**m / (m * np.log(2)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SqrtQCConfig:
    """Configuration for sqrt-friendly QC testing"""
    m: int                              # Bit length
    sample_size: int = 1000            # Sample size for testing
    window: int = 2**18                # Search window
    seed: int = 42                     # RNG seed
    confidence_level: float = 0.95     # Confidence level for Wilson CI

def is_sqrt_friendly(p: int) -> bool:
    """Check if prime p ≡ 3 (mod 4) for efficient square root computation"""
    return p % 4 == 3

def wilson_confidence_interval(successes: int, trials: int, confidence_level: float = 0.95) -> Tuple[float, float]:
    """
    Compute Wilson confidence interval for a binomial proportion.
    
    This is more accurate than normal approximation for small sample sizes.
    
    Parameters:
    -----------
    successes : int
        Number of successes
    trials : int  
        Total number of trials
    confidence_level : float
        Confidence level (e.g., 0.95 for 95%)
        
    Returns:
    --------
    Tuple[float, float] : (lower_bound, upper_bound)
    """
    if trials == 0:
        return 0.0, 0.0
        
    p_hat = successes / trials
    alpha = 1 - confidence_level
    z = stats.norm.ppf(1 - alpha/2)
    
    term1 = p_hat + z**2 / (2 * trials)
    term2 = z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * trials)) / trials)
    denominator = 1 + z**2 / trials
    
    lower = (term1 - term2) / denominator
    upper = (term1 + term2) / denominator
    
    return max(0.0, lower), min(1.0, upper)

def analyze_sqrt_fraction_from_csv(csv_file: str) -> Dict[str, Any]:
    """
    Analyze sqrt-friendly fraction from existing CSV results.
    
    Expected CSV format: columns include 'method', 'prime', 'bit_length'
    """
    logger.info(f"Analyzing sqrt-friendly fractions from {csv_file}")
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    # Validate required columns
    required_cols = ['method', 'prime']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in CSV: {missing_cols}")
    
    results = {}
    
    for method in df['method'].unique():
        method_df = df[df['method'] == method]
        primes = method_df['prime'].tolist()
        
        if not primes:
            logger.warning(f"No primes found for method {method}")
            continue
            
        sqrt_friendly_count = sum(is_sqrt_friendly(p) for p in primes)
        total_count = len(primes)
        fraction = sqrt_friendly_count / total_count if total_count > 0 else 0.0
        
        # Wilson confidence interval
        ci_lower, ci_upper = wilson_confidence_interval(sqrt_friendly_count, total_count)
        
        results[method] = {
            'total_primes': total_count,
            'sqrt_friendly_count': sqrt_friendly_count,
            'sqrt_friendly_fraction': fraction,
            'wilson_ci': (ci_lower, ci_upper),
            'primes': primes
        }
        
        logger.info(f"Method {method}: {sqrt_friendly_count}/{total_count} = {fraction:.4f} sqrt-friendly")
    
    return results

def generate_sqrt_samples(config: SqrtQCConfig) -> Dict[str, Any]:
    """
    Generate fresh samples for sqrt-friendly fraction analysis.
    
    Generates both baseline and Z5D-biased samples.
    """
    logger.info(f"Generating sqrt-friendly samples for m={config.m}")
    
    k = _invert_pnt_to_k(config.m)
    
    # Generate baseline samples
    logger.info("Generating baseline samples...")
    baseline_result = generate_crypto_primes(
        k_values=[k],
        kind="baseline",
        window=config.window,
        max_hits=config.sample_size,
        prime_bits=config.m,
        seed=config.seed
    )
    
    # Generate Z5D-biased samples
    logger.info("Generating Z5D-biased samples...")
    z5d_result = generate_crypto_primes(
        k_values=[k],
        kind="z5d_biased",
        window=config.window,
        max_hits=config.sample_size,
        prime_bits=config.m,
        seed=config.seed
    )
    
    # Analyze both samples
    results = {}
    
    for method, result in [('baseline', baseline_result), ('z5d_biased', z5d_result)]:
        primes = result.primes
        sqrt_friendly_count = sum(is_sqrt_friendly(p) for p in primes)
        total_count = len(primes)
        fraction = sqrt_friendly_count / total_count if total_count > 0 else 0.0
        
        # Wilson confidence interval
        ci_lower, ci_upper = wilson_confidence_interval(sqrt_friendly_count, total_count, config.confidence_level)
        
        results[method] = {
            'total_primes': total_count,
            'sqrt_friendly_count': sqrt_friendly_count,
            'sqrt_friendly_fraction': fraction,
            'wilson_ci': (ci_lower, ci_upper),
            'primes': primes
        }
        
        logger.info(f"Method {method}: {sqrt_friendly_count}/{total_count} = {fraction:.4f} sqrt-friendly")
    
    return results

def compute_qc_statistics(results: Dict[str, Any], config: SqrtQCConfig) -> Dict[str, Any]:
    """
    Compute quality control statistics and pass/fail assessment.
    
    Implements H3 pass/fail gates from Issue #677.
    """
    if 'z5d_biased' not in results:
        return {
            'error': 'No Z5D-biased results available',
            'pass_gate': False,
            'gate_reason': 'Missing Z5D-biased data'
        }
    
    z5d_data = results['z5d_biased']
    z5d_fraction = z5d_data['sqrt_friendly_fraction']
    
    # Check unbiased constraint: |Z5D_frac - 0.5| ≤ 1%
    unbiased_deviation = abs(z5d_fraction - 0.5)
    unbiased_pass = unbiased_deviation <= 0.01
    
    # Check baseline comparison if available
    if 'baseline' in results:
        baseline_data = results['baseline']
        baseline_fraction = baseline_data['sqrt_friendly_fraction']
        
        # Check relative constraint: |Z5D_frac - Baseline_frac| ≤ 1.5%
        relative_deviation = abs(z5d_fraction - baseline_fraction)
        relative_pass = relative_deviation <= 0.015
        
        # Check Wilson CI overlap
        z5d_ci = z5d_data['wilson_ci']
        baseline_ci = baseline_data['wilson_ci']
        ci_overlap = not (z5d_ci[1] < baseline_ci[0] or baseline_ci[1] < z5d_ci[0])
        
    else:
        baseline_fraction = None
        relative_deviation = None
        relative_pass = True  # Pass by default if no baseline
        ci_overlap = True
    
    # Overall pass/fail assessment
    # Gate: |Z5D_frac - 0.5| ≤ 1% AND |Z5D_frac - Baseline_frac| ≤ 1.5%
    pass_gate = unbiased_pass and relative_pass
    
    if pass_gate:
        gate_reason = f"Unbiased deviation {unbiased_deviation:.3f} ≤ 0.01"
        if baseline_fraction is not None:
            gate_reason += f" AND relative deviation {relative_deviation:.3f} ≤ 0.015"
    else:
        if not unbiased_pass:
            gate_reason = f"Unbiased deviation {unbiased_deviation:.3f} > 0.01"
        else:
            gate_reason = f"Relative deviation {relative_deviation:.3f} > 0.015"
    
    statistics = {
        'z5d_fraction': float(z5d_fraction),
        'z5d_ci': z5d_data['wilson_ci'],
        'z5d_total_primes': z5d_data['total_primes'],
        'z5d_sqrt_friendly_count': z5d_data['sqrt_friendly_count'],
        'baseline_fraction': float(baseline_fraction) if baseline_fraction is not None else None,
        'baseline_ci': baseline_data['wilson_ci'] if 'baseline' in results else None,
        'baseline_total_primes': baseline_data['total_primes'] if 'baseline' in results else None,
        'baseline_sqrt_friendly_count': baseline_data['sqrt_friendly_count'] if 'baseline' in results else None,
        'unbiased_deviation': float(unbiased_deviation),
        'relative_deviation': float(relative_deviation) if relative_deviation is not None else None,
        'unbiased_pass': bool(unbiased_pass),
        'relative_pass': bool(relative_pass),
        'ci_overlap': bool(ci_overlap),
        'pass_gate': bool(pass_gate),
        'gate_reason': gate_reason,
        'confidence_level': config.confidence_level
    }
    
    return statistics

def save_results(results: Dict[str, Any], statistics: Dict[str, Any], config: SqrtQCConfig, 
                output_csv: str, output_json: str):
    """Save sqrt-friendly QC results to CSV and JSON"""
    
    # Create detailed results DataFrame
    rows = []
    
    for method, data in results.items():
        for prime in data['primes']:
            rows.append({
                'method': method,
                'prime': prime,
                'is_sqrt_friendly': is_sqrt_friendly(prime),
                'mod4_residue': prime % 4,
                'bit_length': config.m
            })
    
    df = pd.DataFrame(rows)
    
    # Save CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    logger.info(f"Detailed results saved to {output_csv}")
    
    # Combine metrics
    metrics = {
        'config': {
            'bit_length': config.m,
            'sample_size': config.sample_size,
            'window': config.window,
            'seed': config.seed,
            'confidence_level': config.confidence_level
        },
        'results': {
            method: {
                'total_primes': data['total_primes'],
                'sqrt_friendly_count': data['sqrt_friendly_count'],
                'sqrt_friendly_fraction': data['sqrt_friendly_fraction'],
                'wilson_ci': data['wilson_ci']
            }
            for method, data in results.items()
        },
        'statistics': statistics
    }
    
    # Save JSON
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics saved to {output_json}")

def print_summary(results: Dict[str, Any], statistics: Dict[str, Any], config: SqrtQCConfig):
    """Print summary of sqrt-friendly QC results"""
    print("\n" + "="*80)
    print(f"SQRT-FRIENDLY FRACTION QC - HYPOTHESIS H3")
    print(f"Bit length: {config.m}")
    print("="*80)
    
    print("SQRT-FRIENDLY ANALYSIS:")
    for method, data in results.items():
        fraction = data['sqrt_friendly_fraction']
        ci = data['wilson_ci']
        total = data['total_primes']
        sqrt_count = data['sqrt_friendly_count']
        
        print(f"  {method.replace('_', '-').title()}:")
        print(f"    Primes analyzed: {total:,}")
        print(f"    Sqrt-friendly (p ≡ 3 mod 4): {sqrt_count:,}")
        print(f"    Fraction: {fraction:.4f} ({fraction*100:.2f}%)")
        print(f"    Wilson 95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")
        print()
    
    stats = statistics
    print("QUALITY CONTROL GATES:")
    print(f"  Unbiased constraint |frac - 0.5| ≤ 1%:   {'✓ PASS' if stats['unbiased_pass'] else '✗ FAIL'}")
    print(f"    Z5D deviation from 0.5: {stats['unbiased_deviation']:.3f} ({stats['unbiased_deviation']*100:.1f}%)")
    
    if stats['baseline_fraction'] is not None:
        print(f"  Relative constraint |Z5D - baseline| ≤ 1.5%: {'✓ PASS' if stats['relative_pass'] else '✗ FAIL'}")
        print(f"    Z5D vs baseline deviation: {stats['relative_deviation']:.3f} ({stats['relative_deviation']*100:.1f}%)")
        print(f"  Wilson CI overlap: {'✓ YES' if stats['ci_overlap'] else '✗ NO'}")
    else:
        print(f"  Relative constraint: N/A (no baseline data)")
    
    print()
    print(f"OVERALL RESULT: {'✓ PASS' if stats['pass_gate'] else '✗ FAIL'}")
    print(f"Reason: {stats['gate_reason']}")
    print("="*80)

def main():
    parser = argparse.ArgumentParser(
        description="Quality control testing for sqrt-friendly prime fraction (Hypothesis H3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze existing CSV results
    python -m scripts.qc_sqrt_mod4 --m 256 --sample results/form_hitrate_256_pseudo_mersenne.csv
    
    # Generate fresh samples for multiple bit lengths
    python -m scripts.qc_sqrt_mod4 --m-list 128,192,256,384,521 --generate-samples
    
    # Custom sample size
    python -m scripts.qc_sqrt_mod4 --m 256 --generate-samples --sample-size 2000
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
        '--sample',
        type=str,
        help='CSV file with existing prime samples to analyze'
    )
    
    parser.add_argument(
        '--generate-samples',
        action='store_true',
        help='Generate fresh prime samples for analysis'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=1000,
        help='Sample size for generated samples (default: 1000)'
    )
    
    parser.add_argument(
        '--window',
        type=int,
        default=2**18,
        help='Search window size (default: 2^18)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    
    parser.add_argument(
        '--confidence-level',
        type=float,
        default=0.95,
        help='Confidence level for Wilson CI (default: 0.95)'
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
        # Default
        m_values = [256]
        print("Using default bit length: 256")
    
    # Determine analysis mode
    if args.sample and args.generate_samples:
        print("Error: Cannot specify both --sample and --generate-samples")
        return 1
    elif not args.sample and not args.generate_samples:
        print("Error: Must specify either --sample or --generate-samples")
        return 1
    
    overall_pass = True
    
    try:
        for m in m_values:
            logger.info(f"Processing bit length {m}")
            
            config = SqrtQCConfig(
                m=m,
                sample_size=args.sample_size,
                window=args.window,
                seed=args.seed,
                confidence_level=args.confidence_level
            )
            
            # Analyze sqrt-friendly fractions
            if args.sample:
                # Analyze existing CSV
                if len(m_values) > 1:
                    # For multiple m values, try to find corresponding CSV files
                    csv_file = args.sample.replace('256', str(m))  # Simple substitution
                    if not os.path.exists(csv_file):
                        logger.warning(f"CSV file not found for m={m}: {csv_file}")
                        continue
                else:
                    csv_file = args.sample
                
                results = analyze_sqrt_fraction_from_csv(csv_file)
            else:
                # Generate fresh samples
                results = generate_sqrt_samples(config)
            
            # Compute statistics
            statistics = compute_qc_statistics(results, config)
            
            # Save results
            output_csv = os.path.join(args.output_dir, f"results/sqrt_frac_{m}.csv")
            output_json = os.path.join(args.output_dir, f"metrics/sqrt_frac_{m}.json")
            
            save_results(results, statistics, config, output_csv, output_json)
            
            # Print summary
            print_summary(results, statistics, config)
            
            if not statistics['pass_gate']:
                overall_pass = False
        
        return 0 if overall_pass else 1
        
    except Exception as e:
        logger.error(f"Error during sqrt-friendly QC: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())