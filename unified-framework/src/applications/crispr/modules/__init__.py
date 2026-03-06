"""
CRISPR Spectral Resonance Optimization Modules

This package contains core modules for φ-phase transform, arcsin bridge,
and spectral feature extraction for CRISPR gRNA prediction.
"""

from .phi_phase import PhiPhaseTransform, arcsin_bridge
from .spectral_features import SpectralFeatureExtractor

__all__ = [
    'PhiPhaseTransform',
    'arcsin_bridge',
    'SpectralFeatureExtractor',
]
