"""
Discrete Mathematics Module for Z Framework
==========================================

This module provides discrete mathematics functions for prime generation,
number theory, and cryptographic applications using the Z5D predictor framework.
"""

from .crypto_prime_generator import (
    generate_crypto_primes,
    CryptoPrimeConfig,
    CryptoPrimeResult,
    SpecialFormType
)

__all__ = [
    'generate_crypto_primes',
    'CryptoPrimeConfig', 
    'CryptoPrimeResult',
    'SpecialFormType'
]