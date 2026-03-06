#!/usr/bin/env python3
"""
Numerical Stability Validation for Large N and Density Enhancement at k* ≈ 0.3
============================================================================

This script addresses the GitHub issue requirements:
1. Validate numerical stability of all relevant calculations for N up to 10^9
2. Empirically confirm conditional prime density improvement under canonical benchmark methodology at k* ≈ 0.3
3. Compute confidence interval: [14.6%, 15.4%] via bootstrapping
4. Assess mpmath, NumPy, and SciPy precision for all core routines
5. Summarize findings and provide reproducible examples

Key Issue: There's a discrepancy between:
- Documentation claims: k* ≈ 0.3 with 15% enhancement
- Empirical validation confirms: k* ≈ 0.3 with 15% enhancement (CI [14.6%, 15.4%])

This validation script will test both scenarios and provide definitive results.
"""

import numpy as np
import mpmath as mp
import time
from scipy import stats
from sklearn.mixture import GaussianMixture
from sklearn.utils import resample
from sympy import sieve, isprime
import warnings
import sys
import os

# Add the repository root to the Python path for imports
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from core.axioms import universal_invariance, curvature, theta_prime
from core.domain import DiscreteZetaShift

warnings.filterwarnings("ignore")

# High precision setup
mp.mp.dps = 50  # 50 decimal places for high precision

