# Scale-Invariant Geometric Resonance Experiment

## Overview

This experiment was designed to definitively test the hypothesis of "Scale-Invariant Geometric Resonance in Extreme-Scale Semiprime Analysis" - a claimed discovery of emergent patterns in prime factor distributions that could enable cryptographic attacks.

**Status**: ✗ **HYPOTHESIS FALSIFIED**

See [FINDINGS.md](FINDINGS.md) for detailed results and analysis.

## Hypothesis Statement

The tested hypothesis claimed:

1. **Scale-Invariant Geometric Resonance**: Hybrid arbitrary-precision architecture reveals emergent scale-invariance in geometric resonance patterns, enabling sub-millionth percent prime prediction accuracy across 1200+ orders of magnitude.

2. **Asymmetric Distance-Dependent Enrichment**: Adaptive windowing uncovers asymmetric, distance-dependent enrichment in factor detection, preferentially signaling farther-from-square-root primes with 10× enrichment and suggesting exploitable geometric asymmetries for targeted factorization.

## Experimental Design

### Components

1. **Z5D Adapter** (`z5d_adapter.py`)
   - Arbitrary-precision nth-prime estimation using Prime Number Theorem
   - Geometric resonance score calculation
   - Supports extreme scales using mpmath

2. **C Adapter** (`src/z5d_adapter.c`)
   - Performance-optimized implementation using GMP/MPFR
   - For small-scale operations (n < 10¹⁸)
   - Optional component

3. **Adaptive Windowing** (`adversarial_test_adaptive.py`)
   - Implements adaptive search with radius = offset × 1.2
   - Tests enrichment at varying distances from √N
   - Measures asymmetric factor detection patterns

4. **Hypothesis Validation** (`validate_z5d_hypothesis.py`)
   - Comprehensive statistical testing framework
   - Kolmogorov-Smirnov and Mann-Whitney U tests
   - Scale-invariance validation across 5 orders of magnitude

5. **Experiment Runner** (`run_experiment.py`)
   - Orchestrates all test suites
   - Generates comprehensive reports
   - Saves results to JSON

### Test Suites

#### Suite 1: Core Hypothesis Validation
- **Scale Invariance Test**: Validates Z5D score consistency across 10² to 10⁶
- **Prime Prediction Accuracy**: Tests nth-prime estimation against known values
- **Asymmetric Enrichment**: Statistical comparison of balanced vs. unbalanced semiprimes

#### Suite 2: RSA Challenge Tests
- Tests adaptive windowing on known semiprimes
- Validates factor detection capability
- Measures Z5D scores and asymmetry metrics

#### Suite 3: Unbalanced Semiprime Analysis
- Analyzes enrichment patterns in deliberately asymmetric cases
- Tests claim of preferential q-factor detection

## Results Summary

All three core claims were **falsified**:

| Claim | Expected | Observed | Status |
|-------|----------|----------|--------|
| Scale Invariance (CV < 20%) | Yes | 189.5% CV | ✗ FAIL |
| Sub-millionth % accuracy | <0.0001% error | 9.65% mean error | ✗ FAIL |
| 10× q-enrichment | ratio > 10 | ratio = 0.91 | ✗ FAIL |

See [FINDINGS.md](FINDINGS.md) for complete analysis.

## Installation

### Minimal Requirements

```bash
pip install mpmath
```

### Optional (for better performance)

```bash
pip install gmpy2 scipy
```

### C Adapter (Optional)

```bash
# Requires GMP and MPFR libraries
sudo apt-get install libgmp-dev libmpfr-dev  # Debian/Ubuntu
gcc src/z5d_adapter.c -o src/z5d_adapter -lgmp -lmpfr -lm
```

## Running the Experiment

### Quick Start

```bash
python3 run_experiment.py
```

This runs all test suites and generates:
- Console output with detailed results
- `results/experiment_results.json` - Complete data
- `results/experiment_output.txt` - Console log

### Individual Components

```bash
# Test Z5D adapter
python3 z5d_adapter.py

# Run hypothesis validation only
python3 validate_z5d_hypothesis.py

# Run adversarial tests only
python3 adversarial_test_adaptive.py

# Test scaling capabilities
./reproduce_scaling.sh
```

## Architecture

### Hybrid Precision System

The experiment implements a two-tier precision system:

1. **Python/mpmath**: Arbitrary precision for extreme scales
   - Handles n up to 10¹²⁰⁰⁺
   - String-based conversions to avoid overflow
   - Configurable precision (default: 100 decimal places)

