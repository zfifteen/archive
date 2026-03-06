#!/usr/bin/env python3
"""
Debug chirality computation to understand why S_b is too low
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sympy import isprime
import sys
import os
sys.path.append('.')

from core.domain import DiscreteZetaShift
from task3_helical_embeddings import generate_helical_embeddings, fit_fourier_series

def debug_angles_distribution():
    """Debug the angular distribution of embeddings"""
    
    # Generate small sample for debugging
    embeddings, _ = generate_helical_embeddings(2, 50)
    
    # Separate primes and composites
    primes = [e for e in embeddings if e['is_prime']]
    composites = [e for e in embeddings if not e['is_prime']]
    
    print(f"Debugging with {len(primes)} primes, {len(composites)} composites")
    
    # Extract angles
    def get_angles_and_coords(data):
        angles = []
        xs, ys = [], []
        for d in data:
            theta = np.arctan2(d['y'], d['x'])
            if theta < 0:
                theta += 2 * np.pi
            angles.append(theta)
            xs.append(d['x'])
            ys.append(d['y'])
        return np.array(angles), np.array(xs), np.array(ys)
    
    primes_angles, primes_x, primes_y = get_angles_and_coords(primes)
    comp_angles, comp_x, comp_y = get_angles_and_coords(composites)
    
    print(f"Primes angles range: [{np.min(primes_angles):.3f}, {np.max(primes_angles):.3f}]")
    print(f"Composites angles range: [{np.min(comp_angles):.3f}, {np.max(comp_angles):.3f}]")
    
    # Plot angular distributions
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # X-Y scatter
    axes[0,0].scatter(comp_x, comp_y, c='blue', alpha=0.6, label='Composites')
    axes[0,0].scatter(primes_x, primes_y, c='red', alpha=0.8, label='Primes')
    axes[0,0].set_xlabel('X')
    axes[0,0].set_ylabel('Y')
    axes[0,0].set_title('X-Y Coordinates')
    axes[0,0].legend()
    axes[0,0].axis('equal')
    
    # Angular histograms
    axes[0,1].hist(primes_angles, bins=20, alpha=0.7, label='Primes', color='red')
    axes[0,1].hist(comp_angles, bins=20, alpha=0.7, label='Composites', color='blue')
    axes[0,1].set_xlabel('Angle (radians)')
    axes[0,1].set_ylabel('Count')
    axes[0,1].set_title('Angular Distribution')
    axes[0,1].legend()
    
    # Test different Fourier fitting approaches
    
    # Approach 1: Fit to uniform distribution (original)
    _, S_b_1, b1 = fit_fourier_series(primes_angles, M=5)
    
    # Approach 2: Fit to histogram density
    hist, bin_edges = np.histogram(primes_angles, bins=20)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    normalized_hist = hist / np.sum(hist)
    
    # Interpolate to get density at each angle
    density = np.interp(primes_angles, bin_centers, normalized_hist)
    
    # Create design matrix
    n_points = len(primes_angles)
    M = 5
    X = np.ones((n_points, 1 + 2*M))
    for m in range(1, M + 1):
        X[:, m] = np.cos(m * primes_angles)
        X[:, M + m] = np.sin(m * primes_angles)
    
    try:
        coeffs_2 = np.linalg.lstsq(X, density, rcond=None)[0]
        b_coeffs_2 = coeffs_2[M+1:2*M+1]
        S_b_2 = np.sum(np.abs(b_coeffs_2))
    except:
        S_b_2 = 0.0
        b_coeffs_2 = np.zeros(M)
    
    # Approach 3: Use angular velocity/chirality measure
    # Sort by angle and compute angular differences
    sorted_indices = np.argsort(primes_angles)
    sorted_angles = primes_angles[sorted_indices]
    
    # Compute angular increments
    angle_diffs = np.diff(sorted_angles)
    # Handle wrap-around
    if len(angle_diffs) > 0:
        angle_diffs = np.append(angle_diffs, 2*np.pi + sorted_angles[0] - sorted_angles[-1])
    
    # Compute asymmetry in angular increments
    if len(angle_diffs) > 0:
        S_b_3 = np.std(angle_diffs) / np.mean(angle_diffs) if np.mean(angle_diffs) > 0 else 0
    else:
        S_b_3 = 0.0
    
    print(f"\nFourier fitting results:")
    print(f"Approach 1 (uniform): S_b = {S_b_1:.6f}")
    print(f"Approach 2 (density): S_b = {S_b_2:.6f}")
    print(f"Approach 3 (asymmetry): S_b = {S_b_3:.6f}")
    
    print(f"\nFourier coefficients (approach 1):")
    print(f"b_coeffs = {b1}")
    
    # Plot Fourier series fit
    theta_fine = np.linspace(0, 2*np.pi, 1000)
    
    # Reconstruct from approach 1
    fourier_1 = np.ones_like(theta_fine) * coeffs_2[0] if len(coeffs_2) > 0 else np.ones_like(theta_fine)
    if len(coeffs_2) > 2*M:
        for m in range(1, M + 1):
            fourier_1 += coeffs_2[m] * np.cos(m * theta_fine)
            fourier_1 += coeffs_2[M + m] * np.sin(m * theta_fine)
    
    axes[1,0].plot(theta_fine, fourier_1, 'g-', label='Fourier fit')
    axes[1,0].hist(primes_angles, bins=20, density=True, alpha=0.7, color='red', label='Data')
    axes[1,0].set_xlabel('Angle (radians)')
    axes[1,0].set_ylabel('Density')
    axes[1,0].set_title('Fourier Series Fit')
    axes[1,0].legend()
    
    # Polar plot
    axes[1,1].remove()
    axes[1,1] = fig.add_subplot(2, 2, 4, projection='polar')
    axes[1,1].scatter(comp_angles, np.ones_like(comp_angles), c='blue', alpha=0.6, s=30, label='Composites')
    axes[1,1].scatter(primes_angles, np.ones_like(primes_angles), c='red', alpha=0.8, s=50, label='Primes')
    axes[1,1].set_title('Polar Distribution')
    axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig('debug_chirality.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved debug plot to debug_chirality.png")
    
    return S_b_1, S_b_2, S_b_3

if __name__ == "__main__":
    debug_angles_distribution()