"""
Z Framework Core Module
======================

Core implementation of the Z Framework with baseline, enhanced Z_5D,
and geodesic mapping capabilities.

The Z Framework is built on the cornerstone invariant principle,
formalized in cornerstone_invariant.py, which implements the 
Lorentz-inspired normalization equation Z = A(B/c).

For direct access to the cornerstone invariant framework, import:
    from core.cornerstone_invariant import (
        CornerstoneInvariant,
        PhysicalInvariant,
        DiscreteInvariant,
        NumberTheoreticInvariant
    )
"""

from .z_baseline import BaselineZFramework, baseline_z_predictor
from .z_5d_enhanced import Z5DEnhancedPredictor
from .geodesic_mapping import GeodesicMapper
from .zero_line import ZeroLine
from .sha256_pattern_analyzer import SHA256PatternAnalyzer

__all__ = [
    'BaselineZFramework',
    'baseline_z_predictor', 
    'Z5DEnhancedPredictor',
    'GeodesicMapper',
    'ZeroLine',
    'SHA256PatternAnalyzer'
]

__version__ = "1.0.0"
__author__ = "Dionisio Alberto Lopez III"