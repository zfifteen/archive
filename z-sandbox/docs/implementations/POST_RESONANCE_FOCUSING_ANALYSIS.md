# Post-Resonance Focusing Transform: Analysis and Results

## Executive Summary

This document analyzes the post-resonance focusing transform implementation for RSA-2048 factorization and explains why the transform does not meet the quantitative acceptance criteria (shrink_ratio < 1e-200, abs_distance_after ≤ 10^6).

**Key Finding**: The focusing transform achieves zero improvement (shrink_ratio ≈ 1.0) because the available spectral and geometric signals (Green's function amplitude and κ-curvature) both peak at √N, not at the true factors p and q.

## Problem Statement

The Green's function resonance pipeline produces seeds that are ~4% away from the true 1024-bit factors:
- Seeds center at √N with high precision
- True factors p and q are offset from √N by ~±4%
- At 2048-bit scale, 4% relative error = ~10^306 absolute distance
- The ±1000 refinement window cannot bridge this gap

The goal was to implement a deterministic focusing transform that collapses the ~10^306 gap to ≤10^6 (ideally ≤1000) using only analytic/geometric/spectral signals.

## Implementation

The focusing transform (python/post_resonance_focusing.py) implements:

1. **Multi-scale Spectral Scan**: Evaluates candidate factors at multiple log-space offsets from √N (-5% to +5%)
2. **Dual-k Phase Residual Analysis**: Compares resonance at k₁ and k₂ = k₁(1+ε) to detect systematic bias
3. **Dirichlet Kernel Peak-Centering**: Applies harmonic sharpening for sub-integer precision
4. **κ-weighted Scoring**: Combines Green's amplitude with Z5D curvature
5. **Iterative Phase Alignment**: Fine-tunes estimates to minimize phase residual

All operations are deterministic, use only public information about N, and avoid classical factorization methods.

## Empirical Results

### Benchmark Output (2048-bit RSA semiprime)

```
N bit length:         2048
Focusing time:        2.36 ms
Best shrink ratio:    1.000000e+00
Distance after:       5.278907e+306
Distance after (log10): 306.72

Acceptance Criteria:
  Shrink ratio < 1e-200: ✗ (1.000e+00)
  Distance after ≤ 10^6: ✗ (5.279e+306)
  Stretch goal (≤1000): ✗ (5.279e+306)
```

**Result**: The focusing transform produces no measurable improvement.

## Root Cause Analysis

### Signal Analysis at 2048-bit Scale

For the test semiprime N = p × q:
- log(√N) ≈ 709.532
- log(p_true) ≈ 709.493
- log(q_true) ≈ 709.571
- Δlog = log(√N) - log(p) ≈ 0.0385

### Green's Function Amplitude

Evaluation of |G(log p')| = |cos(k(log N - 2 log p'))| at various offsets from √N:

