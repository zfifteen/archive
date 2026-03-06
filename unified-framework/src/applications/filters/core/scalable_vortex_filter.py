#!/usr/bin/env python3
"""
Scalable Vortex Filter for N=10^6 with Performance Optimizations

This version implements optimizations for handling large datasets:
1. Efficient caching and batching
2. Prime sieve comparison for speedup validation
3. Parallel processing where possible
4. Memory-efficient chain computation
"""

import numpy as np
import time
import math
from typing import List, Tuple, Dict
from scipy import stats
from scipy.stats import kstest
from sympy import isprime
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.domain import DiscreteZetaShift

class OptimizedVortexFilter:
    """
    Memory-efficient vortex filter with caching and batching.
    """
    
    def __init__(self, chain_length: int = 15, batch_size: int = 100):
        self.chain_length = chain_length
        self.batch_size = batch_size
        self.chain_cache = {}
        
    def compute_chain_log_std_batch(self, numbers: List[int]) -> Dict[int, float]:
        """
        Compute std(log(chain)) for a batch of numbers efficiently.
        
        Args:
            numbers: List of numbers to process
            
        Returns:
            Dictionary mapping number to its std value
        """
        results = {}
        
        for n in numbers:
            if n in self.chain_cache:
                results[n] = self.chain_cache[n]
                continue
                
            try:
                # Generate chain of O values using unfold_next for efficiency
                zeta = DiscreteZetaShift(n)
                chain = [float(zeta.getO())]
                
                for _ in range(self.chain_length - 1):
                    zeta = zeta.unfold_next()
                    chain.append(float(zeta.getO()))
                
                # Compute log values with better handling
                log_chain = []
                for val in chain:
                    if abs(val) > 1e-10:  # Avoid log of near-zero
                        log_chain.append(np.log(abs(val)))
                    else:
                        log_chain.append(-10.0)  # Small constant for zeros
                
                std_val = float(np.std(log_chain)) if len(log_chain) > 1 else float('inf')
                
                self.chain_cache[n] = std_val
                results[n] = std_val
                
            except Exception as e:
                print(f"Error processing n={n}: {e}")
                results[n] = float('inf')
                
        return results
    
    def apply_filter_efficient(self, numbers: List[int], threshold: float) -> List[int]:
        """
        Apply vortex filter efficiently using batching.
        
        Args:
            numbers: List of numbers to filter
            threshold: Filter threshold θ
            
        Returns:
            List of numbers passing the filter
        """
        filtered = []
        
        # Process in batches for better memory management
        for i in range(0, len(numbers), self.batch_size):
            batch = numbers[i:i + self.batch_size]
            std_values = self.compute_chain_log_std_batch(batch)
            
            for n in batch:
                if std_values[n] <= threshold:
                    filtered.append(n)
                    
        return filtered


class FastPrimeSieve:
    """
    Optimized Sieve of Eratosthenes for performance comparison.
    """
    
    @staticmethod
    def sieve_of_eratosthenes(limit: int) -> List[int]:
        """
        Fast Sieve of Eratosthenes with optimizations.
        
        Args:
            limit: Upper limit for prime generation
            
        Returns:
            List of prime numbers up to limit
        """
        if limit < 2:
            return []
        
        # Use boolean array for efficiency
        sieve = np.ones(limit + 1, dtype=bool)
        sieve[0] = sieve[1] = False
        
        # Optimize loop bounds
        sqrt_limit = int(math.sqrt(limit)) + 1
        
        for i in range(2, sqrt_limit):
            if sieve[i]:
                # Start from i*i and step by i
                sieve[i*i:limit+1:i] = False
        
        return np.where(sieve)[0].tolist()
    
    @staticmethod
    def time_sieve(limit: int) -> Tuple[List[int], float]:
        """
        Time the sieve operation and return primes + time.
        
        Args:
            limit: Upper limit
            
        Returns:
            (primes_list, time_taken)
        """
        start_time = time.time()
        primes = FastPrimeSieve.sieve_of_eratosthenes(limit)
        end_time = time.time()
        return primes, end_time - start_time


