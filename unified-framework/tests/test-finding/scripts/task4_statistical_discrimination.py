"""
Task 4: Statistical Discrimination and GMM Fitting
=================================================

Objective: Quantify separations (Cohen's d>1.2, KL≈0.4-0.6) via GMM and Fourier.

Inputs:
- θ' from Task 1; C=5 components.

Steps:
1. Standardize θ'; fit GMM (sklearn.mixture.GaussianMixture).
2. Compute μ_primes, μ_composites; d = |μ_p - μ_c| / sqrt((var_p + var_c)/2).
3. KL divergence (scipy.stats.entropy).
4. σ_bar = average σ_c over C.
5. Bootstrap for CI.

Outputs:
- JSON: {"cohens_d": float, "KL": float, "sigma_bar": float at k=0.3}.
- BIC/AIC values.

Validation:
- d>1.2; KL 0.4-0.6; σ_bar≈0.12.
- Runtime: ~30 min.
"""

import numpy as np
import pandas as pd
import json
import time
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from scipy.stats import entropy
from scipy import stats
from sympy import sieve, isprime
import warnings
import os
import sys

# Add path for core imports
sys.path.append('/home/runner/work/unified-framework/unified-framework')

try:
    from core.axioms import theta_prime
except ImportError:
    # Fallback implementation based on axioms.py
    def theta_prime(n, k, phi):
        """
        Applies the golden ratio modular transformation θ'(n,k) to warp integer residues.
        """
        return phi * ((n % phi) / phi) ** k

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
K_TARGET = 0.3              # Fixed k value for analysis
C_GMM = 5                   # Number of GMM components
N_MAX = 100000              # Number range to analyze (start smaller for testing)
N_BOOTSTRAP = 1000          # Bootstrap iterations

print(f"Task 4: Statistical Discrimination and GMM Fitting")
print(f"Parameters: N_max={N_MAX}, k={K_TARGET}, C_GMM={C_GMM}")
print(f"Bootstrap iterations: {N_BOOTSTRAP}")

def compute_theta_prime_values(n_max, k):
    """
    Compute θ'(n,k) values for integers from 2 to n_max
    """
    print(f"\nComputing θ'(n, k={k}) for n=2 to {n_max}...")
    
    n_values = np.arange(2, n_max + 1)
    theta_values = np.array([theta_prime(n, k, PHI) for n in n_values])
    
    # Classify as prime or composite
    is_prime = np.array([isprime(int(n)) for n in n_values])
    
    theta_primes = theta_values[is_prime]
    theta_composites = theta_values[~is_prime]
    
    print(f"Found {len(theta_primes)} primes and {len(theta_composites)} composites")
    
    return theta_primes, theta_composites, theta_values, is_prime

def fit_gmm_and_compute_statistics(theta_primes, theta_composites):
    """
    Fit GMM and compute statistical discrimination metrics
    """
    print(f"\nFitting GMM with {C_GMM} components...")
    
    # Combine all theta values for overall standardization
    all_theta = np.concatenate([theta_primes, theta_composites])
    
    # Standardize the data
    scaler = StandardScaler()
    all_theta_scaled = scaler.fit_transform(all_theta.reshape(-1, 1)).flatten()
    
    # Split back into primes and composites (standardized)
    n_primes = len(theta_primes)
    theta_primes_scaled = all_theta_scaled[:n_primes]
    theta_composites_scaled = all_theta_scaled[n_primes:]
    
    # Fit GMM on all standardized data
    gmm = GaussianMixture(n_components=C_GMM, random_state=42, covariance_type='full')
    gmm.fit(all_theta_scaled.reshape(-1, 1))
    
    # Get GMM parameters
    means = gmm.means_.flatten()
    covariances = gmm.covariances_.flatten()
    sigmas = np.sqrt(covariances)
    weights = gmm.weights_
    
    # Compute σ_bar = average σ_c over C components
    sigma_bar = np.mean(sigmas)
    
    # Compute BIC and AIC
    bic = gmm.bic(all_theta_scaled.reshape(-1, 1))
    aic = gmm.aic(all_theta_scaled.reshape(-1, 1))
    
    print(f"GMM fitted with {C_GMM} components")
    print(f"Sigma_bar: {sigma_bar:.4f}")
    print(f"BIC: {bic:.2f}, AIC: {aic:.2f}")
    
    return {
        'gmm': gmm,
        'scaler': scaler,
        'theta_primes_scaled': theta_primes_scaled,
        'theta_composites_scaled': theta_composites_scaled,
        'all_theta_scaled': all_theta_scaled,
        'means': means,
        'sigmas': sigmas,
        'weights': weights,
        'sigma_bar': sigma_bar,
        'bic': bic,
        'aic': aic
    }