| Offset from √N | log(p') | Amplitude |
|----------------|---------|-----------|
| -0.050 | 709.482 | 0.999550 |
| -0.040 | 709.492 | 0.999712 |
| **-0.0385** | **709.493** | **0.999734** ← True p |
| 0.000 | 709.532 | **1.000000** ← Peak at √N |
| +0.040 | 709.572 | 0.999712 |
| +0.050 | 709.582 | 0.999550 |

**Key Observation**: The amplitude difference between √N and the true factors is only **0.0266%**, which is below the noise floor for reliable discrimination.

### Curvature Signal (κ)

The Z5D curvature κ(n) = d(n) · ln(n+1) / e² for large n is:
- κ(√N) ≈ 0.135335
- κ(p_true) ≈ 0.135335

**Key Observation**: Curvature is essentially constant across all candidates in the scan range, providing **zero signal** for distinguishing between different positions.

### Phase Analysis

Phase = k(log N - 2 log p):
- At √N: phase ≈ 0.000 (perfect resonance, m=0)
- At p_true: phase ≈ 0.023 radians
- At q_true: phase ≈ -0.023 radians

The phase differences are symmetric about √N, confirming that p and q are equidistant from √N in log-space. However, the phase signal alone is insufficient to determine the direction or magnitude of the correction needed.

## Fundamental Challenges

### 1. Signal Weakness

Both primary signals (amplitude and curvature) have their global maximum at √N:
- **Green's amplitude**: Peaks at √N by construction (phase = 0)
- **κ-curvature**: Approximately constant across scan range
- **Combined score**: Maximum at √N, not at true factors

### 2. Symmetry Problem

For balanced semiprimes where p ≈ q ≈ √N:
- p and q are symmetrically positioned: √N - δ and √N + δ
- All spectral signals are symmetric about √N
- Without additional constraints, cannot determine which direction to move

### 3. Resolution Limits

The required correction is ~0.04 in log-space, but:
- Amplitude varies by only ~0.03% across this range
- Curvature is constant to available precision
- Sub-percent signal differences are below practical detection threshold

### 4. No "Primality Attractor"

Classical methods like Miller-Rabin can test if a candidate is prime, providing a strong signal to "lock onto" prime factors. The focusing transform is explicitly forbidden from using such tests, removing this key source of information.

## Comparison to Classical Methods

### What Works (but is Forbidden)

1. **Trial Division**: Test divisibility at each candidate → O(√N) work
2. **Pollard's Rho**: Probabilistic cycle detection → Expected O(N^0.25)
3. **ECM**: Elliptic curve method → Subexponential in factor size
4. **NFS**: Number field sieve → Best known classical algorithm for RSA

### What This Transform Uses (Allowed but Insufficient)

1. **Wave Interference**: Naturally finds √N, not factors
2. **Curvature**: Too coarse to distinguish nearby candidates
3. **Phase Residuals**: Symmetric, no directional information
4. **Balance Prior**: Already incorporated (seeds are at √N)

## Theoretical Limitations

The focusing transform is attempting to solve the **integer factorization problem** using only:
- Continuous analytic signals (amplitude, phase)
- Geometric properties (curvature)
- Balance assumptions (p ≈ q ≈ √N)

Without discrete tests (primality, divisibility) or search proportional to error, **there is no known polynomial-time algorithm** that can distinguish between candidates that differ by 10^306 using signals that vary by only 0.03%.

## Conclusions

1. **The Focusing Transform is Correctly Implemented**
   - Multi-scale scanning covers the factor space
   - All available signals are properly evaluated
   - Execution is deterministic and fast (~2.4 ms)

2. **The Transform Fails to Improve Seeds**
   - Shrink ratio ≈ 1.0 (no improvement)
   - Seeds remain ~10^306 away from true factors
   - Bounded ±1000 refinement cannot recover factors

3. **Failure is Fundamental, Not Implementational**
   - Both Green's amplitude and κ-curvature peak at √N
   - Sub-percent signal differences are below detection threshold
   - No directional information available from symmetric signals
   - Problem is equivalent to classical factorization without classical tools

4. **Meeting Acceptance Criteria Would Require**
   - Either: Primality/divisibility tests (forbidden)
   - Or: Search radius proportional to error (forbidden)
   - Or: A breakthrough in factorization theory (not known to exist)

## Recommendations

### For This Story

The current implementation represents a best-effort focusing transform using all available analytic/geometric/spectral signals. The benchmark correctly reports that the transform does not meet the quantitative acceptance criteria (shrink_ratio < 1e-200, abs_distance_after ≤ 10^6), as required by the specification: "If found_factor is False, the report must still be emitted. Hiding failure is not allowed."

### For Future Work

To achieve meaningful focusing at RSA-2048 scale, one or more of the following would be needed:

1. **Additional Physical Constraints**: Discover new spectral signatures that distinguish primes from composites in the 1024-bit range
2. **Quantum Signals**: Use quantum amplitude estimation (requires quantum hardware)
3. **Hybrid Classical Approach**: Combine wave-based seed generation with limited classical refinement
4. **Accept Bounded Search**: Allow search radius proportional to initial error (abandons O(1) refinement constraint)

## References

- Issue: Post-Resonance Focusing Transform for RSA-Scale Factor Recovery
- Implementation: `python/post_resonance_focusing.py`
- Benchmark: `python/examples/rsa_factor_benchmark.py`
- Baseline: PR #182 (RSA-2048 Factor Candidate Extraction Benchmark)

---

*This analysis demonstrates that the focusing transform challenge at RSA-2048 scale is fundamentally hard when restricted to analytic/spectral methods only. The implementation is sound, but the problem is equivalent to factorization without factorization methods.*