2. **C/GMP**: Performance-optimized for small scales (optional)
   - Uses uint64_t for n < 2⁶⁴
   - GMP/MPFR for larger small-scale operations
   - ~10-100× faster than Python for applicable cases

### Adaptive Windowing Algorithm

```
For offset from base_offset to max_offset:
  radius = offset × 1.2  # Adaptive sizing
  
  Search window below √N:
    p_candidates in [√N - offset - radius, √N - offset + radius]
    
  Search window above √N:
    q_candidates in [√N + offset - radius, √N + offset + radius]
    
  Calculate enrichment ratios
  Test for factors
```

### Z5D Geometric Resonance Score

The score measures deviation from expected geometric positioning:

```python
ln_p = log(p)
ln_q = log(q)
ln_n = log(N)

asymmetry = |ln_q - ln_p| / (ln_q + ln_p)
expected_geom_mean = ln_n / 2
actual_position = (ln_p + ln_q) / 2

deviation = |actual_position - expected_geom_mean| / √ln_n
z5d_score = -10 × log(1 + asymmetry) / (1 + deviation)
```

Negative scores indicate "strong resonance" according to the hypothesis.

## File Structure

```
scale_invariant_geometric_resonance/
├── README.md                          # This file
├── FINDINGS.md                        # Detailed experimental results
├── z5d_adapter.py                     # Python arbitrary-precision adapter
├── adversarial_test_adaptive.py       # Adaptive windowing implementation
├── validate_z5d_hypothesis.py         # Statistical validation framework
├── run_experiment.py                  # Main test orchestrator
├── reproduce_scaling.sh               # Scale testing script
├── src/
│   └── z5d_adapter.c                  # C performance adapter (optional)
├── results/
│   ├── experiment_results.json        # Complete test data
│   └── experiment_output.txt          # Console log
├── data/                              # Test data (generated)
└── tests/                             # Unit tests (if any)
```

## Methodology Notes

### Why This Experiment?

The hypothesis made extraordinary claims about:
- Cryptographic vulnerability assessment
- Practical attacks on RSA with unbalanced keys
- Sub-millionth percent prediction accuracy
- Exploitable geometric patterns

These claims required rigorous, unbiased testing. The experiment was designed to:
1. **Implement the described architecture faithfully**
2. **Test all claimed capabilities quantitatively**
3. **Apply proper statistical validation**
4. **Document findings transparently**

### Falsification Criteria

The experiment could falsify the hypothesis if:

1. Z5D scores vary significantly (CV > 20%) across scales → **TRIGGERED**
2. Prime prediction error exceeds 1% → **TRIGGERED**
3. No statistically significant asymmetric enrichment detected → **TRIGGERED**
4. Claimed patterns not reproducible → **PARTIALLY TRIGGERED** (limited by scale)

### Scientific Rigor

- No artificial validation or cherry-picking of results
- All test cases documented and reproducible
- Negative results reported transparently
- Limitations acknowledged clearly

## Interpretation

The falsification of this hypothesis demonstrates:

1. **Extraordinary claims require extraordinary evidence**: The claimed capabilities (defeating RSA encryption) were not supported by experimental evidence.

2. **Asymptotic formulas have known limitations**: The Prime Number Theorem approximations used cannot achieve sub-millionth percent accuracy at finite scales.

3. **Statistical validation is essential**: Many seemingly promising patterns in number theory are statistical artifacts or scaling effects.

4. **Reproducibility matters**: The experiment was designed to be fully reproducible, allowing verification of the falsification.

## Future Work

If this research direction is to be pursued:

1. **Develop rigorous mathematical foundation** before making practical claims
2. **Test on cryptographically-relevant scales** (>100-bit semiprimes)
3. **Benchmark against known factorization algorithms** (GNFS, QS)
4. **Submit to peer review** in cryptography or computational number theory

## References

- [Prime Number Theorem](https://en.wikipedia.org/wiki/Prime_number_theorem)
- [Prime-counting function](https://en.wikipedia.org/wiki/Prime-counting_function)
- [Integer factorization](https://en.wikipedia.org/wiki/Integer_factorization)
- [RSA Factoring Challenge](https://en.wikipedia.org/wiki/RSA_Factoring_Challenge)

## License

This experimental code is provided for research and educational purposes. The implementation accurately reflects the hypothesis as stated but the hypothesis itself is not validated by the results.

## Contact

For questions about the experimental design or results, refer to the issue tracker or create a new discussion.

---

**Last Updated**: 2024-12-26  
**Experiment Status**: COMPLETE  
**Hypothesis Status**: FALSIFIED
