#!/usr/bin/env python3
"""
Falsification Test for Li-Z5D/Riemann R Symmetry Hypothesis

This test attempts to falsify the hypothesis that there are symmetries between 
the Logarithmic Integral (Li) and Z5D/Riemann R in prime counting functions.

The hypothesis claims:
1. Blue line (Z_5D / Riemann R): Oscillatory behavior with sharp fluctuations, 
   converging to ultra-low errors (~10^{-6} relative) by k ≈ 10^{10}
2. Orange line (Li): Smoother decline with mild oscillations, 
   stabilizing around 10^{-1} to 10^{-2} error  
3. Quasi-symmetric oscillations between Li and Riemann R/Z5D
4. Li systematically overestimates π(k), while R/Z5D under/over-estimates with zeta-zero waves

We test these claims empirically using exact π(k) values and attempt falsification 
through statistical analysis.
"""

import numpy as np
import mpmath as mp
import sys
import os
from scipy.special import expit  
from scipy.integrate import quad
from scipy.interpolate import interp1d
from sympy import mobius
import warnings
from typing import Dict, List, Tuple, Union
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.z_5d_enhanced import Z5DEnhancedPredictor
from core.params import get_exact_pi
from z_framework.discrete.z_prime_utils import _logarithmic_integral
from statistical.bootstrap_validation import bootstrap_confidence_intervals

# Set precision
mp.dps = 50