def compute_cohens_d(theta_primes, theta_composites):
    """
    Compute Cohen's d between primes and composites
    d = |μ_p - μ_c| / sqrt((var_p + var_c)/2)
    """
    mu_primes = np.mean(theta_primes)
    mu_composites = np.mean(theta_composites)
    var_primes = np.var(theta_primes, ddof=1)
    var_composites = np.var(theta_composites, ddof=1)
    
    pooled_std = np.sqrt((var_primes + var_composites) / 2)
    cohens_d = np.abs(mu_primes - mu_composites) / pooled_std
    
    print(f"\nCohen's d calculation:")
    print(f"μ_primes: {mu_primes:.4f}")
    print(f"μ_composites: {mu_composites:.4f}")
    print(f"var_primes: {var_primes:.4f}")
    print(f"var_composites: {var_composites:.4f}")
    print(f"Cohen's d: {cohens_d:.4f}")
    
    return cohens_d

def compute_kl_divergence(theta_primes, theta_composites):
    """
    Compute KL divergence between prime and composite distributions
    using histogram approximation and scipy.stats.entropy
    """
    print(f"\nComputing KL divergence...")
    
    # Create common bin edges for both distributions
    min_val = min(np.min(theta_primes), np.min(theta_composites))
    max_val = max(np.max(theta_primes), np.max(theta_composites))
    bins = np.linspace(min_val, max_val, 50)
    
    # Compute histograms (probability distributions)
    hist_primes, _ = np.histogram(theta_primes, bins=bins, density=True)
    hist_composites, _ = np.histogram(theta_composites, bins=bins, density=True)
    
    # Normalize to probabilities
    hist_primes = hist_primes / np.sum(hist_primes)
    hist_composites = hist_composites / np.sum(hist_composites)
    
    # Add small epsilon to avoid log(0)
    epsilon = 1e-10
    hist_primes = hist_primes + epsilon
    hist_composites = hist_composites + epsilon
    
    # Compute KL divergence: KL(P||Q) = sum(P * log(P/Q))
    kl_divergence = entropy(hist_primes, hist_composites)
    
    print(f"KL divergence: {kl_divergence:.4f}")
    
    return kl_divergence

def bootstrap_analysis(theta_primes, theta_composites, n_bootstrap=N_BOOTSTRAP):
    """
    Bootstrap analysis for confidence intervals
    """
    print(f"\nPerforming bootstrap analysis with {n_bootstrap} iterations...")
    
    cohens_d_values = []
    kl_values = []
    sigma_bar_values = []
    
    n_primes = len(theta_primes)
    n_composites = len(theta_composites)
    
    for i in range(n_bootstrap):
        if i % 100 == 0:
            print(f"Bootstrap iteration {i}/{n_bootstrap}")
        
        # Bootstrap samples
        bootstrap_primes = np.random.choice(theta_primes, size=n_primes, replace=True)
        bootstrap_composites = np.random.choice(theta_composites, size=n_composites, replace=True)
        
        # Compute metrics
        cohens_d = compute_cohens_d(bootstrap_primes, bootstrap_composites)
        kl_div = compute_kl_divergence(bootstrap_primes, bootstrap_composites)
        
        # Fit GMM for sigma_bar
        gmm_results = fit_gmm_and_compute_statistics(bootstrap_primes, bootstrap_composites)
        sigma_bar = gmm_results['sigma_bar']
        
        cohens_d_values.append(cohens_d)
        kl_values.append(kl_div)
        sigma_bar_values.append(sigma_bar)
    
    # Compute confidence intervals (2.5% and 97.5% percentiles)
    cohens_d_ci = np.percentile(cohens_d_values, [2.5, 97.5])
    kl_ci = np.percentile(kl_values, [2.5, 97.5])
    sigma_bar_ci = np.percentile(sigma_bar_values, [2.5, 97.5])
    
    print(f"\nBootstrap results:")
    print(f"Cohen's d CI: [{cohens_d_ci[0]:.3f}, {cohens_d_ci[1]:.3f}]")
    print(f"KL divergence CI: [{kl_ci[0]:.3f}, {kl_ci[1]:.3f}]")
    print(f"Sigma_bar CI: [{sigma_bar_ci[0]:.3f}, {sigma_bar_ci[1]:.3f}]")
    
    return {
        'cohens_d_values': cohens_d_values,
        'kl_values': kl_values,
        'sigma_bar_values': sigma_bar_values,
        'cohens_d_ci': cohens_d_ci,
        'kl_ci': kl_ci,
        'sigma_bar_ci': sigma_bar_ci
    }

def validate_results(cohens_d, kl_divergence, sigma_bar):
    """
    Validate results against success criteria
    """
    print(f"\n" + "="*80)
    print("VALIDATION AGAINST SUCCESS CRITERIA")
    print("="*80)
    
    # Success criteria
    cohens_d_threshold = 1.2
    kl_range = [0.4, 0.6]
    sigma_bar_expected = 0.12
    
    # Validate Cohen's d
    cohens_d_valid = cohens_d > cohens_d_threshold
    print(f"Cohen's d > {cohens_d_threshold}: {cohens_d:.3f} {'✓' if cohens_d_valid else '✗'}")
    
    # Validate KL divergence
    kl_valid = kl_range[0] <= kl_divergence <= kl_range[1]
    print(f"KL divergence in [{kl_range[0]}, {kl_range[1]}]: {kl_divergence:.3f} {'✓' if kl_valid else '✗'}")
    
    # Validate sigma_bar
    sigma_bar_valid = abs(sigma_bar - sigma_bar_expected) < 0.05
    print(f"σ_bar ≈ {sigma_bar_expected}: {sigma_bar:.3f} {'✓' if sigma_bar_valid else '✗'}")
    
    overall_valid = cohens_d_valid and kl_valid and sigma_bar_valid
    print(f"\nOverall validation: {'✓ PASSED' if overall_valid else '✗ FAILED'}")
    
    return overall_valid

