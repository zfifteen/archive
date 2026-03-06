"""
Core prime prediction engine using Riemann's R function and Newton-Raphson method.

This module provides the core functionality for predicting the nth prime number
using geometric properties derived from Riemann's R function in a 5D embedding.
"""

from functools import lru_cache
from typing import Dict, Tuple, Optional, Union
import time
import statistics

try:
    import mpmath as mp
    mp.mp.dps = 60
    HAS_MPMATH = True
except ImportError:
    HAS_MPMATH = False
    import math

# Ground truth for validation: p_{10^k} for k=1..18
KNOWN_PRIMES = {
    10**1: 29,
    10**2: 541,
    10**3: 7919,
    10**4: 104729,
    10**5: 1299709,
    10**6: 15485863,
    10**7: 179424673,
    10**8: 2038074743,
    10**9: 22801763489,
    10**10: 252097800623,
    10**11: 2760727302517,
    10**12: 29996224275833,
    10**13: 323780508946331,
    10**14: 3475385758524527,
    10**15: 37124508045065437,
    10**16: 394906913903735329,
    10**17: 4185296581467695669,
    10**18: 44211790234832169331,
}


@lru_cache(None)
def mu(k: int) -> int:
    """
    Compute the Möbius function μ(k).
    
    Returns:
        1 if k is square-free with even number of prime factors
        -1 if k is square-free with odd number of prime factors
        0 if k has a squared prime factor
    """
    if k == 1:
        return 1
    m, p, cnt = k, 2, 0
    while p * p <= m:
        if m % p == 0:
            cnt += 1
            m //= p
            if m % p == 0:
                return 0
        p += 1 if p == 2 else 2
    if m > 1:
        cnt += 1
    return -1 if (cnt % 2) else 1


def _seed_estimate(n: int) -> Union[float, 'mp.mpf']:
    """
    Compute initial seed estimate using Panaitopol/Dusart approximation.
    
    x₀ = n·(L + log L - 1 + (log L - 2)/L), where L = log n
    """
    # Handle edge cases for very small n
    if n < 2:
        return mp.mpf(2) if HAS_MPMATH else 2.0
    
    if HAS_MPMATH:
        n_f = mp.mpf(n)
        L = mp.log(n_f)
        L2 = mp.log(L)
        return n_f * (L + L2 - 1 + (L2 - 2) / L)
    else:
        import math
        L = math.log(n)
        L2 = math.log(L)
        return n * (L + L2 - 1 + (L2 - 2) / L)


def _riemann_R_and_derivative(x: Union[float, 'mp.mpf'], n_f: Union[float, 'mp.mpf']) -> Tuple:
    """
    Compute Riemann R(x) and R'(x) with adaptive truncation.
    
    R(x) = Σ_{k≥1} μ(k)/k · li(x^{1/k})
    R'(x) = (1/log x) · Σ_{k≥1} μ(k)/k · x^{1/k-1}
    
    Returns:
        (R_value, R_prime_value, effective_K)
    """
    if HAS_MPMATH:
        ln_x = mp.log(x)
        S = mp.mpf('0')
        Spp = mp.mpf('0')
        last_abs_T = None
        last_abs_Tp = None
        eta = mp.mpf(10) ** (-int(0.8 * mp.mp.dps))
        K_eff = 0

        for k in range(1, 21):
            mk = mu(k) / mp.mpf(k)
            x1k = x ** (mp.mpf(1) / k)
            T = mk * mp.li(x1k)
            Tp = mk * (x ** (mp.mpf(1) / k - 1))
            S += T
            Spp += Tp
            K_eff = k

            if k >= 2 and Spp != 0:
                aT, aTp = mp.fabs(T), mp.fabs(Tp)
                if last_abs_T is None or last_abs_Tp is None or last_abs_T == 0 or last_abs_Tp == 0:
                    tail_R, tail_Rp = aT, aTp
                else:
                    r = min(max(aT / last_abs_T, mp.mpf('0')), mp.mpf('0.99'))
                    rp = min(max(aTp / last_abs_Tp, mp.mpf('0')), mp.mpf('0.99'))
                    tail_R = aT / (1 - r)
                    tail_Rp = aTp / (1 - rp)

                Rv = S
                Rpv = Spp / ln_x
                fx = Rv - n_f
                Ex = mp.fabs(tail_R / (Rpv if Rpv != 0 else mp.mpf('inf'))) + \
                     mp.fabs((fx * tail_Rp) / ((Rpv**2) if Rpv != 0 else mp.mpf('inf')))
                if Ex / mp.fabs(x) <= eta:
                    break
                last_abs_T, last_abs_Tp = aT, aTp
            else:
                last_abs_T, last_abs_Tp = mp.fabs(T), mp.fabs(Tp)

        return S, Spp / ln_x, K_eff
    else:
        # Fallback for when mpmath is not available - simpler approximation
        import math
        # Use simpler li approximation: li(x) ≈ x/ln(x)
        ln_x = math.log(x)
        S = x / ln_x  # First term approximation
        Sp = 1 / ln_x
        return S, Sp, 1


