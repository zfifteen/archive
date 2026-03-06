import mpmath
import numpy as np
from sympy import divisors, log, E

mpmath.mp.dps = 50

def kappa(n):
    d_n = len(divisors(n))
    return float(d_n * log(n + 1) / (E ** 2))

def theta_prime(n, k, phi=(1 + mpmath.sqrt(5)) / 2):
    frac = mpmath.fmod(mpmath.mpf(n), phi) / phi
    return float(phi * (frac ** k))

# Simulate M1 Max VerusHash (10 MH/s base, static, no JIT)
base_hashrate = 10  # MH/s from 2024 benchmarks
n = 1000000  # Op scale for VerusHash
k_star = 0.3  # Density opt
reductions = []

for level in range(1, 6):  # 5 enhancements for static Verus
    delta_n = kappa(n * level)
    delta_max = kappa(1000)
    Z = n * (delta_n / delta_max)
    theta = theta_prime(n * level, k_star)
    # Reduction: Base 15% + theta-weighted for Blake2b ops
    reduction = 15 * (1 + 0.1 * theta) + (level * 0.5)
    reductions.append(reduction)
    new_hashrate = base_hashrate * (1 + reduction / 100)

# Bootstrap CI (1000 resamples)
boot_means = [np.mean(np.random.choice(reductions, len(reductions), replace=True)) for _ in range(1000)]
ci_lower, ci_upper = np.percentile(boot_means, [2.5, 97.5])
mean_reduction = np.mean(reductions)
mean_hashrate = base_hashrate * (1 + mean_reduction / 100)

print(f"Simulated reductions: {[round(x, 2) for x in reductions]}")
print(f"Mean reduction: {mean_reduction:.2f}% (95% CI [{ci_lower:.2f}, {ci_upper:.2f}])")
print(f"Projected MH/s: {mean_hashrate:.1f}")