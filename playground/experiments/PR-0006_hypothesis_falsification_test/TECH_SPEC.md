# Technical Specification: Hypothesis Falsification Test

## Objective

Design and execute a definitive test to prove or falsify the hypothesis that the zfifteen/playground repository demonstrates:

1. An AI-augmented scientific falsification pipeline for prime gap modeling
2. A reversed hierarchy discovery mechanism where bottom-up analysis outperforms top-down

## Experimental Protocol

### Phase 1: Falsification Pipeline Validation

**Input:** Prime gaps from multiple ranges
**Process:**
1. Generate gaps using high-precision prime generation
2. Apply iterative falsification tests
3. Measure detection rate of distribution deviations
4. Compare against baseline null hypothesis (exponential)

**Metrics:**
- True positive rate (correctly identifying non-exponential)
- False positive rate (falsely rejecting exponential)
- Convergence iterations required

### Phase 2: Distribution Comparison

**Null Hypothesis:** Prime gaps follow exponential distribution
**Alternative:** Prime gaps follow lognormal distribution

**Tests:**
- Kolmogorov-Smirnov test (overall fit)
- Anderson-Darling test (tail emphasis)
- Likelihood ratio test
- Information criteria: AIC, BIC

**Falsification Criterion:** 
If ΔBIC(exp - lognorm) < 10 in >50% of trials, lognormal hypothesis is rejected.

### Phase 3: Fractal Cascade Analysis

**Claim to Test:** Gaps exhibit multiplicative cascade structure

**Method:**
1. Stratify gaps into magnitude quantiles
2. Fit lognormal to each stratum
3. Measure variance scaling: σₖ vs μₖ
4. Estimate Hurst exponent H via log-log regression

**Falsification Criterion:**
- If H varies by >0.2 across ranges, cascade rejected
- If H not in range [0.7, 0.9], cascade rejected

### Phase 4: Bottom-Up vs Top-Down Comparison

**Bottom-Up (Hypothesis):**
- Start from raw gap data
- Compute empirical moments
- Detect patterns without assumptions
- Test reversed hierarchy (higher moments converge faster)

**Top-Down (Baseline):**
- Assume Cramér model (exponential gaps)
- Fit parameters
- Test goodness of fit
- Iterate if fit fails

**Comparison Metrics:**
- False positive count per approach
- Iterations to convergence
- Accuracy of final distribution identification

**Falsification Criterion:**
If bottom-up does NOT show statistically significant improvement (p < 0.05) in false positive reduction, the claim is rejected.

## Data Requirements

### Prime Ranges
- Range 1: 10^6 to 10^7 (small scale)
- Range 2: 10^7 to 10^8 (medium scale)
- Optional: 10^8 to 10^9 (large scale, if time permits)

### Trials
- Minimum 10 independent trials per range
- Fixed random seed for reproducibility
- Train/test splits if model fitting required

## Success Criteria

The hypothesis is **SUPPORTED** if ALL of the following hold:

1. ✓ Lognormal outperforms exponential (ΔBIC ≥ 10) in ≥70% of trials
2. ✓ Fractal cascade detected with stable H ∈ [0.7, 0.9]
3. ✓ Bottom-up shows ≥30% reduction in false positives vs top-down (p < 0.05)
4. ✓ Reversed hierarchy pattern from PR-0005 replicates in ≥2 ranges

The hypothesis is **FALSIFIED** if ANY of the following hold:

1. ✗ Exponential fits as well or better than lognormal in ≥50% of trials
2. ✗ No stable Hurst exponent found (variance >0.2 or outside [0.7, 0.9])
3. ✗ Bottom-up shows no significant advantage over top-down
4. ✗ Reversed hierarchy does not replicate

## Output Requirements

### FINDINGS.md Structure

```markdown
# FINDINGS: Hypothesis Falsification Test

## CONCLUSION
[Lead with clear verdict: SUPPORTED or FALSIFIED]
[State confidence level and key evidence]

## TECHNICAL EVIDENCE

### 1. Distribution Comparison
[Table of BIC values, p-values across trials]

### 2. Fractal Cascade Analysis
[Hurst exponent estimates, variance scaling plots]

### 3. Bottom-Up vs Top-Down
[False positive rates, convergence metrics]

### 4. Reversed Hierarchy Replication
[Moment convergence data, comparison with PR-0005]

## METHODOLOGY
[Brief description of experimental protocol]

## RAW DATA
[Link to detailed results JSON]
```

## Implementation Notes

- Follow incremental coder protocol (one function at a time)
- All code self-contained in experiment folder
- No modifications to parent experiments
- Use existing prime generation utilities if available
- Document all assumptions and limitations
