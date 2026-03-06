#!/usr/bin/env python3
"""
Auto-Tune Scaling Experiments
=============================

This script validates the R* scaling law described in PR #713:
- R* = 1.0 at k = 100
- R* = 1.5 at k = 10^6  
- R* = 31.5 at k = 10^100

It runs auto-tune experiments across multiple scales and analyzes the scaling behavior.
"""

import sys
import os
import json
import time
import argparse
from typing import List, Dict, Any
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from mpmath import mpf, log10

# Import the wave-knob scanner
sys.path.append(os.path.dirname(__file__))
from wave_knob_scanner import WaveKnobScanner

def run_scaling_experiment(k_values: List[str], precision: int = 50, 
                          wheel_modulus: int = 30, max_iterations: int = 100) -> Dict[str, Any]:
    """
    Run auto-tune experiments across multiple k values to study R* scaling.
    
    Args:
        k_values: List of k values to test (as strings to support scientific notation)
        precision: mpmath precision
        wheel_modulus: Wheel modulus for optimization
        max_iterations: Max auto-tune iterations per k
        
    Returns:
        Dictionary with experiment results and analysis
    """
    scanner = WaveKnobScanner(precision=precision, wheel_modulus=wheel_modulus)
    
    results = []
    start_time = time.time()
    
    print(f"Running auto-tune scaling experiment with {len(k_values)} k values...")
    
    for i, k_str in enumerate(k_values):
        print(f"  {i+1}/{len(k_values)}: k = {k_str}")
        
        try:
            k = mpf(k_str)
            result = scanner.auto_tune_scan(k, target_count=1, max_iterations=max_iterations)
            
            # Add log10(k) for scaling analysis
            result['log10_k'] = float(log10(k))
            results.append(result)
            
            print(f"    Locked: {result['locked']}, R*: {result['final_R']:.6f}, "
                  f"Iterations: {result['iterations']}")
            
        except Exception as e:
            print(f"    Error: {str(e)}")
            continue
    
    total_time = time.time() - start_time
    
    # Extract successful results for analysis
    successful_results = [r for r in results if r['locked']]
    
    analysis = {
        'total_experiments': len(k_values),
        'successful_convergences': len(successful_results),
        'convergence_rate': len(successful_results) / len(k_values) if k_values else 0,
        'total_time': total_time,
        'average_time_per_k': total_time / len(k_values) if k_values else 0
    }
    
    if successful_results:
        # Extract R* and log10(k) values for correlation analysis
        r_star_values = [r['final_R'] for r in successful_results]
        log10_k_values = [r['log10_k'] for r in successful_results]
        iteration_counts = [r['iterations'] for r in successful_results]
        
        # Compute scaling statistics
        analysis.update({
            'r_star_mean': np.mean(r_star_values),
            'r_star_std': np.std(r_star_values),
            'r_star_min': np.min(r_star_values),
            'r_star_max': np.max(r_star_values),
            'iterations_mean': np.mean(iteration_counts),
            'iterations_std': np.std(iteration_counts),
            'log10_k_range': [np.min(log10_k_values), np.max(log10_k_values)]
        })
        
        # Correlation analysis: R* vs log10(k)
        if len(r_star_values) >= 2:
            correlation, p_value = pearsonr(log10_k_values, r_star_values)
            analysis.update({
                'scaling_correlation': correlation,
                'scaling_p_value': p_value,
                'scaling_significant': p_value < 0.05,
                'scaling_strong': correlation >= 0.7
            })
        
        # Check specific PR #713 targets
        pr_targets = {
            100: 1.0,
            1000000: 1.5,
            # Note: 10^100 would be too large for practical testing
        }
        
        target_validation = {}
        for target_k, expected_r in pr_targets.items():
            # Find closest result
            closest_result = None
            min_diff = float('inf')
            for r in successful_results:
                k_diff = abs(r['k'] - target_k)
                if k_diff < min_diff:
                    min_diff = k_diff
                    closest_result = r
            
            if closest_result and min_diff / target_k < 0.1:  # Within 10% of target
                actual_r = closest_result['final_R']
                error = abs(actual_r - expected_r) / expected_r
                target_validation[target_k] = {
                    'expected_r': expected_r,
                    'actual_r': actual_r,
                    'relative_error': error,
                    'within_tolerance': error < 0.5  # 50% tolerance for validation
                }
        
        analysis['pr_target_validation'] = target_validation
    
    return {
        'experiment_info': {
            'k_values': k_values,
            'precision': precision,
            'wheel_modulus': wheel_modulus,
            'max_iterations': max_iterations
        },
        'results': results,
        'analysis': analysis
    }


