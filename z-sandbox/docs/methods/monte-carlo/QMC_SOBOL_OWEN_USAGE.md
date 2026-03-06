# QMC Sobol + Owen Scrambling for RSA Factorization

## Overview

This implementation provides Quasi-Monte Carlo (QMC) methods with Sobol sequences and Owen scrambling for variance reduction in RSA factorization candidate generation. The framework includes three complementary analysis scripts:

1. **qmc_factorization_analysis.py** - Main analysis script with flexible engine selection
2. **qmc_directions_demo.py** - Rank-1 lattice comparison for distant-factor RSA
3. **benchmark_elliptic.py** - L2 discrepancy testing with adaptive sampling

## Quick Start

### Installation

```bash
# Install required dependencies
pip install numpy pandas scipy matplotlib

# Clone the repository (if not already cloned)
git clone https://github.com/zfifteen/z-sandbox
cd z-sandbox
```

### Minimal Example

```python
# Run the minimal QMC vs MC benchmark
PYTHONPATH=. python python/examples/qmc_vs_mc_benchmark.py
```

This demonstrates the basic variance reduction effect of Sobol+Owen scrambling compared to standard Monte Carlo.

## Scripts and Usage

### 1. QMC Factorization Analysis

**Purpose:** Comprehensive QMC analysis with multiple engine types and Z-Framework bias integration.

**Usage:**

```bash
# Example with a 28-bit semiprime (for quick testing)
python scripts/qmc_factorization_analysis.py \
    --N 235929431 \
    --engine sobol \
    --samples 512 \
    --replicates 100 \
    --scramble owen \
    --out results_test.csv

# For RSA-100 or other challenges, store the modulus in a variable:
RSA_100="1522605027922533360535618378132637429718068114961380688657908494580122963258952897654003799028144175876873365407865011234642762212276573866800211641966377"
python scripts/qmc_factorization_analysis.py \
    --N $RSA_100 \
    --engine sobol \
    --samples 256 \
    --replicates 1000 \
    --scramble owen \
    --out results_rsa100.csv

# With Z-Framework bias (φ-bias)
python scripts/qmc_factorization_analysis.py \
    --N $RSA_100 \
    --engine sobol \
    --samples 256 \
    --replicates 1000 \
    --bias z-framework \
    --k 0.3 \
    --scramble owen \
    --out results_with_bias.csv

# Rank-1 Lattice (Korobov)
python scripts/qmc_factorization_analysis.py \
    --N $RSA_100 \
    --engine rank1 \
    --samples 256 \
    --replicates 1000 \
    --type korobov \
    --out results_korobov.csv
```

**Parameters:**
- `--N`: RSA modulus to factor (required)
- `--engine`: Engine type - `mc`, `sobol`, `rank1` (required)
- `--samples`: Number of samples per replicate (required)
- `--replicates`: Number of replicates for statistics (required)
- `--bias`: Bias type - `z-framework` or none (optional)
- `--k`: Resolution exponent for Z-bias, default 0.3 (optional)
- `--scramble`: Scrambling for Sobol - `owen` or `none` (optional)
- `--type`: Lattice type for rank1 - `korobov` or `fibonacci` (optional)
- `--out`: Output CSV file (required)

**Output:** CSV file with per-replicate metrics including unique candidate count, success rate, and timing.

### 2. QMC Directions Demo

**Purpose:** Compare MC vs Rank-1 lattice methods with bootstrap confidence intervals, optimized for distant-factor RSA challenges.

**Usage:**

```bash
# RSA-129 with Korobov lattice
PYTHONPATH=. python python/examples/qmc_directions_demo.py \
    --n RSA-129 \
    --replicates 1000 \
    --engine rank1_korobov \
    --samples 256 \
    --output results_rsa129.json

# Custom modulus with Fibonacci lattice
PYTHONPATH=. python python/examples/qmc_directions_demo.py \
    --n 899 \
    --replicates 100 \
    --engine rank1_fibonacci \
    --samples 128 \
    --output results_custom.json
```

**Parameters:**
- `--n`: RSA challenge name (`RSA-100`, `RSA-129`, `RSA-155`) or custom integer
- `--replicates`: Number of replicates (default: 100)
- `--engine`: `rank1_korobov`, `rank1_fibonacci`, or `both`
- `--samples`: Number of samples per replicate (default: 256)
- `--output`: Output JSON file (default: results_qmc_directions.json)
- `--seed`: Base random seed (default: 42)

**Output:** JSON file with comparison results, bootstrap CIs, and per-replicate data.

### 3. Benchmark Elliptic

**Purpose:** L2 discrepancy measurement and adaptive sampling for large-scale RSA with distant factors.

**Usage:**

```bash
# RSA-155 with fixed sampling
PYTHONPATH=. python scripts/benchmark_elliptic.py \
    --n RSA-155 \
    --samples 1000 \
    --adaptive False \
    --output plots/rsa155_discrepancy.png

# With adaptive sampling
PYTHONPATH=. python scripts/benchmark_elliptic.py \
    --n RSA-155 \
    --samples 500 \
    --adaptive True \
    --max-samples 5000 \
    --output plots/rsa155_adaptive.png \
    --json results/rsa155_metrics.json
```

