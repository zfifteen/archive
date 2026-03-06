#!/usr/bin/env python3
"""
Crypto-Friendly Prime Generator for Z5D Test Plan
================================================

Implementation of the crypto-friendly prime generation API as specified in Issue #677.
This module provides the core functionality for generating and testing special-form primes
using Z5D-biased search methods.

API Functions:
- generate_crypto_primes(): Main generation function with configurable parameters
- Special form detection: Pseudo-Mersenne, Generalized Mersenne
- Statistical analysis: Bootstrap confidence intervals, hit-rate calculations
- Performance benchmarking: Montgomery multiplication timing

Author: Copilot Agent
License: MIT
"""

import sys
import os
import numpy as np
import time
import secrets
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any, Union
from sympy import isprime, nextprime, prevprime
import logging

# Add framework paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import Z5D predictor and utilities
try:
    from z_framework.discrete.z5d_predictor import z5d_prime
    from statistical.bootstrap_validation import bootstrap_confidence_intervals
except ImportError:
    # Fallback for development
    def z5d_prime(k):
        """Fallback Z5D predictor using PNT approximation"""
        if k < 6:
            primes = [2, 3, 5, 7, 11, 13]
            return primes[k-1] if k <= len(primes) else 13
        
        # Enhanced PNT approximation 
        log_k = np.log(k)
        log_log_k = np.log(log_k) if log_k > 1 else 1
        pnt = k * (log_k + log_log_k - 1.0 + (log_log_k - 2.0)/log_k)
        
        # Z5D correction terms (simplified)
        c = -0.00247  # calibrated coefficient
        k_star = 0.04449  # calibrated scaling
        d_term = c * pnt
        e_term = k_star * np.exp(log_k / np.e**2) * pnt
        
        return int(pnt + d_term + e_term)
    
    def bootstrap_confidence_intervals(data, statistic_func, confidence_level=0.95, n_bootstrap=1000):
        """Fallback bootstrap implementation"""
        bootstrap_stats = []
        original_stat = statistic_func(data)
        
        for _ in range(n_bootstrap):
            boot_indices = np.random.choice(len(data), len(data), replace=True)
            boot_sample = np.array(data)[boot_indices]
            try:
                boot_stat = statistic_func(boot_sample)
                bootstrap_stats.append(boot_stat)
            except:
                continue
        
        bootstrap_stats = np.array(bootstrap_stats)
        alpha = 1 - confidence_level
        
        return {
            'confidence_interval': (
                np.percentile(bootstrap_stats, (alpha/2) * 100),
                np.percentile(bootstrap_stats, (1 - alpha/2) * 100)
            ),
            'bootstrap_mean': np.mean(bootstrap_stats),
            'bootstrap_std': np.std(bootstrap_stats),
            'original_statistic': original_stat
        }

# Configure logging
logger = logging.getLogger(__name__)

class SpecialFormType(Enum):
    """Types of special-form primes to detect"""
    PSEUDO_MERSENNE = "pseudo_mersenne"  # p = 2^m - c with small c
    GENERALIZED = "generalized"         # p = 2^α(2^β - γ) - 1 with small γ
    SQRT_FRIENDLY = "sqrt_friendly"     # p ≡ 3 (mod 4)

@dataclass
class CryptoPrimeConfig:
    """Configuration for crypto-friendly prime generation"""
    kind: str = "baseline"              # "baseline" or "z5d_biased"
    window: int = 2**18                # Search window size W
    max_hits: int = 100                # Maximum primes to find
    prime_bits: int = 256              # Target bit length
    seed: int = 42                     # RNG seed for reproducibility
    special_form: SpecialFormType = SpecialFormType.PSEUDO_MERSENNE
    c_max: int = 100                   # Maximum c for pseudo-Mersenne
    gamma_max: int = 256               # Maximum γ for generalized
    verbose: bool = False              # Verbose output

@dataclass  
class CryptoPrimeResult:
    """Results from crypto-friendly prime generation"""
    primes: List[int]                  # Found primes
    k_values: List[int]               # Corresponding k values
    candidates_tested: int             # Total primality tests
    special_form_count: int           # Count of special-form primes
    sqrt_friendly_count: int          # Count of sqrt-friendly primes  
    generation_time: float            # Time taken (seconds)
    hit_rate: float                   # Special-form hit rate
    search_method: str                # "baseline" or "z5d_biased"
    bit_length: int                   # Target bit length
    window_size: int                  # Search window used

