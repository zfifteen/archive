#!/usr/bin/env python3
"""
Reproducibility Code Snippets

Code to independently validate all statistical claims
"""

# Load correlation arrays
#==================================================

import numpy as np
import json
from scipy import stats

# Load correlation data
with open('correlation_data.json', 'r') as f:
    data = json.load(f)
a = np.array(data['array_a'])
b = np.array(data['array_b'])

# Compute correlation
r, p = stats.pearsonr(a, b)
print(f"r = {r:.4f}, p = {p:.4e}")


# KS test
#==================================================

import numpy as np
from scipy.stats import ks_2samp

# Load arrays
prime_vals = np.load('prime_chiral_distances.npy')
composite_vals = np.load('composite_chiral_distances.npy')

# KS test
ks_stat, p = ks_2samp(prime_vals, composite_vals)
print(f"KS stat = {ks_stat:.4f}, p = {p:.4e}")


# Bootstrap confidence interval
#==================================================

import numpy as np
from scipy import stats

# Assuming arrays a and b are loaded
boots = []
n = len(a)
for _ in range(10000):
    idx = np.random.randint(0, n, n)
    r_boot, _ = stats.pearsonr(a[idx], b[idx])
    boots.append(r_boot)

ci = np.percentile(boots, [2.5, 97.5])
print(f"95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")


# Cohen's d
#==================================================

import numpy as np

def cohens_d(x, y):
    nx, ny = len(x), len(y)
    s = np.sqrt(((nx-1)*x.std(ddof=1)**2 + (ny-1)*y.std(ddof=1)**2)/(nx+ny-2))
    return (x.mean()-y.mean())/s

# Load data and compute
x = np.load('prime_chiral_distances.npy')
y = np.load('composite_chiral_distances.npy')
d = cohens_d(x, y)
print(f"Cohen's d = {d:.4f}")


