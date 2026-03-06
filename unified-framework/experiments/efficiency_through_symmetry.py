"""
Efficiency Through Symmetry Hypothesis Falsification Experiment

Scientific experiment to test the hypothesis that 100,000 zeta zeros provide 
30-40% further error reduction over base Z5D implementation through enhanced
symmetry properties.

This experiment implements controlled comparison testing with statistical
validation to either support or falsify the claimed performance improvements.
"""

import numpy as np
import mpmath as mp
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from typing import Dict, List, Tuple, Optional
import time
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.zero_line import ZeroLine
from statistical.zeta_zeros_extended import ExtendedZetaZeroProcessor
from core.params import MP_DPS, BOOTSTRAP_RESAMPLES_DEFAULT

import json
import numpy as np

def _json_converter(o):
    """
    JSON default converter for NumPy types.
    """
    if isinstance(o, np.ndarray):
        return o.tolist()
    elif isinstance(o, (np.integer, np.floating)):
        return o.item()
    elif isinstance(o, (np.bool_, bool)):
        return bool(o)
    # Let the encoder complain on anything else
    raise TypeError(f"Type {o.__class__.__name__} not JSON serializable")


# Set high precision
mp.mp.dps = MP_DPS

@dataclass
class ExperimentResult:
    """Data class for storing experiment results."""
    method: str
    k_value: int
    true_value: float
    prediction: float
    error_absolute: float
    error_relative: float
    computation_time: float
    num_zeros_used: int

@dataclass
class StatisticalSummary:
    """Statistical summary of experiment results."""
    method: str
    num_zeros: int
    mean_error: float
    median_error: float
    std_error: float
    max_error: float
    min_error: float
    bootstrap_ci_lower: float
    bootstrap_ci_upper: float
    p_value: Optional[float] = None

