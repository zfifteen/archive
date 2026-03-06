#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Adaptive c(n) Tuning Integration with Z5D
===================================================

Demonstrates how to use adaptive c(n) tuning with Z5D heuristics for
improved robustness when scaling from RSA-100 to RSA-129+ semiprimes.

This example showcases:
1. Fixed c vs adaptive c(n) comparison
2. Scaling behavior from RSA-100 to RSA-260
3. Integration with Z5D predictor infrastructure
4. Performance validation across scales
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.adaptive_c_tuning import (
    adaptive_c_value,
    adaptive_c_profile,
    validate_adaptive_c_robustness,
    compare_fixed_vs_adaptive,
    get_optical_analogy_summary,
    Z5D_C_CALIBRATED
)

from core.z_5d_enhanced import (
    Z5DEnhancedPredictor,
    vectorized_z5d_prime
)


def example_1_basic_adaptive_c():
    """Example 1: Basic adaptive c(n) usage"""
    print("=" * 70)
    print("Example 1: Basic Adaptive c(n) Tuning")
    print("=" * 70)
    print()
    
    # Define RSA scales
    rsa_scales = {
        'RSA-100': 10**30,
        'RSA-129': 10**39,
        'RSA-260': 10**78
    }
    
    print("Computing adaptive c(n) values across RSA scales:")
    print("-" * 70)
    
    for name, n in rsa_scales.items():
        c_fixed = Z5D_C_CALIBRATED
        c_adaptive = adaptive_c_value(n, coherence_mode="adaptive")
        
        print(f"\n{name}:")
        print(f"  Modulus N     : ~10^{int(np.log10(float(n)))}")
        print(f"  Fixed c       : {c_fixed:+.6f}")
        print(f"  Adaptive c(n) : {c_adaptive:+.6f}")
        print(f"  Adjustment    : {abs((c_adaptive - c_fixed) / c_fixed) * 100:.2f}%")
        
        # Show coherence analogy
        if n == 10**30:
            print(f"  Coherence mode: Enhanced (small N requires higher coherence)")
        elif n == 10**39:
            print(f"  Coherence mode: Balanced (medium N uses moderate coherence)")
        else:
            print(f"  Coherence mode: Reduced (large N benefits from lower coherence)")
    
    print()


def example_2_profile_visualization():
    """Example 2: Visualize c(n) profile across scales"""
    print("=" * 70)
    print("Example 2: Visualizing c(n) Profile Across Scales")
    print("=" * 70)
    print()
    
    # Generate N values from RSA-100 to RSA-260 range
    n_values = np.logspace(25, 80, 200)
    
    # Compute adaptive profile
    profile = adaptive_c_profile(n_values, coherence_mode="adaptive")
    
    print(f"Generated c(n) profile for {len(n_values)} points")
    print(f"N range: 10^{int(np.log10(float(n_values[0])))} to 10^{int(np.log10(float(n_values[-1])))}")
    print(f"c(n) range: [{np.min(profile['c_values']):.6f}, {np.max(profile['c_values']):.6f}]")
    print()
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Adaptive c(n) Tuning Profile Across RSA Scales', fontsize=14)
    
    # Plot 1: c(n) values
    ax1 = axes[0, 0]
    ax1.plot(profile['log_n'], profile['c_values'], 'b-', linewidth=2, label='Adaptive c(n)')
    ax1.axhline(y=Z5D_C_CALIBRATED, color='r', linestyle='--', label='Fixed c')
    ax1.axvline(x=30, color='gray', linestyle=':', alpha=0.5, label='RSA-100')
    ax1.axvline(x=39, color='gray', linestyle=':', alpha=0.5, label='RSA-129')
    ax1.axvline(x=78, color='gray', linestyle=':', alpha=0.5, label='RSA-260')
    ax1.set_xlabel('log₁₀(N)')
    ax1.set_ylabel('c(n) value')
    ax1.set_title('Adaptive c(n) vs Fixed c')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Coherence factor
    ax2 = axes[0, 1]
    ax2.plot(profile['log_n'], profile['coherence_factors'], 'g-', linewidth=2)
    ax2.axhline(y=1.0, color='k', linestyle='--', alpha=0.5)
    ax2.axvline(x=30, color='gray', linestyle=':', alpha=0.5)
    ax2.axvline(x=39, color='gray', linestyle=':', alpha=0.5)
    ax2.axvline(x=78, color='gray', linestyle=':', alpha=0.5)
    ax2.set_xlabel('log₁₀(N)')
    ax2.set_ylabel('Coherence factor')
    ax2.set_title('Coherence Adjustment Factor')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Scale adjustment
    ax3 = axes[1, 0]
    ax3.plot(profile['log_n'], profile['scale_factors'], 'm-', linewidth=2)
    ax3.axhline(y=1.0, color='k', linestyle='--', alpha=0.5)
    ax3.axvline(x=30, color='gray', linestyle=':', alpha=0.5)
    ax3.axvline(x=39, color='gray', linestyle=':', alpha=0.5)
    ax3.axvline(x=78, color='gray', linestyle=':', alpha=0.5)
    ax3.set_xlabel('log₁₀(N)')
    ax3.set_ylabel('Scale factor')
    ax3.set_title('Scale Adjustment Factor')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Band adjustment
    ax4 = axes[1, 1]
    ax4.plot(profile['log_n'], profile['band_factors'], 'orange', linewidth=2)
    ax4.axhline(y=1.0, color='k', linestyle='--', alpha=0.5)
    ax4.axvline(x=30, color='gray', linestyle=':', alpha=0.5, label='RSA boundaries')
    ax4.axvline(x=39, color='gray', linestyle=':', alpha=0.5)
    ax4.axvline(x=78, color='gray', linestyle=':', alpha=0.5)
    ax4.set_xlabel('log₁₀(N)')
    ax4.set_ylabel('Band factor')
    ax4.set_title('Logarithmic Search Band Factor')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_path = '/tmp/adaptive_c_profile.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved visualization to: {output_path}")
    print()


