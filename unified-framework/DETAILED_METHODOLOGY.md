# PR-123 Scaling Integration - Detailed Methodology

## Background

This document describes the detailed methodology for integrating PR-123 curvature-threshold-k scaling laws into the geofac factorization system.

## Scaling Laws

### 1. Threshold Scaling

The threshold parameter controls the resonance detection sensitivity:

```
T(N) = 0.92 - 0.10 × log₂(bitLen/30)
```

**Rationale**: As bit length increases, the threshold must decrease to maintain sensitivity to weaker resonance signals.

**Implementation**: `ScaleAdaptiveParams.calculateThreshold()`

### 2. k-shift Scaling

The k-shift parameter adjusts the resonance frequency offset:

```
k(N) = 0.35 + 0.0302 × ln(bitLen/30)
```

**Rationale**: Larger numbers require higher k values to properly capture resonance patterns.

**Implementation**: `ScaleAdaptiveParams.calculateKShift()`

### 3. Sample Count Scaling

The number of samples needed for accurate resonance estimation:

```
samples(N) = round(30000 × (bitLen/60))
minimum: 5000
```

**Rationale**: Linear scaling with bit length ensures adequate sampling density.

**Implementation**: `ScaleAdaptiveParams.calculateSampleCount()`

### 4. Precision Scaling

Mathematical precision required for computations:

```
precision = 4 × bitLen + 200
```

**Rationale**: Higher precision needed for larger numbers to maintain numerical stability.

**Implementation**: `PrecisionUtil.calculatePrecision()`

## Architecture

### Component Overview

```
Main.java
  └─> FactorizerService.java
       ├─> ScaleAdaptiveParams.java (computes T, k, samples)
       ├─> PrecisionUtil.java (computes precision)
       ├─> curvature.json (κ estimates)
       └─> fit.json (phase drift)
```

### Data Flow

1. **Initialization**
   - Load `curvature.json` and `fit.json`
   - Parse scaling parameters

2. **Parameter Computation**
   - Calculate bit length of target number
   - Compute T(N), k(N), samples(N) using formulas
   - Lookup κ_estimated and phase_drift from JSON

3. **Factorization**
   - Apply resonance-based algorithm with computed parameters
   - Use appropriate precision context

4. **Validation**
   - Verify p × q = N
   - Compare against expected factors

## Scaling Data Files

### curvature.json

Contains measured curvature values for different bit lengths:

```json
{
  "measurements": [
    {"bitLength": 30, "curvature": 0.82, "kappa_estimated": 0.35},
    {"bitLength": 60, "curvature": 0.75, "kappa_estimated": 0.38},
    {"bitLength": 127, "curvature": 0.62, "kappa_estimated": 0.44},
    ...
  ]
}
```

Used to estimate κ for interpolated bit lengths.

### fit.json

Contains fitted scaling formulas and phase drift measurements:

```json
{
  "threshold": {
    "formula": "T(N) = 0.92 - 0.10 * log2(bitLen/30)",
    ...
  },
  "phase_drift": [
    {"bitLength": 127, "drift": 0.08},
    ...
  ]
}
```

Used for phase correction in resonance calculations.

## Reproducibility

All parameters are logged for each run:

```
Bit length: 127
Threshold (T): 0.7118
k-shift: 0.3936
Sample count: 63500
κ_estimated: 0.44
Phase drift: 0.08
Precision: 708
```

This allows exact reproduction of any factorization attempt.

## Validation Methodology

### Gate-127 Validation

1. **Input**: N = 137524771864208156028430259349934309717
2. **Expected**: p = 10508623501177419659, q = 13086849276577416863
3. **Verification**:
   - Compute p × q
   - Compare result with N
   - Verify factors match expected values

### Success Criteria

- ✓ Product matches original number
- ✓ Factors match expected values
- ✓ All parameters logged correctly
- ✓ Execution completes without errors

## Performance Characteristics

### Time Complexity

- Parameter computation: O(1)
- JSON loading: O(n) where n = file size
- Factorization: O(f(bitLen, samples)) - depends on resonance algorithm

### Space Complexity

- Scaling data: O(1) - fixed size
- BigInteger precision: O(bitLen)

## Extension Points

### Adding New Bit Lengths

1. Run experiments to measure curvature and phase drift
2. Update `curvature.json` with new measurements
3. Update `fit.json` with new phase drift values
4. Scaling formulas automatically adapt

### Parameter Tuning

Use `sweep_resonance_params.sh` to search parameter space:

```bash
bash scripts/sweep_resonance_params.sh \
  --N <number> \
  --k-min <k_min> \
  --k-max <k_max> \
  --T-min <T_min> \
  --T-max <T_max>
```

## References

- PR-123: https://github.com/zfifteen/geofac/pull/123
- Resonance recalibration experiments
- Gate-127 challenge specification
