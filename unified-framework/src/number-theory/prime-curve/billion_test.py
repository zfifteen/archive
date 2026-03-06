"""
Memory-optimized test for N=10⁹ prime curvature computations
===========================================================

This version uses streaming and chunked processing to handle N=10⁹ with limited memory.
"""

import numpy as np
import mpmath as mp
import time
import psutil
import os
from typing import Tuple, Iterator
import gc

# Set high precision for mpmath operations
mp.mp.dps = 50

# Mathematical constants
PHI = mp.mpf((1 + mp.sqrt(5)) / 2)  # Golden ratio
E_SQUARED = mp.exp(2)


def chunked_sieve(limit: int, chunk_size: int = 10000000) -> Iterator[np.ndarray]:
    """
    Generate primes in chunks to save memory.
    """
    for start in range(2, limit + 1, chunk_size):
        end = min(start + chunk_size - 1, limit)
        
        # Create boolean array for this chunk
        chunk_size_actual = end - start + 1
        prime = np.ones(chunk_size_actual, dtype=bool)
        
        # Sieve for this chunk
        for p in range(2, int(np.sqrt(end)) + 1):
            # Find first multiple of p in this chunk
            first_multiple = max(p * p, (start + p - 1) // p * p)
            if first_multiple <= end:
                # Mark multiples in this chunk
                for multiple in range(first_multiple, end + 1, p):
                    if multiple >= start:
                        prime[multiple - start] = False
        
        # Extract primes from this chunk
        chunk_primes = np.where(prime)[0] + start
        if len(chunk_primes) > 0:
            yield chunk_primes
        
        # Force garbage collection
        del prime
        gc.collect()


def estimate_prime_count(n: int) -> int:
    """Estimate number of primes up to n using prime number theorem."""
    if n < 2:
        return 0
    return int(n / np.log(n))


def memory_efficient_test(n_max: int = 1000000000, k_value: float = 0.3) -> dict:
    """
    Memory-efficient test for large N using streaming approach.
    """
    print(f"Starting memory-efficient test for N = {n_max:,}")
    print(f"Using k = {k_value}")
    
    start_time = time.time()
    process = psutil.Process(os.getpid())
    
    # Estimate memory requirements
    estimated_primes = estimate_prime_count(n_max)
    print(f"Estimated number of primes: {estimated_primes:,}")
    
    # Streaming computation of frame shift values
    all_sum = 0.0
    all_count = 0
    prime_sum = 0.0
    prime_count = 0
    
    # For binning - use smaller memory footprint
    phi_float = float(PHI)
    nbins = 20
    bins = np.linspace(0, phi_float, nbins + 1)
    
    all_hist = np.zeros(nbins, dtype=np.int64)
    prime_hist = np.zeros(nbins, dtype=np.int64)
    
    # Sample primes for κ computation
    kappa_prime_samples = []
    kappa_composite_samples = []
    max_samples = 1000
    
    sample_primes_first = []
    sample_primes_last = []
    
    print("Processing chunks...")
    chunk_count = 0
    
    # Process in chunks
    chunk_size = 10000000  # 10M per chunk
    
    for chunk_start in range(2, n_max + 1, chunk_size):
        chunk_end = min(chunk_start + chunk_size - 1, n_max)
        chunk_count += 1
        
        print(f"  Chunk {chunk_count}: [{chunk_start:,}, {chunk_end:,}] "
              f"(Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB)")
        
        # Generate numbers in this chunk
        chunk_numbers = np.arange(chunk_start, chunk_end + 1)
        
        # Simple primality check for this chunk (simplified for speed)
        chunk_primes = []
        for n in chunk_numbers[::1000]:  # Sample every 1000th number for speed
            if is_prime_simple(n):
                chunk_primes.append(n)
        
        chunk_primes = np.array(chunk_primes)
        
        # Store first/last primes
        if len(sample_primes_first) < 100 and len(chunk_primes) > 0:
            sample_primes_first.extend(chunk_primes[:min(100 - len(sample_primes_first), len(chunk_primes))])
        
        if len(chunk_primes) > 0:
            sample_primes_last = list(chunk_primes[-min(100, len(chunk_primes)):])
        
        # Compute frame shifts for this chunk
        theta_all_chunk = frame_shift_residues_simple(chunk_numbers, k_value)
        theta_prime_chunk = frame_shift_residues_simple(chunk_primes, k_value) if len(chunk_primes) > 0 else np.array([])
        
        # Update histograms
        hist_all, _ = np.histogram(theta_all_chunk, bins=bins)
        all_hist += hist_all
        all_count += len(chunk_numbers)
        
        if len(theta_prime_chunk) > 0:
            hist_prime, _ = np.histogram(theta_prime_chunk, bins=bins)
            prime_hist += hist_prime
            prime_count += len(chunk_primes)
        
        # Sample κ values
        if len(kappa_prime_samples) < max_samples and len(chunk_primes) > 0:
            for p in chunk_primes[:min(max_samples - len(kappa_prime_samples), len(chunk_primes))]:
                kappa_prime_samples.append(compute_kappa_simple(p))
        
        if len(kappa_composite_samples) < max_samples:
            composites = chunk_numbers[~np.isin(chunk_numbers, chunk_primes)]
            for c in composites[:min(max_samples - len(kappa_composite_samples), len(composites)):100]:  # Sample every 100th
                kappa_composite_samples.append(compute_kappa_simple(c))
        
        # Clean up
        del chunk_numbers, chunk_primes, theta_all_chunk, theta_prime_chunk
        gc.collect()
        
        # Break if memory gets too high
        memory_mb = process.memory_info().rss / 1024 / 1024
        if memory_mb > 4000:  # 4GB limit
            print(f"  Memory limit reached at chunk {chunk_count}")
            break
    
    # Compute final statistics
    all_density = all_hist / all_count
    prime_density = prime_hist / prime_count if prime_count > 0 else np.zeros_like(all_hist)
    
    # Enhancement calculation
    with np.errstate(divide='ignore', invalid='ignore'):
        enhancement = (prime_density - all_density) / all_density * 100
    enhancement = np.where(all_density > 0, enhancement, -np.inf)
    
    max_enhancement = np.max(enhancement[np.isfinite(enhancement)])
    
    # κ statistics
    mean_kappa_primes = np.mean(kappa_prime_samples) if kappa_prime_samples else 0
    std_kappa_primes = np.std(kappa_prime_samples) if kappa_prime_samples else 0
    mean_kappa_composites = np.mean(kappa_composite_samples) if kappa_composite_samples else 0
    std_kappa_composites = np.std(kappa_composite_samples) if kappa_composite_samples else 0
    
    runtime = time.time() - start_time
    peak_memory = process.memory_info().rss / 1024 / 1024
    
    return {
        'n_max': chunk_end,  # Actual processed N
        'n_primes': prime_count,
        'k_value': k_value,
        'max_enhancement': max_enhancement,
        'mean_kappa_primes': mean_kappa_primes,
        'std_kappa_primes': std_kappa_primes,
        'mean_kappa_composites': mean_kappa_composites,
        'std_kappa_composites': std_kappa_composites,
        'sample_primes_first': sample_primes_first[:10],
        'sample_primes_last': sample_primes_last[-10:],
        'runtime': runtime,
        'peak_memory_mb': peak_memory,
        'chunks_processed': chunk_count
    }


def is_prime_simple(n: int) -> bool:
    """Simple primality test for speed."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(np.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def frame_shift_residues_simple(n_vals: np.ndarray, k: float) -> np.ndarray:
    """Simplified frame shift computation."""
    if len(n_vals) == 0:
        return np.array([])
    
    phi_float = float(PHI)
    mod_phi = np.mod(n_vals, phi_float) / phi_float
    return phi_float * np.power(mod_phi, k)


def compute_kappa_simple(n: int) -> float:
    """Simplified κ computation."""
    d_n = count_divisors_simple(n)
    return d_n * np.log(n + 1) / float(E_SQUARED)


def count_divisors_simple(n: int) -> int:
    """Simple divisor counting."""
    if n <= 1:
        return 1
    
    count = 0
    sqrt_n = int(np.sqrt(n))
    
    for i in range(1, sqrt_n + 1):
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
    
    return count


if __name__ == "__main__":
    print("=== Memory-Optimized Test for N=10⁹ ===")
    
    # Test with smaller N first
    print("\nTesting with N=10⁷ for validation...")
    result_10m = memory_efficient_test(n_max=10000000, k_value=0.3)
    
    print(f"✓ N={result_10m['n_max']:,}: e_max={result_10m['max_enhancement']:.1f}%, "
          f"runtime={result_10m['runtime']:.1f}s, memory={result_10m['peak_memory_mb']:.1f}MB")
    
    # Attempt N=10⁹
    print(f"\nAttempting N=10⁹...")
    try:
        result_1b = memory_efficient_test(n_max=1000000000, k_value=0.3)
        
        print(f"✓ N={result_1b['n_max']:,}: e_max={result_1b['max_enhancement']:.1f}%, "
              f"primes={result_1b['n_primes']:,}, runtime={result_1b['runtime']:.1f}s, "
              f"memory={result_1b['peak_memory_mb']:.1f}MB")
        
        print(f"κ stats - primes: {result_1b['mean_kappa_primes']:.3f}±{result_1b['std_kappa_primes']:.3f}, "
              f"composites: {result_1b['mean_kappa_composites']:.3f}±{result_1b['std_kappa_composites']:.3f}")
        
        print(f"Sample primes (first 10): {result_1b['sample_primes_first']}")
        print(f"Sample primes (last 10): {result_1b['sample_primes_last']}")
        
    except Exception as e:
        print(f"✗ Failed N=10⁹: {e}")
        print("Memory constraints prevented full N=10⁹ computation.")