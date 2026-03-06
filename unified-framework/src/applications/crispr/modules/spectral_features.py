"""
Spectral Feature Extraction for CRISPR gRNA Prediction

This module implements spectral analysis features for complex DNA waveforms:
- ΔEntropy: Change in spectral entropy (information content)
- Δf₁: Change in fundamental frequency peak magnitude
- Sidelobe ratios: Ratio of sidelobe energy to main lobe
- MSC: Magnitude-squared coherence (off-target similarity)
- W₁: Wasserstein-1 distance between spectra
- SAS: Sidelobe asymmetry score

These features quantify the disruption potential of gRNA sequences and
off-target binding characteristics.
"""

import numpy as np
from scipy.fft import fft, fftfreq
from scipy.stats import entropy, wasserstein_distance
from scipy.signal import find_peaks, windows
from typing import Dict, Optional, Tuple, Union


class SpectralFeatureExtractor:
    """
    Extract spectral features from complex DNA waveforms.

    Computes various spectral metrics to quantify sequence properties
    and disruption potential for CRISPR applications.

    Attributes:
        fft_size (int): FFT size (padded to power of 2 if needed)
        window_type (str): Window function type ('hann', 'hamming', 'blackman', None)
        f1_index (int): Expected fundamental frequency bin index
    """

    def __init__(
        self,
        fft_size: int = 256,
        window_type: str = "hann",
        f1_index: Optional[int] = None,
    ):
        """
        Initialize spectral feature extractor.

        Args:
            fft_size: Size for FFT computation (default: 256)
            window_type: Window function ('hann', 'hamming', 'blackman', None)
            f1_index: Expected fundamental frequency index (default: auto-detect)
        """
        self.fft_size = fft_size
        self.window_type = window_type
        self.f1_index = f1_index

        # Pad to next power of 2 for efficient FFT
        self.fft_size = 2 ** int(np.ceil(np.log2(fft_size)))

    def apply_window(self, waveform: np.ndarray) -> np.ndarray:
        """
        Apply window function to waveform.

        Args:
            waveform: Input complex waveform

        Returns:
            Windowed waveform
        """
        if self.window_type is None or self.window_type.lower() == "none":
            return waveform

        length = len(waveform)

        if self.window_type.lower() == "hann":
            window = windows.hann(length, sym=False)
        elif self.window_type.lower() == "hamming":
            window = windows.hamming(length, sym=False)
        elif self.window_type.lower() == "blackman":
            window = windows.blackman(length, sym=False)
        else:
            raise ValueError(f"Unknown window type: {self.window_type}")

        return waveform * window

    def compute_spectrum(
        self, waveform: np.ndarray, apply_window: bool = True
    ) -> np.ndarray:
        """
        Compute FFT magnitude spectrum.

        Args:
            waveform: Input complex waveform
            apply_window: Whether to apply window function

        Returns:
            Magnitude spectrum (one-sided, positive frequencies)
        """
        if apply_window:
            waveform = self.apply_window(waveform)

        # Zero-pad to FFT size
        if len(waveform) < self.fft_size:
            waveform = np.pad(
                waveform, (0, self.fft_size - len(waveform)), mode="constant"
            )

        # Compute FFT
        spectrum_complex = fft(waveform, n=self.fft_size)

        # Return magnitude spectrum (positive frequencies only)
        magnitude_spectrum = np.abs(spectrum_complex[: self.fft_size // 2])

        return magnitude_spectrum

    def compute_entropy(self, spectrum: np.ndarray) -> float:
        """
        Compute Shannon entropy of spectrum.

        Args:
            spectrum: Magnitude spectrum

        Returns:
            Entropy value in bits
        """
        # Normalize to probability distribution
        spectrum_normalized = spectrum / np.sum(spectrum)

        # Add small epsilon to avoid log(0)
        spectrum_normalized = spectrum_normalized + 1e-12

        return entropy(spectrum_normalized, base=2)

    def find_fundamental_peak(
        self,
        spectrum: np.ndarray,
        expected_index: Optional[int] = None,
        search_window: int = 5,
    ) -> Tuple[int, float]:
        """
        Find fundamental frequency peak.

        Args:
            spectrum: Magnitude spectrum
            expected_index: Expected peak location (searches nearby)
            search_window: Window size for peak search

        Returns:
            Tuple of (peak_index, peak_magnitude)
        """
        if expected_index is None:
            # Use stored f1_index or find global maximum
            if self.f1_index is not None:
                expected_index = self.f1_index
            else:
                # Assume fundamental is in first 20% of spectrum
                search_end = len(spectrum) // 5
                expected_index = np.argmax(spectrum[:search_end])

        # Search in window around expected location
        start_idx = max(0, expected_index - search_window)
        end_idx = min(len(spectrum), expected_index + search_window + 1)

        window_spectrum = spectrum[start_idx:end_idx]
        local_peak_idx = np.argmax(window_spectrum)
        peak_idx = start_idx + local_peak_idx
        peak_magnitude = spectrum[peak_idx]

        return peak_idx, peak_magnitude

    def compute_sidelobe_ratio(
        self,
        spectrum: np.ndarray,
        main_lobe_width: int = 10,
        threshold_ratio: float = 0.25,
    ) -> float:
        """
        Compute sidelobe-to-mainlobe energy ratio.

        Args:
            spectrum: Magnitude spectrum
            main_lobe_width: Width of main lobe region
            threshold_ratio: Minimum ratio to count as sidelobe

        Returns:
            Sidelobe ratio (higher means more sidelobe energy)
        """
        # Find fundamental peak
        peak_idx, peak_mag = self.find_fundamental_peak(spectrum)

        # Define main lobe region
        main_lobe_start = max(0, peak_idx - main_lobe_width // 2)
        main_lobe_end = min(len(spectrum), peak_idx + main_lobe_width // 2)

        # Compute energies
        main_lobe_energy = np.sum(spectrum[main_lobe_start:main_lobe_end] ** 2)

        # Sidelobe is everything outside main lobe above threshold
        threshold = threshold_ratio * peak_mag
        sidelobe_mask = spectrum > threshold
        sidelobe_mask[main_lobe_start:main_lobe_end] = False
        sidelobe_energy = np.sum(spectrum[sidelobe_mask] ** 2)

        # Return ratio
        if main_lobe_energy == 0:
            return 0.0

        return sidelobe_energy / main_lobe_energy

    def compute_delta_entropy(
        self, spectrum_base: np.ndarray, spectrum_mutated: np.ndarray
    ) -> float:
        """
        Compute change in spectral entropy.

        Args:
            spectrum_base: Baseline spectrum
            spectrum_mutated: Mutated/transformed spectrum

        Returns:
            ΔEntropy = H(mutated) - H(base)
        """
        entropy_base = self.compute_entropy(spectrum_base)
        entropy_mutated = self.compute_entropy(spectrum_mutated)

        return entropy_mutated - entropy_base

    def compute_delta_f1(
        self,
        spectrum_base: np.ndarray,
        spectrum_mutated: np.ndarray,
        as_percentage: bool = True,
    ) -> float:
        """
        Compute change in fundamental frequency peak magnitude.

        Args:
            spectrum_base: Baseline spectrum
            spectrum_mutated: Mutated/transformed spectrum
            as_percentage: Return as percentage change

        Returns:
            Δf₁ = (f₁_mutated - f₁_base) / f₁_base (if as_percentage)
        """
        _, f1_base = self.find_fundamental_peak(spectrum_base)
        _, f1_mutated = self.find_fundamental_peak(spectrum_mutated)

        if as_percentage:
            if f1_base == 0:
                return 0.0
            return 100 * (f1_mutated - f1_base) / f1_base
        else:
            return f1_mutated - f1_base

    def compute_delta_sidelobe(
        self, spectrum_base: np.ndarray, spectrum_mutated: np.ndarray
    ) -> float:
        """
        Compute change in sidelobe ratio.

        Args:
            spectrum_base: Baseline spectrum
            spectrum_mutated: Mutated/transformed spectrum

        Returns:
            Δsidelobe = sidelobe_ratio(mutated) - sidelobe_ratio(base)
        """
        sidelobe_base = self.compute_sidelobe_ratio(spectrum_base)
        sidelobe_mutated = self.compute_sidelobe_ratio(spectrum_mutated)

        return sidelobe_mutated - sidelobe_base

    def compute_msc(self, spectrum1: np.ndarray, spectrum2: np.ndarray) -> float:
        """
        Compute magnitude-squared coherence (similarity measure).

        MSC is a frequency-domain correlation measure, similar to
        Pearson correlation but for spectra. Values range [0, 1].

        Args:
            spectrum1: First spectrum
            spectrum2: Second spectrum

        Returns:
            MSC value (1 = identical, 0 = uncorrelated)
        """
        # Ensure same length
        min_len = min(len(spectrum1), len(spectrum2))
        spectrum1 = spectrum1[:min_len]
        spectrum2 = spectrum2[:min_len]

        # Compute cross-spectrum and auto-spectra
        cross_spec = np.sum(spectrum1 * spectrum2)
        auto_spec1 = np.sum(spectrum1**2)
        auto_spec2 = np.sum(spectrum2**2)

        # MSC formula
        if auto_spec1 == 0 or auto_spec2 == 0:
            return 0.0

        msc = (cross_spec**2) / (auto_spec1 * auto_spec2)

        return np.clip(msc, 0, 1)

    def compute_wasserstein(
        self, spectrum1: np.ndarray, spectrum2: np.ndarray
    ) -> float:
        """
        Compute Wasserstein-1 (Earth Mover's) distance between spectra.

        W₁ distance measures the minimum "work" needed to transform
        one distribution into another. Lower values indicate more similarity.

        Args:
            spectrum1: First spectrum
            spectrum2: Second spectrum

        Returns:
            W₁ distance
        """
        # Ensure same length
        min_len = min(len(spectrum1), len(spectrum2))
        spectrum1 = spectrum1[:min_len]
        spectrum2 = spectrum2[:min_len]

        # Normalize to probability distributions
        spectrum1_norm = spectrum1 / (np.sum(spectrum1) + 1e-12)
        spectrum2_norm = spectrum2 / (np.sum(spectrum2) + 1e-12)

        # Compute Wasserstein distance
        w1_distance = wasserstein_distance(
            np.arange(len(spectrum1_norm)),
            np.arange(len(spectrum2_norm)),
            spectrum1_norm,
            spectrum2_norm,
        )

        return w1_distance

    def compute_sidelobe_asymmetry(
        self, spectrum: np.ndarray, main_lobe_width: int = 10
    ) -> float:
        """
        Compute sidelobe asymmetry score (SAS).

        SAS measures the balance between left and right sidelobes,
        which can indicate structural features of the sequence.

        Args:
            spectrum: Magnitude spectrum
            main_lobe_width: Width of main lobe region

        Returns:
            SAS value (0 = symmetric, positive = right-skewed, negative = left-skewed)
        """
        # Find fundamental peak
        peak_idx, _ = self.find_fundamental_peak(spectrum)

        # Define regions
        main_lobe_start = max(0, peak_idx - main_lobe_width // 2)
        main_lobe_end = min(len(spectrum), peak_idx + main_lobe_width // 2)

        # Left and right sidelobe energies
        left_energy = np.sum(spectrum[:main_lobe_start] ** 2)
        right_energy = np.sum(spectrum[main_lobe_end:] ** 2)

        total_energy = left_energy + right_energy
        if total_energy == 0:
            return 0.0

        # Asymmetry score
        sas = (right_energy - left_energy) / total_energy

        return sas

    def compute_composite_disruption_score(
        self,
        spectrum_base: np.ndarray,
        spectrum_mutated: np.ndarray,
        weights: Optional[Dict[str, float]] = None,
    ) -> Tuple[float, Dict[str, float]]:
        """
        Compute composite disruption score from multiple features.

        Default formula:
            D = w_entropy * ΔEntropy + w_f1 * |Δf₁| + w_sidelobe * Δsidelobe

        Args:
            spectrum_base: Baseline spectrum
            spectrum_mutated: Mutated/transformed spectrum
            weights: Dictionary of feature weights (default: equal weights)

        Returns:
            Tuple of (composite_score, feature_dict)
        """
        if weights is None:
            weights = {"entropy": 1.0, "f1": 1.0, "sidelobe": 1.0}

        # Compute individual features
        delta_entropy = self.compute_delta_entropy(spectrum_base, spectrum_mutated)
        delta_f1 = self.compute_delta_f1(
            spectrum_base, spectrum_mutated, as_percentage=True
        )
        delta_sidelobe = self.compute_delta_sidelobe(spectrum_base, spectrum_mutated)

        # Compute composite score
        composite_score = (
            weights.get("entropy", 1.0) * delta_entropy
            + weights.get("f1", 1.0) * abs(delta_f1)
            + weights.get("sidelobe", 1.0) * delta_sidelobe
        )

        features = {
            "delta_entropy": delta_entropy,
            "delta_f1": delta_f1,
            "delta_sidelobe": delta_sidelobe,
            "composite_score": composite_score,
        }

        return composite_score, features

    def extract_all_features(
        self,
        spectrum_base: np.ndarray,
        spectrum_transformed: np.ndarray,
        spectrum_offtarget: Optional[np.ndarray] = None,
    ) -> Dict[str, float]:
        """
        Extract all spectral features in one call.

        Args:
            spectrum_base: Baseline spectrum
            spectrum_transformed: Transformed spectrum (φ-phase + arcsin)
            spectrum_offtarget: Optional off-target spectrum for distance metrics

        Returns:
            Dictionary of all computed features
        """
        features = {}

        # Differential features
        features["delta_entropy"] = self.compute_delta_entropy(
            spectrum_base, spectrum_transformed
        )
        features["delta_f1"] = self.compute_delta_f1(
            spectrum_base, spectrum_transformed, as_percentage=True
        )
        features["delta_sidelobe"] = self.compute_delta_sidelobe(
            spectrum_base, spectrum_transformed
        )

        # Absolute features for transformed spectrum
        features["entropy_transformed"] = self.compute_entropy(spectrum_transformed)
        features["sidelobe_ratio_transformed"] = self.compute_sidelobe_ratio(
            spectrum_transformed
        )
        features["sidelobe_asymmetry_transformed"] = self.compute_sidelobe_asymmetry(
            spectrum_transformed
        )

        # Peak information
        peak_idx, peak_mag = self.find_fundamental_peak(spectrum_transformed)
        features["f1_peak_index"] = peak_idx
        features["f1_peak_magnitude"] = peak_mag

        # Composite disruption score
        composite_score, _ = self.compute_composite_disruption_score(
            spectrum_base, spectrum_transformed
        )
        features["composite_disruption_score"] = composite_score

        # Off-target features (if provided)
        if spectrum_offtarget is not None:
            features["msc_offtarget"] = self.compute_msc(
                spectrum_transformed, spectrum_offtarget
            )
            features["wasserstein_offtarget"] = self.compute_wasserstein(
                spectrum_transformed, spectrum_offtarget
            )

        return features


def compute_gc_content(sequence: str) -> float:
    """
    Compute GC content of DNA sequence.

    Args:
        sequence: DNA sequence string

    Returns:
        GC percentage (0-100)
    """
    sequence = sequence.upper()
    gc_count = sequence.count("G") + sequence.count("C")
    return 100 * gc_count / len(sequence)


def assign_gc_quartile(gc_percentage: float) -> int:
    """
    Assign GC quartile (1-4) based on GC percentage.

    Args:
        gc_percentage: GC content (0-100)

    Returns:
        Quartile number (1, 2, 3, or 4)
    """
    if gc_percentage < 25:
        return 1
    elif gc_percentage < 50:
        return 2
    elif gc_percentage < 75:
        return 3
    else:
        return 4
