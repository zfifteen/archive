#!/usr/bin/env python3
"""
Universal Frame Shift Theory: Z Data Export for Primes
======================================================

Modified implementation to compute and export Z data for the first 1,000,000 primes
to a CSV file, based on the discrete domain Universal Form: Z = n(Δₙ/Δₘₐₓ)

Author: [Author Name]
Date: [Date]
Version: 1.4 (Using UniversalFrameShift Class)

Changes:
- Computes frame shifts and Z = n * Δₙ (with Δₘₐₓ implicitly 1 after clipping)
- Uses UniversalFrameShift class for Z computation
- Exports to CSV for first 1,000,000 primes
- Exits with summary statistics

Usage:
    python universal_frame_shift.py

Requirements:
    numpy >= 1.19.0
"""

import math
import numpy as np
import csv
import time
from typing import Union

# ============================================================================
# UNIVERSAL CONSTANTS AND PARAMETERS
# ============================================================================

N_PRIMES_TARGET = 1000000
N_POINTS = 15485863  # The 1,000,000th prime; set to include exactly or more
DELTA_MAX = 1.0  # Theoretical maximum frame shift after clipping

# ============================================================================
# CORE UNIVERSAL FRAME SHIFT IMPLEMENTATION
# ============================================================================

class UniversalFrameShift:
    """
    Implements the Universal Form: Z = A(B/C)

    In discrete domain: Z = n(Δₙ/Δₘₐₓ)
    Provides bidirectional transformation between observer and universal frames.
    Supports scalar and array inputs.
    """

    def __init__(self, rate: float, invariant_limit: float = math.e):
        """
        Initialize Universal Frame Shift transformer.

        Args:
            rate: Domain-specific rate parameter (B in universal form)
            invariant_limit: Universal invariant constant (C in universal form)

        Raises:
            ValueError: If rate is zero or negative
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")

        self._rate = rate
        self._invariant_limit = invariant_limit
        self._correction_factor = rate / invariant_limit

    @property
    def rate(self) -> float:
        """Get the rate parameter."""
        return self._rate

    @property
    def invariant_limit(self) -> float:
        """Get the invariant limit."""
        return self._invariant_limit

    @property
    def correction_factor(self) -> float:
        """Get the computed correction factor."""
        return self._correction_factor

    def transform(self, observed_quantity: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Transform from observer frame to universal frame.

        Args:
            observed_quantity: Value(s) measured in observer frame (scalar or array)

        Returns:
            Corresponding value(s) in universal coordinates
        """
        return observed_quantity * self._correction_factor

    def inverse_transform(self, universal_quantity: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Transform from universal frame back to observer frame.

        Args:
            universal_quantity: Value(s) in universal coordinates (scalar or array)

        Returns:
            Corresponding value(s) in observer frame
        """
        return universal_quantity / self._correction_factor

# ============================================================================
# MATHEMATICAL UTILITIES
# ============================================================================

def sieve_prime_mask(n: int) -> np.ndarray:
    """
    Generate boolean mask for primes in range [1, n] using Sieve of Eratosthenes.

    Args:
        n: Upper limit of range

    Returns:
        Boolean array of length n where True indicates prime (indices 1 to n)
    """
    if n < 2:
        return np.array([], dtype=bool)

    sieve = np.ones(n + 1, dtype=bool)
    sieve[0:2] = False
    for i in range(2, int(np.sqrt(n)) + 1):
        if sieve[i]:
            sieve[i * i::i] = False
    return sieve[1:]  # Align with n=1 to n

def compute_frame_shifts(n_array: np.ndarray, max_n: int) -> np.ndarray:
    """
    Vectorized computation of frame shifts Δₙ for all positions.

    Args:
        n_array: Array of positions (1 to max_n)
        max_n: Maximum position (for normalization)

    Returns:
        Array of frame shift values Δₙ ∈ [0, 1]
    """
    shifts = np.zeros_like(n_array, dtype=float)
    mask = n_array > 1
    if np.any(mask):
        log_max = np.log(max_n)
        base_shift = np.log(n_array[mask]) / log_max
        gap_phase = 2 * np.pi * n_array[mask] / (np.log(n_array[mask]) + 1)
        oscillation = 0.1 * np.sin(gap_phase)
        shifts[mask] = base_shift + oscillation
    return np.clip(shifts, 0.0, 1.0)  # Enforce theoretical bounds [0,1]

# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def run_analysis(verbose: bool = True) -> dict:
    """
    Compute Z data for the first 1,000,000 primes and write to CSV.

    Args:
        verbose: Whether to print detailed output

    Returns:
        Dictionary containing summary statistics
    """
    if verbose:
        print("Universal Frame Shift Theory: Z Data Export for Primes")
        print("=" * 70)
        print(f"Target primes: {N_PRIMES_TARGET}")
        print(f"Upper limit (n): {N_POINTS}")
        print()

    # Precompute shared arrays
    start_time = time.time()
    n_array = np.arange(1, N_POINTS + 1)
    prime_mask = sieve_prime_mask(N_POINTS)
    frame_shifts = compute_frame_shifts(n_array, N_POINTS)

    num_primes = np.sum(prime_mask)
    if num_primes < N_PRIMES_TARGET:
        raise ValueError(f"Not enough primes up to {N_POINTS}: only {num_primes} found")

    # Extract first N_PRIMES_TARGET primes and their shifts
    primes = n_array[prime_mask][:N_PRIMES_TARGET]
    prime_shifts = frame_shifts[prime_mask][:N_PRIMES_TARGET]

    # Compute Z using UniversalFrameShift class
    z_values = []
    for p, d in zip(primes, prime_shifts):
        transformer = UniversalFrameShift(rate=d, invariant_limit=DELTA_MAX)
        z = transformer.transform(float(p))  # Cast to float for consistency
        z_values.append(z)
    z_values = np.array(z_values)

    # Write to CSV
    csv_filename = 'prime_z_data.csv'
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['prime', 'delta_n', 'z'])
        for p, d, z in zip(primes, prime_shifts, z_values):
            writer.writerow([p, f"{d:.10f}", f"{z:.10f}"])

    computation_time = time.time() - start_time

    # Summary statistics
    summary = {
        'num_primes': len(primes),
        'max_prime': primes[-1],
        'max_delta': np.max(prime_shifts),
        'max_z': np.max(z_values),
        'min_z': np.min(z_values),
        'mean_z': np.mean(z_values),
        'computation_time': computation_time,
        'csv_filename': csv_filename
    }

    if verbose:
        print(f"Wrote Z data for {summary['num_primes']} primes to {summary['csv_filename']}")
        print(f"Max prime: {summary['max_prime']}")
        print(f"Max Δₙ: {summary['max_delta']:.4f}")
        print(f"Max Z: {summary['max_z']:.2f}")
        print(f"Min Z: {summary['min_z']:.2f}")
        print(f"Mean Z: {summary['mean_z']:.2f}")
        print(f"Computation time: {summary['computation_time']:.1f}s")

    return summary

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """
    Main function for command line execution.
    """
    print(__doc__)

    # Run analysis
    try:
        summary = run_analysis(verbose=True)
        print("\n🎯 Z data export completed successfully!")
        return 0

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())