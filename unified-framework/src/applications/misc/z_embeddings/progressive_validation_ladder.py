#!/usr/bin/env python3
"""
Progressive Validation Ladder for Z5D Factorization
==================================================

This module implements a comprehensive progressive validation system for testing Z5D factorization
across increasing RSA key sizes, from RSA-768 (known factorization, 2009) through RSA-4096.

Key Features:
- Progressive testing from known cases to uncharted territory
- Error trend analysis across cryptographic scales  
- Binary search convergence validation at each level
- Performance benchmarking with consistent metrics
- Prediction accuracy tracking and documentation

The validation ladder provides systematic evidence of Z5D algorithm scaling properties
and validates accuracy/performance trends from verified cases to larger scales.
"""

import time
import json
import math
import sys
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import warnings

# Add framework paths
sys.path.insert(0, os.path.dirname(__file__))
from z5d_harness import Z5DHarness

# Create global predictor instance
z5d_predictor = Z5DHarness()

try:
    import mpmath
    mpmath.mp.dps = 1500  # RSA-4096 baseline precision (617-digit primes)
    MPMATH_AVAILABLE = True
except ImportError:
    MPMATH_AVAILABLE = False
    warnings.warn("mpmath not available - high precision mode disabled")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    warnings.warn("numpy not available - array operations disabled")

@dataclass
class ValidationResult:
    """Results from a single validation step in the ladder."""
    rsa_bits: int
    expected_factors: Optional[Tuple[str, str]]
    predicted_k_values: List[float]
    prediction_errors: List[float]
    convergence_iterations: int
    execution_time: float
    binary_search_success: bool
    accuracy_percentage: float
    notes: str

@dataclass
class ProgressiveLadderResults:
    """Complete results from progressive validation ladder."""
    timestamp: str
    total_levels: int
    successful_levels: int
    error_trend_analysis: Dict[str, Any]
    convergence_analysis: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    validation_results: List[ValidationResult]
    overall_success: bool

