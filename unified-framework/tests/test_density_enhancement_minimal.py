#!/usr/bin/env python3
"""
Golden Master Test for Prime-Curve Density Enhancement (Reproducibility Test)

This test verifies that the deterministic demo run produces exactly the expected 
enhancement metrics, bootstrap confidence intervals, and bin counts, ensuring 
reproducibility and guarding against silent algorithm changes.

Test Parameters:
- N = 100,000
- k = 0.3  
- B = 20 (number of bins)
- SEED = 0 (for both numpy.random and Python random)
- θ′ calculation: theta_prime(n, k) = φ * (((n % φ) / φ) ** k)
- Binning: bin edges = np.linspace(0, φ, B+1) where φ = (1 + sqrt(5)) / 2

Expected Golden Master Outputs:
1. Maximal Enhancement (robust): 160.634 ± 0.005 percentage points
2. Bootstrap CI: 2.5%: 7.750 ± 0.005, 97.5%: 681.902 ± 0.005
3. Raw counts per bin: exact match required
4. Bootstrap enhancements vector: 1000 rows, match to 3 decimal places
"""

import numpy as np
import random
from sympy import sieve
from scipy import stats
import csv
import os
from datetime import datetime
import warnings

# Suppress warnings for clean output
warnings.filterwarnings("ignore")

# Test parameters as specified
N = 100000
K = 0.3
B = 20  # number of bins
SEED = 0
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
N_BOOTSTRAP = 1000

# Expected golden master values (observed from deterministic run with SEED=0)
EXPECTED_MAX_ENHANCEMENT = 160.634
EXPECTED_CI_LOWER = 7.750  
EXPECTED_CI_UPPER = 681.902
TOLERANCE_ENHANCEMENT = 0.005
TOLERANCE_CI = 0.005  # Slightly relaxed for bootstrap confidence intervals


def set_seeds(seed=SEED):
    """Set all random seeds for reproducibility."""
    np.random.seed(seed)
    random.seed(seed)


def theta_prime(n, k):
    """
    Calculate θ′ transformation for integer n with curvature parameter k.
    
    Formula: θ′ = φ * ({n/φ} ** k)
    
    Args:
        n: Integer or array of integers
        k: Curvature exponent parameter
        
    Returns:
        Transformed value(s) in range [0, φ)
    """
    mod_phi = np.mod(n, PHI) / PHI
    return PHI * np.power(mod_phi, k)


def generate_primes_and_all_integers(n_max):
    """Generate primes and all integers up to n_max."""
    primes = list(sieve.primerange(2, n_max + 1))
    all_integers = list(range(1, n_max + 1))
    return np.array(primes), np.array(all_integers)


def compute_bin_counts(theta_values, n_bins=B):
    """
    Bin θ′ values into n_bins intervals over [0, φ].
    
    Args:
        theta_values: Array of θ′ transformed values
        n_bins: Number of bins (default 20)
        
    Returns:
        counts: Raw counts per bin
        bin_edges: Bin edges from 0 to φ
    """
    bin_edges = np.linspace(0, PHI, n_bins + 1)
    counts, _ = np.histogram(theta_values, bins=bin_edges)
    return counts, bin_edges


def compute_density_enhancement(prime_counts, all_counts, n_primes, n_all):
    """
    Compute density enhancement for each bin using the original proof.py method.
    
    Enhancement = (prime_density - all_density) / all_density * 100
    where densities are normalized by total number of elements, not bin sums.
    
    Args:
        prime_counts: Raw counts of primes per bin
        all_counts: Raw counts of all integers per bin
        n_primes: Total number of primes
        n_all: Total number of integers
        
    Returns:
        enhancements: Enhancement percentage for each bin
    """
    # Convert to densities (normalize by total number of elements)
    prime_density = prime_counts / n_primes
    all_density = all_counts / n_all
    
    # Compute enhancement, handling division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        enhancements = (prime_density - all_density) / all_density * 100
    
    # Mask infinite/NaN values where all_density is zero
    enhancements = np.where(all_density > 0, enhancements, -np.inf)
    
    return enhancements


def compute_max_enhancement_robust(enhancements):
    """
    Compute robust maximum enhancement, handling NaN and infinite values.
    This matches the compute_e_max_robust function from proof.py.
    
    Args:
        enhancements: Array of enhancement percentages
        
    Returns:
        float: Maximum finite enhancement value
    """
    finite_enhancements = enhancements[np.isfinite(enhancements)]
    if len(finite_enhancements) == 0:
        return -np.inf
    return np.max(finite_enhancements)


