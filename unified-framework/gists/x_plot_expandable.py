import mpmath as mp
import numpy as np
import matplotlib.pyplot as plt
from sympy import divisors
from src.core.params import KAPPA_GEO_DEFAULT as kappa_geo  # ≈0.3 from params.py

# High precision (Z Framework: target Δ_n < 1e-16)
mp.mp.dps = 50

# Enhanced exponents: k = 1..18 with 5 sub-values within each k band
exponents_base = list(range(1, 18))
exponents = []
n_values = []

# Create fine-grained k values: for each integer k, add k + 0.0, k + 0.2, k + 0.4, k + 0.6, k + 0.8
for k in exponents_base:
    for sub_k in [0.0, 0.2, 0.4, 0.6, 0.8]:
        k_fine = k + sub_k
        exponents.append(k_fine)
        n_values.append(mp.mpf(10) ** k_fine)

phi = (1 + mp.sqrt(5)) / 2


# x= ((n/π) / φ)
x_values = [(( n / mp.pi) /  phi ) for n in n_values]

# θ'(n, kappa_geo≈0.3) = φ * frac(n/φ)^{kappa_geo}
frac_parts = [mp.frac(n / phi) for n in n_values]
theta_prime = [phi * mp.power(frac, kappa_geo) for frac in frac_parts]

# Vortex O (κ(n) = d(n) · ln(n+1) / e²), mean over k=1..5 (using base k values only)
def kappa(n):
    n_int = int(n)
    return len(divisors(n_int)) * (mp.log(n_int + 1) / (mp.e ** 2))

# Calculate vortex_o using only the base integer k values for consistency
base_n_values = [mp.mpf(10) ** k for k in exponents_base[:5]]
vortex_o = np.mean([float(kappa(n)) for n in base_n_values])
print(f"Vortex O: {vortex_o:.6f}")  # Expect ~2.919

# Prepare arrays for plotting
x_arr = np.array([float(x) for x in x_values])
theta_arr = np.array([float(t) for t in theta_prime])
k_arr = np.array(exponents)

# Enhanced plotting with more data points
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Plot 1: x vs. log10(n) with fine-grained points
ax1.plot(k_arr, x_arr, marker='o', markersize=3, linestyle='-', linewidth=0.8,
         label='x = n / (π φ)', alpha=0.7)
# Highlight the main k values (integers)
main_k_indices = [i for i, k_val in enumerate(k_arr) if abs(k_val - round(k_val)) < 1e-10]
ax1.scatter(k_arr[main_k_indices], x_arr[main_k_indices],
           color='red', s=30, zorder=5, label='Main k values', alpha=0.8)
ax1.set_xlabel('k (log₁₀ n)')
ax1.set_ylabel('x')
ax1.set_title('Z Framework: Fine-Grained Scaled Invariant x vs. k')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot 2: θ' vs. k with fine-grained points
ax2.plot(k_arr, theta_arr, marker='o', markersize=3, linestyle='-', linewidth=0.8,
         color='orange', label="θ'(n, κ≈0.3)", alpha=0.7)
# Highlight the main k values (integers)
ax2.scatter(k_arr[main_k_indices], theta_arr[main_k_indices],
           color='red', s=30, zorder=5, label='Main k values', alpha=0.8)
ax2.axhline(y=float(np.mean(theta_arr)), color='r', linestyle='--',
            label=f'Mean ≈ {np.mean(theta_arr):.3f}')
ax2.set_xlabel('k')
ax2.set_ylabel("θ'")
ax2.set_title("Geodesic Pattern: Fine-Grained θ'(10^k, κ≈0.3) (Equidistribution)")
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig('x_theta_plot_fine_grained.png', dpi=300)
plt.show()

# Print values for verification (showing first few and last few for brevity)
print(f"\nComputed Values (Z Framework — Fine-Grained Discrete Domain):")
print(f"Total data points: {len(k_arr)}")
print("k        | x        | θ'")
print("-" * 35)

# Show first 10 points
for i in range(min(10, len(k_arr))):
    print(f"{k_arr[i]:8.1f} | {x_arr[i]:8.6f} | {theta_arr[i]:8.6f}")

if len(k_arr) > 20:
    print("...")
    # Show last 10 points
    for i in range(max(10, len(k_arr)-10), len(k_arr)):
        print(f"{k_arr[i]:8.1f} | {x_arr[i]:8.6f} | {theta_arr[i]:8.6f}")

# Additional analysis: variance within k bands
print(f"\nVariance Analysis within k bands:")
print("k band | x variance    | θ' variance")
print("-" * 40)

for k_base in exponents_base[:10]:  # Show first 10 bands
    # Find indices for this k band
    band_mask = (k_arr >= k_base) & (k_arr < k_base + 1)
    band_indices = np.where(band_mask)[0]
    if len(band_indices) > 0:
        x_band = x_arr[band_indices]
        theta_band = theta_arr[band_indices]
        x_var = np.var(x_band)
        theta_var = np.var(theta_band)
        print(f"{k_base:6d} | {x_var:12.8f} | {theta_var:12.8f}")