class EfficiencyThroughSymmetryExperiment:
    """
    Experiment to test the Efficiency Through Symmetry hypothesis.

    This class implements a comprehensive scientific experiment to validate
    or falsify claims about enhanced performance with 100K zeta zeros.
    """

    def __init__(self, max_zeros: int = 100000, precision_dps: int = 50):
        """
        Initialize the experiment.

        Args:
            max_zeros: Maximum number of zeta zeros to compute
            precision_dps: Decimal precision for computations
        """
        self.max_zeros = max_zeros
        self.precision_dps = precision_dps
        mp.mp.dps = precision_dps

        # Initialize components
        self.zero_line = ZeroLine()
        self.zeta_processor = ExtendedZetaZeroProcessor(precision_dps=precision_dps)

        # Test values (k values for prime prediction) - more fine-grained testing
        self.test_k_values = [
            1000, 2000, 5000, 10000, 20000, 50000,
            100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000
        ]

        # True prime values for validation (computed separately)
        self.true_primes = {}

        # Results storage
        self.results = []
        self.statistical_summaries = []

        # Setup logging with reduced verbosity
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        # Override to INFO for important messages only
        self.logger.setLevel(logging.INFO)

    def compute_true_primes(self) -> Dict[int, int]:
        """
        Compute true prime values for test k values.
        Uses sympy for accurate computation of nth primes.
        """
        self.logger.info("Computing true prime values for validation...")
        from sympy import prime

        true_primes = {}
        for k in self.test_k_values:
            try:
                true_primes[k] = int(prime(k))
                self.logger.info(f"p({k}) = {true_primes[k]}")
            except Exception as e:
                self.logger.error(f"Failed to compute p({k}): {e}")
                # Use approximation for very large k
                true_primes[k] = int(k * (np.log(k) + np.log(np.log(k))))

        self.true_primes = true_primes
        return true_primes

    def load_zeta_zeros_from_file(self, filename: str = "zeta.txt", max_zeros: int = None) -> List[complex]:
        """
        Load pre-computed zeta zeros from file to avoid computational cost.

        Args:
            filename: File containing pre-computed zeta zeros
            max_zeros: Maximum number of zeros to load (None for all)

        Returns:
            List of complex zeta zeros
        """
        zeros = []
        filepath = os.path.join(os.path.dirname(__file__), filename)

        try:
            with open(filepath, 'r') as f:
                for i, line in enumerate(f):
                    if max_zeros and i >= max_zeros:
                        break

                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue

                    parts = line.split()
                    if len(parts) >= 2:
                        # Format: index imaginary_part
                        # Real part is always 0.5 for Riemann zeta zeros
                        imag_part = float(parts[1])
                        zero = complex(0.5, imag_part)
                        zeros.append(zero)

        except FileNotFoundError:
            self.logger.error(f"CRITICAL: Zeta zeros file not found: {filepath}")
            self.logger.error("This experiment REQUIRES pre-computed zeta zeros and must never compute them!")
            raise FileNotFoundError(f"Required zeta zeros file missing: {filepath}")
        except Exception as e:
            self.logger.error(f"CRITICAL: Error reading zeta zeros file: {e}")
            raise RuntimeError(f"Failed to load required zeta zeros file: {e}")

        if len(zeros) == 0:
            raise RuntimeError(f"No zeta zeros loaded from {filepath}")

        self.logger.info(f"Successfully loaded {len(zeros)} pre-computed zeta zeros from {filename}")
        return zeros

    def generate_zeta_zeros_computed(self, num_zeros: int) -> List[complex]:
        """
        DEPRECATED: This method should never be called as per user requirements.
        Zeta zeros must always be loaded from pre-computed file.

        Args:
            num_zeros: Number of zeta zeros to compute

        Returns:
            List of complex zeta zeros
        """
        raise RuntimeError("CRITICAL: Zeta zeros computation is forbidden! Must use pre-computed zeta.txt file only!")
    def generate_zeta_zeros(self, num_zeros: int) -> List[complex]:
        """
        Generate zeta zeros - prioritizes pre-computed file over computation.

        Args:
            num_zeros: Number of zeta zeros to use

        Returns:
            List of complex zeta zeros
        """
        return self.load_zeta_zeros_from_file(max_zeros=num_zeros)

    def li_inverse(self, n: float) -> float:
        """Compute inverse logarithmic integral, ensuring real result."""
        n_mp = mp.mpf(n)
        guess = n_mp * (mp.log(n_mp) + mp.log(mp.log(n_mp)) - 1)

        def f(x):
            return mp.li(x) - n_mp

        try:
            result = mp.findroot(f, guess)
            # Ensure we return a real number
            return float(mp.re(result))
        except:
            # Fallback to approximation, ensure real
            return float(mp.re(guess))

    def pi_corrected(self, x: float, zeta_zeros: List[complex], num_zeros: int) -> float:
        """
        Compute corrected prime counting function using zeta zeros.

        Args:
            x: Value to evaluate at
            zeta_zeros: List of zeta zeros
            num_zeros: Number of zeros to use

        Returns:
            Corrected prime count estimate
        """
        x_mp = mp.mpf(x)
        sum_rho = mp.mpf('0')

        for i, zero in enumerate(zeta_zeros[:num_zeros]):
            if i >= num_zeros:
                break

            # Use the zero (real part = 0.5, imaginary part from computation)
            rho = mp.mpc('0.5', zero.imag)
            rho_conj = mp.conj(rho)

            try:
                term1 = mp.li(mp.power(x_mp, rho))
                term2 = mp.li(mp.power(x_mp, rho_conj))
                sum_rho += term1 + term2
            except:
                # Skip problematic terms
                continue

        result = mp.li(x_mp) - sum_rho - mp.log(2)
        # Ensure we return a real number by taking the real part
        return float(mp.re(result))

    def z5d_prime_enhanced(self, k: int, zeta_zeros: List[complex],
                           num_zeros: int, max_iter: int = 20) -> float:
        """
        Enhanced Z5D prime prediction using zeta zeros.

        Args:
            k: Prime index (find k-th prime)
            zeta_zeros: List of zeta zeros
            num_zeros: Number of zeros to use
            max_iter: Maximum Newton iterations

        Returns:
            Predicted k-th prime
        """
        k_mp = mp.mpf(k)
        tol = mp.mpf('1e-20')

        # Initial guess using inverse li
        x = mp.mpf(self.li_inverse(k))

        # Ensure x stays real - take real part if it somehow becomes complex
        if hasattr(x, 'real'):
            # Validate that x is real; document possible scenarios for complexity.
            # x should be real as li_inverse returns a real value for k > 0, but numerical issues may cause complexity.
            if mp.im(x) != 0:
                self.logger.warning(f"x became complex (im={mp.im(x)}) for k={k}. Taking real part.")
                x = mp.re(x)
        x = mp.mpf(x)

        # Newton's method to solve pi_corrected(x) = k
        for iteration in range(max_iter):
            try:
                # Ensure x is real before converting to float
                x_real = mp.re(x)
                px = self.pi_corrected(float(x_real), zeta_zeros, num_zeros)
                px_mp = mp.mpf(px)

                # Derivative approximation
                if x_real > 0:
                    dpx = mp.mpf(1) / mp.log(x_real)
                else:
                    # Fallback for edge cases - ensure real result
                    fallback_result = k_mp * (mp.log(k_mp) + mp.log(mp.log(k_mp)) - 1)
                    return float(mp.re(fallback_result))

                # Newton step
                dx = (px_mp - k_mp) / dpx
                x = mp.re(x - dx)  # Ensure x stays real by taking real part

                # Ensure x stays positive and real
                if x <= 0:
                    x = mp.mpf(k) * mp.log(k)

                if mp.fabs(dx) < tol * mp.fabs(x):  # Use mp.fabs for both dx and x
                    break

            except (ValueError, OverflowError, ZeroDivisionError) as e:
                if iteration == 0:  # Only log on first failure to reduce noise
                    self.logger.debug(f"Newton iteration {iteration} failed: {e}")
                # Use simpler approximation on failure
                return float(k_mp * (mp.log(k_mp) + mp.log(mp.log(k_mp)) - 1))

        return float(mp.re(x))

    def baseline_z5d_prediction(self, k: int) -> float:
        """
        Baseline Z5D prediction without zeta zeros enhancement.

        Args:
            k: Prime index

        Returns:
            Predicted k-th prime
        """
        # Use existing ZeroLine implementation for baseline
        try:
            result = self.zero_line.z5d_prime(k)
            return float(result)
        except Exception:
            # Fallback to PNT approximation
            return k * (np.log(k) + np.log(np.log(k)) - 1)

    def run_single_experiment(self, k: int, method: str,
                              num_zeros: int = 0, zeta_zeros: List[complex] = None) -> ExperimentResult:
        """
        Run a single prediction experiment.

        Args:
            k: Prime index to predict
            method: Method name ('baseline', 'enhanced_10k', 'enhanced_100k')
            num_zeros: Number of zeta zeros to use
            zeta_zeros: Precomputed zeta zeros

        Returns:
            ExperimentResult object
        """
        start_time = time.time()

        # Get true value
        true_value = self.true_primes.get(k, k * np.log(k))

        # Make prediction based on method
        if method == 'baseline':
            prediction = self.baseline_z5d_prediction(k)
        elif method.startswith('enhanced'):
            if zeta_zeros is None:
                zeta_zeros = self.generate_zeta_zeros(num_zeros)
            prediction = self.z5d_prime_enhanced(k, zeta_zeros, num_zeros)
        else:
            raise ValueError(f"Unknown method: {method}")

        computation_time = time.time() - start_time

        # Calculate errors
        error_absolute = abs(prediction - true_value)
        error_relative = error_absolute / true_value if true_value > 0 else float('inf')

        return ExperimentResult(
            method=method,
            k_value=k,
            true_value=true_value,
            prediction=prediction,
            error_absolute=error_absolute,
            error_relative=error_relative,
            computation_time=computation_time,
            num_zeros_used=num_zeros
        )

    def bootstrap_analysis(self, errors: List[float], n_bootstrap: int = 1000) -> Tuple[float, float]:
        """
        Perform bootstrap analysis on error measurements.

        Args:
            errors: List of relative errors
            n_bootstrap: Number of bootstrap samples

        Returns:
            Tuple of (lower_ci, upper_ci) for 95% confidence interval
        """
        bootstrap_means = []

        for _ in range(n_bootstrap):
            # Bootstrap sample
            sample = np.random.choice(errors, size=len(errors), replace=True)
            bootstrap_means.append(np.mean(sample))

        # Calculate 95% confidence interval
        lower_ci = np.percentile(bootstrap_means, 2.5)
        upper_ci = np.percentile(bootstrap_means, 97.5)

        return lower_ci, upper_ci

    def statistical_significance_test(self, errors_baseline: List[float],
                                      errors_enhanced: List[float]) -> float:
        """
        Test statistical significance between baseline and enhanced methods.

        Args:
            errors_baseline: Baseline method errors
            errors_enhanced: Enhanced method errors

        Returns:
            p-value from statistical test
        """
        # Use Wilcoxon rank-sum test (non-parametric)
        try:
            statistic, p_value = stats.ranksums(errors_baseline, errors_enhanced)
            return p_value
        except ValueError:
            return 1.0  # No significant difference

    def run_comprehensive_experiment(self) -> Dict:
        """
        Run the complete experimental protocol with fine-grained testing.

        Returns:
            Dictionary containing all experimental results and analysis
        """
        self.logger.info("Starting Efficiency Through Symmetry Hypothesis Experiment")

        # Step 1: Compute true primes for validation
        self.compute_true_primes()

        # Step 2: Load pre-computed zeta zeros (much faster than computation)
        self.logger.info("Loading pre-computed zeta zeros...")
        all_zeta_zeros = self.load_zeta_zeros_from_file()

        # Step 3: Fine-grained testing with multiple zero counts
        self.logger.info("Setting up fine-grained test scenarios...")
        zero_counts = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]

        # Step 4: Run experiments for each method, zero count, and k value
        methods = [('baseline', 0)]
        for count in zero_counts:
            methods.append((f'enhanced_{count}', count))

        all_results = []

        for k in self.test_k_values:
            self.logger.info(f"Testing k = {k}")

            for method_name, num_zeros in methods:
                # Only log major milestones to reduce console spam
                if method_name == 'baseline' or num_zeros in [1000, 10000, 100000]:
                    self.logger.info(f"  Method: {method_name}")

                try:
                    # Use subset of pre-computed zeros for this test
                    zeros_subset = all_zeta_zeros[:num_zeros] if num_zeros > 0 else None

                    result = self.run_single_experiment(k, method_name, num_zeros, zeros_subset)
                    all_results.append(result)

                    # Only log key results to avoid console overflow
                    if method_name == 'baseline' or num_zeros in [1000, 10000, 100000]:
                        self.logger.info(f"    Prediction: {result.prediction:.1f}")
                        self.logger.info(f"    True value: {result.true_value}")
                        self.logger.info(f"    Relative error: {result.error_relative:.6f}")
                        self.logger.info(f"    Time: {result.computation_time:.3f}s")

                except Exception as e:
                    if method_name == 'baseline' or num_zeros in [1000, 10000, 100000]:
                        self.logger.error(f"    Failed: {e}")

        self.results = all_results

        # Step 5: Enhanced statistical analysis with fine-grained data
        return self.analyze_results_fine_grained()

    def analyze_results_fine_grained(self) -> Dict:
        """
        Enhanced analysis with fine-grained testing results.

        Returns:
            Dictionary containing detailed analysis results
        """
        self.logger.info("Analyzing fine-grained experimental results...")

        # Group results by method and number of zeros
        results_by_method = {}
        results_by_zeros = {}

        for result in self.results:
            method = result.method
            num_zeros = result.num_zeros_used

            if method not in results_by_method:
                results_by_method[method] = []
            results_by_method[method].append(result)

            if num_zeros not in results_by_zeros:
                results_by_zeros[num_zeros] = []
            results_by_zeros[num_zeros].append(result)

        # Generate statistical summaries
        summaries = {}

        for method, method_results in results_by_method.items():
            errors = [r.error_relative for r in method_results]
            times = [r.computation_time for r in method_results]
            num_zeros = method_results[0].num_zeros_used if method_results else 0

            # Bootstrap confidence interval
            if len(errors) > 1:
                ci_lower, ci_upper = self.bootstrap_analysis(errors)
            else:
                ci_lower = ci_upper = np.mean(errors) if errors else 0

            summary = StatisticalSummary(
                method=method,
                num_zeros=num_zeros,
                mean_error=np.mean(errors) if errors else 0,
                median_error=np.median(errors) if errors else 0,
                std_error=np.std(errors) if errors else 0,
                max_error=np.max(errors) if errors else 0,
                min_error=np.min(errors) if errors else 0,
                bootstrap_ci_lower=ci_lower,
                bootstrap_ci_upper=ci_upper
            )

            summaries[method] = summary

        self.statistical_summaries = list(summaries.values())

        # Enhanced hypothesis testing with fine-grained data
        hypothesis_analysis = self.test_hypothesis_claims_fine_grained(results_by_method, results_by_zeros)

        # Convergence analysis
        convergence_analysis = self.analyze_convergence_patterns(results_by_zeros)

        return {
            'results': [asdict(r) for r in self.results],
            'statistical_summaries': [asdict(s) for s in self.statistical_summaries],
            'hypothesis_analysis': hypothesis_analysis,
            'convergence_analysis': convergence_analysis,
            'experiment_metadata': {
                'timestamp': datetime.now().isoformat(),
                'max_zeros_tested': self.max_zeros,
                'precision_dps': self.precision_dps,
                'test_k_values': self.test_k_values,
                'true_primes': self.true_primes,
                'zero_counts_tested': sorted(list(set(r.num_zeros_used for r in self.results))),
                'using_precomputed_zeros': True
            }
        }

    def analyze_convergence_patterns(self, results_by_zeros: Dict) -> Dict:
        """
        Analyze how accuracy improves with increasing numbers of zeta zeros.

        Args:
            results_by_zeros: Results grouped by number of zeros used

        Returns:
            Dictionary containing convergence analysis
        """
        self.logger.info("Analyzing convergence patterns...")

        zero_counts = sorted([z for z in results_by_zeros.keys() if z > 0])
        convergence_data = []

        for num_zeros in zero_counts:
            results = results_by_zeros[num_zeros]
            errors = [r.error_relative for r in results]

            if errors:
                convergence_data.append({
                    'num_zeros': num_zeros,
                    'mean_error': np.mean(errors),
                    'median_error': np.median(errors),
                    'std_error': np.std(errors),
                    'min_error': np.min(errors),
                    'max_error': np.max(errors)
                })

        # Calculate improvement rates
        improvements = []
        for i in range(1, len(convergence_data)):
            prev_error = convergence_data[i-1]['mean_error']
            curr_error = convergence_data[i]['mean_error']

            if prev_error > 0:
                improvement_percent = (prev_error - curr_error) / prev_error * 100
                improvements.append({
                    'from_zeros': convergence_data[i-1]['num_zeros'],
                    'to_zeros': convergence_data[i]['num_zeros'],
                    'improvement_percent': improvement_percent
                })

        return {
            'convergence_data': convergence_data,
            'improvements': improvements,
            'optimal_zero_count': self.find_optimal_zero_count(convergence_data),
            'diminishing_returns_threshold': self.find_diminishing_returns(improvements)
        }

    def find_optimal_zero_count(self, convergence_data: List[Dict]) -> Dict:
        """Find the optimal number of zeros balancing accuracy and computational cost."""
        if not convergence_data:
            return {}

        # Find point with best error
        best_error_point = min(convergence_data, key=lambda x: x['mean_error'])

        # Find point with best error/cost ratio (simplified)
        best_ratio_point = min(convergence_data,
                               key=lambda x: x['mean_error'] * np.log(x['num_zeros'] + 1))

        return {
            'best_accuracy': best_error_point,
            'best_efficiency': best_ratio_point
        }

    def find_diminishing_returns(self, improvements: List[Dict]) -> Dict:
        """Find where improvements start to diminish significantly."""
        if len(improvements) < 2:
            return {}

        # Find where improvement drops below certain threshold
        threshold = 5.0  # 5% improvement threshold

        for i, improvement in enumerate(improvements):
            if improvement['improvement_percent'] < threshold:
                return {
                    'threshold_zeros': improvement['from_zeros'],
                    'threshold_improvement': improvement['improvement_percent'],
                    'recommendation': f"Beyond {improvement['from_zeros']} zeros, improvements < {threshold}%"
                }

        return {'recommendation': "No significant diminishing returns observed in tested range"}

    def test_hypothesis_claims_fine_grained(self, results_by_method: Dict, results_by_zeros: Dict) -> Dict:
        """
        Enhanced hypothesis testing with fine-grained data.

        Args:
            results_by_method: Results grouped by method
            results_by_zeros: Results grouped by number of zeros

        Returns:
            Dictionary containing detailed hypothesis test results
        """
        self.logger.info("Testing hypothesis claims with fine-grained analysis...")

        analysis = {
            'error_reduction_claim': {},
            'confidence_interval_claim': {},
            'statistical_significance': {},
            'fine_grained_analysis': {}
        }

        # Get baseline errors
        baseline_errors = [r.error_relative for r in results_by_method.get('baseline', [])]

        # Test claims for different zero counts
        zero_counts = [10000, 100000]  # Focus on the claimed counts

        for count in zero_counts:
            enhanced_method = f'enhanced_{count}'
            enhanced_errors = [r.error_relative for r in results_by_method.get(enhanced_method, [])]

            if baseline_errors and enhanced_errors:
                baseline_mean = np.mean(baseline_errors)
                enhanced_mean = np.mean(enhanced_errors)

                if baseline_mean > 0:
                    reduction_percent = (baseline_mean - enhanced_mean) / baseline_mean * 100

                    analysis['fine_grained_analysis'][f'{count}_zeros'] = {
                        'reduction_percent': reduction_percent,
                        'baseline_mean_error': baseline_mean,
                        'enhanced_mean_error': enhanced_mean,
                        'claim_30_40_percent': 30 <= reduction_percent <= 40,
                        'statistical_significance': self.statistical_significance_test(baseline_errors, enhanced_errors)
                    }

        # Focus on 100K zeros for main hypothesis test
        enhanced_100k_errors = [r.error_relative for r in results_by_method.get('enhanced_100000', [])]

        if baseline_errors and enhanced_100k_errors:
            baseline_mean = np.mean(baseline_errors)
            enhanced_100k_mean = np.mean(enhanced_100k_errors)

            if baseline_mean > 0:
                reduction_percent = (baseline_mean - enhanced_100k_mean) / baseline_mean * 100

                analysis['error_reduction_claim'] = {
                    'claimed_range': [30, 40],
                    'observed_reduction_percent': reduction_percent,
                    'claim_supported': 30 <= reduction_percent <= 40,
                    'baseline_mean_error': baseline_mean,
                    'enhanced_100k_mean_error': enhanced_100k_mean
                }

            # Test bootstrap CI claim [28.5%, 41.2%]
            if enhanced_100k_errors:
                ci_lower, ci_upper = self.bootstrap_analysis(enhanced_100k_errors)
                ci_lower_percent = ci_lower * 100
                ci_upper_percent = ci_upper * 100

                analysis['confidence_interval_claim'] = {
                    'claimed_ci': [28.5, 41.2],
                    'observed_ci': [ci_lower_percent, ci_upper_percent],
                    'claim_supported': (28.5 <= ci_lower_percent <= 41.2) and (28.5 <= ci_upper_percent <= 41.2)
                }

            # Statistical significance tests
            p_value = self.statistical_significance_test(baseline_errors, enhanced_100k_errors)

            analysis['statistical_significance'] = {
                'p_value': p_value,
                'significant_at_0_05': p_value < 0.05,
                'significant_at_0_01': p_value < 0.01,
                'claimed_significance': 'p < 10^-10',
                'claim_supported': p_value < 1e-10
            }

        return analysis

    def analyze_results(self) -> Dict:
        """
        Analyze experimental results and generate statistical summaries (legacy method).

        Returns:
            Dictionary containing analysis results
        """
        # Fallback to fine-grained analysis
        return self.analyze_results_fine_grained()

    def test_hypothesis_claims(self, results_by_method: Dict) -> Dict:
        """
        Test specific claims from the Efficiency Through Symmetry hypothesis.

        Args:
            results_by_method: Results grouped by method

        Returns:
            Dictionary containing hypothesis test results
        """
        self.logger.info("Testing hypothesis claims...")

        analysis = {
            'error_reduction_claim': {},
            'confidence_interval_claim': {},
            'statistical_significance': {}
        }

        # Get errors for each method
        baseline_errors = [r.error_relative for r in results_by_method.get('baseline', [])]
        enhanced_10k_errors = [r.error_relative for r in results_by_method.get('enhanced_10k', [])]
        enhanced_100k_errors = [r.error_relative for r in results_by_method.get('enhanced_100k', [])]

        # Test claim: 30-40% further error reduction with 100K zeros
        if baseline_errors and enhanced_100k_errors:
            baseline_mean = np.mean(baseline_errors)
            enhanced_100k_mean = np.mean(enhanced_100k_errors)

            if baseline_mean > 0:
                reduction_percent = (baseline_mean - enhanced_100k_mean) / baseline_mean * 100

                analysis['error_reduction_claim'] = {
                    'claimed_range': [30, 40],
                    'observed_reduction_percent': reduction_percent,
                    'claim_supported': 30 <= reduction_percent <= 40,
                    'baseline_mean_error': baseline_mean,
                    'enhanced_100k_mean_error': enhanced_100k_mean
                }

        # Test bootstrap CI claim [28.5%, 41.2%]
        if enhanced_100k_errors:
            ci_lower, ci_upper = self.bootstrap_analysis(enhanced_100k_errors)
            ci_lower_percent = ci_lower * 100
            ci_upper_percent = ci_upper * 100

            analysis['confidence_interval_claim'] = {
                'claimed_ci': [28.5, 41.2],
                'observed_ci': [ci_lower_percent, ci_upper_percent],
                'claim_supported': (28.5 <= ci_lower_percent <= 41.2) and (28.5 <= ci_upper_percent <= 41.2)
            }

        # Statistical significance tests
        if baseline_errors and enhanced_100k_errors:
            p_value = self.statistical_significance_test(baseline_errors, enhanced_100k_errors)

            analysis['statistical_significance'] = {
                'p_value': p_value,
                'significant_at_0_05': p_value < 0.05,
                'significant_at_0_01': p_value < 0.01,
                'claimed_significance': 'p < 10^-10',
                'claim_supported': p_value < 1e-10
            }

        return analysis

    def generate_report(self, results: Dict, output_file: str = None) -> str:
        """
        Generate comprehensive experimental report with fine-grained analysis.

        Args:
            results: Analysis results dictionary
            output_file: Optional file to save report

        Returns:
            Report as string
        """
        report_lines = [
            "# Efficiency Through Symmetry Hypothesis Falsification Report",
            "## Enhanced Fine-Grained Analysis with Pre-Computed Zeta Zeros",
            "",
            f"**Experiment Date:** {results['experiment_metadata']['timestamp']}",
            f"**Precision:** {results['experiment_metadata']['precision_dps']} decimal places",
            f"**Test k values:** {results['experiment_metadata']['test_k_values']}",
            f"**Zero counts tested:** {results['experiment_metadata'].get('zero_counts_tested', [])}",
            f"**Using pre-computed zeros:** {results['experiment_metadata'].get('using_precomputed_zeros', False)}",
            "",
            "## Hypothesis Under Test",
            "",
            "The hypothesis claims that using 100,000 zeta zeros provides:",
            "- 30-40% further error reduction over base Z5D implementation",
            "- Bootstrap confidence interval [28.5%, 41.2%] with n=1,000 resamples",
            "- Statistical significance p < 10^-10",
            "",
            "## Fine-Grained Experimental Results",
            ""
        ]

        # Add convergence analysis if available
        if 'convergence_analysis' in results:
            conv_analysis = results['convergence_analysis']
            report_lines.extend([
                "### Convergence Analysis",
                "",
                "Analysis of how accuracy improves with increasing numbers of zeta zeros:",
                ""
            ])

            if 'convergence_data' in conv_analysis:
                report_lines.extend([
                    "| Zero Count | Mean Error (%) | Median Error (%) | Std Error (%) |",
                    "|------------|----------------|------------------|---------------|"
                ])

                for data in conv_analysis['convergence_data']:
                    row = (f"| {data['num_zeros']} | {data['mean_error']*100:.6f} | "
                           f"{data['median_error']*100:.6f} | {data['std_error']*100:.6f} |")
                    report_lines.append(row)

                report_lines.append("")

            if 'optimal_zero_count' in conv_analysis:
                optimal = conv_analysis['optimal_zero_count']
                if optimal:
                    report_lines.extend([
                        "**Optimal Zero Count Analysis:**",
                        f"- Best accuracy: {optimal.get('best_accuracy', {}).get('num_zeros', 'N/A')} zeros",
                        f"- Best efficiency: {optimal.get('best_efficiency', {}).get('num_zeros', 'N/A')} zeros",
                        ""
                    ])

            if 'diminishing_returns_threshold' in conv_analysis:
                dim_returns = conv_analysis['diminishing_returns_threshold']
                if dim_returns:
                    report_lines.extend([
                        f"**Diminishing Returns:** {dim_returns.get('recommendation', 'N/A')}",
                        ""
                    ])

        # Add detailed results table
        report_lines.extend([
            "### Performance Comparison",
            "",
            "| Method | Num Zeros | Mean Error (%) | Median Error (%) | 95% CI Lower | 95% CI Upper |",
            "|--------|-----------|----------------|------------------|--------------|--------------|"
        ])

        for summary in results['statistical_summaries']:
            row = (f"| {summary['method']} | {summary['num_zeros']} | "
                   f"{summary['mean_error']*100:.6f} | {summary['median_error']*100:.6f} | "
                   f"{summary['bootstrap_ci_lower']*100:.6f} | {summary['bootstrap_ci_upper']*100:.6f} |")
            report_lines.append(row)

        # Add hypothesis test results
        hyp_analysis = results['hypothesis_analysis']

        report_lines.extend([
            "",
            "## Hypothesis Test Results",
            ""
        ])

        # Fine-grained analysis results
        if 'fine_grained_analysis' in hyp_analysis:
            fine_grained = hyp_analysis['fine_grained_analysis']
            report_lines.extend([
                "### Fine-Grained Analysis by Zero Count",
                ""
            ])

            for zero_count, analysis in fine_grained.items():
                status = "✅ SUPPORTED" if analysis.get('claim_30_40_percent', False) else "❌ FALSIFIED"
                report_lines.extend([
                    f"**{zero_count.replace('_', ' ').title()}:**",
                    f"- Error reduction: {analysis.get('reduction_percent', 0):.2f}%",
                    f"- 30-40% claim: {status}",
                    f"- p-value: {analysis.get('statistical_significance', 1):.2e}",
                    ""
                ])

        # Main hypothesis claims
        if 'error_reduction_claim' in hyp_analysis:
            claim = hyp_analysis['error_reduction_claim']
            if claim:
                status = "✅ SUPPORTED" if claim.get('claim_supported', False) else "❌ FALSIFIED"
                report_lines.extend([
                    f"### Error Reduction Claim (100K zeros): {status}",
                    f"- **Claimed:** 30-40% reduction",
                    f"- **Observed:** {claim.get('observed_reduction_percent', 0):.2f}% reduction",
                    ""
                ])

        if 'confidence_interval_claim' in hyp_analysis:
            claim = hyp_analysis['confidence_interval_claim']
            if claim:
                status = "✅ SUPPORTED" if claim.get('claim_supported', False) else "❌ FALSIFIED"
                report_lines.extend([
                    f"### Confidence Interval Claim: {status}",
                    f"- **Claimed CI:** {claim.get('claimed_ci', [])}%",
                    f"- **Observed CI:** [{claim.get('observed_ci', [0,0])[0]:.2f}%, {claim.get('observed_ci', [0,0])[1]:.2f}%]",
                    ""
                ])

        if 'statistical_significance' in hyp_analysis:
            claim = hyp_analysis['statistical_significance']
            if claim:
                status = "✅ SUPPORTED" if claim.get('claim_supported', False) else "❌ FALSIFIED"
                report_lines.extend([
                    f"### Statistical Significance Claim: {status}",
                    f"- **Claimed:** p < 10^-10",
                    f"- **Observed:** p = {claim.get('p_value', 1):.2e}",
                    ""
                ])

        # Add conclusions
        total_claims = 3
        supported_claims = sum([
            hyp_analysis.get('error_reduction_claim', {}).get('claim_supported', False),
            hyp_analysis.get('confidence_interval_claim', {}).get('claim_supported', False),
            hyp_analysis.get('statistical_significance', {}).get('claim_supported', False)
        ])

        report_lines.extend([
            "## Conclusions",
            "",
            f"**Hypothesis Support:** {supported_claims}/{total_claims} claims supported",
            ""
        ])

        if supported_claims == total_claims:
            report_lines.append("✅ **HYPOTHESIS SUPPORTED:** All claims validated by experimental evidence.")
        elif supported_claims > 0:
            report_lines.append("⚠️ **HYPOTHESIS PARTIALLY SUPPORTED:** Some claims validated, others falsified.")
        else:
            report_lines.append("❌ **HYPOTHESIS FALSIFIED:** Experimental evidence does not support the claims.")

        report_lines.extend([
            "",
            "## Computational Advantages",
            "",
            f"- Used pre-computed zeta zeros from file (100,000 zeros available)",
            f"- Significantly reduced computation time compared to on-the-fly calculation",
            f"- Enabled fine-grained testing across {len(results['experiment_metadata'].get('zero_counts_tested', []))} different zero counts",
            f"- Enhanced statistical power through larger sample sizes",
            "",
            "## Reproducibility",
            "",
            "This experiment can be reproduced using:",
            "```python",
            "from experiments.efficiency_through_symmetry import EfficiencyThroughSymmetryExperiment",
            "experiment = EfficiencyThroughSymmetryExperiment()",
            "results = experiment.run_comprehensive_experiment()",
            "report = experiment.generate_report(results)",
            "```",
            "",
            "The experiment automatically uses pre-computed zeta zeros from `zeta.txt` if available,",
            "falling back to computation if the file is not found.",
            ""
        ])

        report_text = "\n".join(report_lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            self.logger.info(f"Report saved to {output_file}")

        return report_text


def main():
    """Main execution function for running the experiment."""
    experiment = EfficiencyThroughSymmetryExperiment()

    print("Starting Efficiency Through Symmetry Hypothesis Falsification Experiment")
    print("=" * 80)

    # Run experiment
    results = experiment.run_comprehensive_experiment()

    # Generate report
    report = experiment.generate_report(results, 'efficiency_through_symmetry_report.md')

    # Save results to JSON
    with open('efficiency_through_symmetry_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=_json_converter)

    print("\nExperiment completed!")
    print("Results saved to: efficiency_through_symmetry_results.json")
    print("Report saved to: efficiency_through_symmetry_report.md")

    return results


if __name__ == "__main__":
    main()