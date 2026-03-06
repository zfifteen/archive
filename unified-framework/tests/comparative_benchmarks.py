#!/usr/bin/env python3
"""
Comparative Benchmarks for Hybrid Prime Identification
=====================================================

Comprehensive benchmark comparing Z Framework hybrid prime identification
against best known methods for k-th prime identification in range 10^1 to 10^5.

Methods compared:
1. Z Framework Hybrid (Enhanced) - Our implementation with rigorous bounds + Miller-Rabin
2. Sieve of Eratosthenes - Classical optimal sieve method
3. Trial Division - Simple primality testing approach  
4. PNT Approximation + Refinement - Prime Number Theorem with binary search
5. Miller-Rabin Standard - Probabilistic primality testing
6. Segmented Sieve - Memory-efficient sieve for large ranges

Metrics measured:
- Execution time
- Memory usage (approximate)
- Accuracy (should be 100% for all)
- Computational efficiency (operations per second)
"""

import sys
import os
import time
import math
import tracemalloc
from typing import Dict, List, Tuple, Optional

# Optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Fallback statistics functions
    def mean(values):
        return sum(values) / len(values) if values else 0

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.hybrid_prime_identification import (
    hybrid_prime_identification,
    miller_rabin_deterministic,
    is_prime_optimized
)

# Import sympy for reference verification
try:
    from sympy import sieve, isprime, nextprime
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("Warning: sympy not available, some reference methods disabled")


