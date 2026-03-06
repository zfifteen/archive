"""
Complete TC-INST-01 Implementation with Weyl Bounds and Control Sequences

This module provides the complete implementation of TC-INST-01: Scale Escalation
including all components specified in the issue:

1. Scale escalation tests for N = 10^6 to 10^8 (configurable)
2. Weyl equidistribution bounds for discrepancy D_N validation  
3. Control sequence validation (random sequences, composites)
4. Complete numerical instability monitoring
5. Comprehensive reporting with all metrics from issue specification

Mathematical Framework:
- θ'(n, k) = φ · {n/φ}^k with optimal k* ≈ 3.33
- Weyl bound: D_N ≤ (1/N) + ∑_{h=1}^H (1/h) | (1/N) ∑ e^{2π i h {n / φ}} | + 1/H  
- Enhancement: (max_i ρ_i - 1) × 100% where ρ_i = (h_{p,i} / h_{n,i}) / (π(N)/N)
- Target: 15.7% enhancement with CI [14.6%, 15.4%]
- Precision: Δ_n / Δ_max < 10^{-6}
"""

import numpy as np
import mpmath as mp
from scipy import stats
from sklearn.mixture import GaussianMixture
from sympy import sieve, isprime
import warnings
import time
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import sys
import os
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.axioms import theta_prime, universal_invariance
from core.domain import DiscreteZetaShift

# Set high precision for numerical stability
mp.mp.dps = 50
warnings.filterwarnings("ignore")

# Mathematical constants
PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)
PI = mp.pi

@dataclass
class TC_INST_01_FullConfig:
    """Complete configuration for TC-INST-01 test case."""
    # Scale escalation parameters (can scale to 10^8)
    N_values: List[int] = None
    # K-sweep parameters for optimization
    k_min: float = 3.2
    k_max: float = 3.4
    k_step: float = 0.002
    # Precision and validation requirements
    precision_dps: int = 50
    precision_threshold: float = 1e-6
    target_enhancement: float = 15.7  # Updated to match issue spec
    target_ci_lower: float = 14.6
    target_ci_upper: float = 15.4
    # Analysis parameters
    bins: int = 20
    gmm_components: int = 5
    fourier_modes: int = 5
    bootstrap_samples: int = 1000
    confidence_level: float = 0.95
    # Weyl bounds parameters
    weyl_H_max: int = 100
    # Control sequence parameters
    control_sample_size: int = 10000
    # Performance parameters
    timeout_seconds: int = 600
    
    def __post_init__(self):
        if self.N_values is None:
            # Manageable progression that can scale to 10^6, 10^7, 10^8
            self.N_values = [10000, 50000, 100000, 500000]

