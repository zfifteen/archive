"""
Unit tests for phi_phase module
"""

import numpy as np
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.phi_phase import (
    PhiPhaseTransform,
    arcsin_bridge,
    encode_dna_complex,
    combined_transform,
    PHI
)


class TestPhiPhaseTransform:
    """Test suite for PhiPhaseTransform class."""
    
    def test_initialization(self):
        """Test proper initialization."""
        transform = PhiPhaseTransform(k=0.300)
        assert transform.k == 0.300
        assert abs(transform.phi - PHI) < 1e-10
    
    def test_invalid_k(self):
        """Test that invalid k values raise errors."""
        with pytest.raises(ValueError):
            PhiPhaseTransform(k=-0.1)
        with pytest.raises(ValueError):
            PhiPhaseTransform(k=1.5)
    
    def test_compute_phase(self):
        """Test phase computation for single position."""
        transform = PhiPhaseTransform(k=0.300)
        phase = transform.compute_phase(0)
        assert isinstance(phase, float)
        assert phase >= 0
    
    def test_compute_phase_array(self):
        """Test phase array computation."""
        transform = PhiPhaseTransform(k=0.300)
        phases = transform.compute_phase_array(100)
        assert len(phases) == 100
        assert all(isinstance(p, (float, np.floating)) for p in phases)
    
    def test_apply_transform(self):
        """Test applying transform to waveform."""
        transform = PhiPhaseTransform(k=0.300)
        waveform = np.array([1+0j, 0+1j, -1+0j, 0-1j])
        transformed = transform.apply_transform(waveform)
        
        assert len(transformed) == len(waveform)
        assert np.iscomplexobj(transformed)
        # Magnitude should be preserved
        assert np.allclose(np.abs(transformed), np.abs(waveform))
    
    def test_apply_transform_non_complex(self):
        """Test that non-complex input raises error."""
        transform = PhiPhaseTransform(k=0.300)
        waveform = np.array([1, 2, 3, 4])
        with pytest.raises(ValueError):
            transform.apply_transform(waveform)
    
    def test_sweep_k(self):
        """Test k-parameter sweep."""
        transform = PhiPhaseTransform(k=0.300)
        waveform = np.array([1+0j, 0+1j, -1+0j, 0-1j] * 10)
        
        k_values, transformed = transform.sweep_k(
            waveform, k_min=0.20, k_max=0.30, k_step=0.05
        )
        
        assert len(k_values) == 3  # 0.20, 0.25, 0.30
        assert transformed.shape[0] == len(k_values)
        assert transformed.shape[1] == len(waveform)
        # Original k should be restored
        assert transform.k == 0.300


class TestArcsinBridge:
    """Test suite for arcsin_bridge function."""
    
    def test_basic_compression(self):
        """Test basic arcsin compression."""
        waveform = np.array([1+0j, 0+1j, -1+0j, 0-1j])
        compressed = arcsin_bridge(waveform, alpha=0.95)
        
        assert len(compressed) == len(waveform)
        assert np.iscomplexobj(compressed)
    
    def test_alpha_range(self):
        """Test alpha parameter validation."""
        waveform = np.array([1+0j, 0+1j])
        
        # Valid alpha
        compressed = arcsin_bridge(waveform, alpha=0.95)
        assert compressed is not None
        
        # Invalid alpha (should raise)
        with pytest.raises(ValueError):
            arcsin_bridge(waveform, alpha=-0.1)
        with pytest.raises(ValueError):
            arcsin_bridge(waveform, alpha=1.5)
    
    def test_with_phi_phases(self):
        """Test arcsin bridge with phi phases."""
        waveform = np.array([1+0j, 0+1j, -1+0j, 0-1j])
        phi_phases = np.array([0.1, 0.2, 0.3, 0.4])
        
        compressed = arcsin_bridge(waveform, alpha=0.95, phi_phases=phi_phases)
        assert len(compressed) == len(waveform)
    
    def test_phi_phases_length_mismatch(self):
        """Test that mismatched phi_phases length raises error."""
        waveform = np.array([1+0j, 0+1j])
        phi_phases = np.array([0.1, 0.2, 0.3])
        
        with pytest.raises(ValueError):
            arcsin_bridge(waveform, alpha=0.95, phi_phases=phi_phases)
    
    def test_magnitude_preservation(self):
        """Test that magnitude is approximately preserved."""
        waveform = np.array([1+0j, 0+1j, -1+0j, 0-1j])
        compressed = arcsin_bridge(waveform, alpha=0.95)
        
        # Magnitudes should be exactly preserved
        assert np.allclose(np.abs(compressed), np.abs(waveform))


