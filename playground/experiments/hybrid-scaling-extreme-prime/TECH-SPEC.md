# TECH-SPEC: Hybrid Scaling Architecture in Extreme Prime Prediction

## 1. Objective

Design and execute a definitive experiment to test the hypothesis that a dual-adapter hybrid scaling architecture enables:
1. Emergent asymptotic convergence in prime prediction across 1200+ orders of magnitude
2. Asymmetric resonance detection favoring larger semiprime factors (q) by ~5x
3. Statistical significance with p < 1e-300 non-randomness
4. Extreme scale accuracy (<0.0001% deviation) at 10^1233

## 2. High-Level Design

### Experimental Framework

**Dual Adapter System:**
- **C Adapter**: GMP/MPFR library, fixed 256-bit precision, for scales ≤50
- **Python Adapter**: gmpy2/mpmath, dynamic precision `dps = max(100, int(bits * 0.4) + 200)`, for scales >50
- **Automatic Switching**: Based on scale threshold in `reproduce_scaling.sh`

**Test Components:**
1. Adapter validation and switching logic
2. Convergence testing across 10^20 to 10^127
3. Extreme scale accuracy at 10^1233
4. Resonance asymmetry detection on semiprimes
5. Statistical significance testing

### Null Hypothesis

If claims are false:
- No logarithmic convergence pattern in relative errors
- No asymmetric resonance between p and q factors
- Errors behave randomly (no statistical significance)
- Extreme scale accuracy fails to meet <0.0001% threshold

## 3. Data and Inputs

### Prime Prediction

**Method**: Prime Number Theorem with asymptotic corrections
```
p_n ≈ n * (ln(n) + ln(ln(n)) - 1 + (ln(ln(n)) - 2)/ln(n))
```

**Test Ranges:**
- Convergence test: 10^20 to 10^127 (30 points)
- Statistical test: 10^20 to 10^100 (50 points)
- Extreme test: 10^1233

### Semiprime Factorization

**Test Cases:**
- Small validation: N = {143, 221, 323, 437, 667, 899}
- Factors: (p, q) pairs where p < q

