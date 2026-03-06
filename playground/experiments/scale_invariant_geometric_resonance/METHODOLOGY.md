# Experimental Methodology

## Hypothesis Under Test

**Claim**: Scale-Invariant Geometric Resonance in Extreme-Scale Semiprime Analysis

**Specific Claims**:
1. Emergent scale-invariance in geometric resonance patterns
2. Sub-millionth percent prime prediction accuracy across 1200+ orders of magnitude
3. Adaptive windowing reveals 10× asymmetric enrichment preferentially signaling farther-from-square-root primes
4. Practical implications for cryptographic vulnerability assessment in unbalanced keys

## Falsification Criteria

The hypothesis would be **falsified** if any of the following are observed:

1. **F1**: Z5D geometric resonance scores show coefficient of variation > 20% across scales
2. **F2**: Prime prediction mean error > 1% for n ∈ {10, 100, 1000}
3. **F3**: No statistically significant (p < 0.05) asymmetric enrichment detected
4. **F4**: Enrichment ratio (q/p) < 5 for unbalanced semiprimes

## Experimental Design

### Architecture Implementation

As specified in the hypothesis supporting data:

1. **Hybrid Arbitrary-Precision System**
   - C adapter (`src/z5d_adapter.c`) using GMP/MPFR with uint64_t for small scales
   - Python adapter (`z5d_adapter.py`) using mpmath for extreme scales
   - String-based conversions to avoid overflow (as in reference: `mpmath.nstr(n_est, …).split('.')[0]`)
   - Dynamic switching based on scale thresholds

2. **Z5D Geometric Resonance Score**
   - Formula derived from log-space geometric positioning
   - Asymmetry measure: |ln(q) - ln(p)| / (ln(q) + ln(p))
   - Scale-normalized deviation from expected geometric mean
   - Phase constant k = 0.27952859830111265 (as specified)

3. **Adaptive Windowing Algorithm**
   - Radius = offset × 1.2 (as specified in lines 130-220 reference)
   - Tests enrichment at offsets from 10% to 50% of √N
   - Separate p and q candidate counting
   - Enrichment ratio calculation

### Test Suites

#### Suite 1: Scale Invariance Validation

**Method**: Calculate Z5D scores at scales 10², 10³, 10⁴, 10⁵, 10⁶

**Validation**:
- Compute coefficient of variation (CV = σ/μ)
- **Pass threshold**: CV < 20%
- **Justification**: Scale-invariant patterns should have low relative variance

**Implementation**: `validate_z5d_hypothesis.py:test_scale_invariance()`

#### Suite 2: Prime Prediction Accuracy

**Method**: Compare nth-prime estimates to known values

**Test Cases**:
- n = 1 → known prime = 2
- n = 2 → known prime = 3
- n = 10 → known prime = 29
- n = 100 → known prime = 541
- n = 1000 → known prime = 7919

**Validation**:
- Calculate percentage error for each
- Compute mean absolute percentage error
- **Pass threshold**: Mean error < 1%
- **Justification**: Claimed "sub-millionth percent" (< 0.0001%) would easily satisfy < 1%

**Implementation**: `validate_z5d_hypothesis.py:test_prime_prediction_accuracy()`

#### Suite 3: Asymmetric Enrichment Analysis

**Method**: Compare enrichment patterns in balanced vs. unbalanced semiprimes

**Test Groups**:
- **Balanced**: p ≈ q (e.g., consecutive primes)
  - (3,5), (5,7), (11,13), (17,19), (29,31), (41,43), (59,61), (71,73)
  
- **Unbalanced**: q >> p (large asymmetry)
  - (3,97), (5,89), (7,83), (11,79), (13,73), (17,67), (19,61), (23,59)

**Validation**:
- Kolmogorov-Smirnov test for distribution difference
- Mann-Whitney U test for median difference
- Calculate mean enrichment ratio (q_enrichment / p_enrichment)
- **Pass thresholds**:
  - Statistical significance: p < 0.05
  - Enrichment ratio > 5 (relaxed from claimed 10× for robustness)

**Implementation**: `validate_z5d_hypothesis.py:test_asymmetric_enrichment_hypothesis()`

#### Suite 4: RSA Challenge Validation

**Method**: Test adaptive windowing on known semiprimes

**Test Cases**: Small semiprimes (N < 1000) with known factorizations
- Validates implementation correctness
- Measures Z5D scores
- Tests detection offsets

**Note**: Not used for hypothesis validation (too small for cryptographic claims)

**Implementation**: `adversarial_test_adaptive.py:test_rsa_challenges()`

### Statistical Methods

#### Kolmogorov-Smirnov Test
- **Purpose**: Compare two empirical distributions
- **Null hypothesis**: Distributions are identical
- **Statistic**: Maximum vertical distance between CDFs
- **Significance level**: α = 0.05

