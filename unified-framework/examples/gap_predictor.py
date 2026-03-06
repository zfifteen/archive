import numpy as np
import math
from sklearn.mixture import GaussianMixture
from mpmath import mp, zetazero
from scipy.stats import gaussian_kde

# Constants
phi = (1 + math.sqrt(5)) / 2
e2 = math.exp(2)
pi_phi = math.pi / phi
N = 10**6
k_values = np.arange(0.2, 0.41, 0.01)  # Balanced step for speed

def sieve_primes(n):
    sieve = np.ones(n+1, dtype=bool)
    sieve[0:2] = False
    for i in range(2, int(math.sqrt(n))+1):
        if sieve[i]:
            sieve[i*i::i] = False
    return np.where(sieve)[0]

primes = sieve_primes(N)

def theta_prime(n, k):
    return phi * ((n % phi / phi) ** k)

def compute_spectral_entropy(values, window=128):
    if len(values) < window:
        return 0.0
    fft_vals = np.abs(np.fft.fft(values[-window:]))
    sum_fft = np.sum(fft_vals) + 1e-10
    probs = fft_vals / sum_fft
    return -np.sum(probs * np.log(probs + 1e-10))

def compute_zeta_zeros(n_zeros):
    mp.dps = 15
    zeros = []
    for i in range(1, n_zeros + 1):
        z = zetazero(i)
        zeros.append(float(z.imag))
    return np.array(zeros)

# k-sweep for density enhancement using KDE
enhancements = []
for k in k_values:
    theta_primes = np.array([theta_prime(p, k) for p in primes])
    all_ns = np.arange(2, N+1)
    theta_all = np.array([theta_prime(n, k) for n in all_ns])

    kde_all = gaussian_kde(theta_all)
    kde_primes = gaussian_kde(theta_primes)

    x = np.linspace(0, phi, 1000)
    rho_all = kde_all(x)
    rho_primes = kde_primes(x)

    density_enh = (rho_primes / (rho_all + 1e-10) - 1) * 100
    mean_enh = np.mean(density_enh)
    enhancements.append(mean_enh)

optimal_k = k_values[np.argmax(enhancements)]
max_enh = max(enhancements)

# GMM at optimal k
theta_primes_opt = np.array([theta_prime(p, optimal_k) for p in primes]).reshape(-1, 1)
gmm = GaussianMixture(n_components=3).fit(theta_primes_opt)
gmm_std = np.mean(np.sqrt(gmm.covariances_.flatten()))

# Fourier asymmetry
fft = np.fft.fft(theta_primes_opt.flatten())
imag_parts = np.abs(np.imag(fft[1:len(fft)//2]))
sum_abs_fft = np.sum(np.abs(fft[1:len(fft)//2])) + 1e-10
sine_sum = np.sum(imag_parts) / sum_abs_fft

# var(O) on prime gaps
prime_gaps = np.diff(primes)
entropies = []
window = 32  # Smaller for variance
for i in range(0, len(prime_gaps) - window, 16):  # Tighter overlap
    entropy = compute_spectral_entropy(prime_gaps[i:i+window])
    if entropy > 1e-5:
        entropies.append(entropy)
var_O = np.var(entropies) if entropies else 0.0
log_log_N = math.log(math.log(N + 1e-10))

# Zeta correlation
mean_gap = np.mean(prime_gaps) + 1e-10
unfolded_prime_gaps = np.cumsum(prime_gaps / mean_gap)

n_zeros = 200
zeta_zeros = compute_zeta_zeros(n_zeros)
zeta_spacings = np.diff(zeta_zeros)
mean_zeta = np.mean(zeta_spacings) + 1e-10
unfolded_zeta = np.cumsum(zeta_spacings / mean_zeta)

min_len = min(len(unfolded_prime_gaps), len(unfolded_zeta))
corr = np.corrcoef(unfolded_prime_gaps[:min_len], unfolded_zeta[:min_len])[0,1] if min_len > 1 else 0.0

# Output results
print(f"Optimal k: {optimal_k:.3f}")
print(f"Max enhancement: {max_enh:.2f}%")
print(f"GMM std: {gmm_std:.3f}")
print(f"Fourier sine sum: {sine_sum:.3f}")
print(f"Var(O): {var_O:.3f}, log log N: {log_log_N:.3f}")
print(f"Zeta corr: {corr:.3f}")