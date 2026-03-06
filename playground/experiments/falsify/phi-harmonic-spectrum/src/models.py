import numpy as np
from scipy.signal import welch
from analysis import compute_psd, get_phi_harmonics


def permutation_test(log_gaps, phi_freqs, n_shuffles=100, nperseg=1024):
    """
    Permutation test: shuffle log_gaps, compute max PSD at φ-frequencies, compare to observed.
    Returns p-value
    """
    # Observed
    freqs, psd = compute_psd(log_gaps, nperseg)
    observed_phi_peaks = [psd[np.argmin(np.abs(freqs - f))] for f in phi_freqs]
    observed_max = max(observed_phi_peaks)

    # Null distribution
    null_maxes = []
    for _ in range(n_shuffles):
        shuffled = np.random.permutation(log_gaps)
        _, psd_null = welch(shuffled, nperseg=nperseg)
        null_phi_peaks = [psd_null[np.argmin(np.abs(freqs - f))] for f in phi_freqs]
        null_maxes.append(max(null_phi_peaks))

    # p-value: fraction where null >= observed
    p_value = np.mean([x >= observed_max for x in null_maxes])
    return p_value, null_maxes


def generate_white_noise_null(length):
    """Generate white noise null model."""
    return np.random.normal(0, 1, length)


def generate_shuffled_null(log_gaps):
    """Generate shuffled null model."""
    return np.random.permutation(log_gaps)


def spectral_concentration_test(phi_freqs, freqs, psd, bandwidth=0.01):
    """
    Test if peaks are concentrated near φ-frequencies vs random bands.
    Returns density near φ vs random.
    """
    phi_density = 0
    random_density = 0
    n_random = len(phi_freqs) * 10  # More random bands

    # Near φ
    for f_phi in phi_freqs:
        idx = np.argmin(np.abs(freqs - f_phi))
        local_psd = psd[max(0, idx - 10) : idx + 11]
        phi_density += np.sum(local_psd > np.mean(psd))

    # Random bands
    random_freqs = np.random.uniform(0, 0.5, n_random)  # Up to Nyquist
    for f_rand in random_freqs:
        idx = np.argmin(np.abs(freqs - f_rand))
        local_psd = psd[max(0, idx - 10) : idx + 11]
        random_density += np.sum(local_psd > np.mean(psd))

    return phi_density / len(phi_freqs), random_density / n_random
