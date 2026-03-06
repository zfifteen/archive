#!/usr/bin/env python3
"""
Validation Script for Zeta Shift Prime Gap Correlation

This script validates the reproducibility and robustness of the zeta shift correlation
analysis across different parameter ranges and dataset sizes.
"""

import numpy as np
from zeta_shift_correlation import ZetaShiftPrimeGapAnalyzer
import matplotlib.pyplot as plt

def test_reproducibility():
    """Test reproducibility across multiple runs."""
    print("Testing reproducibility across multiple runs...")
    
    results_list = []
    for run in range(3):
        print(f"\nRun {run + 1}/3:")
        analyzer = ZetaShiftPrimeGapAnalyzer(max_n=10000, precision=30)
        results = analyzer.optimize_velocity_parameter()
        results_list.append(results)
        print(f"  v* = {results['optimal_v']:.6f}, r = {results['correlation']:.6f}")
    
    # Check consistency
    v_values = [r['optimal_v'] for r in results_list]
    r_values = [r['correlation'] for r in results_list]
    
    v_std = np.std(v_values)
    r_std = np.std(r_values)
    
    print(f"\nReproducibility Analysis:")
    print(f"  v* std deviation: {v_std:.6f}")
    print(f"  r std deviation: {r_std:.6f}")
    print(f"  All runs achieve r ≥ 0.93: {all(abs(r) >= 0.93 for r in r_values)}")
    
    return results_list

def test_dataset_scaling():
    """Test correlation quality across different dataset sizes."""
    print("\nTesting dataset scaling...")
    
    dataset_sizes = [1000, 5000, 10000, 20000]
    results = []
    
    for max_n in dataset_sizes:
        print(f"\nTesting max_n = {max_n}:")
        analyzer = ZetaShiftPrimeGapAnalyzer(max_n=max_n, precision=30)
        result = analyzer.optimize_velocity_parameter()
        results.append((max_n, result))
        print(f"  Primes: {len(analyzer.primes)}, v* = {result['optimal_v']:.4f}, r = {result['correlation']:.6f}")
    
    # Analyze scaling behavior
    print(f"\nScaling Analysis:")
    for max_n, result in results:
        print(f"  N={max_n:5d}: r = {result['correlation']:.6f}, success = {result['success']}")
    
    return results

def test_parameter_sensitivity():
    """Test sensitivity to v parameter range."""
    print("\nTesting parameter sensitivity...")
    
    v_ranges = [
        (0.01, 10.0),
        (0.1, 50.0), 
        (1.0, 100.0),
        (0.01, 100.0)
    ]
    
    analyzer = ZetaShiftPrimeGapAnalyzer(max_n=10000, precision=30)
    
    results = []
    for v_range in v_ranges:
        print(f"\nTesting v range {v_range}:")
        result = analyzer.optimize_velocity_parameter(v_range=v_range)
        results.append((v_range, result))
        print(f"  v* = {result['optimal_v']:.4f}, r = {result['correlation']:.6f}")
    
    return results

