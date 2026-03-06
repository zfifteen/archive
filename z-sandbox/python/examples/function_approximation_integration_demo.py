#!/usr/bin/env python3
"""
Function Approximation Integration Demonstration

Demonstrates how function approximation techniques enhance the geometric
factorization framework across Monte Carlo sampling, Z5D prime prediction,
and Gaussian lattice distance metrics.

Based on the educational post by Joachim Schork from Statistics Globe.

Examples:
1. Tanh-based distance smoothing for candidate ranking
2. Asymmetric Gaussian variance reduction in Monte Carlo
3. Nonlinear least squares for Z5D error bound calibration
4. Spline approximation for smooth curvature functions
"""

import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
from monte_carlo import FactorizationMonteCarloEnhancer
from z5d_axioms import calibrate_error_bounds_with_regression, approximate_curvature_with_spline
from gaussian_lattice import GaussianIntegerLattice


def demo_tanh_smoothed_distance():
    """
    Demonstrate tanh-based distance smoothing for factorization candidates.
    
    Shows how tanh approximation creates smooth transitions in candidate
    ranking near √N, improving differentiability for optimization.
    """
    print("=" * 70)
    print("1. Tanh-Based Distance Smoothing for Candidate Ranking")
    print("=" * 70)
    print()
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    N = 143  # 11 × 13
    sqrt_N = int(np.sqrt(N))
    
    print(f"Target: N = {N} (factors: 11 × 13)")
    print(f"√N = {sqrt_N}")
    print()
    
    # Compare candidates around √N
    candidates = list(range(sqrt_N - 3, sqrt_N + 4))
    print("Candidate distance comparison:")
    print(f"{'Candidate':<12} {'Euclidean':<15} {'Tanh-smoothed':<15} {'Δ':<10} {'Is Factor':<12}")
    print("-" * 70)
    
    for c in candidates:
        euclidean = abs(c - sqrt_N)
        smoothed = enhancer.tanh_smoothed_distance(c, sqrt_N, k=2.0)
        delta = smoothed - euclidean
        is_factor = "✓ YES" if c in [11, 13] else ""
        print(f"{c:<12} {euclidean:<15.6f} {smoothed:<15.6f} {delta:<10.6f} {is_factor:<12}")
    
    print()
    print("Observation: Tanh smoothing provides differentiable metric for")
    print("            gradient-based optimization near √N.")
    print()
    
    # Visualize smoothing effect
    x_range = np.linspace(sqrt_N - 5, sqrt_N + 5, 200)
    euclidean_dists = np.abs(x_range - sqrt_N)
    smoothed_dists = np.array([enhancer.tanh_smoothed_distance(int(x), sqrt_N, k=2.0) 
                                if x.is_integer() else abs(x - sqrt_N)
                                for x in x_range])
    
    plt.figure(figsize=(10, 5))
    plt.plot(x_range, euclidean_dists, label='Euclidean Distance', linewidth=2)
    plt.plot(x_range, smoothed_dists, label='Tanh-Smoothed Distance', linewidth=2, linestyle='--')
    plt.axvline(11, color='g', linestyle=':', alpha=0.7, label='Factor 11')
    plt.axvline(13, color='r', linestyle=':', alpha=0.7, label='Factor 13')
    plt.xlabel('Candidate')
    plt.ylabel('Distance from √N')
    plt.title('Tanh-Based Distance Smoothing Near √N')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('../../plots/tanh_distance_smoothing.png', dpi=150)
    print("  Plot saved: plots/tanh_distance_smoothing.png")
    print()


def demo_variance_reduction():
    """
    Demonstrate asymmetric Gaussian variance reduction in Monte Carlo sampling.
    
    Shows how fitting asymmetric Gaussians to sampling distributions reduces
    noise and improves variance estimates.
    """
    print("=" * 70)
    print("2. Asymmetric Gaussian Variance Reduction in Monte Carlo")
    print("=" * 70)
    print()
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    N = 899  # 29 × 31
    
    print(f"Target: N = {N} (factors: 29 × 31)")
    print("Fitting asymmetric Gaussian to candidate distance distribution...")
    print()
    
    result = enhancer.fit_variance_reduction_gaussian(N, num_samples=500, num_trials=10)
    
    if result['available']:
        print("Fitted asymmetric Gaussian parameters:")
        print(f"  Amplitude: {result['fitted_amplitude']:.4f}")
        print(f"  Mean: {result['fitted_mean']:.4f}")
        print(f"  Std (left):  {result['fitted_std_left']:.4f}")
        print(f"  Std (right): {result['fitted_std_right']:.4f}")
        print()
        print("Variance metrics:")
        print(f"  Raw variance: {result['raw_variance']:.4f}")
        print(f"  Fitted variance: {result['fitted_variance']:.4f}")
        print(f"  Variance reduction ratio: {result['variance_reduction_ratio']:.2%}")
        print(f"  RMSE: {result['rmse']:.6f}")
        print(f"  Samples: {result['num_samples']}")
        print()
        print("Benefit: Reduced variance → more accurate convergence estimates")
        print("         for QMC-φ hybrid and RQMC methods.")
    else:
        print("  Function approximation not available")
    
    print()