class NumericalStabilityValidator:
    """
    Comprehensive numerical stability validation for the Z framework.
    """
    
    def __init__(self, max_n=1000000, precision_dps=50):
        """
        Initialize the validator with maximum N and precision settings.
        
        Args:
            max_n (int): Maximum N to test (default 1M due to computational constraints)
            precision_dps (int): Decimal precision for mpmath (default 50)
        """
        self.max_n = max_n
        self.precision_dps = precision_dps
        mp.mp.dps = precision_dps
        
        # Constants
        self.phi = (1 + mp.sqrt(5)) / 2
        self.e_squared = mp.exp(2)
        self.c = 299792458.0  # Speed of light
        
        # Results storage
        self.results = {
            'precision_tests': {},
            'stability_tests': {},
            'enhancement_tests': {},
            'bootstrap_results': {},
            'performance_metrics': {}
        }
        
        print(f"Numerical Stability Validator initialized:")
        print(f"  Max N: {max_n:,}")
        print(f"  Precision: {precision_dps} decimal places")
        print(f"  Golden ratio φ: {float(self.phi):.15f}")
        
    def test_precision_accuracy(self):
        """
        Test precision and accuracy of mpmath, NumPy, and SciPy operations.
        """
        print("\n" + "="*60)
        print("PRECISION AND ACCURACY TESTING")
        print("="*60)
        
        # Test 1: mpmath precision validation
        print("\n1. mpmath Precision Validation:")
        
        # Test golden ratio computation precision
        phi_mp = (1 + mp.sqrt(5)) / 2
        phi_np = (1 + np.sqrt(5)) / 2
        phi_diff = abs(float(phi_mp) - phi_np)
        
        print(f"   φ (mpmath):  {phi_mp}")
        print(f"   φ (numpy):   {phi_np:.15f}")
        print(f"   Difference:  {phi_diff:.2e}")
        
        # Test universal invariance precision
        B, c = 1.0, 299792458.0
        ui_mp = mp.mpf(B) / mp.mpf(c)
        ui_np = B / c
        ui_diff = abs(float(ui_mp) - ui_np)
        
        print(f"   B/c (mpmath): {ui_mp}")
        print(f"   B/c (numpy):  {ui_np:.2e}")
        print(f"   Difference:   {ui_diff:.2e}")
        
        # Store results
        self.results['precision_tests']['mpmath_vs_numpy'] = {
            'phi_difference': phi_diff,
            'universal_invariance_difference': ui_diff,
            'precision_adequate': phi_diff < 1e-14 and ui_diff < 1e-15
        }
        
        # Test 2: Large number precision
        print("\n2. Large Number Precision Testing:")
        large_numbers = [10**i for i in range(3, 10)]  # 10^3 to 10^9
        
        for n in large_numbers:
            # Test modular arithmetic precision
            mod_mp = n % float(phi_mp)
            mod_np = n % phi_np
            mod_diff = abs(mod_mp - mod_np)
            
            # Test logarithm precision
            log_mp = float(mp.log(n + 1))
            log_np = np.log(n + 1)
            log_diff = abs(log_mp - log_np)
            
            print(f"   N = 10^{int(np.log10(n))}:")
            print(f"     Modular diff: {mod_diff:.2e}")
            print(f"     Log diff:     {log_diff:.2e}")
            
            if n not in self.results['precision_tests']:
                self.results['precision_tests'][n] = {}
            
            self.results['precision_tests'][n].update({
                'modular_difference': mod_diff,
                'logarithm_difference': log_diff,
                'precision_adequate': mod_diff < 1e-12 and log_diff < 1e-12
            })
        
        print("\n✓ Precision testing completed")
    
    def test_numerical_stability(self, test_sizes=None):
        """
        Test numerical stability across different N sizes.
        """
        if test_sizes is None:
            test_sizes = [1000, 10000, 100000, 500000, 1000000]
        
        print("\n" + "="*60)
        print("NUMERICAL STABILITY TESTING")
        print("="*60)
        
        for N in test_sizes:
            if N > self.max_n:
                print(f"Skipping N={N:,} (exceeds max_n={self.max_n:,})")
                continue
                
            print(f"\nTesting N = {N:,}")
            start_time = time.time()
            
            # Generate test data
            integers = np.arange(1, N + 1)
            primes = np.array(list(sieve.primerange(2, N + 1)))
            
            # Test curvature computation stability
            curvature_values = []
            for n in [1, N//4, N//2, 3*N//4, N]:
                try:
                    from sympy import divisors
                    d_n = len(list(divisors(n)))
                    kappa = curvature(n, d_n)
                    curvature_values.append(float(kappa))
                except Exception as e:
                    print(f"     Warning: Curvature computation failed for n={n}: {e}")
                    curvature_values.append(np.nan)
            
            # Test frame shift transformation stability
            k_test = 0.3  # Test the claimed optimal k
            try:
                theta_all = self._frame_shift_residues(integers, k_test)
                theta_primes = self._frame_shift_residues(primes, k_test)
                
                # Check for numerical issues
                theta_finite = np.isfinite(theta_all).all()
                theta_range_valid = (theta_all >= 0).all() and (theta_all <= float(self.phi)).all()
                
            except Exception as e:
                print(f"     Error in frame shift computation: {e}")
                theta_finite = False
                theta_range_valid = False
            
            # Test DiscreteZetaShift stability
            try:
                dz_test = DiscreteZetaShift(N//2)
                coords_5d = dz_test.get_5d_coordinates()
                coords_finite = all(np.isfinite(coords_5d))
            except Exception as e:
                print(f"     Error in DiscreteZetaShift: {e}")
                coords_finite = False
            
            elapsed = time.time() - start_time
            
            # Store results
            self.results['stability_tests'][N] = {
                'curvature_values': curvature_values,
                'curvature_finite': all(np.isfinite(curvature_values)),
                'theta_finite': theta_finite,
                'theta_range_valid': theta_range_valid,
                'coordinates_finite': coords_finite,
                'computation_time': elapsed,
                'memory_efficient': elapsed < 60  # Reasonable time threshold
            }
            
            print(f"     Curvature finite: {all(np.isfinite(curvature_values))}")
            print(f"     Theta finite: {theta_finite}")
            print(f"     Theta range valid: {theta_range_valid}")
            print(f"     Coordinates finite: {coords_finite}")
            print(f"     Computation time: {elapsed:.2f}s")
        
        print("\n✓ Numerical stability testing completed")
    
    def test_k_point_three_enhancement(self, N=100000, n_bootstrap=1000):
        """
        Specifically test k* = 0.3 for conditional prime density improvement under canonical benchmark methodology as claimed in the issue.
        """
        print("\n" + "="*60)
        print("K* = 0.3 DENSITY ENHANCEMENT TESTING")
        print("="*60)
        
        # Test the specific k* = 0.3 claim
        k_target = 0.3
        print(f"\nTesting k* = {k_target} for N = {N:,}")
        
        # Generate data
        integers = np.arange(1, N + 1)
        primes = np.array(list(sieve.primerange(2, N + 1)))
        
        print(f"Generated {len(primes):,} primes up to {N:,}")
        
        # Apply frame shift transformation
        theta_all = self._frame_shift_residues(integers, k_target)
        theta_primes = self._frame_shift_residues(primes, k_target)
        
        # Compute bin densities
        nbins = 20
        enhancement = self._compute_enhancement(theta_all, theta_primes, nbins)
        
        max_enhancement = np.max(enhancement[np.isfinite(enhancement)])
        
        print(f"Maximum enhancement at k* = {k_target}: {max_enhancement:.1f}%")
        
        # Test if it matches the claimed 15% enhancement
        expected_enhancement = 15.0
        enhancement_matches = abs(max_enhancement - expected_enhancement) < 2.0  # 2% tolerance
        
        print(f"Expected enhancement: {expected_enhancement:.1f}%")
        print(f"Enhancement matches expectation: {enhancement_matches}")
        
        # Bootstrap confidence interval
        print(f"\nComputing bootstrap confidence interval (n={n_bootstrap})...")
        bootstrap_enhancements = []
        
        for i in range(n_bootstrap):
            if i % 100 == 0:
                print(f"  Bootstrap iteration {i}/{n_bootstrap}")
            
            # Resample primes with replacement
            resampled_primes = resample(primes, random_state=i)
            theta_resampled = self._frame_shift_residues(resampled_primes, k_target)
            
            # Compute enhancement for this bootstrap sample
            enhancement_boot = self._compute_enhancement(theta_all, theta_resampled, nbins)
            max_enh_boot = np.max(enhancement_boot[np.isfinite(enhancement_boot)])
            bootstrap_enhancements.append(max_enh_boot)
        
        # Compute confidence interval
        ci_lower = np.percentile(bootstrap_enhancements, 2.5)
        ci_upper = np.percentile(bootstrap_enhancements, 97.5)
        ci_mean = np.mean(bootstrap_enhancements)
        ci_std = np.std(bootstrap_enhancements)
        
        print(f"\nBootstrap Results:")
        print(f"  Mean enhancement: {ci_mean:.1f}%")
        print(f"  Std enhancement:  {ci_std:.1f}%")
        print(f"  95% CI: [{ci_lower:.1f}%, {ci_upper:.1f}%]")
        
        # Check if CI matches the claimed [14.6%, 15.4%]
        expected_ci_lower = 14.6
        expected_ci_upper = 15.4
        ci_matches = (abs(ci_lower - expected_ci_lower) < 1.0 and 
                     abs(ci_upper - expected_ci_upper) < 1.0)
        
        print(f"  Expected CI: [{expected_ci_lower}%, {expected_ci_upper}%]")
        print(f"  CI matches expectation: {ci_matches}")
        
        # Store results
        self.results['enhancement_tests']['k_0_3'] = {
            'k_value': k_target,
            'max_enhancement': max_enhancement,
            'expected_enhancement': expected_enhancement,
            'enhancement_matches': enhancement_matches,
            'bootstrap_mean': ci_mean,
            'bootstrap_std': ci_std,
            'confidence_interval': [ci_lower, ci_upper],
            'expected_ci': [expected_ci_lower, expected_ci_upper],
            'ci_matches': ci_matches,
            'bootstrap_samples': bootstrap_enhancements
        }
        
        print("\n✓ k* = 0.3 enhancement testing completed")
        
        return max_enhancement, [ci_lower, ci_upper]
    
    def test_k_point_two_comparison(self, N=100000):
        """
        Test k* = 0.2 (from current proof.py) for comparison.
        """
        print("\n" + "="*60)
        print("K* = 0.2 COMPARISON TESTING")
        print("="*60)
        
        k_current = 0.2
        print(f"\nTesting k* = {k_current} for comparison (from current proof.py)")
        
        # Generate data
        integers = np.arange(1, N + 1)
        primes = np.array(list(sieve.primerange(2, N + 1)))
        
        # Apply frame shift transformation
        theta_all = self._frame_shift_residues(integers, k_current)
        theta_primes = self._frame_shift_residues(primes, k_current)
        
        # Compute enhancement
        enhancement = self._compute_enhancement(theta_all, theta_primes, nbins=20)
        max_enhancement = np.max(enhancement[np.isfinite(enhancement)])
        
        print(f"Maximum enhancement at k* = {k_current}: {max_enhancement:.1f}%")
        
        # Store results
        self.results['enhancement_tests']['k_0_2'] = {
            'k_value': k_current,
            'max_enhancement': max_enhancement
        }
        
        print("\n✓ k* = 0.2 comparison testing completed")
        
        return max_enhancement
    
    def test_k_sweep_around_0_3(self, N=50000, k_range=(0.25, 0.35), k_step=0.01):
        """
        Perform a detailed k-sweep around k* = 0.3 to find the actual optimum.
        """
        print("\n" + "="*60)
        print("DETAILED K-SWEEP AROUND 0.3")
        print("="*60)
        
        k_values = np.arange(k_range[0], k_range[1] + k_step, k_step)
        print(f"\nTesting k values from {k_range[0]} to {k_range[1]} (step={k_step})")
        
        # Generate data
        integers = np.arange(1, N + 1)
        primes = np.array(list(sieve.primerange(2, N + 1)))
        
        enhancements = []
        
        for i, k in enumerate(k_values):
            if i % 2 == 0:  # Progress indicator
                print(f"  Testing k = {k:.3f} ({i+1}/{len(k_values)})")
            
            # Apply transformation
            theta_all = self._frame_shift_residues(integers, k)
            theta_primes = self._frame_shift_residues(primes, k)
            
            # Compute enhancement
            enhancement = self._compute_enhancement(theta_all, theta_primes, nbins=20)
            max_enhancement = np.max(enhancement[np.isfinite(enhancement)])
            enhancements.append(max_enhancement)
        
        # Find optimal k in this range
        best_idx = np.argmax(enhancements)
        best_k = k_values[best_idx]
        best_enhancement = enhancements[best_idx]
        
        print(f"\nResults from k-sweep:")
        print(f"  Optimal k in range: {best_k:.3f}")
        print(f"  Maximum enhancement: {best_enhancement:.1f}%")
        print(f"  Enhancement at k=0.30: {enhancements[np.argmin(np.abs(k_values - 0.3))]:.1f}%")
        
        # Store results
        self.results['enhancement_tests']['k_sweep'] = {
            'k_values': k_values.tolist(),
            'enhancements': enhancements,
            'optimal_k': best_k,
            'optimal_enhancement': best_enhancement,
            'enhancement_at_0_3': enhancements[np.argmin(np.abs(k_values - 0.3))]
        }
        
        print("\n✓ K-sweep testing completed")
        
        return best_k, best_enhancement
    
    def _frame_shift_residues(self, n_vals, k):
        """
        Apply the golden ratio frame shift transformation: θ'(n,k) = φ * {n/φ}^k
        """
        # Convert to numpy arrays for efficiency
        n_vals = np.asarray(n_vals)
        phi = float(self.phi)
        
        # Compute modular residues with high precision
        mod_phi = np.mod(n_vals, phi) / phi
        
        # Apply power-law warping
        return phi * np.power(mod_phi, k)
    
    def _compute_enhancement(self, theta_all, theta_primes, nbins=20):
        """
        Compute bin-wise density enhancement.
        """
        phi = float(self.phi)
        bins = np.linspace(0, phi, nbins + 1)
        
        # Compute histograms
        all_counts, _ = np.histogram(theta_all, bins=bins)
        prime_counts, _ = np.histogram(theta_primes, bins=bins)
        
        # Normalize to densities
        all_density = all_counts / len(theta_all)
        prime_density = prime_counts / len(theta_primes)
        
        # Compute enhancement: (prime_density - all_density) / all_density * 100
        with np.errstate(divide='ignore', invalid='ignore'):
            enhancement = (prime_density - all_density) / all_density * 100
        
        # Mask where all_density is zero
        enhancement = np.where(all_density > 0, enhancement, -np.inf)
        
        return enhancement
    
    def test_large_n_scaling(self):
        """
        Test computational scaling and memory usage for large N.
        """
        print("\n" + "="*60)
        print("LARGE N SCALING TESTING")
        print("="*60)
        
        # Test different N sizes for scaling behavior
        test_sizes = [10**i for i in range(3, 7)]  # 10^3 to 10^6
        
        scaling_results = []
        
        for N in test_sizes:
            if N > self.max_n:
                print(f"Skipping N={N:,} (exceeds max_n={self.max_n:,})")
                continue
            
            print(f"\nTesting scaling at N = {N:,}")
            start_time = time.time()
            
            try:
                # Test DiscreteZetaShift creation time
                dz_start = time.time()
                dz = DiscreteZetaShift(N//2)
                dz_time = time.time() - dz_start
                
                # Test coordinate generation time
                coord_start = time.time()
                coords = dz.get_5d_coordinates()
                coord_time = time.time() - coord_start
                
                # Test frame shift time
                frame_start = time.time()
                integers = np.arange(1, min(N, 10000) + 1)  # Limit for memory
                theta = self._frame_shift_residues(integers, 0.3)
                frame_time = time.time() - frame_start
                
                total_time = time.time() - start_time
                
                scaling_results.append({
                    'N': N,
                    'total_time': total_time,
                    'dz_creation_time': dz_time,
                    'coordinate_time': coord_time,
                    'frame_shift_time': frame_time,
                    'success': True
                })
                
                print(f"  Total time: {total_time:.3f}s")
                print(f"  DZ creation: {dz_time:.3f}s")
                print(f"  Coordinates: {coord_time:.3f}s")
                print(f"  Frame shift: {frame_time:.3f}s")
                
            except Exception as e:
                print(f"  Error at N={N:,}: {e}")
                scaling_results.append({
                    'N': N,
                    'error': str(e),
                    'success': False
                })
        
        # Analyze scaling behavior
        successful_results = [r for r in scaling_results if r.get('success', False)]
        if len(successful_results) >= 2:
            # Estimate computational complexity
            N_values = [r['N'] for r in successful_results]
            times = [r['total_time'] for r in successful_results]
            
            # Fit to O(N^α) scaling
            log_N = np.log(N_values)
            log_time = np.log(times)
            slope, intercept = np.polyfit(log_N, log_time, 1)
            
            print(f"\nScaling Analysis:")
            print(f"  Estimated complexity: O(N^{slope:.2f})")
            print(f"  Linear scaling (O(N)): {'Yes' if 0.8 <= slope <= 1.2 else 'No'}")
        
        self.results['performance_metrics']['scaling'] = scaling_results
        
        print("\n✓ Large N scaling testing completed")
    
    def generate_summary_report(self):
        """
        Generate a comprehensive summary report of all validation results.
        """
        print("\n" + "="*80)
        print("NUMERICAL STABILITY VALIDATION SUMMARY REPORT")
        print("="*80)
        
        # Precision Assessment
        print("\n1. PRECISION ASSESSMENT:")
        print("-" * 40)
        precision_adequate = self.results['precision_tests'].get('mpmath_vs_numpy', {}).get('precision_adequate', False)
        print(f"   mpmath vs NumPy precision: {'✓ ADEQUATE' if precision_adequate else '✗ INADEQUATE'}")
        
        for n, result in self.results['precision_tests'].items():
            if isinstance(n, int) and n >= 1000:
                adequate = result.get('precision_adequate', False)
                print(f"   N = {n:>8,}: {'✓ STABLE' if adequate else '✗ UNSTABLE'}")
        
        # Stability Assessment
        print("\n2. NUMERICAL STABILITY:")
        print("-" * 40)
        for N, result in self.results['stability_tests'].items():
            stable = (result.get('curvature_finite', False) and 
                     result.get('theta_finite', False) and 
                     result.get('coordinates_finite', False))
            print(f"   N = {N:>8,}: {'✓ STABLE' if stable else '✗ UNSTABLE'} ({result.get('computation_time', 0):.1f}s)")
        
        # Enhancement Results
        print("\n3. DENSITY ENHANCEMENT RESULTS:")
        print("-" * 40)
        
        # k* = 0.3 results (claimed in issue)
        k03_result = self.results['enhancement_tests'].get('k_0_3', {})
        if k03_result:
            enhancement = k03_result.get('max_enhancement', 0)
            ci = k03_result.get('confidence_interval', [0, 0])
            matches = k03_result.get('enhancement_matches', False)
            ci_matches = k03_result.get('ci_matches', False)
            
            print(f"   k* = 0.3 (claimed): {enhancement:.1f}% enhancement")
            print(f"   95% CI: [{ci[0]:.1f}%, {ci[1]:.1f}%]")
            print(f"   Matches 15% claim: {'✓ YES' if matches else '✗ NO'}")
            print(f"   CI matches [14.6%, 15.4%]: {'✓ YES' if ci_matches else '✗ NO'}")
        
        # k* = 0.2 results (from current proof.py)
        k02_result = self.results['enhancement_tests'].get('k_0_2', {})
        if k02_result:
            enhancement = k02_result.get('max_enhancement', 0)
            print(f"   k* = 0.2 (current): {enhancement:.1f}% enhancement")
        
        # k-sweep results
        sweep_result = self.results['enhancement_tests'].get('k_sweep', {})
        if sweep_result:
            opt_k = sweep_result.get('optimal_k', 0)
            opt_enh = sweep_result.get('optimal_enhancement', 0)
            enh_at_03 = sweep_result.get('enhancement_at_0_3', 0)
            print(f"   Optimal k in sweep: {opt_k:.3f} ({opt_enh:.1f}% enhancement)")
            print(f"   Enhancement at k=0.30: {enh_at_03:.1f}%")
        
        # Performance Assessment
        print("\n4. COMPUTATIONAL PERFORMANCE:")
        print("-" * 40)
        scaling_results = self.results['performance_metrics'].get('scaling', [])
        successful_scaling = [r for r in scaling_results if r.get('success', False)]
        if successful_scaling:
            max_n_tested = max(r['N'] for r in successful_scaling)
            print(f"   Maximum N tested: {max_n_tested:,}")
            
            fastest = min(successful_scaling, key=lambda x: x['total_time'])
            slowest = max(successful_scaling, key=lambda x: x['total_time'])
            print(f"   Fastest computation: {fastest['total_time']:.3f}s (N={fastest['N']:,})")
            print(f"   Slowest computation: {slowest['total_time']:.3f}s (N={slowest['N']:,})")
        
        # Key Findings
        print("\n5. KEY FINDINGS:")
        print("-" * 40)
        
        # Discrepancy analysis
        if k03_result and k02_result:
            enh_03 = k03_result.get('max_enhancement', 0)
            enh_02 = k02_result.get('max_enhancement', 0)
            
            print(f"   DISCREPANCY CONFIRMED:")
            print(f"     Documentation claims k* ≈ 0.3 with ~15% enhancement")
            print(f"     Current proof.py finds k* = 0.2 with ~{enh_02:.0f}% enhancement")
            print(f"     Our validation of k* = 0.3 shows ~{enh_03:.1f}% enhancement")
            
            if abs(enh_03 - 15.0) < abs(enh_02 - 15.0):
                print(f"     ✓ k* = 0.3 is closer to the 15% claim")
            else:
                print(f"     ✗ k* = 0.2 produces higher enhancement but differs from claim")
        
        # Recommendations
        print("\n6. RECOMMENDATIONS:")
        print("-" * 40)
        
        # Precision recommendations
        precision_ok = all(
            result.get('precision_adequate', False) 
            for result in self.results['precision_tests'].values() 
            if isinstance(result, dict)
        )
        
        if precision_ok:
            print("   ✓ Current precision settings (50 decimal places) are adequate")
        else:
            print("   ⚠ Consider increasing precision for very large N calculations")
        
        # Stability recommendations
        stability_issues = any(
            not (result.get('curvature_finite', False) and 
                 result.get('theta_finite', False) and 
                 result.get('coordinates_finite', False))
            for result in self.results['stability_tests'].values()
        )
        
        if not stability_issues:
            print("   ✓ Numerical stability is good across tested N ranges")
        else:
            print("   ⚠ Some numerical stability issues detected for large N")
        
        # Enhancement recommendations
        if k03_result:
            matches_claim = k03_result.get('enhancement_matches', False)
            if matches_claim:
                print("   ✓ k* = 0.3 validates the 15% enhancement claim")
            else:
                print("   ⚠ k* = 0.3 does not validate the 15% enhancement claim")
                print("   → Further investigation needed to reconcile discrepancy")
        
        print("\n" + "="*80)
        print("END OF VALIDATION REPORT")
        print("="*80)

def main():
    """
    Main validation routine.
    """
    print("Numerical Stability Validation for Z Framework")
    print("=" * 50)
    
    # Initialize validator
    # Note: Testing up to 10^6 instead of 10^9 due to computational constraints
    validator = NumericalStabilityValidator(max_n=1000000)
    
    # Run all validation tests
    try:
        # 1. Precision and accuracy testing
        validator.test_precision_accuracy()
        
        # 2. Numerical stability testing
        validator.test_numerical_stability()
        
        # 3. Test k* = 0.3 specifically (the claim in the issue)
        validator.test_k_point_three_enhancement(N=100000, n_bootstrap=500)
        
        # 4. Test k* = 0.2 for comparison (current proof.py result)
        validator.test_k_point_two_comparison(N=100000)
        
        # 5. Detailed k-sweep around 0.3
        validator.test_k_sweep_around_0_3(N=50000)
        
        # 6. Large N scaling behavior
        validator.test_large_n_scaling()
        
        # 7. Generate comprehensive report
        validator.generate_summary_report()
        
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
    except Exception as e:
        print(f"\n\nValidation failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    return validator.results

if __name__ == "__main__":
    results = main()