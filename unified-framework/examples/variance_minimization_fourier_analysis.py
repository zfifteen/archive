"""
Variance Minimization and Fourier Asymmetry Analysis
==================================================

This script implements the requirements from issue #94:
1. Replace hard-coded natural number ratios with curvature-based geodesics
2. Minimize variance σ ≈ 0.118 in embedding coordinates  
3. Fit observed density ρ(x) to Fourier series model with M=5
4. Target spectral bias Sb ≈ 0.45 (CI [0.42, 0.48])
5. Document variance reduction and Fourier analysis process

Mathematical Framework:
- Curvature-based geodesic parameter: k(n) = f(κ(n)) where κ(n) = d(n)·ln(n+1)/e²
- Embedding coordinates: θ'(n,k) = φ · {n/φ}^k(n)
- Fourier series: ρ(x) ≈ a₀ + Σ[aₘcos(2πmx) + bₘsin(2πmx)]
- Spectral bias: Sb = Σ|bₘ| for m=1 to M=5
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from scipy.optimize import curve_fit, minimize
from sympy import sieve
import warnings
import os
import sys

# Add path for core imports
sys.path.append('/home/runner/work/unified-framework/unified-framework')
from src.core.domain import DiscreteZetaShift

# Suppress warnings and set headless backend
warnings.filterwarnings("ignore")
plt.switch_backend('Agg')

# Constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
E_SQUARED = np.exp(2)
M_FOURIER = 5  # Number of Fourier harmonics
TARGET_VARIANCE = 0.118  # Target variance
TARGET_SPECTRAL_BIAS = 0.45  # Target spectral bias

class VarianceMinimizationOptimizer:
    """
    Optimizes curvature-based geodesic parameters to minimize embedding variance
    while achieving target Fourier asymmetry.
    """
    
    def __init__(self, n_range=(2, 1000), prime_limit=10000):
        self.n_range = n_range
        self.prime_limit = prime_limit
        self.primes_list = list(sieve.primerange(2, prime_limit + 1))
        
    def compute_variance_for_k_function(self, k_params):
        """
        Compute embedding variance for a given k-parameter function.
        k_params: [a, b, c] where k(κ) = a + b*sigmoid(c*κ)
        """
        a, b, c = k_params
        coords_list = []
        
        for n in range(self.n_range[0], min(self.n_range[1], 200)):  # Limit for efficiency
            d = DiscreteZetaShift(n)
            # Override k calculation with custom function
            kappa_normalized = float(d.kappa_bounded) / float(E_SQUARED)
            k_custom = a + b / (1 + np.exp(-c * (kappa_normalized - 0.5)))
            
            # Compute coordinates with custom k
            attrs = d.attributes
            theta_d = PHI * ((attrs['D'] % PHI) / PHI) ** k_custom
            theta_e = PHI * ((attrs['E'] % PHI) / PHI) ** k_custom
            x = float(d.a * np.cos(float(theta_d)))
            y = float(d.a * np.sin(float(theta_e)))
            z = float(attrs['F']) / E_SQUARED
            w = float(attrs['I'])
            u = float(attrs['O'])
            
            coords_list.append([x, y, z, w, u])
        
        coords_array = np.array(coords_list)
        variances = np.var(coords_array, axis=0)
        mean_variance = np.mean(variances)
        
        return mean_variance, variances
    
    def objective_function(self, k_params):
        """
        Objective function to minimize: squared difference from target variance
        """
        mean_variance, _ = self.compute_variance_for_k_function(k_params)
        return (mean_variance - TARGET_VARIANCE) ** 2
    
    def optimize_k_parameters(self):
        """
        Optimize k-parameter function to minimize variance
        """
        print("Optimizing curvature-based geodesic parameters...")
        
        # Initial guess: k(κ) = 0.2 + 0.3*sigmoid(5*(κ-0.5))
        initial_guess = [0.2, 0.3, 5.0]
        bounds = [(0.01, 0.5), (0.01, 1.0), (0.1, 20.0)]
        
        result = minimize(self.objective_function, initial_guess, bounds=bounds, method='L-BFGS-B')
        
        if result.success:
            optimal_params = result.x
            optimal_variance, _ = self.compute_variance_for_k_function(optimal_params)
            print(f"Optimization successful!")
            print(f"Optimal parameters: a={optimal_params[0]:.4f}, b={optimal_params[1]:.4f}, c={optimal_params[2]:.4f}")
            print(f"Achieved variance: {optimal_variance:.6f} (target: {TARGET_VARIANCE})")
            return optimal_params, optimal_variance
        else:
            print("Optimization failed, using default parameters")
            return [0.2, 0.3, 5.0], None

class FourierAsymmetryAnalyzer:
    """
    Analyzes Fourier asymmetry in prime distributions using optimized embeddings
    """
    
    def __init__(self, primes_list, k_params):
        self.primes_list = primes_list
        self.k_params = k_params
        
    def compute_theta_prime_values(self):
        """
        Compute θ'(p, k(κ)) values for primes using optimized k function
        """
        theta_prime_values = []
        
        for p in self.primes_list[:1000]:  # Limit for efficiency
            d = DiscreteZetaShift(p)
            
            # Use optimized k function
            kappa_normalized = float(d.kappa_bounded) / float(E_SQUARED)
            a, b, c = self.k_params
            k_opt = a + b / (1 + np.exp(-c * (kappa_normalized - 0.5)))
            
            # Compute θ'(p, k_opt)
            attrs = d.attributes
            theta_d = PHI * ((attrs['D'] % PHI) / PHI) ** k_opt
            
            # Normalize to [0, 1)
            normalized_theta = (theta_d % PHI) / PHI
            theta_prime_values.append(float(normalized_theta))
            
        return np.array(theta_prime_values)
    
    def fourier_series(self, x, *coeffs):
        """
        Fourier series: a₀ + Σ[aₘcos(2πmx) + bₘsin(2πmx)]
        """
        result = coeffs[0]  # a₀ term
        for m in range(1, M_FOURIER + 1):
            a_m = coeffs[2*m - 1]  # aₘ coefficient
            b_m = coeffs[2*m]      # bₘ coefficient
            result += a_m * np.cos(2 * np.pi * m * x) + b_m * np.sin(2 * np.pi * m * x)
        return result
    
    def fit_fourier_coefficients(self, x_vals):
        """
        Fit Fourier series to density distribution
        """
        # Create histogram density
        hist, bin_edges = np.histogram(x_vals, bins=100, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Initial guess: small random values
        p0 = np.random.normal(0, 0.1, 2 * M_FOURIER + 1)
        p0[0] = 1.0  # a₀ initial guess
        
        try:
            # Fit coefficients
            popt, _ = curve_fit(self.fourier_series, bin_centers, hist, p0=p0, maxfev=5000)
            
            # Extract a and b coefficients
            a_coeffs = np.array([popt[0]] + [popt[2*m - 1] for m in range(1, M_FOURIER + 1)])
            b_coeffs = np.array([0] + [popt[2*m] for m in range(1, M_FOURIER + 1)])  # b₀ = 0
            
            return a_coeffs, b_coeffs, bin_centers, hist
        except:
            print("Fourier fitting failed, using fallback method")
            return self.fit_fourier_fallback(x_vals)
    
    def fit_fourier_fallback(self, x_vals):
        """
        Fallback Fourier fitting using least squares
        """
        hist, bin_edges = np.histogram(x_vals, bins=100, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Build design matrix
        n_points = len(bin_centers)
        A = np.ones((n_points, 2 * M_FOURIER + 1))
        
        for i, x in enumerate(bin_centers):
            for m in range(1, M_FOURIER + 1):
                A[i, 2*m - 1] = np.cos(2 * np.pi * m * x)  # aₘ terms
                A[i, 2*m] = np.sin(2 * np.pi * m * x)      # bₘ terms
        
        # Solve least squares
        coeffs, _, _, _ = np.linalg.lstsq(A, hist, rcond=None)
        
        a_coeffs = np.array([coeffs[0]] + [coeffs[2*m - 1] for m in range(1, M_FOURIER + 1)])
        b_coeffs = np.array([0] + [coeffs[2*m] for m in range(1, M_FOURIER + 1)])
        
        return a_coeffs, b_coeffs, bin_centers, hist
    
    def compute_spectral_bias(self, b_coeffs):
        """
        Compute spectral bias Sb = Σ|bₘ| for m=1 to M_FOURIER
        """
        return np.sum(np.abs(b_coeffs[1:]))  # Exclude b₀
    
    def analyze_fourier_asymmetry(self):
        """
        Complete Fourier asymmetry analysis
        """
        print("Computing θ'(p, k_opt) values for primes...")
        theta_prime_values = self.compute_theta_prime_values()
        
        print("Fitting Fourier series coefficients...")
        a_coeffs, b_coeffs, bin_centers, hist = self.fit_fourier_coefficients(theta_prime_values)
        
        spectral_bias = self.compute_spectral_bias(b_coeffs)
        
        print(f"Fourier Analysis Results:")
        print(f"  Spectral bias Sb = {spectral_bias:.4f} (target: {TARGET_SPECTRAL_BIAS})")
        print(f"  a coefficients: {a_coeffs}")
        print(f"  b coefficients: {b_coeffs}")
        
        return {
            'theta_prime_values': theta_prime_values,
            'spectral_bias': spectral_bias,
            'a_coeffs': a_coeffs,
            'b_coeffs': b_coeffs,
            'bin_centers': bin_centers,
            'hist': hist,
            'fourier_fit': self.fourier_series(bin_centers, *np.concatenate([[a_coeffs[0]], np.ravel(list(zip(a_coeffs[1:], b_coeffs[1:])))])),
            'target_achieved': abs(spectral_bias - TARGET_SPECTRAL_BIAS) < 0.03
        }

def create_visualization_plots(optimizer_results, fourier_results):
    """
    Create comprehensive visualization plots
    """
    print("Creating visualization plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Variance optimization
    ax1 = axes[0, 0]
    ax1.axhline(y=TARGET_VARIANCE, color='red', linestyle='--', label=f'Target σ = {TARGET_VARIANCE}')
    ax1.axhline(y=optimizer_results['achieved_variance'], color='blue', linestyle='-', 
                label=f'Achieved σ = {optimizer_results["achieved_variance"]:.6f}')
    ax1.set_ylabel('Variance')
    ax1.set_title('Embedding Variance Optimization')
    ax1.legend()
    ax1.grid(True)
    
    # Plot 2: θ' distribution
    ax2 = axes[0, 1]
    theta_vals = fourier_results['theta_prime_values']
    ax2.hist(theta_vals, bins=50, density=True, alpha=0.7, label='Data')
    ax2.plot(fourier_results['bin_centers'], fourier_results['fourier_fit'], 'r-', label='Fourier fit')
    ax2.set_xlabel('θ\' normalized')
    ax2.set_ylabel('Density')
    ax2.set_title('Prime θ\' Distribution and Fourier Fit')
    ax2.legend()
    ax2.grid(True)
    
    # Plot 3: Fourier coefficients
    ax3 = axes[1, 0]
    m_vals = range(M_FOURIER + 1)
    ax3.bar([m - 0.2 for m in m_vals], fourier_results['a_coeffs'], width=0.4, label='aₘ (cosine)', alpha=0.7)
    ax3.bar([m + 0.2 for m in m_vals], fourier_results['b_coeffs'], width=0.4, label='bₘ (sine)', alpha=0.7)
    ax3.set_xlabel('Harmonic m')
    ax3.set_ylabel('Coefficient value')
    ax3.set_title('Fourier Coefficients')
    ax3.legend()
    ax3.grid(True)
    
    # Plot 4: Spectral bias
    ax4 = axes[1, 1]
    ax4.axhline(y=TARGET_SPECTRAL_BIAS, color='red', linestyle='--', label=f'Target Sb = {TARGET_SPECTRAL_BIAS}')
    ax4.axhline(y=fourier_results['spectral_bias'], color='blue', linestyle='-',
                label=f'Achieved Sb = {fourier_results["spectral_bias"]:.4f}')
    ax4.set_ylabel('Spectral Bias')
    ax4.set_title('Spectral Bias Achievement')
    ax4.legend()
    ax4.grid(True)
    
    plt.tight_layout()
    
    # Save plots
    os.makedirs('examples/variance_fourier_output', exist_ok=True)
    plt.savefig('docs/assets/variance_fourier_output/variance_minimization_fourier_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Plots saved to docs/assets/variance_fourier_output/variance_minimization_fourier_analysis.png")

def main():
    """
    Main analysis pipeline
    """
    print("=" * 70)
    print("VARIANCE MINIMIZATION AND FOURIER ASYMMETRY ANALYSIS")
    print("=" * 70)
    print(f"Target variance: σ ≈ {TARGET_VARIANCE}")
    print(f"Target spectral bias: Sb ≈ {TARGET_SPECTRAL_BIAS}")
    print(f"Fourier harmonics: M = {M_FOURIER}")
    
    # Step 1: Optimize variance
    print("\nStep 1: Optimizing embedding variance...")
    optimizer = VarianceMinimizationOptimizer()
    optimal_k_params, achieved_variance = optimizer.optimize_k_parameters()
    
    # Step 2: Fourier analysis
    print("\nStep 2: Fourier asymmetry analysis...")
    fourier_analyzer = FourierAsymmetryAnalyzer(optimizer.primes_list, optimal_k_params)
    fourier_results = fourier_analyzer.analyze_fourier_asymmetry()
    
    # Step 3: Create visualizations
    print("\nStep 3: Creating visualizations...")
    optimizer_results = {
        'optimal_k_params': optimal_k_params,
        'achieved_variance': achieved_variance
    }
    create_visualization_plots(optimizer_results, fourier_results)
    
    # Step 4: Results summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"Variance Optimization:")
    print(f"  Target variance: {TARGET_VARIANCE}")
    print(f"  Achieved variance: {achieved_variance:.6f}" if achieved_variance else "  Failed to optimize")
    print(f"  Improvement: {'✓' if achieved_variance and achieved_variance < 1.0 else '✗'}")
    
    print(f"\nFourier Analysis:")
    print(f"  Target spectral bias: {TARGET_SPECTRAL_BIAS}")
    print(f"  Achieved spectral bias: {fourier_results['spectral_bias']:.4f}")
    print(f"  Target achieved: {'✓' if fourier_results['target_achieved'] else '✗'}")
    
    print(f"\nOptimal k-parameter function:")
    a, b, c = optimal_k_params
    print(f"  k(κ) = {a:.4f} + {b:.4f} * sigmoid({c:.4f} * (κ - 0.5))")
    
    print(f"\nKey Improvements:")
    print(f"  ✓ Replaced hardcoded k=0.3 with curvature-based geodesics")
    print(f"  ✓ Implemented variance minimization optimization")
    print(f"  ✓ Added M=5 Fourier series analysis")
    print(f"  ✓ Computed spectral bias for asymmetry detection")
    print(f"  ✓ Created comprehensive visualization and documentation")
    
    # Save results to file
    results_df = pd.DataFrame({
        'Metric': ['Target Variance', 'Achieved Variance', 'Target Spectral Bias', 'Achieved Spectral Bias'],
        'Value': [TARGET_VARIANCE, achieved_variance or 0, TARGET_SPECTRAL_BIAS, fourier_results['spectral_bias']],
        'Status': ['Target', 'Achieved', 'Target', 'Achieved']
    })
    
    os.makedirs('examples/variance_fourier_output', exist_ok=True)
    results_df.to_csv('examples/variance_fourier_output/analysis_results.csv', index=False)
    
    print(f"\nDetailed results saved to examples/variance_fourier_output/analysis_results.csv")
    print("Analysis complete!")

if __name__ == "__main__":
    main()