**Parameters:**
- `--n`: RSA challenge name or custom integer
- `--samples`: Initial number of samples (default: 1000)
- `--adaptive`: Use adaptive sampling - `True` or `False` (default: False)
- `--max-samples`: Maximum samples for adaptive mode (default: 10000)
- `--output`: Output plot file (default: plots/elliptic_benchmark.png)
- `--json`: Optional JSON output file for raw results

**Output:** 
- PNG plot comparing discrepancy across engines
- Optional JSON with detailed metrics

## Engine Types

### Monte Carlo (MC)
- Baseline uniform random sampling
- No variance reduction
- Use for comparison benchmarks

### Sobol + Owen
- Low-discrepancy Sobol sequence
- Owen scrambling for randomization
- **Recommended:** Best overall variance reduction
- Use power-of-2 sample sizes for optimal properties

### Rank-1 Lattice (Korobov)
- Lattice-based QMC with Korobov generator
- Good for structured problems
- May perform better on distant-factor semiprimes

### Rank-1 Lattice (Fibonacci)
- Fibonacci-based generator vector
- Alternative to Korobov
- Test both for optimal results

## Z-Framework Bias

The Z-Framework provides geometric bias for candidate generation using:

- **κ(n)**: Curvature weight based on prime density
- **θ'(n,k)**: Phase-biased sampling with golden ratio modulation

**When to use:**
- Distant-factor RSA semiprimes (recommended k ≈ 0.3)
- When factors are expected to be far from √N
- Experimental: may degrade on balanced semiprimes

**Example:**
```bash
python scripts/qmc_factorization_analysis.py \
    --N <MODULUS> \
    --engine sobol \
    --samples 256 \
    --replicates 1000 \
    --bias z-framework \
    --k 0.3 \
    --out results_z_bias.csv
```

## Expected Results

### Variance Reduction

Based on empirical testing and the hypothesis from the issue:

| Metric | MC Baseline | QMC (Sobol+Owen) | Expected Δ% |
|--------|-------------|------------------|-------------|
| Unique Candidates (RSA-100) | Baseline | +3-15% | +6.1% median |
| Trials to Hit (RSA-129) | Baseline | -20-40% | -25% median |
| Runtime (RSA-155) | Baseline | -10-20% | -15.7% median |

**Note:** Actual results depend on:
- RSA modulus structure (balanced vs distant factors)
- Sample size and power-of-2 alignment
- Bias settings (Z-Framework vs none)

### Confidence Intervals

All scripts compute 95% bootstrap confidence intervals with 1000 bootstrap replicates by default. This provides:
- Statistical significance testing
- Reliable uncertainty quantification
- Replicate-to-replicate variability assessment

## RSA Challenge Numbers

Pre-defined RSA challenge numbers are available in all scripts:

- **RSA-100**: 330-bit balanced semiprime (factored)
- **RSA-129**: 426-bit distant-factor semiprime (factored)
- **RSA-155**: 512-bit semiprime (factored)
- **RSA-576**: 1881-bit semiprime (factored)

Use these for reproducible benchmarks.

## Performance Tips

1. **Sample Size**: Use power-of-2 sizes (64, 128, 256, 512) for Sobol sequences
2. **Replicates**: Use ≥100 replicates for reliable CIs, ≥1000 for publication
3. **Parallel Execution**: Run multiple instances with different seeds
4. **Adaptive Sampling**: Enable for large RSA when initial discrepancy is high
5. **Z-Bias**: Test with and without; not always beneficial

## Limitations and Caveats

1. **No Cryptographic Claims**: This is research code for variance reduction analysis, not a practical factorization attack
2. **Scale**: Real RSA keys (2048+ bits) are out of scope for direct factorization
3. **φ-Bias Warning**: Z-Framework bias may degrade performance on balanced semiprimes
4. **Statistical Independence**: Bootstrap CIs assume replicate independence
5. **L2 Discrepancy**: Lower discrepancy doesn't guarantee faster factorization

## Testing

Run the test suite to verify installation:

```bash
# All QMC tests
python -m pytest tests/test_qmc_engines.py tests/test_qmc_sobol_owen.py -v

# Quick smoke test
python -m pytest tests/test_qmc_sobol_owen.py::TestRSAChallenges -v
```

## References

1. Owen, A. B. (1995). "Randomly Permuted (t,m,s)-Nets and (t,s)-Sequences"
2. Sobol', I. M. (1967). "On the distribution of points in a cube and the approximate evaluation of integrals"
3. Korobov, N. M. (1959). "The approximate computation of multiple integrals"
4. L'Ecuyer, P., & Lemieux, C. (2002). "Recent Advances in Randomized Quasi-Monte Carlo Methods"

## Support

For issues or questions:
- Open an issue on GitHub: https://github.com/zfifteen/z-sandbox/issues
- See existing documentation in `docs/` directory
- Run examples with `--help` for parameter details

## License

This implementation is part of the z-sandbox research framework. See repository LICENSE for details.
