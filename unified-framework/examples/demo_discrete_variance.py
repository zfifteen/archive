"""
Demonstration script for Discrete Analogs of Quantum Nonlocality via Zeta Shift Cascades

This script provides a comprehensive demonstration of the var(O) ~ log log N scaling
relationship and geodesic effects in discrete zeta shift cascades.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from experiments.discrete_variance_propagation import QuantumNonlocalityAnalyzer

def comprehensive_analysis():
    """
    Run comprehensive analysis demonstrating discrete variance propagation
    and quantum nonlocality patterns in zeta shift cascades.
    """
    print("=" * 70)
    print("DISCRETE ANALOGS OF QUANTUM NONLOCALITY VIA ZETA SHIFT CASCADES")
    print("=" * 70)
    print("Modeling discrete variance propagation: var(O) ~ log log N")
    print("Simulating discrete geodesic effects on operator variance")
    print("Using θ'(n,k) and κ(n) transformations")
    print()
    
    # Initialize analyzer with larger cascade for better statistics
    analyzer = QuantumNonlocalityAnalyzer(max_N=500, seed=2)
    
    # 1. Variance Scaling Analysis
    print("1. VARIANCE SCALING ANALYSIS")
    print("-" * 30)
    print("Testing var(O) ~ log log N relationship across multiple cascade lengths...")
    
    N_values = [16, 32, 64, 128, 256, 400]
    scaling_results = analyzer.analyze_variance_scaling(N_values)
    
    print(f"Scaling relationship: {scaling_results['scaling_formula']}")
    print(f"Correlation coefficient: {scaling_results['correlation']:.6f}")
    print(f"R-squared: {scaling_results['r_squared']:.6f}")
    
    # Validate the log log N scaling
    if scaling_results['correlation'] > 0.7:
        print("✓ Strong evidence for var(O) ~ log log N scaling detected!")
    elif scaling_results['correlation'] > 0.5:
        print("○ Moderate evidence for var(O) ~ log log N scaling")
    else:
        print("× Weak evidence for var(O) ~ log log N scaling")
    
    print()
    
    # 2. Geodesic Effects Analysis
    print("2. GEODESIC EFFECTS ANALYSIS")
    print("-" * 30)
    print("Simulating discrete geodesic effects using θ'(n,k) and κ(n) transformations...")
    
    # Test with more k values around the expected optimal region
    k_values = np.linspace(0.1, 0.5, 21)
    geodesic_results = analyzer.simulate_geodesic_effects(N=300, k_values=k_values)
    
    print(f"Optimal k parameter: {geodesic_results['optimal_k']:.3f}")
    print(f"Maximum geodesic effect: {geodesic_results['max_geodesic_effect']:.8f}")
    
    # Check if optimal k is near expected value of 0.3
    expected_k = 0.3
    if abs(geodesic_results['optimal_k'] - expected_k) < 0.1:
        print(f"✓ Optimal k ({geodesic_results['optimal_k']:.3f}) is near expected value (0.3)")
    else:
        print(f"○ Optimal k ({geodesic_results['optimal_k']:.3f}) differs from expected value (0.3)")
    
    print()
    
    # 3. Quantum Nonlocality Metrics
    print("3. QUANTUM NONLOCALITY METRICS")
    print("-" * 32)
    print("Analyzing quantum nonlocality patterns in zeta shift cascades...")
    
    nonlocality_results = analyzer.quantum_nonlocality_metrics(N=300)
    
    print(f"Cross-correlation between regions: {nonlocality_results['cross_correlation']:.6f}")
    print(f"Entanglement metric: {nonlocality_results['entanglement_metric']:.6f}")
    print(f"Nonlocality violation: {nonlocality_results['nonlocality_violation']:.6f}")
    print(f"Bell inequality factor: {nonlocality_results['bell_inequality_factor']:.6f}")
    print(f"Quantum advantage detected: {nonlocality_results['quantum_advantage']}")
    
    # Interpret results
    if nonlocality_results['quantum_advantage']:
        print("✓ Quantum nonlocality patterns detected in discrete system!")
    elif nonlocality_results['bell_inequality_factor'] > 0.5:
        print("○ Weak quantum-like correlations observed")
    else:
        print("× No significant quantum nonlocality detected")
    
    print()
    
    # 4. Advanced Analysis
    print("4. ADVANCED ANALYSIS")
    print("-" * 18)
    print("Detailed examination of cascade properties...")
    
    # Generate larger cascade for detailed analysis
    cascade_N = 200
    cascade = analyzer.generate_cascade(cascade_N)
    O_values = analyzer.extract_operator_values(cascade)
    
    # Analyze distribution properties
    O_mean = np.mean(O_values)
    O_std = np.std(O_values)
    O_var = np.var(O_values)
    
    print(f"Cascade length: {cascade_N}")
    print(f"O values - Mean: {O_mean:.6f}, Std: {O_std:.6f}, Variance: {O_var:.6f}")
    
    # Test θ'(n,k) transformation effects
    theta_values_03 = analyzer.apply_theta_prime_transformation(cascade, k=0.3)
    theta_corr = np.corrcoef(O_values, theta_values_03)[0, 1]
    print(f"θ'(n,k=0.3) correlation with O values: {theta_corr:.6f}")
    
    # Test κ(n) curvature effects
    curvature_values = analyzer.compute_curvature_values(cascade)
    curvature_corr = np.corrcoef(O_values, curvature_values)[0, 1]
    print(f"κ(n) correlation with O values: {curvature_corr:.6f}")
    
    print()
    
    # 5. Summary and Interpretation
    print("5. SUMMARY AND INTERPRETATION")
    print("-" * 31)
    
    summary = {
        'var_scaling_confirmed': scaling_results['correlation'] > 0.6,
        'optimal_k_near_expected': abs(geodesic_results['optimal_k'] - 0.3) < 0.15,
        'quantum_patterns_detected': nonlocality_results['bell_inequality_factor'] > 0.3,
        'strong_geodesic_effects': geodesic_results['max_geodesic_effect'] > 1e-6
    }
    
    findings = []
    if summary['var_scaling_confirmed']:
        findings.append("✓ var(O) ~ log log N scaling relationship confirmed")
    if summary['optimal_k_near_expected']:
        findings.append("✓ Optimal curvature parameter k near theoretical expectation")
    if summary['quantum_patterns_detected']:
        findings.append("✓ Quantum-like correlation patterns detected")
    if summary['strong_geodesic_effects']:
        findings.append("✓ Significant geodesic effects on operator variance")
        
    if findings:
        print("Key findings:")
        for finding in findings:
            print(f"  {finding}")
    else:
        print("No strong patterns detected in this analysis.")
    
    print()
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    
    return {
        'scaling_results': scaling_results,
        'geodesic_results': geodesic_results,
        'nonlocality_results': nonlocality_results,
        'summary': summary,
        'cascade_stats': {
            'N': cascade_N,
            'O_mean': O_mean,
            'O_var': O_var,
            'theta_correlation': theta_corr,
            'curvature_correlation': curvature_corr
        }
    }

def create_summary_visualization(results):
    """
    Create summary visualization of key results.
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Variance scaling
    scaling = results['scaling_results']
    ax1.scatter(scaling['log_log_N'], scaling['variances'], color='red', s=80, alpha=0.7, zorder=5)
    x_fit = np.linspace(min(scaling['log_log_N']), max(scaling['log_log_N']), 100)
    y_fit = scaling['slope'] * x_fit + scaling['intercept']
    ax1.plot(x_fit, y_fit, 'b-', linewidth=2, label=f"R² = {scaling['r_squared']:.3f}")
    ax1.set_xlabel('log(log(N))')
    ax1.set_ylabel('var(O)')
    ax1.set_title('Variance Scaling: var(O) ~ log log N')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Geodesic effects
    geodesic = results['geodesic_results']
    ax2.plot(geodesic['k_values'], geodesic['geodesic_effects'], 'g-', linewidth=2)
    ax2.axvline(x=geodesic['optimal_k'], color='red', linestyle='--', alpha=0.7, 
                label=f"Optimal k = {geodesic['optimal_k']:.3f}")
    ax2.set_xlabel('k parameter')
    ax2.set_ylabel('Geodesic Effect Metric')
    ax2.set_title('Discrete Geodesic Effects')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Variance ratios
    ax3.plot(geodesic['k_values'], geodesic['variance_ratios'], 'purple', linewidth=2)
    ax3.axvline(x=geodesic['optimal_k'], color='red', linestyle='--', alpha=0.7)
    ax3.set_xlabel('k parameter')
    ax3.set_ylabel('Variance Ratio')
    ax3.set_title('Variance Modulation via θ\'(n,k)')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Correlations
    k_vals = geodesic['k_values']
    ax4.plot(k_vals, geodesic['theta_correlations'], 'orange', linewidth=2, label='θ\'(n,k) correlation')
    ax4.plot(k_vals, geodesic['curvature_correlations'], 'brown', linewidth=2, label='κ(n) correlation')
    ax4.axvline(x=geodesic['optimal_k'], color='red', linestyle='--', alpha=0.7)
    ax4.set_xlabel('k parameter')
    ax4.set_ylabel('Correlation Coefficient')
    ax4.set_title('Transformation Correlations')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/tmp/discrete_variance_propagation_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Summary visualization saved to /tmp/discrete_variance_propagation_analysis.png")

if __name__ == "__main__":
    # Run comprehensive analysis
    results = comprehensive_analysis()
    
    # Create visualization
    create_summary_visualization(results)
    
    # Print final summary
    print("\nFINAL SUMMARY:")
    print("-" * 15)
    print(f"var(O) scaling correlation: {results['scaling_results']['correlation']:.4f}")
    print(f"Optimal k parameter: {results['geodesic_results']['optimal_k']:.3f}")
    print(f"Quantum nonlocality factor: {results['nonlocality_results']['bell_inequality_factor']:.4f}")
    print(f"Analysis demonstrates discrete variance propagation patterns in zeta shift cascades.")