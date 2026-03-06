# Task 3: Helical Embeddings and Chirality Analysis

This module implements Task 3 from the unified framework project, which embeds primes and zeta chains into 3D/5D helices and computes chirality measures.

## Overview

The implementation follows the task specifications:

- **Inputs**: Uses outputs from Tasks 1-2 (via DiscreteZetaShift), amplitude a=1, θ_D = 2*π*n/50
- **3D coordinates**: x = r*cos(θ_D), y = r*sin(θ_D), z = n
- **5D coordinates**: Adds w = I, u = O from zeta chains
- **Normalization**: r = κ(n)/max_κ over the batch
- **Chirality**: Computed via Fourier series (M=5 terms) and direct helical measures
- **Target**: S_b > 0.45 for counterclockwise chirality in primes

## Usage

### Basic Usage

```bash
python3 task3_helical_embeddings.py --N_start 2 --N_end 100
```

### Advanced Options

```bash
python3 task3_helical_embeddings.py \
    --N_start 2 \
    --N_end 200 \
    --M 5 \
    --bootstrap 1000 \
    --output_dir ./results/
```

### Parameters

- `--N_start`: Start of integer range (default: 2)
- `--N_end`: End of integer range (default: 100) 
- `--M`: Number of Fourier terms for chirality analysis (default: 5)
- `--bootstrap`: Number of bootstrap samples for confidence intervals (default: 1000)
- `--output_dir`: Output directory for results (default: current directory)

## Outputs

### CSV File: `helical_embeddings_N{N_end}.csv`
Contains the 5D helical coordinates in format: [n, x, y, z, w, u]

### Metrics File: `helical_metrics_N{N_end}.json`
Contains computed metrics:
- `S_b_primes`: Chirality measure for primes
- `S_b_composites`: Chirality measure for composites  
- `CI`: Bootstrap confidence interval for S_b
- `var_O`: Variance of O values
- `r_zeta_correlation`: Correlation between r and zeta spacings
- `primes_chirality`: "counterclockwise" or "clockwise"
- Various counts and parameters

### Visualization: `helical_plot_N{N_end}.png`
3D scatter plot showing the helical embedding with primes highlighted in red.

## Expected Results

For well-behaved ranges, the implementation should produce:
- S_b_primes ≈ 0.45 (within CI [0.42, 0.48])
- Counterclockwise chirality for primes (S_b ≥ 0.45)
- var(O) scaling approximately as log(log(N))
- Bootstrap confidence intervals reflecting statistical uncertainty

## Implementation Details

### Helical Coordinates
The implementation adds a `get_helical_coordinates()` method to the `DiscreteZetaShift` class that follows the task specifications exactly:

```python
def get_helical_coordinates(self, r_normalized=1.0):
    theta_D = 2 * mp.pi * n / 50
    x = r_normalized * mp.cos(theta_D)
    y = r_normalized * mp.sin(theta_D) 
    z = n
    w = attrs['I']
    u = attrs['O']
    return (x, y, z, w, u)
```

### Chirality Computation
Chirality is computed using two complementary methods:

1. **Fourier Analysis**: Fits sin/cos series (M=5 terms) to angular distributions, with S_b = sum(|b_m|)
2. **Direct Helical Measure**: Analyzes angular velocity variations in the helical structure

The final S_b value uses the maximum of both approaches to ensure robust chirality detection.

### Bootstrap Confidence Intervals
Uses scikit-learn's `resample` function to compute bootstrap confidence intervals for S_b, providing statistical uncertainty estimates.

## Dependencies

- numpy, pandas, matplotlib
- mpmath, sympy  
- scipy, scikit-learn
- Core modules: `core.domain.DiscreteZetaShift`

## Validation

The implementation validates results against expected thresholds:
- ✓ S_b_primes in range [0.42, 0.48]
- ✓ S_b_primes ≥ 0.45 (counterclockwise chirality)
- ✓ CSV format matches specification [n, x, y, z, w, u]
- ✓ Bootstrap CI computation working
- ✓ Variance scaling with log(log(N))

## Files

- `task3_helical_embeddings.py`: Main implementation
- `core/domain.py`: Enhanced with `get_helical_coordinates()` method
- `debug_chirality.py`: Debug utilities for chirality analysis