import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import bootstrap
from numpy import pi

sns.set(style="whitegrid")

# ----------------------------------------------------------------------
# 1. Simulate Scaled Riemann Zeros (cluster2 approximation)
# ----------------------------------------------------------------------
n_zeros = 2000
# Replace with actual scaled zeros array when available
scaled_zeros = np.sort(np.random.normal(loc=30, scale=5, size=n_zeros))

# ----------------------------------------------------------------------
# 2. Spectral Form Factor (SFF)
# ----------------------------------------------------------------------
def compute_sff(zeros, taus):
    """Compute normalized Spectral Form Factor."""
    N = len(zeros)
    return np.array([np.abs(np.sum(np.exp(1j * tau * zeros)))**2 / N for tau in taus])

# Bootstrap error bars for SFF
n_boot = 200
taus = np.linspace(0.01, 5, 300)
sffs_boot = []
for _ in range(n_boot):
    sample = np.random.choice(scaled_zeros, size=n_zeros, replace=True)
    sffs_boot.append(compute_sff(sample, taus))
sffs_boot = np.array(sffs_boot)
sff_mean = sffs_boot.mean(axis=0)
sff_std = sffs_boot.std(axis=0)

# Plot SFF
plt.figure(figsize=(8, 5))
plt.plot(taus, sff_mean, color='C0', label='Mean SFF')
plt.fill_between(taus, sff_mean - sff_std, sff_mean + sff_std,
                 color='C0', alpha=0.3, label='±1σ (bootstrap)')
plt.axvline(1, color='k', linestyle='--', alpha=0.5)
plt.title('Spectral Form Factor (Cluster2)')
plt.xlabel('τ')
plt.ylabel('K(τ) / N')
plt.legend()
plt.tight_layout()
plt.savefig('sff_cluster2.png')
plt.close()

# ----------------------------------------------------------------------
# 3. Two-Point Correlation Function R₂(s)
# ----------------------------------------------------------------------
def empirical_r2(spacings, s_max=5, bins=200):
    """Empirical two-point correlation histogram of spacings."""
    hist, edges = np.histogram(spacings, bins=bins, range=(0, s_max), density=True)
    centers = (edges[:-1] + edges[1:]) / 2
    return centers, hist

def gue_sine_kernel(s):
    """GUE sine-kernel two-point correlation."""
    return 1 - (np.sin(pi * s) / (pi * s))**2

# Compute nearest-neighbor spacings
spacings = np.diff(scaled_zeros)
s_vals, r2_emp = empirical_r2(spacings)

# Plot R2(s)
plt.figure(figsize=(8, 5))
plt.plot(s_vals, r2_emp, color='C2', label='Empirical R₂(s)')
plt.plot(s_vals, gue_sine_kernel(s_vals), '--', color='C3', label='GUE sine kernel')
plt.title('Two-Point Correlation Function R₂(s)')
plt.xlabel('s (normalized spacing)')
plt.ylabel('R₂(s)')
plt.legend()
plt.tight_layout()
plt.savefig('r2_cluster2.png')
plt.close()

# ----------------------------------------------------------------------
# 4. Helical Embedding of Scaled Riemann Zeros
# ----------------------------------------------------------------------
phi = (1 + np.sqrt(5)) / 2
n = np.arange(n_zeros)
angles = 2 * pi * n / phi
radii = scaled_zeros
theta_prime = phi * ((n % phi) / phi)**3.33  # θ'(n, k*=3.33)

# Polar plot
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='polar')
sc = ax.scatter(angles, radii, c=theta_prime, cmap='viridis', s=15)
ax.set_title('Helical Embedding on Golden-Ratio Spiral')
cbar = plt.colorbar(sc, ax=ax, pad=0.1)
cbar.set_label("θ'(n, k*=3.33)")
plt.savefig('helical_embedding_cluster2.png')
plt.close()
