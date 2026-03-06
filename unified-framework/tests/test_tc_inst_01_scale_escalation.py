"""
TC-INST-01: Scale Escalation Test Implementation

This module implements the specific test case TC-INST-01 from the issue specification:
"Validate enhancement at increasing N with baseline precision."

Test Case Specification:
- ID: TC-INST-01
- Description: Scale Escalation
- Preconditions: Primes up to N=10^{10}; dps=50
- Steps: 
  1. Compute θ'(n,k) for primes with dynamic k = 0.3 · (π / ln(n̄))
  2. Bin (B=20), calculate enhancement  
  3. Bootstrap CI
- Expected Results: Enhancement ≈15% (CI [14.6,15.4]); deviation <10^{-6}

Key Mathematical Requirements:
- θ'(n, k) = φ · {n/φ}^k with k = 0.3 · (π / ln(n̄))  
- Density enhancement: (max_i ρ_i - 1) × 100%, ρ_i = (h_{p,i} / h_{n,i}) / (π(N)/N)
- Weyl bounds: D_N ≤ (1/N) + ∑_{h=1}^H (1/h) | (1/N) ∑ e^{2π i h {n / φ}} | + 1/H
- Precision: Δ_n / Δ_max < 10^{-6}
"""

import numpy as np
import mpmath as mp
from scipy import stats
from sklearn.mixture import GaussianMixture
from sympy import sieve, isprime, primefactors
import warnings
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.axioms import theta_prime, universal_invariance
from core.domain import DiscreteZetaShift

# Set high precision as per specification
mp.mp.dps = 50
warnings.filterwarnings("ignore")

# Mathematical constants with high precision
PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)
PI = mp.pi

@dataclass
class TC_INST_01_Config:
    """Configuration for TC-INST-01 test case."""
    # Scale escalation parameters
    N_values: List[int] = None
    # Precision requirements
    precision_dps: int = 50
    precision_threshold: float = 1e-6
    # Enhancement targets from issue
    target_enhancement: float = 15.0
    target_ci_lower: float = 14.6
    target_ci_upper: float = 15.4
    # Binning parameters
    bins: int = 20
    # Bootstrap parameters
    bootstrap_samples: int = 1000
    confidence_level: float = 0.95
    # Dynamic k computation factor
    k_factor: float = 0.3
    
    def __post_init__(self):
        if self.N_values is None:
            # Start with manageable sizes for testing, can scale up
            self.N_values = [1000, 5000, 10000, 50000, 100000]

