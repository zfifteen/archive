"""
Symbolic Axiom Derivation Module
===============================

This module provides SymPy-based symbolic derivation and manipulation of the 
Z Framework's core axioms and mathematical formulations.

Modules:
    axiom_derivation: Symbolic derivation of framework axioms
    formula_manipulation: Advanced formula manipulation and simplification
    verification: Symbolic verification of mathematical relationships
    thales_theorem: Thales' theorem verification and Z Framework integration
"""

from .axiom_derivation import *
from .formula_manipulation import *
from .verification import *
from .thales_theorem import (
    ThalesTheoremsVerifier, 
    ZFrameworkThalesIntegration,
    run_comprehensive_thales_verification,
    ThalesTrialResult
)
from .noether_theorems import (
    derive_discrete_noether_first_theorem,
    derive_discrete_noether_second_theorem,
    derive_prime_density_conservation,
    derive_continuous_discrete_connection,
    noether_theorems_summary
)

__all__ = [
    'derive_universal_invariance',
    'derive_curvature_formula', 
    'derive_golden_ratio_transformation',
    'derive_5d_metric_tensor',
    'simplify_zeta_shift',
    'expand_geometric_series',
    'factor_polynomial_expressions',
    'verify_axiom_consistency',
    'verify_dimensional_analysis',
    'validate_symbolic_computation',
    'ThalesTheoremsVerifier',
    'ZFrameworkThalesIntegration',
    'run_comprehensive_thales_verification',
    'ThalesTrialResult',
    'derive_discrete_noether_first_theorem',
    'derive_discrete_noether_second_theorem',
    'derive_prime_density_conservation',
    'derive_continuous_discrete_connection',
    'noether_theorems_summary'
]