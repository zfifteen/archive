#!/usr/bin/env python3
"""
Full Δₚ & Δ_q Analysis and Z-Metric Distance Distributions
"""

import math
import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis
from scipy.spatial.distance import pdist

# 1. Primality Test
def is_prime(k):
    if k < 2 or (k % 2 == 0 and k != 2):
        return False
    r = int(math.sqrt(k))
    for i in range(3, r + 1, 2):
        if k % i == 0:
            return False
    return True

# 2. Sample semiprime pairs returning Δₚ and Δ_q
def sample_semiprime_deltas(n_samples, n_min, n_max, balance_tol):
    results = []
    for _ in range(n_samples):
        r = random.uniform(math.sqrt(n_min), math.sqrt(n_max))
        p_lo, p_hi = int(r*(1-balance_tol)), int(r*(1+balance_tol))
        q_lo, q_hi = p_lo, p_hi

        # sample p
        p = random.randint(max(2, p_lo), p_hi)
        while p <= p_hi and not is_prime(p):
            p += 1
        if not is_prime(p):
            continue

        # sample q
        q = random.randint(max(2, q_lo), q_hi)
        while q <= q_hi and not is_prime(q):
            q += 1
        if not is_prime(q):
            continue

        n   = p * q
        s   = math.sqrt(n)
        dp  = s - p
        dq  = s - q
        results.append((dp, dq))
    return np.array(results)

# 3. Settings
tols      = [0.01, 0.05, 0.10, 0.20]
n_samples = 5000
n_min, n_max = 10**8, 10**9

# 4. Data collection
all_data = {}
for tol in tols:
    arr = sample_semiprime_deltas(n_samples, n_min, n_max, tol)
    all_data[tol] = arr
    print(f"tol={tol:.2f}: collected {len(arr)} pairs")

# 5. Moment Quantification for Δₚ
moments = []
for tol, arr in all_data.items():
    dp = arr[:,0]
    moments.append({
        "tol": tol,
        "mean":   np.mean(dp),
        "var":    np.var(dp),
        "skew":   skew(dp),
        "kurt":   kurtosis(dp)
    })

# 6. Print moments as a table
print("\ntol   mean       var        skew       kurtosis")
for m in moments:
    print(f"{m['tol']:<5.2f} {m['mean']:>8.3f} {m['var']:>10.3f} "
          f"{m['skew']:>9.3f} {m['kurt']:>11.3f}")

# 7. CDF and Quantile Plots of |Δₚ|
plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
for tol in tols:
    dp = np.abs(all_data[tol][:,0])
    sns.ecdfplot(dp, label=f"{tol:.2f}")
plt.title("CDF of |Δₚ|")
plt.xlabel("|Δₚ|")
plt.ylabel("ECDF")
plt.legend(title="tol")

plt.subplot(1,2,2)
quantiles = np.linspace(0,1,100)
for tol in tols:
    dp = np.abs(all_data[tol][:,0])
    qs = np.quantile(dp, quantiles)
    plt.plot(quantiles, qs, label=f"{tol:.2f}")
plt.title("Quantile Curves of |Δₚ|")
plt.xlabel("Quantile")
plt.ylabel("|Δₚ| value")
plt.legend(title="tol")
plt.tight_layout()
plt.show()

# 8. Joint Δₚ–Δ_q Scatter (for a subsample)
plt.figure(figsize=(6,6))
for tol in tols:
    sample = all_data[tol]
    idx    = np.random.choice(len(sample), size=500, replace=False)
    plt.scatter(sample[idx,0], sample[idx,1], alpha=0.4, label=f"{tol:.2f}")
plt.title("Δₚ vs Δ_q Scatter")
plt.xlabel("Δₚ")
plt.ylabel("Δ_q")
plt.legend(title="tol")
plt.tight_layout()
plt.show()

# 9. Z-Metric Distances: Euclidean on (Δₚ, Δ_q)
plt.figure(figsize=(10,5))
for tol in tols:
    pts = all_data[tol]
    # compute pairwise distances on a random subset
    subset = pts[np.random.choice(len(pts), 300, replace=False)]
    dists  = pdist(subset, metric='euclidean')
    sns.kdeplot(dists, label=f"{tol:.2f}", fill=True, alpha=0.3)
plt.title("Z-Metric Distance Distributions")
plt.xlabel("Distance")
plt.ylabel("Density")
plt.legend(title="tol")
plt.tight_layout()
plt.show()
