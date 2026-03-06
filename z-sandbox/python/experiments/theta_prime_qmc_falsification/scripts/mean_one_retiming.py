#!/usr/bin/env python3
"""
Mean-One Retiming Implementation

Implements deterministic φ-based interval biasing with mean-one cadence
for QMC sampling retiming. Enforces E[interval'] = base with bias bounded
in [1-α, 1+α] where α ≤ 0.2.

Mathematical Definition:
- Golden LCG: G = 0x9E3779B97F4A7C15
- Deterministic φ: u = (slot * G & 0xFFFFFFFFFFFFFFFF) / 2^64
- Mean-one bias: b = 1.0 + α * (2*u - 1)
- Bounded interval: interval' = base * clip(b, 1-α, 1+α)
"""

from typing import Union, List
import numpy as np

# 64-bit golden ratio LCG constant
GOLDEN_LCG_CONSTANT = 0x9E3779B97F4A7C15
U64_MAX = 0xFFFFFFFFFFFFFFFF


def golden_u64(slot: int) -> float:
    """
    Deterministic golden-ratio based pseudo-random number generator.
    
    Uses 64-bit golden LCG to generate deterministic uniform [0,1] values
    without floating-point arithmetic in the core computation.
    
    Args:
        slot: Integer slot index (non-negative)
        
    Returns:
        Pseudo-random value in [0, 1]
        
    Example:
        >>> u1 = golden_u64(0)
        >>> u2 = golden_u64(1)
        >>> 0.0 <= u1 <= 1.0 and 0.0 <= u2 <= 1.0
        True
    """
    if slot < 0:
        raise ValueError(f"slot must be non-negative, got {slot}")
    
    # 64-bit golden LCG: multiply and mask
    product = (slot * GOLDEN_LCG_CONSTANT) & U64_MAX
    
    # Convert to [0, 1] by dividing by 2^64
    return product / (2**64)


def interval_biased(
    base_ms: float,
    slot: int,
    alpha: float = 0.2
) -> float:
    """
    Mean-one interval biasing with bounded perturbation.
    
    Applies deterministic golden-ratio-based bias to base interval
    while maintaining mean-one property: E[interval'] = base.
    
    Args:
        base_ms: Base interval value (must be positive)
        slot: Slot index for deterministic pseudo-random
        alpha: Bias amplitude, must be in (0, 0.2] (default: 0.2)
        
    Returns:
        Biased interval with E[result] = base_ms
        
    Raises:
        ValueError: If base_ms <= 0, slot < 0, or alpha not in (0, 0.2]
        
    Example:
        >>> # Mean-one property verification
        >>> base = 100.0
        >>> samples = [interval_biased(base, i, 0.2) for i in range(10000)]
        >>> abs(np.mean(samples) - base) < 1.0  # Within 1% of base
        True
    """
    if base_ms <= 0:
        raise ValueError(f"base_ms must be positive, got {base_ms}")
    if slot < 0:
        raise ValueError(f"slot must be non-negative, got {slot}")
    if not (0 < alpha <= 0.2):
        raise ValueError(f"alpha must be in (0, 0.2], got {alpha}")
    
    # Get deterministic uniform [0, 1]
    u = golden_u64(slot)
    
    # Mean-one bias: b = 1 + α(2u - 1)
    # E[b] = 1 + α(2*E[u] - 1) = 1 + α(2*0.5 - 1) = 1
    b = 1.0 + alpha * (2.0 * u - 1.0)
    
    # Clip to bounds [1-α, 1+α]
    lo, hi = 1.0 - alpha, 1.0 + alpha
    b_clipped = min(max(b, lo), hi)
    
    # Apply bias to base interval
    return base_ms * b_clipped


