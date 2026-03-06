"""
Phi-Phase Transform and Arcsin Bridge for CRISPR gRNA Prediction

This module implements the golden-ratio (φ) phase transform and arcsin bridge
operations for complex DNA waveforms. The φ-phase transform applies a position-
dependent phase modulation tuned to the golden ratio, while the arcsin bridge
provides phase compression to sharpen spectral features.

Mathematical Formulation:
    φ-phase transform: θ'(n,k) = φ·((n mod φ)/φ)^k
    Arcsin bridge: z̃ = arcsin(α·sin(z)) where z = Arg(x) + θ'
    
    where φ = (1 + √5)/2 ≈ 1.618 (golden ratio)
          k ∈ [0.20, 0.40] is the phase power parameter
          α ∈ [0.85, 0.98] is the compression factor
"""

import numpy as np
from typing import Optional, Tuple


# Golden ratio constant
PHI = (1 + np.sqrt(5)) / 2  # ≈ 1.618033988749895


class PhiPhaseTransform:
    """
    Golden-ratio phase transform for complex DNA waveforms.
    
    Applies position-dependent phase modulation based on the golden ratio,
    with tunable power parameter k to control spectral morphology.
    
    Attributes:
        k (float): Phase power parameter, typically in [0.20, 0.40]
        phi (float): Golden ratio constant
    """
    
    def __init__(self, k: float = 0.300, phi: Optional[float] = None):
        """
        Initialize φ-phase transform.
        
        Args:
            k: Phase power parameter (default: 0.300, optimal empirically)
            phi: Golden ratio value (default: (1+√5)/2)
        """
        self.k = k
        self.phi = phi if phi is not None else PHI
        
        if not 0.0 <= k <= 1.0:
            raise ValueError(f"k parameter must be in [0, 1], got {k}")
    
    def compute_phase(self, n: int, length: Optional[int] = None) -> float:
        """
        Compute φ-phase value for position n.
        
        Args:
            n: Position index (0-based)
            length: Optional sequence length for normalization
            
        Returns:
            Phase value θ'(n,k)
        """
        # θ'(n,k) = φ·((n mod φ)/φ)^k
        n_mod_phi = n % self.phi
        normalized = n_mod_phi / self.phi
        phase = self.phi * (normalized ** self.k)
        
        return phase
    
    def compute_phase_array(self, length: int) -> np.ndarray:
        """
        Compute φ-phase array for all positions in a sequence.
        
        Args:
            length: Length of the sequence
            
        Returns:
            Array of phase values θ'(n,k) for n in [0, length)
        """
        positions = np.arange(length)
        n_mod_phi = positions % self.phi
        normalized = n_mod_phi / self.phi
        phases = self.phi * (normalized ** self.k)
        
        return phases
    
    def apply_transform(self, waveform: np.ndarray) -> np.ndarray:
        """
        Apply φ-phase transform to a complex waveform.
        
        Args:
            waveform: Complex numpy array representing DNA sequence
            
        Returns:
            Transformed waveform y[n;k] = x[n]·exp(i·θ'(n,k))
        """
        if not np.iscomplexobj(waveform):
            raise ValueError("Waveform must be a complex array")
        
        length = len(waveform)
        phases = self.compute_phase_array(length)
        
        # Apply phase modulation: y[n;k] = x[n] * exp(i*θ'(n,k))
        phase_factors = np.exp(1j * phases)
        transformed = waveform * phase_factors
        
        return transformed
    
    def sweep_k(
        self, 
        waveform: np.ndarray, 
        k_min: float = 0.20, 
        k_max: float = 0.40, 
        k_step: float = 0.005
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sweep over k parameter range and return transformed waveforms.
        
        Args:
            waveform: Input complex waveform
            k_min: Minimum k value (default: 0.20)
            k_max: Maximum k value (default: 0.40)
            k_step: Step size for k sweep (default: 0.005)
            
        Returns:
            Tuple of (k_values, transformed_waveforms) where transformed_waveforms
            is a 2D array with shape (n_k_values, waveform_length)
        """
        k_values = np.arange(k_min, k_max + k_step/2, k_step)
        transformed_waveforms = []
        
        original_k = self.k
        for k_val in k_values:
            self.k = k_val
            transformed = self.apply_transform(waveform)
            transformed_waveforms.append(transformed)
        
        # Restore original k
        self.k = original_k
        
        return k_values, np.array(transformed_waveforms)


def arcsin_bridge(
    waveform: np.ndarray, 
    alpha: float = 0.95,
    phi_phases: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Apply arcsin bridge compression to complex waveform phases.
    
    The arcsin bridge compresses the phase spectrum to sharpen fundamental
    frequency peaks and suppress sidelobes. The operation is:
        z̃ = arcsin(α·sin(z))
    where z = Arg(waveform) + θ'(n,k) (if phi_phases provided)
    
    Args:
        waveform: Complex numpy array
        alpha: Compression factor in [0.85, 0.98] (default: 0.95)
        phi_phases: Optional array of φ-phase values to add before compression
        
    Returns:
        Complex array with compressed phases: |waveform|·exp(i·z̃)
        
    Raises:
        ValueError: If alpha not in valid range
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be in [0, 1], got {alpha}")
    
    if alpha < 0.85 or alpha > 0.98:
        import warnings
        warnings.warn(
            f"alpha={alpha} is outside recommended range [0.85, 0.98]. "
            "This may lead to over-compression or under-compression."
        )
    
    # Extract magnitude and phase
    magnitude = np.abs(waveform)
    phase = np.angle(waveform)
    
    # Add φ-phase if provided
    if phi_phases is not None:
        if len(phi_phases) != len(waveform):
            raise ValueError(
                f"phi_phases length {len(phi_phases)} must match "
                f"waveform length {len(waveform)}"
            )
        phase = phase + phi_phases
    
    # Apply arcsin bridge: z̃ = arcsin(α·sin(z))
    compressed_phase = np.arcsin(alpha * np.sin(phase))
    
    # Reconstruct complex waveform with compressed phase
    compressed_waveform = magnitude * np.exp(1j * compressed_phase)
    
    return compressed_waveform


def combined_transform(
    waveform: np.ndarray,
    k: float = 0.300,
    alpha: float = 0.95,
    phi: Optional[float] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Apply combined φ-phase and arcsin bridge transform.
    
    This is a convenience function that applies both transforms in sequence:
    1. Compute φ-phase values
    2. Apply φ-phase transform to waveform
    3. Apply arcsin bridge with phase compression
    
    Args:
        waveform: Input complex waveform
        k: Phase power parameter (default: 0.300)
        alpha: Compression factor (default: 0.95)
        phi: Golden ratio value (default: None, uses standard value)
        
    Returns:
        Tuple of (phi_transformed, arcsin_compressed, phi_phases)
        where phi_transformed is after φ-phase only,
        arcsin_compressed is after both transforms,
        and phi_phases is the array of phase values
    """
    # Initialize transform
    phi_transform = PhiPhaseTransform(k=k, phi=phi)
    
    # Apply φ-phase transform
    phi_phases = phi_transform.compute_phase_array(len(waveform))
    phi_transformed = phi_transform.apply_transform(waveform)
    
    # Apply arcsin bridge to φ-phase transformed waveform
    arcsin_compressed = arcsin_bridge(phi_transformed, alpha=alpha)
    
    return phi_transformed, arcsin_compressed, phi_phases


# Convenience function for DNA sequence encoding
def encode_dna_complex(sequence: str) -> np.ndarray:
    """
    Encode DNA sequence as complex waveform.
    
    Encoding:
        A -> 1+0j (positive real)
        T -> -1+0j (negative real)
        C -> 0+1j (positive imaginary)
        G -> 0-1j (negative imaginary)
    
    Args:
        sequence: DNA sequence string (A, T, C, G)
        
    Returns:
        Complex numpy array
        
    Raises:
        ValueError: If sequence contains invalid characters
    """
    encoding = {
        'A': 1+0j, 
        'T': -1+0j, 
        'C': 0+1j, 
        'G': 0-1j
    }
    
    sequence = sequence.upper()
    
    try:
        waveform = np.array([encoding[base] for base in sequence])
    except KeyError as e:
        raise ValueError(f"Invalid DNA base: {e}. Sequence must contain only A, T, C, G")
    
    return waveform
