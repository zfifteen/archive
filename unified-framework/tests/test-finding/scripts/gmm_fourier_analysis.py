"""
Gaussian Mixture Model and Fourier Analysis for θ' Distributions
================================================================

Objective: Fit GMM to θ' distributions and compute Fourier asymmetry to confirm 
clustering and chirality at k=0.3.

Inputs:
- Primes up to N=10^6
- k=0.3; M_Fourier=5; C_GMM=5

Methods:
1. Compute θ'(p,k=0.3) for primes p; normalize x_p = {θ'(p,k)/φ}
2. Fit Fourier: ρ(x) ≈ a0 + sum (a_m cos(2π m x) + b_m sin(2π m x)) using scipy.optimize.curve_fit
3. Sine asymmetry S_b = sum |b_m| for m=1 to 5
4. Fit GMM: Use sklearn.mixture.GaussianMixture(n_components=5, random_state=0) on standardized x_p
5. Compute bar_σ = mean of σ_c; BIC/AIC from model
6. Bootstrap 1000x for CI on S_b and bar_σ

Expected Outputs:
- Table: k=0.3 | S_b | CI_S_b | bar_σ | CI_bar_σ | BIC | AIC
- Coefficients: a_m, b_m arrays
- Plot data: GMM params (μ_c, σ_c, π_c)

Success Criteria: S_b≈0.45 (CI [0.42,0.48]); bar_σ≈0.12; BIC validation
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from scipy.optimize import curve_fit
from sympy import sieve
import warnings
import matplotlib.pyplot as plt
from tqdm import tqdm
import os

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Set matplotlib backend for headless environment
plt.switch_backend('Agg')

# Constants
phi = (1 + np.sqrt(5)) / 2  # Golden ratio
N_MAX = 1000000  # 10^6 as specified in requirements
k_target = 0.3   # Fixed k value for analysis
M_FOURIER = 5    # Number of Fourier harmonics
C_GMM = 5        # Number of GMM components
N_BOOTSTRAP = 1000  # Bootstrap iterations

print(f"Starting GMM and Fourier Analysis for θ' distributions")
print(f"Parameters: N={N_MAX}, k={k_target}, M_Fourier={M_FOURIER}, C_GMM={C_GMM}")
print(f"Bootstrap iterations: {N_BOOTSTRAP}")

# Generate primes up to N_MAX
print(f"\nGenerating primes up to {N_MAX}...")
primes_list = list(sieve.primerange(2, N_MAX + 1))
print(f"Generated {len(primes_list)} primes")

def frame_shift_residues(n_vals, k):
    """
    θ'(n,k) = φ * {n/φ} ** k
    """
    mod_phi = np.mod(n_vals, phi) / phi
    return phi * np.power(mod_phi, k)

def normalize_to_unit_interval(theta_vals):
    """
    Normalize θ' values to [0,1) by computing {θ'/φ}
    """
    return (theta_vals % phi) / phi

def fourier_series(x, *coeffs):
    """
    Fourier series: a0 + sum(a_m*cos(2π*m*x) + b_m*sin(2π*m*x))
    coeffs = [a0, a1, b1, a2, b2, ..., a_M, b_M]
    """
    result = coeffs[0]  # a0 term
    for m in range(1, M_FOURIER + 1):
        a_m = coeffs[2*m - 1]  # a_m coefficient
        b_m = coeffs[2*m]      # b_m coefficient
        result += a_m * np.cos(2 * np.pi * m * x) + b_m * np.sin(2 * np.pi * m * x)
    return result

def fit_fourier_coefficients(x_vals, density_vals):
    """
    Fit Fourier series coefficients using curve_fit
    Returns a_coeffs, b_coeffs arrays
    """
    # Initial guess: small random values
    p0 = np.random.normal(0, 0.1, 2 * M_FOURIER + 1)
    
    try:
        # Fit coefficients
        popt, _ = curve_fit(fourier_series, x_vals, density_vals, p0=p0, maxfev=5000)
        
        # Extract a and b coefficients
        a_coeffs = np.array([popt[0]] + [popt[2*m - 1] for m in range(1, M_FOURIER + 1)])
        b_coeffs = np.array([0] + [popt[2*m] for m in range(1, M_FOURIER + 1)])  # b0 = 0
        
        return a_coeffs, b_coeffs
    except:
        # Fallback to least squares if curve_fit fails
        return fit_fourier_least_squares(x_vals, density_vals)

def fit_fourier_least_squares(x_vals, density_vals):
    """
    Fallback Fourier fitting using least squares
    """
    # Build design matrix
    n_points = len(x_vals)
    A = np.ones((n_points, 2 * M_FOURIER + 1))
    
    for i, x in enumerate(x_vals):
        for m in range(1, M_FOURIER + 1):
            A[i, 2*m - 1] = np.cos(2 * np.pi * m * x)  # a_m terms
            A[i, 2*m] = np.sin(2 * np.pi * m * x)      # b_m terms
    
    # Solve least squares
    coeffs, _, _, _ = np.linalg.lstsq(A, density_vals, rcond=None)
    
    # Extract coefficients
    a_coeffs = np.array([coeffs[0]] + [coeffs[2*m - 1] for m in range(1, M_FOURIER + 1)])
    b_coeffs = np.array([0] + [coeffs[2*m] for m in range(1, M_FOURIER + 1)])
    
    return a_coeffs, b_coeffs

def compute_fourier_asymmetry(x_vals):
    """
    Compute Fourier asymmetry S_b = sum |b_m| for m=1 to M_FOURIER
    """
    # Create histogram density
    hist, bin_edges = np.histogram(x_vals, bins=100, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Fit Fourier coefficients
    a_coeffs, b_coeffs = fit_fourier_coefficients(bin_centers, hist)
    
    # Compute sine asymmetry (excluding b0 which is 0)
    S_b = np.sum(np.abs(b_coeffs[1:]))  # Sum |b_m| for m=1 to M_FOURIER
    
    return S_b, a_coeffs, b_coeffs

def fit_gmm_analysis(x_vals):
    """
    Fit GMM and compute mean sigma with proper standardization
    """
    # Standardize data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(x_vals.reshape(-1, 1))
    
    # Fit GMM
    gmm = GaussianMixture(n_components=C_GMM, random_state=0, covariance_type='full')
    gmm.fit(X_scaled)
    
    # Extract parameters
    means = scaler.inverse_transform(gmm.means_)
    covariances_scaled = gmm.covariances_ * (scaler.scale_[0] ** 2)
    sigmas = np.sqrt(covariances_scaled.flatten())
    weights = gmm.weights_
    
    # Compute mean sigma
    bar_sigma = np.mean(sigmas)
    
    # Compute BIC and AIC
    bic = gmm.bic(X_scaled)
    aic = gmm.aic(X_scaled)
    
    return bar_sigma, bic, aic, means.flatten(), sigmas, weights

def bootstrap_analysis(primes_array, n_bootstrap=N_BOOTSTRAP):
    """
    Bootstrap analysis for confidence intervals
    """
    print(f"\nPerforming bootstrap analysis with {n_bootstrap} iterations...")
    
    S_b_values = []
    bar_sigma_values = []
    
    # Original sample size
    n_primes = len(primes_array)
    
    for i in tqdm(range(n_bootstrap), desc="Bootstrap"):
        # Bootstrap sample
        bootstrap_indices = np.random.choice(n_primes, size=n_primes, replace=True)
        bootstrap_primes = primes_array[bootstrap_indices]
        
        # Compute θ' and normalize
        theta_bootstrap = frame_shift_residues(bootstrap_primes, k_target)
        x_bootstrap = normalize_to_unit_interval(theta_bootstrap)
        
        # Compute metrics
        S_b, _, _ = compute_fourier_asymmetry(x_bootstrap)
        bar_sigma, _, _, _, _, _ = fit_gmm_analysis(x_bootstrap)
        
        S_b_values.append(S_b)
        bar_sigma_values.append(bar_sigma)
    
    # Compute confidence intervals (2.5% and 97.5% percentiles)
    S_b_ci = np.percentile(S_b_values, [2.5, 97.5])
    bar_sigma_ci = np.percentile(bar_sigma_values, [2.5, 97.5])
    
    return S_b_values, bar_sigma_values, S_b_ci, bar_sigma_ci

# Main Analysis
print(f"\nComputing θ'(p, k={k_target}) for {len(primes_list)} primes...")
primes_array = np.array(primes_list)
theta_primes = frame_shift_residues(primes_array, k_target)

print("Normalizing to unit interval...")
x_primes = normalize_to_unit_interval(theta_primes)

print("Computing Fourier analysis...")
S_b, a_coeffs, b_coeffs = compute_fourier_asymmetry(x_primes)

print("Fitting GMM...")
bar_sigma, bic, aic, gmm_means, gmm_sigmas, gmm_weights = fit_gmm_analysis(x_primes)

print("Performing bootstrap analysis...")
S_b_bootstrap, bar_sigma_bootstrap, S_b_ci, bar_sigma_ci = bootstrap_analysis(primes_array)

# Results Summary
print("\n" + "="*80)
print("GMM AND FOURIER ANALYSIS RESULTS")
print("="*80)

print(f"\nPrimary Metrics at k = {k_target}:")
print(f"Fourier Sine Asymmetry (S_b): {S_b:.3f}")
print(f"S_b Confidence Interval: [{S_b_ci[0]:.3f}, {S_b_ci[1]:.3f}]")
print(f"GMM Mean Sigma (bar_σ): {bar_sigma:.3f}")  
print(f"bar_σ Confidence Interval: [{bar_sigma_ci[0]:.3f}, {bar_sigma_ci[1]:.3f}]")
print(f"BIC: {bic:.2f}")
print(f"AIC: {aic:.2f}")

print(f"\nFourier Coefficients:")
print(f"a_coeffs: {a_coeffs}")
print(f"b_coeffs: {b_coeffs}")

print(f"\nGMM Parameters:")
print(f"Means (μ_c): {gmm_means}")
print(f"Sigmas (σ_c): {gmm_sigmas}")  
print(f"Weights (π_c): {gmm_weights}")

# Create Results Table
results_table = pd.DataFrame({
    'k': [k_target],
    'S_b': [S_b],
    'CI_S_b_lower': [S_b_ci[0]],
    'CI_S_b_upper': [S_b_ci[1]],
    'bar_σ': [bar_sigma],
    'CI_bar_σ_lower': [bar_sigma_ci[0]],
    'CI_bar_σ_upper': [bar_sigma_ci[1]],
    'BIC': [bic],
    'AIC': [aic]
})

print(f"\nResults Table:")
print(results_table.to_string(index=False, float_format='%.3f'))

# Validation against success criteria
print(f"\n" + "="*80)
print("VALIDATION AGAINST SUCCESS CRITERIA")
print("="*80)

expected_S_b = 0.45
expected_S_b_ci = [0.42, 0.48]
expected_bar_sigma = 0.12

print(f"Expected S_b ≈ {expected_S_b} (CI {expected_S_b_ci})")
print(f"Actual S_b = {S_b:.3f} (CI [{S_b_ci[0]:.3f}, {S_b_ci[1]:.3f}])")
print(f"S_b within expected range: {expected_S_b_ci[0] <= S_b <= expected_S_b_ci[1]}")

print(f"\nExpected bar_σ ≈ {expected_bar_sigma}")
print(f"Actual bar_σ = {bar_sigma:.3f}")
print(f"bar_σ close to expected: {abs(bar_sigma - expected_bar_sigma) < 0.05}")

# Save results to files
output_dir = "/home/runner/work/unified-framework/unified-framework/number-theory/prime-curve/gmm_fourier_results"
os.makedirs(output_dir, exist_ok=True)

# Save main results
results_table.to_csv(f"{output_dir}/results_table.csv", index=False)

# Save coefficients
coeffs_df = pd.DataFrame({
    'a_coeffs': a_coeffs,
    'b_coeffs': b_coeffs
})
coeffs_df.to_csv(f"{output_dir}/fourier_coefficients.csv", index=False)

# Save GMM parameters
gmm_params_df = pd.DataFrame({
    'component': range(C_GMM),
    'mean': gmm_means,
    'sigma': gmm_sigmas,
    'weight': gmm_weights
})
gmm_params_df.to_csv(f"{output_dir}/gmm_parameters.csv", index=False)

# Save bootstrap results
bootstrap_df = pd.DataFrame({
    'S_b_bootstrap': S_b_bootstrap,
    'bar_sigma_bootstrap': bar_sigma_bootstrap
})
bootstrap_df.to_csv(f"{output_dir}/bootstrap_results.csv", index=False)

print(f"\nResults saved to: {output_dir}/")
print("Files generated:")
print("- results_table.csv")
print("- fourier_coefficients.csv") 
print("- gmm_parameters.csv")
print("- bootstrap_results.csv")

print(f"\nAnalysis completed successfully!")