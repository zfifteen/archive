#!/usr/bin/env python3
"""
Geomagnetic Jerk Visualization Script
=====================================

Author: Dionisio Lopez
Date: February 1, 2026
Inspired by: S0 News video on geomagnetic jerks and the 2026 paper by
             Khanyile et al. on Southern African geomagnetic field modeling

Purpose:
--------
This script demonstrates what a geomagnetic jerk IS by showing how it appears
in the magnetic field and its derivatives. A geomagnetic jerk is a sudden change
in the secular variation (first time derivative) of Earth's magnetic field,
appearing as a V-shaped kink in SV plots and a step/spike in secular acceleration
(second derivative) plots.

Scientific Background:
----------------------
Geomagnetic jerks are rapid changes in Earth's core dynamics that occur on
annual to decadal timescales. They provide insights into fluid motion in the
outer core. Recent research shows jerks are becoming more frequent, with Earth
entering a "constant state of jerkiness" - multiple events detected in
2019-2020, 2021, and 2022-2023.

Output:
-------
- A 3-panel matplotlib figure saved as 'geomagnetic_jerk_visualization.png'
- Panel (a): Magnetic field B(t) - smooth curve, jerk barely visible
- Panel (b): Secular variation dB/dt - V-SHAPE clearly shows the jerk
- Panel (c): Secular acceleration d2B/dt2 - step/spike at jerk time

Dependencies:
-------------
- numpy >= 1.21.0
- matplotlib >= 3.4.0
- scipy >= 1.7.0

Usage:
------
    python geomagnetic_jerk_visualizer.py

References:
-----------
1. Khanyile, S.L., Nahayo, E., et al. (2026). Modelling earth's magnetic field
   over southern Africa between 2014 and 2023. Physics of the Earth and
   Planetary Interiors, 372, 107504.

2. Khanyile, S.L. & Nahayo, E. (2024). Geomagnetic jerks observed in
   geomagnetic observatory data over southern Africa between 2017 and 2023.
   South African Journal of Geology, 127(1), 131-136.

3. S0 News (2026). Solar Flares Surge to Life, Unstable Earth.
   https://www.youtube.com/watch?v=Cp3ZR4RntnE

License:
--------
MIT License - Free to use, modify, and distribute with attribution.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from typing import Tuple

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

RANDOM_SEED = 42  # For reproducibility
START_YEAR = 2010
END_YEAR = 2025
NUM_POINTS = 500
JERK_YEAR = 2021  # The simulated jerk occurs in 2021

# Secular variation parameters (nT/year)
SV_BEFORE_JERK = 30.0  # Rate of change before jerk
SV_AFTER_JERK = -10.0  # Rate of change after jerk

# Visualization parameters
FIGURE_WIDTH = 10  # inches
FIGURE_HEIGHT = 8  # inches
DPI = 150
OUTPUT_FILENAME = 'geomagnetic_jerk_visualization.png'


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def generate_synthetic_field(
    time_array: np.ndarray,
    jerk_time: float,
    sv_before: float,
    sv_after: float,
    noise_level: float = 2.0,
    smoothing_sigma: float = 3.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate synthetic geomagnetic field data with a jerk event.

    This function creates a realistic-looking magnetic field time series
    by constructing a piecewise-linear secular variation (first derivative)
    with a discontinuity at the jerk time, then integrating to get the field.

    Parameters:
    -----------
    time_array : np.ndarray
        Array of time values (years)
    jerk_time : float
        Year when the jerk occurs
    sv_before : float
        Secular variation rate before jerk (nT/year)
    sv_after : float
        Secular variation rate after jerk (nT/year)
    noise_level : float, optional
        Standard deviation of Gaussian noise (default: 2.0)
    smoothing_sigma : float, optional
        Sigma parameter for Gaussian smoothing (default: 3.0)

    Returns:
    --------
    B : np.ndarray
        Magnetic field values (nT)
    secular_variation : np.ndarray
        First derivative dB/dt (nT/year)
    secular_acceleration : np.ndarray
        Second derivative d2B/dt2 (nT/year^2)
    """
    # Create piecewise secular variation with V-shape at jerk
    secular_variation = np.where(
        time_array < jerk_time,
        sv_before + 5 * np.sin(0.5 * (time_array - START_YEAR)),
        sv_after + 5 * np.sin(0.5 * (time_array - START_YEAR))
    )

    # Add Gaussian noise to simulate measurement uncertainty
    secular_variation += np.random.normal(0, noise_level, len(time_array))

    # Apply Gaussian smoothing
    secular_variation = gaussian_filter1d(secular_variation, sigma=smoothing_sigma)

    # Integrate secular variation to get magnetic field B(t)
    dt = time_array[1] - time_array[0]
    B = np.cumsum(secular_variation) * dt
    B = B - B[0] + 25000  # Offset to realistic values (~25000 nT)

    # Compute secular acceleration (second derivative)
    secular_acceleration = np.gradient(secular_variation, dt)

    return B, secular_variation, secular_acceleration


