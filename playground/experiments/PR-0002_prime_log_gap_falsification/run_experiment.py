#!/usr/bin/env python3
"""
Prime Log-Gap Falsification Experiment - Main Runner

This script executes the full experiment across all scales (10^6, 10^7, 10^8)
and generates comprehensive results.

Author: GitHub Copilot
Date: December 2025
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np

from prime_generator import generate_primes_to_limit, compute_log_gaps, KNOWN_PI_VALUES
from log_gap_analysis import (
    compute_descriptive_stats,
    compute_quintile_analysis,
    compute_decile_analysis,
    compute_scale_comparison,
    generate_summary_dataframe
)
from distribution_tests import (
    fit_distributions,
    compare_distributions,
    compute_skewness_kurtosis_check
)
from autocorrelation import compute_autocorrelation_analysis
from visualization import (
    plot_log_gap_histogram,
    plot_qq_lognormal,
    plot_decay_trend,
    plot_acf_pacf,
    plot_scale_comparison
)


def run_phase(scale, results_dir, verbose=True, autocorr_mode='none', max_lag=40, subsample_rate=None):
    """
    Run a single phase of the experiment.
    
    Args:
        scale: Upper bound for primes (e.g., 10**6)
        results_dir: Directory to save results
        verbose: Print progress
        autocorr_mode: Autocorrelation test mode ('none', 'ljungbox', 'ljungbox-fixed', 'ljungbox-subsample')
        max_lag: Maximum lag for Ljung-Box test
        subsample_rate: Subsampling rate for ljungbox-subsample mode
        
    Returns:
        Dictionary with all analysis results
    """
    phase_name = f"10^{int(np.log10(scale))}"
    if verbose:
        print(f"\n{'='*70}")
        print(f"PHASE: {phase_name} (Generating primes up to {scale:,})")
        print(f"{'='*70}")
    
    results = {
        'scale': scale,
        'phase_name': phase_name,
        'timestamp': datetime.now().isoformat()
    }
    
    # 1. Generate primes
    if verbose:
        print(f"\n[1/6] Generating primes...")
    start_time = time.time()
    primes = generate_primes_to_limit(scale, validate=True)
    gen_time = time.time() - start_time
    
    expected_count = KNOWN_PI_VALUES.get(scale, None)
    actual_count = len(primes)
    
    if verbose:
        print(f"  π({scale:,}) = {actual_count:,}")
        if expected_count:
            print(f"  Expected: {expected_count:,} ✓")
        print(f"  Time: {gen_time:.2f}s")
    
    results['prime_generation'] = {
        'count': actual_count,
        'expected': expected_count,
        'time_seconds': gen_time,
        'validation_passed': actual_count == expected_count if expected_count else True
    }
    
    # 2. Compute log-gaps
    if verbose:
        print(f"\n[2/6] Computing log-gaps...")
    data = compute_log_gaps(primes)
    log_gaps = data['log_gaps']
    
    if verbose:
        print(f"  Log-gap count: {len(log_gaps):,}")
        print(f"  Range: [{log_gaps.min():.6f}, {log_gaps.max():.6f}]")
    
    # 3. Descriptive statistics
    if verbose:
        print(f"\n[3/6] Computing descriptive statistics...")
    desc_stats = compute_descriptive_stats(log_gaps)
    results['descriptive'] = desc_stats
    
    if verbose:
        print(f"  Mean: {desc_stats['mean']:.6f}")
        print(f"  Std: {desc_stats['std']:.6f}")
        print(f"  Skewness: {desc_stats['skewness']:.4f}")
        print(f"  Excess Kurtosis: {desc_stats['kurtosis']:.4f}")
    
    # 4. Quintile/Decile analysis (Tests T1, T2)
    if verbose:
        print(f"\n[4/6] Running quintile/decile analysis (T1, T2)...")
    quintile = compute_quintile_analysis(log_gaps)
    decile = compute_decile_analysis(log_gaps)
    results['quintile'] = quintile
    results['decile'] = decile
    
    if verbose:
        print(f"  Quintile means: {[f'{m:.6f}' for m in quintile['bin_means']]}")
        print(f"  Decay ratio (Q1/Q5): {quintile['decay_ratio']:.2f}")
        print(f"  Slope: {quintile['slope']:.4e}")
        print(f"  R²: {quintile['r_squared']:.4f}")
        print(f"  p-value: {quintile['p_value']:.4e}")
        print(f"  F1 Falsified: {quintile['f1_falsified']}")
    
    # 5. Distribution tests (Tests T3, T4, T7, T8)
    if verbose:
        print(f"\n[5/6] Running distribution tests (T3, T4, T7, T8)...")
    dist_fits = fit_distributions(log_gaps)
    dist_comparison = compare_distributions(dist_fits)
    skew_kurt = compute_skewness_kurtosis_check(log_gaps)
    
    results['distribution'] = dist_fits
    results['distribution_comparison'] = dist_comparison
    results['skewness_kurtosis'] = skew_kurt
    
    if verbose:
        print(f"  Best fit: {dist_comparison['best_fit']} (KS={dist_comparison['best_ks']:.4f})")
        print(f"  Normal KS: {dist_comparison['normal_ks']:.4f}")
        print(f"  Log-normal KS: {dist_comparison['lognormal_ks']:.4f}")
        print(f"  KS ratio (Normal/Lognormal): {dist_comparison['ks_ratio_normal_lognormal']:.2f}")
        print(f"  F2 Falsified (normal better): {dist_comparison['f2_falsified']}")
        print(f"  F5 Falsified (normal-like skew/kurt): {skew_kurt['f5_falsified']}")
    
    # 6. Autocorrelation tests (Tests T5, T6)
    if verbose:
        print(f"\n[6/6] Running autocorrelation tests (T5, T6)...")
        print(f"  Mode: {autocorr_mode}")
    
    # Determine whether to run Ljung-Box based on mode
    run_ljungbox = autocorr_mode != 'none'
    
    # Set subsample parameter based on mode
    subsample = None
    if autocorr_mode == 'ljungbox-subsample' and subsample_rate:
        subsample = int(len(log_gaps) * subsample_rate) if subsample_rate < 1.0 else int(subsample_rate)
    
    # Run autocorrelation analysis with optional Ljung-Box
    acf_results = compute_autocorrelation_analysis(
        log_gaps, 
        nlags=20,
        run_ljungbox=run_ljungbox,
        max_lag=max_lag,
        subsample=subsample
    )
    
    # Build results dict with optional fields
    results['autocorrelation'] = {
        'nlags': acf_results['nlags'],
        'acf': acf_results['acf'].tolist() if hasattr(acf_results['acf'], 'tolist') else list(acf_results['acf']),
        'significant_lags': acf_results['significant_lags'],
        'has_short_range_structure': acf_results['has_short_range_structure'],
        'ljungbox_status': acf_results['ljungbox_status'],
        'autocorr_mode': autocorr_mode
    }
    
    # Add Ljung-Box results only if evaluated
    if run_ljungbox and acf_results['ljungbox_all_p_above_005'] is not None:
        results['autocorrelation']['ljungbox_all_p_above_005'] = acf_results['ljungbox_all_p_above_005']
        results['autocorrelation']['f4_falsified'] = acf_results['f4_falsified']
    else:
        results['autocorrelation']['ljungbox_all_p_above_005'] = None
        results['autocorrelation']['f4_falsified'] = None
    
    if verbose:
        print(f"  Significant lags: {acf_results['significant_lags']}")
        print(f"  Has short-range structure: {acf_results['has_short_range_structure']}")
        if run_ljungbox:
            print(f"  Ljung-Box all p > 0.05: {acf_results['ljungbox_all_p_above_005']}")
            print(f"  F4 Falsified (white noise): {acf_results['f4_falsified']}")
        else:
            print(f"  Ljung-Box: not evaluated (autocorr mode = {autocorr_mode})")

    
    # Generate figures
    if verbose:
        print(f"\nGenerating figures...")
    
    figures_dir = os.path.join(results_dir, 'figures')
    os.makedirs(figures_dir, exist_ok=True)
    
    scale_str = f"1e{int(np.log10(scale))}"
    
    plot_log_gap_histogram(
        log_gaps, 
        os.path.join(figures_dir, f'log_gap_histogram_{scale_str}.png'),
        f'(N={scale:,})'
    )
    
    plot_qq_lognormal(
        log_gaps,
        os.path.join(figures_dir, f'qq_plot_{scale_str}.png'),
        f'(N={scale:,})'
    )
    
    plot_decay_trend(
        quintile,
        os.path.join(figures_dir, f'decay_trend_{scale_str}.png'),
        f'(N={scale:,})'
    )
    
    plot_acf_pacf(
        acf_results,
        os.path.join(figures_dir, f'acf_pacf_{scale_str}.png'),
        f'(N={scale:,})'
    )
    
    return results


def summarize_falsification(all_results):
    """
    Summarize falsification status across all scales.
    
    Args:
        all_results: Dictionary mapping scale to results
        
    Returns:
        Dictionary with falsification summary
    """
    summary = {
        'F1': {'description': 'Non-decreasing quintile trend', 'falsified': False, 'scales': []},
        'F2': {'description': 'Normal fits better than log-normal', 'falsified': False, 'scales': []},
        'F4': {'description': 'White noise (no autocorrelation)', 'falsified': False, 'scales': [], 'evaluated': False},
        'F5': {'description': 'Normal-like skewness/kurtosis', 'falsified': False, 'scales': []},
        'F6': {'description': 'Scale-dependent reversals', 'falsified': False, 'scales': []},
    }
    
    for scale, results in all_results.items():
        if results['quintile']['f1_falsified']:
            summary['F1']['falsified'] = True
            summary['F1']['scales'].append(scale)
        
        if results['distribution_comparison']['f2_falsified']:
            summary['F2']['falsified'] = True
            summary['F2']['scales'].append(scale)
        
        # F4 only evaluated if Ljung-Box was run
        if results['autocorrelation']['f4_falsified'] is not None:
            summary['F4']['evaluated'] = True
            if results['autocorrelation']['f4_falsified']:
                summary['F4']['falsified'] = True
                summary['F4']['scales'].append(scale)
        
        if results['skewness_kurtosis']['f5_falsified']:
            summary['F5']['falsified'] = True
            summary['F5']['scales'].append(scale)
    
    # F6: Check scale consistency
    scales = sorted(all_results.keys())
    if len(scales) >= 2:
        slopes = [all_results[s]['quintile']['slope'] for s in scales]
        if not all(s < 0 for s in slopes):
            summary['F6']['falsified'] = True
            summary['F6']['scales'] = scales
    
    # Overall conclusion
    any_falsified = any(f['falsified'] for f in summary.values())
    summary['hypothesis_falsified'] = any_falsified
    summary['hypothesis_supported'] = not any_falsified
    
    return summary


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Prime Log-Gap Falsification Experiment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Default fast run (no autocorrelation test - recommended for large scales):
  python3 run_experiment.py --scales 1e6,1e7 --autocorr none

  # Run with Ljung-Box test (slower, O(n²) cost):
  python3 run_experiment.py --scales 1e6 --autocorr ljungbox --max-lag 50

  # Run with fixed small lag for bounded cost:
  python3 run_experiment.py --scales 1e6,1e7 --autocorr ljungbox-fixed --max-lag 40

  # Run on subsample for approximate test at scale:
  python3 run_experiment.py --scales 1e7 --autocorr ljungbox-subsample --subsample-rate 100000
        '''
    )
    
    parser.add_argument(
        '--scales',
        type=str,
        default='1e6,1e7,1e8',
        help='Comma-separated list of scales to test (e.g., "1e6,1e7,1e8"). Default: "1e6,1e7,1e8"'
    )
    
    parser.add_argument(
        '--autocorr',
        type=str,
        choices=['none', 'ljungbox', 'ljungbox-fixed', 'ljungbox-subsample'],
        default='none',
        help='''Autocorrelation test mode (default: none).
        - none: Skip Ljung-Box test (fast, recommended for scale > 1e7).
        - ljungbox: Run standard Ljung-Box test (O(n²), slow at scale).
        - ljungbox-fixed: Run with fixed small max_lag for bounded cost.
        - ljungbox-subsample: Run on subsample (approximate test).
        '''
    )
    
    parser.add_argument(
        '--max-lag',
        type=int,
        default=40,
        help='Maximum lag for Ljung-Box test (default: 40). Ignored if --autocorr=none.'
    )
    
    parser.add_argument(
        '--subsample-rate',
        type=float,
        default=None,
        help='Subsampling rate for ljungbox-subsample mode. If < 1.0, treated as fraction; if >= 1, treated as count. Example: 0.1 or 100000'
    )
    
    parser.add_argument(
        '--bins',
        type=int,
        default=50,
        help='Number of bins for trend analysis (default: 50)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducible subsampling (default: 42)'
    )
    
    return parser.parse_args()


def main():
    """Run the full experiment."""
    args = parse_arguments()
    
    print("=" * 70)
    print("PRIME LOG-GAP FALSIFICATION EXPERIMENT")
    print("PR-0002")
    print("=" * 70)
    print(f"\nStart time: {datetime.now().isoformat()}")
    print(f"\nConfiguration:")
    print(f"  Scales: {args.scales}")
    print(f"  Autocorrelation mode: {args.autocorr}")
    if args.autocorr != 'none':
        print(f"  Max lag: {args.max_lag}")
        if args.autocorr == 'ljungbox-subsample' and args.subsample_rate:
            print(f"  Subsample rate: {args.subsample_rate}")
    else:
        print(f"  Ljung-Box test: DISABLED (default for performance)")
        print(f"  Note: Autocorrelation claims require --autocorr=ljungbox")
    
    # Setup directories
    base_dir = os.path.dirname(__file__)
    results_dir = os.path.join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Parse scales
    scales = [int(float(s)) for s in args.scales.split(',')]
    
    all_results = {}
    
    # Run all phases
    for scale in scales:
        results = run_phase(
            scale, 
            results_dir, 
            verbose=True,
            autocorr_mode=args.autocorr,
            max_lag=args.max_lag,
            subsample_rate=args.subsample_rate
        )
        all_results[scale] = results
    
    # Cross-scale comparison
    print(f"\n{'='*70}")
    print("CROSS-SCALE COMPARISON")
    print(f"{'='*70}")
    
    scale_comparison = compute_scale_comparison(all_results)
    print(f"  Directional consistency: {scale_comparison['directional_consistent']}")
    print(f"  Decay consistency: {scale_comparison['decay_consistent']}")
    print(f"  F6 Falsified: {scale_comparison['f6_falsified']}")
    
    # Generate comparison plot
    plot_scale_comparison(
        all_results,
        os.path.join(results_dir, 'figures', 'scale_comparison.png')
    )
    
    # Falsification summary
    print(f"\n{'='*70}")
    print("FALSIFICATION SUMMARY")
    print(f"{'='*70}")
    
    falsification = summarize_falsification(all_results)
    
    for f_id, f_data in falsification.items():
        if f_id.startswith('F'):
            if f_id == 'F4' and not f_data.get('evaluated', True):
                status = "NOT EVALUATED (autocorr=none)"
                print(f"  {f_id}: {f_data['description']} - {status}")
            else:
                status = "FALSIFIED" if f_data['falsified'] else "NOT FALSIFIED"
                print(f"  {f_id}: {f_data['description']} - {status}")
    
    print(f"\n  {'='*50}")
    if falsification['hypothesis_falsified']:
        print("  CONCLUSION: HYPOTHESIS IS FALSIFIED")
    else:
        if not falsification['F4']['evaluated']:
            print("  CONCLUSION: HYPOTHESIS IS SUPPORTED (not proven)")
            print("  NOTE: Autocorrelation (F4) not evaluated. Use --autocorr=ljungbox to verify.")
        else:
            print("  CONCLUSION: HYPOTHESIS IS SUPPORTED (not proven)")
    print(f"  {'='*50}")
    
    # Save results
    results_file = os.path.join(results_dir, 'experiment_results.json')
    
    # Convert numpy types to Python types for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(v) for v in obj]
        return obj
    
    serializable_results = {
        'all_results': {str(k): convert_to_serializable(v) for k, v in all_results.items()},
        'falsification_summary': convert_to_serializable(falsification),
        'scale_comparison': convert_to_serializable(scale_comparison)
    }
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    # Generate CSV summaries
    for scale, results in all_results.items():
        df = generate_summary_dataframe(results)
        csv_file = os.path.join(results_dir, f'summary_1e{int(np.log10(scale))}.csv')
        df.to_csv(csv_file, index=False)
        print(f"Summary saved to: {csv_file}")
    
    print(f"\nEnd time: {datetime.now().isoformat()}")
    print(f"\n{'='*70}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*70}")
    
    return falsification['hypothesis_supported']


if __name__ == "__main__":
    supported = main()
    sys.exit(0 if supported else 1)
