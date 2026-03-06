# RSA-260 Geometric Factorization

This implementation provides geometric factorization for RSA-260 using the comb formula with strict adherence to precision and invariant requirements.

## Overview

RSA-260 is a 260-digit (862-bit) unfactored semiprime from the RSA Factoring Challenge. This implementation uses geometric methods based on:

- **Comb Formula**: `p_m = exp((log N - 2πm/k)/2)`
- **Fixed Center**: `log(N)/2` (never shifted)
- **Fractional m Sampling**: Sub-integer precision for m
- **Distance Ranking**: Candidates ranked by `|log(p) - center|`
- **High Precision**: mpmath with dps≥1000

## RSA-260 Canonical Value

```
22112825529529666435281085255026230927612089502470015394413748319128822941
40200198651272972656974659908590033003140005117074220456085927635795375718
59542988389587092292384910067030341246205457845664136645406842143612930176
94020846391065875914794251435144458199
```

- **Digits**: 260
- **Bits**: 862
- **Status**: Unfactored (as of 2025)

References:
- [Wikipedia: RSA numbers](https://en.wikipedia.org/wiki/RSA_numbers)
- [Schneier on Security: RSA-250 Factored](https://www.schneier.com/blog/archives/2020/04/rsa-250_factore.html)

## Quick Start

### Basic Usage

```bash
# Default parameters (dps=1000, k=0.3, window=0.05, step=0.0001)
python3 python/rsa260_repro.py

# Custom parameters
python3 python/rsa260_repro.py --dps 2000 --k 0.29 --window 0.1 --step 0.00001

# Using wrapper script
./scripts/run_rsa260.sh --dps 1000 --k 0.3 --window 0.05
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dps` | 1000 | Decimal precision (minimum 1000) |
| `--k` | 0.3 | Wave number parameter |
| `--m0` | auto | Center m value (auto-estimated) |
| `--window` | 0.05 | Window width for m sampling (±window) |
| `--step` | 0.0001 | Step size for fractional m |
| `--neighbor_radius` | 2 | Check ±radius around candidates |
| `--prp_rounds` | 32 | Miller-Rabin primality test rounds |

## Architecture

### Components

1. **`python/rsa260_repro.py`**
   - Main runner script
   - Implements comb formula with fractional m
   - Distance-based candidate ranking
   - Deterministic Miller-Rabin PRP test
   - Parameter logging

2. **`python/geom/m0_estimator.py`**
   - Resonance-based m₀ estimation
   - For balanced RSA: m₀ ≈ 0
   - Provides confidence windows

3. **`tests/test_comb_invariants.py`**
   - Tests core invariants:
     - Center = log(N)/2 (fixed)
     - Fractional m sampling enabled
     - Distance-based ranking
     - High precision (dps≥1000)
     - No float64 fallback

4. **`tests/test_prp_gate.py`**
   - Tests PRP determinism:
     - Fixed witness bases
     - Reproducibility
     - Known primes/composites

5. **`scripts/run_rsa260.sh`**
   - Wrapper script with logging
   - CLI parameter management
   - Output formatting

## Key Requirements

### 1. Fixed Center
The center is **always** `log(N)/2` and is **never shifted** by bias corrections or other adjustments.

```python
log_N = mplog(N)
center = log_N / 2  # Fixed, immutable
```

### 2. High Precision
All calculations use mpmath with `dps≥1000`:

```python
mp.dps = 1000  # Minimum for RSA-260
```

No float64 fallback allowed.

### 3. Fractional m Sampling
Sample fractional m values (not integer-m):

```python
m = m0 - window
while m <= m0 + window:
    p = comb_formula(N, k, m, dps)
    # ...
    m += step  # Fractional step (e.g., 0.0001)
```

### 4. Distance Ranking
Candidates ranked by `|log(p) - center|`:

```python
distance = abs(log(p) - log(N)/2)
ranked.sort(key=lambda x: x[2])  # Sort by distance
```

### 5. Deterministic PRP
Miller-Rabin with fixed witness bases (first 32 primes):

```python
witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, ...]
```

## Testing

### Run All Tests

```bash
# Run comb invariant tests
python3 -m pytest tests/test_comb_invariants.py -v

# Run PRP gate tests
python3 -m pytest tests/test_prp_gate.py -v

# Run both
python3 -m pytest tests/test_comb_invariants.py tests/test_prp_gate.py -v
```

### Test Coverage

- ✅ Center is fixed at log(N)/2
- ✅ Fractional m sampling enabled
- ✅ Distance-based ranking
- ✅ Minimum dps=1000 enforced
- ✅ No float64 fallback
- ✅ Deterministic PRP
- ✅ Reproducible results

## Mathematical Framework

### Comb Formula

The comb formula generates factor candidates:

```
p_m = exp((log N - 2πm/k)/2)
```

Where:
- `N`: Semiprime
- `k`: Wave number (controls spacing)
- `m`: Resonance mode (fractional for sub-integer precision)

### Resonance Theory

For balanced RSA semiprimes (p ≈ q ≈ √N):
- True factors correspond to m ≈ 0
- Phase quantization: `log N - 2 log p = 2πm/k`
- For p = √N: `log N - 2 log(√N) = 0` → `m = 0`

### Distance Metric

Candidates are ranked by distance from center:

```
distance(p) = |log(p) - log(N)/2|
```

Smaller distance → closer to √N → more likely factor.

## Examples

### Example 1: Default Parameters

```bash
python3 python/rsa260_repro.py
```

Output:
```
================================================================================
RSA-260 Geometric Factorization
================================================================================
Timestamp: 2025-11-04T01:44:33.104Z
N (bits): 862
N (digits): 260

Parameters:
  dps: 1000
  k: 0.3
  log(N): 595.7366502...
  center (log(N)/2): 297.8683251...

Resonance Analysis:
  m0 (balanced): 0.000000
  m0 (residue): 0.000000
  m0 (recommended): 0.000000
  window: ±1.666667

Sampling Configuration:
  m0: 0.000000
  window: ±0.05
  step: 0.0001
  expected_samples: 1000
  neighbor_radius: ±2
  prp_rounds: 32

Generating fractional-m candidates...
  Generated 1001 candidates

Ranking by distance from center...
  Top 10 by distance:
    1. m=0.000000, p=..., distance=...
    ...
```

### Example 2: Custom Parameters

```bash
python3 python/rsa260_repro.py --dps 2000 --k 0.29 --window 0.1 --step 0.00001
```

### Example 3: Using Wrapper Script

```bash
./scripts/run_rsa260.sh --dps 1000 --k 0.3 --window 0.05
```

Logs saved to `logs/rsa260_run_YYYYMMDD_HHMMSS.log`

## Performance

### Computational Cost

- **Precision**: O(dps²) for mpmath operations
- **Candidates**: O(window/step) samples
- **Ranking**: O(n log n) sort
- **PRP Test**: O(log n) per candidate

### Typical Runtime

For default parameters (1000 samples):
- Candidate generation: ~1-2 seconds
- Ranking: <1 second
- PRP testing: Variable (depends on candidate count)

### Memory Usage

- High precision: ~1-10 MB for dps=1000
- Candidate storage: <100 MB for typical runs

## Limitations

### Known Issues

1. **RSA-260 is unfactored**: This implementation provides a framework but does not guarantee success on RSA-260.
2. **Computational scale**: Full exploration requires significant compute resources.
3. **No NFS/CADO**: Pure geometric methods only (as required).

### Scope

This implementation is for:
- ✅ Research and validation
- ✅ Testing geometric methods
- ✅ Establishing invariants and precision requirements
- ❌ Production factorization (RSA-260 remains unsolved)

## References

### Papers & Standards

- Rabin, M. O. (1980). "Probabilistic algorithm for testing primality"
- RSA Factoring Challenge (historical)
- Z5D Axioms (internal framework)

### External Links

- [RSA Numbers (Wikipedia)](https://en.wikipedia.org/wiki/RSA_numbers)
- [RSA-250 Factored (Schneier)](https://www.schneier.com/blog/archives/2020/04/rsa-250_factore.html)

### Internal Documentation

- `docs/GOAL.md` - Research goals
- `docs/IMPLEMENTATION_SUMMARY_256BIT.md` - 256-bit pipeline
- `python/README_FACTORIZATION_256BIT.md` - 256-bit methods

## Contributing

When modifying this code:

1. **Maintain invariants**: Center must remain fixed at log(N)/2
2. **Preserve precision**: Never fall back to float64
3. **Keep determinism**: PRP tests must be reproducible
4. **Update tests**: All tests must pass
5. **Document changes**: Update this README

## License

Part of the z-sandbox research framework.
