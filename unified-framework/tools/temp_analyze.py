import numpy as np
import mpmath as mp
mp.dps = 50

zeros = np.load('src/data/zeta_zeros.npy')[:1000]
spacings = np.diff(zeros)
spacing_imag = np.imag(spacings)

phi = mp.phi
k = 0.3

def theta_prime(n, k):
    mod = float(mp.fmod(n, phi))
    return float(phi * (mod / phi)**k)

theta_vals = [theta_prime(i+1, k) for i in range(len(spacings))]

# Compute correlation
from scipy.stats import pearsonr
corr, _ = pearsonr(spacing_imag, theta_vals)
print("Pearson correlation for first 1000 spacings and theta':", corr)

# Also try k=1
k=1
theta_vals1 = [theta_prime(i+1, k) for i in range(len(spacings))]
corr1, _ = pearsonr(spacing_imag, theta_vals1)
print("For k=1:", corr1)

# k=0.5
k=0.5
theta_vals05 = [theta_prime(i+1, k) for i in range(len(spacings))]
corr05, _ = pearsonr(spacing_imag, theta_vals05)
print("For k=0.5:", corr05)