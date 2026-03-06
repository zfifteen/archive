#!/usr/bin/env python3
"""
Visualization script for Li-Z5D Symmetry Hypothesis Analysis

Generates plots comparing relative errors of different prime counting approximations
to evaluate the symmetry hypothesis claims.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add tests to path to import the test module
sys.path.append(os.path.dirname(__file__))
from test_li_z5d_symmetry_falsification import PrimeCountingFalsificationTest

def create_comparison_plot(test_results: dict, save_path: str = None):
    """
    Create log-log plot comparing relative errors similar to the problem statement description
    
    Args:
        test_results: Results from falsification test
        save_path: Optional path to save the plot
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Extract data
    k_values = np.array(test_results['k_values'])
    errors = test_results['relative_errors']
    
    # Plot each method with appropriate styling to match description
    ax.loglog(k_values, errors['Z5D'], 'b-', linewidth=2, label='Z_5D/Riemann R', alpha=0.8)
    ax.loglog(k_values, errors['Li'], 'orange', linewidth=2, label='Li (Logarithmic Integral)', alpha=0.8)
    ax.loglog(k_values, errors['PASE'], 'g--', linewidth=2, label='PASE (k/log k)', alpha=0.8)
    ax.loglog(k_values, errors['Riemann_R'], 'purple', linewidth=1, linestyle=':', label='Riemann R (truncated)', alpha=0.6)
    
    # Add reference lines for claimed error levels
    ax.axhline(y=1e-6, color='blue', linestyle='--', alpha=0.5, label='Z5D claimed level (~10⁻⁶)')
    ax.axhline(y=1e-2, color='orange', linestyle='--', alpha=0.5, label='Li claimed level (~10⁻²)')
    ax.axhline(y=1e-1, color='green', linestyle='--', alpha=0.5, label='PASE claimed level (~10⁻¹)')
    
    # Formatting
    ax.set_xlabel('k', fontsize=14)
    ax.set_ylabel('Relative Error |approx - π(k)| / π(k)', fontsize=14)
    ax.set_title('Prime Counting Approximation Errors: Testing Li-Z5D Symmetry Claims', fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12, loc='upper right')
    
    # Set axis limits to match problem description range
    ax.set_xlim(1e2, 1e8)
    ax.set_ylim(1e-8, 1e2)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    return fig, ax

