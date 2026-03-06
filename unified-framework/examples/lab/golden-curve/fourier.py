import math
import sympy
import numpy as np
from scipy.stats import chisquare
from sklearn.preprocessing import MinMaxScaler
from scipy.fft import fft  # New for Fourier

def divisor_count(n):
    return sympy.divisor_count(n)

def Z_kappa(n):
    return (divisor_count(n) * math.log(n)) / math.exp(2) if n > 1 else 0

def Z(n, a=1):
    return n / math.exp(a * Z_kappa(n))

# Primes up to N, compute gaps/CV/entropy/χ²/Fourier
N = 10000
primes = list(sympy.primerange(2, N+1))
z_primes = [Z(p) for p in primes]
prime_gaps = np.diff(primes)
z_gaps = np.diff(z_primes)

def cv(gaps):
    return np.std(gaps) / np.mean(gaps)

def hist_entropy(gaps):
    hist, _ = np.histogram(gaps, bins='auto', density=True)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist)) if len(hist) > 0 else 0

def normalize_and_chisq(gaps, bins=10):
    if len(gaps) < 2:
        return None, None
    scaler = MinMaxScaler()
    norm_gaps = scaler.fit_transform(gaps.reshape(-1, 1)).flatten()
    hist, _ = np.histogram(norm_gaps, bins=bins)
    expected = [len(norm_gaps)/bins] * bins
    chi2_stat, p_val = chisquare(hist, f_exp=expected)
    return chi2_stat, p_val

# New: Spectral entropy from FFT power spectrum
def spectral_entropy(gaps):
    fft_vals = np.abs(fft(gaps - np.mean(gaps)))  # Detrend and FFT
    psd = fft_vals ** 2 / len(gaps)  # Power spectral density
    psd_norm = psd[psd > 0] / np.sum(psd[psd > 0])  # Normalize
    return -np.sum(psd_norm * np.log(psd_norm)) if len(psd_norm) > 0 else 0

prime_chi2, prime_p = normalize_and_chisq(prime_gaps)
z_chi2, z_p = normalize_and_chisq(z_gaps)
prime_spec_ent = spectral_entropy(prime_gaps)
z_spec_ent = spectral_entropy(z_gaps)

print(f"Number of primes: {len(primes)}")
print(f"Prime gaps CV: {cv(prime_gaps):.3f}, Hist Entropy: {hist_entropy(prime_gaps):.3f}, Spec Entropy: {prime_spec_ent:.3f}, χ²: {prime_chi2:.3f}, p: {prime_p:.5f}")
print(f"Z gaps CV: {cv(z_gaps):.3f}, Hist Entropy: {hist_entropy(z_gaps):.3f}, Spec Entropy: {z_spec_ent:.3f}, χ²: {z_chi2:.3f}, p: {z_p:.5f}")