def create_jerk_visualization(
    time_array: np.ndarray,
    B: np.ndarray,
    secular_variation: np.ndarray,
    secular_acceleration: np.ndarray,
    jerk_time: float,
    output_filename: str = OUTPUT_FILENAME
) -> None:
    """
    Create and save a 3-panel visualization of a geomagnetic jerk.

    Parameters:
    -----------
    time_array : np.ndarray
        Array of time values (years)
    B : np.ndarray
        Magnetic field values (nT)
    secular_variation : np.ndarray
        First derivative dB/dt (nT/year)
    secular_acceleration : np.ndarray
        Second derivative d2B/dt2 (nT/year^2)
    jerk_time : float
        Year when jerk occurs (for annotation)
    output_filename : str, optional
        Output PNG filename
    """
    fig, axes = plt.subplots(3, 1, figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), sharex=True)
    fig.suptitle('What is a Geomagnetic Jerk?\nVisualized through Derivatives',
                 fontsize=14, fontweight='bold')

    # Panel (a): Magnetic Field B(t)
    axes[0].plot(time_array, B, 'b-', linewidth=1.5)
    axes[0].axvline(x=jerk_time, color='red', linestyle='--', alpha=0.7,
                    label=f'Jerk ({int(jerk_time)})')
    axes[0].set_ylabel('B (nT)', fontsize=11, fontweight='bold')
    axes[0].set_title('(a) Magnetic Field - Jerk barely visible', fontsize=10, loc='left')
    axes[0].legend(loc='upper right', framealpha=0.9)
    axes[0].grid(True, alpha=0.3)

    # Panel (b): Secular Variation (V-SHAPE)
    axes[1].plot(time_array, secular_variation, 'g-', linewidth=1.5)
    axes[1].axvline(x=jerk_time, color='red', linestyle='--', alpha=0.7)
    axes[1].axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    axes[1].set_ylabel('dB/dt (nT/yr)', fontsize=11, fontweight='bold')
    axes[1].set_title('(b) Secular Variation (1st derivative) - V-SHAPE reveals the jerk!',
                      fontsize=10, loc='left')
    jerk_index = np.argmin(np.abs(time_array - jerk_time))
    axes[1].annotate('V-shape\n(JERK)', xy=(jerk_time, secular_variation[jerk_index]),
                     xytext=(jerk_time + 2, 20), fontsize=10, color='red', fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color='red', lw=2))
    axes[1].grid(True, alpha=0.3)

    # Panel (c): Secular Acceleration
    axes[2].plot(time_array, secular_acceleration, 'purple', linewidth=1.5)
    axes[2].axvline(x=jerk_time, color='red', linestyle='--', alpha=0.7)
    axes[2].axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    axes[2].set_ylabel('d\u00b2B/dt\u00b2 (nT/yr\u00b2)', fontsize=11, fontweight='bold')
    axes[2].set_xlabel('Year', fontsize=11, fontweight='bold')
    axes[2].set_title('(c) Secular Acceleration (2nd derivative) - Step/spike at jerk',
                      fontsize=10, loc='left')
    axes[2].grid(True, alpha=0.3)

    # Shade the jerk region
    for ax in axes:
        ax.axvspan(jerk_time - 0.5, jerk_time + 0.5, alpha=0.2, color='red', zorder=0)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=DPI, bbox_inches='tight')
    print(f'Figure saved as {output_filename}')
    plt.show()


def main():
    """Main execution function."""
    print('=' * 70)
    print('Geomagnetic Jerk Visualizer')
    print('=' * 70)
    print(f'Time range: {START_YEAR}-{END_YEAR}')
    print(f'Jerk year: {JERK_YEAR}')
    print(f'Output: {OUTPUT_FILENAME}')
    print('=' * 70)

    np.random.seed(RANDOM_SEED)
    time_array = np.linspace(START_YEAR, END_YEAR, NUM_POINTS)

    print('\n[1/2] Generating synthetic geomagnetic field data...')
    B, secular_variation, secular_acceleration = generate_synthetic_field(
        time_array=time_array,
        jerk_time=JERK_YEAR,
        sv_before=SV_BEFORE_JERK,
        sv_after=SV_AFTER_JERK
    )

    print('[2/2] Creating visualization...')
    create_jerk_visualization(
        time_array=time_array,
        B=B,
        secular_variation=secular_variation,
        secular_acceleration=secular_acceleration,
        jerk_time=JERK_YEAR
    )

    print('\nVisualization complete!')


if __name__ == '__main__':
    main()
