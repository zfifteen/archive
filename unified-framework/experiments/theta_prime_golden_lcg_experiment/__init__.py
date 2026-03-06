"""
θ′-Biased Ordering via Golden LCG Experiment

A self-contained experiment to test the hypothesis that θ′-biased ordering
via golden LCG yields >0% lift in variance reduction (RSA QMC), spectral
disruption scoring (CRISPR), and rekey success under drift (crypto).

Author: Unified Framework Team
Date: November 2025
"""

__version__ = "1.0.0"
__author__ = "Unified Framework Team"

# Core components
from .golden_lcg import GoldenLCG
from .theta_prime_bias import ThetaPrimeBias

# Test modules
from .rsa_qmc_test import RSAQMCTest
from .crispr_spectral_test import CRISPRSpectralTest
from .crypto_rekey_test import CryptoRekeyTest
from .cross_validation import CrossValidation

__all__ = [
    'GoldenLCG',
    'ThetaPrimeBias',
    'RSAQMCTest',
    'CRISPRSpectralTest',
    'CryptoRekeyTest',
    'CrossValidation',
]
