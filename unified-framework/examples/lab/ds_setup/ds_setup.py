import numpy as np
from mpmath import mp, phi, e, log, sin, zetazero
import matplotlib.pyplot as plt
from sympy import sieve, divisor_count
from scipy.stats import pearsonr, ks_2samp
from sklearn.mixture import GaussianMixture
from scipy.fft import fft, fftfreq

mp.dps = 50  # Decimal precision

def kappa(n):
    """Frame-normalized curvature κ(n) = d(n) * ln(n+1) / e²"""
    return divisor_count(n) * log(n + 1) / (e**2)

def Z_discrete(n, Δ_max=mp.exp(2)):
    """Z = n * (Δ_n / Δ_max) with Δ_n = v * κ(n) and v=1"""
    Δ_n = 1 * kappa(n)
    return float(n) * float(Δ_n / Δ_max)

def prime_curvature_enhancement(N_max=1000, k_min=0.2, k_max=0.4, dk=0.002, bins=20):
    golden_ratio = float(phi)  # Ensure it's a float

    # Generate primes and composites
    primes = list(sieve.primerange(2, N_max))
    composites = [n for n in range(2, N_max) if n not in primes]

    best_k, best_enhance = None, -float('inf')
    k_values = np.arange(k_min, k_max + dk, dk)

    for k in k_values:
        # Transform values: θ'(n, k) = φ * {n/φ}^k where {x} is the fractional part of x
        def transform(n):
            mod = float(n % golden_ratio)
            return golden_ratio * (mod / golden_ratio) ** k
        prime_vals = [float(transform(p)) for p in primes]
        comp_vals = [float(transform(c)) for c in composites]

        # Bin densities in [0, φ)
        hist_p, edges = np.histogram(prime_vals, bins=bins, range=(0, golden_ratio), density=True)
        hist_c, _ = np.histogram(comp_vals, bins=edges, density=True)

        # Relative enhancement e_i = (d_P,i - d_N,i) / d_N,i * 100%
        with np.errstate(divide='ignore', invalid='ignore'):
            enhance = np.nanmean(
                np.where(hist_c != 0, (hist_p - hist_c) / hist_c, 0)
            ) * 100

        if enhance > best_enhance:
            best_enhance = enhance
            best_k = k

    return best_k, best_enhance

# Execute for N_max=1000
k_opt, enhance_opt = prime_curvature_enhancement()
print(f"Optimal k*: {k_opt:.3f}, Max enhancement: {enhance_opt:.1f}%")

def unfolded_zero(j):
    """Unfolded zero: \tilde{t}_j = Im(ρ_j) / (2π * log(Im(ρ_j)/(2πe))"""
    z = zetazero(j)  # j-th non-trivial zero
    im_z = float(mp.im(z))
    return im_z / (2 * np.pi * np.log(im_z / (2 * np.pi * np.e)))

# Compute first 1000 unfolded zeros and prime spacings
primes = list(sieve.primerange(2, 1000))
unfolded_zeros = [unfolded_zero(j) for j in range(1, 1001)]
prime_gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]

# Calculate Pearson correlation
corr, p_value = pearsonr(unfolded_zeros[:len(prime_gaps)], prime_gaps)
print(f"Pearson r: {corr:.4f}, p-value: {p_value:.2e}")

def helical_3d_plot(primes, k_opt, N_max=1000):
    golden_ratio = float(phi)
    def transform(n):
        mod = float(n % golden_ratio)
        return golden_ratio * (mod / golden_ratio) ** k_opt

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    for p in primes:
        θ_prime = transform(p)
        z_val = float(sin(2 * mp.pi * p / 10))
        x = p * np.cos(θ_prime)
        y = p * np.sin(θ_prime)
        ax.scatter(x, y, z_val, c='r', s=10)

    ax.set_xlabel('X: n·cos(θ\'(p))')
    ax.set_ylabel('Y: n·sin(θ\'(p))')
    ax.set_zlabel('Z: sin(2πn/10)')
    plt.title('Prime Geodesics in 3D Helical Embedding')
    plt.show()

# Generate primes up to 1000 and plot
primes = list(sieve.primerange(2, 1000))
helical_3d_plot(primes, k_opt)

def dna_waveform(sequence):
    mapping = {'A': 1+0j, 'T': -1+0j, 'C': 0+1j, 'G': 0-1j}
    return np.array([mapping.get(nuc, 0j) for nuc in sequence])

def spectral_entropy(signal):
    fft_vals = fft(signal)
    power = np.abs(fft_vals)**2
    prob = power / np.sum(power)
    return -np.sum(prob * np.log(np.clip(prob, 1e-12, None)))

def disruption_score(sequence, Z_n):
    waveform = dna_waveform(sequence)
    H = spectral_entropy(waveform)
    Δf1 = np.abs(fftfreq(len(waveform))[1] - fftfreq(len(waveform))[0])
    return Z_n * Δf1 + H  # Simplified disruption metric

# Example usage
seq = "ATCGATCGTAGCTAGCTAGCTAGCT"
Z_n = Z_discrete(len(seq))
score = disruption_score(seq, Z_n)
print(f"Disruption score: {score:.4f}")

Z_vals = [Z_discrete(p) for p in primes]
gmm = GaussianMixture(n_components=3).fit(np.array(Z_vals).reshape(-1,1))
print(f"Mean variances: {np.mean(gmm.covariances_):.4f}")