class PrimeDensityAnalyzer:
    """Analyzes prime density enhancement using the Z-model framework."""
    
    def __init__(self, config: TC_INST_01_Config):
        self.config = config
        # Ensure high precision is set
        mp.mp.dps = config.precision_dps
    
    def compute_dynamic_k(self, primes: np.ndarray) -> float:
        """
        Compute dynamic k = 0.3 · (π / ln(n̄)) where n̄ is mean of primes.
        
        Args:
            primes: Array of prime numbers
            
        Returns:
            Dynamic curvature parameter k
        """
        if len(primes) == 0:
            return self.config.k_factor
        
        n_mean = float(np.mean(primes))
        if n_mean <= 1:
            return self.config.k_factor
        
        # Use high precision computation
        n_mean_mp = mp.mpf(n_mean)
        ln_n_mean = mp.log(n_mean_mp)
        k_dynamic = self.config.k_factor * float(PI / ln_n_mean)
        
        return k_dynamic
    
    def compute_theta_prime_array(self, n_values: np.ndarray, k: float) -> np.ndarray:
        """
        Compute θ'(n,k) = φ · {n/φ}^k for array of values.
        
        Uses high-precision arithmetic to minimize numerical errors.
        """
        phi = float(PHI)
        
        # Use vectorized computation for efficiency while maintaining precision
        result = []
        for n in n_values:
            # High precision computation for each value
            theta_val = float(theta_prime(n, k, phi=PHI))
            result.append(theta_val)
        
        return np.array(result)
    
    def validate_precision(self, theta_values: np.ndarray, n_values: np.ndarray, k: float) -> Tuple[float, bool]:
        """
        Validate numerical precision meets Δ_n < 10^{-6} requirement.
        
        Returns:
            (max_deviation, precision_ok): Maximum precision deviation and validation status
        """
        # Sample subset for precision validation (computational efficiency)
        sample_size = min(100, len(n_values))
        indices = np.random.choice(len(n_values), sample_size, replace=False)
        
        max_deviation = 0.0
        
        for i in indices:
            n = n_values[i]
            
            # Compute with different precision levels
            with mp.workdps(25):  # Lower precision
                theta_low = float(theta_prime(n, k))
            
            with mp.workdps(100):  # Higher precision  
                theta_high = float(theta_prime(n, k))
            
            # Check deviation
            deviation = abs(theta_values[i] - theta_high)
            max_deviation = max(max_deviation, deviation)
        
        precision_ok = max_deviation < self.config.precision_threshold
        return max_deviation, precision_ok
    
    def compute_density_enhancement(self, theta_all: np.ndarray, theta_primes: np.ndarray, 
                                  N: int, num_primes: int) -> Tuple[np.ndarray, float]:
        """
        Compute density enhancement using specification formula:
        ρ_i = (h_{p,i} / h_{n,i}) / (π(N)/N)
        Enhancement = (max_i ρ_i - 1) × 100%
        """
        phi = float(PHI)
        bins = np.linspace(0, phi, self.config.bins + 1)
        
        # Compute histogram counts
        h_n, _ = np.histogram(theta_all, bins=bins)  # All integers histogram
        h_p, _ = np.histogram(theta_primes, bins=bins)  # Primes histogram
        
        # Avoid division by zero
        h_n = np.maximum(h_n, 1)
        
        # Prime density in the full range
        pi_N_over_N = num_primes / N
        
        # Compute density ratios ρ_i = (h_{p,i} / h_{n,i}) / (π(N)/N)
        rho_i = (h_p / h_n) / pi_N_over_N
        
        # Enhancement = (max_i ρ_i - 1) × 100%
        max_rho = np.max(rho_i)
        enhancement = (max_rho - 1) * 100
        
        return rho_i, enhancement
    
    def bootstrap_confidence_interval(self, theta_primes: np.ndarray, theta_all: np.ndarray,
                                    N: int, num_primes: int) -> Tuple[float, float]:
        """
        Compute bootstrap confidence interval for enhancement.
        
        Resamples prime data and recomputes enhancement to estimate uncertainty.
        """
        enhancements = []
        n_samples = len(theta_primes)
        
        for _ in range(self.config.bootstrap_samples):
            # Bootstrap resample of primes
            bootstrap_indices = np.random.choice(n_samples, n_samples, replace=True)
            theta_primes_bootstrap = theta_primes[bootstrap_indices]
            
            # Compute enhancement for bootstrap sample
            _, enhancement = self.compute_density_enhancement(
                theta_all, theta_primes_bootstrap, N, num_primes)
            enhancements.append(enhancement)
        
        # Compute confidence interval
        alpha = 1 - self.config.confidence_level
        ci_lower = np.percentile(enhancements, (alpha/2) * 100)
        ci_upper = np.percentile(enhancements, (1 - alpha/2) * 100)
        
        return ci_lower, ci_upper
    
    def validate_weyl_discrepancy(self, primes: np.ndarray, k: float) -> float:
        """
        Compute Weyl discrepancy bound for equidistribution validation.
        D_N ≤ (1/N) + ∑_{h=1}^H (1/h) | (1/N) ∑ e^{2π i h {n / φ}} | + 1/H
        """
        N = len(primes)
        if N == 0:
            return float('inf')
        
        phi = float(PHI)
        H = min(50, N)  # Practical limit for H
        
        # First term: 1/N
        first_term = 1.0 / N
        
        # Second term: ∑_{h=1}^H (1/h) | (1/N) ∑ e^{2π i h {n / φ}} |
        second_term = 0.0
        for h in range(1, H + 1):
            exponential_sum = 0.0 + 0.0j
            for n in primes:
                fractional_part = (n % phi) / phi
                phase = 2 * np.pi * h * fractional_part
                exponential_sum += np.exp(1j * phase)
            
            exponential_sum /= N
            magnitude = abs(exponential_sum)
            second_term += magnitude / h
        
        # Third term: 1/H
        third_term = 1.0 / H
        
        discrepancy = first_term + second_term + third_term
        return discrepancy
    
    def run_single_validation(self, N: int) -> Dict:
        """
        Run TC-INST-01 validation for a single N value.
        
        Steps:
        1. Generate primes up to N
        2. Compute dynamic k = 0.3 · (π / ln(n̄))  
        3. Compute θ'(n,k) for all integers and primes
        4. Validate precision (Δ_n < 10^{-6})
        5. Compute density enhancement
        6. Bootstrap confidence interval
        7. Validate against expected results
        """
        start_time = time.time()
        
        # Step 1: Generate sequences
        print(f"  Generating primes up to N={N:,}...")
        primes_list = list(sieve.primerange(2, N + 1))
        primes = np.array(primes_list)
        num_primes = len(primes)
        
        if num_primes < 10:
            raise ValueError(f"Insufficient primes for N={N}")
        
        all_integers = np.arange(2, N + 1)
        
        # Step 2: Compute dynamic k
        k_dynamic = self.compute_dynamic_k(primes)
        print(f"  Dynamic k = {k_dynamic:.4f}")
        
        # Step 3: Compute transformations  
        print(f"  Computing θ'(n,k) transformations...")
        theta_all = self.compute_theta_prime_array(all_integers, k_dynamic)
        theta_primes = self.compute_theta_prime_array(primes, k_dynamic)
        
        # Step 4: Validate precision
        max_deviation, precision_ok = self.validate_precision(theta_primes, primes, k_dynamic)
        
        # Step 5: Compute density enhancement
        print(f"  Computing density enhancement...")
        rho_i, enhancement = self.compute_density_enhancement(
            theta_all, theta_primes, N, num_primes)
        
        # Step 6: Bootstrap confidence interval
        print(f"  Computing bootstrap confidence interval...")
        ci_lower, ci_upper = self.bootstrap_confidence_interval(
            theta_primes, theta_all, N, num_primes)
        
        # Step 7: Weyl discrepancy
        weyl_discrepancy = self.validate_weyl_discrepancy(primes, k_dynamic)
        
        # Validation against expected results
        enhancement_in_target = (self.config.target_ci_lower <= enhancement <= self.config.target_ci_upper)
        ci_overlaps_target = not (ci_upper < self.config.target_ci_lower or 
                                ci_lower > self.config.target_ci_upper)
        precision_satisfied = precision_ok
        
        validation_passed = enhancement_in_target and ci_overlaps_target and precision_satisfied
        
        computation_time = time.time() - start_time
        
        result = {
            'N': N,
            'num_primes': num_primes,
            'prime_ratio': num_primes / N,
            'k_dynamic': k_dynamic,
            'enhancement': enhancement,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'max_precision_deviation': max_deviation,
            'precision_ok': precision_ok,
            'weyl_discrepancy': weyl_discrepancy,
            'enhancement_in_target': enhancement_in_target,
            'ci_overlaps_target': ci_overlaps_target,
            'validation_passed': validation_passed,
            'computation_time': computation_time,
            'density_ratios': rho_i.tolist()
        }
        
        return result