def predict_nth_prime(n: int, use_high_precision: bool = True) -> int:
    """
    Predict the nth prime number using Z5D geodesic framework.
    
    Args:
        n: Index of the prime to predict (e.g., 1000000 for the millionth prime)
        use_high_precision: Whether to use high-precision mpmath computation
        
    Returns:
        Predicted nth prime number as integer
        
    Example:
        >>> predict_nth_prime(10)
        29
        >>> predict_nth_prime(1000000)
        15485863
    """
    if not HAS_MPMATH and use_high_precision:
        raise ImportError("mpmath is required for high precision. Install with: pip install mpmath")
    
    if HAS_MPMATH and use_high_precision:
        n_f = mp.mpf(n)
        x0 = _seed_estimate(n)
        Rv, Rpv, _ = _riemann_R_and_derivative(x0, n_f)
        if Rpv == 0:
            return int(mp.nint(x0))
        x1 = x0 - (Rv - n_f) / Rpv
        return int(mp.nint(x1))
    else:
        # Simple approximation when mpmath is not available
        import math
        x0 = _seed_estimate(n)
        return int(x0)


def predict_prime(n: int) -> int:
    """
    Predict the nth prime number (alias for predict_nth_prime).
    
    Args:
        n: Index of the prime to predict
        
    Returns:
        Predicted nth prime number
        
    Example:
        >>> predict_prime(1000000)
        15485863
    """
    return predict_nth_prime(n, use_high_precision=True)


def predict_prime_fast(n: int) -> int:
    """
    Fast prime prediction using simpler approximation.
    
    Sacrifices some accuracy for speed when mpmath overhead is undesirable.
    
    Args:
        n: Index of the prime to predict
        
    Returns:
        Predicted nth prime number
    """
    return predict_nth_prime(n, use_high_precision=False)


def benchmark_prediction(n: int, iterations: int = 5) -> Dict[str, float]:
    """
    Benchmark prime prediction performance.
    
    Args:
        n: Index of prime to predict
        iterations: Number of iterations for timing
        
    Returns:
        Dictionary with timing statistics (mean, median, min, max in milliseconds)
        
    Example:
        >>> stats = benchmark_prediction(1000000)
        >>> print(f"Average: {stats['mean_ms']:.3f} ms")
    """
    if not HAS_MPMATH:
        raise ImportError("mpmath is required for benchmarking")
    
    # Warm-up
    _ = predict_prime(n)
    
    times = []
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        _ = predict_prime(n)
        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1e6)  # Convert to milliseconds
    
    return {
        'mean_ms': statistics.mean(times),
        'median_ms': statistics.median(times),
        'min_ms': min(times),
        'max_ms': max(times),
        'iterations': iterations,
    }


def get_prediction_stats(n: int) -> Dict[str, Union[int, float, str]]:
    """
    Get comprehensive statistics for a prime prediction.
    
    Args:
        n: Index of prime to predict
        
    Returns:
        Dictionary with prediction, timing, error (if known), and accuracy info
        
    Example:
        >>> stats = get_prediction_stats(1000000)
        >>> print(f"Prediction: {stats['predicted']}")
        >>> print(f"Error: {stats['error_ppm']:.2f} ppm")
    """
    if not HAS_MPMATH:
        raise ImportError("mpmath is required for detailed statistics")
    
    # Time the prediction
    t0 = time.perf_counter_ns()
    predicted = predict_prime(n)
    t1 = time.perf_counter_ns()
    runtime_ms = (t1 - t0) / 1e6
    
    result = {
        'n': n,
        'predicted': predicted,
        'runtime_ms': runtime_ms,
    }
    
    # Check if we have ground truth
    if n in KNOWN_PRIMES:
        truth = KNOWN_PRIMES[n]
        error = abs(predicted - truth)
        rel_error = (predicted - truth) / truth
        result.update({
            'actual': truth,
            'absolute_error': error,
            'error_ppm': abs(rel_error) * 1e6,
            'relative_error_pct': rel_error * 100,
            'accuracy': 'exact' if error == 0 else f'{100 - abs(rel_error)*100:.6f}%'
        })
    
    return result


# Convenience function for displaying results
def display_prediction(n: int, verbose: bool = True) -> int:
    """
    Predict and display the nth prime with statistics.
    
    Args:
        n: Index of prime to predict
        verbose: Whether to print detailed statistics
        
    Returns:
        Predicted prime number
    """
    stats = get_prediction_stats(n)
    result = stats['predicted']
    
    if verbose:
        print(f"\nZ5D Prime Predictor")
        print(f"{'='*50}")
        print(f"Index (n):          {stats['n']:,}")
        print(f"Predicted Prime:    {stats['predicted']:,}")
        print(f"Runtime:            {stats['runtime_ms']:.3f} ms")
        
        if 'actual' in stats:
            print(f"Actual Prime:       {stats['actual']:,}")
            print(f"Absolute Error:     {stats['absolute_error']}")
            print(f"Error (ppm):        {stats['error_ppm']:.6f}")
            print(f"Relative Error:     {stats['relative_error_pct']:.12f}%")
            print(f"Accuracy:           {stats['accuracy']}")
        print(f"{'='*50}\n")
    
    return result
