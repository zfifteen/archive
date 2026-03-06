import numpy as np
from scipy.signal import welch, find_peaks, detrend
from math import sqrt, pi, e

PHI = (1 + sqrt(5)) / 2  # Golden ratio


def compute_psd(log_gaps, nperseg=1024):
    """
    Compute power spectral density using Welch method.
    Returns freqs, psd
    """
    # Preprocessing
    log_gaps_detrended = detrend(log_gaps)
    window = np.hanning(len(log_gaps_detrended))
    log_gaps_windowed = log_gaps_detrended * window

    freqs, psd = welch(log_gaps_windowed, nperseg=nperseg)
    return freqs, psd


def get_harmonics(N, constant, k_max=10):
    """Get harmonic frequencies: f_k = k * constant / N"""
    return [k * constant / N for k in range(1, k_max + 1)]


def get_phi_harmonics(N, k_max=10):
    """Get φ-harmonic frequencies: f_k = k * φ / N"""
    return get_harmonics(N, PHI, k_max)


def get_pi_harmonics(N, k_max=10):
    """Get π-harmonic frequencies"""
    return get_harmonics(N, pi, k_max)


def get_e_harmonics(N, k_max=10):
    """Get e-harmonic frequencies"""
    return get_harmonics(N, e, k_max)


def find_peaks_in_psd(freqs, psd, prominence=0.1):
    """
    Find peaks in PSD.
    Returns peak_freqs, peak_amplitudes
    """
    peaks, properties = find_peaks(psd, prominence=prominence)
    peak_freqs = freqs[peaks]
    peak_amplitudes = psd[peaks]
    return peak_freqs, peak_amplitudes


def alignment_score(peak_freqs, harmonic_freqs, epsilon=0.01):
    """
    Compute alignment score: count peaks within epsilon of any harmonic.
    """
    count = 0
    for peak in peak_freqs:
        if any(abs(peak - f_h) < epsilon for f_h in harmonic_freqs):
            count += 1
    return count


def phi_alignment_score(peak_freqs, phi_freqs, epsilon=0.01):
    return alignment_score(peak_freqs, phi_freqs, epsilon)


def z_score_phi_peaks(phi_freqs, freqs, psd):
    """
    Compute Z-scores for PSD at φ-frequencies.
    """
    mu_psd = np.mean(psd)
    sigma_psd = np.std(psd)
    z_scores = []
    for f_phi in phi_freqs:
        idx = np.argmin(np.abs(freqs - f_phi))
        psd_val = psd[idx]
        z = (psd_val - mu_psd) / sigma_psd
        z_scores.append(z)
    return z_scores


def peak_prominence_score(phi_freqs, freqs, psd):
    """
    Compute peak prominence at φ-frequencies: PSD(f_phi) / median(PSD)
    """
    median_psd = np.median(psd)
    scores = []
    for f_phi in phi_freqs:
        idx = np.argmin(np.abs(freqs - f_phi))
        score = psd[idx] / median_psd
        scores.append(score)
    return scores
