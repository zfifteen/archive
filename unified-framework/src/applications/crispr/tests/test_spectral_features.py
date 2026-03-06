"""
Unit tests for spectral_features module
"""

import numpy as np
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.spectral_features import (
    SpectralFeatureExtractor,
    compute_gc_content,
    assign_gc_quartile,
)
from modules.phi_phase import encode_dna_complex


class TestSpectralFeatureExtractor:
    """Test suite for SpectralFeatureExtractor class."""

    def test_initialization(self):
        """Test proper initialization."""
        extractor = SpectralFeatureExtractor(fft_size=256, window_type="hann")
        assert extractor.fft_size == 256
        assert extractor.window_type == "hann"

    def test_fft_size_power_of_2(self):
        """Test that FFT size is padded to power of 2."""
        extractor = SpectralFeatureExtractor(fft_size=200)
        assert extractor.fft_size == 256  # Next power of 2

        extractor = SpectralFeatureExtractor(fft_size=300)
        assert extractor.fft_size == 512

    def test_compute_spectrum(self):
        """Test spectrum computation."""
        extractor = SpectralFeatureExtractor(fft_size=256, window_type="hann")
        waveform = encode_dna_complex("ATCGATCGATCGATCG")

        spectrum = extractor.compute_spectrum(waveform)
        assert len(spectrum) == 128  # Half of FFT size (positive frequencies)
        assert np.all(spectrum >= 0)  # Magnitude should be non-negative

    def test_compute_entropy(self):
        """Test entropy computation."""
        extractor = SpectralFeatureExtractor()
        spectrum = np.array([0.5, 0.3, 0.2])

        entropy = extractor.compute_entropy(spectrum)
        assert entropy > 0
        assert entropy < 10  # Reasonable range for bits

    def test_find_fundamental_peak(self):
        """Test fundamental peak finding."""
        extractor = SpectralFeatureExtractor()
        # Create spectrum with clear peak at index 10
        spectrum = np.random.rand(128) * 0.1
        spectrum[10] = 1.0

        peak_idx, peak_mag = extractor.find_fundamental_peak(spectrum)
        assert peak_idx == 10
        assert abs(peak_mag - 1.0) < 0.01

    def test_compute_sidelobe_ratio(self):
        """Test sidelobe ratio computation."""
        extractor = SpectralFeatureExtractor()
        # Create spectrum with main lobe and sidelobes
        spectrum = np.random.rand(128) * 0.1
        spectrum[10] = 1.0  # Main peak
        spectrum[50:60] = 0.3  # Sidelobes

        ratio = extractor.compute_sidelobe_ratio(spectrum)
        assert ratio >= 0
        assert isinstance(ratio, float)

    def test_delta_entropy(self):
        """Test delta entropy computation."""
        extractor = SpectralFeatureExtractor()
        waveform1 = encode_dna_complex("ATCGATCGATCGATCG")
        waveform2 = encode_dna_complex("AAAACCCCGGGGTTTT")

        spectrum1 = extractor.compute_spectrum(waveform1)
        spectrum2 = extractor.compute_spectrum(waveform2)

        delta_entropy = extractor.compute_delta_entropy(spectrum1, spectrum2)
        assert isinstance(delta_entropy, float)

    def test_delta_f1(self):
        """Test delta f1 computation."""
        extractor = SpectralFeatureExtractor()
        waveform1 = encode_dna_complex("ATCGATCGATCGATCG")
        waveform2 = encode_dna_complex("AAAACCCCGGGGTTTT")

        spectrum1 = extractor.compute_spectrum(waveform1)
        spectrum2 = extractor.compute_spectrum(waveform2)

        delta_f1 = extractor.compute_delta_f1(spectrum1, spectrum2, as_percentage=True)
        assert isinstance(delta_f1, float)

    def test_compute_msc(self):
        """Test MSC computation."""
        extractor = SpectralFeatureExtractor()
        spectrum1 = np.random.rand(128)
        spectrum2 = np.random.rand(128)

        msc = extractor.compute_msc(spectrum1, spectrum2)
        assert 0 <= msc <= 1

        # Identical spectra should have MSC = 1
        msc_identical = extractor.compute_msc(spectrum1, spectrum1)
        assert abs(msc_identical - 1.0) < 0.01

    def test_compute_wasserstein(self):
        """Test Wasserstein distance computation."""
        extractor = SpectralFeatureExtractor()
        spectrum1 = np.random.rand(128)
        spectrum2 = np.random.rand(128)

        w1_dist = extractor.compute_wasserstein(spectrum1, spectrum2)
        assert w1_dist >= 0

        # Identical spectra should have W1 = 0
        w1_identical = extractor.compute_wasserstein(spectrum1, spectrum1)
        assert abs(w1_identical) < 0.01

    def test_compute_sidelobe_asymmetry(self):
        """Test sidelobe asymmetry score."""
        extractor = SpectralFeatureExtractor()
        spectrum = np.random.rand(128)

        sas = extractor.compute_sidelobe_asymmetry(spectrum)
        assert -1 <= sas <= 1

    def test_composite_disruption_score(self):
        """Test composite disruption score computation."""
        extractor = SpectralFeatureExtractor()
        waveform1 = encode_dna_complex("ATCGATCGATCGATCG")
        waveform2 = encode_dna_complex("AAAACCCCGGGGTTTT")

        spectrum1 = extractor.compute_spectrum(waveform1)
        spectrum2 = extractor.compute_spectrum(waveform2)

        score, features = extractor.compute_composite_disruption_score(
            spectrum1, spectrum2
        )

        assert isinstance(score, float)
        assert "delta_entropy" in features
        assert "delta_f1" in features
        assert "delta_sidelobe" in features

    def test_extract_all_features(self):
        """Test extraction of all features."""
        extractor = SpectralFeatureExtractor()
        waveform1 = encode_dna_complex("ATCGATCGATCGATCG")
        waveform2 = encode_dna_complex("AAAACCCCGGGGTTTT")

        spectrum1 = extractor.compute_spectrum(waveform1)
        spectrum2 = extractor.compute_spectrum(waveform2)

        features = extractor.extract_all_features(spectrum1, spectrum2)

        # Check that expected features are present
        expected_keys = [
            "delta_entropy",
            "delta_f1",
            "delta_sidelobe",
            "entropy_transformed",
            "sidelobe_ratio_transformed",
            "sidelobe_asymmetry_transformed",
            "f1_peak_index",
            "f1_peak_magnitude",
            "composite_disruption_score",
        ]

        for key in expected_keys:
            assert key in features

    def test_window_functions(self):
        """Test different window functions."""
        waveform = encode_dna_complex("ATCGATCGATCGATCG")

        # Test each window type
        for window in ["hann", "hamming", "blackman", "none"]:
            extractor = SpectralFeatureExtractor(window_type=window)
            spectrum = extractor.compute_spectrum(waveform)
            assert len(spectrum) > 0

    def test_invalid_window(self):
        """Test that invalid window raises error."""
        extractor = SpectralFeatureExtractor(window_type="invalid")
        waveform = encode_dna_complex("ATCG")

        with pytest.raises(ValueError):
            extractor.compute_spectrum(waveform)