def create_symmetry_analysis_plot(test_results: dict, save_path: str = None):
    """
    Create additional analysis plots showing symmetry patterns
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    k_values = np.array(test_results['k_values'])
    errors = test_results['relative_errors']
    
    # Plot 1: Direct error comparison
    ax1.semilogx(k_values, errors['Li'], 'orange', label='Li Error', linewidth=2)
    ax1.semilogx(k_values, errors['Z5D'], 'blue', label='Z5D Error', linewidth=2)
    ax1.set_xlabel('k')
    ax1.set_ylabel('Relative Error')
    ax1.set_title('Direct Error Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Error difference (symmetry analysis)
    error_diff = np.array(errors['Li']) - np.array(errors['Z5D'])
    ax2.semilogx(k_values, error_diff, 'red', linewidth=2)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.set_xlabel('k')
    ax2.set_ylabel('Li Error - Z5D Error')
    ax2.set_title('Error Difference (Symmetry Test)')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Bias patterns
    # Extract approximation values to compute biases
    biases = test_results['symmetry_tests']
    methods = ['Li', 'Z5D', 'Riemann_R', 'PASE']
    bias_values = [biases['li_bias'], biases['z5d_bias'], biases['r_bias'], 0]  # PASE bias not computed
    
    ax3.bar(methods, bias_values, color=['orange', 'blue', 'purple', 'green'], alpha=0.7)
    ax3.set_ylabel('Mean Bias')
    ax3.set_title('Systematic Bias Comparison')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Correlation scatter
    if np.all(np.isfinite(errors['Li'])) and np.all(np.isfinite(errors['Z5D'])):
        ax4.scatter(errors['Li'], errors['Z5D'], alpha=0.6, s=50)
        ax4.set_xlabel('Li Relative Error')
        ax4.set_ylabel('Z5D Relative Error') 
        ax4.set_title(f'Error Correlation (r={test_results["symmetry_tests"]["li_z5d_correlation"]:.3f})')
        ax4.grid(True, alpha=0.3)
        
        # Add correlation line if valid
        corr = test_results["symmetry_tests"]["li_z5d_correlation"]
        if np.isfinite(corr) and abs(corr) > 0.1:
            z = np.polyfit(errors['Li'], errors['Z5D'], 1)
            p = np.poly1d(z)
            ax4.plot(errors['Li'], p(errors['Li']), "r--", alpha=0.8)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Symmetry analysis plot saved to {save_path}")
    
    return fig

def generate_falsification_report(test_results: dict):
    """
    Generate a comprehensive falsification report
    """
    print("\n" + "="*80)
    print("COMPREHENSIVE FALSIFICATION ANALYSIS REPORT")
    print("="*80)
    
    evidence = test_results['falsification_evidence']
    params = test_results['test_parameters']
    
    print(f"\nTest Parameters:")
    print(f"  k range: {params['k_range'][0]:.1e} to {params['k_range'][1]:.1e}")
    print(f"  Number of test points: {params['num_points']}")
    print(f"  Runtime: {test_results['runtime_seconds']:.2f} seconds")
    
    print(f"\nOverall Verdict:")
    print(f"  Hypothesis Falsified: {'YES' if evidence['overall_hypothesis_falsified'] else 'NO'}")
    print(f"  Claims Falsified: {evidence['falsified_claims_count']}/{evidence['total_claims_tested']}")
    
    print(f"\nDetailed Analysis:")
    
    # Error level claims
    error_tests = test_results['error_claims_tests']
    print(f"  Ultra-low Z5D error claim (~10⁻⁶): {'FALSIFIED' if evidence.get('ultra_low_error_falsified') else 'SUPPORTED'}")
    if 'ultra_low_error_reason' in evidence:
        print(f"    Reason: {evidence['ultra_low_error_reason']}")
    
    print(f"  Li error range claim (10⁻¹ to 10⁻²): {'FALSIFIED' if evidence.get('li_error_range_falsified') else 'SUPPORTED'}")
    
    # Symmetry claims  
    symmetry = test_results['symmetry_tests']
    print(f"  Li-Z5D correlation: {symmetry['li_z5d_correlation']:.4f}")
    print(f"  Symmetry claim: {'FALSIFIED' if evidence.get('symmetry_falsified') else 'SUPPORTED'}")
    if 'symmetry_reason' in evidence:
        print(f"    Reason: {evidence['symmetry_reason']}")
    
    # Bias pattern claims
    print(f"  Li overestimation bias: {symmetry['li_bias']:.2e}")
    print(f"  Z5D bias: {symmetry['z5d_bias']:.2e}")
    print(f"  Bias pattern claim: {'FALSIFIED' if evidence.get('bias_pattern_falsified') else 'SUPPORTED'}")
    
    # Statistical summary
    print(f"\nStatistical Summary:")
    print(f"  Mean symmetry difference: {symmetry['symmetry_difference']:.2e}")
    
    oscillatory = test_results['oscillatory_tests']
    print(f"  Z5D variance: {oscillatory['Z5D_variance']:.2e}")
    print(f"  Li variance: {oscillatory['Li_variance']:.2e}")
    print(f"  Z5D more oscillatory: {oscillatory['Z5D_more_oscillatory']}")
    
    print("\n" + "="*80)

def main():
    """Run visualization and analysis"""
    print("Generating Li-Z5D Symmetry Analysis Visualizations")
    print("=" * 60)
    
    # Run falsification test with higher resolution for better plots
    test = PrimeCountingFalsificationTest(max_k=10**8, num_points=30)
    results = test.run_falsification_test()
    
    # Generate plots
    print("\nGenerating comparison plot...")
    fig1, ax1 = create_comparison_plot(results, 'li_z5d_comparison.png')
    
    print("Generating symmetry analysis plot...")
    fig2 = create_symmetry_analysis_plot(results, 'li_z5d_symmetry_analysis.png')
    
    # Generate comprehensive report
    generate_falsification_report(results)
    
    # Show plots if in interactive mode
    try:
        plt.show()
    except:
        print("Note: Plots saved to files (interactive display not available)")

if __name__ == "__main__":
    main()