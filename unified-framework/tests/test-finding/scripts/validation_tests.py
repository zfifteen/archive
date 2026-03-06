#!/usr/bin/env python3
"""
Validation Test Suite for Z Framework
=====================================

This script tests key computational claims in the Z Framework and identifies
discrepancies between documentation and implementation.

Usage: python3 validation_tests.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from sympy import sieve
import mpmath as mp
from scipy import stats
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

# Set high precision
mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2

class ValidationTests:
    """Test suite for validating Z Framework computational claims."""
    
    def __init__(self, N_max=1000):
        """Initialize with maximum number for testing."""
        self.N_max = N_max
        self.primes = list(sieve.primerange(1, N_max + 1))
        self.integers = list(range(1, N_max + 1))
        print(f"Initialized with {len(self.primes)} primes up to {N_max}")
    
    def theta_prime_transform(self, n, k):
        """Golden ratio modular transformation."""
        phi = float(PHI)
        return phi * ((n % phi) / phi) ** k
    
    def test_optimal_k_claim(self, k_range=(0.2, 0.4), delta_k=0.002, n_bins=20):
        """
        Test the claim about optimal k* and prime enhancement.
        
        Documentation claims: k* ≈ 0.3, enhancement ≈ 15%
        Empirical validation (August 2025): k* ≈ 0.3, enhancement = 15% (CI [14.6%, 15.4%])
        """
        print("\n=== Testing Optimal k* Claim ===")
        
        k_values = np.arange(k_range[0], k_range[1] + delta_k, delta_k)
        enhancements = []
        
        for k in k_values:
            # Transform primes and integers
            prime_transforms = [self.theta_prime_transform(p, k) for p in self.primes]
            int_transforms = [self.theta_prime_transform(n, k) for n in self.integers]
            
            # Create bins
            max_val = float(PHI)
            bin_edges = np.linspace(0, max_val, n_bins + 1)
            
            # Count in bins
            prime_counts, _ = np.histogram(prime_transforms, bins=bin_edges)
            int_counts, _ = np.histogram(int_transforms, bins=bin_edges)
            
            # Compute densities and enhancements
            prime_density = prime_counts / len(self.primes)
            int_density = int_counts / len(self.integers)
            
            # Avoid division by zero
            valid_bins = int_density > 0
            if not np.any(valid_bins):
                enhancements.append(-np.inf)
                continue
            
            enhancement = np.zeros(n_bins)
            enhancement[valid_bins] = (prime_density[valid_bins] - int_density[valid_bins]) / int_density[valid_bins] * 100
            enhancement[~valid_bins] = -np.inf
            
            max_enhancement = np.max(enhancement[enhancement != -np.inf])
            enhancements.append(max_enhancement)
        
        enhancements = np.array(enhancements)
        valid_enhancements = enhancements[enhancements != -np.inf]
        
        if len(valid_enhancements) == 0:
            print("ERROR: No valid enhancements computed!")
            return None
        
        # Find optimal k
        valid_indices = enhancements != -np.inf
        best_idx = np.argmax(enhancements[valid_indices])
        k_star = k_values[valid_indices][best_idx]
        max_enhancement = valid_enhancements[best_idx]
        
        print(f"Computed k* = {k_star:.3f}")
        print(f"Max enhancement = {max_enhancement:.1f}%")
        print(f"Documentation claims: k* ≈ 0.3, enhancement ≈ 15%")
        
        # Check consistency
        k_discrepancy = abs(k_star - 0.3)
        enhancement_discrepancy = abs(max_enhancement - 15.0)
        
        print(f"\nDISCREPANCY ANALYSIS:")
        print(f"k* discrepancy: {k_discrepancy:.3f}")
        print(f"Enhancement discrepancy: {enhancement_discrepancy:.1f}%")
        
        if k_discrepancy > 0.05 or enhancement_discrepancy > 10:
            print("⚠️  VALIDATION FAILURE: Significant discrepancies detected!")
        else:
            print("✅ VALIDATION PASSED: Results consistent with documentation")
        
        return {
            'k_star': k_star,
            'max_enhancement': max_enhancement,
            'k_values': k_values,
            'enhancements': enhancements
        }
    
    def test_statistical_significance(self, k_star, n_bootstrap=100):
        """
        Test statistical significance of prime enhancement at k*.
        
        H0: No systematic enhancement (random distribution)
        H1: Systematic enhancement exists
        """
        print(f"\n=== Testing Statistical Significance at k*={k_star:.3f} ===")
        
        # Compute baseline enhancement
        prime_transforms = [self.theta_prime_transform(p, k_star) for p in self.primes]
        
        # Bootstrap test
        bootstrap_enhancements = []
        n_primes = len(self.primes)
        
        for _ in range(n_bootstrap):
            # Random sample of integers (same size as primes)
            random_sample = np.random.choice(self.integers, size=n_primes, replace=False)
            random_transforms = [self.theta_prime_transform(n, k_star) for n in random_sample]
            
            # Compute enhancement for random sample
            bin_edges = np.linspace(0, float(PHI), 21)
            prime_counts, _ = np.histogram(prime_transforms, bins=bin_edges)
            random_counts, _ = np.histogram(random_transforms, bins=bin_edges)
            
            prime_density = prime_counts / len(prime_transforms)
            random_density = random_counts / len(random_transforms)
            
            valid_bins = random_density > 0
            if np.any(valid_bins):
                enhancement = (prime_density[valid_bins] - random_density[valid_bins]) / random_density[valid_bins] * 100
                max_enhancement = np.max(enhancement) if len(enhancement) > 0 else 0
                bootstrap_enhancements.append(max_enhancement)
        
        if len(bootstrap_enhancements) == 0:
            print("ERROR: No bootstrap samples computed!")
            return None
        
        # Compute baseline enhancement
        int_transforms = [self.theta_prime_transform(n, k_star) for n in self.integers]
        bin_edges = np.linspace(0, float(PHI), 21)
        prime_counts, _ = np.histogram(prime_transforms, bins=bin_edges)
        int_counts, _ = np.histogram(int_transforms, bins=bin_edges)
        
        prime_density = prime_counts / len(self.primes)
        int_density = int_counts / len(self.integers)
        valid_bins = int_density > 0
        
        if np.any(valid_bins):
            baseline_enhancement = (prime_density[valid_bins] - int_density[valid_bins]) / int_density[valid_bins] * 100
            baseline_max = np.max(baseline_enhancement)
        else:
            baseline_max = 0
        
        # Statistical test
        bootstrap_mean = np.mean(bootstrap_enhancements)
        bootstrap_std = np.std(bootstrap_enhancements)
        
        if bootstrap_std > 0:
            z_score = (baseline_max - bootstrap_mean) / bootstrap_std
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed test
        else:
            z_score = np.inf if baseline_max > bootstrap_mean else 0
            p_value = 0
        
        print(f"Baseline enhancement: {baseline_max:.1f}%")
        print(f"Bootstrap mean: {bootstrap_mean:.1f}%")
        print(f"Bootstrap std: {bootstrap_std:.1f}%")
        print(f"Z-score: {z_score:.2f}")
        print(f"P-value: {p_value:.6f}")
        
        alpha = 0.05
        if p_value < alpha:
            print(f"✅ SIGNIFICANT: Enhancement is statistically significant (p < {alpha})")
        else:
            print(f"❌ NOT SIGNIFICANT: Enhancement is not statistically significant (p >= {alpha})")
        
        return {
            'baseline_enhancement': baseline_max,
            'bootstrap_mean': bootstrap_mean,
            'bootstrap_std': bootstrap_std,
            'z_score': z_score,
            'p_value': p_value
        }
    
    def test_precision_claims(self):
        """Test high-precision computation claims."""
        print("\n=== Testing Precision Claims ===")
        
        # Test mpmath precision
        print(f"mpmath precision: {mp.mp.dps} decimal places")
        
        # Test golden ratio precision
        phi_computed = float(PHI)
        phi_expected = (1 + np.sqrt(5)) / 2
        phi_error = abs(phi_computed - phi_expected)
        
        print(f"Golden ratio φ = {phi_computed}")
        print(f"Error vs numpy: {phi_error:.2e}")
        
        # Test modular operation precision for large n
        test_values = [100, 1000, 10000]
        for n in test_values:
            mod_result = n % float(PHI)
            fractional_part = mod_result / float(PHI)
            print(f"n={n}: n mod φ = {mod_result:.10f}, fractional = {fractional_part:.10f}")
        
        print("✅ Precision tests completed")
    
    def run_all_tests(self):
        """Run all validation tests."""
        print("Z FRAMEWORK VALIDATION TEST SUITE")
        print("=" * 40)
        
        # Test 1: Optimal k* claim
        k_results = self.test_optimal_k_claim()
        
        if k_results is not None:
            # Test 2: Statistical significance
            self.test_statistical_significance(k_results['k_star'])
        
        # Test 3: Precision claims
        self.test_precision_claims()
        
        print("\n" + "=" * 40)
        print("VALIDATION SUMMARY:")
        print("- Check VALIDATION.md for detailed analysis")
        print("- Resolve computational discrepancies before publication")
        print("- Add proper statistical validation methodology")

if __name__ == "__main__":
    # Run validation tests
    validator = ValidationTests(N_max=1000)
    validator.run_all_tests()