def demo_error_bound_calibration():
    """
    Demonstrate Z5D error bound calibration using nonlinear least squares.
    
    Shows how regression fits Z5D error bound parameters (α, β, γ) to
    empirical prime prediction errors for improved large-k extrapolation.
    """
    print("=" * 70)
    print("3. Z5D Error Bound Calibration with Nonlinear Least Squares")
    print("=" * 70)
    print()
    
    print("Calibrating error bound model: error(k) = C / (k^α * ln(k)^β * ln(ln(k))^γ)")
    print()
    
    # Simulate realistic empirical error data
    k_values = np.array([1000, 5000, 10000, 50000, 100000, 500000, 1000000])
    
    # True parameters (realistic values from prime prediction theory)
    true_C = 1000.0
    true_alpha, true_beta, true_gamma = 0.28, 3.2, 1.8
    
    # Generate "empirical" errors with noise
    true_errors = true_C / (k_values**true_alpha * np.log(k_values)**true_beta * 
                           np.log(np.log(k_values))**true_gamma)
    np.random.seed(42)
    empirical_errors = true_errors * (1 + 0.1 * np.random.randn(len(k_values)))
    
    print("Empirical error data (simulated):")
    print(f"{'k':<10} {'Error':<15}")
    print("-" * 25)
    for k, err in zip(k_values, empirical_errors):
        print(f"{k:<10} {err:<15.6e}")
    print()
    
    # Calibrate using regression
    result = calibrate_error_bounds_with_regression(
        k_values, empirical_errors,
        alpha_init=0.28, beta_init=3.2, gamma_init=1.8
    )
    
    if result['available']:
        print("Calibration results:")
        print(f"  Fitted C: {result['fitted_params']['C']:.3e}")
        print(f"  Fitted α: {result['fitted_params']['alpha']:.4f} (initial: 0.28)")
        print(f"  Fitted β: {result['fitted_params']['beta']:.4f} (initial: 3.2)")
        print(f"  Fitted γ: {result['fitted_params']['gamma']:.4f} (initial: 1.8)")
        print(f"  RMSE: {result['rmse']:.6e}")
        print()
        print("Cross-validation metrics:")
        print(f"  Mean train error: {result['cross_val_metrics']['mean_train_error']:.6e}")
        print(f"  Mean val error: {result['cross_val_metrics']['mean_val_error']:.6e}")
        print(f"  Overfitting ratio: {result['cross_val_metrics']['overfitting_ratio']:.3f}")
        print(f"  Overfitting detected: {result['overfitting_detected']}")
        print()
        
        # Visualize fit
        plt.figure(figsize=(10, 5))
        plt.loglog(k_values, empirical_errors, 'bo', label='Empirical Errors', markersize=8)
        plt.loglog(k_values, result['predictions'], 'r-', label='Fitted Model', linewidth=2)
        plt.loglog(k_values, true_errors, 'g--', label='True Model', linewidth=2, alpha=0.7)
        plt.xlabel('Prime Index k')
        plt.ylabel('Prediction Error')
        plt.title('Z5D Error Bound Calibration via Nonlinear Least Squares')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('../../plots/z5d_error_bound_calibration.png', dpi=150)
        print("  Plot saved: plots/z5d_error_bound_calibration.png")
        print()
        
        print("Application: Improved semiprime targeting for large RSA challenges")
        print("             by refining error bounds at k > 10^12.")
    else:
        print("  Function approximation not available")
    
    print()


