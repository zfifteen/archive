"""
Task 4: Enhanced Statistical Discrimination and GMM Fitting
=========================================================

Enhanced version with improved discrimination techniques and parameter tuning.
"""

import numpy as np
import pandas as pd
import json
import time
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from scipy.stats import entropy, ks_2samp
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
N_MAX = 100000              # Number range to analyze
N_BOOTSTRAP = 100           # Reduced for faster testing

print(f"Task 4: Enhanced Statistical Discrimination and GMM Fitting")
print(f"Parameters: N_max={N_MAX}, k={K_TARGET}, C_GMM={C_GMM}")
print(f"Bootstrap iterations: {N_BOOTSTRAP}")

def explore_optimal_k():
    """
    Explore different k values to find one that provides better discrimination
    """
    print("\nExploring k values for better discrimination...")
    
    k_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    n_test = 10000  # Test with smaller sample
    
    results = []
    
    for k in k_values:
        # Generate test data
        n_values = np.arange(2, n_test + 1)
        theta_values = np.array([theta_prime(n, k, PHI) for n in n_values])
        is_prime = np.array([isprime(int(n)) for n in n_values])
        
        theta_primes = theta_values[is_prime]
        theta_composites = theta_values[~is_prime]
        
        # Compute basic metrics
        mu_p = np.mean(theta_primes)
        mu_c = np.mean(theta_composites)
        var_p = np.var(theta_primes, ddof=1)
        var_c = np.var(theta_composites, ddof=1)
        
        cohens_d = np.abs(mu_p - mu_c) / np.sqrt((var_p + var_c) / 2)
        
        # KS test for distributional differences
        ks_stat, ks_pval = ks_2samp(theta_primes, theta_composites)
        
        results.append({
            'k': k,
            'cohens_d': cohens_d,
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pval,
            'mu_p': mu_p,
            'mu_c': mu_c,
            'n_primes': len(theta_primes),
            'n_composites': len(theta_composites)
        })
        
        print(f"k={k:.1f}: d={cohens_d:.4f}, KS={ks_stat:.4f} (p={ks_pval:.4e}), μ_p={mu_p:.3f}, μ_c={mu_c:.3f}")
    
    # Find best k for discrimination
    best_k_d = max(results, key=lambda x: x['cohens_d'])
    best_k_ks = max(results, key=lambda x: x['ks_statistic'])
    
    print(f"\nBest k for Cohen's d: {best_k_d['k']} (d={best_k_d['cohens_d']:.4f})")
    print(f"Best k for KS statistic: {best_k_ks['k']} (KS={best_k_ks['ks_statistic']:.4f})")
    
    return results

def compute_enhanced_theta_prime_values(n_max, k):
    """
    Enhanced computation with additional transformations to improve discrimination
    """
    print(f"\nComputing enhanced θ'(n, k={k}) for n=2 to {n_max}...")
    
    n_values = np.arange(2, n_max + 1)
    
    # Standard θ' computation
    theta_values = np.array([theta_prime(n, k, PHI) for n in n_values])
    
    # Additional transformations to enhance discrimination
    # 1. Fractional part enhancement
    theta_frac = theta_values % 1
    
    # 2. Log-transformed values (to handle different scales)
    theta_log = np.log(theta_values + 1e-10)  # Avoid log(0)
    
    # 3. Normalized values
    theta_norm = (theta_values - np.mean(theta_values)) / np.std(theta_values)
    
    # Classify as prime or composite
    is_prime = np.array([isprime(int(n)) for n in n_values])
    
    # Create result dictionary
    result = {
        'raw': {
            'primes': theta_values[is_prime],
            'composites': theta_values[~is_prime]
        },
        'fractional': {
            'primes': theta_frac[is_prime],
            'composites': theta_frac[~is_prime]
        },
        'log': {
            'primes': theta_log[is_prime],
            'composites': theta_log[~is_prime]
        },
        'normalized': {
            'primes': theta_norm[is_prime],
            'composites': theta_norm[~is_prime]
        },
        'is_prime': is_prime
    }
    
    print(f"Found {len(result['raw']['primes'])} primes and {len(result['raw']['composites'])} composites")
    
    return result

