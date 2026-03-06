# Quick Reference Guide

## Running the Experiment

### Complete Test Suite
```bash
python3 run_experiment.py
```

### Individual Tests
```bash
# Z5D Adapter self-test
python3 z5d_adapter.py

# Core hypothesis validation
python3 validate_z5d_hypothesis.py

# Adversarial testing
python3 adversarial_test_adaptive.py

# Scaling tests
./reproduce_scaling.sh
```

## Key Results

### Hypothesis: FALSIFIED

Three core claims tested and all failed:

1. **Scale Invariance**: ✗ CV = 189.5% (threshold: <20%)
2. **Prime Prediction**: ✗ Mean error = 9.65% (claim: <0.0001%)
3. **Asymmetric Enrichment**: ✗ Ratio = 0.91 (claim: >10)

### Test Statistics

| Metric | Value |
|--------|-------|
| Total test suites | 3 |
| Test cases | 20+ |
| Scales tested | 10² to 10⁶ |
| Semiprimes factored | 12/12 (small N only) |
| Overall status | HYPOTHESIS NOT VALIDATED |

## File Guide

| File | Purpose |
|------|---------|
| `FINDINGS.md` | **READ FIRST** - Complete results and analysis |
| `README.md` | Experiment overview and methodology |
| `run_experiment.py` | Main test orchestrator |
| `z5d_adapter.py` | Arbitrary-precision prime operations |
| `validate_z5d_hypothesis.py` | Statistical validation framework |
| `adversarial_test_adaptive.py` | Adaptive windowing tests |
| `reproduce_scaling.sh` | Scale testing script |
| `results/experiment_results.json` | Complete test data |

## Interpretation

The experiment was designed to fairly test extraordinary claims about:
- Cryptographic vulnerability assessment
- Exploitable geometric patterns in semiprimes
- Sub-millionth percent accuracy in prime prediction

**None of these claims were validated by the experimental evidence.**

The successful factorization of small semiprimes (N < 1000) does not support the broader claims about cryptographic applications or extreme-scale patterns.

## Dependencies

### Required
- Python 3.x
- mpmath: `pip install mpmath`

### Optional
- gmpy2: `pip install gmpy2` (faster arithmetic)
- scipy: `pip install scipy` (better statistics)
- GCC + GMP/MPFR (for C adapter)

## Timeline

- **Design**: Implemented hybrid architecture per hypothesis description
- **Execution**: All tests completed in <1 minute
- **Analysis**: Falsification detected across all validation criteria
- **Documentation**: Comprehensive findings with conclusion-first format

## Next Steps

If pursuing this research:
1. Develop rigorous mathematical proofs
2. Test at cryptographically-relevant scales (>100 bits)
3. Benchmark against known algorithms
4. Seek peer review in cryptography/number theory

---

For full details, see [FINDINGS.md](FINDINGS.md)