def interval_biased_batch(
    base_ms: float,
    n_samples: int,
    alpha: float = 0.2,
    seed: int = 0
) -> np.ndarray:
    """
    Generate batch of biased intervals with mean-one property.
    
    Vectorized version for efficient generation of multiple intervals.
    
    Args:
        base_ms: Base interval value
        n_samples: Number of intervals to generate
        alpha: Bias amplitude in (0, 0.2]
        seed: Starting slot index (default: 0)
        
    Returns:
        Array of shape (n_samples,) with biased intervals
        
    Example:
        >>> intervals = interval_biased_batch(100.0, 1000, alpha=0.15)
        >>> abs(intervals.mean() - 100.0) < 0.5
        True
        >>> intervals.min() >= 85.0 and intervals.max() <= 115.0
        True
    """
    if base_ms <= 0:
        raise ValueError(f"base_ms must be positive, got {base_ms}")
    if n_samples <= 0:
        raise ValueError(f"n_samples must be positive, got {n_samples}")
    if not (0 < alpha <= 0.2):
        raise ValueError(f"alpha must be in (0, 0.2], got {alpha}")
    
    # Generate slots
    slots = np.arange(seed, seed + n_samples, dtype=np.uint64)
    
    # Vectorized golden LCG - use Python's arbitrary precision for constants
    # Convert to object array to handle large integers properly
    products = np.zeros(n_samples, dtype=np.float64)
    for i, slot in enumerate(slots):
        products[i] = ((int(slot) * GOLDEN_LCG_CONSTANT) & U64_MAX) / (2**64)
    
    u_values = products
    
    # Mean-one bias
    b_values = 1.0 + alpha * (2.0 * u_values - 1.0)
    
    # Clip to bounds
    lo, hi = 1.0 - alpha, 1.0 + alpha
    b_clipped = np.clip(b_values, lo, hi)
    
    # Apply to base
    return base_ms * b_clipped


def verify_mean_one_property(
    base_ms: float = 100.0,
    n_samples: int = 100000,
    alpha: float = 0.2,
    tolerance: float = 0.01
) -> dict:
    """
    Verify mean-one property of interval biasing.
    
    Statistical test that E[interval'] ≈ base within specified tolerance.
    
    Args:
        base_ms: Base interval to test
        n_samples: Number of samples for Monte Carlo estimate
        alpha: Bias amplitude
        tolerance: Acceptable relative error (default: 1%)
        
    Returns:
        Dictionary with verification results including mean, std, and pass/fail
    """
    intervals = interval_biased_batch(base_ms, n_samples, alpha)
    
    mean_val = intervals.mean()
    std_val = intervals.std()
    min_val = intervals.min()
    max_val = intervals.max()
    
    # Check mean-one property
    relative_error = abs(mean_val - base_ms) / base_ms
    passes = relative_error < tolerance
    
    # Check bounds
    expected_min = base_ms * (1.0 - alpha)
    expected_max = base_ms * (1.0 + alpha)
    bounds_ok = (min_val >= expected_min - 1e-6) and (max_val <= expected_max + 1e-6)
    
    return {
        'base': base_ms,
        'alpha': alpha,
        'n_samples': n_samples,
        'mean': mean_val,
        'std': std_val,
        'min': min_val,
        'max': max_val,
        'expected_min': expected_min,
        'expected_max': expected_max,
        'relative_error': relative_error,
        'tolerance': tolerance,
        'mean_one_passes': passes,
        'bounds_ok': bounds_ok,
        'all_checks_pass': passes and bounds_ok
    }


if __name__ == "__main__":
    print("Mean-One Retiming Validation")
    print("=" * 70)
    
    # Test deterministic golden_u64
    print("\n1. Testing golden_u64 determinism:")
    for slot in [0, 1, 10, 100]:
        u = golden_u64(slot)
        print(f"   slot={slot:3d}: u={u:.10f}")
    
    # Test mean-one property for different alphas
    print("\n2. Testing mean-one property:")
    for alpha in [0.05, 0.10, 0.15, 0.20]:
        result = verify_mean_one_property(base_ms=100.0, n_samples=100000, alpha=alpha)
        status = "✓ PASS" if result['all_checks_pass'] else "✗ FAIL"
        print(f"\n   α={alpha:.2f}: {status}")
        print(f"      Mean: {result['mean']:.6f} (target: {result['base']:.6f})")
        print(f"      Relative error: {result['relative_error']:.6%}")
        print(f"      Range: [{result['min']:.4f}, {result['max']:.4f}]")
        print(f"      Expected: [{result['expected_min']:.4f}, {result['expected_max']:.4f}]")
    
    # Test batch consistency
    print("\n3. Testing batch generation consistency:")
    base = 50.0
    alpha = 0.15
    batch1 = interval_biased_batch(base, 100, alpha, seed=42)
    batch2 = interval_biased_batch(base, 100, alpha, seed=42)
    print(f"   Seed=42, n=100: Batches identical: {np.allclose(batch1, batch2)}")
    print(f"   Batch mean: {batch1.mean():.4f} (expected: {base:.4f})")
    
    print("\n" + "=" * 70)
    print("All validations complete.")
