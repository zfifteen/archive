from typing import Optional, List, Dict

import random
import time
import json
import math
import mpmath as mp
mp.dps = 50

import sympy

MPMATH_AVAILABLE = True
import warnings
# Configuration constants
NUM_SEMIPRIMES = 50  # Number of semiprimes to test in benchmark

def enhanced_logarithmic_integral(x: float, num_terms: int = 10) -> float:
    """
    Enhanced logarithmic integral Li(x) with higher-order terms to reduce O(1/log k) error.
    
    Uses series expansion: Li(x) = γ + ln(ln(x)) + Σ(n=1 to ∞) (ln(x))^n / (n! * n)
    where γ is the Euler-Mascheroni constant.
    
    Parameters
    ----------
    x : float
        Input value for logarithmic integral
    num_terms : int, optional
        Number of series terms to include (default 10 for crypto-scale accuracy)
        
    Returns
    -------
    float
        Enhanced logarithmic integral approximation
    """
    if not MPMATH_AVAILABLE:
        warnings.warn("mpmath not available - using crude approximation")
        return x / math.log(x) if x > 1 else 0
    
    if x <= 1:
        return mp.mpf(0)
    
    # Use high precision for crypto-scale accuracy
    mp_x = mp.mpf(x)
    ln_x = mp.log(mp_x)
    
    if ln_x <= 0:
        return mp.mpf(0)
    
    ln_ln_x = mp.log(ln_x)
    
    # Start with dominant terms
    result = mp.euler + ln_ln_x  # γ + ln(ln(x))
    
    # Add series terms: Σ(n=1 to num_terms) (ln(x))^n / (n! * n)
    ln_x_power = ln_x
    factorial = mp.mpf(1)
    
    for n in range(1, num_terms + 1):
        factorial *= n
        term = ln_x_power / (factorial * n)
        result += term
        ln_x_power *= ln_x
        
        # Early termination if term becomes negligible
        if abs(term) < mp.mpf(10) ** (-mp.mp.dps + 10):
            break
    
    return float(result)

def compensated_k_estimation(n: int, error_compensation: bool = True) -> float:
    """
    Advanced k estimation with error growth compensation for cryptographic scales.
    
    Uses enhanced logarithmic integral with Richardson extrapolation and empirical
    error compensation to address O(1/log k) error growth.
    
    Parameters
    ----------
    n : int
        The semiprime to factor
    error_compensation : bool, optional
        Apply empirical error compensation (default True)
        
    Returns
    -------
    float
        Compensated k estimate for prime search
    """
    if not MPMATH_AVAILABLE:
        warnings.warn("mpmath not available - using basic k estimation")
        sqrt_n = math.sqrt(n)
        return sqrt_n / math.log(sqrt_n) if sqrt_n > 1 else 1
    
    # High precision computation
    n_mp = mp.mpf(str(n))
    sqrt_n = mp.sqrt(n_mp)
    
    # Enhanced Li(√n) with higher-order terms
    k_est = enhanced_logarithmic_integral(float(sqrt_n), num_terms=15)
    
    # Richardson extrapolation for error reduction
    k_est_coarse = enhanced_logarithmic_integral(float(sqrt_n), num_terms=10)
    k_est_fine = enhanced_logarithmic_integral(float(sqrt_n), num_terms=20)
    
    # Extrapolate to reduce error
    extrapolated = (4 * k_est_fine - k_est_coarse) / 3
    
    # Empirical error compensation for crypto scales
    if error_compensation:
        log_sqrt_n = mp.log(sqrt_n)
        compensation = 0.5 / log_sqrt_n if log_sqrt_n > 0 else 0
        extrapolated += compensation
    
    return float(extrapolated)

def z5d_prime(k: float, c: float = -0.00247, kstar: float = 0.04449, kappa_geo: float = 0.3) -> float:
    """
    Z5D prime predictor wrapper with high precision.
    
    Parameters
    ----------
    k : float
        Index value for prime estimation
    c : float, optional
        Dilation calibration parameter (default from issue)
    kstar : float, optional  
        Curvature calibration parameter (default from issue)
    kappa_geo : float, optional
        Geodesic modulation parameter (default from issue)
        
    Returns
    -------
    float
        Estimated kth prime using Z5D methodology
    """
    if not MPMATH_AVAILABLE:
        warnings.warn("mpmath not available - using reduced precision")
        return 0
    
    # Use high-precision mpmath computation
    mp_k = mp.mpf(k)
    ln_k = mp.log(mp_k)
    ln_ln_k = mp.log(ln_k)
    
    # Prime Number Theorem base estimate with high precision
    term1 = ln_k + ln_ln_k - 1 + (ln_ln_k - 2) / ln_k
    pnt = mp_k * term1
    
    # Geodesic modulation with high precision  
    e2 = mp.exp(2)
    geo_mod = kappa_geo * mp.log(mp_k + 1) / e2
    
    # Z5D corrections
    dk = mp.mpf(2) * pnt * c
    ek = pnt * kstar * geo_mod
    
    # Final result
    result = pnt + dk + ek
    return float(result.real) if hasattr(result, 'real') else float(result)

def probe_semiprime_z5d(n: int, trials: int = 1000) -> Optional[int]:
    """
    Z5D-based semiprime factorization using Newton-R predictor.

    Parameters
    ----------
    n : int
        Semiprime to factor
    trials : int, optional
        Search trials around k_est (default 1000)

    Returns
    -------
    Optional[int]
        Found factor, or None if not found
    """
    k_est = compensated_k_estimation(n, error_compensation=False)
    
    # Search around k_est
    for i in range(-trials // 2, trials // 2 + 1):
        delta_k = float(i)
        k = k_est + delta_k
        
        if k <= 0:
            continue
        
        pred_p = z5d_prime(k)
        cand_p = int(round(pred_p))
        
        if cand_p > 1 and cand_p < n and n % cand_p == 0:
            return cand_p
    
    return None

def generate_random_64bit_semiprime(seed: int = 42) -> int:
    random.seed(seed)
    # Generate two random 32-bit primes and multiply
    p = sympy.randprime(2**31, 2**32 - 1)
    q = sympy.randprime(2**31, 2**32 - 1)
    return p * q

if __name__ == "__main__":
    random.seed(42)
    results = []
    for i in range(NUM_SEMIPRIMES):
        n = generate_random_64bit_semiprime(seed=42 + i)
        start_time = time.time()
        factor = probe_semiprime_z5d(n, trials=1000)
        end_time = time.time()
        success = factor is not None
        results.append({
            'n': n,
            'factor': factor,
            'time': end_time - start_time,
            'success': success
        })
        print(f"N={n}, Factor={factor}, Time={end_time - start_time:.4f}s, Success={success}")
    
    hit_rate = sum(1 for r in results if r['success']) / len(results)
    avg_time = sum(r['time'] for r in results) / len(results)
    print(f"Hit rate: {hit_rate:.2%}")
    print(f"Average time: {avg_time:.4f}s")
    
    # Save to JSON
    with open('z5d_benchmark_64bit_results.json', 'w') as f:
        json.dump(results, f, indent=4)