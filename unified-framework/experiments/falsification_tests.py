#!/usr/bin/env python3
"""
Enhanced Sieve Algorithm Falsification Tests
==========================================

This module implements systematic falsification tests for the Z Framework's
Enhanced Sieve Algorithm claims, specifically targeting:

1. conditional prime density improvement under canonical benchmark methodology (CI: [14.6%, 15.4%])
2. 20% acceleration in prime generation 
3. Optimal k* ≈ 0.3 for curvature geodesics
4. Prime corridors modulo 30 effectiveness
5. Superiority over random selection methods

Author: Copilot (GitHub Issue #391)
Date: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, kstest, normaltest, chi2_contingency
from sympy import divisors, isprime, nextprime
import mpmath as mp
import time
import sys
import os
import warnings
from collections import defaultdict

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.geodesic_mapping import GeodesicMapper
    from core.z_5d_enhanced import Z5DEnhancedPredictor
    from core.z_baseline import BaselineZFramework
    CORE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Core modules not available: {e}")
    CORE_MODULES_AVAILABLE = False

# Constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
E_SQUARED = np.exp(2)
PRIME_CORRIDORS_MOD30 = [1, 7, 11, 13, 17, 19, 23, 29]

class EnhancedSieveFalsificationSuite:
    """Comprehensive falsification test suite for Enhanced Sieve Algorithm claims"""
    
    def __init__(self, seed=42):
        """Initialize test suite with reproducible random seed"""
        self.seed = seed
        np.random.seed(seed)
        self.results = {}
        self.verbose = True
        
        if CORE_MODULES_AVAILABLE:
            self.geodesic_mapper = GeodesicMapper(k_optimal=0.3)
            self.z5d_predictor = Z5DEnhancedPredictor()
            self.baseline = BaselineZFramework()
        else:
            print("Running tests with local implementations only")
    
    def log(self, message):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(message)
    
    def test_1_prime_density_enhancement_falsification(self, N=10000):
        """
        Test 1: Prime Density Enhancement Claims
        
        Systematically test the claimed 15% ± 0.4% enhancement by:
        - Testing multiple scale ranges
        - Comparing against random baselines  
        - Statistical significance testing
        - Confidence interval validation
        
        Falsification criteria:
        - Enhancement < 10% (significantly below claimed 15%)
        - No statistical significance vs random
        - Confidence intervals don't overlap claimed [14.6%, 15.4%]
        """
        self.log("=== Test 1: Prime Density Enhancement Falsification ===")
        
        # Generate test data
        test_scales = [1000, 5000, 10000, 20000]
        enhancements = []
        random_comparisons = []
        statistical_significance = []
        
        for scale in test_scales:
            self.log(f"Testing density enhancement at scale N={scale}")
            
            # Generate primes up to scale
            primes = [p for p in range(2, scale) if isprime(p)]
            
            if len(primes) < 50:
                continue
                
            # Test geodesic enhancement
            if CORE_MODULES_AVAILABLE:
                enhancement_result = self.geodesic_mapper.compute_density_enhancement(
                    primes, n_bins=50, n_bootstrap=500
                )
                enhancement_pct = enhancement_result.get('enhancement_percent', 0) * 100
                ci_lower = enhancement_result.get('ci_lower', 0) * 100  
                ci_upper = enhancement_result.get('ci_upper', 0) * 100
            else:
                # Local implementation
                enhancement_pct, ci_lower, ci_upper = self._local_density_enhancement(primes)
            
            # Compare against random selection baseline
            random_enhancements = []
            for _ in range(10):  # Multiple random trials
                random_selection = np.random.choice(primes, size=len(primes)//4, replace=False)
                random_enhancement = self._compute_random_enhancement(random_selection, primes)
                random_enhancements.append(random_enhancement)
            
            random_mean = np.mean(random_enhancements)
            random_std = np.std(random_enhancements)
            
            # Statistical significance test
            if enhancement_pct > random_mean + 2 * random_std:
                is_significant = True
            else:
                is_significant = False
            
            enhancements.append(enhancement_pct)
            random_comparisons.append(random_mean)
            statistical_significance.append(is_significant)
            
            self.log(f"  Enhancement: {enhancement_pct:.2f}% (CI: [{ci_lower:.2f}%, {ci_upper:.2f}%])")
            self.log(f"  Random baseline: {random_mean:.2f}% ± {random_std:.2f}%")
            self.log(f"  Statistically significant: {is_significant}")
        
        # Falsification analysis
        mean_enhancement = np.mean(enhancements)
        claimed_range = [14.6, 15.4]
        
        falsification_flags = []
        
        # Check if enhancement is significantly below claimed 15%
        if mean_enhancement < 10.0:
            falsification_flags.append("Enhancement significantly below 15% claim")
        
        # Check if any enhancements overlap claimed confidence interval
        overlaps_claimed_ci = any(
            ci_lower <= 15.4 and ci_upper >= 14.6 
            for ci_lower, ci_upper in [(mean_enhancement - 2, mean_enhancement + 2)]
        )
        if not overlaps_claimed_ci:
            falsification_flags.append("Confidence intervals don't overlap claimed [14.6%, 15.4%]")
        
        # Check statistical significance 
        if sum(statistical_significance) < len(statistical_significance) * 0.8:
            falsification_flags.append("Less than 80% of tests show statistical significance")
        
        self.results['test_1'] = {
            'scales': test_scales,
            'enhancements': enhancements,
            'random_comparisons': random_comparisons,
            'statistical_significance': statistical_significance,
            'mean_enhancement': mean_enhancement,
            'falsification_flags': falsification_flags,
            'is_falsified': len(falsification_flags) > 0
        }
        
        if falsification_flags:
            self.log(f"✗ FALSIFICATION DETECTED: {'; '.join(falsification_flags)}")
            return False
        else:
            self.log("✓ Density enhancement claims survive falsification attempt")
            return True
    
    def test_2_sieve_acceleration_falsification(self, max_n=100000):
        """
        Test 2: 20% Sieve Acceleration Claims
        
        Test the claimed 20% acceleration in prime generation by:
        - Implementing enhanced sieve vs standard sieve
        - Measuring actual performance improvements
        - Testing across different scales
        
        Falsification criteria:
        - Acceleration < 10% (significantly below claimed 20%)
        - No consistent performance improvement
        - Performance degrades at larger scales
        """
        self.log("=== Test 2: Sieve Acceleration Falsification ===")
        
        test_ranges = [1000, 10000, 50000, 100000]
        acceleration_factors = []
        
        for n_limit in test_ranges:
            self.log(f"Testing sieve acceleration up to N={n_limit}")
            
            # Standard sieve implementation
            start_time = time.time()
            standard_primes = self._standard_sieve_of_eratosthenes(n_limit)
            standard_time = time.time() - start_time
            
            # Enhanced sieve with modulo 30 corridors
            start_time = time.time()
            enhanced_primes = self._enhanced_sieve_with_corridors(n_limit)
            enhanced_time = time.time() - start_time
            
            # Calculate acceleration factor
            if enhanced_time > 0:
                acceleration = (standard_time - enhanced_time) / enhanced_time * 100
            else:
                acceleration = 0
            
            acceleration_factors.append(acceleration)
            
            # Verify correctness
            standard_set = set(standard_primes)
            enhanced_set = set(enhanced_primes)
            accuracy = len(standard_set & enhanced_set) / len(standard_set) * 100
            
            self.log(f"  Acceleration: {acceleration:.2f}%")
            self.log(f"  Accuracy: {accuracy:.2f}%")
            self.log(f"  Standard time: {standard_time:.4f}s, Enhanced time: {enhanced_time:.4f}s")
        
        # Falsification analysis
        mean_acceleration = np.mean(acceleration_factors)
        
        falsification_flags = []
        
        # Check if acceleration is significantly below claimed 20%
        if mean_acceleration < 10.0:
            falsification_flags.append("Acceleration significantly below 20% claim")
        
        # Check for performance degradation at scale
        if len(acceleration_factors) >= 2:
            if acceleration_factors[-1] < acceleration_factors[0] * 0.5:
                falsification_flags.append("Performance degrades significantly at larger scales")
        
        # Check consistency (standard deviation)
        if np.std(acceleration_factors) > mean_acceleration * 0.5:
            falsification_flags.append("Highly inconsistent performance across scales")
        
        self.results['test_2'] = {
            'test_ranges': test_ranges,
            'acceleration_factors': acceleration_factors,
            'mean_acceleration': mean_acceleration,
            'falsification_flags': falsification_flags,
            'is_falsified': len(falsification_flags) > 0
        }
        
        if falsification_flags:
            self.log(f"✗ FALSIFICATION DETECTED: {'; '.join(falsification_flags)}")
            return False
        else:
            self.log("✓ Sieve acceleration claims survive falsification attempt")
            return True
    
    def test_3_optimal_k_parameter_falsification(self):
        """
        Test 3: Optimal k* ≈ 0.3 Parameter Claims
        
        Test the claim that k* ≈ 0.3 is optimal by:
        - Testing k values across wide range [0.1, 1.0]
        - Measuring enhancement for each k value
        - Statistical analysis of optimality
        
        Falsification criteria:
        - k=0.3 is not optimal (other k values perform significantly better)
        - Multiple k values perform equally well (no clear optimum)
        - Enhancement is insensitive to k choice
        """
        self.log("=== Test 3: Optimal k* Parameter Falsification ===")
        
        k_values = np.linspace(0.1, 1.0, 19)  # Test 19 k values
        N = 5000
        primes = [p for p in range(2, N) if isprime(p)]
        
        enhancements_by_k = []
        
        for k in k_values:
            # Test geodesic transformation with this k value
            if CORE_MODULES_AVAILABLE:
                temp_mapper = GeodesicMapper(k_optimal=k)
                enhancement_result = temp_mapper.compute_density_enhancement(
                    primes, n_bins=30, n_bootstrap=200
                )
                enhancement = enhancement_result.get('enhancement_percent', 0) * 100
            else:
                enhancement = self._local_geodesic_enhancement(primes, k)
            
            enhancements_by_k.append(enhancement)
            self.log(f"  k={k:.2f}: Enhancement = {enhancement:.2f}%")
        
        # Find optimal k
        optimal_idx = np.argmax(enhancements_by_k)
        optimal_k = k_values[optimal_idx]
        optimal_enhancement = enhancements_by_k[optimal_idx]
        
        # Find enhancement at claimed k=0.3
        k_03_idx = np.argmin(np.abs(k_values - 0.3))
        k_03_enhancement = enhancements_by_k[k_03_idx]
        
        falsification_flags = []
        
        # Check if k=0.3 is significantly suboptimal
        enhancement_diff = optimal_enhancement - k_03_enhancement
        if enhancement_diff > 5.0:  # 5% difference threshold
            falsification_flags.append(f"k={optimal_k:.2f} performs {enhancement_diff:.1f}% better than k=0.3")
        
        # Check if enhancement is insensitive to k
        enhancement_range = max(enhancements_by_k) - min(enhancements_by_k)
        if enhancement_range < 2.0:  # Less than 2% variation
            falsification_flags.append("Enhancement insensitive to k choice (< 2% variation)")
        
        # Check for multiple optima (flat landscape)
        top_10_percent = np.percentile(enhancements_by_k, 90)
        num_near_optimal = sum(1 for e in enhancements_by_k if e >= top_10_percent)
        if num_near_optimal > len(k_values) * 0.3:  # >30% of k values are near-optimal
            falsification_flags.append("Multiple k values perform equally well (no clear optimum)")
        
        self.results['test_3'] = {
            'k_values': k_values.tolist(),
            'enhancements_by_k': enhancements_by_k,
            'optimal_k': optimal_k,
            'optimal_enhancement': optimal_enhancement,
            'k_03_enhancement': k_03_enhancement,
            'enhancement_diff': enhancement_diff,
            'falsification_flags': falsification_flags,
            'is_falsified': len(falsification_flags) > 0
        }
        
        if falsification_flags:
            self.log(f"✗ FALSIFICATION DETECTED: {'; '.join(falsification_flags)}")
            return False
        else:
            self.log("✓ Optimal k* ≈ 0.3 claims survive falsification attempt")
            return True
    
    def test_4_prime_corridors_mod30_falsification(self, N=30000):
        """
        Test 4: Prime Corridors Modulo 30 Effectiveness
        
        Test the effectiveness of focusing on residue classes {1,7,11,13,17,19,23,29} mod 30:
        - Compare corridor-based vs uniform random selection
        - Test statistical significance of prime concentration
        - Validate against other moduli (wheel factorization comparison)
        
        Falsification criteria:
        - No significant concentration in claimed corridors
        - Other moduli perform equally well or better
        - Random selection within corridors performs as well
        """
        self.log("=== Test 4: Prime Corridors Modulo 30 Falsification ===")
        
        # Generate primes up to N
        primes = [p for p in range(2, N) if isprime(p)]
        primes_gt_5 = [p for p in primes if p > 5]  # Exclude 2, 3, 5 as specified
        
        # Analyze distribution in corridors mod 30
        corridor_counts = defaultdict(int)
        non_corridor_counts = defaultdict(int)
        
        for prime in primes_gt_5:
            residue = prime % 30
            if residue in PRIME_CORRIDORS_MOD30:
                corridor_counts[residue] += 1
            else:
                non_corridor_counts[residue] += 1
        
        total_corridor_primes = sum(corridor_counts.values())
        total_non_corridor_primes = sum(non_corridor_counts.values())
        
        # Expected distribution if uniform
        total_primes_gt_5 = len(primes_gt_5)
        expected_corridor_fraction = len(PRIME_CORRIDORS_MOD30) / 30  # 8/30
        expected_corridor_count = total_primes_gt_5 * expected_corridor_fraction
        
        # Chi-square test for corridor concentration
        observed = [total_corridor_primes, total_non_corridor_primes]
        expected = [expected_corridor_count, total_primes_gt_5 - expected_corridor_count]
        
        try:
            chi2_stat, chi2_p = chi2_contingency([observed, expected])[:2]
        except:
            chi2_stat, chi2_p = 0, 1.0
        
        # Test against other wheel moduli
        other_moduli = [6, 12, 30, 60, 210]  # Common wheel factorization moduli
        moduli_concentrations = {}
        
        for modulus in other_moduli:
            if modulus != 30:
                # Find coprime residues for this modulus
                coprime_residues = [i for i in range(1, modulus) if np.gcd(i, modulus) == 1]
                
                # Count primes in these residues
                in_coprime = sum(1 for p in primes_gt_5 if (p % modulus) in coprime_residues)
                concentration = in_coprime / len(primes_gt_5)
                moduli_concentrations[modulus] = concentration
        
        # Corridor concentration for mod 30
        corridor_concentration = total_corridor_primes / len(primes_gt_5)
        
        falsification_flags = []
        
        # Check statistical significance of corridor concentration
        if chi2_p > 0.05:  # Not statistically significant
            falsification_flags.append(f"Corridor concentration not statistically significant (p={chi2_p:.3f})")
        
        # Check if other moduli perform better
        mod30_concentration = corridor_concentration
        better_moduli = [(mod, conc) for mod, conc in moduli_concentrations.items() 
                        if conc > mod30_concentration + 0.05]  # 5% threshold
        
        if better_moduli:
            falsification_flags.append(f"Other moduli perform better: {better_moduli}")
        
        # Check if concentration is minimal
        if corridor_concentration < 0.85:  # Should be very high for effective sieving
            falsification_flags.append(f"Low corridor concentration: {corridor_concentration:.3f}")
        
        self.results['test_4'] = {
            'total_primes_analyzed': len(primes_gt_5),
            'corridor_counts': dict(corridor_counts),
            'total_corridor_primes': total_corridor_primes,
            'corridor_concentration': corridor_concentration,
            'chi2_stat': chi2_stat,
            'chi2_p': chi2_p,
            'moduli_concentrations': moduli_concentrations,
            'falsification_flags': falsification_flags,
            'is_falsified': len(falsification_flags) > 0
        }
        
        if falsification_flags:
            self.log(f"✗ FALSIFICATION DETECTED: {'; '.join(falsification_flags)}")
            return False
        else:
            self.log("✓ Prime corridors mod 30 claims survive falsification attempt")
            return True
    
    def test_5_geodesic_vs_random_falsification(self, N=5000, num_trials=20):
        """
        Test 5: Geodesic Mapping vs Random Selection
        
        Compare geodesic mapping performance against sophisticated random baselines:
        - Random selection with same statistical properties
        - Random selection with equivalent computational cost
        - Multiple random strategies
        
        Falsification criteria:
        - Random methods perform as well as geodesic mapping
        - No consistent advantage for geodesic mapping
        - Statistical indistinguishability from random
        """
        self.log("=== Test 5: Geodesic vs Random Selection Falsification ===")
        
        primes = [p for p in range(2, N) if isprime(p)]
        
        # Geodesic mapping results
        if CORE_MODULES_AVAILABLE:
            geodesic_result = self.geodesic_mapper.compute_density_enhancement(
                primes, n_bins=40, n_bootstrap=300
            )
            geodesic_enhancement = geodesic_result.get('enhancement_percent', 0) * 100
        else:
            geodesic_enhancement = self._local_geodesic_enhancement(primes, 0.3)
        
        # Random baseline strategies
        random_strategies = {
            'uniform_random': [],
            'weighted_random': [],
            'structured_random': [],
            'correlated_random': []
        }
        
        for trial in range(num_trials):
            # Strategy 1: Uniform random selection
            random_subset = np.random.choice(primes, size=len(primes)//3, replace=False)
            uniform_enhancement = self._compute_random_enhancement(random_subset, primes)
            random_strategies['uniform_random'].append(uniform_enhancement)
            
            # Strategy 2: Weighted random (prefer smaller primes)
            weights = 1.0 / np.array(primes)
            weighted_probs = weights / np.sum(weights)
            weighted_subset = np.random.choice(primes, size=len(primes)//3, 
                                             replace=False, p=weighted_probs)
            weighted_enhancement = self._compute_random_enhancement(weighted_subset, primes)
            random_strategies['weighted_random'].append(weighted_enhancement)
            
            # Strategy 3: Structured random (systematic sampling)
            step = len(primes) // (len(primes) // 3)
            start_idx = np.random.randint(0, step)
            structured_subset = primes[start_idx::step][:len(primes)//3]
            structured_enhancement = self._compute_random_enhancement(structured_subset, primes)
            random_strategies['structured_random'].append(structured_enhancement)
            
            # Strategy 4: Correlated random (mimic geodesic properties)
            correlated_values = np.random.normal(size=len(primes))
            correlated_indices = np.argsort(correlated_values)[:len(primes)//3]
            correlated_subset = [primes[i] for i in correlated_indices]
            correlated_enhancement = self._compute_random_enhancement(correlated_subset, primes)
            random_strategies['correlated_random'].append(correlated_enhancement)
        
        # Statistical comparison
        falsification_flags = []
        
        for strategy, enhancements in random_strategies.items():
            mean_random = np.mean(enhancements)
            std_random = np.std(enhancements)
            
            self.log(f"  {strategy}: {mean_random:.2f}% ± {std_random:.2f}%")
            
            # Check if random strategy performs as well as geodesic
            if mean_random + 2 * std_random > geodesic_enhancement:
                falsification_flags.append(f"{strategy} performs comparably (within 2σ)")
        
        # Overall random performance
        all_random = []
        for enhancements in random_strategies.values():
            all_random.extend(enhancements)
        
        overall_random_mean = np.mean(all_random)
        overall_random_std = np.std(all_random)
        
        # Statistical significance test
        z_score = (geodesic_enhancement - overall_random_mean) / overall_random_std
        
        if abs(z_score) < 2.0:  # Not statistically significant
            falsification_flags.append(f"No statistical significance vs random (z={z_score:.2f})")
        
        self.results['test_5'] = {
            'geodesic_enhancement': geodesic_enhancement,
            'random_strategies': {k: {'mean': np.mean(v), 'std': np.std(v)} 
                                for k, v in random_strategies.items()},
            'overall_random_mean': overall_random_mean,
            'overall_random_std': overall_random_std,
            'z_score': z_score,
            'falsification_flags': falsification_flags,
            'is_falsified': len(falsification_flags) > 0
        }
        
        self.log(f"Geodesic enhancement: {geodesic_enhancement:.2f}%")
        self.log(f"Overall random baseline: {overall_random_mean:.2f}% ± {overall_random_std:.2f}%")
        
        if falsification_flags:
            self.log(f"✗ FALSIFICATION DETECTED: {'; '.join(falsification_flags)}")
            return False
        else:
            self.log("✓ Geodesic mapping shows clear advantage over random selection")
            return True
    
    # Helper methods
    def _local_density_enhancement(self, prime_list, n_bins=50):
        """Local implementation of density enhancement calculation"""
        if len(prime_list) < 10:
            return 0, 0, 0
        
        # Simple geodesic transform
        transformed = [PHI * ((p % PHI) / PHI) ** 0.3 for p in prime_list]
        
        # Histogram analysis
        hist, _ = np.histogram(transformed, bins=n_bins)
        bin_densities = hist / len(transformed)
        
        mean_density = 1.0 / n_bins
        max_density = np.max(bin_densities)
        enhancement_pct = (max_density - mean_density) / mean_density * 100
        
        # Simple confidence interval (±2% assumed)
        return enhancement_pct, enhancement_pct - 2, enhancement_pct + 2
    
    def _compute_random_enhancement(self, subset, full_list):
        """Compute enhancement for random subset"""
        if len(subset) == 0 or len(full_list) == 0:
            return 0
        
        subset_density = len(subset) / len(full_list)
        expected_density = 0.25  # Assuming 25% selection rate
        
        if expected_density > 0:
            return (subset_density - expected_density) / expected_density * 100
        return 0
    
    def _local_geodesic_enhancement(self, prime_list, k):
        """Local implementation of geodesic enhancement for given k"""
        if len(prime_list) < 10:
            return 0
        
        transformed = [PHI * ((p % PHI) / PHI) ** k for p in prime_list]
        
        # Simple enhancement metric
        hist, _ = np.histogram(transformed, bins=30)
        bin_densities = hist / len(transformed)
        mean_density = 1.0 / 30
        max_density = np.max(bin_densities)
        
        return (max_density - mean_density) / mean_density * 100
    
    def _standard_sieve_of_eratosthenes(self, limit):
        """Standard Sieve of Eratosthenes implementation"""
        if limit < 2:
            return []
        
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, limit + 1, i):
                    sieve[j] = False
        
        return [i for i in range(2, limit + 1) if sieve[i]]
    
    def _enhanced_sieve_with_corridors(self, limit):
        """Enhanced sieve using modulo 30 corridors"""
        if limit < 2:
            return []
        
        # Start with special cases
        primes = []
        if limit >= 2: primes.append(2)
        if limit >= 3: primes.append(3) 
        if limit >= 5: primes.append(5)
        
        # Sieve only numbers in corridors mod 30
        candidates = []
        for i in range(7, limit + 1):
            if i % 30 in PRIME_CORRIDORS_MOD30:
                candidates.append(i)
        
        # Simple primality test for candidates (not full sieve optimization)
        for candidate in candidates:
            is_prime = True
            for p in primes:
                if p * p > candidate:
                    break
                if candidate % p == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(candidate)
        
        return sorted(primes)
    
    def run_all_falsification_tests(self):
        """Run complete falsification test suite"""
        self.log("Enhanced Sieve Algorithm Falsification Test Suite")
        self.log("=" * 60)
        self.log("")
        
        test_results = {}
        
        # Run all falsification tests
        self.log("Running falsification tests...")
        test_results['density_enhancement'] = self.test_1_prime_density_enhancement_falsification()
        test_results['sieve_acceleration'] = self.test_2_sieve_acceleration_falsification()
        test_results['optimal_k_parameter'] = self.test_3_optimal_k_parameter_falsification()
        test_results['prime_corridors'] = self.test_4_prime_corridors_mod30_falsification()
        test_results['geodesic_vs_random'] = self.test_5_geodesic_vs_random_falsification()
        
        # Summary analysis
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        self.log("")
        self.log("=" * 60)
        self.log("FALSIFICATION TEST SUMMARY")
        self.log("=" * 60)
        
        for test_name, passed in test_results.items():
            status = "SURVIVED" if passed else "FALSIFIED"
            self.log(f"{test_name}: {status}")
        
        self.log("")
        self.log(f"Overall: {passed_tests}/{total_tests} claims survived falsification attempts")
        
        # Determine overall conclusion
        if passed_tests == total_tests:
            conclusion = "✓ Enhanced Sieve Algorithm claims survive comprehensive falsification testing"
            overall_status = "ROBUST"
        elif passed_tests >= total_tests * 0.8:
            conclusion = "~ Enhanced Sieve Algorithm shows robustness with some concerns identified"
            overall_status = "PARTIALLY_ROBUST"
        elif passed_tests >= total_tests * 0.5:
            conclusion = "⚠ Enhanced Sieve Algorithm shows significant vulnerabilities"
            overall_status = "VULNERABLE"
        else:
            conclusion = "✗ Enhanced Sieve Algorithm claims are largely falsified"
            overall_status = "FALSIFIED"
        
        self.log("")
        self.log(conclusion)
        
        return {
            'overall_status': overall_status,
            'test_results': test_results,
            'detailed_results': self.results,
            'conclusion': conclusion,
            'passed_tests': passed_tests,
            'total_tests': total_tests
        }

def main():
    """Main function to run falsification tests and generate conclusions"""
    print("Enhanced Sieve Algorithm Falsification Analysis")
    print("=" * 55)
    print("")
    print("Systematically testing Z Framework Enhanced Sieve Algorithm claims:")
    print("- conditional prime density improvement under canonical benchmark methodology")  
    print("- 20% sieve acceleration")
    print("- Optimal k* ≈ 0.3 parameter")
    print("- Prime corridors modulo 30 effectiveness")
    print("- Geodesic mapping superiority")
    print("")
    
    # Initialize and run falsification suite
    falsification_suite = EnhancedSieveFalsificationSuite(seed=42)
    
    # Run complete test suite
    results = falsification_suite.run_all_falsification_tests()
    
    # Save detailed results
    import json
    with open('enhanced_sieve_falsification_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: enhanced_sieve_falsification_results.json")
    print("Falsification analysis complete.")
    
    return results

if __name__ == "__main__":
    results = main()