#### Mann-Whitney U Test
- **Purpose**: Test if two groups have different medians
- **Null hypothesis**: Distributions have equal medians
- **Statistic**: Rank-sum based U statistic
- **Significance level**: α = 0.05

#### Coefficient of Variation
- **Purpose**: Measure relative variability
- **Formula**: CV = σ/μ (standard deviation / mean)
- **Interpretation**: CV < 20% indicates low relative variance

### Implementation Details

#### Prime Number Theorem Approximation

As referenced in supporting data, uses PNT asymptotic expansion:

```
p_n ≈ n × (ln(n) + ln(ln(n)) - 1 + (ln(ln(n)) - 2) / ln(n))
```

With geometric resonance phase correction:

```
correction = 1 + k × ln(n) / n
p_n_corrected = p_n × correction
```

Where k = 0.27952859830111265 (constant from README.md reference)

#### Adaptive Window Search

```
for offset_pct in [0.1, 0.15, 0.2, ..., 0.5]:
    offset = √N × offset_pct
    radius = offset × 1.2  # As specified
    
    # Search below √N
    p_window = [√N - offset - radius, √N - offset + radius]
    count_p_candidates in p_window
    
    # Search above √N
    q_window = [√N + offset - radius, √N + offset + radius]
    count_q_candidates in q_window
    
    p_enrichment = p_candidates / (2 × radius)
    q_enrichment = q_candidates / (2 × radius)
    enrichment_ratio = q_enrichment / p_enrichment
```

### Data Collection

**Metrics Recorded**:
- Z5D scores at each scale
- Prime prediction errors (percentage)
- Enrichment counts and ratios
- Statistical test results (KS, MW)
- Detection offsets for successful factorizations

**Output Formats**:
- JSON: Complete structured results
- Text: Human-readable console output
- Markdown: Formatted findings report

### Quality Assurance

**Code Review**:
- Modular design with clear separation of concerns
- Comprehensive error handling
- Input validation
- Unit tests for core functions (self-tests in adapters)

**Reproducibility**:
- Fixed random seeds (none used - deterministic)
- Version-controlled code
- Documented dependencies
- Platform-independent (Python 3.x + mpmath)

**Transparency**:
- All test cases documented
- Negative results reported
- Limitations acknowledged
- Source code available

## Execution Protocol

1. **Environment Setup**
   ```bash
   pip install mpmath  # Required
   pip install gmpy2   # Optional (performance)
   pip install scipy   # Optional (better statistics)
   ```

2. **Run Complete Suite**
   ```bash
   python3 run_experiment.py
   ```

3. **Review Results**
   - Console output for immediate feedback
   - `results/experiment_results.json` for complete data
   - `FINDINGS.md` for analysis

4. **Verify Reproducibility**
   - Re-run `python3 run_experiment.py`
   - Compare output to previous run
   - Should be identical (deterministic)

## Expected Runtime

- **Complete suite**: <1 minute
- **Scale invariance**: ~5 seconds
- **Prime prediction**: <1 second
- **Asymmetric enrichment**: ~30 seconds
- **RSA challenges**: ~10 seconds

## Limitations

**Acknowledged Constraints**:
1. Could not test at claimed 10^1200 scale (computational limits)
2. Simplified statistics without scipy (KS/MW tests less precise)
3. Small sample sizes (~20 per group)
4. No tests on cryptographically-relevant sizes (>100 bits)

**Mitigation**:
- Focused on claimed properties at achievable scales
- Used simplified but valid statistical approximations
- Documented all limitations transparently
- Set conservative pass thresholds

## Validity Threats

**Internal Validity**:
- ✓ Implementation matches specification
- ✓ Test cases appropriate for claims
- ✓ Statistical methods correctly applied
- ✓ No systematic errors detected

**External Validity**:
- Limited to small-scale tests (N < 10^6 primarily)
- Cannot extrapolate to cryptographic scales
- Results may not generalize beyond test cases

**Construct Validity**:
- Z5D score captures geometric positioning
- Enrichment ratio measures asymmetry
- Statistical tests appropriate for hypotheses

**Conclusion Validity**:
- Multiple falsification criteria
- Conservative thresholds
- Robust to implementation variations

## Results Preview

See [FINDINGS.md](FINDINGS.md) for complete results.

**Summary**:
- **F1 Triggered**: CV = 189.5% >> 20% threshold
- **F2 Triggered**: Mean error = 9.65% >> 1% threshold
- **F3 Triggered**: No statistical significance detected
- **F4 Triggered**: Enrichment ratio = 0.91 << 5 threshold

**Conclusion**: Hypothesis FALSIFIED on all criteria.

---

**Last Updated**: 2024-12-26  
**Methodology Version**: 1.0
