# RSA-260 Run Log Template

This document provides a template for logging RSA-260 factorization runs with complete parameter tracking and reproducibility information.

## Run Metadata

**Run ID**: `rsa260_run_YYYYMMDD_HHMMSS`  
**Timestamp**: ISO 8601 format  
**Host**: System identifier  
**Commit**: Git commit hash  

## Environment

```
Python version: 3.x.x
mpmath version: x.x.x
System: Linux/macOS/Windows
CPU: [CPU info]
Memory: [RAM info]
```

## Parameters

### Core Parameters
- **N**: RSA-260 canonical value (260 digits, 862 bits)
- **dps**: Decimal precision (≥1000)
- **k**: Wave number parameter
- **center**: log(N)/2 (fixed, immutable)

### Sampling Configuration
- **m0**: Center m value (auto-estimated or specified)
- **window**: Window width (±window from m0)
- **step**: Step size for fractional m
- **expected_samples**: 2 × window / step

### Testing Configuration
- **neighbor_radius**: ±radius for candidate testing
- **prp_rounds**: Miller-Rabin rounds
- **witnesses**: First 32 primes [2, 3, 5, ..., 131]

## Resonance Analysis

```
log(N): [value with 10+ decimals]
center: [log(N)/2 with 10+ decimals]
m0 (balanced): [value]
m0 (residue): [value]
m0 (recommended): [value]
window: ±[value]
```

## Results

### Candidate Generation
- **Generated**: N candidates
- **Time**: X.XX seconds

### Ranking
- **Method**: Distance from center |log(p) - center|
- **Top-N candidates**: List with (m, p, distance)

### Testing
- **Candidates tested**: N
- **PRP passes**: N
- **Exact divisions checked**: N
- **Factors found**: 0 or 2 (p, q)

## Top Candidates

```
Rank | m-value   | Candidate (first 40 digits)                | Distance
-----|-----------|-------------------------------------------|-------------
1    | 0.000000  | 4702427620870912079506137874887325273... | 8.870e-131
2    | 0.001000  | 4751930069600484582180649483359805035... | 1.047e-02
3    | -0.001000 | 4653440855746597256441175506098082905... | 1.047e-02
...
```

## Performance

- **Total runtime**: X.XX seconds
- **Memory peak**: X.XX MB
- **Samples per second**: N/sec
- **Candidate generation**: X.XX sec
- **Ranking**: X.XX sec
- **PRP testing**: X.XX sec

## Success Criteria

- [ ] Center verified at log(N)/2
- [ ] Fractional m sampling confirmed
- [ ] Distance-based ranking applied
- [ ] High precision maintained (dps≥1000)
- [ ] Deterministic PRP used
- [ ] All candidates tested with ±neighbor_radius
- [ ] Exact division checked for PRP passes

## Result

**Status**: [SUCCESS / NO FACTOR FOUND]

### If SUCCESS:
```
p = [full p value]
q = [full q value]
Verification: p × q = N ✓
Discovery: m = [m_value], offset = [offset]
```

### If NO FACTOR FOUND:
```
Tested: N candidates
Elapsed: X.XX seconds
Next steps: [Adjust k/window/step, try different m0, etc.]
```

## Reproducibility

### Command
```bash
python3 python/rsa260_repro.py \
  --dps 1000 \
  --k 0.3 \
  --m0 0.0 \
  --window 0.05 \
  --step 0.0001 \
  --neighbor_radius 2 \
  --prp_rounds 32
```

### Verification
To reproduce this run:
1. Clone repository at commit [hash]
2. Install dependencies: `pip install mpmath sympy`
3. Run command above
4. Compare output with this log

## Notes

[Any observations, anomalies, or insights from this run]

## Next Actions

[Planned parameter adjustments or follow-up runs]

---

## Example: Sample Run Log

### Run Metadata
- **Run ID**: rsa260_run_20251104_015247
- **Timestamp**: 2025-11-04T01:52:47.703965Z
- **Host**: github-actions-runner
- **Commit**: 0475d10

### Parameters
- **dps**: 1000
- **k**: 0.3
- **m0**: 0.0 (auto-estimated)
- **window**: ±0.001
- **step**: 0.001
- **neighbor_radius**: ±2
- **prp_rounds**: 32

### Resonance Analysis
```
log(N): 597.1631117734
center: 298.5815558867
m0 (balanced): 0.000000
m0 (residue): 0.000000
m0 (recommended): 0.000000
window: ±1.754386
```

### Results
- **Generated**: 3 candidates
- **Tested**: 15 candidates (with neighbor offsets)
- **Status**: NO FACTOR FOUND
- **Time**: 0.02 seconds

### Top Candidates
```
1. m=0.000000, distance=8.870e-131
2. m=-0.001000, distance=1.047e-02
3. m=0.001000, distance=1.047e-02
```

### Notes
Quick test run with minimal window to verify implementation.
All invariants satisfied, ready for larger-scale runs.
