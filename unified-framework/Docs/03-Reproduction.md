# Reproduction

## Canonical φ Benchmark

**Exact command with seed:**
```bash
python src/core/geodesic_mapping.py --n 1000000 --bins 20 --k 0.3 --bootstrap 10000 --seed 42
```

**Expected outputs:**
- Best-bin uplift (%) with 95% CI
- Permutation p-value vs randomized labels
- Enhancement statistics in local finite window

## nth-Prime Z_5D Benchmark

**Calibrated predictor test:**
```bash
python src/core/z_5d_enhanced.py --k 100000 --validate-accuracy
```

**Expected accuracy:**
- k=10^5: <0.01% relative error
- Prediction: ~1,299,709 (true value: 1,299,709)

## TC-INST-01 Geodesic Validation

**Complete validation suite:**
```bash
python validate_tc_inst_01.py --seed 42 --precision 50
```

**Expected results:**
- z₁ = 51.549
- Trimmed variance = 0.113
- 9 tests, 100% pass rate

## High-Scale Validation

**Ultra-extreme scale predictions:**
```bash
python scripts/ultra_extreme_scale_prediction.py --output results/ultra_scale.csv
```

**Parameters:**
- Range: 10^6 to 10^16
- 10 exponential bands
- High-precision arithmetic (dps=50)