def main():
    """
    Main execution function for Task 4
    """
    start_time = time.time()
    
    # Step 1: Compute θ' values from Task 1
    theta_primes, theta_composites, all_theta, is_prime = compute_theta_prime_values(N_MAX, K_TARGET)
    
    # Step 2: Compute Cohen's d
    cohens_d = compute_cohens_d(theta_primes, theta_composites)
    
    # Step 3: Compute KL divergence
    kl_divergence = compute_kl_divergence(theta_primes, theta_composites)
    
    # Step 4: Fit GMM and compute σ_bar
    gmm_results = fit_gmm_and_compute_statistics(theta_primes, theta_composites)
    sigma_bar = gmm_results['sigma_bar']
    bic = gmm_results['bic']
    aic = gmm_results['aic']
    
    # Step 5: Bootstrap for confidence intervals
    bootstrap_results = bootstrap_analysis(theta_primes, theta_composites)
    
    # Prepare results
    results = {
        "k": K_TARGET,
        "cohens_d": float(cohens_d),
        "KL": float(kl_divergence),
        "sigma_bar": float(sigma_bar),
        "BIC": float(bic),
        "AIC": float(aic),
        "n_primes": len(theta_primes),
        "n_composites": len(theta_composites),
        "confidence_intervals": {
            "cohens_d_ci": [float(x) for x in bootstrap_results['cohens_d_ci']],
            "KL_ci": [float(x) for x in bootstrap_results['kl_ci']],
            "sigma_bar_ci": [float(x) for x in bootstrap_results['sigma_bar_ci']]
        }
    }
    
    # Create output directory
    output_dir = "/home/runner/work/unified-framework/unified-framework/task4_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save JSON results
    json_output_path = os.path.join(output_dir, "task4_results.json")
    with open(json_output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save detailed results
    detailed_results = {
        **results,
        "gmm_parameters": {
            "means": [float(x) for x in gmm_results['means']],
            "sigmas": [float(x) for x in gmm_results['sigmas']],
            "weights": [float(x) for x in gmm_results['weights']]
        },
        "bootstrap_samples": {
            "cohens_d_values": [float(x) for x in bootstrap_results['cohens_d_values']],
            "kl_values": [float(x) for x in bootstrap_results['kl_values']],
            "sigma_bar_values": [float(x) for x in bootstrap_results['sigma_bar_values']]
        }
    }
    
    detailed_output_path = os.path.join(output_dir, "task4_detailed_results.json")
    with open(detailed_output_path, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    # Display results
    print(f"\n" + "="*80)
    print("TASK 4 RESULTS SUMMARY")
    print("="*80)
    
    print(f"\nPrimary Metrics at k = {K_TARGET}:")
    print(f"Cohen's d: {cohens_d:.4f}")
    print(f"KL divergence: {kl_divergence:.4f}")
    print(f"σ_bar: {sigma_bar:.4f}")
    print(f"BIC: {bic:.2f}")
    print(f"AIC: {aic:.2f}")
    
    print(f"\nConfidence Intervals (95%):")
    print(f"Cohen's d: [{bootstrap_results['cohens_d_ci'][0]:.3f}, {bootstrap_results['cohens_d_ci'][1]:.3f}]")
    print(f"KL divergence: [{bootstrap_results['kl_ci'][0]:.3f}, {bootstrap_results['kl_ci'][1]:.3f}]")
    print(f"σ_bar: [{bootstrap_results['sigma_bar_ci'][0]:.3f}, {bootstrap_results['sigma_bar_ci'][1]:.3f}]")
    
    # Validation
    is_valid = validate_results(cohens_d, kl_divergence, sigma_bar)
    
    # Runtime information
    end_time = time.time()
    runtime_minutes = (end_time - start_time) / 60
    print(f"\nRuntime: {runtime_minutes:.2f} minutes")
    
    print(f"\nResults saved to:")
    print(f"- {json_output_path}")
    print(f"- {detailed_output_path}")
    
    return results, is_valid

if __name__ == "__main__":
    try:
        results, is_valid = main()
        print(f"\n{'='*80}")
        print(f"TASK 4 COMPLETED {'SUCCESSFULLY' if is_valid else 'WITH ISSUES'}")
        print(f"{'='*80}")
        
        # Return appropriate exit code
        sys.exit(0 if is_valid else 1)
        
    except Exception as e:
        print(f"\nERROR: Task 4 failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)