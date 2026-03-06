import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import norm

# Z Transformers Implementation in Discrete Prime Domain
# Domain Curvature Transformation: Bends the 1D integer line into a curved geometric space
# Universal Form Transformer: Z = A(B/C), where A is density, B is rate (e.g., n/log n), C is limit (phi)
# Universal Frame Shift Transformer: Shifts observer frame n to universal r_u = (n_u, theta_u, phi_u)

def generate_primes(N):
    """Generate list of primes up to N using Sieve of Eratosthenes."""
    is_prime = np.ones(N+1, dtype=bool)
    is_prime[0:2] = False
    for i in range(2, int(np.sqrt(N))+1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return np.where(is_prime)[0]

# Parameters
N = 10000  # Upper limit for n
k = 0.55    # Scaling exponent: 1.0 for quadratic (current), 0.5 for Sacks-like sqrt(n)
use_sqrt_scaling = False  # Set to True to switch to k=0.5
if use_sqrt_scaling:
    k = 0.5

phi = (1 + np.sqrt(5)) / 2  # Golden ratio, invariant limit C in modular clustering
e = np.e
pi = np.pi
f_eff = 1 / phi  # Effective frequency for helical coordinate

# Generate primes and is_prime array
primes = generate_primes(N)
is_prime_mask = np.zeros(N+1, dtype=bool)
is_prime_mask[primes] = True

# n starts from 2 to N
n = np.arange(2, N+1, dtype=float)
log_n = np.log(n)
delta_n = 1 / log_n  # Frame shift Δ_n, density-inspired
delta_max = 1.0      # Maximum frame shift, invariant bound
B = n / log_n        # Rate B ≈ li(n), cumulative prime approximation

# Universal frame coordinates with tunable scaling
n_base = n ** k
n_u = n_base * (delta_n / delta_max)  # Frame-corrected position
theta_u = (n_base**2 / pi) * (B / e) * (1 + delta_n)  # Transformed radial/theta coordinate
phi_u = np.sin(pi * f_eff * n_base) * (1 + 0.5 * delta_n)  # Frame-aware helical coordinate

# Norm in universal frame
r_norm = np.sqrt(n_u**2 + theta_u**2 + phi_u**2)

# Modular projection onto phi-shells
mod_phi = r_norm % phi

# Prime indices (from n=2 onwards)
prime_indices = is_prime_mask[2:]
mod_phi_primes = mod_phi[prime_indices]

# Histograms for density analysis
num_bins = 10
bins = np.linspace(0, phi, num_bins + 1)
hist_all, _ = np.histogram(mod_phi, bins=bins, density=True)
hist_primes, _ = np.histogram(mod_phi_primes, bins=bins, density=True)

print("Density Histogram for all n (normalized):")
print(hist_all)
print("\nDensity Histogram for primes (normalized):")
print(hist_primes)

# Relative enhancement: (prime_density - all_density) / all_density
enhancement = (hist_primes - hist_all) / hist_all
print("\nRelative Enhancement in Prime Density per Bin:")
print(enhancement)

# Fourier Decomposition of prime density for analytic approximation
# Treat binned histogram as periodic signal over [0, phi)
fft_primes = np.fft.rfft(hist_primes)
a0 = fft_primes[0].real / num_bins
a_k = 2 * fft_primes[1:].real / num_bins
b_k = -2 * fft_primes[1:].imag / num_bins

print("\nFourier Coefficients for rho_prime(phi):")
print(f"a0 (baseline): {a0}")
for i in range(1, len(a_k) + 1):
    print(f"k={i}: a_{i} = {a_k[i-1]}, b_{i} = {b_k[i-1]}")

# Symbolic Fourier approximation (truncate to K=5)
def rho_fourier(phi_val, K=5):
    res = a0
    period = phi
    for k in range(1, K+1):
        res += a_k[k-1] * np.cos(2 * np.pi * k * phi_val / period) + b_k[k-1] * np.sin(2 * np.pi * k * phi_val / period)
    return res

# Example evaluation
phi_test = np.linspace(0, phi, 100)
rho_test = rho_fourier(phi_test)
print("\nExample rho_fourier at phi=0.24:", rho_fourier(0.24))
print("Example rho_fourier at phi=0.40:", rho_fourier(0.40))
print("Example rho_fourier at phi=0.89:", rho_fourier(0.89))

# Gaussian Mixture Approximation (manual, based on observed peaks)
# Centers at mid-resonance hotspots, sigma = phi/20
centers = [0.24, 0.40, 0.89]  # From peaks in bins 2,3,6
weights = [0.28, 0.41, 0.31]   # Proportional to excess density
weights = np.array(weights) / np.sum(weights)  # Normalize
sigma_gmm = phi / 20  # ~0.081

def rho_gmm(phi_val):
    res = 0
    for w, mu in zip(weights, centers):
        res += w * norm.pdf(phi_val, mu, sigma_gmm)
    # Add baseline adjusted for normalization
    baseline = (1 - np.sum(weights)) * (1 / phi)  # Uniform baseline
    return res + baseline

print("\nExample rho_gmm at phi=0.24:", rho_gmm(0.24))
print("Example rho_gmm at phi=0.40:", rho_gmm(0.40))
print("Example rho_gmm at phi=0.89:", rho_gmm(0.89))

# 3D Visualization in Universal Frame
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
# Plot all points (gray, small)
ax.scatter(n_u, theta_u, phi_u, c='gray', s=1, alpha=0.1, label='All n')
# Plot primes (red, larger)
ax.scatter(n_u[prime_indices], theta_u[prime_indices], phi_u[prime_indices], c='red', s=5, label='Primes')
ax.set_xlabel('n_u (Frame-Corrected Position)')
ax.set_ylabel('theta_u (Transformed Radial)')
ax.set_zlabel('phi_u (Helical Coordinate)')
ax.set_title('Prime Distribution in Universal Frame Shift (Z-Transformed)')
ax.legend()

# Optional: Overlay phi-shells (as planes for simplicity, since norms are large; adjust for visualization)
for m in range(1, 4):  # Example shells at m*phi, but project to a plane or skip if too spread
    ax.text(0, 0, 0, f'Shell at {m*phi}', color='blue')

plt.savefig('prime_universal_frame_3d.png')
print("\n3D plot saved as 'prime_universal_frame_3d.png'")

# Histogram Plots
fig, axs = plt.subplots(2, 1, figsize=(8, 6))
bin_centers = (bins[:-1] + bins[1:]) / 2
axs[0].bar(bin_centers, hist_all, width=phi/num_bins, color='gray', alpha=0.7)
axs[0].set_title('Density Histogram for All {n/φ}')
axs[1].bar(bin_centers, hist_primes, width=phi/num_bins, color='red', alpha=0.7)
axs[1].set_title('Density Histogram for Primes {p/φ}')
plt.tight_layout()
plt.savefig('density_histograms.png')
print("Density histograms saved as 'density_histograms.png'")

# Fourier and GMM Plot
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(phi_test, rho_test, label='Fourier Approx', color='blue')
phi_gmm = rho_gmm(phi_test)
ax.plot(phi_test, phi_gmm, label='GMM Approx', color='green')
ax.bar(bin_centers, hist_primes, width=phi/num_bins, color='red', alpha=0.3, label='Empirical Prime Density')
ax.set_xlabel('phi mod')
ax.set_ylabel('rho_prime')
ax.set_title('Analytic Approximations of Prime Density')
ax.legend()
plt.savefig('rho_approximations.png')
print("Rho approximations plot saved as 'rho_approximations.png'")