class PrimeBenchmark:
    """Comprehensive benchmark suite for k-th prime identification methods"""
    
    def __init__(self):
        self.results = {
            'z_framework_hybrid': [],
            'sieve_eratosthenes': [],
            'trial_division': [],
            'pnt_approximation': [],
            'miller_rabin_standard': [],
            'segmented_sieve': [],
            'sympy_reference': []
        }
        
        # Known k-th primes for validation
        self.known_primes = {
            10: 29, 25: 97, 50: 229, 100: 541, 250: 1597, 500: 3571,
            1000: 7919, 2500: 22307, 5000: 48611, 10000: 104729,
            25000: 287117, 50000: 611953, 100000: 1299709
        }
    
    def measure_performance(self, func, *args, **kwargs) -> Dict:
        """Measure execution time and memory usage of a function"""
        # Start memory tracking
        tracemalloc.start()
        
        # Memory measurement (if available)
        mem_before = 0
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Time execution
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        end_time = time.perf_counter()
        
        # Memory after
        mem_after = mem_before
        if PSUTIL_AVAILABLE:
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'result': result,
            'success': success,
            'error': error,
            'time': end_time - start_time,
            'memory_used': mem_after - mem_before,
            'peak_memory': peak / 1024 / 1024  # MB
        }
    
    def z_framework_hybrid_method(self, k: int) -> int:
        """Z Framework enhanced hybrid method"""
        result = hybrid_prime_identification(
            k,
            use_rigorous_bounds=True,
            bounds_type="auto", 
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=min(100000, max(1000, k * 10))
        )
        return result['predicted_prime']
    
    def sieve_eratosthenes_method(self, k: int) -> int:
        """Classical Sieve of Eratosthenes (memory-safe)"""
        if k <= 0:
            return None
            
        # Memory safety check
        if k > 10000:
            raise ValueError(f"k={k} too large for memory-safe sieve (max 10000)")
            
        # Estimate upper bound using PNT with safety margin
        if k < 6:
            limit = 15
        else:
            # Improved bounds for small k
            ln_k = math.log(k)
            if k >= 688383:
                limit = int(k * (ln_k + math.log(ln_k) - 1 + 1.8 * math.log(ln_k) / ln_k))
            else:
                limit = int(k * (ln_k + math.log(ln_k)) * 1.3)
            
            # Additional memory safety limit
            limit = min(limit, 200000)  # Cap at 200k to prevent memory issues
        
        # Generate primes using sieve
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        
        for i in range(2, int(math.sqrt(limit)) + 1):
            if sieve[i]:
                for j in range(i * i, limit + 1, i):
                    sieve[j] = False
        
        # Collect primes until we have k
        primes = []
        for i in range(2, limit + 1):
            if sieve[i]:
                primes.append(i)
                if len(primes) == k:
                    return primes[-1]
        
        # If we didn't find enough primes, expand the search
        raise ValueError(f"Sieve limit {limit} insufficient for k={k}")
    
    def trial_division_method(self, k: int) -> int:
        """Simple trial division approach"""
        if k <= 0:
            return None
        
        primes_found = 0
        candidate = 2
        
        while primes_found < k:
            if self.is_prime_trial_division(candidate):
                primes_found += 1
                if primes_found == k:
                    return candidate
            candidate += 1
        
        return None
    
    def is_prime_trial_division(self, n: int) -> bool:
        """Check if number is prime using trial division"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def pnt_approximation_method(self, k: int) -> int:
        """Prime Number Theorem approximation with binary search refinement"""
        if k <= 0:
            return None
        
        # Initial approximation using PNT
        if k < 6:
            estimates = [2, 3, 5, 7, 11]
            return estimates[k-1] if k <= len(estimates) else None
        
        ln_k = math.log(k)
        if k >= 688383:
            # More accurate bound for large k
            approx = k * (ln_k + math.log(ln_k) - 1 + 1.2 * math.log(ln_k) / ln_k)
        else:
            approx = k * (ln_k + math.log(ln_k) - 1)
        
        # Binary search around approximation
        lower = max(2, int(approx * 0.8))
        upper = int(approx * 1.2)
        
        # Verify bounds contain k-th prime by counting
        while self.count_primes_up_to(lower) >= k:
            lower = int(lower * 0.9)
        while self.count_primes_up_to(upper) < k:
            upper = int(upper * 1.1)
        
        # Binary search for exact k-th prime
        while lower < upper:
            mid = (lower + upper) // 2
            count = self.count_primes_up_to(mid)
            
            if count < k:
                lower = mid + 1
            else:
                upper = mid
        
        # Find the exact k-th prime around this point
        candidate = lower
        count = self.count_primes_up_to(candidate - 1)
        
        while count < k:
            if self.is_prime_trial_division(candidate):
                count += 1
                if count == k:
                    return candidate
            candidate += 1
        
        return candidate
    
    def count_primes_up_to(self, n: int) -> int:
        """Count primes up to n using trial division (for small ranges)"""
        if n < 2:
            return 0
        
        count = 0
        for i in range(2, n + 1):
            if self.is_prime_trial_division(i):
                count += 1
        return count
    
    def miller_rabin_standard_method(self, k: int) -> int:
        """Standard Miller-Rabin probabilistic method"""
        if k <= 0:
            return None
        
        primes_found = 0
        candidate = 2
        
        while primes_found < k:
            if self.miller_rabin_probabilistic(candidate):
                primes_found += 1
                if primes_found == k:
                    return candidate
            candidate += 1
        
        return None
    
    def miller_rabin_probabilistic(self, n: int, rounds: int = 10) -> bool:
        """Probabilistic Miller-Rabin primality test"""
        if n < 2:
            return False
        if n in [2, 3]:
            return True
        if n % 2 == 0:
            return False
        
        # Write n-1 as d * 2^r
        r = 0
        d = n - 1
        while d % 2 == 0:
            d //= 2
            r += 1
        
        # Perform rounds of testing
        for _ in range(rounds):
            a = 2 + (hash(str(n) + str(_)) % (n - 4))  # Deterministic "random"
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
    
    def segmented_sieve_method(self, k: int) -> int:
        """Segmented sieve for memory efficiency"""
        if k <= 0:
            return None
        
        # For small k, use simple sieve
        if k <= 1000:
            return self.sieve_eratosthenes_method(k)
        
        # Estimate limit
        ln_k = math.log(k)
        limit = int(k * (ln_k + math.log(ln_k)) * 1.2)
        
        # First, find all primes up to sqrt(limit) for segment sieving
        sqrt_limit = int(math.sqrt(limit)) + 1
        base_sieve = [True] * sqrt_limit
        base_sieve[0] = base_sieve[1] = False
        
        for i in range(2, int(math.sqrt(sqrt_limit)) + 1):
            if base_sieve[i]:
                for j in range(i * i, sqrt_limit, i):
                    base_sieve[j] = False
        
        base_primes = [i for i in range(2, sqrt_limit) if base_sieve[i]]
        
        # Segmented sieving
        segment_size = min(100000, limit // 10)
        primes_found = 0
        primes = []
        
        for low in range(2, limit + 1, segment_size):
            high = min(low + segment_size - 1, limit)
            segment = [True] * (high - low + 1)
            
            # Sieve current segment
            for p in base_primes:
                if p * p > high:
                    break
                
                # Find first multiple of p in segment
                start = max(p * p, (low + p - 1) // p * p)
                
                for j in range(start, high + 1, p):
                    segment[j - low] = False
            
            # Collect primes from segment
            for i in range(len(segment)):
                if segment[i] and (low + i) >= 2:
                    primes.append(low + i)
                    primes_found += 1
                    if primes_found == k:
                        return primes[-1]
        
        raise ValueError(f"Could not find {k}-th prime with limit {limit}")
    
    def sympy_reference_method(self, k: int) -> int:
        """SymPy reference implementation"""
        if not SYMPY_AVAILABLE:
            return None
        
        # Extend sieve if necessary
        if k > len(sieve):
            # Estimate upper bound
            ln_k = math.log(k) if k > 1 else 1
            limit = int(k * (ln_k + math.log(ln_k)) * 1.3) if k >= 6 else 30
            sieve.extend_to_no(k)
        
        return sieve[k - 1]  # 0-indexed
    
    def run_benchmark_for_k(self, k: int) -> Dict:
        """Run all methods for a specific k value"""
        print(f"\nBenchmarking k={k} (expected: {self.known_primes.get(k, 'unknown')})")
        
        methods = [
            ('z_framework_hybrid', self.z_framework_hybrid_method),
            ('sieve_eratosthenes', self.sieve_eratosthenes_method),
            ('trial_division', self.trial_division_method),
            ('pnt_approximation', self.pnt_approximation_method),
            ('miller_rabin_standard', self.miller_rabin_standard_method),
            ('segmented_sieve', self.segmented_sieve_method),
        ]
        
        if SYMPY_AVAILABLE:
            methods.append(('sympy_reference', self.sympy_reference_method))
        
        results = {}
        
        for method_name, method_func in methods:
            print(f"  Testing {method_name}...", end=" ")
            
            # Skip slow/memory-intensive methods for large k to prevent system hangs
            if k > 2000 and method_name in ['trial_division']:
                print("SKIPPED (too slow)")
                results[method_name] = {
                    'result': None, 'success': False, 'time': float('inf'),
                    'memory_used': 0, 'peak_memory': 0, 'error': 'Skipped for performance'
                }
                continue
            
            if k > 5000 and method_name in ['pnt_approximation']:
                print("SKIPPED (too slow)")
                results[method_name] = {
                    'result': None, 'success': False, 'time': float('inf'),
                    'memory_used': 0, 'peak_memory': 0, 'error': 'Skipped for performance'
                }
                continue
                
            if k > 10000 and method_name in ['sieve_eratosthenes', 'segmented_sieve']:
                print("SKIPPED (memory intensive)")
                results[method_name] = {
                    'result': None, 'success': False, 'time': float('inf'),
                    'memory_used': 0, 'peak_memory': 0, 'error': 'Skipped for memory safety'
                }
                continue
            
            perf = self.measure_performance(method_func, k)
            results[method_name] = perf
            
            if perf['success']:
                expected = self.known_primes.get(k, perf['result'])
                correct = perf['result'] == expected
                status = "✅" if correct else f"❌ (got {perf['result']}, expected {expected})"
                print(f"{status} {perf['time']:.3f}s")
            else:
                print(f"❌ ERROR: {perf['error']}")
        
        return results
    
    def run_full_benchmark(self, k_values: List[int] = None) -> Dict:
        """Run comprehensive benchmark across k values"""
        if k_values is None:
            # Memory-safe default test range: focus on smaller k values to prevent system hangs
            k_values = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
        
        print("Comparative Benchmark: K-th Prime Identification")
        print("=" * 60)
        print("Testing range: 10^1 to 10^4 (memory-safe defaults)")
        print("Methods: Z Framework Hybrid, Sieve of Eratosthenes, Trial Division,")
        print("         PNT Approximation, Miller-Rabin, Segmented Sieve, SymPy Reference")
        print("Note: Use custom k_values for larger ranges or run fast_comparative_benchmark.py")
        
        all_results = {}
        
        for k in k_values:
            if k in self.known_primes:
                all_results[k] = self.run_benchmark_for_k(k)
        
        # Generate summary
        self.generate_summary(all_results)
        
        return all_results
    
    def generate_summary(self, results: Dict):
        """Generate benchmark summary and analysis"""
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        
        # Collect data for analysis
        methods = set()
        for k_results in results.values():
            methods.update(k_results.keys())
        
        methods = sorted(methods)
        
        # Performance summary table
        print(f"\n{'Method':<25} {'Avg Time (s)':<15} {'Success Rate':<15} {'Avg Memory (MB)':<15}")
        print("-" * 70)
        
        for method in methods:
            times = []
            successes = 0
            total = 0
            memories = []
            
            for k, k_results in results.items():
                if method in k_results:
                    result = k_results[method]
                    total += 1
                    if result['success']:
                        successes += 1
                        times.append(result['time'])
                        memories.append(result['peak_memory'])
            
            avg_time = mean(times) if times else float('inf')
            success_rate = successes / total if total > 0 else 0
            avg_memory = mean(memories) if memories else 0
            
            print(f"{method:<25} {avg_time:<15.4f} {success_rate:<15.1%} {avg_memory:<15.2f}")
        
        # Detailed performance by k value
        print(f"\nDetailed Results by K Value:")
        print(f"{'K':<8}", end="")
        for method in methods:
            print(f"{method[:12]:<15}", end="")
        print()
        print("-" * (8 + 15 * len(methods)))
        
        for k in sorted(results.keys()):
            print(f"{k:<8}", end="")
            for method in methods:
                if method in results[k]:
                    result = results[k][method]
                    if result['success']:
                        print(f"{result['time']:<15.3f}", end="")
                    else:
                        print(f"{'FAILED':<15}", end="")
                else:
                    print(f"{'N/A':<15}", end="")
            print()
        
        # Performance ranking
        print(f"\nPerformance Ranking (by average time):")
        avg_times = []
        for method in methods:
            times = []
            for k_results in results.values():
                if method in k_results and k_results[method]['success']:
                    times.append(k_results[method]['time'])
            
            if times:
                avg_times.append((method, mean(times)))
        
        avg_times.sort(key=lambda x: x[1])
        
        for i, (method, avg_time) in enumerate(avg_times, 1):
            print(f"{i}. {method}: {avg_time:.4f}s average")
        
        # Accuracy verification
        print(f"\nAccuracy Verification:")
        all_accurate = True
        for k, k_results in results.items():
            expected = self.known_primes.get(k)
            if expected:
                print(f"K={k} (expected: {expected})")
                for method, result in k_results.items():
                    if result['success']:
                        correct = result['result'] == expected
                        status = "✅" if correct else "❌"
                        print(f"  {method}: {result['result']} {status}")
                        if not correct:
                            all_accurate = False
        
        print(f"\nOverall Accuracy: {'✅ All methods accurate' if all_accurate else '❌ Some inaccuracies detected'}")


def main():
    """Run the comparative benchmark"""
    benchmark = PrimeBenchmark()
    
    # Memory-safe test subset to prevent system hangs
    quick_test_k = [10, 100, 500, 1000]  # Reduced max k to prevent memory issues
    print("Running memory-safe validation test...")
    print("Note: For larger k values or full benchmarks, use fast_comparative_benchmark.py")
    results = benchmark.run_full_benchmark(quick_test_k)
    
    # Optional: Run full benchmark (requires sufficient memory)
    # print("\nRunning full benchmark (WARNING: memory intensive)...")
    # full_results = benchmark.run_full_benchmark()
    
    return results


if __name__ == "__main__":
    main()