class ScalableOptimizer:
    """
    Scalable optimizer for large datasets.
    """
    
    def __init__(self, vortex_filter: OptimizedVortexFilter):
        self.vortex_filter = vortex_filter
        
    def estimate_optimal_threshold(self, sample_numbers: List[int], 
                                 sample_primes: List[int]) -> float:
        """
        Estimate optimal threshold using a smaller sample.
        
        Args:
            sample_numbers: Sample of numbers to analyze
            sample_primes: Known primes in the sample
            
        Returns:
            Estimated optimal threshold
        """
        print("Estimating optimal threshold from sample...")
        
        # Compute std values for sample
        std_values = self.vortex_filter.compute_chain_log_std_batch(sample_numbers)
        
        # Separate primes and composites
        prime_stds = [std_values[n] for n in sample_numbers if n in sample_primes]
        composite_stds = [std_values[n] for n in sample_numbers if n not in sample_primes]
        
        if not prime_stds or not composite_stds:
            print("Warning: Insufficient primes or composites in sample")
            return 3.0  # Default fallback
        
        # Find threshold that separates distributions
        prime_mean = np.mean(prime_stds)
        composite_mean = np.mean(composite_stds)
        
        print(f"Prime mean std: {prime_mean:.4f}")
        print(f"Composite mean std: {composite_mean:.4f}")
        
        # Use a threshold between the means, closer to primes
        optimal_theta = prime_mean + 0.3 * (composite_mean - prime_mean)
        
        return optimal_theta
    
    def validate_performance(self, filtered_numbers: List[int], 
                           true_primes: List[int],
                           vortex_time: float, sieve_time: float) -> Dict:
        """
        Validate performance metrics.
        
        Args:
            filtered_numbers: Numbers that passed the filter
            true_primes: True prime numbers
            vortex_time: Time taken by vortex filter
            sieve_time: Time taken by sieve
            
        Returns:
            Performance metrics dictionary
        """
        # Basic accuracy metrics
        primes_found = [n for n in filtered_numbers if n in true_primes]
        composites_found = [n for n in filtered_numbers if n not in true_primes]
        
        precision = len(primes_found) / len(filtered_numbers) if filtered_numbers else 0.0
        recall = len(primes_found) / len(true_primes) if true_primes else 0.0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Error rate (ε92% approximation)
        error_rate = len(composites_found) / len(filtered_numbers) if filtered_numbers else 0.0
        
        # Speedup calculation
        speedup_factor = sieve_time / vortex_time if vortex_time > 0 else 0.0
        
        # KS test if possible
        ks_stat, p_value = 1.0, 1.0
        if len(filtered_numbers) > 10 and len(true_primes) > 10:
            try:
                # Normalize distributions for comparison
                filtered_norm = np.array(filtered_numbers, dtype=float)
                primes_norm = np.array(true_primes, dtype=float)
                
                # Convert to empirical CDFs
                filtered_norm = (filtered_norm - filtered_norm.min()) / (filtered_norm.max() - filtered_norm.min())
                primes_norm = (primes_norm - primes_norm.min()) / (primes_norm.max() - primes_norm.min())
                
                ks_stat, p_value = stats.ks_2samp(filtered_norm, primes_norm)
            except Exception as e:
                print(f"KS test failed: {e}")
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'error_rate': error_rate,
            'speedup_factor': speedup_factor,
            'ks_statistic': ks_stat,
            'ks_p_value': p_value,
            'primes_found': len(primes_found),
            'composites_found': len(composites_found),
            'total_filtered': len(filtered_numbers),
            'vortex_time': vortex_time,
            'sieve_time': sieve_time
        }


def main_scalable():
    """
    Main function for scalable vortex filter testing.
    """
    print("Scalable Vortex Filter for N=10^6")
    print("=" * 50)
    
    # Start with smaller test, then scale up
    test_sizes = [1000, 10000]  # Can add 100000, 1000000 for full test
    chain_length = 15
    
    for N in test_sizes:
        print(f"\nTesting with N={N}")
        print("-" * 30)
        
        # Initialize components
        vortex_filter = OptimizedVortexFilter(chain_length=chain_length, batch_size=50)
        optimizer = ScalableOptimizer(vortex_filter)
        
        # Generate test data
        print("Generating test data...")
        test_numbers = list(range(2, N + 1))
        
        # Get reference primes
        print("Computing reference primes with sieve...")
        true_primes, sieve_time = FastPrimeSieve.time_sieve(N)
        print(f"Found {len(true_primes)} primes in {sieve_time:.4f}s")
        
        # Use sample for threshold estimation
        sample_size = min(200, N // 10)
        sample_numbers = test_numbers[::max(1, len(test_numbers) // sample_size)][:sample_size]
        sample_primes = [n for n in sample_numbers if n in true_primes]
        
        # Estimate optimal threshold
        optimal_theta = optimizer.estimate_optimal_threshold(sample_numbers, sample_primes)
        print(f"Estimated optimal threshold: {optimal_theta:.6f}")
        
        # Apply filter to full dataset
        print("Applying vortex filter...")
        start_time = time.time()
        filtered_numbers = vortex_filter.apply_filter_efficient(test_numbers, optimal_theta)
        vortex_time = time.time() - start_time
        
        print(f"Vortex filter completed in {vortex_time:.4f}s")
        print(f"Filtered {len(filtered_numbers)} numbers from {len(test_numbers)}")
        
        # Validate performance
        metrics = optimizer.validate_performance(
            filtered_numbers, true_primes, vortex_time, sieve_time
        )
        
        # Display results
        print("\nPerformance Metrics:")
        print(f"Precision:    {metrics['precision']:.6f}")
        print(f"Recall:       {metrics['recall']:.6f}")
        print(f"F1 Score:     {metrics['f1_score']:.6f}")
        print(f"Error Rate:   {metrics['error_rate']:.6f} (target: ≤0.08)")
        print(f"Speedup:      {metrics['speedup_factor']:.2f}x (target: ≥3x)")
        print(f"KS Stat:      {metrics['ks_statistic']:.6f} (target: ≈0.04)")
        print(f"KS p-value:   {metrics['ks_p_value']:.6f} (target: <0.01)")
        
        # Status check
        success_criteria = [
            metrics['error_rate'] <= 0.08,
            metrics['speedup_factor'] >= 3.0,
            metrics['ks_statistic'] <= 0.05,
            metrics['ks_p_value'] < 0.01
        ]
        
        print(f"\nSuccess Criteria Met: {sum(success_criteria)}/4")
        if all(success_criteria):
            print("✓ ALL REQUIREMENTS SATISFIED")
        else:
            print("⚠ NEEDS FURTHER OPTIMIZATION")
        
        # Memory usage info
        cache_size = len(vortex_filter.chain_cache)
        print(f"Cache utilization: {cache_size} entries")


if __name__ == "__main__":
    main_scalable()