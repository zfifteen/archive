#!/usr/bin/env python3
"""
Linear Curvature Performance Demonstration
==========================================

Demonstrates the performance improvement achieved by replacing trigonometric
curvature calculations with linearized κ_g ≈ Δθ'/Δs using fixed-point
arithmetic and golden ratio transformations.

Usage:
    python demo_linear_curvature.py
"""

import time
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.kappa_linear import (
    gen_frac_phi, kappa_linear_sequence, benchmark_linear_vs_traditional,
    kappa_linear_replace_trigonometric
)


def demonstrate_performance():
    """Demonstrate performance improvements across different scales."""
    print("=== Linear Curvature Performance Demonstration ===\n")
    
    scales = [100, 500, 1000, 2000]
    results = []
    
    print("Scale   | Linear Time | Traditional Time | Speedup  | Correlation")
    print("--------|-------------|------------------|----------|------------")
    
    for N in scales:
        benchmark = benchmark_linear_vs_traditional(N=N, k=0.3, use_fast=True)
        
        results.append({
            'N': N,
            'linear_time': benchmark['linear_time'],
            'traditional_time': benchmark['traditional_time'],
            'speedup': benchmark['speedup_factor'],
            'correlation': benchmark['correlation']
        })
        
        print(f"{N:6d}  | {benchmark['linear_time']:9.4f}s | "
              f"{benchmark['traditional_time']:14.4f}s | "
              f"{benchmark['speedup_factor']:6.2f}x | "
              f"{benchmark['correlation']:9.4f}")
    
    return results


def demonstrate_trigonometric_replacement():
    """Demonstrate trigonometric function replacement with linear approximations."""
    print("\n=== Trigonometric Function Replacement ===\n")
    
    n_values = list(range(1, 21))
    trig_results = kappa_linear_replace_trigonometric(n_values, use_fast=True)
    
    print("n  | θ (rad) | sin(θ)   | sin_linear | cos(θ)   | cos_linear | κ_linear")
    print("---|---------|----------|------------|----------|------------|----------")
    
    for i, n in enumerate(n_values):
        theta = trig_results['theta_linear'][i]
        sin_exact = np.sin(theta)
        cos_exact = np.cos(theta)
        sin_linear = trig_results['sin_linear'][i]
        cos_linear = trig_results['cos_linear'][i]
        kappa_linear = trig_results['kappa_linear'][i]
        
        print(f"{n:2d} | {theta:7.4f} | {sin_exact:8.5f} | {sin_linear:10.5f} | "
              f"{cos_exact:8.5f} | {cos_linear:10.5f} | {kappa_linear:8.5f}")


def demonstrate_fixed_point_precision():
    """Demonstrate fixed-point precision effects."""
    print("\n=== Fixed-Point Precision Demonstration ===\n")
    
    N = 10
    scale_bits_values = [16, 32, 48]
    
    print("n  | 16-bit       | 32-bit       | 48-bit       | Difference")
    print("---|--------------|--------------|--------------|------------")
    
    results = {}
    for scale_bits in scale_bits_values:
        frac_values = list(gen_frac_phi(N, scale_bits=scale_bits, use_fast=False))
        results[scale_bits] = frac_values
    
    for i in range(N):
        frac_16 = results[16][i]
        frac_32 = results[32][i]
        frac_48 = results[48][i]
        diff_32_48 = abs(frac_32 - frac_48)
        
        print(f"{i+1:2d} | {frac_16:12.9f} | {frac_32:12.9f} | {frac_48:12.9f} | {diff_32_48:10.2e}")


def demonstrate_golden_ratio_properties():
    """Demonstrate golden ratio mathematical properties in the implementation."""
    print("\n=== Golden Ratio Properties ===\n")
    
    from core.kappa_linear import PHI_FLOAT, ALPHA_FLOAT
    
    print(f"Golden ratio φ = {PHI_FLOAT:.15f}")
    print(f"Alpha = 1/φ = {ALPHA_FLOAT:.15f}")
    print(f"φ * α = {PHI_FLOAT * ALPHA_FLOAT:.15f} (should be ≈ 1.0)")
    print(f"φ² - φ - 1 = {PHI_FLOAT**2 - PHI_FLOAT - 1:.2e} (should be ≈ 0)")
    
    # Demonstrate Beatty sequence properties
    N = 20
    frac_values = list(gen_frac_phi(N, use_fast=True))
    
    print(f"\nFirst {N} values of {{n/φ}} sequence:")
    for i, frac in enumerate(frac_values, 1):
        print(f"{{%2d/φ}} = %8.6f" % (i, frac))
    
    # Show distribution
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    hist, _ = np.histogram(frac_values, bins=bins)
    print(f"\nDistribution in bins [0,0.2), [0.2,0.4), [0.4,0.6), [0.6,0.8), [0.8,1.0):")
    print(f"Counts: {hist}")


def create_performance_plot(results):
    """Create a performance visualization plot."""
    print("\n=== Creating Performance Plot ===")
    
    try:
        scales = [r['N'] for r in results]
        speedups = [r['speedup'] for r in results]
        
        plt.figure(figsize=(10, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(scales, speedups, 'bo-', linewidth=2, markersize=8)
        plt.xlabel('Problem Size (N)')
        plt.ylabel('Speedup Factor')
        plt.title('Linear Curvature Performance Improvement')
        plt.grid(True, alpha=0.3)
        plt.yscale('linear')
        
        # Add speedup values as text
        for x, y in zip(scales, speedups):
            plt.annotate(f'{y:.1f}x', (x, y), textcoords="offset points", 
                        xytext=(0,10), ha='center')
        
        plt.subplot(1, 2, 2)
        linear_times = [r['linear_time'] for r in results]
        trad_times = [r['traditional_time'] for r in results]
        
        plt.plot(scales, linear_times, 'g-', label='Linear Curvature', linewidth=2)
        plt.plot(scales, trad_times, 'r-', label='Traditional Curvature', linewidth=2)
        plt.xlabel('Problem Size (N)')
        plt.ylabel('Computation Time (seconds)')
        plt.title('Computation Time Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        
        plt.tight_layout()
        
        # Use cross-platform temporary directory
        temp_dir = tempfile.gettempdir()
        plot_path = os.path.join(temp_dir, 'linear_curvature_performance.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"Performance plot saved to {plot_path}")
        
    except ImportError:
        print("Matplotlib not available for plotting")
    except Exception as e:
        print(f"Plot creation failed: {e}")


def main():
    """Main demonstration function."""
    print("Linear Curvature Implementation Demonstration")
    print("=" * 50)
    
    # Performance demonstration
    results = demonstrate_performance()
    
    # Trigonometric replacement
    demonstrate_trigonometric_replacement()
    
    # Fixed-point precision
    demonstrate_fixed_point_precision()
    
    # Golden ratio properties
    demonstrate_golden_ratio_properties()
    
    # Create performance plot
    create_performance_plot(results)
    
    # Summary
    print("\n=== Summary ===")
    avg_speedup = np.mean([r['speedup'] for r in results])
    print(f"Average speedup achieved: {avg_speedup:.2f}x")
    print(f"Maximum speedup achieved: {max(r['speedup'] for r in results):.2f}x")
    print(f"Implementation provides significant performance improvement")
    print(f"while maintaining mathematical accuracy for small-angle approximations.")
    
    print("\n✓ Linear curvature demonstration completed successfully!")


if __name__ == "__main__":
    main()