def compute_enhanced_metrics(theta_data):
    """
    Compute enhanced discrimination metrics
    """
    print("\nComputing enhanced discrimination metrics...")
    
    metrics = {}
    
    for transform_name, data in theta_data.items():
        if transform_name == 'is_prime':
            continue
            
        theta_primes = data['primes']
        theta_composites = data['composites']
        
        # Cohen's d
        mu_p = np.mean(theta_primes)
        mu_c = np.mean(theta_composites)
        var_p = np.var(theta_primes, ddof=1)
        var_c = np.var(theta_composites, ddof=1)
        cohens_d = np.abs(mu_p - mu_c) / np.sqrt((var_p + var_c) / 2)
        
        # Enhanced KL divergence with adaptive binning
        kl_div = compute_adaptive_kl_divergence(theta_primes, theta_composites)
        
        # Wasserstein distance (Earth Mover's Distance)
        from scipy.stats import wasserstein_distance
        wasserstein_dist = wasserstein_distance(theta_primes, theta_composites)
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_pval = ks_2samp(theta_primes, theta_composites)
        
        # Energy distance
        from scipy.spatial.distance import pdist, squareform
        def energy_distance(x, y):
            """Compute energy distance between two samples"""
            m, n = len(x), len(y)
            xy = np.concatenate([x, y])
            dists = squareform(pdist(xy.reshape(-1, 1)))
            
            # E[|X-Y|]
            exy = np.mean(dists[:m, m:])
            # E[|X-X'|]  
            exx = np.mean(dists[:m, :m][np.triu_indices(m, k=1)])
            # E[|Y-Y'|]
            eyy = np.mean(dists[m:, m:][np.triu_indices(n, k=1)])
            
            return 2 * exy - exx - eyy
        
        energy_dist = energy_distance(theta_primes[:1000], theta_composites[:1000])  # Sample for efficiency
        
        metrics[transform_name] = {
            'cohens_d': cohens_d,
            'kl_divergence': kl_div,
            'wasserstein_distance': wasserstein_dist,
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pval,
            'energy_distance': energy_dist,
            'mu_primes': mu_p,
            'mu_composites': mu_c,
            'var_primes': var_p,
            'var_composites': var_c
        }
        
        print(f"{transform_name.capitalize()}: d={cohens_d:.4f}, KL={kl_div:.4f}, W={wasserstein_dist:.4f}, KS={ks_stat:.4f}")
    
    return metrics

def compute_adaptive_kl_divergence(theta_primes, theta_composites):
    """
    Compute KL divergence with adaptive binning strategy
    """
    # Try different numbers of bins to find stable estimate
    bin_counts = [25, 50, 100, 200]
    kl_estimates = []
    
    for n_bins in bin_counts:
        min_val = min(np.min(theta_primes), np.min(theta_composites))
        max_val = max(np.max(theta_primes), np.max(theta_composites))
        bins = np.linspace(min_val, max_val, n_bins)
        
        hist_primes, _ = np.histogram(theta_primes, bins=bins, density=True)
        hist_composites, _ = np.histogram(theta_composites, bins=bins, density=True)
        
        # Normalize
        hist_primes = hist_primes / np.sum(hist_primes)
        hist_composites = hist_composites / np.sum(hist_composites)
        
        # Add smoothing
        epsilon = 1e-10
        hist_primes = hist_primes + epsilon
        hist_composites = hist_composites + epsilon
        
        # Renormalize
        hist_primes = hist_primes / np.sum(hist_primes)
        hist_composites = hist_composites / np.sum(hist_composites)
        
        kl_div = entropy(hist_primes, hist_composites)
        if np.isfinite(kl_div):
            kl_estimates.append(kl_div)
    
    return np.mean(kl_estimates) if kl_estimates else 0.0

def fit_enhanced_gmm(theta_primes, theta_composites):
    """
    Enhanced GMM fitting with better parameter estimation
    """
    print(f"\nFitting enhanced GMM with {C_GMM} components...")
    
    # Combine data for overall standardization
    all_theta = np.concatenate([theta_primes, theta_composites])
    
    # Try different covariance types for better fit
    covariance_types = ['full', 'tied', 'diag', 'spherical']
    best_gmm = None
    best_bic = np.inf
    
    for cov_type in covariance_types:
        # Standardize the data
        scaler = StandardScaler()
        all_theta_scaled = scaler.fit_transform(all_theta.reshape(-1, 1)).flatten()
        
        # Fit GMM
        gmm = GaussianMixture(
            n_components=C_GMM, 
            random_state=42, 
            covariance_type=cov_type,
            n_init=5  # Multiple initializations for stability
        )
        
        try:
            gmm.fit(all_theta_scaled.reshape(-1, 1))
            bic = gmm.bic(all_theta_scaled.reshape(-1, 1))
            
            if bic < best_bic:
                best_bic = bic
                best_gmm = gmm
                best_scaler = scaler
                best_cov_type = cov_type
        
        except Exception as e:
            print(f"Failed to fit GMM with {cov_type} covariance: {e}")
            continue
    
    if best_gmm is None:
        raise ValueError("Failed to fit any GMM model")
    
    # Extract parameters from best model
    means = best_gmm.means_.flatten()
    
    if best_cov_type == 'full':
        covariances = best_gmm.covariances_.flatten()
    elif best_cov_type == 'tied':
        covariances = np.diag(best_gmm.covariances_)
    elif best_cov_type == 'diag':
        covariances = best_gmm.covariances_.flatten()
    else:  # spherical
        covariances = best_gmm.covariances_
    
    sigmas = np.sqrt(np.abs(covariances))  # Ensure positive
    weights = best_gmm.weights_
    
    # Compute enhanced σ_bar with variance weighting
    sigma_bar = np.average(sigmas, weights=weights)  # Weighted average
    
    aic = best_gmm.aic(all_theta_scaled.reshape(-1, 1))
    
    print(f"Best GMM: {best_cov_type} covariance, BIC: {best_bic:.2f}")
    print(f"Enhanced σ_bar (weighted): {sigma_bar:.4f}")
    
    return {
        'gmm': best_gmm,
        'scaler': best_scaler,
        'covariance_type': best_cov_type,
        'means': means,
        'sigmas': sigmas,
        'weights': weights,
        'sigma_bar': sigma_bar,
        'bic': best_bic,
        'aic': aic
    }