def create_scaling_plot(experiment_data: Dict[str, Any], output_path: str = None):
    """
    Create R* scaling plot showing relationship between log10(k) and R*.
    
    Args:
        experiment_data: Results from run_scaling_experiment
        output_path: Output file path (None for display)
    """
    successful_results = [r for r in experiment_data['results'] if r['locked']]
    
    if len(successful_results) < 2:
        print("Not enough successful results for plotting")
        return
    
    log10_k_values = [r['log10_k'] for r in successful_results]
    r_star_values = [r['final_R'] for r in successful_results]
    iteration_counts = [r['iterations'] for r in successful_results]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot 1: R* vs log10(k)
    ax1.scatter(log10_k_values, r_star_values, c=iteration_counts, 
               cmap='viridis', s=50, alpha=0.7)
    ax1.set_xlabel('log10(k)')
    ax1.set_ylabel('R* (Resonance Ratio)')
    ax1.set_title('Wave-Knob R* Scaling Law')
    ax1.grid(True, alpha=0.3)
    
    # Add trendline if we have enough points
    if len(log10_k_values) >= 2:
        z = np.polyfit(log10_k_values, r_star_values, 1)
        p = np.poly1d(z)
        x_trend = np.linspace(min(log10_k_values), max(log10_k_values), 100)
        ax1.plot(x_trend, p(x_trend), 'r--', alpha=0.8, 
                label=f'Trend: R* = {z[0]:.3f}·log10(k) + {z[1]:.3f}')
        ax1.legend()
    
    # Add colorbar for iterations
    cbar = plt.colorbar(ax1.collections[0], ax=ax1)
    cbar.set_label('Convergence Iterations')
    
    # Plot 2: Convergence iterations vs log10(k)
    ax2.scatter(log10_k_values, iteration_counts, alpha=0.7, s=50)
    ax2.set_xlabel('log10(k)')
    ax2.set_ylabel('Convergence Iterations')
    ax2.set_title('Auto-Tune Convergence Efficiency')
    ax2.grid(True, alpha=0.3)
    
    # Add PR #713 reference points if available
    pr_targets = {100: 1.0, 1000000: 1.5}
    for target_k, expected_r in pr_targets.items():
        log_k = np.log10(target_k)
        if min(log10_k_values) <= log_k <= max(log10_k_values):
            ax1.axvline(log_k, color='red', linestyle=':', alpha=0.5)
            ax1.text(log_k, expected_r, f'PR#713\nk={target_k}\nR*={expected_r}', 
                    ha='center', va='bottom', fontsize=8, 
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Scaling plot saved to {output_path}")
    else:
        plt.show()


def main():
    """Main CLI interface for scaling experiments."""
    parser = argparse.ArgumentParser(description='Auto-Tune Scaling Experiments')
    
    parser.add_argument('--k-range', type=str, default='100,10000,5',
                       help='k range: start,stop,count (log-spaced)')
    parser.add_argument('--k-list', type=str, 
                       help='Specific k values: k1,k2,k3,...')
    parser.add_argument('--precision', type=int, default=50,
                       help='mpmath precision')
    parser.add_argument('--wheel', type=int, default=30, choices=[30, 210],
                       help='Wheel modulus')
    parser.add_argument('--max-iterations', type=int, default=100,
                       help='Max auto-tune iterations')
    parser.add_argument('--output', type=str, default='data/scaling_experiment.json',
                       help='Output JSON file')
    parser.add_argument('--plot', type=str, 
                       help='Output plot file (PNG/PDF)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Determine k values to test
    if args.k_list:
        k_values = args.k_list.split(',')
    else:
        try:
            start, stop, count = args.k_range.split(',')
            k_vals = np.logspace(np.log10(float(start)), np.log10(float(stop)), int(count))
            k_values = [f'{k:.0f}' if k < 1e6 else f'{k:.0e}' for k in k_vals]
        except ValueError:
            print("Error: Invalid k-range format. Use: start,stop,count")
            return 1
    
    if args.verbose:
        print(f"Testing k values: {k_values}")
    
    # Run scaling experiment
    experiment_data = run_scaling_experiment(
        k_values, 
        precision=args.precision,
        wheel_modulus=args.wheel,
        max_iterations=args.max_iterations
    )
    
    # Display results
    analysis = experiment_data['analysis']
    print(f"\nScaling Experiment Results:")
    print(f"  Total experiments: {analysis['total_experiments']}")
    print(f"  Successful convergences: {analysis['successful_convergences']}")
    print(f"  Convergence rate: {analysis['convergence_rate']:.1%}")
    print(f"  Total time: {analysis['total_time']:.2f}s")
    
    if 'r_star_mean' in analysis:
        print(f"  R* statistics:")
        print(f"    Mean: {analysis['r_star_mean']:.3f} ± {analysis['r_star_std']:.3f}")
        print(f"    Range: [{analysis['r_star_min']:.3f}, {analysis['r_star_max']:.3f}]")
        print(f"  Iterations: {analysis['iterations_mean']:.1f} ± {analysis['iterations_std']:.1f}")
        
        if 'scaling_correlation' in analysis:
            print(f"  R* vs log10(k) correlation: r = {analysis['scaling_correlation']:.3f} "
                  f"(p = {analysis['scaling_p_value']:.2e})")
            if analysis['scaling_significant']:
                print(f"    ✅ Correlation is statistically significant")
            if analysis['scaling_strong']:
                print(f"    ✅ Correlation is strong (r ≥ 0.7)")
        
        if 'pr_target_validation' in analysis:
            print(f"  PR #713 target validation:")
            for k, validation in analysis['pr_target_validation'].items():
                status = "✅" if validation['within_tolerance'] else "❌"
                print(f"    k={k}: Expected R*={validation['expected_r']}, "
                      f"Actual R*={validation['actual_r']:.3f} "
                      f"({validation['relative_error']:.1%} error) {status}")
    
    # Save results (convert numpy types to native Python for JSON serialization)
    def convert_numpy_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj
    
    experiment_data_serializable = convert_numpy_types(experiment_data)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(experiment_data_serializable, f, indent=2)
    print(f"\nResults saved to {args.output}")
    
    # Generate plot if requested
    if args.plot:
        os.makedirs(os.path.dirname(args.plot), exist_ok=True)
        create_scaling_plot(experiment_data, args.plot)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())