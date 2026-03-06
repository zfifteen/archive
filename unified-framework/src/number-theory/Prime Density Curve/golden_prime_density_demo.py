import numpy as np
from scipy.stats import gaussian_kde, bootstrap
from sympy.ntheory import primerange
import mpmath as mp
import matplotlib.pyplot as plt

mp.mp.dps = 50
PHI = float((1 + mp.sqrt(5)) / 2)

def theta_prime(n, k=0.3, phi=PHI):
    n_mp = mp.mpf(n)
    mod_phi = float(mp.fmod(n_mp, phi))
    frac = mod_phi / phi
    return phi * (frac ** k)

# Parameters
N = 10000000
k = 0.3

# Generate integer and prime arrays
nums = np.arange(1, N + 1)
primes = np.array(list(primerange(1, N + 1)))

# Apply θ'(n, k) transformation
theta_all = np.array([theta_prime(n, k) for n in nums])
theta_primes = np.array([theta_prime(p, k) for p in primes])

# KDE for both populations
kde_all = gaussian_kde(theta_all, bw_method='scott')
kde_primes = gaussian_kde(theta_primes, bw_method='scott')

# Evaluate density on uniform grid
x = np.linspace(0, PHI, 500)
rho_all = kde_all(x)
rho_primes = kde_primes(x)

# Prime density enhancement statistics
enhancement = (rho_primes / rho_all - 1) * 100
max_enh = np.max(enhancement)
mean_enh = np.mean(enhancement)
median_enh = np.median(enhancement)

# Bootstrap CI for mean enhancement
res = bootstrap((enhancement,), np.mean, confidence_level=0.95, n_resamples=1000, method='percentile')
ci_lo, ci_hi = res.confidence_interval

# Output all relevant stats
print(f"Prime density enhancement (maximum): {max_enh:.2f}%")
print(f"Prime density enhancement (mean):    {mean_enh:.2f}%")
print(f"Prime density enhancement (median):  {median_enh:.2f}%")
print(f"95% CI for mean enhancement:         [{ci_lo:.2f}%, {ci_hi:.2f}%]")

# Visualization
plt.figure(figsize=(10,5))
plt.plot(x, rho_all, label='All Integers', color='gray', alpha=0.5)
plt.plot(x, rho_primes, label='Primes', color='crimson')
plt.xlabel(r"$\theta'(n, k=0.3)$")
plt.ylabel("Density")
plt.title("KDE of θ'(n, k=0.3) for Primes vs All Integers")
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(10,4))
plt.plot(x, enhancement, label='Prime Density Enhancement (%)')
plt.axhline(mean_enh, color='green', linestyle=':', label=f"Mean: {mean_enh:.2f}%")
plt.axhline(median_enh, color='purple', linestyle='--', label=f"Median: {median_enh:.2f}%")
plt.xlabel(r"$\theta'(n, k=0.3)$")
plt.ylabel("Enhancement (%)")
plt.title("Prime Density Enhancement Across θ'(n, k=0.3)")
plt.legend()
plt.tight_layout()
plt.show()