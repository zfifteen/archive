import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from core.orbital import orbital_periods, pairwise_ratios, theta_prime
import mpmath as mp

# --- PARAMETERS FOR REPRODUCTION ---
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
k = 0.3                     # Geodesic exponent
N = len(orbital_periods)    # Number of planets

# --- 1. Compute sorted pairwise orbital period ratios ---
ratios_data = pairwise_ratios(orbital_periods)
labels, ratios = zip(*ratios_data)
ratios = np.array(ratios)

# --- 2. Geodesic modular transformation θ'(ratio, k) on orbital ratios ---
theta_ratios = np.array([theta_prime(r, k, PHI) for r in ratios])

# --- 3. Get first len(ratios) Riemann zeta zeros (imaginary part only) ---
num = len(theta_ratios)
zeta_zeros = [float(mp.zetazero(i+1).imag) for i in range(num)]

# --- 4. Compute normalized spacings between consecutive zeros ---
zeta_spacings = np.diff(zeta_zeros)
zeta_spacings_norm = (zeta_spacings - np.min(zeta_spacings)) / (np.max(zeta_spacings) - np.min(zeta_spacings))

# Align theta_ratios and zeta_spacings to same length for correlation
theta_ratios_aligned = np.sort(theta_ratios[:-1])
zeta_spacings_aligned = np.sort(zeta_spacings_norm)

# --- 5. Pearson correlation coefficient ---
r, p = pearsonr(theta_ratios_aligned, zeta_spacings_aligned)

# --- 6. Plotting ---
plt.figure(figsize=(10, 6))
plt.plot(theta_ratios_aligned, zeta_spacings_aligned, 'o-', color='purple', label="Aligned, sorted data")
plt.title(
    "Empirical Correlation: Geodesic Orbital Ratios vs. Riemann Zeta Zero Spacings\n"
    f"Pearson r = {r:.3f} (p = {p:.2g})"
)
plt.xlabel("Geodesic Orbital Ratio θ'(ratio, k=0.3)")
plt.ylabel("Normalized Zeta Zero Spacing")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

# --- 7. Show parameters for full reproducibility ---
subtitle = (
    f"orbital_periods = {list(orbital_periods.keys())}\n"
    f"PHI = {PHI:.15f}, k = {k}, N_pairs = {len(ratios)}\n"
    "θ'(n, k) = φ · {n/φ}^k where {x} is the fractional part of x\n"
    "Zeta zeros: mpmath.zetazero(i+1).imag"
)
plt.figtext(0.5, 0.01, subtitle, ha='center', fontsize=9, color='dimgray')

plt.show()

print(f"Pearson correlation between sorted geodesic orbital ratios and normalized zeta zero spacings: r = {r:.3f} (p = {p:.2g})")