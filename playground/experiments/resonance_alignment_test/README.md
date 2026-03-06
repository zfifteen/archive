# Scale-Invariant Resonance Alignment Falsification Test

## Quick Start

```bash
cd experiments/resonance_alignment_test
python test_hypothesis.py
```

**Results**: See `FINDINGS.md` for the complete report.  
**Verdict**: FALSIFIED

---

## Purpose

This experiment tests the following hypothesis:

**"Scale-Invariant Resonance Alignment in Extreme-Scale Prime Prediction"**

### Claims to Test

1. **Asymmetric Enrichment**: Z5D scoring shows 5x enrichment for the larger prime factor (q) in semiprimes, but no enrichment for the smaller factor (p)
2. **Logarithmic Accuracy**: Non-obvious logarithmic improvement in prediction accuracy with increasing scale, achieving sub-millionth percent relative errors at 10^1233
3. **Statistical Significance**: KS test with p < 1e-300 indicating asymmetric bias
4. **QMC Advantage**: Quasi-Monte Carlo sampling (Sobol/Halton) provides superior accuracy over standard methods
5. **Scale Invariance**: Invariant resonance patterns (k_or_phase = 0.27952859830111265) across scales

## Methodology

### Test Design

This is a **falsification experiment** - we seek to either:
- **PROVE**: Demonstrate the claims with reproducible statistical evidence
- **FALSIFY**: Show the claims do not hold under rigorous testing

### Test Cases

1. **Enrichment Test** (`test_enrichment_near_factor`)
   - Generate semiprimes N = p*q at various scales
   - Test for prediction score enrichment near p vs q
   - Compute enrichment ratios and statistical significance
   - **Expected if TRUE**: 5x enrichment near q, ~1x near p
   - **Expected if FALSE**: Similar enrichment patterns or random distribution

2. **Logarithmic Accuracy Test** (`test_logarithmic_accuracy_improvement`)
   - Test prime prediction at scales: 10^100, 10^200, 10^500, 10^1000
   - Measure relative errors at each scale
   - Fit logarithmic model to error progression
   - **Expected if TRUE**: Errors decrease logarithmically (Z-score -5.62 to -8.84)
   - **Expected if FALSE**: Errors constant or increasing with scale

3. **QMC Comparison Test** (`test_qmc_vs_standard_sampling`)
   - Compare Sobol/Halton sequences to standard Monte Carlo
   - Measure prediction accuracy for both methods
   - **Expected if TRUE**: QMC shows measurable improvement
   - **Expected if FALSE**: No significant difference or MC performs better

## Implementation Status

Following incremental coder protocol:
- ✅ Complete scaffolding created
- ⏳ Implementing functions one at a time
- ⏳ Documentation updates after each implementation
- ⏳ Final FINDINGS.md report

## Files

- `test_hypothesis.py` - Main test implementation
- `FINDINGS.md` - Results and conclusions (generated after tests run)
- `README.md` - This file

## Dependencies

**None!** This implementation uses only Python standard library (no external dependencies).

The test runs with Python 3.6+ and requires no package installation.

## Running the Test

```bash
cd experiments/resonance_alignment_test
python test_hypothesis.py
```

Results will be written to `FINDINGS.md`.

## Scientific Rigor

This test follows these principles:
1. **Reproducibility**: Fixed random seeds, documented parameters
2. **Statistical Validity**: Proper hypothesis testing with p-values
3. **Transparency**: All code and data documented
4. **Falsifiability**: Clear criteria for proving/disproving claims
5. **Conservatism**: Null hypothesis is "claims are false" - burden of proof on claims

## References

Claims sourced from problem statement:
- Validation on N₁₂₇ (1233-digit semiprime)
- Z5D scoring methodology
- QMC sampling with Sobol/Halton sequences
- PNT asymptotic expansions
- Adaptive windowing strategy (13%-300% around √N)

## Author

GitHub Copilot (Incremental Coder Agent)
Testing hypothesis for zfifteen/playground repository

## License

Same as parent repository
