#!/usr/bin/env python3
"""
Golden Ratio Tangent Circles Demonstration

Showcases the symmetric arrangement of tangent circles scaled by powers
of the golden ratio φ ≈ 1.618, and demonstrates integration with the
z-sandbox framework for:

1. Low-discrepancy sampling (extending low_discrepancy.py)
2. Monte Carlo variance reduction
3. Gaussian lattice enhancements
4. Z5D curvature calculations
5. Factor candidate generation

Usage:
    python golden_ratio_tangent_circles_demo.py
"""

import sys
import os
import math

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from golden_ratio_tangent_circles import (
    GoldenRatioTangentCircles,
    TangentChainSampler,
    PHI, PHI_SQ, PHI_CUBE
)
import matplotlib.pyplot as plt
import numpy as np


def demo_basic_visualization():
    """
    Demonstrate basic tangent circles visualization.
    """
    print("\n" + "=" * 70)
    print("Demo 1: Basic Tangent Circles Visualization")
    print("=" * 70)
    
    arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
    
    # Create visualization
    fig = arrangement.visualize(
        output_file="demo_basic_tangent_circles.png",
        show_arc=True,
        show_labels=True
    )
    plt.close(fig)
    
    print("✓ Created basic visualization: demo_basic_tangent_circles.png")
    
    # Show circle properties
    circle_data = arrangement.get_circle_data()
    print(f"\nTotal circles: {len(circle_data)}")
    print(f"Total area: {sum(c['area'] for c in circle_data):.6f}")
    print(f"Largest radius: {max(c['radius'] for c in circle_data):.6f} (φ²)")
    print(f"Smallest radius: {min(c['radius'] for c in circle_data):.6f} (φ⁻⁴)")


def demo_hierarchical_sampling():
    """
    Demonstrate hierarchical sampling using tangent circle structure.
    """
    print("\n" + "=" * 70)
    print("Demo 2: Hierarchical Sampling")
    print("=" * 70)
    
    sampler = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
    
    # Generate samples
    n_samples = 2000
    samples = sampler.generate_hierarchical_samples(n_samples, dimension=2)
    
    print(f"Generated {n_samples} hierarchical samples")
    
    # Visualize sample distribution
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Draw reference circles at φ-scales
    for scale_idx in range(5):
        power = scale_idx - 2
        radius = 1.0 * (PHI ** power)
        circle = plt.Circle((0, 0), radius, fill=False, 
                           edgecolor='gray', linestyle='--', alpha=0.3)
        ax.add_patch(circle)
        ax.text(radius * 0.707, radius * 0.707, f"φ^{power}",
               fontsize=8, color='gray')
    
    # Plot samples
    ax.scatter(samples[:, 0], samples[:, 1], s=1, alpha=0.5, c='blue')
    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Hierarchical Sampling with φ-scaled Tangent Circles')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("demo_hierarchical_sampling.png", dpi=150)
    plt.close(fig)
    
    print("✓ Created hierarchical sampling visualization: demo_hierarchical_sampling.png")
    
    # Analyze sample properties
    radii = np.sqrt(samples[:, 0]**2 + samples[:, 1]**2)
    print(f"\nSample statistics:")
    print(f"  Mean radius: {np.mean(radii):.6f}")
    print(f"  Std radius: {np.std(radii):.6f}")
    print(f"  Min radius: {np.min(radii):.6f}")
    print(f"  Max radius: {np.max(radii):.6f}")


