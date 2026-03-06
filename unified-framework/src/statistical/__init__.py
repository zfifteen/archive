"""
Statistical Analysis Module

This module provides statistical tools and analysis capabilities for the Z Framework.
"""

# Enhanced zeta spacing predictor (Issue #724)
from .zeta_spacing_predictor import (
    tau_sieve,
    kappa_from_tau,
    fit_linear_with_beta,
    z5d_zeta_spacings,
    z5d_zeta_approx,
    rescale_gammas,
    EnhancedZetaSpacingPredictor
)

__all__ = [
    # Enhanced zeta spacing predictor
    'tau_sieve',
    'kappa_from_tau', 
    'fit_linear_with_beta',
    'z5d_zeta_spacings',
    'z5d_zeta_approx',
    'rescale_gammas',
    'EnhancedZetaSpacingPredictor'
]