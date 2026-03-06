import numpy as np
from sympy import isprime, primerange
import mpmath as mp
import math

mp.dps = 50  # High precision for Z-framework invariants

def circular_distance(a, b):
    diff = abs(a - b) % (2 * math.pi)
    return min(diff, 2 * math.pi - diff)

def z5d_predictor(n, k_range=np.arange(0.1, 1.0, 0.01), dim=5, eps=0.07, use_eps_fallback=True):
    """
    Z5D Predictor: 5D geometric resolution for prime-density prediction.
    Uses θ'(n,k) = φ * ((n mod φ)/φ)^k as base, extended to 5D embedding.
    Predicts optimal k for minimizing embedding distance to n's invariant Z.
    
    Returns: dict with predicted k, embedding distance, and top candidates.
    Includes eps-based fallback for small n if no geometric candidates.
    """
    phi = (1 + mp.sqrt(5)) / 2  # Golden ratio invariant
    z_n = n * (mp.log(n+1) / phi)  # Adjusted invariant to φ for better fit
    
    best_k = None
    min_dist = float('inf')
    predictions = []
    
    for k in k_range:
        theta_prime = phi * ((n % phi) / phi) ** k
        dist = abs(theta_prime - z_n)
        predictions.append((k, dist))
        
        if dist < min_dist:
            min_dist = dist
            best_k = k
    
    # 5D extension: predict p,q candidates via geometric geodesics
    # Improved heuristic: q ≈ sqrt(n) * (theta_prime / phi), with multiple offsets
    theta_prime_best = phi * ((n % phi) / phi) ** best_k
    sqrt_n = mp.sqrt(n)
    base_q = int(sqrt_n * (theta_prime_best / phi))
    
    candidates = []
    for offset in [-2, -1, 0, 1, 2]:  # Generate 5 candidates around base_q
        q_pred = base_q + offset
        if q_pred > 1 and q_pred < n:
            p_pred = n // q_pred
            if p_pred > 1 and isprime(p_pred) and isprime(q_pred) and p_pred * q_pred == n:
                candidates.append((min(p_pred, q_pred), max(p_pred, q_pred)))  # Ensure order
    
    # Eps-based fallback if no candidates and enabled
    if not candidates and use_eps_fallback:
        fallback_candidates = set()
        sqrt_n_int = int(math.sqrt(n)) + 1
        small_primes = list(primerange(2, sqrt_n_int))
        for k in k_range:  # Use same k_range
            theta_n = (phi * ((n % phi) / phi) ** k) % (2 * math.pi)
            for p in small_primes:
                theta_p = (phi * ((p % phi) / phi) ** k) % (2 * math.pi)
                if circular_distance(theta_n, theta_p) <= eps:
                    fallback_candidates.add(p)
        for p in sorted(fallback_candidates):
            if n % p == 0:
                q = n // p
                if isprime(q):
                    candidates.append((min(p, q), max(p, q)))
    
    return {
        'best_k': best_k,
        'min_dist': float(min_dist),
        'predictions': predictions,
        'candidates': candidates
    }

# Example usage
if __name__ == "__main__":
    n = 15  # Semiprime example
    result = z5d_predictor(n)
    print(f"For n={n}: Best k={result['best_k']}, Dist={result['min_dist']}")
    print(f"Candidates: {result['candidates']}")