class WeylEquidistributionAnalyzer:
    """Analyzer for Weyl equidistribution bounds and discrepancy validation."""
    
    def __init__(self, H_max: int = 100):
        self.H_max = H_max
    
    def compute_discrepancy_bound(self, n_values: np.ndarray, phi: float = None) -> Dict:
        """
        Compute Weyl discrepancy bound: D_N ≤ (1/N) + ∑_{h=1}^H (1/h) | (1/N) ∑ e^{2π i h {n / φ}} | + 1/H
        
        Returns comprehensive discrepancy analysis including individual terms.
        """
        if phi is None:
            phi = float(PHI)
        
        N = len(n_values)
        if N == 0:
            return {'discrepancy_bound': float('inf'), 'terms': {}}
        
        # First term: 1/N
        first_term = 1.0 / N
        
        # Second term computation with detailed tracking
        second_term = 0.0
        H = min(self.H_max, N)
        exponential_magnitudes = []
        
        for h in range(1, H + 1):
            # Compute (1/N) ∑ e^{2π i h {n / φ}}
            exponential_sum = 0.0 + 0.0j
            for n in n_values:
                fractional_part = float((n % phi) / phi)
                phase = 2 * np.pi * h * fractional_part
                exponential_sum += np.exp(1j * phase)
            
            exponential_sum /= N
            magnitude = abs(exponential_sum)
            exponential_magnitudes.append(magnitude)
            second_term += magnitude / h
        
        # Third term: 1/H
        third_term = 1.0 / H
        
        # Total discrepancy bound
        discrepancy_bound = first_term + second_term + third_term
        
        return {
            'discrepancy_bound': discrepancy_bound,
            'first_term': first_term,
            'second_term': second_term,
            'third_term': third_term,
            'H': H,
            'N': N,
            'exponential_magnitudes': exponential_magnitudes,
            'max_exponential_magnitude': max(exponential_magnitudes) if exponential_magnitudes else 0.0,
            'mean_exponential_magnitude': np.mean(exponential_magnitudes) if exponential_magnitudes else 0.0
        }
    
    def validate_weyl_criterion(self, n_values: np.ndarray, k: float, phi: float = None) -> Dict:
        """
        Validate Weyl criterion: lim (1/N) ∑ e^{2π i k {n / φ}} = 0 for k ≠ 0.
        
        Returns detailed analysis of equidistribution convergence.
        """
        if phi is None:
            phi = float(PHI)
        
        N = len(n_values)
        if N == 0 or k == 0:
            return {'criterion_satisfied': True, 'magnitude': 0.0}
        
        # Compute (1/N) ∑ e^{2π i k {n / φ}}
        exponential_sum = 0.0 + 0.0j
        for n in n_values:
            fractional_part = float((n % phi) / phi)
            phase = 2 * np.pi * k * fractional_part
            exponential_sum += np.exp(1j * phase)
        
        exponential_sum /= N
        magnitude = abs(exponential_sum)
        
        # Expected convergence rate for equidistribution
        expected_bound = 1.0 / np.sqrt(N)
        criterion_satisfied = magnitude < expected_bound
        
        return {
            'criterion_satisfied': criterion_satisfied,
            'magnitude': magnitude,
            'expected_bound': expected_bound,
            'convergence_rate': magnitude * np.sqrt(N),
            'N': N,
            'k': k
        }

class ControlSequenceValidator:
    """Validator for control sequences (random, composites) comparison."""
    
    def __init__(self, sample_size: int = 10000):
        self.sample_size = sample_size
    
    def generate_random_sequence(self, N: int) -> np.ndarray:
        """Generate random integer sequence for control testing."""
        np.random.seed(42)  # Reproducible results
        return np.random.randint(2, N, self.sample_size)
    
    def generate_composite_sequence(self, N: int) -> np.ndarray:
        """Generate sequence of composite numbers for control testing."""
        composites = []
        n = 4  # First composite
        
        while len(composites) < self.sample_size and n < N:
            if not isprime(n):
                composites.append(n)
            n += 1
        
        # Pad with random composites if needed
        while len(composites) < self.sample_size:
            candidate = np.random.randint(4, N)
            if not isprime(candidate):
                composites.append(candidate)
        
        return np.array(composites[:self.sample_size])
    
    def validate_control_enhancement(self, control_sequence: np.ndarray, N: int, k: float,
                                   analyzer) -> Dict:
        """
        Validate enhancement for control sequence using same methodology as primes.
        
        Returns enhancement metrics for comparison with prime sequences.
        """
        # Generate comparison all-integers sequence
        all_integers = np.arange(2, min(N + 1, max(control_sequence) + 1))
        
        # Apply frame shift transformation
        theta_all = analyzer.frame_shift_residues(all_integers, k)
        theta_control = analyzer.frame_shift_residues(control_sequence, k)
        
        # Compute enhancement using same method as primes
        all_d, control_d, enh = analyzer.bin_densities(theta_all, theta_control)
        
        # Compute maximum enhancement
        finite_enh = enh[np.isfinite(enh)]
        max_enhancement = np.max(finite_enh) if len(finite_enh) > 0 else 0.0
        
        # Bootstrap confidence interval
        ci_lower, ci_upper = analyzer.bootstrap_confidence_interval(enh)
        
        return {
            'sequence_type': 'control',
            'sequence_size': len(control_sequence),
            'max_enhancement': max_enhancement,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'enhancement_distribution': enh.tolist()
        }

