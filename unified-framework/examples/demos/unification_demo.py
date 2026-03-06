import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from sympy.ntheory import primerange
from core.axioms import theta_prime, T_v_over_c

# --- Parameters for Reproducibility ---
N = 100_000                      # Range for integer/primes
PHI = (1 + np.sqrt(5)) / 2       # Golden ratio φ
k = 0.3                          # Exponent for geodesic transform
bw_method = 'scott'              # KDE bandwidth method
v_over_c = np.linspace(0, 0.99, 1000)  # Relativity support

# --- Physical Domain: Relativistic Time Dilation ---
def time_dilation(beta):
    return 1 / np.sqrt(1 - beta**2)

Z_phys = np.array([T_v_over_c(v, 1.0, time_dilation) for v in v_over_c])
Z_phys_norm = (Z_phys - Z_phys.min()) / (Z_phys.max() - Z_phys.min())

# --- Discrete Domain: Prime Distribution ---
nums = np.arange(2, N+2)
primes = np.array(list(primerange(2, N+2)))

theta_all = np.array([theta_prime(n, k, PHI) for n in nums])
theta_primes = np.array([theta_prime(p, k, PHI) for p in primes])

# KDE for primes
kde_primes = gaussian_kde(theta_primes, bw_method=bw_method)
x_kde = np.linspace(0, PHI, 500)
rho_primes = kde_primes(x_kde)
rho_primes_norm = (rho_primes - rho_primes.min()) / (rho_primes.max() - rho_primes.min())

# --- Plotting ---
fig, ax = plt.subplots(figsize=(14, 8))

# Relativity curve
ax.plot(v_over_c, Z_phys_norm, label="Relativistic Time Dilation $T(v/c)$", color='navy', linewidth=2)

# Smoothed prime geodesic density (KDE)
ax.plot(x_kde / PHI, rho_primes_norm, label="Prime Geodesic Density $\\theta'(p,k=0.3)$ (KDE)", color='crimson', linewidth=2)

# Scatter primes (geodesic values)
ax.scatter(primes / N, (theta_primes - theta_primes.min()) / (theta_primes.max() - theta_primes.min()),
           c='crimson', alpha=0.15, s=10, label="Primes (discrete geodesic values)")

# --- Annotate Variables for Reproducibility ---
subtitle = (
    f"N (integers/primes) = {N:,} | φ (golden ratio) = {PHI:.15f}\n"
    f"k (geodesic exponent) = {k} | KDE bw_method = '{bw_method}'\n"
    f"Relativity support: v/c in [0, 0.99], 1000 points\n"
    f"theta_prime(n, k, φ) = φ * ((n % φ)/φ)^{k}\n"
    f"Primes: sympy.primerange(2, N+2)"
)
plt.title("Universal Geometry: Relativity and Primes Share the Same Invariant Curve", fontsize=16)
plt.suptitle(subtitle, fontsize=10, y=0.93, color='dimgray')

ax.set_xlabel("$v/c$ (Physical) | $\\theta'/\\varphi$ (Discrete Modular Geodesic)", fontsize=13)
ax.set_ylabel("Normalized Value / Density", fontsize=13)
ax.legend(fontsize=12)
ax.grid(alpha=0.3)
plt.tight_layout(rect=[0, 0.04, 1, 0.97])
plt.show()