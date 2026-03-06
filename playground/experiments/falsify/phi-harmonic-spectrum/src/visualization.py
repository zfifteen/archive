import matplotlib.pyplot as plt
import numpy as np
from analysis import get_phi_harmonics


def plot_power_spectrum(freqs, psd, phi_freqs, save_path=None):
    """Plot PSD with φ-harmonic markers."""
    plt.figure(figsize=(12, 6))
    plt.plot(freqs, psd, label="Power Spectrum")
    for i, f in enumerate(phi_freqs):
        plt.axvline(
            f,
            color="red",
            linestyle="--",
            label=f"φ-harmonic {i + 1}" if i == 0 else "",
        )
    plt.xlabel("Frequency")
    plt.ylabel("Power Spectral Density")
    plt.title("Power Spectrum with φ-Harmonics")
    plt.legend()
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_peak_alignment(peak_freqs, phi_freqs, epsilon=0.01, save_path=None):
    """Plot histogram of peak distances to nearest φ-harmonic."""
    distances = []
    for peak in peak_freqs:
        dist = min(abs(peak - f_phi) for f_phi in phi_freqs)
        distances.append(dist)

    plt.figure(figsize=(8, 5))
    plt.hist(distances, bins=50, alpha=0.7)
    plt.axvline(epsilon, color="red", linestyle="--", label=f"ε = {epsilon}")
    plt.xlabel("Distance to Nearest φ-Harmonic")
    plt.ylabel("Number of Peaks")
    plt.title("Peak Alignment to φ-Harmonics")
    plt.legend()
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_permutation_null(observed_max, null_maxes, save_path=None):
    """Plot observed vs null distribution."""
    plt.figure(figsize=(8, 5))
    plt.hist(null_maxes, bins=50, alpha=0.7, label="Null Distribution")
    plt.axvline(
        observed_max,
        color="red",
        linestyle="--",
        label=f"Observed Max = {observed_max:.3f}",
    )
    plt.xlabel("Max PSD at φ-Frequencies")
    plt.ylabel("Frequency")
    plt.title("Permutation Test: Observed vs Null")
    plt.legend()
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_multi_range_comparison(results_dict, save_path=None):
    """Plot spectral peaks across different prime ranges."""
    fig, axes = plt.subplots(len(results_dict), 1, figsize=(12, 6 * len(results_dict)))
    if len(results_dict) == 1:
        axes = [axes]

    for ax, (range_name, (freqs, psd, phi_freqs)) in zip(axes, results_dict.items()):
        ax.plot(freqs, psd)
        for f in phi_freqs:
            ax.axvline(f, color="red", linestyle="--")
        ax.set_title(f"Power Spectrum: {range_name}")
        ax.set_xlabel("Frequency")
        ax.set_ylabel("PSD")
        ax.grid(True)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()
