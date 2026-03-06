"""
Z Framework Quantum Computing Integration Module
===============================================

This module provides quantum computing integration capabilities for the Z Framework,
specifically focusing on real-time zeta function zero approximations and quantum-enhanced
prime number prediction algorithms.

The core hypothesis implemented here is that the integration of Z5D calibration
(with k* ≈ 0.04449 and density enhancement of ~210% at N=10^6) into quantum computing
algorithms can revolutionize prime number prediction by enabling real-time zeta
function zero approximations with unprecedented accuracy.

Modules:
--------
real_time_zeta_approximation : Real-time zeta zero approximation with quantum enhancement
"""

from .real_time_zeta_approximation import (
    RealTimeZetaApproximator,
    QuantumZetaConfig,
    approximate_zeta_zero_real_time,
    quantum_prime_prediction,
    validate_real_time_hypothesis
)

__all__ = [
    'RealTimeZetaApproximator',
    'QuantumZetaConfig', 
    'approximate_zeta_zero_real_time',
    'quantum_prime_prediction',
    'validate_real_time_hypothesis'
]