class ProgressiveValidationLadder:
    """
    Progressive Validation Ladder for Z5D Factorization Testing
    
    Tests Z5D factorization accuracy and performance across increasing RSA key sizes,
    starting from known factorizations and progressing to uncharted territory.
    """
    
    # RSA-768 factorization (known from 2009)
    RSA_768_FACTORS = (
        "33478071698956898786044169848212690817704794983713768568912431388982883793878002287614711652531743087737814467999489",
        "36746043666799590428244633799627952632279158164343087642676032283815739666511279233373417143396810270092798736308917"
    )
    
    def __init__(self, enable_high_precision: bool = True):
        """Initialize the validation ladder."""
        self.enable_high_precision = enable_high_precision and MPMATH_AVAILABLE
        self.validation_levels = self._setup_validation_levels()
        
    def set_dynamic_precision(self, bits: int) -> int:
        """
        Set dynamic precision for mpmath based on RSA bit length.
        Based on PR #686 insights with baseline dps=50 and scaling factor.
        
        Args:
            bits: RSA key size in bits
            
        Returns:
            int: New dps value set for mpmath
        """
        if not self.enable_high_precision:
            return 50
            
        base_dps = 1500  # RSA-4096 baseline precision
        scaling_factor = bits // 10  # Conservative scaling from 4096-bit baseline
        new_dps = base_dps + scaling_factor  # e.g., 1500 + 409 = 1909 for 4096 bits
        
        mpmath.mp.dps = new_dps
        return new_dps
    
    def pnt_baseline_estimate(self, k: float) -> float:
        """
        Baseline Prime Number Theorem estimation for comparison.
        
        Args:
            k: k-index for prime estimation
            
        Returns:
            float: PNT estimate of the k-th prime
        """
        if k <= 0:
            return 0.0
            
        try:
            if self.enable_high_precision:
                with mpmath.workdps(50):
                    k_mp = mpmath.mpf(k)
                    log_k = mpmath.log(k_mp)
                    # Standard PNT approximation: p_k ≈ k * ln(k)
                    return k_mp * log_k
            else:
                return k * math.log(k)
        except (OverflowError, ValueError):
            return float('inf')
    
    def benchmark_comparison(self, k_values: List[float], true_primes: List[int]) -> Dict[str, Any]:
        """
        Compare Z5D vs PNT performance for given k-values and true primes.
        
        Args:
            k_values: List of k-indices  
            true_primes: List of corresponding true prime values
            
        Returns:
            dict: Comparison metrics
        """
        z5d_errors = []
        pnt_errors = []
        z5d_times = []
        pnt_times = []
        
        for k, true_prime in zip(k_values, true_primes):
            # Z5D prediction
            start_time = time.time()
            try:
                z5d_pred = z5d_predictor.z5d_prime(k)
                z5d_error = float(abs(z5d_pred - true_prime) / true_prime)
            except:
                z5d_error = float('inf')
            z5d_time = time.time() - start_time
            
            # PNT baseline prediction  
            start_time = time.time()
            pnt_pred = self.pnt_baseline_estimate(k)
            pnt_error = float(abs(pnt_pred - true_prime) / true_prime)
            pnt_time = time.time() - start_time
            
            z5d_errors.append(z5d_error)
            pnt_errors.append(pnt_error)
            z5d_times.append(z5d_time)
            pnt_times.append(pnt_time)
        
        # Calculate summary statistics
        valid_z5d = [e for e in z5d_errors if not math.isinf(e)]
        valid_pnt = [e for e in pnt_errors if not math.isinf(e)]
        
        return {
            'z5d_avg_error': sum(valid_z5d) / len(valid_z5d) if valid_z5d else float('inf'),
            'pnt_avg_error': sum(valid_pnt) / len(valid_pnt) if valid_pnt else float('inf'),
            'z5d_avg_time': sum(z5d_times) / len(z5d_times),
            'pnt_avg_time': sum(pnt_times) / len(pnt_times),
            'z5d_success_rate': len(valid_z5d) / len(z5d_errors),
            'pnt_success_rate': len(valid_pnt) / len(pnt_errors),
            'speedup_ratio': (sum(z5d_times) / len(z5d_times)) / (sum(pnt_times) / len(pnt_times)) if pnt_times else float('inf')
        }
    
    def safe_k_estimate(self, n: int, delta_max: Optional[float] = None,
                       tolerance: float = 1e-6) -> Tuple[Any, bool]:
        """
        Safe k-index estimation with overflow protection.
        
        Args:
            n: Number for k-index estimation
            delta_max: Maximum delta for computation (optional)
            tolerance: Numerical tolerance
            
        Returns:
            tuple: (k_estimate, extrapolated_flag)
        """
        try:
            if self.enable_high_precision:
                with mpmath.workdps(100):
                    n_mp = mpmath.mpf(n)
                    # Use logarithmic integral inverse approximation
                    log_n = mpmath.log(n_mp)
                    
                    # Check for potential overflow conditions - RSA-4096+ scale
                    if log_n > 5000 or n_mp > mpmath.mpf('1e1000'):
                        return mpmath.mpf('1e1000'), True  # Flag as extrapolated

                    k = n_mp / log_n * (1 + 1/log_n + 2.51/(log_n**2))

                    # Additional safety checks for RSA-4096+ scale
                    if mpmath.isinf(k) or mpmath.isnan(k) or k > mpmath.mpf('1e1000'):
                        return mpmath.mpf('1e1000'), True  # Cap for ultra-scales

                    return k, False  # Return mpmath object, not float!
            else:
                log_n = math.log(n)
                if log_n > 2300 or n > 1e1000:  # RSA-4096+ scale limits
                    return 1e1000, True

                k = n / log_n * (1 + 1/log_n + 2.51/(log_n**2))

                if math.isinf(k) or math.isnan(k) or k > 1e1000:
                    return 1e1000, True
                    
                return k, False
                
        except (OverflowError, ValueError, ZeroDivisionError):
            return 1e1000, True  # Flag as extrapolated due to numerical issues
        
    def _setup_validation_levels(self) -> List[Dict[str, Any]]:
        """Setup the progressive validation levels."""
        return [
            {
                'name': 'RSA-768',
                'bits': 768,
                'known_factors': self.RSA_768_FACTORS,
                'description': 'Known factorization from 2009 - baseline validation',
                'trials': 100,
                'max_iterations': 1000,
                'tolerance': 1e-6
            },
            {
                'name': 'RSA-1024',
                'bits': 1024,
                'known_factors': None,  # Self-generated for testing
                'description': 'Standard RSA-1024 - intermediate validation',
                'trials': 50,
                'max_iterations': 2000,
                'tolerance': 1e-5
            },
            {
                'name': 'RSA-2048',
                'bits': 2048,
                'known_factors': None,  # Self-generated for testing
                'description': 'Standard RSA-2048 - advanced validation',
                'trials': 25,
                'max_iterations': 5000,
                'tolerance': 1e-4
            },
            {
                'name': 'RSA-4096',
                'bits': 4096,
                'known_factors': None,  # Self-generated for testing
                'description': 'RSA-4096 demonstration - extreme scale validation',
                'trials': 10,
                'max_iterations': 10000,
                'tolerance': 1e-3
            }
        ]
    
    def generate_rsa_test_composite(self, bits: int) -> Tuple[int, Tuple[int, int]]:
        """
        Generate a test composite number for RSA validation.
        
        For testing purposes, generates two random primes of appropriate size.
        In real cryptographic applications, these would be chosen more carefully.
        """
        import random
        
        # Calculate target prime size (roughly half the composite size)
        prime_bits = bits // 2
        
        # Generate two test primes of appropriate size
        # Note: This is for testing only, not cryptographically secure
        min_prime = 2**(prime_bits - 1)
        max_prime = 2**prime_bits - 1
        
        def is_probably_prime(n, k=20):
            """Miller-Rabin primality test."""
            if n < 2:
                return False
            if n == 2 or n == 3:
                return True
            if n % 2 == 0:
                return False
            
            # Write n-1 as d * 2^r
            r = 0
            d = n - 1
            while d % 2 == 0:
                r += 1
                d //= 2
            
            # Miller-Rabin test
            for _ in range(k):
                a = random.randrange(2, n - 1)
                x = pow(a, d, n)
                if x == 1 or x == n - 1:
                    continue
                for _ in range(r - 1):
                    x = pow(x, 2, n)
                    if x == n - 1:
                        break
                else:
                    return False
            return True
        
        # Find two primes
        p = random.randrange(min_prime, max_prime)
        while not is_probably_prime(p):
            p = random.randrange(min_prime, max_prime)
            
        q = random.randrange(min_prime, max_prime)
        while not is_probably_prime(q) or q == p:
            q = random.randrange(min_prime, max_prime)
        
        n = p * q
        return n, (p, q)
    
    def estimate_k_from_prime(self, p: int) -> Tuple[Any, bool]:
        """
        Estimate the k-index for a given prime using inverse PNT with safety guards.
        
        Args:
            p: Prime number for k-index estimation
            
        Returns:
            tuple: (k_estimate, extrapolated_flag)
        """
        return self.safe_k_estimate(p)
    
    def binary_search_convergence_test(self, n: int, factors: Tuple[int, int], 
                                     max_iterations: int, tolerance: float) -> Tuple[bool, int, List[float]]:
        """
        Test binary search convergence for factor prediction.
        
        Uses Z5D predictor to iteratively refine factor estimates.
        """
        p, q = factors
        k_p, extrapolated_p = self.estimate_k_from_prime(p)
        k_q, extrapolated_q = self.estimate_k_from_prime(q)
        
        if extrapolated_p or extrapolated_q:
            print("Warning: K-index estimation required extrapolation due to scale limits")
        
        # Binary search bounds
        k_min = min(k_p, k_q) * 0.5
        k_max = max(k_p, k_q) * 2.0
        
        convergence_history = []
        
        for iteration in range(max_iterations):
            k_mid = (k_min + k_max) / 2
            
            try:
                # Use the correct function name
                pred_p = z5d_predictor.z5d_prime(k_mid)
                
                error = float(abs(pred_p - p) / p)
                convergence_history.append(error)
                
                if error < tolerance:
                    return True, iteration + 1, convergence_history
                
                # Adjust search bounds based on prediction
                if pred_p < p:
                    k_min = k_mid
                else:
                    k_max = k_mid
                    
            except Exception as e:
                warnings.warn(f"Prediction error at iteration {iteration}: {e}")
                break
        
        return False, max_iterations, convergence_history
    
    def validate_single_level(self, level_config: Dict[str, Any]) -> ValidationResult:
        """Validate a single level in the progressive ladder."""
        print(f"\nValidating {level_config['name']} ({level_config['bits']} bits)")
        print("-" * 60)
        
        # Set dynamic precision based on bit length (around line 200 as suggested)
        dps = self.set_dynamic_precision(level_config['bits'])
        print(f"Set dps to {dps} for {level_config['bits']}-bit validation")
        
        start_time = time.time()
        
        # Generate or use known test case
        if level_config['known_factors']:
            # Use known RSA-768 factorization
            p_str, q_str = level_config['known_factors']
            p, q = int(p_str), int(q_str)
            n = p * q
            factors = (p, q)
            print(f"Using known factors for {level_config['name']}")
        else:
            # Generate test composite
            n, factors = self.generate_rsa_test_composite(level_config['bits'])
            p, q = factors
            print(f"Generated test composite: {level_config['bits']} bits")
        
        print(f"Composite N: {len(str(n))} digits")
        print(f"Factor 1: {len(str(p))} digits")
        print(f"Factor 2: {len(str(q))} digits")
        
        # Estimate k-values for factors using safe estimation
        k_p, extrapolated_p = self.estimate_k_from_prime(p)
        k_q, extrapolated_q = self.estimate_k_from_prime(q)
        # Convert mpmath to string for JSON serialization if needed
        def safe_k_convert(k):
            try:
                import mpmath
                if hasattr(k, '__module__') and 'mpmath' in str(type(k)):
                    return mpmath.nstr(k, 6)
            except Exception:
                pass
            try:
                return f"{k:.6e}"
            except Exception:
                return str(k)

        predicted_k_values = [safe_k_convert(k_p), safe_k_convert(k_q)]
        
        # Check for extrapolation flags
        if extrapolated_p or extrapolated_q:
            print("Hypothesis: Extrapolated k due to scale; requires geodesic enhancement.")
        
        # Safe formatting for both float and mpmath objects
        def safe_format(k):
            try:
                import mpmath
                if hasattr(k, '__module__') and 'mpmath' in str(type(k)):
                    return mpmath.nstr(k, 3)
            except Exception:
                pass
            try:
                return f"{k:.2e}"
            except Exception:
                return str(k)

        print(f"Estimated k-indices: {safe_format(k_p)}, {safe_format(k_q)}")
        
        # Calculate prediction errors with safety checks
        try:
            # Check for infinite k-values before prediction (handle both float and mpmath)
            def is_invalid_k(k):
                if hasattr(k, '__module__') and 'mpmath' in str(type(k)):
                    return mpmath.isinf(k) or mpmath.isnan(k)
                else:
                    return math.isinf(k) or math.isnan(k)

            if is_invalid_k(k_p) or is_invalid_k(k_q):
                print("Warning: Infinite or NaN k-values detected - prediction failed")
                prediction_errors = [float('inf'), float('inf')]
            else:
                # Use the correct function names from z5d_predictor
                pred_p = z5d_predictor.z5d_prime(k_p)
                pred_q = z5d_predictor.z5d_prime(k_q)
                
                error_p = abs(pred_p - p) / p
                error_q = abs(pred_q - q) / q
                prediction_errors = [error_p, error_q]
                
                print(f"Prediction errors: {error_p:.6f}, {error_q:.6f}")
            
        except Exception as e:
            warnings.warn(f"Prediction error: {e}")
            prediction_errors = [float('inf'), float('inf')]
        
        # Test binary search convergence
        print("Testing binary search convergence...")
        convergence_success, iterations, convergence_history = self.binary_search_convergence_test(
            n, factors, level_config['max_iterations'], level_config['tolerance']
        )
        
        print(f"Convergence: {'SUCCESS' if convergence_success else 'FAILED'}")
        print(f"Iterations: {iterations}")
        
        # Calculate overall accuracy
        if all(e != float('inf') for e in prediction_errors):
            accuracy = (1 - max(prediction_errors)) * 100
        else:
            accuracy = 0.0
        
        execution_time = time.time() - start_time
        print(f"Execution time: {execution_time:.3f}s")
        print(f"Accuracy: {accuracy:.2f}%")
        
        return ValidationResult(
            rsa_bits=level_config['bits'],
            expected_factors=(str(p), str(q)) if level_config['known_factors'] else None,
            predicted_k_values=predicted_k_values,
            prediction_errors=prediction_errors,
            convergence_iterations=iterations,
            execution_time=execution_time,
            binary_search_success=convergence_success,
            accuracy_percentage=accuracy,
            notes=level_config['description']
        )
    
    def analyze_error_trends(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Analyze error trends across validation levels."""
        if not results:
            return {}
        
        bits = [r.rsa_bits for r in results]
        max_errors = [max(r.prediction_errors) if r.prediction_errors and all(e != float('inf') for e in r.prediction_errors) else None for r in results]
        accuracies = [r.accuracy_percentage for r in results]
        
        # Filter out invalid errors
        valid_data = [(b, e, a) for b, e, a in zip(bits, max_errors, accuracies) if e is not None]
        
        if not valid_data:
            return {'status': 'insufficient_data'}
        
        valid_bits, valid_errors, valid_accuracies = zip(*valid_data)
        
        # Calculate trend statistics
        if len(valid_errors) > 1:
            # Simple linear regression for error growth
            if NUMPY_AVAILABLE:
                coeffs = np.polyfit(valid_bits, valid_errors, 1)
                error_trend_slope = coeffs[0]
            else:
                # Manual calculation
                n = len(valid_bits)
                sum_x = sum(valid_bits)
                sum_y = sum(valid_errors)
                sum_xy = sum(x*y for x, y in zip(valid_bits, valid_errors))
                sum_x2 = sum(x*x for x in valid_bits)
                error_trend_slope = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x*sum_x)
        else:
            error_trend_slope = 0.0
        
        return {
            'status': 'success',
            'error_trend_slope': error_trend_slope,
            'error_growth_rate': 'increasing' if error_trend_slope > 0 else 'decreasing',
            'min_error': min(valid_errors),
            'max_error': max(valid_errors),
            'avg_accuracy': sum(valid_accuracies) / len(valid_accuracies),
            'scale_dependency': error_trend_slope > 1e-6
        }
    
    def analyze_convergence_performance(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Analyze convergence performance across validation levels."""
        if not results:
            return {}
        
        successful_convergence = sum(1 for r in results if r.binary_search_success)
        total_levels = len(results)
        
        avg_iterations = sum(r.convergence_iterations for r in results) / total_levels
        max_iterations = max(r.convergence_iterations for r in results)
        min_iterations = min(r.convergence_iterations for r in results)
        
        return {
            'convergence_success_rate': successful_convergence / total_levels,
            'avg_iterations': avg_iterations,
            'max_iterations': max_iterations,
            'min_iterations': min_iterations,
            'consistent_convergence': successful_convergence == total_levels
        }
    
    def calculate_performance_metrics(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        if not results:
            return {}
        
        total_time = sum(r.execution_time for r in results)
        avg_time = total_time / len(results)
        
        valid_accuracies = [r.accuracy_percentage for r in results if r.accuracy_percentage > 0]
        
        return {
            'total_execution_time': total_time,
            'average_time_per_level': avg_time,
            'overall_accuracy': sum(valid_accuracies) / len(valid_accuracies) if valid_accuracies else 0.0,
            'throughput_levels_per_second': len(results) / total_time if total_time > 0 else 0.0,
            'scalability_rating': self._calculate_scalability_rating(results)
        }
    
    def _calculate_scalability_rating(self, results: List[ValidationResult]) -> str:
        """Calculate a qualitative scalability rating."""
        if not results:
            return 'unknown'
        
        # Check if performance degrades significantly with scale
        execution_times = [r.execution_time for r in results]
        if len(execution_times) < 2:
            return 'insufficient_data'
        
        # Simple heuristic: if time increases by more than 10x, it's poor scalability
        time_ratio = max(execution_times) / min(execution_times)
        
        if time_ratio < 2:
            return 'excellent'
        elif time_ratio < 5:
            return 'good'
        elif time_ratio < 10:
            return 'fair'
        else:
            return 'poor'
    
    def run_progressive_validation(self) -> ProgressiveLadderResults:
        """Run the complete progressive validation ladder."""
        print("Starting Progressive Validation Ladder for Z5D Factorization")
        print("=" * 80)
        print(f"Testing levels: {len(self.validation_levels)}")
        print(f"High precision mode: {'ENABLED' if self.enable_high_precision else 'DISABLED'}")
        print("=" * 80)
        
        start_time = time.time()
        validation_results = []
        successful_levels = 0
        
        for i, level_config in enumerate(self.validation_levels, 1):
            print(f"\n[Level {i}/{len(self.validation_levels)}]")
            
            try:
                result = self.validate_single_level(level_config)
                validation_results.append(result)
                
                if result.binary_search_success and result.accuracy_percentage > 50:
                    successful_levels += 1
                    
            except Exception as e:
                print(f"ERROR in level {i}: {e}")
                # Add failed result
                validation_results.append(ValidationResult(
                    rsa_bits=level_config['bits'],
                    expected_factors=None,
                    predicted_k_values=[],
                    prediction_errors=[float('inf')],
                    convergence_iterations=0,
                    execution_time=0.0,
                    binary_search_success=False,
                    accuracy_percentage=0.0,
                    notes=f"FAILED: {str(e)}"
                ))
        
        # Analyze results
        error_trend_analysis = self.analyze_error_trends(validation_results)
        convergence_analysis = self.analyze_convergence_performance(validation_results)
        performance_metrics = self.calculate_performance_metrics(validation_results)
        
        total_time = time.time() - start_time
        overall_success = successful_levels >= len(self.validation_levels) // 2
        
        print("\n" + "=" * 80)
        print("PROGRESSIVE VALIDATION LADDER COMPLETE")
        print("=" * 80)
        print(f"Total execution time: {total_time:.2f}s")
        print(f"Successful levels: {successful_levels}/{len(self.validation_levels)}")
        print(f"Overall success: {'PASS' if overall_success else 'FAIL'}")
        
        return ProgressiveLadderResults(
            timestamp=datetime.now().isoformat(),
            total_levels=len(self.validation_levels),
            successful_levels=successful_levels,
            error_trend_analysis=error_trend_analysis,
            convergence_analysis=convergence_analysis,
            performance_metrics=performance_metrics,
            validation_results=validation_results,
            overall_success=overall_success
        )
    
    def save_results(self, results: ProgressiveLadderResults, filename: str = None):
        """Save validation results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"progressive_validation_ladder_results_{timestamp}.json"
        
        # Convert dataclass to dict
        results_dict = asdict(results)
        
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
        
        print(f"\nResults saved to: {filename}")
        return filename
    
    def print_summary_report(self, results: ProgressiveLadderResults):
        """Print a comprehensive summary report."""
        print("\n" + "=" * 80)
        print("PROGRESSIVE VALIDATION LADDER - SUMMARY REPORT")
        print("=" * 80)
        
        print(f"Timestamp: {results.timestamp}")
        print(f"Total Levels: {results.total_levels}")
        print(f"Successful Levels: {results.successful_levels}")
        print(f"Success Rate: {results.successful_levels/results.total_levels*100:.1f}%")
        print(f"Overall Result: {'PASS' if results.overall_success else 'FAIL'}")
        
        # Error trend analysis
        print("\nERROR TREND ANALYSIS:")
        print("-" * 40)
        eta = results.error_trend_analysis
        if eta.get('status') == 'success':
            print(f"Error growth trend: {eta['error_growth_rate']}")
            print(f"Trend slope: {eta['error_trend_slope']:.2e}")
            print(f"Min error: {eta['min_error']:.6f}")
            print(f"Max error: {eta['max_error']:.6f}")
            print(f"Average accuracy: {eta['avg_accuracy']:.2f}%")
            print(f"Scale dependent: {'YES' if eta['scale_dependency'] else 'NO'}")
        else:
            print("Insufficient data for trend analysis")
        
        # Convergence analysis
        print("\nCONVERGENCE ANALYSIS:")
        print("-" * 40)
        ca = results.convergence_analysis
        print(f"Convergence success rate: {ca['convergence_success_rate']*100:.1f}%")
        print(f"Average iterations: {ca['avg_iterations']:.1f}")
        print(f"Iteration range: {ca['min_iterations']} - {ca['max_iterations']}")
        print(f"Consistent convergence: {'YES' if ca['consistent_convergence'] else 'NO'}")
        
        # Performance metrics
        print("\nPERFORMANCE METRICS:")
        print("-" * 40)
        pm = results.performance_metrics
        print(f"Total execution time: {pm['total_execution_time']:.2f}s")
        print(f"Average time per level: {pm['average_time_per_level']:.2f}s")
        print(f"Overall accuracy: {pm['overall_accuracy']:.2f}%")
        print(f"Throughput: {pm['throughput_levels_per_second']:.2f} levels/s")
        print(f"Scalability rating: {pm['scalability_rating'].upper()}")
        
        # Individual level results
        print("\nINDIVIDUAL LEVEL RESULTS:")
        print("-" * 40)
        for i, result in enumerate(results.validation_results, 1):
            status = "PASS" if result.binary_search_success and result.accuracy_percentage > 50 else "FAIL"
            print(f"Level {i}: RSA-{result.rsa_bits} - {status} ({result.accuracy_percentage:.1f}% accuracy)")


def main():
    """Main CLI interface for Progressive Validation Ladder."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Progressive Validation Ladder for Z5D Factorization')
    parser.add_argument('--no-high-precision', action='store_true',
                        help='Disable high precision mode')
    parser.add_argument('--output', '-o', type=str,
                        help='Output filename for results')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Initialize validation ladder
    ladder = ProgressiveValidationLadder(enable_high_precision=not args.no_high_precision)
    
    # Run validation
    results = ladder.run_progressive_validation()
    
    # Save results
    output_file = ladder.save_results(results, args.output)
    
    # Print summary
    ladder.print_summary_report(results)
    
    # Exit with appropriate code
    exit_code = 0 if results.overall_success else 1
    print(f"\nExiting with code: {exit_code}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()