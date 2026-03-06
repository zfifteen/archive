import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mpmath as mp
import pandas as pd

mp.mp.dps = 50  # High precision

PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)

import core.axioms
# axioms
K = mp.mpf(mp.pi / mp.e)

CSV_FILE = 'zeta_zeros.csv'
N = 500

def compute_zeta_zeros(n):
    zeros = []
    for k in range(1, n + 1):
        zero = mp.zetazero(k)
        imag_part = mp.im(zero)
        zeros.append(float(imag_part))  # Convert to float for storage
    return zeros

# Load or compute zeros
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    t = df['zeros'].tolist()
    if len(t) < N:
        print(f"Existing file has only {len(t)} zeros, recomputing...")
        t = compute_zeta_zeros(N)
        pd.DataFrame({'zeros': t}).to_csv(CSV_FILE, index=False)
else:
    t = compute_zeta_zeros(N)
    pd.DataFrame({'zeros': t}).to_csv(CSV_FILE, index=False)

# Compute 3D helical coordinates
xs, ys, zs = [], [], []
for j in range(1, N + 1):
    a = mp.mpf(j)
    b = mp.mpf(t[j - 1])
    c = E_SQUARED
    if a == 0 or b == 0:
        continue  # Skip invalid
    D = c / a
    E = c / b
    d_over_e = D / E
    F = PHI * ((d_over_e % PHI) / PHI) ** K
    theta_d = PHI * ((D % PHI) / PHI) ** K
    theta_e = PHI * ((E % PHI) / PHI) ** K
    x = a * mp.cos(theta_d)
    y = a * mp.sin(theta_e)
    z = F / E_SQUARED
    xs.append(float(x))
    ys.append(float(y))
    zs.append(float(z))

# Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xs, ys, zs, c='r', marker='o', s=20)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Helical Embedding of First 500 Riemann Zeta Zeros')

# Legend with parameters
legend_text = f'φ ≈ {float(PHI):.3f}\nk* = {float(K)}\ne² ≈ {float(E_SQUARED):.3f}'
ax.text2D(0.05, 0.95, legend_text, transform=ax.transAxes, fontsize=12,
          verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

plt.show()