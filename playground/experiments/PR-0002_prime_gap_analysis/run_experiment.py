#!/usr/bin/env python3
"""
Prime Gap Distribution Analysis - Main Experiment Runner

Runs complete statistical analysis of prime gaps at specified scale.
Tests hypotheses H-MAIN-A, H-MAIN-B, H-MAIN-C.
"""

import argparse
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from prime_generator import generate_primes
from gap_analysis import analyze_gaps
from distribution_tests import test_distributions
from autocorrelation import test_autocorrelation
from visualization import plot_qq, plot_acf, plot_gap_histogram, plot_pnt_deviation


def run_experiment(scale: float, output_dir: str = 'results') -> dict:
    """Run complete experiment at specified scale.
    
    Args:
        scale: Upper limit for prime generation (e.g., 1e6, 1e7, 1e8)
        output_dir: Directory for output files
        
    Returns:
        Dictionary with all analysis results
    """
    limit = int(scale)
    print(f"\n{'=' * 70}")
    print(f"Prime Gap Distribution Analysis - Scale: {limit:,}")
    print(f"{'=' * 70}\n")
    
    # Create output directories
    output_path = Path(output_dir)
    figures_path = output_path / 'figures'
    figures_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Generate primes
    print("Step 1: Generating primes...")
    primes = generate_primes(limit)
    print(f"Generated {len(primes):,} primes\n")
    
    # Step 2: Gap analysis (H-MAIN-A)
    print("Step 2: Testing H-MAIN-A (PNT Deviation)...")
    gap_results = analyze_gaps(primes)
    pnt_results = gap_results['pnt_analysis']
    print(f"  Overall mean gap/log(p): {pnt_results['overall_mean']:.6f}")
    print(f"  Regression slope: {pnt_results['slope']:.6f}")
    print(f"  R²: {pnt_results['r_squared']:.6f}")
    print(f"  p-value: {pnt_results['p_value']:.6f}")
    print(f"  Interpretation: {pnt_results['interpretation']}\n")
    
    # Step 3: Distribution testing (H-MAIN-B)
    print("Step 3: Testing H-MAIN-B (Lognormal Distribution)...")
    dist_results = test_distributions(primes)
    print(f"  Interpretation: {dist_results['interpretation']}")
    for band_name, results in dist_results['band_results'].items():
        if 'best_fit' in results:
            print(f"  Band {band_name}: best fit = {results['best_fit']}")
    print()
    
    # Step 4: Autocorrelation analysis (H-MAIN-C)
    print("Step 4: Testing H-MAIN-C (Autocorrelation)...")
    acf_results = test_autocorrelation(primes)
    print(f"  Ljung-Box Q: {acf_results['ljung_box_Q']:.6f}")
    print(f"  p-value: {acf_results['ljung_box_p']:.6f}")
    print(f"  Significant lags: {acf_results['significant_lags'][:5]}...")
    print(f"  Interpretation: {acf_results['interpretation']}\n")
    
    # Step 5: OEIS validation
    print("Step 5: OEIS Validation...")
    oeis_validation = gap_results['oeis_validation']
    for limit_val, results in oeis_validation.items():
        match_str = "✓" if results['matches'] else "✗"
        print(f"  {match_str} π({limit_val:,}): "
              f"gap={results['actual_gap']} (expected {results['expected_gap']}), "
              f"prime={results['actual_prime']} (expected {results['expected_prime']})")
    print()
    
    # Step 6: Generate visualizations
    print("Step 6: Generating visualizations...")
    gaps = gap_results['quantities']['gaps']
    normalized_gaps = gap_results['quantities']['normalized_gaps']
    
    # Q-Q plots for each band
    for band_name, band_results in dist_results['band_results'].items():
        if 'error' not in band_results:
            band_lower, band_upper = {
                '1e5_1e6': (10**5, 10**6),
                '1e6_1e7': (10**6, 10**7),
                '1e7_1e8': (10**7, 10**8),
            }[band_name]
            
            mask = (primes[:-1] >= band_lower) & (primes[:-1] < band_upper)
            band_gaps = gaps[mask]
            
            if len(band_gaps) > 0:
                plot_qq(band_gaps, band_name, 
                       output=str(figures_path / f'qq_plot_{band_name}.png'))
    
    # ACF plot
    plot_acf(gaps, acf_results['acf'], acf_results['confidence_band'],
            output=str(figures_path / 'acf_plot.png'))
    
    # Gap histogram
    plot_gap_histogram(gaps, output=str(figures_path / 'gap_histogram.png'))
    
    # PNT deviation plot
    plot_pnt_deviation(primes, normalized_gaps, pnt_results,
                      output=str(figures_path / 'pnt_deviation.png'))
    
    print("  Saved all plots to results/figures/\n")
    
    # Step 7: Save results
    print("Step 7: Saving results...")
    results = {
        'scale': limit,
        'n_primes': len(primes),
        'pnt_analysis': {
            'overall_mean': float(pnt_results['overall_mean']),
            'slope': float(pnt_results['slope']),
            'r_squared': float(pnt_results['r_squared']),
            'p_value': float(pnt_results['p_value']),
            'ci_lower': float(pnt_results['ci_lower']),
            'ci_upper': float(pnt_results['ci_upper']),
            'interpretation': pnt_results['interpretation'],
        },
        'distribution_analysis': {
            'interpretation': dist_results['interpretation'],
            'lognormal_count': dist_results['lognormal_count'],
            'exponential_count': dist_results['exponential_count'],
            'best_fits': dist_results['best_fits'],
        },
        'autocorrelation_analysis': {
            'ljung_box_Q': float(acf_results['ljung_box_Q']),
            'ljung_box_p': float(acf_results['ljung_box_p']),
            'n_significant_lags': len(acf_results['significant_lags']),
            'significant_lags': acf_results['significant_lags'][:10],
            'interpretation': acf_results['interpretation'],
        },
        'oeis_validation': {
            str(k): {
                'expected_gap': int(v['expected_gap']),
                'actual_gap': int(v['actual_gap']),
                'expected_prime': int(v['expected_prime']),
                'actual_prime': int(v['actual_prime']),
                'matches': bool(v['matches']),
            }
            for k, v in oeis_validation.items()
        }
    }
    
    results_file = output_path / f'analysis_results_{limit}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"  Saved results to {results_file}\n")
    
    # Summary
    print(f"{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Scale: {limit:,}")
    print(f"Primes: {len(primes):,}")
    print(f"\nH-MAIN-A (PNT): {pnt_results['interpretation']}")
    print(f"H-MAIN-B (Lognormal): {dist_results['interpretation']}")
    print(f"H-MAIN-C (Autocorrelation): {acf_results['interpretation']}")
    print(f"{'=' * 70}\n")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Prime Gap Distribution Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--scale',
        type=float,
        default=1e6,
        help='Upper limit for prime generation (default: 1e6)',
    )
    parser.add_argument(
        '--output',
        type=str,
        default='results',
        help='Output directory (default: results)',
    )
    
    args = parser.parse_args()
    
    # Run experiment
    run_experiment(args.scale, args.output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
