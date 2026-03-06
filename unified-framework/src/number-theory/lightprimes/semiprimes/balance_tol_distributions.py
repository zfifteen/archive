#!/usr/bin/env python3
"""
Plot Δ_p distributions for various balance_tol settings.

For each tolerance:
 1. Sample semiprimes (p, q) within ±tol × √n.
 2. Compute Δ_p = √n − p.
 3. Plot histogram + KDE of Δ_p.
"""

import math
import random
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# 1. Simple primality test for small k
def is_prime(k):
    if k < 2 or (k % 2 == 0 and k != 2):
        return False
    r = int(math.sqrt(k))
    for i in range(3, r + 1, 2):
        if k % i == 0:
            return False
    return True


# 2. Generate semiprime samples for a given balance_tol
def sample_semiprimes(n_samples, n_min, n_max, balance_tol):
    deltas = []
    for _ in range(n_samples):
        # pick a random value for sqrt(n)
        r = random.uniform(math.sqrt(n_min), math.sqrt(n_max))
        # sample p in [r(1-tol), r(1+tol)]
        p_start = int(max(2, r * (1 - balance_tol)))
        p_end = int(r * (1 + balance_tol))

        # find a prime p in that interval
        p = random.randint(p_start, p_end)
        while p < p_end and not is_prime(p):
            p += 1
        if not is_prime(p):
            continue

        # choose q similarly in the same window
        q = random.randint(p_start, p_end)
        while q < p_end and not is_prime(q):
            q += 1
        if not is_prime(q):
            continue

        n = p * q
        sqrt_n = math.sqrt(n)
        deltas.append(sqrt_n - p)
    return deltas


# 3. Settings
tols = [0.01, 0.05, 0.1, 0.2]
n_samples = 5000
n_min, n_max = 10 ** 8, 10 ** 9  # adjust range as needed

# 4. Collect Δ_p for each tol
delta_map = {}
for tol in tols:
    deltas = sample_semiprimes(n_samples, n_min, n_max, tol)
    delta_map[tol] = deltas
    print(f"Collected {len(deltas)} samples for tol={tol}")

# 5. Plotting
plt.figure(figsize=(10, 6))
colors = sns.color_palette("tab10", len(tols))

for i, tol in enumerate(tols):
    sns.histplot(
        delta_map[tol],
        kde=True,
        stat="density",
        bins=50,
        color=colors[i],
        alpha=0.4,
        label=f"tol = {tol:.2f}"
    )

plt.title("Distribution of Δₚ = √n − p for Various `balance_tol`")
plt.xlabel("Δₚ")
plt.ylabel("Density")
plt.legend(title="balance_tol")
plt.tight_layout()
plt.show()