**Resonance Parameters:**
- Window size: 500-1000 around factor location
- Phase modulation: φ (golden ratio) and e (Euler's number)

## 4. Algorithms

### 4.1 Z5D Score Computation

**Implementation** (`z5d_adapter.py:90-120`):
```python
def compute_z5d_score(predicted, actual):
    relative_error = abs((predicted - actual) / actual)
    return log10(relative_error)
```

### 4.2 Geometric Amplitude

**Implementation** (`tools/run_geofac_peaks_mod.py:220-250`):
```python
def compute_geometric_amplitude(k):
    ln_k = log(k)
    phi_term = cos(ln_k * PHI)
    e_term = cos(ln_k * E)
    return phi_term * e_term
```

Where:
- PHI = (1 + √5) / 2 ≈ 1.618
- E = 2.718...

### 4.3 Convergence Testing

**Method**: Linear regression on log-log scale
```python
log_errors = log10(relative_errors)
log_scales = log10(scales)
slope, intercept, r², p_value = linregress(log_scales, log_errors)
```

**Success Criteria**: slope < 0, p < 0.01, R² > 0.95

### 4.4 Resonance Asymmetry

**Method**: Compare signal strength in windows around p and q
```python
p_signal = mean(|amplitudes_around_p|)
q_signal = mean(|amplitudes_around_q|)
enrichment_ratio = q_signal / p_signal
```

**Success Criteria**: enrichment_ratio > 3.0 (conservative threshold for 5x claim)

## 5. Metrics and Analysis

### 5.1 Convergence Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Slope | β from log(error) ~ β·log(scale) | Should be negative |
| R² | Coefficient of determination | Should be > 0.95 |
| p-value | Significance of regression | Should be < 0.01 |

### 5.2 Accuracy Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Relative Error | |predicted - actual| / |actual| | - |
| % Deviation | relative_error × 100 | < 0.0001% |

### 5.3 Asymmetry Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Enrichment Ratio | q_signal / p_signal | > 5.0 |
| Asymmetry Count | # cases with ratio > 3 | Majority |

### 5.4 Statistical Metrics

| Test | Statistic | Target |
|------|-----------|--------|
| Runs Test | p-value | < 1e-300 (claimed) |
| ACF(1) | Autocorrelation | High (>0.8) |
| Anderson-Darling | Test statistic | Reject randomness |

## 6. Falsification Criteria

### Evidence FALSIFYING the hypothesis:

**Convergence:**
✗ Slope ≥ 0 or p-value > 0.05
✗ R² < 0.90
✗ No systematic error decrease with scale

**Extreme Accuracy:**
✗ Deviation at 10^1233 > 0.0001%

**Asymmetry:**
✗ Mean enrichment ratio < 2.0
✗ < 30% of cases show > 3x enrichment
✗ Signal strengths approximately equal

**Statistical Significance:**
✗ p-value > 1e-10 (significantly larger than claimed 1e-300)
✗ ACF(1) < 0.5

### Evidence SUPPORTING the hypothesis:

✓ Slope < -1, R² > 0.99, p < 1e-10
✓ Extreme accuracy < 0.0001% deviation
✓ Mean enrichment > 4.0, majority > 3x
✓ p-value < 1e-300

## 7. Expected Outputs

### 7.1 Quantitative Results

**Table 1: Convergence Analysis**
- Slope, R², p-value
- Error trends across scales
- Extreme scale accuracy

**Table 2: Resonance Asymmetry**
- Enrichment ratios per semiprime
- Mean/median enrichment
- Asymmetry confirmation rate

**Table 3: Statistical Tests**
- Runs test p-value
- ACF values
- Anderson-Darling statistic

### 7.2 Artifacts

**Files:**
- `FINDINGS.md`: Lead with conclusion, followed by technical evidence
- `experiment_results.json`: Raw numerical results
- `experiment_output.txt`: Full console output
- `README.md`: Usage instructions
- `TECH-SPEC.md`: This document

**Code:**
- `z5d_adapter.py`: Python adapter implementation
- `src/z5d_adapter.c`: C adapter implementation
- `tools/run_geofac_peaks_mod.py`: Resonance detection
- `z5d_validation_n127.py`: Validation experiments
- `run_experiment.py`: Main experiment runner
- `reproduce_scaling.sh`: Benchmark automation

## 8. Implementation Notes

### 8.1 Dependencies

**Python Libraries:**
```
numpy>=1.20.0
scipy>=1.7.0
mpmath>=1.2.0  # Optional, for higher precision
gmpy2>=2.1.0   # Optional, for GMP bindings
```

**C Libraries:**
```
libgmp-dev     # GNU Multiple Precision
libmpfr-dev    # Multiple Precision Floating-Point
gcc            # Compiler
```

### 8.2 Precision Management

**C Adapter (scales ≤50):**
- Fixed 256-bit precision
- Sufficient for 10^50 range
- Faster execution

**Python Adapter (scales >50):**
- Dynamic precision based on scale
- Formula: `dps = max(100, int(bits * 0.4) + 200)`
- Prevents overflow at extreme scales

### 8.3 Algorithm Complexity

**PNT Approximation:** O(log n) for ln and ln(ln) computations
**Resonance Scan:** O(window_size) per factor
**Convergence Test:** O(n_points × log n)
**Total Runtime:** Expected < 1 second for full suite

## 9. Validation Checks

### Pre-Execution

- [ ] All dependencies installed
- [ ] Test data ranges defined
- [ ] Success/failure criteria pre-registered
- [ ] Random seeds set (if applicable)

### Post-Execution

- [ ] All tests completed without errors
- [ ] Results saved in JSON format
- [ ] FINDINGS.md created with conclusion first
- [ ] Code is reproducible
- [ ] Artifacts committed to repository

## 10. Potential Pitfalls

### 10.1 Numerical Precision

**Risk:** Overflow or underflow at extreme scales
**Mitigation:** Use dynamic precision, string conversion for very large numbers

### 10.2 Small Sample Size

**Risk:** Resonance test limited to small semiprimes
**Mitigation:** Acknowledge limitation; hypothesis claims apply to 256-426 bit range

### 10.3 Statistical Power

**Risk:** Cannot achieve p < 1e-300 with finite samples
**Mitigation:** Test for high significance (p < 1e-10) and document discrepancy

### 10.4 Compilation Dependencies

**Risk:** C adapter requires GMP/MPFR which may not be available
**Mitigation:** Make C adapter optional; Python adapter is primary implementation

## 11. Interpretation Guidelines

### Fully Confirmed

All four claims supported:
→ Dual adapter architecture is validated
→ Convergence is exceptional
→ Asymmetry is real
→ Statistical significance is extreme
→ **Hypothesis CONFIRMED**

### Partially Confirmed

Some claims supported, others falsified:
→ Document which aspects work and which don't
→ Provide alternative explanations
→ **Hypothesis PARTIALLY FALSIFIED**

### Fully Falsified

All or most claims fail:
→ No convergence or poor fit
→ No asymmetry detected
→ Low statistical significance
→ **Hypothesis FALSIFIED**

## 12. References

### Mathematical Background

1. **Prime Number Theorem**: Wolfram MathWorld
   - https://mathworld.wolfram.com/PrimeNumberTheorem.html
   - Error bounds: O(n / (ln n)²)
   - Asymptotic corrections included

2. **GNFS (Comparison)**: Wikipedia
   - https://en.wikipedia.org/wiki/General_number_field_sieve
   - State-of-art factorization method
   - No known resonance-based shortcuts

### Implementation References

1. **GMP Library**: GNU Multiple Precision Arithmetic
2. **MPFR Library**: Multiple Precision Floating-Point Reliable
3. **mpmath**: Python library for arbitrary-precision arithmetic

## 13. Timeline

**Completed**: 2025-12-26
**Total Time**: < 1 hour for implementation + testing
**Runtime**: 0.01 seconds for full experiment suite

## 14. Conclusion Format

### FINDINGS.md Structure

```markdown
# FINDINGS

## CONCLUSION
[Lead with the verdict: CONFIRMED / PARTIALLY FALSIFIED / FALSIFIED]
[Summarize key findings]

## TECHNICAL SUPPORTING EVIDENCE
[Detailed analysis with tables, numbers, references]

### 1. Dual Adapter System
[Test results]

### 2. Convergent Accuracy
[Convergence analysis, extreme scale test]

### 3. Resonance Asymmetry
[Enrichment ratios, asymmetry detection]

### 4. Statistical Significance
[p-values, autocorrelation, tests]

## METHODOLOGY
[Experimental design, limitations, robustness]

## INTERPRETATION
[What this means, implications, future work]

## REFERENCES
[Citations, links, code locations]
```

---

**Document Version**: 1.0
**Last Updated**: 2025-12-26
**Experiment Status**: COMPLETE