class TestGCContentFunctions:
    """Test suite for GC content functions."""

    def test_compute_gc_content(self):
        """Test GC content computation."""
        # 50% GC
        seq1 = "ATCG"
        assert abs(compute_gc_content(seq1) - 50.0) < 0.01

        # 100% GC
        seq2 = "GCGC"
        assert abs(compute_gc_content(seq2) - 100.0) < 0.01

        # 0% GC
        seq3 = "ATAT"
        assert abs(compute_gc_content(seq3) - 0.0) < 0.01

        # 80% GC
        seq4 = "GCGCA"
        assert abs(compute_gc_content(seq4) - 80.0) < 0.01

    def test_gc_content_case_insensitive(self):
        """Test that GC content is case-insensitive."""
        seq_upper = "ATCG"
        seq_lower = "atcg"

        assert abs(compute_gc_content(seq_upper) - compute_gc_content(seq_lower)) < 0.01

    def test_assign_gc_quartile(self):
        """Test GC quartile assignment."""
        assert assign_gc_quartile(10.0) == 1
        assert assign_gc_quartile(30.0) == 2
        assert assign_gc_quartile(60.0) == 3
        assert assign_gc_quartile(80.0) == 4

        # Edge cases
        assert assign_gc_quartile(0.0) == 1
        assert assign_gc_quartile(25.0) == 2
        assert assign_gc_quartile(50.0) == 3
        assert assign_gc_quartile(75.0) == 4
        assert assign_gc_quartile(100.0) == 4


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_pipeline(self):
        """Test full analysis pipeline."""
        from modules.phi_phase import combined_transform

        # Encode sequence
        sequence = "ATCGATCGATCGATCGATCGATCG"
        waveform_base = encode_dna_complex(sequence)

        # Apply transforms
        phi_transformed, arcsin_compressed, _ = combined_transform(
            waveform_base, k=0.300, alpha=0.95
        )

        # Extract features
        extractor = SpectralFeatureExtractor(fft_size=256, window_type="hann")
        spectrum_base = extractor.compute_spectrum(waveform_base)
        spectrum_final = extractor.compute_spectrum(arcsin_compressed)

        features = extractor.extract_all_features(spectrum_base, spectrum_final)

        # Validate output
        assert len(features) > 0
        assert all(
            isinstance(v, (int, float, np.integer, np.floating))
            for v in features.values()
        )

    def test_batch_processing(self):
        """Test batch processing of multiple sequences."""
        sequences = [
            "ATCGATCGATCGATCG",
            "AAAACCCCGGGGTTTT",
            "ATATATATATATATA",
            "GCGCGCGCGCGCGCGC",
        ]

        extractor = SpectralFeatureExtractor()
        results = []

        for seq in sequences:
            seq_clean = seq.replace(" ", "")
            waveform = encode_dna_complex(seq_clean)
            spectrum = extractor.compute_spectrum(waveform)
            features = {
                "sequence": seq_clean,
                "gc_content": compute_gc_content(seq_clean),
                "entropy": extractor.compute_entropy(spectrum),
            }
            results.append(features)

        assert len(results) == len(sequences)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