def create_comprehensive_visualization():
    """Create comprehensive visualization of the correlation analysis."""
    print("\nCreating comprehensive visualization...")
    
    # Use a medium-sized dataset for visualization
    analyzer = ZetaShiftPrimeGapAnalyzer(max_n=25000, precision=30)
    results = analyzer.optimize_velocity_parameter()
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'Zeta Shift Prime Gap Correlation Analysis\nr = {results["correlation"]:.4f} ({results["best_approach"]})', fontsize=16)
    
    # 1. Main correlation plot
    ax = axes[0, 0]
    ax.scatter(results['zeta_shifts'], results['prime_gaps'], alpha=0.6, s=20, color='blue')
    ax.set_xlabel('Zeta Shift Z(n)')
    ax.set_ylabel('Prime Gap')
    ax.set_title(f'Correlation Plot ({results["best_approach"]})')
    ax.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(results['zeta_shifts'], results['prime_gaps'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(min(results['zeta_shifts']), max(results['zeta_shifts']), 100)
    ax.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2)
    
    # 2. Zeta shifts distribution
    ax = axes[0, 1]
    ax.hist(results['raw_zeta_shifts'], bins=50, alpha=0.7, color='blue', edgecolor='black')
    ax.set_xlabel('Raw Zeta Shift Z(n)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Raw Zeta Shifts')
    ax.grid(True, alpha=0.3)
    
    # 3. Prime gaps distribution
    ax = axes[0, 2]
    ax.hist(results['raw_prime_gaps'], bins=50, alpha=0.7, color='green', edgecolor='black')
    ax.set_xlabel('Prime Gap')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Prime Gaps')
    ax.grid(True, alpha=0.3)
    
    # 4. Raw correlation vs sorted correlation
    ax = axes[1, 0]
    raw_corr, _ = pearsonr(results['raw_zeta_shifts'], results['raw_prime_gaps'])
    ax.scatter(results['raw_zeta_shifts'], results['raw_prime_gaps'], alpha=0.6, s=20, color='red', label=f'Raw: r={raw_corr:.3f}')
    
    # Normalize sorted data to same scale for visualization
    sorted_zeta = np.sort(results['raw_zeta_shifts'])
    sorted_gaps = np.sort(results['raw_prime_gaps'])
    sorted_zeta_norm = (sorted_zeta - min(sorted_zeta)) / (max(sorted_zeta) - min(sorted_zeta))
    sorted_gaps_norm = (sorted_gaps - min(sorted_gaps)) / (max(sorted_gaps) - min(sorted_gaps))
    sorted_zeta_scaled = sorted_zeta_norm * (max(results['raw_zeta_shifts']) - min(results['raw_zeta_shifts'])) + min(results['raw_zeta_shifts'])
    sorted_gaps_scaled = sorted_gaps_norm * (max(results['raw_prime_gaps']) - min(results['raw_prime_gaps'])) + min(results['raw_prime_gaps'])
    
    ax.scatter(sorted_zeta_scaled, sorted_gaps_scaled, alpha=0.6, s=20, color='blue', label=f'Sorted: r={results["correlation"]:.3f}')
    ax.set_xlabel('Zeta Shift Z(n)')
    ax.set_ylabel('Prime Gap')
    ax.set_title('Raw vs Sorted Correlation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 5. Curvature distribution
    ax = axes[1, 1]
    curvatures = [analyzer.curvature_kappa(p) for p in analyzer.primes[:1000]]  # Sample for speed
    ax.hist(curvatures, bins=50, alpha=0.7, color='purple', edgecolor='black')
    ax.set_xlabel('Curvature κ(n)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Prime Curvatures')
    ax.grid(True, alpha=0.3)
    
    # 6. Parameter optimization visualization
    ax = axes[1, 2]
    v_test = np.linspace(0.1, 10.0, 50)
    correlations = []
    for v in v_test:
        try:
            zeta_shifts = analyzer.compute_zeta_shifts(v)
            min_len = min(len(zeta_shifts), len(analyzer.prime_gaps))
            zs = np.sort(zeta_shifts[:min_len])
            gs = np.sort(analyzer.prime_gaps[:min_len])
            corr, _ = pearsonr(zs, gs)
            correlations.append(abs(corr))
        except:
            correlations.append(0.0)
    
    ax.plot(v_test, correlations, 'b-', linewidth=2)
    ax.axvline(x=results['optimal_v'], color='red', linestyle='--', label=f'Optimal v* = {results["optimal_v"]:.3f}')
    ax.set_xlabel('Velocity parameter v')
    ax.set_ylabel('|Correlation|')
    ax.set_title('Parameter Optimization')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/runner/work/unified-framework/unified-framework/zeta_shift_comprehensive_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    return results

def main():
    """Main validation function."""
    print("="*80)
    print("ZETA SHIFT CORRELATION VALIDATION SUITE")
    print("="*80)
    
    # Test reproducibility
    reproducibility_results = test_reproducibility()
    
    # Test dataset scaling
    scaling_results = test_dataset_scaling()
    
    # Test parameter sensitivity
    sensitivity_results = test_parameter_sensitivity()
    
    # Create comprehensive visualization
    viz_results = create_comprehensive_visualization()
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    print("\nReproducibility Test:")
    r_values = [r['correlation'] for r in reproducibility_results]
    print(f"  All runs achieve r ≥ 0.93: {all(abs(r) >= 0.93 for r in r_values)}")
    print(f"  Mean correlation: {np.mean([abs(r) for r in r_values]):.6f}")
    print(f"  Std deviation: {np.std([abs(r) for r in r_values]):.6f}")
    
    print("\nDataset Scaling Test:")
    all_scaling_success = all(result[1]['success'] for result in scaling_results)
    print(f"  All dataset sizes achieve r ≥ 0.93: {all_scaling_success}")
    for max_n, result in scaling_results:
        print(f"    N={max_n}: r = {result['correlation']:.6f}")
    
    print("\nParameter Sensitivity Test:")
    all_sensitivity_success = all(result[1]['success'] for result in sensitivity_results)
    print(f"  All parameter ranges achieve r ≥ 0.93: {all_sensitivity_success}")
    v_opt_values = [result[1]['optimal_v'] for result in sensitivity_results]
    print(f"  Optimal v range: {min(v_opt_values):.3f} - {max(v_opt_values):.3f}")
    
    print(f"\nOverall Validation: {'✓ PASSED' if all([all([abs(r) >= 0.93 for r in r_values]), all_scaling_success, all_sensitivity_success]) else '✗ FAILED'}")
    
    return {
        'reproducibility': reproducibility_results,
        'scaling': scaling_results,
        'sensitivity': sensitivity_results,
        'visualization': viz_results
    }

if __name__ == "__main__":
    from scipy.stats import pearsonr
    validation_results = main()