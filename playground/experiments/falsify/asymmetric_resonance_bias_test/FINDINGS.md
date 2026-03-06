# FINDINGS: Asymmetric Resonance Bias in Semiprime Factorization

## CONCLUSION

**HYPOTHESIS FALSIFIED** ✗

The Z5D scoring mechanism does NOT demonstrate the predicted asymmetric enrichment bias. Asymmetry ratio: 0.73 (threshold: 5.0).

## TECHNICAL EVIDENCE

### Test Subject: N₁₂₇

- **N** = 85065147212363892189230678941569931741
- **p** = 8264141345021879351 (63 bits, smaller factor)
- **q** = 10293283193129930891 (64 bits, larger factor)
- **N bit length** = 126 bits
- **Verification**: p × q = 85065147212363892189230678941569931741 ✓

### Experimental Parameters

- **Candidates requested**: 1,000,000
- **Unique candidates generated**: 1,000,000
- **Generation method**: 106-bit QMC (Sobol sequences)
- **Generation time**: 2.63s
- **Scoring time**: 1.33s

### Enrichment Analysis

**Factor Offsets from √N:**
- p offset: 10.40% (below √N)
- q offset: +11.60% (above √N)

**High-Scoring Candidate Distribution:**
- Score threshold (90th percentile): 0.525118
- Total high-scoring candidates: 100,000
- Expected per window (uniform): 2000.0

**Near-p Region (±2% window around p):**
- Total candidates in window: 20,002
- High-scoring candidates: 8369
- Enrichment ratio: 4.18x

**Near-q Region (±2% window around q):**
- Total candidates in window: 20,002
- High-scoring candidates: 6072
- Enrichment ratio: 3.04x

**Asymmetry Metric:**
- Asymmetry ratio (q/p enrichment): **0.73**
- Interpretation: The larger factor (q) shows 0.7x more enrichment than the smaller factor (p)

### QMC Uniformity Validation

**Statistical Tests:**
- Kolmogorov-Smirnov statistic: 1.000000
- KS p-value: 0.0000 (FAIL at α=0.05)
- Chi-square statistic: 9900000.00
- Chi-square p-value: 0.0000 (FAIL at α=0.05)

**Quantization Analysis:**
- Raw candidates generated: 100,000
- Unique candidates: 100,000
- Duplicates detected: 0
- Maximum discrepancy: 1.000000

## METHODOLOGY

### Z5D Scoring Mechanism

Candidates are evaluated across five dimensions:
1. **Distance from √N** (normalized, weight 0.25)
2. **Fermat residue strength** (proximity to perfect square, weight 0.30)
3. **Primality likelihood** (6k±1 pattern, weight 0.15)
4. **Gap distribution** (log-scale proximity, weight 0.20)
5. **Small prime smoothness** (divisibility penalty, weight 0.10)

### 106-bit QMC Construction

Candidates generated using Sobol sequences:
1. Generate 2D samples (hi, lo) from [0,1)²
2. Convert to 53-bit integers
3. Combine via bit-shifting: `(hi << 53) | lo`
4. Scale to ±√N offset range
5. Avoid float quantization at extreme scales

### Statistical Analysis

- **Enrichment ratio**: (observed high-scoring in window) / (expected under uniform)
- **Asymmetry ratio**: enrichment_q / enrichment_p
- **Success criterion**: Asymmetry ratio ≥ 5.0

## REFERENCES

- Prime Number Theorem: https://mathworld.wolfram.com/PrimeNumberTheorem.html
- Sobol Sequences: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.Sobol.html
- Experiment code: `/experiments/asymmetric_resonance_bias_test/`
