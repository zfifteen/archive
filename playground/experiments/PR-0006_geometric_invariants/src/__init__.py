"""
Geometric Invariants Framework - Unifying Cryptography and Biology

This package implements geometric invariants from the Z Framework that apply
to both RSA factorization (cryptography) and DNA sequence analysis (biology).

Core components:
- z_framework: Curvature metrics and golden-ratio phase functions
- crypto: QMC sampling and RSA candidate generation
- bio: DNA spectral analysis and CRISPR guide optimization
"""

from .z_framework import (
    divisor_count,
    curvature_metric,
    golden_ratio_phase,
    ZFrameworkCalculator
)

__all__ = [
    'divisor_count',
    'curvature_metric',
    'golden_ratio_phase',
    'ZFrameworkCalculator',
]

__version__ = '0.1.0'
