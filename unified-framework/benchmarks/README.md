# Z Framework Benchmark Suite

Comprehensive benchmarking and validation tools for the Z Framework's Stadlmann integration, conical flow models, and geodesic density enhancements.

## Overview

This benchmark suite validates the claims and performance characteristics documented in the Z Framework daily summary reports, including:

- **Stadlmann Distribution Level Integration** (Issue #625)
- **Conical Flow Models** (Issue #631)
- **Geodesic Density Enhancement**
- **Bootstrap Confidence Intervals**
- **Statistical Validation**

## Benchmark Scripts

### 1. Stadlmann Extended Validation

**File:** `stadlmann_extended_validation.py`

Tests higher distribution levels (θ > 0.525) and validates density boost claims.

**Features:**
- Distribution levels from θ = 0.525 to θ = 0.560
- Bootstrap confidence intervals (1,000 resamples)
- Density boost validation (claimed: 1-2% with CI [0.8%, 2.2%])
- Scale dependence analysis (N = 10^4 to 10^6)
- Z_5D prediction comparison across levels

**Usage:**
```bash
python benchmarks/stadlmann_extended_validation.py
```

**Expected Output:**
- Distribution level analysis table
- Z_5D prediction comparisons
- Scale dependence statistics
- Summary of validation results

**Claims Tested:**
- θ ≈ 0.525 (Stadlmann 2023) provides optimal balance
- 1-2% density boost with CI [0.8%, 2.2%] for k ≥ 10^5
- <0.01% error for k ≥ 10^5

### 2. Geodesic Density Enhancement Benchmark

**File:** `geodesic_density_benchmark.py`

Validates geodesic-informed prime density enhancement using φ-residue transformations.

**Features:**
- Tests θ'(n, k) = φ · ((n mod φ)/φ)^k transformation
- Bootstrap confidence intervals for density enhancement
- Kappa (k*) optimization analysis (validates k* ≈ 0.3)
- Scale dependence testing (N = 10^4 to 10^6)
- Kolmogorov-Smirnov test for asymmetry

**Usage:**
```bash
python benchmarks/geodesic_density_benchmark.py
```

**Expected Output:**
- Enhancement statistics with 95% CI
- Kappa optimization results
- Scale dependence analysis
- KS test for φ-residue distribution

**Claims Tested:**
- 15-20% geodesic-driven prime density improvement
- CI [14.6%, 15.4%] for enhancement
- k* ≈ 0.3 as optimal exponent
- KS p ≈ 0 for asymmetry in clustering

### 3. Conical Flow Speedup Benchmark

**File:** `conical_flow_speedup_benchmark.py`

Tests performance and accuracy of conical flow models.

**Features:**
- Speedup comparison (baseline vs conical-optimized)
- Model accuracy validation with various sample sizes
- Density enhancement factor analysis
- Evaporation time scaling tests

**Usage:**
```bash
python benchmarks/conical_flow_speedup_benchmark.py
```

**Expected Output:**
- Speedup statistics across different scales
- Model accuracy with pass rates
- Density enhancement factors
- Evaporation time validation

**Claims Tested:**
- 93-100x speedups via conical flow models
- 100% pass rate with <1e-6 mean error
- Constant-rate evaporation model (T = h0/k)
- ~0.2-0.5% density boost from Stadlmann level

## Running All Benchmarks

To run all benchmarks sequentially:

```bash
cd benchmarks
python stadlmann_extended_validation.py
python geodesic_density_benchmark.py
python conical_flow_speedup_benchmark.py
```

Or create a simple runner script:

```bash
#!/bin/bash
for script in stadlmann_extended_validation.py \
              geodesic_density_benchmark.py \
              conical_flow_speedup_benchmark.py; do
    echo "Running $script..."
    python benchmarks/$script
    echo ""
done
```

## Requirements

All benchmarks require:
- Python 3.8+
- numpy
- sympy
- scipy
- mpmath
- matplotlib (optional, for visualization)

Install via:
```bash
pip install -e .
```

## Benchmark Configuration

Key parameters can be adjusted in each script:

- **Bootstrap resamples:** Default 1,000 (configurable via `n_bootstrap` parameter)
- **Prime sample size:** Defaults to N = 10^6 (configurable via `max_n` parameter)
- **Iterations:** Default 5-10 per test (configurable via `n_iterations` parameter)

## Understanding Results

### Passing Criteria

1. **Distribution Level Tests:**
   - Enhancement should fall within claimed range [0.8%, 2.2%]
   - Confidence intervals should overlap with claims

2. **Geodesic Enhancement:**
   - Mean enhancement in range [15%, 20%]
   - CI should overlap with [14.6%, 15.4%]
   - Optimal k* near 0.3

3. **Conical Flow:**
   - Pass rate ≥ 95%
   - Mean error < 1e-6
   - T/h₀ = 1/k for evaporation time

### Interpretation Notes

- **Speedup claims:** May vary significantly based on hardware, implementation, and measurement methodology
- **Statistical significance:** Bootstrap CIs provide robust estimates but are sample-dependent
- **Scale effects:** Some enhancements may only appear at larger scales (k ≥ 10^5)

## References

- **Stadlmann 2023:** arXiv:2212.10867 - Distribution level θ ≈ 0.5253 for smooth moduli
- **Issue #625:** Stadlmann 0.525 Level Integration
- **Issue #631:** Conical Flow Model - Constant-Rate Self-Similar Flows
- **Daily Summary:** Progress reports and empirical validations

## Contributing

To add new benchmarks:

1. Create a new Python file in `benchmarks/`
2. Follow the existing structure (header, imports, test functions, main)
3. Include bootstrap confidence intervals where applicable
4. Document claims being tested
5. Add usage instructions to this README

## Troubleshooting

**SymPy not available:**
- Install via: `pip install sympy`
- Some benchmarks require SymPy for prime generation

**Slow execution:**
- Reduce `n_bootstrap` parameter (e.g., from 1000 to 100)
- Reduce `max_n` for prime generation (e.g., from 10^6 to 10^5)
- Use smaller sample sizes

**Memory issues:**
- Process primes in batches
- Use iterators instead of lists where possible
- Reduce sample sizes

## License

MIT License - See repository LICENSE file for details.
