"""
Core Symbolic Module for Arctan Optimization
============================================

This module provides specialized symbolic optimizations for arctangent expressions
in the Z Framework.
"""

from .atan_opt import (
    simplify_arctan_half_angle, 
    atan_half_angle_derivative, 
    simplify_arctan_double_angle_at_half,
    apply_arctan_optimizations
)

__all__ = [
    'simplify_arctan_half_angle', 
    'atan_half_angle_derivative', 
    'simplify_arctan_double_angle_at_half',
    'apply_arctan_optimizations'
]