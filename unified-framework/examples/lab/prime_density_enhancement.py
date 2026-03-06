from sympy.ntheory import primerange
import numpy as np
from scipy.stats import gaussian_kde

# Constants
phi = (1 + np.sqrt(5)) / 2
N = 100000  # Range limit

# Generate arrays
nums = np.arange(1, N + 1)
primes = np.array(list(primerange(1, N + 1)))

# Geodesic transform function
def theta_prime(n, k=0.3):
    return phi * (((n % phi) / phi) ** k)

# Apply transform
theta_all = np.array([theta_prime(n) for n in nums])
theta_primes = np.array([theta_prime(p) for p in primes])

# KDE estimation
kde_all = gaussian_kde(theta_all, bw_method='scott')
kde_primes = gaussian_kde(theta_primes, bw_method='scott')

x = np.linspace(0, phi, 1000)
rho_all = kde_all(x)
rho_primes = kde_primes(x)

# Enhancement metric
enhancement = np.max((rho_primes / rho_all - 1) * 100)
print(f"Enhancement: {enhancement:.2f}%")