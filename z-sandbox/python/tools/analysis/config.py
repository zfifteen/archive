"""
Configuration guardrails for zero-bias resonance validation.

Provides validation and enforcement of precision requirements and deterministic RNG seeding.
"""

import random
import numpy as np
from typing import Optional

class ConfigGuardrails:
    """Guardrails for configuration parameters in zero-bias validation."""

    MIN_PRECISION_DIGITS = 300
    REQUIRED_SEED = 42

    @staticmethod
    def validate_precision(precision_digits: int) -> bool:
        """Validate that precision meets minimum requirements."""
        return precision_digits >= ConfigGuardrails.MIN_PRECISION_DIGITS

    @staticmethod
    def enforce_precision(precision_digits: Optional[int] = None) -> int:
        """Enforce minimum precision, using default if not provided."""
        if precision_digits is None:
            return ConfigGuardrails.MIN_PRECISION_DIGITS
        if not ConfigGuardrails.validate_precision(precision_digits):
            raise ValueError(f"Precision must be at least {ConfigGuardrails.MIN_PRECISION_DIGITS} digits, got {precision_digits}")
        return precision_digits

    @staticmethod
    def validate_seed(seed: int) -> bool:
        """Validate that seed matches required deterministic value."""
        return seed == ConfigGuardrails.REQUIRED_SEED

    @staticmethod
    def enforce_seed(seed: Optional[int] = None) -> int:
        """Enforce deterministic seeding, using required seed."""
        if seed is None:
            seed = ConfigGuardrails.REQUIRED_SEED
        if not ConfigGuardrails.validate_seed(seed):
            raise ValueError(f"Seed must be {ConfigGuardrails.REQUIRED_SEED} for deterministic results, got {seed}")
        return seed

    @staticmethod
    def setup_rng(seed: Optional[int] = None) -> int:
        """Setup random number generators with enforced seed."""
        enforced_seed = ConfigGuardrails.enforce_seed(seed)
        random.seed(enforced_seed)
        np.random.seed(enforced_seed)
        return enforced_seed

    @staticmethod
    def validate_config(precision_digits: int, seed: int) -> dict:
        """Validate complete configuration and return validation results."""
        precision_valid = ConfigGuardrails.validate_precision(precision_digits)
        seed_valid = ConfigGuardrails.validate_seed(seed)

        return {
            'precision_valid': precision_valid,
            'seed_valid': seed_valid,
            'all_valid': precision_valid and seed_valid,
            'min_precision': ConfigGuardrails.MIN_PRECISION_DIGITS,
            'required_seed': ConfigGuardrails.REQUIRED_SEED
        }