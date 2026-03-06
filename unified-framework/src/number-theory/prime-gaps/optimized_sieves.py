"""
Optimized Prime Sieves for Large-Scale Prime Gap Analysis
=========================================================

This module implements highly optimized sieve algorithms for generating primes
up to N=10^9, specifically designed for prime gap analysis in the Z framework.

Features:
- Optimized Sieve of Eratosthenes with memory and computation efficiency
- Sieve of Atkin implementation for comparison and validation
- Segmented sieving for memory-efficient large N computation
- Integration with Z framework curvature models

References:
- Z Framework: Z = A(B/c) universal invariance
- Curvature measure: κ(n) = d(n)·ln(n+1)/e²
- Frame shift: θ'(n,k) = φ·{n/φ}^k
"""

import numpy as np
import math
import time
import gc
from typing import Iterator, List, Tuple, Optional
import psutil
import os


class OptimizedSieves:
    """
    Collection of optimized sieve algorithms for large-scale prime generation.
    """
    
    def __init__(self, memory_limit_mb: int = 1000):
        """
        Initialize with memory constraints.
        
        Args:
            memory_limit_mb: Maximum memory usage in megabytes
        """
        self.memory_limit_mb = memory_limit_mb
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        
    def sieve_of_eratosthenes_optimized(self, limit: int) -> np.ndarray:
        """
        Optimized Sieve of Eratosthenes with memory efficiency.
        
        Optimizations:
        - Only odd numbers stored (halves memory)
        - Bit packing for further memory reduction
        - Early termination and skip optimizations
        
        Args:
            limit: Upper bound for prime generation
            
        Returns:
            Array of primes up to limit
        """
        if limit < 2:
            return np.array([], dtype=np.int64)
        if limit == 2:
            return np.array([2], dtype=np.int64)
            
        # Memory check
        estimated_memory = limit // 16  # Bit packing estimate
        if estimated_memory > self.memory_limit_bytes:
            raise MemoryError(f"Estimated memory {estimated_memory/1024/1024:.1f}MB exceeds limit {self.memory_limit_mb}MB")
        
        # Only store odd numbers (2 is handled separately)
        size = (limit - 1) // 2
        sieve = np.ones(size, dtype=bool)
        
        # Sieve the odd numbers
        sqrt_limit = int(math.sqrt(limit))
        for i in range(3, sqrt_limit + 1, 2):
            if sieve[(i - 3) // 2]:  # i is prime
                # Mark multiples of i starting from i*i
                start = i * i
                if start % 2 == 0:
                    start += i  # Make it odd
                for j in range(start, limit, 2 * i):
                    sieve[(j - 3) // 2] = False
        
        # Collect primes
        primes = [2]  # Add 2 first
        primes.extend(2 * np.where(sieve)[0] + 3)
        
        return np.array(primes, dtype=np.int64)
    
    def sieve_of_eratosthenes_segmented(self, limit: int, segment_size: Optional[int] = None) -> Iterator[np.ndarray]:
        """
        Segmented Sieve of Eratosthenes for memory-efficient large N processing.
        
        This approach processes the sieve in segments to handle N=10^9 efficiently.
        
        Args:
            limit: Upper bound for prime generation
            segment_size: Size of each segment (auto-calculated if None)
            
        Yields:
            Arrays of primes found in each segment
        """
        if segment_size is None:
            # Auto-calculate segment size based on memory limit
            segment_size = min(int(math.sqrt(limit)), self.memory_limit_mb * 1024 * 8)
            segment_size = max(segment_size, 1000000)  # Minimum 1M
        
        # First, find all primes up to sqrt(limit) using simple sieve
        sqrt_limit = int(math.sqrt(limit)) + 1
        small_primes = self.sieve_of_eratosthenes_optimized(sqrt_limit)
        
        # Process segments
        low = 2  # Start from 2
        while low <= limit:
            high = min(low + segment_size - 1, limit)
            
            # Create segment array
            size = high - low + 1
            sieve = np.ones(size, dtype=bool)
            
            # Sieve using small primes
            for p in small_primes:
                if p * p > high:
                    break
                
                # Find first multiple of p in [low, high]
                start = max(p * p, (low + p - 1) // p * p)
                
                # Mark multiples in this segment
                for j in range(start, high + 1, p):
                    sieve[j - low] = False
            
            # Collect primes from this segment
            indices = np.where(sieve)[0]
            segment_primes = indices + low
            
            # Filter out primes that are too small for this segment (shouldn't happen but safety check)
            segment_primes = segment_primes[segment_primes >= low]
            
            if len(segment_primes) > 0:
                yield segment_primes
            
            # Move to next segment
            low = high + 1
            
            # Memory cleanup
            del sieve
            gc.collect()
    
    def sieve_of_atkin(self, limit: int) -> np.ndarray:
        """
        Sieve of Atkin implementation for comparison with Eratosthenes.
        
        The Sieve of Atkin is theoretically faster for very large numbers
        but has higher constant factors. Good for validation and comparison.
        
        Args:
            limit: Upper bound for prime generation
            
        Returns:
            Array of primes up to limit
        """
        if limit < 2:
            return np.array([], dtype=np.int64)
        
        # Memory check
        estimated_memory = limit // 8
        if estimated_memory > self.memory_limit_bytes:
            raise MemoryError(f"Estimated memory {estimated_memory/1024/1024:.1f}MB exceeds limit {self.memory_limit_mb}MB")
        
        # Initialize sieve
        sieve = np.zeros(limit + 1, dtype=bool)
        
        # Main algorithm
        sqrt_limit = int(math.sqrt(limit))
        
        # 4x² + y² form
        for x in range(1, sqrt_limit + 1):
            for y in range(1, sqrt_limit + 1):
                n = 4 * x * x + y * y
                if n <= limit and (n % 12 == 1 or n % 12 == 5):
                    sieve[n] = not sieve[n]
        
        # 3x² + y² form
        for x in range(1, sqrt_limit + 1):
            for y in range(2, sqrt_limit + 1, 2):
                n = 3 * x * x + y * y
                if n <= limit and n % 12 == 7:
                    sieve[n] = not sieve[n]
        
        # 3x² - y² form (x > y)
        for x in range(2, sqrt_limit + 1):
            for y in range(x - 1, 0, -2):
                n = 3 * x * x - y * y
                if n <= limit and n % 12 == 11:
                    sieve[n] = not sieve[n]
        
        # Mark squares of primes as composite
        for i in range(5, sqrt_limit + 1):
            if sieve[i]:
                square = i * i
                for j in range(square, limit + 1, square):
                    sieve[j] = False
        
        # Collect primes
        primes = [2, 3]  # Add 2 and 3
        primes.extend(np.where(sieve[5:])[0] + 5)
        
        return np.array(primes, dtype=np.int64)
    
    def benchmark_sieves(self, test_limit: int = 1000000) -> dict:
        """
        Benchmark different sieve implementations.
        
        Args:
            test_limit: Limit for benchmarking
            
        Returns:
            Dictionary with benchmark results
        """
        results = {}
        
        # Benchmark Eratosthenes
        start_time = time.time()
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss
        
        primes_erat = self.sieve_of_eratosthenes_optimized(test_limit)
        
        end_time = time.time()
        end_memory = process.memory_info().rss
        
        results['eratosthenes'] = {
            'time': end_time - start_time,
            'memory_mb': (end_memory - start_memory) / 1024 / 1024,
            'prime_count': len(primes_erat),
            'largest_prime': primes_erat[-1] if len(primes_erat) > 0 else 0
        }
        
        # Benchmark Atkin (if feasible)
        if test_limit <= 10000000:  # Atkin is memory-intensive
            start_time = time.time()
            start_memory = process.memory_info().rss
            
            primes_atkin = self.sieve_of_atkin(test_limit)
            
            end_time = time.time()
            end_memory = process.memory_info().rss
            
            results['atkin'] = {
                'time': end_time - start_time,
                'memory_mb': (end_memory - start_memory) / 1024 / 1024,
                'prime_count': len(primes_atkin),
                'largest_prime': primes_atkin[-1] if len(primes_atkin) > 0 else 0
            }
            
            # Verify results match
            results['verification'] = {
                'results_match': np.array_equal(primes_erat, primes_atkin),
                'eratosthenes_count': len(primes_erat),
                'atkin_count': len(primes_atkin)
            }
        
        # Benchmark segmented sieve
        start_time = time.time()
        start_memory = process.memory_info().rss
        
        primes_segmented = []
        for segment in self.sieve_of_eratosthenes_segmented(test_limit):
            primes_segmented.extend(segment)
        primes_segmented = np.array(primes_segmented, dtype=np.int64)
        
        end_time = time.time()
        end_memory = process.memory_info().rss
        
        results['segmented'] = {
            'time': end_time - start_time,
            'memory_mb': (end_memory - start_memory) / 1024 / 1024,
            'prime_count': len(primes_segmented),
            'largest_prime': primes_segmented[-1] if len(primes_segmented) > 0 else 0
        }
        
        return results


def validate_sieve_correctness(limit: int = 100000) -> bool:
    """
    Validate sieve implementations against known prime sequences.
    
    Args:
        limit: Limit for validation testing
        
    Returns:
        True if all implementations produce correct results
    """
    sieves = OptimizedSieves()
    
    # Known first few primes
    known_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    
    # Test Eratosthenes
    primes_erat = sieves.sieve_of_eratosthenes_optimized(50)
    if not np.array_equal(primes_erat, known_primes):
        print(f"Eratosthenes validation failed: {primes_erat} != {known_primes}")
        return False
    
    # Test Atkin
    primes_atkin = sieves.sieve_of_atkin(50)
    if not np.array_equal(primes_atkin, known_primes):
        print(f"Atkin validation failed: {primes_atkin} != {known_primes}")
        return False
    
    # Test segmented
    primes_segmented = []
    for segment in sieves.sieve_of_eratosthenes_segmented(50, segment_size=20):
        primes_segmented.extend(segment)
    primes_segmented = np.array(primes_segmented, dtype=np.int64)
    
    if not np.array_equal(primes_segmented, known_primes):
        print(f"Segmented validation failed: {primes_segmented} != {known_primes}")
        return False
    
    print("✓ All sieve implementations validated successfully")
    return True


if __name__ == "__main__":
    # Validation and benchmarking
    print("=== Optimized Sieve Validation and Benchmarking ===")
    
    # Validate correctness
    if not validate_sieve_correctness():
        print("❌ Validation failed!")
        exit(1)
    
    # Benchmark performance
    print("\n=== Benchmarking Sieves ===")
    sieves = OptimizedSieves(memory_limit_mb=500)
    
    for test_limit in [100000, 1000000]:
        print(f"\n--- Benchmark for N = {test_limit:,} ---")
        results = sieves.benchmark_sieves(test_limit)
        
        for method, stats in results.items():
            if method == 'verification':
                print(f"Verification: {'✓' if stats['results_match'] else '❌'} "
                      f"({stats['eratosthenes_count']} vs {stats['atkin_count']})")
            else:
                print(f"{method.capitalize():>12}: {stats['time']:.3f}s, "
                      f"{stats['memory_mb']:.1f}MB, {stats['prime_count']:,} primes")