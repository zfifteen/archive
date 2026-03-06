"""
Bio.QuantumTopology - Quantum-Inspired Topological Analysis for Biological Sequences

This module integrates the Z Framework's mathematical tools with Biopython,
providing quantum-inspired geometric transformations and topological analysis
of biological sequences using φ-based geodesics and Bell-type correlations.

Key Features:
- Helical coordinate generation using golden ratio geodesics
- Quantum-inspired sequence alignment metrics
- Topological visualization and analysis
- Pure Python implementation with NumPy/SciPy

Mathematical Foundation:
- Universal invariant: Z = A(B/c)
- Geodesic mapping: θ'(n, k) = φ·{n/φ}^k
- Optimal curvature: k* ≈ 0.3 for conditional prime density improvement under canonical benchmark methodology
- Golden ratio: φ = (1 + √5)/2

Usage:
    from Bio.QuantumTopology import generate_helical_coordinates, quantum_alignment
    from Bio.Seq import Seq
    
    seq = Seq("ATGCGATCGATC")
    coords = generate_helical_coordinates(seq)
    alignment_score = quantum_alignment(seq1, seq2)
    
**Important**: Bio.Seq comes from the biopython package. If you see import errors:
    pip install biopython
"""

# Check if biopython is available and provide helpful error message
try:
    from Bio.Seq import Seq
    _BIOPYTHON_AVAILABLE = True
except ImportError:
    _BIOPYTHON_AVAILABLE = False
    import warnings
    warnings.warn(
        "Bio.Seq requires biopython package. "
        "Install with: pip install biopython\n"
        "Note: Bio.Seq comes from 'biopython', not a separate 'seq' package.",
        ImportWarning,
        stacklevel=2
    )

from .helical import generate_helical_coordinates, compute_quantum_correlations

# Only import biopython-dependent modules if biopython is available
if _BIOPYTHON_AVAILABLE:
    from .alignment import quantum_alignment, compute_bell_violation
    from .visualizer import export_helical_visualization
    from .geodesic_hotspot_mapper import ZGeodesicHotspotMapper
    
    __all__ = [
        'generate_helical_coordinates',
        'compute_quantum_correlations', 
        'quantum_alignment',
        'compute_bell_violation',
        'export_helical_visualization',
        'ZGeodesicHotspotMapper'
    ]
else:
    __all__ = [
        'generate_helical_coordinates',
        'compute_quantum_correlations'
    ]

__version__ = "0.1.0"
__author__ = "DAL"

# Module-level constants from Z Framework
PHI = (1 + 5**0.5) / 2  # Golden ratio
E_SQUARED = 2.71828**2  # e² normalization constant  
OPTIMAL_K = 0.3  # Optimal curvature parameter for density enhancement
SPEED_OF_LIGHT_NM_NS = 299.792458  # Speed of light in nm/ns for quantum transforms