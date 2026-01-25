# Gap Anomaly Detector

## Overview

A monitoring system that detects anomalous prime gaps—gaps that significantly violate the expected lognormal+ACF model at a given scale.

## What It Does

Monitors a stream of primes and flags gaps that are statistical outliers:
- Computes expected gap distribution (lognormal parameters) for current scale
- Tracks recent gap history for ACF baseline
- Identifies gaps that deviate significantly from both lognormal and ACF expectations
- Outputs anomaly score and diagnostic information

## Why This Is Novel

**Couldn't exist before the lognormal+ACF baseline.**

Without the discovery:
- No rigorous statistical model for "normal" gap behavior
- No way to define "anomalous" beyond ad-hoc heuristics (e.g., "gaps bigger than 2×log(p)")
- No incorporation of gap memory/correlation

With lognormal+ACF model:
- **Statistical null hypothesis**: Gaps should be lognormal with predictable autocorrelation
- **Deviation detection**: Gaps that violate this model are quantifiably anomalous
- **Multi-dimensional anomaly**: Can detect gaps that are:
  - Too large/small relative to lognormal distribution
  - Too correlated/uncorrelated relative to ACF pattern
  - Appearing in wrong sequence given recent history

## Use Cases

### Pseudorandom Number Generator Testing
Test PRNGs that generate "prime-like" sequences. If the PRNG produces gaps that are too regular or too random (violating lognormal+ACF), flag it as weak.

**Example:**  
PRNG claims to generate primes near 10^9  
Detector: Checks if gaps match lognormal(μ=23.03, σ²=...) and ACF pattern for that scale  
Result: PRNG gaps too uniform → flagged as non-prime-like

### Prime Database Quality Assurance
Verify integrity of prime databases (e.g., primegap.db, OEIS sequences). Detect corruption or insertion errors by finding gaps that don't match expected distribution.

### Maximal Gap Research
Automatically identify unusually large gaps (maximal gaps) without manual inspection. The detector's anomaly score highlights gaps worth investigating.

### Cryptographic Audit
Analyze prime generation in cryptographic libraries. If a library produces primes whose gaps are "too structured" or "too anomalous," investigate for potential backdoors or biases.

## Key Innovation

**This is the first statistically rigorous gap anomaly detector.**

Previous approaches:
- Ad-hoc rules: "Gap > k×log(p) is large"
- No memory model: Treat each gap independently
- No distributional baseline: No model for what's "normal"

This approach:
- Lognormal baseline: Probabilistic model for gap sizes
- ACF baseline: Model for gap correlation
- Multi-dimensional scoring: Anomaly in size, sequence, or correlation

## Status

**Concept stage** — awaiting implementation after core `prime_gap` library is complete.

## Technical Requirements

Depends on:
- `prime_gap.gap_analysis` — for lognormal parameter estimation and ACF computation
- `prime_gap.lognormal_prefilter` — for gap normalization
- Statistical testing library (scipy or equivalent for hypothesis tests)
- Streaming prime input (online mode) or batch mode for database verification

## Performance Baseline

Detector must:
- Correctly flag known maximal gaps (e.g., first occurrence primes for Bertrand primes)
- Have low false positive rate (< 1% for random prime sequences)
- Detect synthetic anomalies (injected gaps with wrong distribution) with > 95% accuracy

## Anomaly Scoring

Proposed multi-dimensional score:

1. **Lognormal deviation**: Z-score of gap size relative to lognormal(μ(scale), σ²(scale))
2. **ACF deviation**: How much does this gap violate predicted ACF pattern?
3. **Sequence anomaly**: Does gap sequence (last K gaps) have unusual joint probability?

Combined anomaly score: `A = w1×Z_lognormal + w2×Z_ACF + w3×Z_sequence`

Threshold: Flag if `A > threshold` (e.g., 3.0 for 99.7% confidence)

## Implementation Strategy

1. **Baseline model**: Pre-compute lognormal parameters and ACF patterns for scale ranges
2. **Online detector**: Stream primes, maintain gap buffer, compute anomaly score per gap
3. **Flagging**: Output gaps exceeding threshold with diagnostic info
4. **Calibration**: Tune weights (w1, w2, w3) and threshold on known datasets

## Limitations

- **Scale-dependent**: Parameters must adapt as prime magnitude changes
- **Startup period**: Requires K initial gaps to establish ACF baseline
- **False positives**: Legitimate rare gaps (e.g., first maximal gap at a scale) will trigger detector

## Future Enhancements

- **Adaptive thresholds**: Automatically adjust threshold based on observed false positive rate
- **Gap clustering**: Detect clusters of anomalous gaps (indicative of systematic corruption)
- **Visualization**: Real-time plot of gap stream with anomalies highlighted
- **Integration with databases**: Continuous monitoring mode for live prime generation
