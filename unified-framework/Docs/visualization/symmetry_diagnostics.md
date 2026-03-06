# Symmetry Diagnostics Plots

This module implements Figure X as described in issue #403: **Symmetry diagnostics between the logarithmic integral (Li) and Z₅D predictors for π(k)**.

## Overview

The symmetry diagnostics plot consists of four complementary panels that quantify and visualize the quasi-symmetric relationship between the classical Li approximation and the Z₅D geodesic-corrected predictor across k from 10² to 10¹⁰.

## Generated Files

### Main Implementation
- `symmetry_diagnostics_figure_x.png` - Actual implementation using Z5D predictor
- `symmetry_diagnostics_analysis_report.txt` - Statistical analysis of the actual results

### Theoretical Demonstration  
- `theoretical_symmetry_diagnostics_figure_x.png` - Theoretical demonstration showing expected behavior
- `theoretical_symmetry_analysis_report.txt` - Analysis of theoretical expectations

## Panel Descriptions

### Panel A: Collapse Test
- **Plot**: Difference in relative error (ε_LI - ε_Z5D) vs phase term φ/B
- **Expected**: Near-perfect line with r² > 0.95
- **Purpose**: Confirms that the missing φ/B term in Li is the dominant symmetry driver

### Panel B: Pivot Symmetry
- **Plot**: Relative errors for Li (red) and Z5D (green) crossing at pivot point
- **Expected**: Crossing at k₀ ≈ e^(e²) ≈ 1620 where φ = 0
- **Purpose**: Shows role reversal in error behavior around the pivot

### Panel C: Order-Gap Check
- **Plot**: Scaled errors showing decay orders (ε_LI × ln k vs ε_Z5D × ln² k)  
- **Expected**: Flattened curves revealing 1/ln vs 1/ln² decay orders
- **Purpose**: Demonstrates Z5D's higher-order cancellation yielding sub-0.01% errors for k ≥ 10⁵

### Panel D: Affine Alignment
- **Plot**: Scatter of ε_LI vs ε_Z5D with regression line
- **Expected**: Slope ≈ 1.8, intercept ≈ 0.02, tight affine relationship
- **Purpose**: Shows explicit formula consistency π(k) ≈ Li(k) - ∑_ρ Li(k^ρ)/|ρ|

## Parameters

- **Z5D parameters**: c = -0.00247, k* = 0.04449
- **Range**: k ∈ [10², 10¹⁰]  
- **Bootstrap validation**: N = 1000 resamples
- **Expected correlation**: r ≈ 0.93 (empirical, pending independent validation) (p < 10⁻¹⁰)

## Usage

### Standalone Generation
```bash
# Generate actual implementation plot
python src/visualization/symmetry_diagnostics.py

# Generate theoretical demonstration plot  
python src/visualization/theoretical_symmetry_diagnostics.py
```

### Integrated Generation
```bash
# Generate all plots including symmetry diagnostics
python tests/generate_all_plots.py
```

## Integration

The symmetry diagnostics plots are integrated into the comprehensive plot generation suite and will be automatically generated as part of the full visualization pipeline.

## Theoretical Foundation

Under the Riemann Hypothesis:
- Li's bias is O(1/ln k) 
- Z5D's bias is O(1/ln² k)
- Phase term φ/B acts as deterministic "symmetry coordinate"
- Affine relationship modulated by Riemann zeta zeros

This demonstrates the Z-Framework's geodesic phase-bit interpretation and provides empirical validation of the theoretical symmetry predictions.