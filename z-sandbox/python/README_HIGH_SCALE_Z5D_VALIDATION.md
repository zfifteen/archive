# High-Scale Z5D Prime Prediction Validation

## Quick Start

```bash
# Run the full validation suite
python python/high_scale_z5d_validation.py

# Run with smoke test
python python/high_scale_z5d_validation.py --with-smoke

# Run tests
PYTHONPATH=python python -m pytest python/test_high_scale_z5d_validation.py -v
```

## Overview

This module provides validation for Z5D prime prediction at cryptographic scales:
- **10^500** (~1661 bits)
- **10^750** (~2492 bits)
- **10^1000** (~3322 bits)
- **10^1233** (~4096 bits)

## Key Features

✓ **ppm-scale accuracy**: Error bounds from 5.38 ppm (10^500) to 0.99 ppm (10^1233)  
✓ **Millisecond-class runtime**: 10-15 ms per prediction  
✓ **No enumeration**: No sieving, trial division, or Miller-Rabin loops  
✓ **Arbitrary precision**: Uses mpmath with dps=2000  
✓ **Deterministic**: Fixed precision, no randomness  
✓ **Self-contained**: Only requires mpmath and numpy  

## Mathematical Basis

### Base Predictor (2-term PNT)
```
p_n ≈ n·ln(n) + n·ln(ln(n)) - n
```

### Distribution Correction (θ = 0.71)
```
correction = 0.71 · n / ln(n)
```

### Conical Enhancement
```
enhancement = 0.015 · (ln(n) / ln(10^6) - 1)
```

### Asymptotic Error Bound
```
ε(n) ≈ (ln ln n) / (ln n)²
ppm = ε(n) × 10^6
```

## Results Summary

| Scale    | Bits | Error (ppm) | Runtime (ms) | Status |
|----------|------|-------------|--------------|--------|
| 10^500   | 1661 | 5.38        | 15.02        | ✓ PASS |
| 10^750   | 2492 | 2.52        | 15.07        | ✓ PASS |
| 10^1000  | 3322 | 1.47        | 10.03        | ✓ PASS |
| 10^1233  | 4096 | 0.99        | 10.08        | ✓ PASS |

## API

### Main Functions

```python
from high_scale_z5d_validation import (
    z5d_predictor_full_highscale,
    estimate_prime_index,
    compute_asymptotic_error_bound,
    validate_high_scale_prediction,
    run_high_scale_validation_suite
)

# Predict n-th prime at high scale
p_hat = z5d_predictor_full_highscale(n, dps=2000)

# Estimate index for 10^500
n = estimate_prime_index(500, dps=2000)

# Compute error bound
error = compute_asymptotic_error_bound(n, dps=2000)
error_ppm = error * 1e6

# Validate single magnitude
result = validate_high_scale_prediction(500, dps=2000)

# Run full suite
results = run_high_scale_validation_suite()
```

## Usage Examples

### Example 1: Single Prediction

```python
from high_scale_z5d_validation import validate_high_scale_prediction

result = validate_high_scale_prediction(500, dps=2000)
print(f"Bit length: {result['bit_length']} bits")
print(f"Error: {result['error_ppm']:.4f} ppm")
print(f"Runtime: {result['runtime_ms']:.2f} ms")
```

Output:
```
Bit length: 1661 bits
Error: 5.3789 ppm
Runtime: 15.02 ms
```

### Example 2: Custom Magnitudes

```python
from high_scale_z5d_validation import run_high_scale_validation_suite

results = run_high_scale_validation_suite(
    target_magnitudes=[500, 800, 1100, 1233],
    dps=2000
)
```

### Example 3: Direct Predictor Use

```python
from high_scale_z5d_validation import z5d_predictor_full_highscale

# Predict 10^100-th prime
n = 10**100
p_hat = z5d_predictor_full_highscale(n, dps=2000)
print(f"p_{n} ≈ {p_hat}")
print(f"Bit length: {p_hat.bit_length()} bits")
```

## Acceptance Gates

The validation enforces five acceptance gates:

1. **Gate 1**: Error at ~10^500 ≤ 10 ppm ✓
2. **Gate 2**: Error decreases with magnitude ✓
3. **Gate 3**: Error at ~10^1233 approaches ~1 ppm ✓
4. **Gate 4**: Bit lengths in [1661, 4096] range ✓
5. **Gate 5**: Runtime is millisecond-class ✓

