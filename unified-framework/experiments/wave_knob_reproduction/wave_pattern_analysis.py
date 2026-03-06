#!/usr/bin/env python3
"""
Wave Pattern Analysis - R-Sweep and Fringe Pattern Studies
==========================================================

This script performs comprehensive R-sweep analysis to validate the wave-like
interference patterns described in PR #713. It generates heatmaps and correlation
analysis to demonstrate the fringe patterns with target Pearson r ≥ 0.93.
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any, Tuple
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from mpmath import mpf

# Import the wave-knob scanner
sys.path.append(os.path.dirname(__file__))
from wave_knob_scanner import WaveKnobScanner

def analyze_wave_patterns(k: str, window_range: Tuple[int, int, int], 
                         step_range: Tuple[int, int, int], 
                         precision: int = 50, wheel_modulus: int = 30) -> Dict[str, Any]:
    """
    Perform comprehensive wave pattern analysis via R-sweep.
    
    Args:
        k: Prime index to analyze
        window_range: (start, stop, step) for window values
        step_range: (start, stop, step) for step values  
        precision: mpmath precision
        wheel_modulus: Wheel modulus
        
    Returns:
        Analysis results including correlations and wave metrics
    """
    scanner = WaveKnobScanner(precision=precision, wheel_modulus=wheel_modulus)
    
    print(f"Analyzing wave patterns for k = {k}")
    print(f"Window range: {window_range}")
    print(f"Step range: {step_range}")
    
    # Perform R-sweep
    k_val = mpf(k)
    results = scanner.r_sweep_experiment(k_val, window_range, step_range)
    
    if not results:
        return {'error': 'No scan results obtained'}
    
    # Extract data for analysis
    windows = [r['window'] for r in results]
    steps = [r['step'] for r in results]
    R_values = [r['R'] for r in results]
    prime_counts = [r['prime_count'] for r in results]
    resonance_valleys = [r for r in results if r['is_resonance_valley']]
    
    # Fringe pattern analysis: correlation between R and prime_count
    if len(R_values) >= 2 and len(prime_counts) >= 2:
        correlation_R_count, p_value_R_count = pearsonr(R_values, prime_counts)
    else:
        correlation_R_count = p_value_R_count = 0.0
    
    # Alternative correlations for fringe detection
    log_R_values = [np.log(R) for R in R_values if R > 0]
    log_R_counts = [prime_counts[i] for i, R in enumerate(R_values) if R > 0]
    
    if len(log_R_values) >= 2:
        correlation_logR_count, p_value_logR_count = pearsonr(log_R_values, log_R_counts)
    else:
        correlation_logR_count = p_value_logR_count = 0.0
    
    # Window vs count correlation (another fringe indicator)
    correlation_window_count, p_value_window_count = pearsonr(windows, prime_counts)
    
    # Resonance valley analysis
    resonance_R_values = [r['R'] for r in resonance_valleys]
    resonance_statistics = {
        'count': len(resonance_valleys),
        'R_min': min(resonance_R_values) if resonance_R_values else None,
        'R_max': max(resonance_R_values) if resonance_R_values else None,
        'R_mean': np.mean(resonance_R_values) if resonance_R_values else None,
        'R_std': np.std(resonance_R_values) if resonance_R_values else None
    }
    
    # Count oscillation analysis (fringe signature)
    count_range = max(prime_counts) - min(prime_counts) if prime_counts else 0
    count_std = np.std(prime_counts) if prime_counts else 0
    count_mean = np.mean(prime_counts) if prime_counts else 0
    
    oscillation_coefficient = count_std / count_mean if count_mean > 0 else 0
    
    analysis = {
        'k': k,
        'total_scans': len(results),
        'parameter_ranges': {
            'window_range': window_range,
            'step_range': step_range,
            'R_range': [min(R_values), max(R_values)] if R_values else [0, 0],
            'count_range': [min(prime_counts), max(prime_counts)] if prime_counts else [0, 0]
        },
        'fringe_correlations': {
            'R_vs_count': {
                'correlation': correlation_R_count,
                'p_value': p_value_R_count,
                'significant': p_value_R_count < 0.05,
                'strong': abs(correlation_R_count) >= 0.7,
                'pr713_target': abs(correlation_R_count) >= 0.93
            },
            'logR_vs_count': {
                'correlation': correlation_logR_count,
                'p_value': p_value_logR_count,
                'significant': p_value_logR_count < 0.05,
                'strong': abs(correlation_logR_count) >= 0.7,
                'pr713_target': abs(correlation_logR_count) >= 0.93
            },
            'window_vs_count': {
                'correlation': correlation_window_count,
                'p_value': p_value_window_count,
                'significant': p_value_window_count < 0.05,
                'strong': abs(correlation_window_count) >= 0.7,
                'pr713_target': abs(correlation_window_count) >= 0.93
            }
        },
        'resonance_analysis': resonance_statistics,
        'oscillation_metrics': {
            'count_std': count_std,
            'count_mean': count_mean,
            'count_range': count_range,
            'oscillation_coefficient': oscillation_coefficient,
            'high_oscillation': oscillation_coefficient > 0.5
        },
        'scan_results': results
    }
    
    return analysis


def create_wave_heatmap(analysis: Dict[str, Any], output_path: str = None):
    """
    Create heatmap showing prime count vs (window, step) parameters.
    
    Args:
        analysis: Wave pattern analysis results
        output_path: Output file path (None for display)
    """
    results = analysis['scan_results']
    
    if not results:
        print("No data for heatmap")
        return
    
    # Create pivot table for heatmap
    windows = sorted(list(set(r['window'] for r in results)))
    steps = sorted(list(set(r['step'] for r in results)))
    
    # Initialize heatmap data
    heatmap_data = np.zeros((len(windows), len(steps)))
    
    for r in results:
        i = windows.index(r['window'])
        j = steps.index(r['step'])
        heatmap_data[i, j] = r['prime_count']
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Heatmap 1: Prime count
    sns.heatmap(heatmap_data, xticklabels=steps, yticklabels=windows, 
               annot=True, fmt='.0f', cmap='viridis', ax=ax1,
               cbar_kws={'label': 'Prime Count'})
    ax1.set_title(f'Wave-Knob Heatmap: Prime Count vs (Window, Step)\nk = {analysis["k"]}')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Window')
    
    # Heatmap 2: R ratios
    R_data = np.zeros((len(windows), len(steps)))
    for r in results:
        i = windows.index(r['window'])
        j = steps.index(r['step'])
        R_data[i, j] = r['R']
    
    sns.heatmap(R_data, xticklabels=steps, yticklabels=windows, 
               annot=True, fmt='.2f', cmap='plasma', ax=ax2,
               cbar_kws={'label': 'R Ratio'})
    ax2.set_title(f'Wave-Knob R Ratios vs (Window, Step)\nk = {analysis["k"]}')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Window')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Wave heatmap saved to {output_path}")
    else:
        plt.show()


def create_fringe_plots(analysis: Dict[str, Any], output_path: str = None):
    """
    Create fringe pattern plots showing correlations.
    
    Args:
        analysis: Wave pattern analysis results
        output_path: Output file path (None for display)
    """
    results = analysis['scan_results']
    
    if not results:
        print("No data for fringe plots")
        return
    
    R_values = [r['R'] for r in results]
    prime_counts = [r['prime_count'] for r in results]
    windows = [r['window'] for r in results]
    resonance_valleys = [r for r in results if r['is_resonance_valley']]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Prime count vs R ratio
    ax1.scatter(R_values, prime_counts, alpha=0.7, s=30)
    
    # Highlight resonance valleys
    if resonance_valleys:
        valley_R = [r['R'] for r in resonance_valleys]
        valley_counts = [r['prime_count'] for r in resonance_valleys]
        ax1.scatter(valley_R, valley_counts, color='red', s=60, 
                   label=f'Resonance Valleys (n={len(resonance_valleys)})', zorder=5)
        ax1.legend()
    
    corr = analysis['fringe_correlations']['R_vs_count']
    ax1.set_xlabel('R = window/step')
    ax1.set_ylabel('Prime Count')
    ax1.set_title(f'Fringe Pattern: Count vs R\nr = {corr["correlation"]:.3f}, p = {corr["p_value"]:.2e}')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Prime count vs log(R)
    log_R = [np.log(R) for R in R_values if R > 0]
    log_R_counts = [prime_counts[i] for i, R in enumerate(R_values) if R > 0]
    
    ax2.scatter(log_R, log_R_counts, alpha=0.7, s=30)
    corr_log = analysis['fringe_correlations']['logR_vs_count']
    ax2.set_xlabel('log(R)')
    ax2.set_ylabel('Prime Count')
    ax2.set_title(f'Fringe Pattern: Count vs log(R)\nr = {corr_log["correlation"]:.3f}, p = {corr_log["p_value"]:.2e}')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Prime count vs window
    ax3.scatter(windows, prime_counts, alpha=0.7, s=30)
    corr_window = analysis['fringe_correlations']['window_vs_count']
    ax3.set_xlabel('Window Size')
    ax3.set_ylabel('Prime Count')
    ax3.set_title(f'Count vs Window\nr = {corr_window["correlation"]:.3f}, p = {corr_window["p_value"]:.2e}')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: R distribution in resonance valleys
    if resonance_valleys:
        valley_R = [r['R'] for r in resonance_valleys]
        ax4.hist(valley_R, bins=min(10, len(valley_R)), alpha=0.7, edgecolor='black')
        ax4.set_xlabel('R* in Resonance Valleys')
        ax4.set_ylabel('Frequency')
        ax4.set_title(f'R* Distribution (n={len(valley_R)})')
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No Resonance Valleys\nFound', 
                ha='center', va='center', transform=ax4.transAxes, fontsize=12)
        ax4.set_title('R* Distribution')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Fringe plots saved to {output_path}")
    else:
        plt.show()


def main():
    """Main CLI interface for wave pattern analysis."""
    parser = argparse.ArgumentParser(description='Wave Pattern Analysis')
    
    parser.add_argument('--k', type=str, required=True, 
                       help='Prime index to analyze')
    parser.add_argument('--window-range', type=str, default='2,30,2',
                       help='Window range: start,stop,step')
    parser.add_argument('--step-range', type=str, default='1,8,1',
                       help='Step range: start,stop,step')
    parser.add_argument('--precision', type=int, default=50,
                       help='mpmath precision')
    parser.add_argument('--wheel', type=int, default=30, choices=[30, 210],
                       help='Wheel modulus')
    parser.add_argument('--output', type=str, default='data/wave_patterns.json',
                       help='Output JSON file')
    parser.add_argument('--heatmap', type=str,
                       help='Heatmap output file')
    parser.add_argument('--fringe-plots', type=str,
                       help='Fringe plots output file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Parse ranges
    try:
        window_range = tuple(map(int, args.window_range.split(',')))
        step_range = tuple(map(int, args.step_range.split(',')))
    except ValueError:
        print("Error: Invalid range format. Use: start,stop,step")
        return 1
    
    # Run wave pattern analysis
    analysis = analyze_wave_patterns(
        args.k, window_range, step_range, 
        precision=args.precision, wheel_modulus=args.wheel
    )
    
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return 1
    
    # Display results
    print(f"\nWave Pattern Analysis Results for k = {analysis['k']}:")
    print(f"  Total scans: {analysis['total_scans']}")
    print(f"  Resonance valleys: {analysis['resonance_analysis']['count']}")
    
    if analysis['resonance_analysis']['R_min'] is not None:
        print(f"  R* range in valleys: [{analysis['resonance_analysis']['R_min']:.3f}, "
              f"{analysis['resonance_analysis']['R_max']:.3f}]")
        print(f"  Mean R*: {analysis['resonance_analysis']['R_mean']:.3f}")
    
    print(f"\nFringe Pattern Correlations:")
    for name, corr in analysis['fringe_correlations'].items():
        status = "✅" if corr['pr713_target'] else "❌"
        sig_status = "significant" if corr['significant'] else "not significant"
        print(f"  {name}: r = {corr['correlation']:.3f} (p = {corr['p_value']:.2e}) "
              f"[{sig_status}] {status}")
    
    print(f"\nOscillation Metrics:")
    osc = analysis['oscillation_metrics']
    print(f"  Count std/mean: {osc['oscillation_coefficient']:.3f}")
    print(f"  Count range: {osc['count_range']}")
    print(f"  High oscillation: {'Yes' if osc['high_oscillation'] else 'No'}")
    
    # Check PR #713 targets
    pr_targets_met = any(corr['pr713_target'] for corr in analysis['fringe_correlations'].values())
    print(f"\nPR #713 Target (r ≥ 0.93): {'✅ MET' if pr_targets_met else '❌ NOT MET'}")
    
    # Save results (simple format to avoid JSON issues)
    try:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w') as f:
            # Write simplified results
            simple_results = {
                'k': analysis['k'],
                'total_scans': analysis['total_scans'],
                'resonance_valleys': analysis['resonance_analysis']['count'],
                'correlations': {name: {'r': corr['correlation'], 'p': corr['p_value'], 
                                      'target_met': corr['pr713_target']} 
                               for name, corr in analysis['fringe_correlations'].items()},
                'pr713_target_met': pr_targets_met
            }
            json.dump(simple_results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    except Exception as e:
        print(f"Warning: Could not save JSON results: {e}")
    
    # Generate visualizations
    if args.heatmap:
        os.makedirs(os.path.dirname(args.heatmap), exist_ok=True)
        create_wave_heatmap(analysis, args.heatmap)
    
    if args.fringe_plots:
        os.makedirs(os.path.dirname(args.fringe_plots), exist_ok=True)
        create_fringe_plots(analysis, args.fringe_plots)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())