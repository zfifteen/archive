import mpmath as mp
from geodesic_utils import theta_prime

def factor_naive(n, max_iters=1000000):
    sqrt_n = int(mp.sqrt(n))
    count = 0
    for i in range(2, sqrt_n + 1):
        if count >= max_iters:
            return None
        if n % i == 0:
            q = n // i
            return i, q
        count += 1
    return None

def factor_z5d(n, k=0.3):
    sqrt_n = int(mp.sqrt(n))
    start = max(3, sqrt_n - 100000)
    end = min(n, sqrt_n + 100000)
    for cand in range(start, end, 2):
        if n % cand == 0:
            q = n // cand
            return cand, q
    return None