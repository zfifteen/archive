# Fractal Cascade Structure Falsification Test
Date: 2025-12-24 22:41:54.577079
## Summary
Analyzed 1 prime ranges
## Falsification Criteria
The hypothesis is FALSIFIED if:
1. H not in [0.6, 1.0] OR highly variable across ranges
2. Within-stratum KS pass rate < 80%
3. Null models (Cramér) successfully replicate structure

## Verdict
**FALSIFIED**
- Hurst exponent outside valid range or inconsistent
- Within-stratum lognormality not supported (<80% pass)

## Observed Results

### Range 1e6:1e7
- N gaps: 586080
- H estimate: 1.332 [0.392, 2.485]
- R²: 0.759
- Strata used: 5
- KS pass rate: 0.0%

## Null Model Comparison
- cramer (1e6:1e7): H=1.343 (ΔH=+0.011), KS=0.0%
- cascade (1e6:1e7): H=1.068 (ΔH=-0.264), KS=80.0%