def enhanced_main():
    """
    Enhanced main execution function
    """
    start_time = time.time()
    
    # Step 0: Explore k values (optional analysis)
    k_exploration = explore_optimal_k()
    
    # Step 1: Compute enhanced θ' values
    theta_data = compute_enhanced_theta_prime_values(N_MAX, K_TARGET)
    
    # Step 2: Compute enhanced metrics for all transformations
    all_metrics = compute_enhanced_metrics(theta_data)
    
    # Step 3: Select best transformation for final analysis
    best_transform = max(all_metrics.keys(), 
                        key=lambda x: all_metrics[x]['cohens_d'])
    
    print(f"\nUsing best transformation: {best_transform}")
    best_data = theta_data[best_transform]
    best_metrics = all_metrics[best_transform]
    
    # Step 4: Enhanced GMM fitting
    gmm_results = fit_enhanced_gmm(best_data['primes'], best_data['composites'])
    
    # Step 5: Final results
    results = {
        "k": K_TARGET,
        "best_transformation": best_transform,
        "cohens_d": float(best_metrics['cohens_d']),
        "KL": float(best_metrics['kl_divergence']),
        "sigma_bar": float(gmm_results['sigma_bar']),
        "BIC": float(gmm_results['bic']),
        "AIC": float(gmm_results['aic']),
        "wasserstein_distance": float(best_metrics['wasserstein_distance']),
        "ks_statistic": float(best_metrics['ks_statistic']),
        "ks_pvalue": float(best_metrics['ks_pvalue']),
        "energy_distance": float(best_metrics['energy_distance']),
        "gmm_covariance_type": gmm_results['covariance_type'],
        "n_primes": len(best_data['primes']),
        "n_composites": len(best_data['composites']),
        "all_transformations": {
            name: {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                   for k, v in metrics.items()}
            for name, metrics in all_metrics.items()
        },
        "k_exploration": k_exploration
    }
    
    # Create output directory
    output_dir = "/home/runner/work/unified-framework/unified-framework/task4_enhanced_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results
    with open(os.path.join(output_dir, "enhanced_results.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display results
    print(f"\n" + "="*80)
    print("ENHANCED TASK 4 RESULTS")
    print("="*80)
    
    print(f"\nBest transformation: {best_transform}")
    print(f"Primary Metrics at k = {K_TARGET}:")
    print(f"Cohen's d: {best_metrics['cohens_d']:.4f}")
    print(f"KL divergence: {best_metrics['kl_divergence']:.4f}")
    print(f"σ_bar: {gmm_results['sigma_bar']:.4f}")
    print(f"BIC: {gmm_results['bic']:.2f}")
    print(f"AIC: {gmm_results['aic']:.2f}")
    
    print(f"\nAdditional Metrics:")
    print(f"Wasserstein distance: {best_metrics['wasserstein_distance']:.4f}")
    print(f"KS statistic: {best_metrics['ks_statistic']:.4f} (p={best_metrics['ks_pvalue']:.2e})")
    print(f"Energy distance: {best_metrics['energy_distance']:.4f}")
    
    # Validation
    validation_results = {
        'cohens_d_valid': best_metrics['cohens_d'] > 1.2,
        'kl_valid': 0.4 <= best_metrics['kl_divergence'] <= 0.6,
        'sigma_bar_valid': abs(gmm_results['sigma_bar'] - 0.12) < 0.05
    }
    
    print(f"\n" + "="*80)
    print("ENHANCED VALIDATION")
    print("="*80)
    print(f"Cohen's d > 1.2: {best_metrics['cohens_d']:.3f} {'✓' if validation_results['cohens_d_valid'] else '✗'}")
    print(f"KL in [0.4, 0.6]: {best_metrics['kl_divergence']:.3f} {'✓' if validation_results['kl_valid'] else '✗'}")
    print(f"σ_bar ≈ 0.12: {gmm_results['sigma_bar']:.3f} {'✓' if validation_results['sigma_bar_valid'] else '✗'}")
    
    overall_valid = all(validation_results.values())
    print(f"\nOverall validation: {'✓ PASSED' if overall_valid else '✗ FAILED'}")
    
    # Runtime
    runtime_minutes = (time.time() - start_time) / 60
    print(f"\nRuntime: {runtime_minutes:.2f} minutes")
    print(f"Results saved to: {output_dir}/enhanced_results.json")
    
    return results, overall_valid

if __name__ == "__main__":
    try:
        results, is_valid = enhanced_main()
        sys.exit(0 if is_valid else 1)
    except Exception as e:
        print(f"\nERROR: Enhanced Task 4 failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)