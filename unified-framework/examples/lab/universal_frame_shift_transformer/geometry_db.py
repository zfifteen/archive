#!/usr/bin/env python3
"""
Universal Frame Shift Theory: Z Data Export for Integers
=======================================================

Modified implementation to compute and export Z data for every integer up to 100,000
to a CSV file, based on the discrete domain Universal Form: Z = n(Δₙ/Δₘₐₓ)

Author: [Author Name]
Date: [Date]
Version: 1.4 (Z Data Export for Integers)

Changes:
- Computes frame shifts and Z = n * Δₙ (with Δₘₐₓ implicitly 1 after clipping)
- Exports to CSV for integers 1 to 100,000
- Exits with summary statistics

Usage:
    python universal_frame_shift_integers.py

Requirements:
    numpy >= 1.19.0
"""

import math
import numpy as np
import csv
import time
from typing import Tuple

# ============================================================================
# UNIVERSAL CONSTANTS AND PARAMETERS
# ============================================================================

N_POINTS = 100000  # Upper limit for integers

# ============================================================================
# MATHEMATICAL UTILITIES
# ============================================================================

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
    Compute Z data for every integer up to 100,000 and write to CSV.

    Args:
        verbose: Whether to print detailed output

    Returns:
        Dictionary containing summary statistics
    """
    if verbose:
        print("Universal Frame Shift Theory: Z Data Export for Integers")
        print("=" * 70)
        print(f"Target integers: {N_POINTS}")
        print()

    # Precompute shared arrays
    start_time = time.time()
    n_array = np.arange(1, N_POINTS + 1)
    frame_shifts = compute_frame_shifts(n_array, N_POINTS)

    # Compute Z = n * Δₙ (Δₘₐₓ=1)
    z_values = n_array * frame_shifts

    # Write to CSV
    csv_filename = 'integer_z_data.csv'
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n', 'delta_n', 'z'])
        for p, d, z in zip(n_array, frame_shifts, z_values):
            writer.writerow([p, f"{d:.10f}", f"{z:.10f}"])

    computation_time = time.time() - start_time

    # Summary statistics
    summary = {
        'num_integers': len(n_array),
        'max_n': n_array[-1],
        'max_delta': np.max(frame_shifts),
        'max_z': np.max(z_values),
        'min_z': np.min(z_values),
        'mean_z': np.mean(z_values),
        'computation_time': computation_time,
        'csv_filename': csv_filename
    }

    if verbose:
        print(f"Wrote Z data for {summary['num_integers']} integers to {summary['csv_filename']}")
        print(f"Max n: {summary['max_n']}")
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