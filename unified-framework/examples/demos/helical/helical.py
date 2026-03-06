import numpy as np
import matplotlib.pyplot as plt
from sympy import isprime
from core.domain import DiscreteZetaShift, E_SQUARED, PHI

# Parameters used for reproducibility
N0 = 500000
N1 = 1000000
v = 1.0
delta_max = E_SQUARED
phi = float(PHI)
theta_k = 0.3

coords = []
is_primes = []
for n in range(N0, N1 + 1):
    zeta = DiscreteZetaShift(n, v=v, delta_max=delta_max)
    coords.append(zeta.get_3d_coordinates())
    is_primes.append(isprime(n))

coords = np.array(coords)
is_primes = np.array(is_primes)

fig = plt.figure(figsize=(12,10))
ax = fig.add_subplot(111, projection='3d')

# Plotting
ax.scatter(coords[~is_primes, 0], coords[~is_primes, 1], coords[~is_primes, 2],
           c='skyblue', alpha=0.3, s=1, label='Composites')
ax.scatter(coords[is_primes, 0], coords[is_primes, 1], coords[is_primes, 2],
           c='red', alpha=0.7, s=8, label='Primes')

# Title and parameter annotation
title = (f"Helical Embedding of n={N0}..{N1} (Primes Highlighted)\n"
         f"Parameters: v={v}, delta_max={delta_max:.4f}, φ={phi:.6f}, θ' k={theta_k}")
ax.set_title(title, fontsize=12)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()

# Add text box with parameters for clarity (optional, redundant with title)
param_text = (
    f"N0 = {N0}\n"
    f"N1 = {N1}\n"
    f"v = {v}\n"
    f"delta_max = {delta_max:.4f}\n"
    f"φ = {phi:.6f}\n"
    f"theta_prime k = {theta_k}"
)
plt.gcf().text(0.02, 0.02, param_text, fontsize=10, family='monospace', va='bottom', ha='left',
               bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

plt.tight_layout()
plt.show()