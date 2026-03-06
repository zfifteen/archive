# Golden Master Test Outputs

This directory contains the golden master outputs for the prime-curve density enhancement test.

## Files

### `counts_primes_vs_all.csv`
Raw bin counts comparing prime distribution vs all integer distribution:
- `bin_index`: Bin number (0 to B-1)
- `prime_counts`: Number of primes in this bin
- `all_counts`: Number of all integers in this bin  
- `enhancement_pct`: Density enhancement percentage for this bin

### `bootstrap_midbin_enhancement.csv`
Bootstrap resampling results for confidence interval calculation:
- `bootstrap_sample`: Sample number (0 to 999)
- `max_enhancement`: Maximum KDE-smoothed enhancement for this bootstrap sample

### `theta_prime_n1_20_k0.3.csv`
Sample θ′ transformation values for first 20 integers:
- `n`: Integer value (1 to 20)
- `theta_prime`: Transformed value θ′ = φ * ({n/φ} ** k)

## Test Parameters

- **N**: 100,000 (number range)
- **k**: 0.3 (curvature parameter)
- **B**: 20 (number of bins) 
- **SEED**: 0 (for reproducibility)
- **φ**: 1.618033988749895 (golden ratio)
- **Binning**: edges = np.linspace(0, φ, B+1)

## Expected Golden Master Values

- **Maximal Enhancement (robust)**: 160.634% ± 0.005
- **Bootstrap CI (95%)**:
  - 2.5%: 7.750% ± 0.005
  - 97.5%: 681.902% ± 0.005
- **Bootstrap samples**: 1000 resamples using percentile method

## Algorithm

1. Generate primes and all integers from 1 to N
2. Apply θ′ transformation: `θ′ = φ * ({n/φ} ** k)`
3. Bin values into B bins with edges from 0 to φ
4. Compute density enhancement: `(prime_density - all_density) / all_density * 100`
5. Apply robust maximum to find maximum enhancement
6. Bootstrap resample primes 1000 times for confidence interval
7. Use percentile method for CI bounds

All outputs include metadata with φ value, parameters, and generation timestamp.