import numpy as np
import matplotlib.pyplot as plt
from mpmath import mp, ln, e, mpf
from sympy.ntheory.factor_ import divisors
from tqdm import tqdm

# High precision
mp.dps = 50
delta_max = e ** 2

def divisor_count(n):
    return len(divisors(n))

def curvature_kappa(n):
    return mpf(divisor_count(n)) * ln(n + 1) / delta_max

def z_value(n):
    return mpf(n) * curvature_kappa(n) / delta_max

# Generate data
n_vals = np.arange(1, 100001)
kappa_vals = []
z_vals = []

for n in tqdm(n_vals, desc="Computing κ(n) and Z(n)"):
    kappa = curvature_kappa(n)
    z = z_value(n)
    kappa_vals.append(float(kappa))  # truncate AFTER mpf calc
    z_vals.append(float(z))

# Plot κ(n)
plt.figure(figsize=(12, 5))
plt.plot(n_vals, kappa_vals, color="darkblue", linewidth=0.5)
plt.title("Frame-Normalized Curvature κ(n) up to n = 100,000")
plt.xlabel("n")
plt.ylabel("κ(n)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot Z(n)
plt.figure(figsize=(12, 5))
plt.plot(n_vals, z_vals, color="darkgreen", linewidth=0.5)
plt.title("Z Model Value Z(n) up to n = 100,000")
plt.xlabel("n")
plt.ylabel("Z(n)")
plt.grid(True)
plt.tight_layout()
plt.show()