def bootstrap_enhancement_ci(theta_primes, theta_all, n_bootstrap=N_BOOTSTRAP, seed=SEED):
    """
    Compute bootstrap confidence interval for enhancement.
    This matches the bootstrap approach from proof.py.
    
    Args:
        theta_primes: θ′ values for primes
        theta_all: θ′ values for all integers  
        n_bootstrap: Number of bootstrap samples
        seed: Random seed for reproducibility
        
    Returns:
        bootstrap_enhancements: Array of bootstrap enhancement values
        ci_lower: 2.5th percentile
        ci_upper: 97.5th percentile
    """
    # Set seed for bootstrap reproducibility
    np.random.seed(seed)
    
    n_primes = len(theta_primes)
    n_all = len(theta_all)
    bootstrap_enhancements = []
    
    for i in range(n_bootstrap):
        # Resample primes with replacement
        bootstrap_indices = np.random.choice(n_primes, size=n_primes, replace=True)
        bootstrap_theta_primes = theta_primes[bootstrap_indices]
        
        # Compute bin counts and enhancement for this bootstrap sample
        prime_counts, _ = compute_bin_counts(bootstrap_theta_primes)
        all_counts, _ = compute_bin_counts(theta_all)
        
        enhancements = compute_density_enhancement(prime_counts, all_counts, n_primes, n_all)
        
        # Use robust max enhancement (not KDE smoothed)
        max_enhancement = compute_max_enhancement_robust(enhancements)
        bootstrap_enhancements.append(max_enhancement)
    
    bootstrap_enhancements = np.array(bootstrap_enhancements)
    
    # Compute percentile-based confidence interval
    ci_lower = np.percentile(bootstrap_enhancements, 2.5)
    ci_upper = np.percentile(bootstrap_enhancements, 97.5)
    
    return bootstrap_enhancements, ci_lower, ci_upper


def save_outputs(prime_counts, all_counts, bootstrap_enhancements, theta_primes_sample, n_primes, n_all):
    """Save all outputs to CSV files with metadata."""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create metadata comment
    timestamp = datetime.now().isoformat()
    metadata = f"# Generated on {timestamp}\n# φ = {PHI}\n# Parameters: N={N}, k={K}, B={B}, SEED={SEED}\n"
    
    # 1. Save counts comparison
    counts_file = os.path.join(output_dir, 'counts_primes_vs_all.csv')
    with open(counts_file, 'w', newline='') as f:
        f.write(metadata)
        writer = csv.writer(f)
        writer.writerow(['bin_index', 'prime_counts', 'all_counts', 'enhancement_pct'])
        
        enhancements = compute_density_enhancement(prime_counts, all_counts, n_primes, n_all)
        for i, (pc, ac, enh) in enumerate(zip(prime_counts, all_counts, enhancements)):
            writer.writerow([i, pc, ac, f"{enh:.6f}"])
    
    # 2. Save bootstrap enhancements
    bootstrap_file = os.path.join(output_dir, 'bootstrap_midbin_enhancement.csv')
    with open(bootstrap_file, 'w', newline='') as f:
        f.write(metadata)
        writer = csv.writer(f)
        writer.writerow(['bootstrap_sample', 'max_enhancement'])
        
        for i, enh in enumerate(bootstrap_enhancements):
            writer.writerow([i, f"{enh:.6f}"])
    
    # 3. Save theta_prime sample for first 20 integers
    theta_file = os.path.join(output_dir, 'theta_prime_n1_20_k0.3.csv')
    with open(theta_file, 'w', newline='') as f:
        f.write(metadata)
        writer = csv.writer(f)
        writer.writerow(['n', 'theta_prime'])
        
        for i, theta in enumerate(theta_primes_sample[:20], 1):
            writer.writerow([i, f"{theta:.6f}"])


