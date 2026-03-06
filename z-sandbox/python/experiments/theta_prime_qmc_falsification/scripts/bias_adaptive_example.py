#!/usr/bin/env python3
"""
Bias-Adaptive Example

Demonstrates adaptive α selection based on local curvature κ(n).
Shows how retiming parameter can adapt to geometric features of the
number being factored.

Hypothesis: Adaptive α based on κ(n) may improve performance vs fixed α.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import numpy as np
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils.z_framework import kappa
from mean_one_retiming import interval_biased_batch


def adaptive_alpha(n: int, alpha_base: float = 0.15, scale_factor: float = 0.5) -> float:
    """
    Compute adaptive α based on curvature κ(n).
    
    α(n) = α_base * (1 + scale_factor * κ(n))
    
    Intuition: Higher curvature regions may benefit from stronger retiming.
    
    Args:
        n: Candidate value
        alpha_base: Base α value
        scale_factor: Scaling factor for κ influence
        
    Returns:
        Adaptive α value clipped to [0.05, 0.20]
    """
    kappa_val = kappa(n)
    alpha_adapted = alpha_base * (1.0 + scale_factor * kappa_val)
    
    # Clip to valid range
    return np.clip(alpha_adapted, 0.05, 0.20)


def demonstrate_adaptive_alpha(
    N: int,
    n_candidates: int = 1000,
    output_dir: Path = None
):
    """
    Demonstrate adaptive α selection around √N.
    
    Args:
        N: RSA modulus
        n_candidates: Number of candidates to generate
        output_dir: Optional output directory for plots
    """
    print("Bias-Adaptive α Demonstration")
    print("=" * 70)
    print(f"  N: {N}")
    print(f"  N bit length: {N.bit_length()}")
    print()
    
    sqrt_N = int(math.sqrt(N))
    
    # Generate candidate range around √N (use floats to avoid overflow)
    spread = 0.05
    candidates = np.linspace(
        float(sqrt_N) * (1 - spread),
        float(sqrt_N) * (1 + spread),
        n_candidates
    ).astype(np.int64)
    
    # Compute curvatures
    kappa_vals = np.array([kappa(c) for c in candidates])
    
    # Compute adaptive alphas
    alpha_fixed = 0.15
    alpha_adaptive = np.array([adaptive_alpha(c, alpha_base=0.15, scale_factor=0.5) for c in candidates])
    
    print(f"Fixed α: {alpha_fixed}")
    print(f"Adaptive α range: [{alpha_adaptive.min():.4f}, {alpha_adaptive.max():.4f}]")
    print(f"Adaptive α mean: {alpha_adaptive.mean():.4f}")
    print(f"κ(n) range: [{kappa_vals.min():.6f}, {kappa_vals.max():.6f}]")
    
    # Create visualization
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
        
        # Normalize distances for plotting (avoid overflow with large numbers)
        distances_normalized = (candidates.astype(float) - float(sqrt_N)) / float(sqrt_N) * 100  # as percentage
        
        # Plot 1: κ(n) vs position
        ax1.plot(distances_normalized, kappa_vals, 'b-', linewidth=1, alpha=0.7)
        ax1.set_xlabel('Distance from √N (%)')
        ax1.set_ylabel('κ(n)')
        ax1.set_title(f'Curvature κ(n) around √N (N bits: {N.bit_length()})')
        ax1.grid(True, alpha=0.3)
        ax1.axvline(0, color='r', linestyle='--', alpha=0.5, label='√N')
        ax1.legend()
        
        # Plot 2: Adaptive α vs position
        ax2.plot(distances_normalized, alpha_adaptive, 'g-', linewidth=1.5, alpha=0.7, label='Adaptive α')
        ax2.axhline(alpha_fixed, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label='Fixed α')
        ax2.set_xlabel('Distance from √N (%)')
        ax2.set_ylabel('α')
        ax2.set_title('Adaptive α vs Fixed α')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_ylim([0.04, 0.21])
        
        # Plot 3: κ(n) vs α relationship
        ax3.scatter(kappa_vals, alpha_adaptive, c=distances_normalized, 
                   cmap='coolwarm', alpha=0.6, s=10)
        ax3.set_xlabel('κ(n)')
        ax3.set_ylabel('α')
        ax3.set_title('Adaptive α as function of κ(n)')
        ax3.grid(True, alpha=0.3)
        cbar = plt.colorbar(ax3.collections[0], ax=ax3)
        cbar.set_label('Distance from √N (%)')
        
        plt.tight_layout()
        output_file = output_dir / "bias_adaptive_example.png"
        plt.savefig(output_file, dpi=150)
        print(f"\nSaved plot to {output_file}")
        plt.close()
    
    # Generate sample intervals with fixed vs adaptive
    print("\nGenerating sample intervals:")
    n_samples = 1000
    base_interval = 1.0
    
    # Fixed α
    intervals_fixed = interval_biased_batch(base_interval, n_samples, alpha=alpha_fixed, seed=42)
    
    # Adaptive α (use mean adaptive for fair comparison)
    alpha_mean = alpha_adaptive.mean()
    intervals_adaptive = interval_biased_batch(base_interval, n_samples, alpha=alpha_mean, seed=42)
    
    print(f"\nFixed α={alpha_fixed:.3f}:")
    print(f"  Mean: {intervals_fixed.mean():.6f} (target: {base_interval:.6f})")
    print(f"  Std:  {intervals_fixed.std():.6f}")
    print(f"  Range: [{intervals_fixed.min():.4f}, {intervals_fixed.max():.4f}]")
    
    print(f"\nAdaptive α={alpha_mean:.3f}:")
    print(f"  Mean: {intervals_adaptive.mean():.6f} (target: {base_interval:.6f})")
    print(f"  Std:  {intervals_adaptive.std():.6f}")
    print(f"  Range: [{intervals_adaptive.min():.4f}, {intervals_adaptive.max():.4f}]")


if __name__ == "__main__":
    # Use RSA-100 for demonstration
    RSA_100 = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000795641669258795963466392520424679069476232232770723
    
    output_dir = Path(__file__).parent.parent / "plots"
    
    demonstrate_adaptive_alpha(
        N=RSA_100,
        n_candidates=1000,
        output_dir=output_dir
    )
    
    print("\n" + "=" * 70)
    print("Demonstration complete.")