class TestEncodeDNAComplex:
    """Test suite for encode_dna_complex function."""
    
    def test_valid_sequence(self):
        """Test encoding of valid DNA sequence."""
        sequence = "ATCG"
        waveform = encode_dna_complex(sequence)
        
        assert len(waveform) == 4
        assert np.iscomplexobj(waveform)
        
        # Check specific encodings
        assert waveform[0] == 1+0j  # A
        assert waveform[1] == -1+0j  # T
        assert waveform[2] == 0+1j  # C
        assert waveform[3] == 0-1j  # G
    
    def test_case_insensitive(self):
        """Test that encoding is case-insensitive."""
        seq_upper = "ATCG"
        seq_lower = "atcg"
        seq_mixed = "AtCg"
        
        w1 = encode_dna_complex(seq_upper)
        w2 = encode_dna_complex(seq_lower)
        w3 = encode_dna_complex(seq_mixed)
        
        assert np.allclose(w1, w2)
        assert np.allclose(w1, w3)
    
    def test_invalid_bases(self):
        """Test that invalid bases raise error."""
        with pytest.raises(ValueError):
            encode_dna_complex("ATCGN")
        with pytest.raises(ValueError):
            encode_dna_complex("ATCG123")


class TestCombinedTransform:
    """Test suite for combined_transform function."""
    
    def test_combined_transform(self):
        """Test combined φ-phase and arcsin transform."""
        sequence = "ATCGATCG"
        waveform = encode_dna_complex(sequence)
        
        phi_transformed, arcsin_compressed, phi_phases = combined_transform(
            waveform, k=0.300, alpha=0.95
        )
        
        assert len(phi_transformed) == len(waveform)
        assert len(arcsin_compressed) == len(waveform)
        assert len(phi_phases) == len(waveform)
        
        assert np.iscomplexobj(phi_transformed)
        assert np.iscomplexobj(arcsin_compressed)
    
    def test_transform_parameters(self):
        """Test with different parameters."""
        sequence = "ATCGATCGATCGATCG"
        waveform = encode_dna_complex(sequence)
        
        # Test with different k values
        _, compressed_k02, _ = combined_transform(waveform, k=0.2, alpha=0.95)
        _, compressed_k03, _ = combined_transform(waveform, k=0.3, alpha=0.95)
        
        # Results should be different for different k
        assert not np.allclose(compressed_k02, compressed_k03)


class TestPhysicalProperties:
    """Test physical properties and edge cases."""
    
    def test_golden_ratio_value(self):
        """Test that PHI is the golden ratio."""
        expected_phi = (1 + np.sqrt(5)) / 2
        assert abs(PHI - expected_phi) < 1e-10
    
    def test_phase_periodicity(self):
        """Test quasi-periodic nature of phi-phase."""
        transform = PhiPhaseTransform(k=0.300)
        phases = transform.compute_phase_array(1000)
        
        # Phases should not be exactly periodic
        # Check that no exact period exists in first 100 samples
        for period in range(2, 100):
            if not np.allclose(phases[:period], phases[period:2*period]):
                break
        else:
            pytest.fail("Phases appear to be exactly periodic")
    
    def test_k_effect_on_phase_distribution(self):
        """Test that k affects phase distribution."""
        transform_low = PhiPhaseTransform(k=0.1)
        transform_high = PhiPhaseTransform(k=0.9)
        
        length = 100
        phases_low = transform_low.compute_phase_array(length)
        phases_high = transform_high.compute_phase_array(length)
        
        # High k should have more variation
        assert np.std(phases_high) > np.std(phases_low)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