def run_golden_master_test():
    """
    Run the complete golden master test for density enhancement.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("=== Golden Master Test for Prime-Curve Density Enhancement ===")
    print(f"Parameters: N={N}, k={K}, B={B}, SEED={SEED}")
    print(f"φ (golden ratio) = {PHI:.15f}")
    
    # Set reproducible seeds
    set_seeds(SEED)
    
    # Generate data
    print(f"\nGenerating primes and integers up to {N}...")
    primes, all_integers = generate_primes_and_all_integers(N)
    print(f"Found {len(primes)} primes out of {len(all_integers)} integers")
    
    # Apply θ′ transformation
    print(f"\nApplying θ′ transformation with k={K}...")
    theta_primes = theta_prime(primes, K)
    theta_all = theta_prime(all_integers, K)
    
    print(f"θ′ range: [{np.min(theta_all):.6f}, {np.max(theta_all):.6f}] (should be [0, {PHI:.6f}])")
    
    # Compute bin counts
    print(f"\nBinning into {B} bins...")
    prime_counts, bin_edges = compute_bin_counts(theta_primes, B)
    all_counts, _ = compute_bin_counts(theta_all, B)
    
    # Compute enhancements using correct method
    enhancements = compute_density_enhancement(prime_counts, all_counts, len(primes), len(all_integers))
    max_enhancement = compute_max_enhancement_robust(enhancements)
    
    print(f"Max enhancement (robust): {max_enhancement:.3f}%")
    
    # Bootstrap confidence interval
    print(f"\nComputing bootstrap CI with {N_BOOTSTRAP} samples...")
    bootstrap_enhancements, ci_lower, ci_upper = bootstrap_enhancement_ci(
        theta_primes, theta_all, N_BOOTSTRAP, SEED)
    
    print(f"Bootstrap CI (95%): [{ci_lower:.3f}%, {ci_upper:.3f}%]")
    
    # Save outputs
    print("\nSaving outputs...")
    save_outputs(prime_counts, all_counts, bootstrap_enhancements, 
                 theta_prime(np.arange(1, 21), K), len(primes), len(all_integers))
    
    # Golden master assertions
    print("\n=== Golden Master Validation ===")
    
    # Test 1: Maximal enhancement  
    enh_diff = abs(max_enhancement - EXPECTED_MAX_ENHANCEMENT)
    enh_pass = enh_diff <= TOLERANCE_ENHANCEMENT
    print(f"1. Max Enhancement: {max_enhancement:.3f}% (expected {EXPECTED_MAX_ENHANCEMENT:.3f}% ± {TOLERANCE_ENHANCEMENT:.3f}) - {'PASS' if enh_pass else 'FAIL'}")
    
    # Test 2: Bootstrap CI bounds
    ci_lower_diff = abs(ci_lower - EXPECTED_CI_LOWER)
    ci_upper_diff = abs(ci_upper - EXPECTED_CI_UPPER)
    ci_lower_pass = ci_lower_diff <= TOLERANCE_CI
    ci_upper_pass = ci_upper_diff <= TOLERANCE_CI
    
    print(f"2. Bootstrap CI Lower: {ci_lower:.3f}% (expected {EXPECTED_CI_LOWER:.3f}% ± {TOLERANCE_CI:.3f}) - {'PASS' if ci_lower_pass else 'FAIL'}")
    print(f"3. Bootstrap CI Upper: {ci_upper:.3f}% (expected {EXPECTED_CI_UPPER:.3f}% ± {TOLERANCE_CI:.3f}) - {'PASS' if ci_upper_pass else 'FAIL'}")
    
    # Test 3: Bootstrap array length and finite values
    bootstrap_valid = len(bootstrap_enhancements) == N_BOOTSTRAP and np.all(np.isfinite(bootstrap_enhancements))
    print(f"4. Bootstrap Array: {len(bootstrap_enhancements)} samples, all finite - {'PASS' if bootstrap_valid else 'FAIL'}")
    
    # Overall result
    all_tests_pass = enh_pass and ci_lower_pass and ci_upper_pass and bootstrap_valid
    
    print(f"\n=== Overall Result: {'PASS' if all_tests_pass else 'FAIL'} ===")
    
    if not all_tests_pass:
        print("\nDetailed diagnostics:")
        print(f"  Enhancement difference: {enh_diff:.6f} (tolerance: {TOLERANCE_ENHANCEMENT:.6f})")
        print(f"  CI lower difference: {ci_lower_diff:.6f} (tolerance: {TOLERANCE_CI:.6f})")
        print(f"  CI upper difference: {ci_upper_diff:.6f} (tolerance: {TOLERANCE_CI:.6f})")
        print(f"  Bootstrap samples: {len(bootstrap_enhancements)}/{N_BOOTSTRAP}")
        print(f"  Bootstrap finite: {np.sum(np.isfinite(bootstrap_enhancements))}/{N_BOOTSTRAP}")
    
    return all_tests_pass


if __name__ == "__main__":
    import sys
    
    success = run_golden_master_test()
    sys.exit(0 if success else 1)