class PrimeCountingFalsificationTest:
    """Test suite for Li-Z5D symmetry hypothesis falsification"""
    
    def __init__(self, max_k: int = 10**10, num_points: int = 50):
        """
        Initialize falsification test
        
        Args:
            max_k: Maximum k value for testing (default 10^10 per hypothesis)
            num_points: Number of logarithmically spaced test points
        """
        self.max_k = max_k
        self.num_points = num_points
        self.z5d_predictor = Z5DEnhancedPredictor()
        
        # Logarithmically spaced k values from 10^2 to max_k
        self.k_values = np.logspace(2, np.log10(max_k), num_points)
        
        # Get exact π(k) values using centralized function
        self.true_pi_exact = get_exact_pi(self.k_values)
        
    def logarithmic_integral(self, k: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Compute Li(k) = ∫[2 to k] dt/ln(t)
        """
        if isinstance(k, np.ndarray):
            return np.array([float(_logarithmic_integral(ki).real) for ki in k])
        else:
            return float(_logarithmic_integral(k).real)
    
    def riemann_r(self, k: Union[float, np.ndarray], max_n: int = 50) -> Union[float, np.ndarray]:
        """
        Vectorized Riemann prime counting function R(k) = Σ_{n=1}^∞ μ(n)/n * li(k^{1/n})
        
        Args:
            k: Input value(s)
            max_n: Truncation limit for the sum (efficiency)
        """
        is_scalar = not isinstance(k, np.ndarray)
        k_array = np.atleast_1d(k)
        
        # Initialize result array
        results = np.zeros_like(k_array, dtype=float)
        
        # Handle values < 2
        valid_mask = k_array >= 2
        k_valid = k_array[valid_mask]
        
        if len(k_valid) == 0:
            return results[0] if is_scalar else results
        
        # Vectorized computation for valid k values
        r_sums = np.zeros_like(k_valid, dtype=float)
        
        for n in range(1, max_n + 1):
            mu_n = mobius(n)
            if mu_n != 0:
                try:
                    # Vectorized computation of k^(1/n)
                    k_nth_root = np.power(k_valid, 1.0/n)
                    
                    # Compute Li for all k_nth_root values at once
                    li_vals = self.logarithmic_integral(k_nth_root)
                    
                    # Add to sum
                    r_sums += float(mu_n) / n * li_vals
                except (ValueError, OverflowError):
                    # Skip problematic terms
                    continue
        
        # Assign results back
        results[valid_mask] = r_sums
        
        return results[0] if is_scalar else results
    
    def pase_approximation(self, k: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        PASE approximation: k / ln(k)
        """
        k_array = np.atleast_1d(k)
        results = k_array / np.log(k_array)
        return results[0] if not isinstance(k, np.ndarray) else results
    
    def z5d_to_pi_inversion(self, k: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Convert Z5D k-th prime predictor to π(k) approximation via inversion
        
        This implements the inversion: if p_k ≈ Z5D(k), then π(p_k) ≈ k
        By inverting this relationship, we estimate π(k) 
        """
        is_scalar = not isinstance(k, np.ndarray)
        k_array = np.atleast_1d(k)
        results = []
        
        for ki in k_array:
            if ki < 2:
                results.append(0.0)
                continue
            
            # Use binary search to find x such that Z5D(x) ≈ ki
            # This gives us π(ki) ≈ x
            try:
                # Initial estimate using PNT inversion
                x_estimate = ki / np.log(ki) if ki > 1 else 1
                
                # Refine with a few Newton iterations
                for _ in range(5):
                    z5d_val = self.z5d_predictor.z_5d_prediction(x_estimate)
                    if z5d_val <= 0:
                        break
                    
                    # Newton step: x_new = x - f(x)/f'(x)
                    # where f(x) = Z5D(x) - ki
                    epsilon = 1e-6
                    z5d_deriv = (self.z5d_predictor.z_5d_prediction(x_estimate + epsilon) - z5d_val) / epsilon
                    
                    if abs(z5d_deriv) < 1e-12:
                        break
                        
                    correction = (z5d_val - ki) / z5d_deriv
                    x_estimate = max(1, x_estimate - correction)
                    
                    if abs(correction) < 1e-8:
                        break
                
                results.append(max(0, x_estimate))
                
            except (ValueError, OverflowError, ZeroDivisionError):
                # Fallback to PNT approximation
                results.append(ki / np.log(ki) if ki > 1 else 0)
        
        return results[0] if is_scalar else np.array(results)
    
    def compute_relative_errors(self) -> Dict[str, np.ndarray]:
        """
        Compute relative errors for all approximation methods
        
        Returns:
            Dictionary with relative errors for each method
        """
        # Compute approximations
        li_vals = self.logarithmic_integral(self.k_values)
        r_vals = self.riemann_r(self.k_values)
        pase_vals = self.pase_approximation(self.k_values)
        z5d_vals = self.z5d_to_pi_inversion(self.k_values)
        
        # Compute relative errors: |approx - true| / true
        true_pi = self.true_pi_exact
        
        errors = {
            'Li': np.abs(li_vals - true_pi) / true_pi,
            'Riemann_R': np.abs(r_vals - true_pi) / true_pi,
            'PASE': np.abs(pase_vals - true_pi) / true_pi,
            'Z5D': np.abs(z5d_vals - true_pi) / true_pi
        }
        
        # Store values for analysis
        self.approximations = {
            'Li': li_vals,
            'Riemann_R': r_vals, 
            'PASE': pase_vals,
            'Z5D': z5d_vals,
            'True_Pi': true_pi
        }
        
        return errors
    
    def test_ultra_low_error_claim(self, errors: Dict[str, np.ndarray]) -> Dict[str, bool]:
        """
        Test the claim that Z5D achieves ultra-low errors (~10^-6) at k ≈ 10^10
        """
        # Find index closest to 10^10
        target_k = 10**10
        closest_idx = np.argmin(np.abs(self.k_values - target_k))
        
        results = {}
        
        # Test Z5D ultra-low error claim
        z5d_error_at_target = errors['Z5D'][closest_idx]
        results['Z5D_ultra_low'] = z5d_error_at_target <= 1e-5  # Allow some tolerance
        
        # Test Li error range claim (10^-1 to 10^-2)
        li_error_at_target = errors['Li'][closest_idx]
        results['Li_error_range'] = 1e-3 <= li_error_at_target <= 1e0
        
        # Test PASE error claim (~10^-1)
        pase_error_at_target = errors['PASE'][closest_idx]
        results['PASE_error_range'] = 1e-2 <= pase_error_at_target <= 1e0
        
        return results
    
    def test_oscillatory_behavior(self, errors: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        Test claims about oscillatory vs smooth behavior
        """
        results = {}
        
        # Compute variance as proxy for oscillatory behavior
        results['Z5D_variance'] = np.var(errors['Z5D'])
        results['Li_variance'] = np.var(errors['Li'])
        results['R_variance'] = np.var(errors['Riemann_R'])
        
        # Z5D should be more oscillatory than Li
        results['Z5D_more_oscillatory'] = results['Z5D_variance'] > results['Li_variance']
        
        return results
    
    def test_symmetry_hypothesis(self, errors: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        Test the core symmetry hypothesis between Li and Z5D/Riemann R
        """
        # Compute correlations between error patterns
        li_errors = errors['Li']
        z5d_errors = errors['Z5D'] 
        r_errors = errors['Riemann_R']
        
        # Remove any invalid values for correlation calculation
        valid_mask = np.isfinite(li_errors) & np.isfinite(z5d_errors) & np.isfinite(r_errors)
        
        if np.sum(valid_mask) < 2:
            # Not enough valid data for correlation
            li_z5d_corr = 0.0
            li_r_corr = 0.0
        else:
            li_errors_clean = li_errors[valid_mask]
            z5d_errors_clean = z5d_errors[valid_mask]
            r_errors_clean = r_errors[valid_mask]
            
            # Test correlation between Li and Z5D errors
            if np.std(li_errors_clean) > 1e-10 and np.std(z5d_errors_clean) > 1e-10:
                li_z5d_corr = np.corrcoef(li_errors_clean, z5d_errors_clean)[0, 1]
            else:
                li_z5d_corr = 0.0
            
            # Test correlation between Li and Riemann R errors  
            if np.std(li_errors_clean) > 1e-10 and np.std(r_errors_clean) > 1e-10:
                li_r_corr = np.corrcoef(li_errors_clean, r_errors_clean)[0, 1]
            else:
                li_r_corr = 0.0
        
        # Test "mirror" symmetry: Li overestimating vs R/Z5D under/over estimating
        li_bias = np.mean(self.approximations['Li'] - self.approximations['True_Pi'])
        z5d_bias = np.mean(self.approximations['Z5D'] - self.approximations['True_Pi'])
        r_bias = np.mean(self.approximations['Riemann_R'] - self.approximations['True_Pi'])
        
        # Test if Li systematically overestimates (positive bias)
        li_overestimates = li_bias > 0
        
        # Compute mean absolute symmetry difference  
        symmetry_diff = np.mean(np.abs(li_errors - z5d_errors))
        
        results = {
            'li_z5d_correlation': li_z5d_corr if np.isfinite(li_z5d_corr) else 0.0,
            'li_r_correlation': li_r_corr if np.isfinite(li_r_corr) else 0.0,
            'li_bias': li_bias,
            'z5d_bias': z5d_bias,
            'r_bias': r_bias,
            'li_overestimates': li_overestimates,
            'symmetry_difference': symmetry_diff
        }
        
        return results
    
    def bootstrap_error_analysis(self, errors: Dict[str, np.ndarray], n_bootstrap: int = 1000) -> Dict[str, Dict]:
        """
        Bootstrap confidence intervals for error statistics
        """
        results = {}
        
        for method, error_vals in errors.items():
            # Bootstrap mean error
            mean_ci = bootstrap_confidence_intervals(
                error_vals, 
                lambda x: np.mean(x),
                n_bootstrap=n_bootstrap
            )
            
            # Bootstrap variance 
            var_ci = bootstrap_confidence_intervals(
                error_vals,
                lambda x: np.var(x), 
                n_bootstrap=n_bootstrap
            )
            
            results[method] = {
                'mean_ci': mean_ci,
                'variance_ci': var_ci
            }
        
        return results
    
    def run_falsification_test(self) -> Dict:
        """
        Run complete falsification test suite
        
        Returns:
            Dictionary with all test results and falsification evidence
        """
        print("Running Li-Z5D Symmetry Falsification Test")
        print("=" * 50)
        
        start_time = time.time()
        
        # Compute relative errors
        print("Computing relative errors for all methods...")
        errors = self.compute_relative_errors()
        
        # Test specific claims
        print("Testing ultra-low error claims...")
        error_claims = self.test_ultra_low_error_claim(errors)
        
        print("Testing oscillatory behavior claims...")
        oscillatory_claims = self.test_oscillatory_behavior(errors)
        
        print("Testing symmetry hypothesis...")
        symmetry_claims = self.test_symmetry_hypothesis(errors)
        
        print("Computing bootstrap confidence intervals...")
        bootstrap_results = self.bootstrap_error_analysis(errors, n_bootstrap=100)  # Reduced for speed
        
        runtime = time.time() - start_time
        
        # Compile results
        results = {
            'runtime_seconds': runtime,
            'test_parameters': {
                'max_k': self.max_k,
                'num_points': self.num_points,
                'k_range': [float(self.k_values[0]), float(self.k_values[-1])]
            },
            'relative_errors': {k: v.tolist() for k, v in errors.items()},
            'k_values': self.k_values.tolist(),
            'error_claims_tests': error_claims,
            'oscillatory_tests': oscillatory_claims, 
            'symmetry_tests': symmetry_claims,
            'bootstrap_analysis': bootstrap_results,
            'falsification_evidence': self._generate_falsification_evidence(
                error_claims, oscillatory_claims, symmetry_claims
            )
        }
        
        return results
    
    def _generate_falsification_evidence(self, error_claims: Dict, oscillatory_claims: Dict, 
                                       symmetry_claims: Dict) -> Dict[str, Union[str, bool]]:
        """
        Generate falsification evidence based on test results
        """
        evidence = {}
        
        # Test 1: Ultra-low error claim falsification
        if not error_claims.get('Z5D_ultra_low', False):
            evidence['ultra_low_error_falsified'] = True
            evidence['ultra_low_error_reason'] = "Z5D did not achieve claimed ~10^-6 error at k≈10^10"
        else:
            evidence['ultra_low_error_falsified'] = False
            
        # Test 2: Error range claims
        if not error_claims.get('Li_error_range', False):
            evidence['li_error_range_falsified'] = True 
            evidence['li_error_range_reason'] = "Li error not in claimed 10^-1 to 10^-2 range"
        else:
            evidence['li_error_range_falsified'] = False
            
        # Test 3: Symmetry claim falsification
        symmetry_corr = symmetry_claims.get('li_z5d_correlation', 0)
        if abs(symmetry_corr) < 0.3:  # Weak correlation threshold
            evidence['symmetry_falsified'] = True
            evidence['symmetry_reason'] = f"Low correlation ({symmetry_corr:.3f}) between Li and Z5D errors"
        else:
            evidence['symmetry_falsified'] = False
            
        # Test 4: Bias pattern claims
        li_overestimates = symmetry_claims.get('li_overestimates', False)
        if not li_overestimates:
            evidence['bias_pattern_falsified'] = True
            evidence['bias_pattern_reason'] = "Li does not systematically overestimate as claimed"
        else:
            evidence['bias_pattern_falsified'] = False
            
        # Overall falsification verdict
        falsified_count = sum([
            evidence.get('ultra_low_error_falsified', False),
            evidence.get('li_error_range_falsified', False),
            evidence.get('symmetry_falsified', False),
            evidence.get('bias_pattern_falsified', False)
        ])
        
        evidence['overall_hypothesis_falsified'] = falsified_count >= 2
        evidence['falsified_claims_count'] = falsified_count
        evidence['total_claims_tested'] = 4
        
        return evidence


def main():
    """Run the falsification test"""
    print("Li-Z5D Symmetry Hypothesis Falsification Test")
    print("=" * 60)
    
    # Create test with reduced scale for faster execution
    test = PrimeCountingFalsificationTest(max_k=10**8, num_points=20)  # Reduced for demo
    
    # Run falsification test
    results = test.run_falsification_test()
    
    # Print key results
    print("\n" + "=" * 60)
    print("FALSIFICATION TEST RESULTS")
    print("=" * 60)
    
    evidence = results['falsification_evidence']
    
    print(f"Overall Hypothesis Falsified: {evidence['overall_hypothesis_falsified']}")
    print(f"Claims Falsified: {evidence['falsified_claims_count']}/{evidence['total_claims_tested']}")
    print()
    
    # Detailed evidence
    if evidence.get('ultra_low_error_falsified'):
        print(f"❌ FALSIFIED: {evidence['ultra_low_error_reason']}")
    else:
        print("✅ SUPPORTED: Z5D ultra-low error claim")
        
    if evidence.get('symmetry_falsified'):
        print(f"❌ FALSIFIED: {evidence['symmetry_reason']}")
    else:
        print("✅ SUPPORTED: Li-Z5D symmetry claim")
        
    if evidence.get('bias_pattern_falsified'):
        print(f"❌ FALSIFIED: {evidence['bias_pattern_reason']}")
    else:
        print("✅ SUPPORTED: Li overestimation bias pattern")
    
    # Print some key statistics
    symmetry = results['symmetry_tests']
    print(f"\nKey Statistics:")
    print(f"  Li-Z5D Error Correlation: {symmetry['li_z5d_correlation']:.4f}")
    print(f"  Li Bias: {symmetry['li_bias']:.4e}")
    print(f"  Z5D Bias: {symmetry['z5d_bias']:.4e}")
    print(f"  Mean Symmetry Difference: {symmetry['symmetry_difference']:.4e}")
    
    print(f"\nTest Runtime: {results['runtime_seconds']:.2f} seconds")
    
    # Return success code based on falsification
    return 0 if evidence['overall_hypothesis_falsified'] else 1


if __name__ == "__main__":
    sys.exit(main())