# Asymmetric Resonance Bias in Semiprime Factorization

## Hypothesis

This experiment tests the following hypothesis:

**The Z5D scoring mechanism demonstrates an emergent asymmetric enrichment bias, strongly concentrating high-ranked candidates near the larger prime factor (q > √N) while providing no guidance towards the smaller factor (p < √N).**

Additionally, we validate:

**A 106-bit QMC (Quasi-Monte Carlo) construction using Sobol sequences preserves uniform distribution without float-induced quantization biases at scales exceeding 10^600.**

## Background

In semiprime factorization (N = p×q where p < q), the square root √N falls between the two factors:
- p < √N < q
- Offset from √N to p: typically -10% to -20%
- Offset from √N to q: typically +10% to +20%

The Z5D scoring system evaluates candidates based on five mathematical dimensions. The hypothesis predicts asymmetric behavior: high scores cluster near q but not near p.

## Experimental Design

### Test Subject
- **N₁₂₇**: A 127-bit semiprime with known factors
- Generated using two 63-64 bit primes
- Allows ground-truth validation of enrichment

### Methodology
1. **Candidate Generation**: Use 106-bit QMC (Sobol sequences) to generate 1M candidates uniformly distributed around √N
2. **Scoring**: Apply Z5D scoring to all candidates
3. **Enrichment Analysis**: 
   - Classify candidates as "near p" or "near q" (±2% windows)
   - Identify high-scoring candidates (>90th percentile)
   - Compute enrichment ratios vs. baseline uniform expectation
4. **Asymmetry Measurement**: Calculate ratio of q-enrichment to p-enrichment

### Success Criteria

**Hypothesis SUPPORTED if:**
- Enrichment near q is 5x-10x higher than baseline
- Enrichment near p is ≈0x (no significant enrichment)
- Asymmetry ratio (q/p enrichment) > 5.0

**Hypothesis FALSIFIED if:**
- Enrichment is symmetric (similar for p and q)
- No significant enrichment in either region
- Asymmetry ratio < 2.0

## Implementation

### Files
- `z5d_scoring.py`: Z5D scoring mechanism and QMC candidate generation
- `run_experiment.py`: Main experimental harness
- `FINDINGS.md`: Results and analysis (created after execution)
- `README.md`: This file

### Dependencies
- Python 3.8+
- scipy (for QMC Sobol sequences)
- numpy (for statistical analysis)

### Running the Experiment

```bash
cd experiments/asymmetric_resonance_bias_test
python run_experiment.py
```

Results will be written to `FINDINGS.md`.

## References

- Prime Number Theorem: https://mathworld.wolfram.com/PrimeNumberTheorem.html
- Sobol Sequences: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.Sobol.html