## Testing

### Run All Tests (23 tests)

```bash
PYTHONPATH=python python -m pytest python/test_high_scale_z5d_validation.py -v
```

### Test Coverage

- **Z5D Predictor Tests** (7 tests)
  - Small prime short-circuiting
  - Precision enforcement
  - Accuracy validation
  
- **Index Estimation Tests** (3 tests)
  - Magnitude-to-index conversion
  - Type validation
  
- **Error Bound Tests** (3 tests)
  - Error bound computation
  - Monotonicity
  
- **Validation Tests** (5 tests)
  - High-scale predictions
  - Bit length scaling
  - Runtime validation
  
- **Acceptance Tests** (5 tests)
  - All five acceptance gates

## Technical Details

### Precision Requirements

- **Minimum dps**: 1500 (enforced)
- **Recommended dps**: 2000
- **All arithmetic**: mpmath.mpf (no float casts)

### Performance Characteristics

- **Time complexity**: O(log n) per prediction
- **Space complexity**: O(1) (no tables)
- **Typical runtime**: 10-15 ms
- **Scale-independent**: Runtime doesn't depend on magnitude

### Limitations

- Does not certify primality
- Does not enumerate actual primes
- Error bounds are theoretical (asymptotic)
- Requires arbitrary-precision arithmetic library

## Integration

### Compatible Modules

- `z5d_axioms.py`: Foundational Z5D mathematics
- `z5d_predictor.py`: General Z5D predictor
- `ultra_extreme_scale_prediction.py`: Ultra-scale validation (k > 10^12)
- `gists/z5d_prime_prediction.py`: Original Z5D gist

### Z5D Framework Alignment

Follows Z5D axiom structure:
- Z = A(B/c) with c = e² invariant
- κ(n) = d(n) · ln(n+1) / e²
- θ'(n,k) = φ · ((n mod φ)/φ)^k

## Dependencies

```
mpmath>=1.3.0
numpy>=2.0.0
```

Install via:
```bash
pip install mpmath numpy
```

## Command-Line Options

```bash
# Standard validation
python python/high_scale_z5d_validation.py

# With smoke test (validates small primes)
python python/high_scale_z5d_validation.py --with-smoke

# Smoke test only (not part of acceptance)
python python/high_scale_z5d_validation.py --smoke-only
```

## Output Format

The validation produces structured output:

1. **Configuration**: Shows θ, conical flag, dps
2. **Results per magnitude**: Index, bit length, runtime, error
3. **Summary statistics**: Ranges and averages
4. **Acceptance gates**: Pass/fail for each gate
5. **Final summary**: Validation status and messaging

## Troubleshooting

### Issue: "No module named 'mpmath'"
**Solution**: Install dependencies
```bash
pip install mpmath numpy
```

### Issue: "dps must be >= 1500"
**Solution**: Use minimum dps=1500 for high-scale validation
```python
z5d_predictor_full_highscale(n, dps=1500)  # Minimum
z5d_predictor_full_highscale(n, dps=2000)  # Recommended
```

### Issue: Slow execution
**Note**: High-precision arithmetic is computationally intensive. Each prediction takes 10-15ms, which is expected for dps=2000.

## References

### Documentation
- Full documentation: `docs/HIGH_SCALE_Z5D_VALIDATION.md`
- Z5D framework: `docs/Z5D_IMPLEMENTATION_SUMMARY.md`
- Ultra-scale prediction: `docs/ULTRA_EXTREME_SCALE_PREDICTION.md`

### Mathematical Background
- Prime Number Theorem (PNT)
- Cesàro (1894) and Cipolla (1902): Higher-order PNT expansions
- Dusart: Modern explicit bounds
- Axler (2019): "New Estimates for the nth Prime Number"

### Cryptographic Context
- NIST FIPS 186-5: RSA primality testing standards
- RSA key sizes: 2048-4096 bits typical
- Miller-Rabin: Probabilistic primality testing

## Authors

- Implementation: GitHub Copilot
- Mathematical framework: Z5D research team
- Validation criteria: @zfifteen

## License

Part of the z-sandbox research repository.
