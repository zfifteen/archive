#!/usr/bin/env python3
"""
Curvature Field Visualization
==============================

Generate visualizations of the Z5D curvature field κ(p) in 3D space.
Shows how curvature correlates with fractal complexity.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from z5d_curvature import (
    kappa_field,
    mandelbulb_distance_estimator,
    visualize_curvature_field
)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_curvature_slice(z_slice: float = 0.0, resolution: int = 200,
                         extent: float = 3.0, output_file: str = None):
    """
    Plot 2D slice of curvature field.
    
    Args:
        z_slice: Z-coordinate of the slice
        resolution: Grid resolution
        extent: Spatial extent
        output_file: Optional output file path
    """
    print(f"Generating curvature field slice at z={z_slice}...")
    
    kappa_values = visualize_curvature_field(resolution, z_slice, extent)
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Curvature field
    x = np.linspace(-extent, extent, resolution)
    y = np.linspace(-extent, extent, resolution)
    
    im1 = ax1.imshow(kappa_values, extent=[-extent, extent, -extent, extent],
                     origin='lower', cmap='viridis', aspect='auto')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_title(f'Z5D Curvature Field κ(p) at z={z_slice}')
    ax1.grid(alpha=0.3)
    
    divider1 = make_axes_locatable(ax1)
    cax1 = divider1.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im1, cax=cax1, label='κ(p)')
    
    # Plot 2: Distance field (for comparison)
    X, Y = np.meshgrid(x, y)
    points = np.stack([X.ravel(), Y.ravel(), 
                      np.full(X.size, z_slice)], axis=1)
    
    distances = np.array([
        mandelbulb_distance_estimator(p, power=8.0) 
        for p in points
    ]).reshape(X.shape)
    
    im2 = ax2.imshow(np.log1p(np.abs(distances)), 
                     extent=[-extent, extent, -extent, extent],
                     origin='lower', cmap='plasma', aspect='auto')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title(f'Distance Field (log scale) at z={z_slice}')
    ax2.grid(alpha=0.3)
    
    divider2 = make_axes_locatable(ax2)
    cax2 = divider2.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im2, cax=cax2, label='log(1 + |d|)')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Saved to: {output_file}")
    else:
        plt.show()


def plot_curvature_comparison(num_slices: int = 5, output_file: str = None):
    """
    Plot multiple z-slices showing curvature variation.
    
    Args:
        num_slices: Number of z-slices to plot
        output_file: Optional output file path
    """
    print(f"Generating {num_slices} curvature field slices...")
    
    z_values = np.linspace(-2.0, 2.0, num_slices)
    
    fig, axes = plt.subplots(1, num_slices, figsize=(4 * num_slices, 4))
    if num_slices == 1:
        axes = [axes]
    
    extent = 3.0
    resolution = 150
    
    for ax, z in zip(axes, z_values):
        kappa_values = visualize_curvature_field(resolution, z, extent)
        
        im = ax.imshow(kappa_values, extent=[-extent, extent, -extent, extent],
                       origin='lower', cmap='viridis', aspect='auto',
                       vmin=-1, vmax=2)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'z={z:.1f}')
        ax.grid(alpha=0.3)
    
    # Add colorbar to the right of all plots
    fig.subplots_adjust(right=0.9)
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    fig.colorbar(im, cax=cbar_ax, label='κ(p)')
    
    plt.suptitle('Z5D Curvature Field Across Z-Slices', y=0.98, fontsize=14)
    
    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Saved to: {output_file}")
    else:
        plt.show()


def plot_step_size_distribution(num_samples: int = 1000, output_file: str = None):
    """
    Plot distribution of Z5D adaptive step sizes.
    
    Args:
        num_samples: Number of sample points
        output_file: Optional output file path
    """
    print(f"Analyzing step size distribution ({num_samples} samples)...")
    
    from z5d_curvature import z5d_step_size, standard_step_size
    
    np.random.seed(42)
    
    # Sample random points
    radius = np.random.uniform(0.5, 5.0, num_samples)
    theta = np.random.uniform(0, 2 * np.pi, num_samples)
    phi = np.random.uniform(0, np.pi, num_samples)
    
    points = np.stack([
        radius * np.sin(phi) * np.cos(theta),
        radius * np.sin(phi) * np.sin(theta),
        radius * np.cos(phi)
    ], axis=1)
    
    # Compute distances and step sizes
    distances = np.array([
        mandelbulb_distance_estimator(p, power=8.0) 
        for p in points
    ])
    
    z5d_steps = np.array([
        z5d_step_size(d, p) 
        for d, p in zip(distances, points)
    ])
    
    std_steps = np.array([
        standard_step_size(d) 
        for d in distances
    ])
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Step size distributions
    ax = axes[0, 0]
    ax.hist(z5d_steps, bins=50, alpha=0.7, label='Z5D', color='blue')
    ax.hist(std_steps, bins=50, alpha=0.7, label='Standard', color='red')
    ax.set_xlabel('Step Size')
    ax.set_ylabel('Frequency')
    ax.set_title('Step Size Distribution')
    ax.legend()
    ax.set_yscale('log')
    ax.grid(alpha=0.3)
    
    # Plot 2: Step size vs distance
    ax = axes[0, 1]
    ax.scatter(distances, z5d_steps, alpha=0.3, s=1, label='Z5D', color='blue')
    ax.scatter(distances, std_steps, alpha=0.3, s=1, label='Standard', color='red')
    ax.set_xlabel('Distance to Surface')
    ax.set_ylabel('Step Size')
    ax.set_title('Step Size vs Distance to Surface')
    ax.legend()
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(alpha=0.3)
    
    # Plot 3: Speedup factor
    ax = axes[1, 0]
    speedup = z5d_steps / std_steps
    ax.hist(speedup, bins=50, color='green', alpha=0.7)
    ax.axvline(np.mean(speedup), color='red', linestyle='--', 
               label=f'Mean: {np.mean(speedup):.2f}×')
    ax.set_xlabel('Speedup Factor (Z5D / Standard)')
    ax.set_ylabel('Frequency')
    ax.set_title('Per-Step Speedup Distribution')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Plot 4: Statistics
    ax = axes[1, 1]
    ax.axis('off')
    
    stats_text = f"""
    Step Size Statistics:
    
    Z5D Method:
      Mean:   {np.mean(z5d_steps):.4f}
      Median: {np.median(z5d_steps):.4f}
      Std:    {np.std(z5d_steps):.4f}
      Max:    {np.max(z5d_steps):.4f}
    
    Standard Method:
      Mean:   {np.mean(std_steps):.4f}
      Median: {np.median(std_steps):.4f}
      Std:    {np.std(std_steps):.4f}
      Max:    {np.max(std_steps):.4f}
    
    Speedup:
      Mean:   {np.mean(speedup):.2f}×
      Median: {np.median(speedup):.2f}×
      Max:    {np.max(speedup):.2f}×
    """
    
    ax.text(0.1, 0.5, stats_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.suptitle('Z5D Adaptive Step Size Analysis', y=0.995, fontsize=14)
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Saved to: {output_file}")
    else:
        plt.show()


def main():
    """Generate all visualizations."""
    
    output_dir = '../screenshots'
    os.makedirs(output_dir, exist_ok=True)
    
    print("Z5D Mandelbulb Curvature Visualization")
    print("=" * 60)
    print()
    
    # Generate visualizations
    plot_curvature_slice(
        z_slice=0.0,
        resolution=200,
        output_file=f'{output_dir}/curvature_slice.png'
    )
    print()
    
    plot_curvature_comparison(
        num_slices=5,
        output_file=f'{output_dir}/curvature_comparison.png'
    )
    print()
    
    plot_step_size_distribution(
        num_samples=2000,
        output_file=f'{output_dir}/step_size_analysis.png'
    )
    print()
    
    print("=" * 60)
    print("All visualizations generated successfully!")
    print(f"Output directory: {output_dir}")


if __name__ == '__main__':
    main()
