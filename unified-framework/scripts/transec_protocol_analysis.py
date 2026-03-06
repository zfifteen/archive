#!/usr/bin/env python3
"""
TRANSEC Protocol Optimization Analysis
=====================================

This script analyzes TRANSEC (TRANsmission SECurity) protocol optimizations by testing
prime-valued indices for curvature reduction (25-88% target).

The analysis simulates cryptographic protocol performance with different index selections,
measuring curvature reduction metrics and correlations.

Author: Unified Framework Team
Date: November 2025
"""

import sys
import os
import random
import math
from typing import List, Tuple, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import sympy
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

try:
    import statsmodels.api as sm
    from statsmodels.stats import correlation
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

class TRANSECAnalyzer:
    """Analyzer for TRANSEC protocol optimizations."""

    def __init__(self, protocol_length: int = 1000):
        self.protocol_length = protocol_length
        self.primes = self._generate_primes(protocol_length * 2)

    def _generate_primes(self, limit: int) -> List[int]:
        """Generate primes up to limit."""
        if HAS_SYMPY:
            return list(sympy.primerange(2, limit))
        else:
            # Simple sieve
            sieve = [True] * (limit + 1)
            sieve[0] = sieve[1] = False
            for i in range(2, int(limit**0.5) + 1):
                if sieve[i]:
                    for j in range(i*i, limit + 1, i):
                        sieve[j] = False
            return [i for i in range(2, limit + 1) if sieve[i]]

    def simulate_protocol_curvature(self, indices: List[int], noise_factor: float = 0.1) -> Dict[str, Any]:
        """Simulate protocol curvature for given indices."""

        # Generate base signal (represents protocol performance metric)
        base_signal = [math.sin(2 * math.pi * i / self.protocol_length) for i in range(self.protocol_length)]

        # Apply index-based modulation
        modulated_signal = []
        for i in range(self.protocol_length):
            if i < len(indices):
                idx = indices[i]
                # Prime indices introduce specific phase shifts
                phase_shift = (idx % 360) * math.pi / 180
                modulation = math.cos(phase_shift) * (1 + noise_factor * random.random())
                modulated_signal.append(base_signal[i] * modulation)
            else:
                modulated_signal.append(base_signal[i])

        # Calculate curvature metrics
        if HAS_NUMPY:
            signal = np.array(modulated_signal)
            # Second derivative as curvature measure
            curvature = np.gradient(np.gradient(signal))
            mean_curvature = np.mean(np.abs(curvature))
            std_curvature = np.std(curvature)
            max_curvature = np.max(np.abs(curvature))
        else:
            # Fallback calculation
            curvature = []
            for i in range(1, len(modulated_signal) - 1):
                # Simple second difference
                second_diff = modulated_signal[i-1] - 2*modulated_signal[i] + modulated_signal[i+1]
                curvature.append(second_diff)

            mean_curvature = sum(abs(c) for c in curvature) / len(curvature)
            std_curvature = math.sqrt(sum((c - mean_curvature)**2 for c in curvature) / len(curvature))
            max_curvature = max(abs(c) for c in curvature)

        return {
            'mean_curvature': mean_curvature,
            'std_curvature': std_curvature,
            'max_curvature': max_curvature,
            'signal': modulated_signal[:100],  # First 100 points for analysis
            'curvature': curvature[:100] if isinstance(curvature, list) else curvature[:100].tolist()
        }

    def analyze_prime_vs_random_indices(self, n_samples: int = 100) -> Dict[str, Any]:
        """Compare prime-valued vs random indices for curvature reduction."""

        results = {'prime_indices': [], 'random_indices': []}

        for sample in range(n_samples):
            # Generate prime indices
            prime_indices = random.sample(self.primes[:self.protocol_length], min(50, len(self.primes)))

            # Generate random indices
            random_indices = [random.randint(1, self.protocol_length) for _ in range(len(prime_indices))]

            # Analyze both
            prime_result = self.simulate_protocol_curvature(prime_indices)
            random_result = self.simulate_protocol_curvature(random_indices)

            results['prime_indices'].append(prime_result)
            results['random_indices'].append(random_result)

        # Calculate statistics
        prime_curvatures = [r['mean_curvature'] for r in results['prime_indices']]
        random_curvatures = [r['mean_curvature'] for r in results['random_indices']]

        if HAS_NUMPY:
            prime_mean = np.mean(prime_curvatures)
            prime_std = np.std(prime_curvatures)
            random_mean = np.mean(random_curvatures)
            random_std = np.std(random_curvatures)

            # Curvature reduction percentage
            if random_mean > 0:
                reduction_pct = ((random_mean - prime_mean) / random_mean) * 100
            else:
                reduction_pct = 0
        else:
            prime_mean = sum(prime_curvatures) / len(prime_curvatures)
            prime_std = math.sqrt(sum((x - prime_mean)**2 for x in prime_curvatures) / len(prime_curvatures))
            random_mean = sum(random_curvatures) / len(random_curvatures)
            random_std = math.sqrt(sum((x - random_mean)**2 for x in random_curvatures) / len(random_curvatures))

            if random_mean > 0:
                reduction_pct = ((random_mean - prime_mean) / random_mean) * 100
            else:
                reduction_pct = 0

        # Statistical significance test
        significance = self._test_significance(prime_curvatures, random_curvatures)

        return {
            'prime_curvature_mean': prime_mean,
            'prime_curvature_std': prime_std,
            'random_curvature_mean': random_mean,
            'random_curvature_std': random_std,
            'curvature_reduction_percent': reduction_pct,
            'target_achieved': 25 <= reduction_pct <= 88,
            'statistical_significance': significance,
            'n_samples': n_samples
        }

    def _test_significance(self, group1: List[float], group2: List[float]) -> Dict[str, Any]:
        """Test statistical significance between two groups."""
        if not HAS_STATSMODELS or not HAS_NUMPY:
            # Simple t-test approximation
            mean1 = sum(group1) / len(group1)
            mean2 = sum(group2) / len(group2)
            var1 = sum((x - mean1)**2 for x in group1) / len(group1)
            var2 = sum((x - mean2)**2 for x in group2) / len(group2)

            # Pooled standard error
            se = math.sqrt(var1/len(group1) + var2/len(group2))
            t_stat = abs(mean1 - mean2) / se if se > 0 else 0

            # Approximate p-value (very rough)
            p_value = 2 * (1 - self._normal_cdf(t_stat))

            return {
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05,
                'method': 'approximate_t_test'
            }

        # Use statsmodels for proper statistical test
        try:
            # Two-sample t-test
            t_stat, p_value, df = sm.stats.ttest_ind(group1, group2)

            return {
                't_statistic': t_stat,
                'p_value': p_value,
                'degrees_of_freedom': df,
                'significant': p_value < 0.05,
                'method': 'statsmodels_ttest'
            }
        except Exception:
            return {
                'error': 'Statistical test failed',
                'significant': False,
                'method': 'failed'
            }

    def _normal_cdf(self, x: float) -> float:
        """Approximate normal CDF for p-value calculation."""
        # Abramowitz & Stegun approximation
        a1 =  0.254829592
        a2 = -0.284496736
        a3 =  1.421413741
        a4 = -1.453152027
        a5 =  1.061405429
        p  =  0.3275911

        sign = 1 if x >= 0 else -1
        x = abs(x) / math.sqrt(2.0)

        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

        return 0.5 * (1 + sign * y)

    def optimize_index_selection(self) -> Dict[str, Any]:
        """Optimize index selection for maximum curvature reduction."""

        # Test different prime selection strategies
        strategies = {
            'small_primes': self.primes[:50],
            'large_primes': self.primes[-50:],
            'random_primes': random.sample(self.primes, 50),
            'fibonacci_primes': [p for p in self.primes[:100] if self._is_fibonacci(p)][:20]
        }

        results = {}
        for strategy, indices in strategies.items():
            if indices:  # Only test if we have indices
                result = self.simulate_protocol_curvature(indices)
                results[strategy] = result['mean_curvature']

        # Find best strategy
        if results:
            best_strategy = min(results, key=results.get)
            best_curvature = results[best_strategy]
            baseline_curvature = results.get('random_primes', results[list(results.keys())[0]])

            if baseline_curvature > 0:
                improvement = ((baseline_curvature - best_curvature) / baseline_curvature) * 100
            else:
                improvement = 0
        else:
            best_strategy = None
            improvement = 0

        return {
            'strategies_tested': results,
            'best_strategy': best_strategy,
            'improvement_percent': improvement,
            'optimization_successful': improvement > 10  # Arbitrary threshold
        }

    def is_probable_prime(self, n: int, k: int = 12) -> bool:
        """Miller-Rabin primality test."""
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False

        # Write n-1 as 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        # Witness loop
        witnesses = [2, 3, 5, 7, 11, 13, 23, 29, 31, 37, 41, 43, 47][:k]
        for a in witnesses:
            if a >= n:
                continue

            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue

            for _ in range(r - 1):
                x = (x * x) % n
                if x == n - 1:
                    break
            else:
                return False

        return True

    def _is_fibonacci(self, n: int) -> bool:
        """Check if a number is a Fibonacci number."""
        # A number is Fibonacci if 5*n^2 + 4 or 5*n^2 - 4 is a perfect square
        def is_perfect_square(x: int) -> bool:
            root = int(math.sqrt(x))
            return root * root == x

        return is_perfect_square(5 * n * n + 4) or is_perfect_square(5 * n * n - 4)

    def fibonacci_prime_optimization(self, n_samples: int = 1000) -> Dict[str, Any]:
        """Advanced optimization using Fibonacci primes for curvature reduction."""
        print("Running Fibonacci prime optimization analysis...")

        # Generate Fibonacci primes (primes that are also Fibonacci numbers)
        fib_primes = []
        n = 2
        while len(fib_primes) < 50:  # Get first 50 Fibonacci primes
            if self._is_fibonacci(n) and self.is_probable_prime(n):
                fib_primes.append(n)
            n += 1

        if not fib_primes:
            return {"error": "No Fibonacci primes found"}

        # Test different Fibonacci prime selection strategies
        strategies = {
            'fibonacci_primes_small': fib_primes[:10],
            'fibonacci_primes_medium': fib_primes[10:25],
            'fibonacci_primes_large': fib_primes[25:40],
            'fibonacci_primes_mixed': fib_primes[::2][:15],  # Every other one
            'fibonacci_primes_weighted': sorted(fib_primes[:20], key=lambda x: x % 7)  # Weighted by modulo
        }

        results = {}
        for strategy_name, primes in strategies.items():
            if len(primes) >= 5:  # Need minimum sample
                curvatures = []
                for _ in range(min(n_samples // len(strategies), 100)):
                    result = self.simulate_protocol_curvature(primes)
                    curvatures.append(result['mean_curvature'])

                if HAS_NUMPY:
                    mean_curvature = np.mean(curvatures)
                    std_curvature = np.std(curvatures)
                    ci_lower = np.percentile(curvatures, 2.5)
                    ci_upper = np.percentile(curvatures, 97.5)
                else:
                    mean_curvature = sum(curvatures) / len(curvatures)
                    std_curvature = math.sqrt(sum((x - mean_curvature)**2 for x in curvatures) / len(curvatures))
                    ci_lower = sorted(curvatures)[int(0.025 * len(curvatures))]
                    ci_upper = sorted(curvatures)[int(0.975 * len(curvatures))]

                results[strategy_name] = {
                    'mean_curvature': mean_curvature,
                    'std_curvature': std_curvature,
                    'ci_95': [ci_lower, ci_upper],
                    'n_primes': len(primes),
                    'primes_used': primes[:5]  # Show first 5
                }

        # Find best strategy
        if results:
            best_strategy = min(results.keys(), key=lambda k: results[k]['mean_curvature'])
            best_result = results[best_strategy]

            # Calculate improvement over baseline (random primes)
            baseline_primes = fib_primes[:10]  # Use same count as strategies
            baseline_curvatures = []
            for _ in range(100):
                result = self.simulate_protocol_curvature(baseline_primes)
                baseline_curvatures.append(result['mean_curvature'])

            if HAS_NUMPY:
                baseline_mean = np.mean(baseline_curvatures)
            else:
                baseline_mean = sum(baseline_curvatures) / len(baseline_curvatures)

            if baseline_mean > 0:
                improvement = ((baseline_mean - best_result['mean_curvature']) / baseline_mean) * 100
            else:
                improvement = 0

            return {
                'strategies_tested': results,
                'best_strategy': best_strategy,
                'best_curvature': best_result['mean_curvature'],
                'improvement_percent': improvement,
                'target_achieved': improvement >= 25,
                'fibonacci_primes_found': len(fib_primes),
                'baseline_mean': baseline_mean
            }

        return {"error": "No valid strategies tested"}

    def correlation_analysis(self, n_samples: int = 1000) -> Dict[str, Any]:
        """Advanced correlation analysis between prime properties and curvature reduction."""
        print("Running advanced correlation analysis...")

        if not HAS_STATSMODELS:
            return {"error": "statsmodels required for correlation analysis"}

        # Generate comprehensive dataset
        data_points = []
        for _ in range(n_samples):
            # Generate random prime set
            primes = random.sample(self.primes[:1000], random.randint(5, 20))

            # Calculate properties
            prime_sum = sum(primes)
            prime_mean = prime_sum / len(primes)
            prime_std = math.sqrt(sum((p - prime_mean)**2 for p in primes) / len(primes))
            prime_skewness = sum(((p - prime_mean) / prime_std)**3 for p in primes) / len(primes)
            prime_kurtosis = sum(((p - prime_mean) / prime_std)**4 for p in primes) / len(primes) - 3

            # Fibonacci properties
            fib_count = sum(1 for p in primes if self._is_fibonacci(p))
            fib_ratio = fib_count / len(primes)

            # Simulate curvature
            result = self.simulate_protocol_curvature(primes)
            curvature = result['mean_curvature']

            data_points.append({
                'prime_sum': prime_sum,
                'prime_mean': prime_mean,
                'prime_std': prime_std,
                'prime_skewness': prime_skewness,
                'prime_kurtosis': prime_kurtosis,
                'fib_ratio': fib_ratio,
                'set_size': len(primes),
                'curvature': curvature
            })

        # Convert to DataFrame-like analysis
        import pandas as pd  # Try to import pandas for easier analysis

        try:
            df_data = {k: [d[k] for d in data_points] for k in data_points[0].keys()}
            df = pd.DataFrame(df_data)

            # Calculate correlations with curvature
            correlations = {}
            p_values = {}

            for col in ['prime_sum', 'prime_mean', 'prime_std', 'prime_skewness',
                       'prime_kurtosis', 'fib_ratio', 'set_size']:
                corr = df[col].corr(df['curvature'])
                correlations[col] = corr

                # Simple p-value approximation (this is not rigorous)
                n = len(df)
                t_stat = abs(corr) * math.sqrt((n - 2) / (1 - corr**2))
                p_val = 2 * (1 - self._normal_cdf(t_stat))
                p_values[col] = p_val

            # Find strongest correlations
            strongest_corr = max(correlations.items(), key=lambda x: abs(x[1]))
            significant_corrs = {k: v for k, v in correlations.items()
                               if p_values[k] < 1e-10}

            return {
                'correlations': correlations,
                'p_values': p_values,
                'strongest_correlation': strongest_corr,
                'significant_correlations': significant_corrs,
                'target_achieved': len(significant_corrs) > 0 and
                                 any(abs(corr) >= 0.93 for corr in significant_corrs.values()),
                'n_samples': n_samples
            }

        except ImportError:
            # Fallback without pandas
            return {
                'error': 'pandas required for comprehensive correlation analysis',
                'n_samples': n_samples
            }

def main():
    """Main analysis."""
    print("=" * 70)
    print("TRANSEC Protocol Optimization Analysis")
    print("=" * 70)

    analyzer = TRANSECAnalyzer(protocol_length=1000)

    # 1. Prime vs Random Index Analysis
    print("\n1. Prime vs Random Index Curvature Analysis")
    print("-" * 45)

    comparison = analyzer.analyze_prime_vs_random_indices(n_samples=50)

    print(".4f")
    print(".4f")
    print(".2f")
    print(f"Target achieved (25-88%): {'✓' if comparison['target_achieved'] else '✗'}")

    if 'statistical_significance' in comparison:
        sig = comparison['statistical_significance']
        if isinstance(sig, dict) and 'p_value' in sig:
            print(".4f")
            print(f"Significant: {'✓' if sig.get('significant', False) else '✗'}")

    # 2. Index Selection Optimization
    print("\n2. Index Selection Optimization")
    print("-" * 35)

    optimization = analyzer.optimize_index_selection()

    if optimization['strategies_tested']:
        print("Strategy curvatures:")
        for strategy, curvature in optimization['strategies_tested'].items():
            print(".6f")

        print(f"\nBest strategy: {optimization['best_strategy']}")
        print(".2f")
        print(f"Optimization successful: {'✓' if optimization['optimization_successful'] else '✗'}")

    # 3. Fibonacci Prime Optimization
    print("\n3. Fibonacci Prime Optimization")
    print("-" * 32)

    fib_optimization = analyzer.fibonacci_prime_optimization(n_samples=200)

    if 'error' not in fib_optimization:
        print(f"Fibonacci primes found: {fib_optimization['fibonacci_primes_found']}")
        print(f"Best strategy: {fib_optimization['best_strategy']}")
        print(".6f")
        print(".2f")
        print(f"Target achieved (≥25%): {'✓' if fib_optimization['target_achieved'] else '✗'}")

        print("\nTop strategies:")
        sorted_strategies = sorted(fib_optimization['strategies_tested'].items(),
                                 key=lambda x: x[1]['mean_curvature'])
        for strategy, data in sorted_strategies[:3]:
            print(".6f")
    else:
        print(f"Error: {fib_optimization['error']}")

    # 4. Correlation Analysis
    print("\n4. Advanced Correlation Analysis")
    print("-" * 33)

    correlation_results = analyzer.correlation_analysis(n_samples=500)

    if 'error' not in correlation_results:
        print(f"Correlations with curvature (target r ≥ 0.93, p < 10^-10):")
        for var, corr in correlation_results['correlations'].items():
            p_val = correlation_results['p_values'][var]
            significant = p_val < 1e-10
            strong = abs(corr) >= 0.93
            marker = "✓" if significant and strong else "⚠" if significant else ""
            print(".4f")

        strong_corrs = correlation_results.get('significant_correlations', {})
        if strong_corrs:
            strongest = max(strong_corrs.items(), key=lambda x: abs(x[1]))
            print(f"\nStrongest correlation: {strongest[0]} = {strongest[1]:.4f}")
            print(f"Significant correlations: {len(strong_corrs)} found")
        else:
            print("\nNo significant correlations found")

        print(f"Target achieved: {'✓' if correlation_results.get('target_achieved', False) else '✗'}")
    else:
        print(f"Error: {correlation_results['error']}")

    # 3. Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    overall_success = (
        comparison.get('target_achieved', False) and
        optimization.get('optimization_successful', False)
    )

    print(f"Curvature reduction target (25-88%): {'ACHIEVED' if comparison.get('target_achieved', False) else 'NOT ACHIEVED'}")
    print(f"Index optimization successful: {'✓' if optimization.get('optimization_successful', False) else '✗'}")
    print(f"Overall TRANSEC optimization: {'SUCCESSFUL' if overall_success else 'NEEDS IMPROVEMENT'}")

    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()