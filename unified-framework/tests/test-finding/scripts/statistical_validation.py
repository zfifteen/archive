#!/usr/bin/env python3
"""
Statistical Validation and Mathematical Support for Z Framework
==============================================================

This module provides rigorous statistical validation for key claims in the Z Framework,
including proper confidence intervals, significance testing, and mathematical derivations.

Author: DAL
Created: 2025
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize_scalar
import mpmath as mp
from sympy import sieve, divisors
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import json
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional

# High precision settings
mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2

@dataclass
class ValidationResult:
    """Container for validation results with statistical measures."""
    parameter: float
    enhancement: float
    confidence_interval: Tuple[float, float]
    p_value: float
    effect_size: float
    sample_size: int
    methodology: str
    validation_status: str

class StatisticalValidator:
    """
    Comprehensive statistical validation for Z Framework claims.
    
    This class implements proper statistical methodology to validate
    mathematical claims about prime distributions and optimal parameters.
    """
    
    def __init__(self, N_max: int = 10000, random_seed: int = 42):
        """
        Initialize validator with specified parameters.
        
        Parameters:
        -----------
        N_max : int
            Maximum integer for analysis
        random_seed : int
            Random seed for reproducibility
        """
        np.random.seed(random_seed)
        self.N_max = N_max
        self.primes = list(sieve.primerange(1, N_max + 1))
        self.integers = list(range(1, N_max + 1))
        
        print(f"Initialized StatisticalValidator:")
        print(f"  N_max = {N_max}")
        print(f"  Primes found: {len(self.primes)}")
        print(f"  Prime density: {len(self.primes)/N_max:.4f}")
    
    def theta_prime_transform(self, n: int, k: float) -> float:
        """
        Golden ratio modular transformation with high precision.
        
        Formula: θ'(n,k) = φ · {n/φ}^k
        
        Mathematical Properties:
        - Domain: n ∈ ℤ⁺, k > 0
        - Range: [0, φ)
        - Uses high-precision mpmath for accuracy
        """
        phi = float(PHI)
        fractional_part = (n % phi) / phi
        return phi * (fractional_part ** k)
    
    def compute_binned_enhancement(self, k: float, n_bins: int = 20) -> Tuple[float, np.ndarray, np.ndarray]:
        """
        Compute prime density enhancement in bins for given k.
        
        Returns:
        --------
        max_enhancement : float
            Maximum enhancement percentage across bins
        prime_density : np.ndarray
            Prime density in each bin
        int_density : np.ndarray
            Integer density in each bin
        """
        # Transform sequences
        prime_transforms = np.array([self.theta_prime_transform(p, k) for p in self.primes])
        int_transforms = np.array([self.theta_prime_transform(n, k) for n in self.integers])
        
        # Create bins
        bin_edges = np.linspace(0, float(PHI), n_bins + 1)
        
        # Count occurrences
        prime_counts, _ = np.histogram(prime_transforms, bins=bin_edges)
        int_counts, _ = np.histogram(int_transforms, bins=bin_edges)
        
        # Compute normalized densities
        prime_density = prime_counts / len(self.primes)
        int_density = int_counts / len(self.integers)
        
        # Compute enhancements (avoiding division by zero)
        enhancement = np.zeros(n_bins)
        valid_bins = int_density > 0
        
        if np.any(valid_bins):
            enhancement[valid_bins] = (
                (prime_density[valid_bins] - int_density[valid_bins]) / 
                int_density[valid_bins] * 100
            )
            enhancement[~valid_bins] = -np.inf
            
            # Return maximum valid enhancement
            valid_enhancements = enhancement[enhancement != -np.inf]
            max_enhancement = np.max(valid_enhancements) if len(valid_enhancements) > 0 else 0
        else:
            max_enhancement = 0
        
        return max_enhancement, prime_density, int_density
    
    def bootstrap_confidence_interval(self, k: float, n_bootstrap: int = 1000, 
                                    alpha: float = 0.05) -> Tuple[float, Tuple[float, float]]:
        """
        Compute bootstrap confidence interval for enhancement at given k.
        
        Methodology:
        - Resample primes with replacement
        - Compute enhancement for each bootstrap sample
        - Calculate percentile-based confidence interval
        
        Returns:
        --------
        mean_enhancement : float
            Mean enhancement across bootstrap samples
        ci : tuple
            (lower_bound, upper_bound) confidence interval
        """
        bootstrap_enhancements = []
        
        for _ in range(n_bootstrap):
            # Bootstrap sample of primes
            bootstrap_primes = np.random.choice(self.primes, size=len(self.primes), replace=True)
            
            # Transform bootstrap sample
            bootstrap_transforms = [self.theta_prime_transform(p, k) for p in bootstrap_primes]
            int_transforms = [self.theta_prime_transform(n, k) for n in self.integers]
            
            # Compute enhancement
            bin_edges = np.linspace(0, float(PHI), 21)
            prime_counts, _ = np.histogram(bootstrap_transforms, bins=bin_edges)
            int_counts, _ = np.histogram(int_transforms, bins=bin_edges)
            
            prime_density = prime_counts / len(bootstrap_primes)
            int_density = int_counts / len(self.integers)
            
            valid_bins = int_density > 0
            if np.any(valid_bins):
                enhancement = (prime_density[valid_bins] - int_density[valid_bins]) / int_density[valid_bins] * 100
                max_enhancement = np.max(enhancement) if len(enhancement) > 0 else 0
                bootstrap_enhancements.append(max_enhancement)
        
        if len(bootstrap_enhancements) == 0:
            return 0, (0, 0)
        
        bootstrap_enhancements = np.array(bootstrap_enhancements)
        mean_enhancement = np.mean(bootstrap_enhancements)
        
        # Percentile-based confidence interval
        lower_percentile = 100 * alpha / 2
        upper_percentile = 100 * (1 - alpha / 2)
        
        ci_lower = np.percentile(bootstrap_enhancements, lower_percentile)
        ci_upper = np.percentile(bootstrap_enhancements, upper_percentile)
        
        return mean_enhancement, (ci_lower, ci_upper)
    
    def find_optimal_k(self, k_range: Tuple[float, float] = (0.1, 0.5), 
                      n_points: int = 100) -> ValidationResult:
        """
        Find optimal k* that maximizes prime enhancement with statistical validation.
        
        This method implements a rigorous search for the optimal curvature parameter
        with proper statistical validation including confidence intervals and significance testing.
        """
        print("\n" + "="*60)
        print("RIGOROUS OPTIMAL k* ANALYSIS")
        print("="*60)
        
        k_values = np.linspace(k_range[0], k_range[1], n_points)
        enhancements = []
        
        print(f"Testing {n_points} k values in range {k_range}")
        
        # Compute enhancement for each k
        for i, k in enumerate(k_values):
            enhancement, _, _ = self.compute_binned_enhancement(k)
            enhancements.append(enhancement)
            
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i+1}/{n_points} ({100*(i+1)/n_points:.1f}%)")
        
        enhancements = np.array(enhancements)
        
        # Find optimal k
        best_idx = np.argmax(enhancements)
        k_star = k_values[best_idx]
        max_enhancement = enhancements[best_idx]
        
        print(f"\nOptimal k* found: {k_star:.4f}")
        print(f"Maximum enhancement: {max_enhancement:.2f}%")
        
        # Bootstrap confidence interval for optimal k
        print("\nComputing bootstrap confidence interval...")
        mean_enhancement, ci = self.bootstrap_confidence_interval(k_star, n_bootstrap=1000)
        
        # Significance testing
        print("Performing significance test...")
        p_value = self.test_enhancement_significance(k_star, n_permutations=1000)
        
        # Effect size (Cohen's d)
        effect_size = self.compute_effect_size(k_star)
        
        # Determine validation status
        if ci[0] > 0 and p_value < 0.05:
            validation_status = "VALIDATED"
        elif p_value < 0.05:
            validation_status = "SIGNIFICANT_BUT_UNCERTAIN"
        else:
            validation_status = "NOT_SIGNIFICANT"
        
        result = ValidationResult(
            parameter=k_star,
            enhancement=max_enhancement,
            confidence_interval=ci,
            p_value=p_value,
            effect_size=effect_size,
            sample_size=len(self.primes),
            methodology="Bootstrap CI + Permutation Test",
            validation_status=validation_status
        )
        
        # Print detailed results
        print(f"\n" + "="*60)
        print("STATISTICAL VALIDATION RESULTS")
        print("="*60)
        print(f"Optimal k*: {result.parameter:.4f}")
        print(f"Enhancement: {result.enhancement:.2f}%")
        print(f"95% Confidence Interval: [{ci[0]:.2f}%, {ci[1]:.2f}%]")
        print(f"P-value: {result.p_value:.6f}")
        print(f"Effect Size (Cohen's d): {result.effect_size:.3f}")
        print(f"Sample Size: {result.sample_size}")
        print(f"Validation Status: {result.validation_status}")
        
        return result
    
    def test_enhancement_significance(self, k: float, n_permutations: int = 1000) -> float:
        """
        Test statistical significance of enhancement using permutation test.
        
        H0: Prime distribution is random (no systematic enhancement)
        H1: Primes show systematic enhancement at parameter k
        
        Returns p-value for two-tailed test.
        """
        # Baseline enhancement
        baseline_enhancement, _, _ = self.compute_binned_enhancement(k)
        
        # Permutation test
        permutation_enhancements = []
        
        for _ in range(n_permutations):
            # Random permutation of integer labels
            shuffled_indices = np.random.permutation(len(self.integers))
            pseudo_primes = [self.integers[i] for i in shuffled_indices[:len(self.primes)]]
            
            # Transform pseudo-primes
            pseudo_transforms = [self.theta_prime_transform(p, k) for p in pseudo_primes]
            int_transforms = [self.theta_prime_transform(n, k) for n in self.integers]
            
            # Compute enhancement
            bin_edges = np.linspace(0, float(PHI), 21)
            pseudo_counts, _ = np.histogram(pseudo_transforms, bins=bin_edges)
            int_counts, _ = np.histogram(int_transforms, bins=bin_edges)
            
            pseudo_density = pseudo_counts / len(pseudo_primes)
            int_density = int_counts / len(self.integers)
            
            valid_bins = int_density > 0
            if np.any(valid_bins):
                enhancement = (pseudo_density[valid_bins] - int_density[valid_bins]) / int_density[valid_bins] * 100
                max_enhancement = np.max(enhancement) if len(enhancement) > 0 else 0
                permutation_enhancements.append(max_enhancement)
        
        if len(permutation_enhancements) == 0:
            return 1.0
        
        # Two-tailed p-value
        permutation_enhancements = np.array(permutation_enhancements)
        p_value = np.mean(np.abs(permutation_enhancements) >= abs(baseline_enhancement))
        
        return p_value
    
    def compute_effect_size(self, k: float) -> float:
        """
        Compute Cohen's d effect size for enhancement at given k.
        
        Effect size quantifies the magnitude of the difference in standardized units.
        """
        # Transform sequences
        prime_transforms = [self.theta_prime_transform(p, k) for p in self.primes]
        int_transforms = [self.theta_prime_transform(n, k) for n in self.integers]
        
        # Bin data
        bin_edges = np.linspace(0, float(PHI), 21)
        prime_counts, _ = np.histogram(prime_transforms, bins=bin_edges)
        int_counts, _ = np.histogram(int_transforms, bins=bin_edges)
        
        # Normalize
        prime_density = prime_counts / len(self.primes)
        int_density = int_counts / len(self.integers)
        
        # Cohen's d = (mean1 - mean2) / pooled_std
        mean_diff = np.mean(prime_density) - np.mean(int_density)
        pooled_std = np.sqrt((np.var(prime_density) + np.var(int_density)) / 2)
        
        if pooled_std > 0:
            cohens_d = mean_diff / pooled_std
        else:
            cohens_d = 0
        
        return cohens_d
    
    def validate_documentation_claims(self) -> Dict:
        """
        Validate specific claims made in documentation against computational results.
        
        Returns detailed comparison of claimed vs computed values.
        """
        print("\n" + "="*60)
        print("DOCUMENTATION CLAIMS VALIDATION")
        print("="*60)
        
        # Documented claims
        claimed_k_star = 0.3
        claimed_enhancement = 15.0
        claimed_ci = (14.6, 15.4)
        
        # Compute actual values
        actual_result = self.find_optimal_k()
        
        # Compute values at claimed k*
        claimed_enhancement_actual, _, _ = self.compute_binned_enhancement(claimed_k_star)
        claimed_mean, claimed_ci_actual = self.bootstrap_confidence_interval(claimed_k_star)
        
        # Analysis
        k_discrepancy = abs(actual_result.parameter - claimed_k_star)
        enhancement_discrepancy = abs(actual_result.enhancement - claimed_enhancement)
        
        validation_summary = {
            'claimed': {
                'k_star': claimed_k_star,
                'enhancement': claimed_enhancement,
                'confidence_interval': claimed_ci
            },
            'computed': {
                'k_star': actual_result.parameter,
                'enhancement': actual_result.enhancement,
                'confidence_interval': actual_result.confidence_interval
            },
            'at_claimed_k': {
                'enhancement': claimed_enhancement_actual,
                'confidence_interval': claimed_ci_actual
            },
            'discrepancies': {
                'k_star': k_discrepancy,
                'enhancement': enhancement_discrepancy
            },
            'validation_status': 'MAJOR_DISCREPANCIES' if (k_discrepancy > 0.05 or enhancement_discrepancy > 10) else 'CONSISTENT'
        }
        
        # Print detailed comparison
        print(f"\nCLAIMED vs COMPUTED:")
        print(f"k*: {claimed_k_star:.3f} vs {actual_result.parameter:.3f} (discrepancy: {k_discrepancy:.3f})")
        print(f"Enhancement: {claimed_enhancement:.1f}% vs {actual_result.enhancement:.1f}% (discrepancy: {enhancement_discrepancy:.1f}%)")
        print(f"CI: {claimed_ci} vs {actual_result.confidence_interval}")
        
        print(f"\nAt claimed k*={claimed_k_star}:")
        print(f"Enhancement: {claimed_enhancement_actual:.1f}%")
        print(f"CI: [{claimed_ci_actual[0]:.1f}%, {claimed_ci_actual[1]:.1f}%]")
        
        print(f"\nVALIDATION STATUS: {validation_summary['validation_status']}")
        
        return validation_summary

def main():
    """Run comprehensive statistical validation of Z Framework claims."""
    print("Z FRAMEWORK STATISTICAL VALIDATION")
    print("="*60)
    print("This module provides rigorous statistical validation for mathematical claims")
    print("in the Z Framework, including proper confidence intervals and significance testing.")
    print("")
    
    # Initialize validator
    validator = StatisticalValidator(N_max=5000)
    
    # Run comprehensive validation
    results = validator.validate_documentation_claims()
    
    # Save results
    with open('statistical_validation_results.json', 'w') as f:
        # Convert numpy types to native Python for JSON serialization
        results_serializable = {}
        for key, value in results.items():
            if isinstance(value, dict):
                results_serializable[key] = {k: float(v) if isinstance(v, (np.float64, np.float32)) else v 
                                           for k, v in value.items()}
            else:
                results_serializable[key] = float(value) if isinstance(value, (np.float64, np.float32)) else value
        
        json.dump(results_serializable, f, indent=2)
    
    print(f"\n" + "="*60)
    print("STATISTICAL VALIDATION COMPLETE")
    print("="*60)
    print("Results saved to: statistical_validation_results.json")
    print("See VALIDATION.md for interpretation and next steps")

if __name__ == "__main__":
    main()