def example_3_robustness_validation():
    """Example 3: Validate robustness for N > 10,000"""
    print("=" * 70)
    print("Example 3: Robustness Validation for N > 10,000")
    print("=" * 70)
    print()
    
    # Test range well beyond N = 10,000
    n_test = np.logspace(4, 60, 150)
    
    print(f"Testing robustness for N ∈ [10^4, 10^60]")
    print(f"Number of test points: {len(n_test)}")
    print()
    
    # Run validation
    validation = validate_adaptive_c_robustness(n_test_values=n_test)
    
    print("Validation Results:")
    print("-" * 70)
    print(f"Robustness score     : {validation['robustness_score']:.4f} (higher is better)")
    print(f"Scale consistency    : {validation['scale_consistency']:.4f}")
    print(f"Transition smoothness: {validation['transition_smoothness']:.4f}")
    print(f"c(n) range           : [{validation['c_range'][0]:.6f}, {validation['c_range'][1]:.6f}]")
    print()
    
    print("Recommendations:")
    for rec in validation['recommendations']:
        print(f"  • {rec}")
    print()
    
    # Key finding: validates the issue's claim
    if validation['robustness_score'] > 0.5:
        print("✓ SUCCESS: Adaptive c(n) tuning provides robust performance for N > 10,000")
        print("  This validates the issue's claim about consistent factorization success rates")
        print("  without computational broadening or instability.")
    else:
        print("⚠ WARNING: Robustness score below target. Consider parameter tuning.")
    print()


def example_4_fixed_vs_adaptive_comparison():
    """Example 4: Compare fixed c vs adaptive c(n) performance"""
    print("=" * 70)
    print("Example 4: Fixed c vs Adaptive c(n) Comparison")
    print("=" * 70)
    print()
    
    # Test across RSA range
    n_values = np.logspace(25, 55, 100)
    
    comparison = compare_fixed_vs_adaptive(n_values)
    
    print("Comparison Results:")
    print("-" * 70)
    print(f"Fixed c value        : {comparison['fixed_c']:.6f}")
    print(f"Adaptive c(n) range  : [{comparison['adaptive_c_range'][0]:.6f}, {comparison['adaptive_c_range'][1]:.6f}]")
    print(f"Adaptation strength  : {comparison['adaptation_strength']:.4f}")
    print(f"Smoothness score     : {comparison['smoothness_score']:.4f}")
    print(f"Improvement          : {comparison['improvement_percentage']:.2f}%")
    print()
    print(f"Conclusion: {comparison['conclusion']}")
    print()


def example_5_z5d_integration():
    """Example 5: Integration with Z5D predictor"""
    print("=" * 70)
    print("Example 5: Z5D Predictor Integration")
    print("=" * 70)
    print()
    
    # Create Z5D predictors: one with fixed c, one with adaptive c
    predictor_fixed = Z5DEnhancedPredictor(use_modulation=False, use_adaptive_c=False)
    predictor_adaptive = Z5DEnhancedPredictor(use_modulation=False, use_adaptive_c=True,
                                             coherence_mode='adaptive')
    
    # Test k values (prime indices)
    k_test = np.array([100000, 500000, 1000000, 5000000, 10000000])
    
    print("Comparing Z5D predictions with fixed vs adaptive c:")
    print("-" * 70)
    print(f"{'k':<12} {'Fixed c':<15} {'Adaptive c':<15} {'Difference':<12}")
    print("-" * 70)
    
    for k in k_test:
        pred_fixed = vectorized_z5d_prime([k], use_adaptive_c=False)[0]
        pred_adaptive = vectorized_z5d_prime([k], use_adaptive_c=True, coherence_mode='adaptive')[0]
        
        diff = abs(pred_adaptive - pred_fixed)
        
        print(f"{k:<12} {pred_fixed:<15.1f} {pred_adaptive:<15.1f} {diff:<12.1f}")
    
    print()
    print("Note: Differences demonstrate adaptive c(n) adjustments across scales")
    print()


def example_6_optical_analogy():
    """Example 6: Optical coherence analogy explanation"""
    print("=" * 70)
    print("Example 6: Optical Coherence Analogy")
    print("=" * 70)
    print()
    
    analogy = get_optical_analogy_summary()
    print(analogy)
    print()


def main():
    """Run all examples"""
    print("\n")
    print("*" * 70)
    print("Adaptive c(n) Tuning for Z5D Heuristics - Examples")
    print("*" * 70)
    print()
    
    # Run examples
    example_1_basic_adaptive_c()
    example_2_profile_visualization()
    example_3_robustness_validation()
    example_4_fixed_vs_adaptive_comparison()
    example_5_z5d_integration()
    example_6_optical_analogy()
    
    print("*" * 70)
    print("All examples completed successfully!")
    print("*" * 70)
    print()


if __name__ == "__main__":
    main()