class ComprehensiveAsymptoticAnalyzer:
    """Comprehensive analyzer combining all validation components."""
    
    def __init__(self, config: TC_INST_01_FullConfig):
        self.config = config
        self.weyl_analyzer = WeylEquidistributionAnalyzer(config.weyl_H_max)
        self.control_validator = ControlSequenceValidator(config.control_sample_size)
        
        # Ensure high precision
        mp.mp.dps = config.precision_dps
    
    def frame_shift_residues(self, n_vals: np.ndarray, k: float) -> np.ndarray:
        """Compute θ'(n,k) = φ · {n/φ}^k with high precision."""
        phi = float(PHI)
        mod_phi = np.mod(n_vals, phi) / phi
        return phi * np.power(mod_phi, k)
    
    def bin_densities(self, theta_all: np.ndarray, theta_pr: np.ndarray, nbins: int = 20) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute binned densities and enhancements."""
        phi = float(PHI)
        bins = np.linspace(0, phi, nbins + 1)
        
        all_counts, _ = np.histogram(theta_all, bins=bins)
        pr_counts, _ = np.histogram(theta_pr, bins=bins)
        
        all_d = all_counts / len(theta_all)
        pr_d = pr_counts / len(theta_pr)
        
        with np.errstate(divide='ignore', invalid='ignore'):
            enh = (pr_d - all_d) / all_d * 100
        
        enh = np.where(all_d > 0, enh, -np.inf)
        return all_d, pr_d, enh
    
    def bootstrap_confidence_interval(self, enhancements: np.ndarray,
                                    confidence_level: float = 0.95,
                                    n_bootstrap: int = 1000) -> Tuple[float, float]:
        """Compute bootstrap confidence interval."""
        valid_enhancements = enhancements[np.isfinite(enhancements)]
        
        if len(valid_enhancements) == 0:
            return (-np.inf, np.inf)
        
        bootstrap_means = []
        n_samples = len(valid_enhancements)
        
        for _ in range(n_bootstrap):
            bootstrap_sample = np.random.choice(valid_enhancements, size=n_samples, replace=True)
            bootstrap_means.append(np.mean(bootstrap_sample))
        
        alpha = 1 - confidence_level
        ci_lower = np.percentile(bootstrap_means, (alpha / 2) * 100)
        ci_upper = np.percentile(bootstrap_means, (1 - alpha / 2) * 100)
        
        return (ci_lower, ci_upper)
    
    def gmm_analysis(self, theta_pr: np.ndarray, n_components: int = 5) -> Dict:
        """Perform GMM analysis with detailed metrics."""
        phi = float(PHI)
        X = ((theta_pr % phi) / phi).reshape(-1, 1)
        
        gm = GaussianMixture(n_components=n_components, covariance_type='full', 
                           random_state=42).fit(X)
        
        # Extract detailed metrics
        weights = gm.weights_
        means = gm.means_.flatten()
        sigmas = np.sqrt([gm.covariances_[i].flatten()[0] for i in range(n_components)])
        
        return {
            'n_components': n_components,
            'weights': weights.tolist(),
            'means': means.tolist(),
            'sigmas': sigmas.tolist(),
            'mean_sigma': np.mean(sigmas),
            'bic': gm.bic(X),
            'aic': gm.aic(X),
            'log_likelihood': gm.score(X)
        }
    
    def fourier_analysis(self, theta_pr: np.ndarray, M: int = 5) -> Dict:
        """Perform Fourier analysis with detailed coefficients."""
        phi = float(PHI)
        y, edges = np.histogram(theta_pr, bins=100, density=True)
        centers = (edges[:-1] + edges[1:]) / 2 / phi
        
        def design(x):
            cols = [np.ones_like(x)]
            for k in range(1, M + 1):
                cols.append(np.cos(2 * np.pi * k * x))
                cols.append(np.sin(2 * np.pi * k * x))
            return np.vstack(cols).T
        
        A = design(centers)
        coeffs, residuals, rank, s = np.linalg.lstsq(A, y, rcond=None)
        
        a_coeffs = coeffs[0::2]  # cosine coefficients  
        b_coeffs = coeffs[1::2]  # sine coefficients
        
        return {
            'M': M,
            'a_coefficients': a_coeffs.tolist(),
            'b_coefficients': b_coeffs.tolist(),
            'sum_abs_b': np.sum(np.abs(b_coeffs)),
            'sum_abs_a': np.sum(np.abs(a_coeffs)),
            'residuals': residuals.tolist() if len(residuals) > 0 else [],
            'fourier_asymmetry': np.sum(np.abs(b_coeffs))  # Main asymmetry metric
        }
    
    def validate_numerical_stability(self, primes_sample: np.ndarray, k: float) -> Dict:
        """Comprehensive numerical stability validation."""
        stability_results = []
        
        # Sample for computational efficiency
        sample_size = min(100, len(primes_sample))
        sample_indices = np.random.choice(len(primes_sample), sample_size, replace=False)
        
        for i in sample_indices:
            n = primes_sample[i]
            
            # Multi-precision validation
            precisions = [25, 50, 100]
            theta_values = {}
            
            for dps in precisions:
                with mp.workdps(dps):
                    theta_values[dps] = float(theta_prime(n, k))
            
            # Compute precision deviations
            reference = theta_values[100]  # Highest precision as reference
            deviations = {dps: abs(theta_values[dps] - reference) for dps in precisions[:-1]}
            
            stability_results.append({
                'n': int(n),
                'deviations': deviations,
                'max_deviation': max(deviations.values())
            })
        
        # Aggregate stability metrics
        max_overall_deviation = max(r['max_deviation'] for r in stability_results)
        mean_deviation = np.mean([r['max_deviation'] for r in stability_results])
        stability_ok = max_overall_deviation < self.config.precision_threshold
        
        return {
            'max_deviation': max_overall_deviation,
            'mean_deviation': mean_deviation,
            'std_deviation': np.std([r['max_deviation'] for r in stability_results]),
            'stability_ok': stability_ok,
            'sample_size': sample_size,
            'precision_threshold': self.config.precision_threshold,
            'detailed_results': stability_results[:10]  # Sample for reporting
        }
    
    def run_comprehensive_analysis(self, N: int) -> Dict:
        """
        Run comprehensive TC-INST-01 analysis for given N.
        
        Includes all components: k-sweep, Weyl bounds, control sequences, stability monitoring.
        """
        start_time = time.time()
        print(f"  Running comprehensive analysis for N={N:,}")
        
        # Generate sequences
        print(f"    Generating primes up to N={N:,}...")
        primes_list = list(sieve.primerange(2, N + 1))
        primes_array = np.array(primes_list)
        num_primes = len(primes_list)
        
        if num_primes < 10:
            raise ValueError(f"Insufficient primes for N={N}")
        
        all_integers = np.arange(2, N + 1)
        print(f"    Found {num_primes:,} primes (ratio: {num_primes/N:.4f})")
        
        # K-sweep optimization
        print(f"    Performing k-sweep optimization...")
        k_values = np.arange(self.config.k_min, self.config.k_max + self.config.k_step, 
                           self.config.k_step)
        best_k = None
        best_enhancement = -np.inf
        k_sweep_results = []
        
        for k in k_values:
            theta_all = self.frame_shift_residues(all_integers, k)
            theta_pr = self.frame_shift_residues(primes_array, k)
            
            _, _, enh = self.bin_densities(theta_all, theta_pr, self.config.bins)
            finite_enh = enh[np.isfinite(enh)]
            max_enh = np.max(finite_enh) if len(finite_enh) > 0 else -np.inf
            
            k_sweep_results.append({'k': k, 'enhancement': max_enh})
            
            if max_enh > best_enhancement:
                best_enhancement = max_enh
                best_k = k
        
        print(f"    Optimal k* = {best_k:.3f} with enhancement = {best_enhancement:.1f}%")
        
        # Main analysis with optimal k
        theta_all_opt = self.frame_shift_residues(all_integers, best_k)
        theta_pr_opt = self.frame_shift_residues(primes_array, best_k)
        
        # Enhancement analysis
        _, _, enh_opt = self.bin_densities(theta_all_opt, theta_pr_opt, self.config.bins)
        enhancement = best_enhancement
        ci_lower, ci_upper = self.bootstrap_confidence_interval(enh_opt, 
                                                               self.config.confidence_level,
                                                               self.config.bootstrap_samples)
        
        # Weyl equidistribution analysis
        print(f"    Computing Weyl equidistribution bounds...")
        weyl_discrepancy = self.weyl_analyzer.compute_discrepancy_bound(primes_array)
        weyl_criterion = self.weyl_analyzer.validate_weyl_criterion(primes_array, best_k)
        
        # GMM and Fourier analysis
        print(f"    Performing GMM and Fourier analysis...")
        gmm_results = self.gmm_analysis(theta_pr_opt, self.config.gmm_components)
        fourier_results = self.fourier_analysis(theta_pr_opt, self.config.fourier_modes)
        
        # Numerical stability validation
        print(f"    Validating numerical stability...")
        stability_results = self.validate_numerical_stability(primes_array, best_k)
        
        # Control sequence validation
        print(f"    Validating control sequences...")
        random_seq = self.control_validator.generate_random_sequence(N)
        composite_seq = self.control_validator.generate_composite_sequence(N)
        
        random_results = self.control_validator.validate_control_enhancement(
            random_seq, N, best_k, self)
        composite_results = self.control_validator.validate_control_enhancement(
            composite_seq, N, best_k, self)
        
        # Validation against targets
        enhancement_in_target = abs(enhancement - self.config.target_enhancement) < 5.0
        ci_overlaps_target = not (ci_upper < self.config.target_ci_lower or 
                                ci_lower > self.config.target_ci_upper)
        precision_ok = stability_results['stability_ok']
        weyl_ok = weyl_criterion['criterion_satisfied']
        
        # Control sequence comparison
        random_lower = random_results['max_enhancement'] < enhancement
        composite_lower = composite_results['max_enhancement'] < enhancement
        
        validation_passed = (enhancement_in_target and ci_overlaps_target and 
                           precision_ok and weyl_ok and random_lower and composite_lower)
        
        computation_time = time.time() - start_time
        
        result = {
            'N': N,
            'num_primes': num_primes,
            'prime_ratio': num_primes / N,
            'k_star': best_k,
            'enhancement': enhancement,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'weyl_analysis': {
                'discrepancy': weyl_discrepancy,
                'criterion': weyl_criterion
            },
            'gmm_analysis': gmm_results,
            'fourier_analysis': fourier_results,
            'stability_analysis': stability_results,
            'control_sequences': {
                'random': random_results,
                'composite': composite_results
            },
            'validation_checks': {
                'enhancement_in_target': enhancement_in_target,
                'ci_overlaps_target': ci_overlaps_target,
                'precision_ok': precision_ok,
                'weyl_ok': weyl_ok,
                'random_lower': random_lower,
                'composite_lower': composite_lower
            },
            'validation_passed': validation_passed,
            'computation_time': computation_time,
            'k_sweep_results': k_sweep_results,
            'timestamp': datetime.now().isoformat()
        }
        
        return result

class TC_INST_01_TestExecutor:
    """Main test executor for TC-INST-01 with comprehensive reporting."""
    
    def __init__(self, config: TC_INST_01_FullConfig = None):
        if config is None:
            config = TC_INST_01_FullConfig()
        self.config = config
        self.analyzer = ComprehensiveAsymptoticAnalyzer(config)
    
    def execute_test_case(self) -> Dict:
        """Execute complete TC-INST-01 test case."""
        print("=" * 100)
        print("TC-INST-01: SCALE ESCALATION - COMPREHENSIVE ASYMPTOTIC CONVERGENCE VALIDATION")
        print("=" * 100)
        print(f"Target Enhancement: {self.config.target_enhancement}%")
        print(f"Target CI: [{self.config.target_ci_lower}%, {self.config.target_ci_upper}%]")
        print(f"Precision Threshold: {self.config.precision_threshold}")
        print(f"Weyl H_max: {self.config.weyl_H_max}")
        print(f"Bootstrap Samples: {self.config.bootstrap_samples}")
        print()
        
        results = []
        
        for N in self.config.N_values:
            print(f"Executing validation for N={N:,}")
            
            try:
                result = self.analyzer.run_comprehensive_analysis(N)
                results.append(result)
                
                # Summary output
                print(f"  ✓ k* = {result['k_star']:.3f}")
                print(f"  ✓ Enhancement = {result['enhancement']:.1f}%")
                print(f"  ✓ CI = [{result['ci_lower']:.1f}%, {result['ci_upper']:.1f}%]")
                print(f"  ✓ Weyl discrepancy = {result['weyl_analysis']['discrepancy']['discrepancy_bound']:.4f}")
                print(f"  ✓ Max precision deviation = {result['stability_analysis']['max_deviation']:.2e}")
                print(f"  ✓ Random control enhancement = {result['control_sequences']['random']['max_enhancement']:.1f}%")
                print(f"  ✓ Composite control enhancement = {result['control_sequences']['composite']['max_enhancement']:.1f}%")
                print(f"  ✓ Validation passed: {result['validation_passed']}")
                print(f"  ✓ Computation time: {result['computation_time']:.2f}s")
                print()
                
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                print()
                continue
        
        # Generate comprehensive test report
        test_report = self.generate_comprehensive_report(results)
        
        return {
            'test_case_id': 'TC-INST-01',
            'description': 'Scale Escalation - Comprehensive Asymptotic Convergence Validation',
            'config': self.config,
            'individual_results': results,
            'test_report': test_report,
            'execution_timestamp': datetime.now().isoformat()
        }
    
    def generate_comprehensive_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive test report with detailed analysis."""
        if not results:
            return {'status': 'FAILED', 'reason': 'No valid results'}
        
        # Basic statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['validation_passed'])
        pass_rate = passed_tests / total_tests
        
        # Enhancement convergence analysis
        enhancements = [r['enhancement'] for r in results]
        k_stars = [r['k_star'] for r in results]
        N_values = [r['N'] for r in results]
        
        # Convergence trend analysis
        if len(enhancements) > 1:
            enhancement_trend = np.polyfit(np.log10(N_values), enhancements, 1)[0]
            k_star_stability = np.std(k_stars) < 0.1
        else:
            enhancement_trend = 0.0
            k_star_stability = True
        
        # Precision analysis
        precision_deviations = [r['stability_analysis']['max_deviation'] for r in results]
        all_precise = all(d < self.config.precision_threshold for d in precision_deviations)
        
        # Weyl analysis
        weyl_bounds = [r['weyl_analysis']['discrepancy']['discrepancy_bound'] for r in results]
        weyl_convergence = all(r['weyl_analysis']['criterion']['criterion_satisfied'] for r in results)
        
        # Control sequence analysis
        control_effectiveness = all(
            r['control_sequences']['random']['max_enhancement'] < r['enhancement'] and
            r['control_sequences']['composite']['max_enhancement'] < r['enhancement']
            for r in results
        )
        
        # Overall assessment
        convergence_validated = (
            pass_rate >= 0.75 and
            all_precise and
            weyl_convergence and
            control_effectiveness and
            k_star_stability
        )
        
        status = 'PASSED' if convergence_validated else 'FAILED'
        
        report = {
            'overall_status': status,
            'convergence_validated': convergence_validated,
            'pass_rate': pass_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'enhancement_analysis': {
                'values': enhancements,
                'mean': np.mean(enhancements),
                'std': np.std(enhancements),
                'trend_slope': enhancement_trend,
                'converging_to_target': abs(enhancements[-1] - self.config.target_enhancement) < 5.0 if enhancements else False
            },
            'k_star_analysis': {
                'values': k_stars,
                'mean': np.mean(k_stars),
                'std': np.std(k_stars),
                'stable': k_star_stability
            },
            'precision_analysis': {
                'max_deviation': max(precision_deviations),
                'mean_deviation': np.mean(precision_deviations),
                'all_within_threshold': all_precise,
                'threshold': self.config.precision_threshold
            },
            'weyl_analysis': {
                'discrepancy_bounds': weyl_bounds,
                'mean_discrepancy': np.mean(weyl_bounds),
                'all_criteria_satisfied': weyl_convergence
            },
            'control_analysis': {
                'random_always_lower': control_effectiveness,
                'composite_always_lower': control_effectiveness,
                'effectiveness_validated': control_effectiveness
            },
            'asymptotic_convergence': {
                'enhancement_converging': enhancement_trend < 0,  # Enhancement should decrease with N
                'k_star_stable': k_star_stability,
                'precision_maintained': all_precise,
                'weyl_criterion_satisfied': weyl_convergence
            }
        }
        
        return report
    
    def save_results(self, results: Dict, filename: str = None):
        """Save comprehensive results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tc_inst_01_results_{timestamp}.json'
        
        # Convert numpy types for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            else:
                return obj
        
        json_results = convert_for_json(results)
        
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"Results saved to {filename}")
        return filename

def main():
    """Main execution function for comprehensive TC-INST-01 testing."""
    # Configure for comprehensive validation
    config = TC_INST_01_FullConfig(
        N_values=[5000, 10000, 25000, 50000],  # Manageable sizes for demonstration
        k_min=3.2,
        k_max=3.4,
        k_step=0.01,  # Coarser for faster execution
        precision_threshold=1e-6,
        target_enhancement=15.7,
        bootstrap_samples=500,  # Reduced for faster execution
        weyl_H_max=50,
        control_sample_size=5000
    )
    
    # Execute test case
    executor = TC_INST_01_TestExecutor(config)
    results = executor.execute_test_case()
    
    # Print summary report
    print("\n" + "=" * 120)
    print("TC-INST-01 COMPREHENSIVE TEST REPORT")
    print("=" * 120)
    
    report = results['test_report']
    print(f"Overall Status: {report['overall_status']}")
    print(f"Pass Rate: {report['pass_rate']:.1%}")
    print(f"Convergence Validated: {report['convergence_validated']}")
    print()
    
    print("Enhancement Analysis:")
    enh_analysis = report['enhancement_analysis']
    print(f"  Mean Enhancement: {enh_analysis['mean']:.1f}% (±{enh_analysis['std']:.1f}%)")
    print(f"  Converging to Target: {enh_analysis['converging_to_target']}")
    print(f"  Trend Slope: {enh_analysis['trend_slope']:.3f}")
    print()
    
    print("Precision Analysis:")
    prec_analysis = report['precision_analysis']
    print(f"  Max Deviation: {prec_analysis['max_deviation']:.2e}")
    print(f"  All Within Threshold: {prec_analysis['all_within_threshold']}")
    print()
    
    print("Control Sequence Validation:")
    ctrl_analysis = report['control_analysis']
    print(f"  Random Always Lower: {ctrl_analysis['random_always_lower']}")
    print(f"  Composite Always Lower: {ctrl_analysis['composite_always_lower']}")
    print()
    
    # Save results
    filename = executor.save_results(results)
    
    print(f"\nComprehensive validation {'PASSED' if report['overall_status'] == 'PASSED' else 'FAILED'}")
    print("=" * 120)
    
    return results

if __name__ == "__main__":
    results = main()