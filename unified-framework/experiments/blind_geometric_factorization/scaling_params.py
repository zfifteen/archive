"""
PR-123/969 Scaling Parameters for Geometric Factorization

This module implements the scaling formulas from PR-123 (curvature drift & scaling laws)
and PR-969 (parameter pipeline) for adaptive geometric factorization.

Scaling Formulas:
- Threshold: T(N) = 0.92 - 0.10 * log2(bitLen/30)
- k-shift: k(N) = 0.35 + 0.0302 * ln(bitLen/30)
- Sample count: samples(N) = round(30000 * (bitLen/60)), min 5000
- Precision: precision(N) = 4 * bitLen + 200

These formulas were calibrated for geometric resonance detection across
bit lengths from 30 to 256 bits.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScalingParams:
    """Container for scale-adaptive factorization parameters."""
    bit_length: int
    threshold: float  # T(N) - resonance acceptance threshold
    k_shift: float    # k(N) - geodesic/curvature parameter
    sample_count: int # Number of resonance evaluations
    precision: int    # Decimal precision for arithmetic
    kappa_estimated: Optional[float] = None  # From curvature measurements
    phase_drift: Optional[float] = None      # From phase fit data
    
    def __str__(self) -> str:
        return (
            f"ScalingParams(bitLen={self.bit_length}, "
            f"T={self.threshold:.4f}, k={self.k_shift:.4f}, "
            f"samples={self.sample_count}, precision={self.precision})"
        )


def compute_threshold(bit_length: int) -> float:
    """
    Compute threshold T(N) using PR-123 formula.
    
    T(N) = 0.92 - 0.10 * log2(bitLen/30)
    
    The threshold decreases logarithmically with bit length, reflecting
    that resonance peaks become less pronounced at larger scales.
    """
    if bit_length <= 0:
        raise ValueError("Bit length must be positive")
    
    ratio = bit_length / 30.0
    return 0.92 - 0.10 * math.log2(ratio)


def compute_k_shift(bit_length: int) -> float:
    """
    Compute k-shift k(N) using PR-123 formula.
    
    k(N) = 0.35 + 0.0302 * ln(bitLen/30)
    
    The k parameter increases logarithmically with bit length,
    adjusting the geodesic curvature sensitivity.
    """
    if bit_length <= 0:
        raise ValueError("Bit length must be positive")
    
    ratio = bit_length / 30.0
    return 0.35 + 0.0302 * math.log(ratio)


def compute_sample_count(bit_length: int) -> int:
    """
    Compute sample count using PR-969 formula.
    
    samples(N) = round(30000 * (bitLen/60)), minimum 5000
    
    Linear scaling ensures sufficient resonance evaluations at larger scales.
    """
    if bit_length <= 0:
        raise ValueError("Bit length must be positive")
    
    samples = round(30000 * (bit_length / 60.0))
    return max(5000, samples)


def compute_precision(bit_length: int) -> int:
    """
    Compute required decimal precision.
    
    precision(N) = 4 * bitLen + 200
    
    Ensures sufficient precision for accurate arithmetic at the given scale.
    """
    if bit_length <= 0:
        raise ValueError("Bit length must be positive")
    
    return 4 * bit_length + 200


def get_scaling_params(N: int) -> ScalingParams:
    """
    Get complete scaling parameters for a given number N.
    
    Uses PR-123/969 formulas to compute all adaptive parameters.
    
    Parameters
    ----------
    N : int
        The semiprime to factor
        
    Returns
    -------
    ScalingParams
        Complete parameter set for geometric factorization
    """
    bit_length = N.bit_length()
    
    threshold = compute_threshold(bit_length)
    k_shift = compute_k_shift(bit_length)
    sample_count = compute_sample_count(bit_length)
    precision = compute_precision(bit_length)
    
    # Estimate kappa based on bit length (from curvature measurements)
    # These are interpolated from PR-123 measurements at {30, 60, 90, 127, 256} bits
    if bit_length <= 30:
        kappa = 0.30
    elif bit_length <= 60:
        kappa = 0.35 + 0.05 * (bit_length - 30) / 30
    elif bit_length <= 90:
        kappa = 0.40 + 0.02 * (bit_length - 60) / 30
    elif bit_length <= 127:
        kappa = 0.42 + 0.02 * (bit_length - 90) / 37
    else:
        kappa = 0.44 + 0.01 * min((bit_length - 127) / 129, 1.0)
    
    # Phase drift estimate (increases with scale)
    phase_drift = 0.02 + 0.06 * math.log(bit_length / 30.0) if bit_length > 30 else 0.02
    
    return ScalingParams(
        bit_length=bit_length,
        threshold=threshold,
        k_shift=k_shift,
        sample_count=sample_count,
        precision=precision,
        kappa_estimated=kappa,
        phase_drift=phase_drift
    )


# Reference: Known Gate-127 parameters for comparison
GATE_127_PARAMS = ScalingParams(
    bit_length=127,
    threshold=0.7118,
    k_shift=0.3936,
    sample_count=63500,
    precision=708,
    kappa_estimated=0.44,
    phase_drift=0.08
)


if __name__ == "__main__":
    # Test scaling computations
    print("PR-123/969 Scaling Parameter Tests")
    print("=" * 60)
    
    test_bits = [32, 64, 90, 127, 256]
    for bits in test_bits:
        # Create a test number with approximately that many bits
        N = (1 << (bits - 1)) + (1 << (bits // 2))
        params = get_scaling_params(N)
        print(f"\n{bits}-bit:")
        print(f"  Threshold T(N) = {params.threshold:.4f}")
        print(f"  k-shift k(N) = {params.k_shift:.4f}")
        print(f"  Sample count = {params.sample_count}")
        print(f"  Precision = {params.precision}")
        print(f"  κ_estimated = {params.kappa_estimated:.2f}")
        print(f"  Phase drift = {params.phase_drift:.2f}")
    
    # Compare with Gate-127 reference
    print("\n" + "=" * 60)
    print("Gate-127 Reference Comparison:")
    gate127_N = 137524771864208156028430259349934309717
    computed = get_scaling_params(gate127_N)
    print(f"  Computed: {computed}")
    print(f"  Reference: {GATE_127_PARAMS}")