class TC_INST_01_TestRunner:
    """Test runner for TC-INST-01: Scale Escalation."""
    
    def __init__(self, config: TC_INST_01_Config = None):
        if config is None:
            config = TC_INST_01_Config()
        self.config = config
        self.analyzer = PrimeDensityAnalyzer(config)
    
    def run_test_case(self) -> Dict:
        """
        Execute TC-INST-01: Scale Escalation test case.
        
        Returns comprehensive results including validation status for each N.
        """
        print("=" * 60)
        print("TC-INST-01: Scale Escalation Test")  
        print("=" * 60)
        print(f"Target Enhancement: {self.config.target_enhancement}%")
        print(f"Target CI: [{self.config.target_ci_lower}%, {self.config.target_ci_upper}%]")
        print(f"Precision Threshold: {self.config.precision_threshold}")
        print(f"High Precision DPS: {self.config.precision_dps}")
        print()
        
        results = []
        
        for N in self.config.N_values:
            print(f"Running validation for N={N:,}")
            
            try:
                result = self.analyzer.run_single_validation(N)
                results.append(result)
                
                # Print summary
                print(f"  Enhancement: {result['enhancement']:.1f}%")
                print(f"  CI: [{result['ci_lower']:.1f}%, {result['ci_upper']:.1f}%]")
                print(f"  Precision deviation: {result['max_precision_deviation']:.2e}")
                print(f"  Weyl discrepancy: {result['weyl_discrepancy']:.4f}")
                print(f"  Validation passed: {result['validation_passed']}")
                print(f"  Computation time: {result['computation_time']:.2f}s")
                print()
                
            except Exception as e:
                print(f"  ERROR: {e}")
                print()
                continue
        
        # Summary analysis
        test_summary = self.generate_test_summary(results)
        
        return {
            'test_case_id': 'TC-INST-01',
            'description': 'Scale Escalation',
            'config': self.config,
            'individual_results': results,
            'test_summary': test_summary
        }
    
    def generate_test_summary(self, results: List[Dict]) -> Dict:
        """Generate summary analysis of test results."""
        if not results:
            return {'status': 'FAILED', 'reason': 'No valid results'}
        
        # Validation statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['validation_passed'])
        pass_rate = passed_tests / total_tests
        
        # Enhancement statistics
        enhancements = [r['enhancement'] for r in results]
        avg_enhancement = np.mean(enhancements)
        std_enhancement = np.std(enhancements)
        
        # Precision statistics
        max_deviations = [r['max_precision_deviation'] for r in results]
        max_overall_deviation = max(max_deviations)
        
        # Overall test status
        overall_pass = pass_rate >= 0.8  # At least 80% of tests should pass
        precision_pass = max_overall_deviation < self.config.precision_threshold
        
        test_status = 'PASSED' if (overall_pass and precision_pass) else 'FAILED'
        
        summary = {
            'status': test_status,
            'pass_rate': pass_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'avg_enhancement': avg_enhancement,
            'std_enhancement': std_enhancement,
            'max_precision_deviation': max_overall_deviation,
            'precision_requirement_met': precision_pass,
            'target_enhancement': self.config.target_enhancement,
            'target_ci_range': [self.config.target_ci_lower, self.config.target_ci_upper]
        }
        
        return summary
    
    def print_detailed_report(self, test_results: Dict):
        """Print detailed test report."""
        print("\n" + "=" * 80)
        print("TC-INST-01: DETAILED TEST REPORT")
        print("=" * 80)
        
        summary = test_results['test_summary']
        print(f"Overall Status: {summary['status']}")
        print(f"Pass Rate: {summary['pass_rate']:.1%} ({summary['passed_tests']}/{summary['total_tests']})")
        print(f"Average Enhancement: {summary['avg_enhancement']:.1f}% (±{summary['std_enhancement']:.1f}%)")
        print(f"Max Precision Deviation: {summary['max_precision_deviation']:.2e}")
        print(f"Precision Requirement Met: {summary['precision_requirement_met']}")
        print()
        
        print("Individual Test Results:")
        print("-" * 80)
        print("N\t\tk_dyn\tEnh%\tCI_Low\tCI_High\tPrec_Dev\tValid")
        print("-" * 80)
        
        for result in test_results['individual_results']:
            print(f"{result['N']:,}\t{result['k_dynamic']:.3f}\t{result['enhancement']:.1f}\t"
                  f"{result['ci_lower']:.1f}\t{result['ci_upper']:.1f}\t"
                  f"{result['max_precision_deviation']:.1e}\t{result['validation_passed']}")
        
        print("\n" + "=" * 80)

def main():
    """Main execution function for TC-INST-01."""
    # Configure test with manageable N values for initial validation
    config = TC_INST_01_Config(
        N_values=[1000, 2000, 5000, 10000],  # Start small, can scale up
        precision_threshold=1e-6,
        target_enhancement=15.0,
        target_ci_lower=14.6,
        target_ci_upper=15.4,
        bootstrap_samples=500,  # Reduce for faster testing
        bins=20
    )
    
    # Run test case
    runner = TC_INST_01_TestRunner(config)
    test_results = runner.run_test_case()
    
    # Print detailed report
    runner.print_detailed_report(test_results)
    
    return test_results

if __name__ == "__main__":
    results = main()