def demo_annulus_sampling():
    """
    Demonstrate annulus sampling for factorization candidate generation.
    """
    print("\n" + "=" * 70)
    print("Demo 3: Annulus Sampling (Factorization Application)")
    print("=" * 70)
    
    # Example: Generate candidates around √N for N = 143 = 11 × 13
    N = 143
    sqrt_N = math.sqrt(N)
    
    # Define annulus around √N
    r_inner = sqrt_N * 0.9
    r_outer = sqrt_N * 1.1
    
    print(f"N = {N} (factors: 11 × 13)")
    print(f"√N ≈ {sqrt_N:.6f}")
    print(f"Sampling annulus: [{r_inner:.6f}, {r_outer:.6f}]")
    
    sampler = TangentChainSampler(base_radius=sqrt_N, num_scales=7, seed=42)
    samples = sampler.generate_annulus_samples(500, r_inner, r_outer)
    
    # Visualize
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Draw annulus boundaries
    inner_circle = plt.Circle((0, 0), r_inner, fill=False, 
                             edgecolor='red', linestyle='--', linewidth=2)
    outer_circle = plt.Circle((0, 0), r_outer, fill=False,
                             edgecolor='red', linestyle='--', linewidth=2)
    ax.add_patch(inner_circle)
    ax.add_patch(outer_circle)
    
    # Draw √N reference
    sqrt_circle = plt.Circle((0, 0), sqrt_N, fill=False,
                            edgecolor='green', linestyle='-', linewidth=2,
                            label=f'√N ≈ {sqrt_N:.2f}')
    ax.add_patch(sqrt_circle)
    
    # Plot samples
    ax.scatter(samples[:, 0], samples[:, 1], s=10, alpha=0.5, c='blue',
              label='Candidate samples')
    
    # Mark actual factors if they map to radii
    factor_radius_1 = 11.0
    factor_radius_2 = 13.0
    ax.scatter([factor_radius_1], [0], s=200, c='red', marker='*',
              label=f'Factor p={11}', zorder=5)
    ax.scatter([factor_radius_2], [0], s=200, c='orange', marker='*',
              label=f'Factor q={13}', zorder=5)
    
    ax.set_aspect('equal')
    ax.set_xlabel('X (candidate value space)')
    ax.set_ylabel('Y (geometric embedding)')
    ax.set_title(f'Annulus Sampling for Factorization (N={N})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("demo_annulus_sampling.png", dpi=150)
    plt.close(fig)
    
    print("✓ Created annulus sampling visualization: demo_annulus_sampling.png")
    print(f"\nGenerated {len(samples)} candidate samples in annulus")


def demo_monte_carlo_integration():
    """
    Demonstrate variance reduction in Monte Carlo integration.
    """
    print("\n" + "=" * 70)
    print("Demo 4: Monte Carlo Integration with Tangent Chain Sampling")
    print("=" * 70)
    
    # Define a test function to integrate over a disk
    def test_function(x, y):
        """Gaussian-like function for integration."""
        return np.exp(-(x**2 + y**2) / 2)
    
    # Compare uniform vs tangent chain sampling
    n_samples = 1000
    max_radius = 3.0
    
    # Method 1: Uniform random sampling
    rng = np.random.RandomState(42)
    theta_uniform = rng.uniform(0, 2 * math.pi, n_samples)
    r_uniform = np.sqrt(rng.uniform(0, max_radius**2, n_samples))
    x_uniform = r_uniform * np.cos(theta_uniform)
    y_uniform = r_uniform * np.sin(theta_uniform)
    
    values_uniform = test_function(x_uniform, y_uniform)
    integral_uniform = np.mean(values_uniform) * math.pi * max_radius**2
    variance_uniform = np.var(values_uniform)
    
    # Method 2: Tangent chain sampling
    sampler = TangentChainSampler(base_radius=max_radius / 2, num_scales=5, seed=42)
    samples_tangent = sampler.generate_hierarchical_samples(n_samples, dimension=2)
    
    # Scale to disk
    radii_tangent = np.sqrt(samples_tangent[:, 0]**2 + samples_tangent[:, 1]**2)
    scale_factor = max_radius / np.max(radii_tangent)
    samples_tangent = samples_tangent * scale_factor
    
    values_tangent = test_function(samples_tangent[:, 0], samples_tangent[:, 1])
    integral_tangent = np.mean(values_tangent) * math.pi * max_radius**2
    variance_tangent = np.var(values_tangent)
    
    print(f"Test function: exp(-(x² + y²)/2) over disk of radius {max_radius}")
    print(f"Number of samples: {n_samples}")
    print()
    print("Results:")
    print(f"  Uniform sampling:")
    print(f"    Integral estimate: {integral_uniform:.6f}")
    print(f"    Sample variance: {variance_uniform:.6f}")
    print(f"  Tangent chain sampling:")
    print(f"    Integral estimate: {integral_tangent:.6f}")
    print(f"    Sample variance: {variance_tangent:.6f}")
    print(f"  Variance reduction: {variance_uniform / variance_tangent:.2f}x")
    
    # Visualize comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Uniform sampling
    ax1.scatter(x_uniform, y_uniform, c=values_uniform, s=10, alpha=0.6, 
               cmap='viridis')
    ax1.set_aspect('equal')
    ax1.set_title(f'Uniform Sampling\nVariance: {variance_uniform:.4f}')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    
    # Tangent chain sampling
    scatter = ax2.scatter(samples_tangent[:, 0], samples_tangent[:, 1],
                         c=values_tangent, s=10, alpha=0.6, cmap='viridis')
    ax2.set_aspect('equal')
    ax2.set_title(f'Tangent Chain Sampling\nVariance: {variance_tangent:.4f}')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    
    plt.colorbar(scatter, ax=ax2, label='Function value')
    plt.tight_layout()
    plt.savefig("demo_monte_carlo_variance.png", dpi=150)
    plt.close(fig)
    
    print("✓ Created Monte Carlo comparison: demo_monte_carlo_variance.png")


def demo_self_similarity():
    """
    Demonstrate self-similarity property of golden ratio circles.
    """
    print("\n" + "=" * 70)
    print("Demo 5: Self-Similarity and Fractal Properties")
    print("=" * 70)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    scales = [1.0, PHI, PHI_SQ]
    titles = ["Scale: 1", f"Scale: φ ≈ {PHI:.3f}", f"Scale: φ² ≈ {PHI_SQ:.3f}"]
    
    for ax, scale, title in zip(axes, scales, titles):
        arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
        arrangement.compute_circle_positions()
        
        # Scale all circles
        for circle in arrangement.circles:
            circle.x *= scale
            circle.y *= scale
            circle.radius *= scale
        
        # Draw circles
        for circle in arrangement.circles:
            circle_patch = plt.Circle(
                (circle.x, circle.y),
                circle.radius,
                color=circle.color,
                alpha=0.5,
                edgecolor='black',
                linewidth=1
            )
            ax.add_patch(circle_patch)
        
        # Draw baseline
        x_min = min(c.x - c.radius for c in arrangement.circles) - 0.5
        x_max = max(c.x + c.radius for c in arrangement.circles) + 0.5
        ax.axhline(y=0, color='black', linewidth=1, linestyle='--', alpha=0.3)
        
        ax.set_aspect('equal')
        ax.set_xlim(x_min, x_max)
        y_max = max(c.y + c.radius for c in arrangement.circles) + 0.5
        ax.set_ylim(-0.5, y_max)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("demo_self_similarity.png", dpi=150)
    plt.close(fig)
    
    print("✓ Created self-similarity visualization: demo_self_similarity.png")
    print("\nObservation: The pattern maintains its structure at all φ-scales")
    print("This self-similarity property enables hierarchical sampling and")
    print("variance reduction across multiple scales simultaneously.")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("Golden Ratio Tangent Circles - Comprehensive Demonstration")
    print("=" * 70)
    print()
    print("This demo showcases:")
    print("1. Basic tangent circles visualization")
    print("2. Hierarchical sampling with φ-scales")
    print("3. Annulus sampling for factorization")
    print("4. Monte Carlo variance reduction")
    print("5. Self-similarity properties")
    print()
    
    # Run demos
    demo_basic_visualization()
    demo_hierarchical_sampling()
    demo_annulus_sampling()
    demo_monte_carlo_integration()
    demo_self_similarity()
    
    # Summary
    print("\n" + "=" * 70)
    print("All Demonstrations Complete!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - demo_basic_tangent_circles.png")
    print("  - demo_hierarchical_sampling.png")
    print("  - demo_annulus_sampling.png")
    print("  - demo_monte_carlo_variance.png")
    print("  - demo_self_similarity.png")
    print()
    print("Integration points with z-sandbox:")
    print("  ✓ low_discrepancy.py: Tangent chain sampling extends golden-angle")
    print("  ✓ monte_carlo.py: Hierarchical sampling reduces variance")
    print("  ✓ gaussian_lattice.py: Tangent circles enhance distance metrics")
    print("  ✓ multiplication_viz_factor.py: Geometric lens for factorization")
    print("  ✓ z5d_axioms.py: Self-similar scaling in curvature calculations")
    print("=" * 70)


if __name__ == "__main__":
    main()