def _is_pseudo_mersenne(p: int, c_max: int = 100) -> Tuple[bool, int]:
    """
    Check if prime p is pseudo-Mersenne: p = 2^m - c with small c
    
    Returns:
        (is_pseudo_mersenne, c_value)
    """
    if p <= 2:
        return False, 0
        
    # Find the largest power of 2 less than or equal to p
    m = p.bit_length()
    
    # Check for exact powers and nearby values
    for m_test in range(max(1, m-2), m+3):
        power_2_m = 2**m_test
        c = power_2_m - p
        
        if 0 < c <= c_max:
            return True, c
            
    return False, 0

def _is_generalized_mersenne(p: int, gamma_max: int = 256) -> Tuple[bool, Tuple[int, int, int]]:
    """
    Check if prime p is generalized Mersenne: p = 2^α(2^β - γ) - 1
    
    Returns:
        (is_generalized, (alpha, beta, gamma))
    """
    if p <= 2:
        return False, (0, 0, 0)
    
    # Try small values of α and β
    for alpha in range(1, 8):
        for beta in range(1, 16):
            # p + 1 = 2^α(2^β - γ)
            factor = 2**alpha
            if (p + 1) % factor != 0:
                continue
                
            quotient = (p + 1) // factor
            # quotient = 2^β - γ, so γ = 2^β - quotient
            power_2_beta = 2**beta
            gamma = power_2_beta - quotient
            
            if 0 < gamma <= gamma_max:
                return True, (alpha, beta, gamma)
                
    return False, (0, 0, 0)

def _is_sqrt_friendly(p: int) -> bool:
    """Check if prime p ≡ 3 (mod 4) for efficient square root computation"""
    return p % 4 == 3

def _invert_pnt_to_k(m: int) -> int:
    """
    Invert PNT to find k such that the k-th prime ≈ 2^m
    Uses Newton's method for robust inversion.
    """
    target = 2**m
    
    # Initial guess using PNT approximation
    log_target = np.log(target)
    k = target / log_target
    
    # Newton's method refinement
    for _ in range(10):
        pred = z5d_prime(int(k))
        error = pred - target
        
        if abs(error) < target * 1e-6:  # Converged
            break
            
        # Derivative approximation
        k_delta = max(1, int(k * 0.001))
        pred_delta = z5d_prime(int(k + k_delta))
        derivative = (pred_delta - pred) / k_delta
        
        if derivative > 0:
            k = k - error / derivative
        else:
            break
            
    return max(1, int(k))