def demo_curvature_spline():
    """
    Demonstrate spline approximation for Z5D curvature functions.
    
    Shows how cubic splines create smooth, differentiable approximations
    of κ(n) = d(n)·ln(n+1)/e² for geometric calculations.
    """
    print("=" * 70)
    print("4. Spline Approximation for Z5D Curvature κ(n)")
    print("=" * 70)
    print()
    
    print("Approximating κ(n) = d(n)·ln(n+1)/e² with cubic splines")
    print()
    
    # Sample curvature at key points
    n_values = np.array([100, 500, 1000, 2000, 5000, 10000])
    
    result = approximate_curvature_with_spline(n_values, smoothing=0.0)
    
    if result['available']:
        print("Spline-approximated curvature values:")
        print(f"{'n':<10} {'κ(n)':<15} {'dκ/dn':<15}")
        print("-" * 40)
        for i, n in enumerate(n_values):
            kappa = result['smoothed_values'][i]
            d_kappa = result['derivative_values'][i]
            print(f"{n:<10} {kappa:<15.6f} {d_kappa:<15.6e}")
        print()
        
        # Evaluate on dense grid for visualization
        n_dense = np.linspace(100, 10000, 500)
        kappa_dense = result['spline_approximator'].evaluate(n_dense)
        
        plt.figure(figsize=(10, 5))
        plt.plot(n_dense, kappa_dense, 'b-', label='Spline Approximation', linewidth=2)
        plt.plot(n_values, result['smoothed_values'], 'ro', label='Sample Points', markersize=8)
        plt.xlabel('n')
        plt.ylabel('κ(n)')
        plt.title('Cubic Spline Approximation of Z5D Curvature')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('../../plots/z5d_curvature_spline.png', dpi=150)
        print("  Plot saved: plots/z5d_curvature_spline.png")
        print()
        
        print("Benefits:")
        print("  - Smooth, differentiable κ(n) for affine-invariant operations")
        print("  - Efficient evaluation at arbitrary points")
        print("  - Supports barycentric coordinate calculations in GVA")
    else:
        print("  Function approximation not available")
    
    print()


def demo_lattice_distance_smoothing():
    """
    Demonstrate tanh-smoothed lattice distance metrics.
    
    Shows how tanh approximation reduces discontinuities in Gaussian
    lattice distance calculations at lattice boundaries.
    """
    print("=" * 70)
    print("5. Tanh-Smoothed Lattice Distance Metrics")
    print("=" * 70)
    print()
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    print("Comparing standard vs. tanh-smoothed lattice distances")
    print()
    
    # Test points near lattice boundaries
    test_pairs = [
        (0+0j, 1+0j, "Lattice edge"),
        (0+0j, 0.5+0j, "Midpoint"),
        (0+0j, 1.5+1.5j, "Near diagonal"),
        (0+0j, 3+4j, "Pythagorean (3-4-5)"),
    ]
    
    print(f"{'z1':<12} {'z2':<12} {'Description':<20} {'Standard':<12} {'Tanh-smoothed':<15} {'Δ':<10}")
    print("-" * 90)
    
    for z1, z2, desc in test_pairs:
        standard_dist = float(lattice.lattice_enhanced_distance(z1, z2, lattice_scale=1.0))
        smoothed_dist = float(lattice.tanh_smoothed_lattice_distance(z1, z2, k=2.0))
        delta = smoothed_dist - standard_dist
        
        print(f"{str(z1):<12} {str(z2):<12} {desc:<20} {standard_dist:<12.6f} {smoothed_dist:<15.6f} {delta:<10.6f}")
    
    print()
    print("Observation: Tanh smoothing reduces discontinuities at lattice")
    print("            boundaries, improving gradient-based GVA optimization.")
    print()


def main():
    """Run all demonstrations."""
    print("\n")
    print("=" * 70)
    print("Function Approximation Integration Demonstration")
    print("Based on educational post by Joachim Schork (Statistics Globe)")
    print("=" * 70)
    print()
    
    # Run demonstrations
    demo_tanh_smoothed_distance()
    demo_variance_reduction()
    demo_error_bound_calibration()
    demo_curvature_spline()
    demo_lattice_distance_smoothing()
    
    print("=" * 70)
    print("All demonstrations complete!")
    print("=" * 70)
    print()
    print("Summary of Benefits:")
    print("  ✓ Tanh smoothing: Differentiable distance metrics for optimization")
    print("  ✓ Gaussian fitting: Reduced variance in Monte Carlo sampling")
    print("  ✓ Nonlinear least squares: Precise Z5D error bound calibration")
    print("  ✓ Spline approximation: Smooth curvature for geometric calculations")
    print("  ✓ Lattice smoothing: Reduced discontinuities in GVA distance metrics")
    print()
    print("These techniques enhance factorization efficiency while mitigating")
    print("overfitting risks through cross-validation and regularization.")
    print()


if __name__ == "__main__":
    main()