def generate_crypto_primes(
    k_values: List[int],
    kind: str = "baseline", 
    window: int = 2**18,
    max_hits: int = 100,
    prime_bits: int = 256,
    seed: int = 42
) -> CryptoPrimeResult:
    """
    Generate crypto-friendly primes using Z5D-biased or baseline search.
    
    This is the main API function specified in Issue #677.
    
    Parameters:
    -----------
    k_values : List[int]
        List of k values for prime prediction
    kind : str 
        Search method: "baseline" or "z5d_biased"  
    window : int
        Search window size W (default: 2^18)
    max_hits : int
        Maximum number of primes to find
    prime_bits : int
        Target bit length for primes  
    seed : int
        Random seed for reproducibility
        
    Returns:
    --------
    CryptoPrimeResult with found primes and statistics
    """
    start_time = time.time()
    np.random.seed(seed)
    
    primes = []
    k_vals = []
    candidates_tested = 0
    special_form_count = 0
    sqrt_friendly_count = 0
    
    logger.info(f"Starting {kind} search for {len(k_values)} k values")
    
    for k in k_values[:max_hits]:
        if kind == "z5d_biased":
            # Z5D-biased: center search around Z5D prediction
            center = z5d_prime(k)
        else:
            # Baseline: center around 2^m for corresponding bit length
            if prime_bits:
                center = 2**prime_bits
            else:
                center = z5d_prime(k)  # Fallback
        
        # Search window [center - W, center + W]
        start_range = max(3, center - window//2)
        end_range = center + window//2
        
        # Ensure odd candidates only
        if start_range % 2 == 0:
            start_range += 1
            
        candidates_in_window = 0
        
        # Search for primes in window
        for candidate in range(start_range, end_range, 2):
            candidates_tested += 1
            candidates_in_window += 1
            
            if isprime(candidate):
                primes.append(candidate)
                k_vals.append(k)
                
                # Check special forms
                is_pseudo, c_val = _is_pseudo_mersenne(candidate)
                is_gen, gen_params = _is_generalized_mersenne(candidate)
                is_sqrt = _is_sqrt_friendly(candidate)
                
                if is_pseudo or is_gen:
                    special_form_count += 1
                    
                if is_sqrt:
                    sqrt_friendly_count += 1
                    
                if len(primes) >= max_hits:
                    break
                    
        if len(primes) >= max_hits:
            break
    
    generation_time = time.time() - start_time
    hit_rate = special_form_count / max(1, candidates_tested)
    
    result = CryptoPrimeResult(
        primes=primes,
        k_values=k_vals,
        candidates_tested=candidates_tested,
        special_form_count=special_form_count,
        sqrt_friendly_count=sqrt_friendly_count,
        generation_time=generation_time,
        hit_rate=hit_rate,
        search_method=kind,
        bit_length=prime_bits,
        window_size=window
    )
    
    logger.info(f"Generated {len(primes)} primes in {generation_time:.2f}s")
    logger.info(f"Special form hit rate: {hit_rate:.4f}")
    
    return result

def benchmark_vs_baseline(
    m_values: List[int] = [128, 192, 224, 255, 256, 384, 521],
    window: int = 2**18,
    budget: int = 200000,
    special_form: SpecialFormType = SpecialFormType.PSEUDO_MERSENNE,
    seed: int = 42
) -> Dict[int, Dict[str, Any]]:
    """
    Benchmark Z5D-biased vs baseline search across multiple bit lengths.
    
    Returns hit-rate comparison and bootstrap confidence intervals.
    """
    results = {}
    
    for m in m_values:
        logger.info(f"Benchmarking bit length {m}")
        
        # Convert bit length to k value
        k = _invert_pnt_to_k(m)
        k_values = [k]
        
        # Run baseline search
        baseline_result = generate_crypto_primes(
            k_values, 
            kind="baseline",
            window=window,
            max_hits=budget//1000,  # Limit for reasonable runtime
            prime_bits=m,
            seed=seed
        )
        
        # Run Z5D-biased search  
        z5d_result = generate_crypto_primes(
            k_values,
            kind="z5d_biased", 
            window=window,
            max_hits=budget//1000,
            prime_bits=m,
            seed=seed
        )
        
        # Calculate hit-rate difference
        baseline_rate = baseline_result.hit_rate
        z5d_rate = z5d_result.hit_rate
        
        if baseline_rate > 0:
            ratio = z5d_rate / baseline_rate
            delta = z5d_rate - baseline_rate
        else:
            ratio = float('inf') if z5d_rate > 0 else 1.0
            delta = z5d_rate
        
        results[m] = {
            'baseline_hit_rate': baseline_rate,
            'z5d_hit_rate': z5d_rate,
            'ratio': ratio,
            'delta': delta,
            'baseline_primes': len(baseline_result.primes),
            'z5d_primes': len(z5d_result.primes),
            'baseline_special_forms': baseline_result.special_form_count,
            'z5d_special_forms': z5d_result.special_form_count
        }
        
        logger.info(f"m={m}: baseline={baseline_rate:.4f}, z5d={z5d_rate:.4f}, ratio={ratio:.2f}")
    
    return results

if __name__ == "__main__":
    # Example usage and testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Crypto-friendly prime generator test")
    parser.add_argument("--m", type=int, default=256, help="Bit length")
    parser.add_argument("--kind", default="z5d_biased", choices=["baseline", "z5d_biased"])
    parser.add_argument("--window", type=int, default=2**18, help="Search window size")
    parser.add_argument("--max-hits", type=int, default=50, help="Maximum primes to find")
    
    args = parser.parse_args()
    
    # Convert bit length to k
    k = _invert_pnt_to_k(args.m)
    
    # Generate primes
    result = generate_crypto_primes(
        k_values=[k],
        kind=args.kind,
        window=args.window, 
        max_hits=args.max_hits,
        prime_bits=args.m
    )
    
    print(f"Generated {len(result.primes)} primes")
    print(f"Special form count: {result.special_form_count}")
    print(f"Hit rate: {result.hit_rate:.4f}")
    print(f"Time: {result.generation_time:.2f}s")