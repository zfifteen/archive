---
name: Z Framework Issue (Bug | Enhancement | Research | Dataset | Docs)
about: Structured template for issues in the unified-framework (Z = A(B/c), Z5D, geodesic mapping, cooperative mesh)
title: "[Z] <concise-title>"
labels: ["triage"]
assignees: ["zfifteen"]
---

<!--
Use this template for all issue types. Keep tone precise and scientific.
Follow the repository’s “Z Framework Guidelines for Code Generation”.

Core Principle
- Normalize via Z = A(B/c); A = frame-dependent, B = rate/shift, c = invariant (speed of light or e²).

Validation Priorities
- Reproducible tests first (mpmath; target absolute error < 1e-16).
- Label hypotheses clearly when unverified.
-->

## 0) Issue type
- [ ] Bug
- [ ] Enhancement / Feature
- [ ] Research / Hypothesis (unverified)
- [ ] Dataset / Benchmark
- [ ] Documentation / Examples

## 1) Summary
<!-- One or two sentences describing the problem, request, or hypothesis. -->
- Problem/Goal:
- Scope and impact:

## 2) Z classification and form
Select all that apply and specify the concrete form.

- Domain:
  - [ ] Physical: Z = T(v/c) with causality checks
  - [ ] Discrete: Z = n(Δₙ/Δₘₐₓ), κ(n) = d(n)·ln(n+1)/e²
  - [ ] Geometric resolution: θ′(n,k) = φ · {n/φ}^k, with k≈0.3
  - [ ] Other:
- Concrete Z-expression (A, B, c):
  - A (frame-dependent):
  - B (rate/shift):
  - c (invariant; e.g., c or e²):
  - Units/scale conventions:

## 3) Domain-specific constraints and guards
- Physical:
  - [ ] Enforce |v| < c (raise ValueError on violation)
  - Edge cases near |v|/c → 1:
- Discrete:
  - [ ] Guard Δₘₐₓ ≠ 0 (zero-division safe)
  - [ ] d(n) well-defined for n=0 and large n
- Geometric:
  - φ usage and numeric stability:
  - k selection rationale (≈0.3 unless justified):
- Additional constraints or exceptions:
- Failure modes and explicit error handling:

## 4) Cooperative Z-enabled mesh (if applicable)
Provide parameters when discussing the mesh, Z5D, or verification.

- Target definition (e.g., hash threshold or acceptance criterion):
- Geodesic filter parameters:
  - τ (tau):
  - k (beta/exponent):
- Advantage/closed form:
  - Function name and definition:
  - Assumptions/approximations:
- Mesh parameters:
  - Batch size:
  - Verifier sampling rate:
  - Budget/attestation requirements (if any):
- Expected metrics:
  - Baseline vs. Z-mode trials-to-hit:
  - Relative enhancement (%) target:
  - Acceptance criteria:

## 5) Datasets, references, and cross-checks
- Files/Notebooks:
  - [ ] zeta_zeros.csv
  - [ ] Z5D_Reference_Impl-2.ipynb
  - [ ] Other:
- Literature / Derivations:
- Cross-check plan (what will be compared against what):

## 6) Reproducible test plan (required; mpmath preferred)
Target numerical precision: abs error < 1e-16 (unless justified).

```python
# Minimal self-contained test (adjust as needed)
import mpmath as mp
mp.mp.dps = 60  # ~2e-59; ensures <1e-16 absolute tolerance is trivial

def Z(A, B, c):
    # Example skeleton; replace with actual function under test
    if c == 0:
        raise ZeroDivisionError("Invariant c must be non-zero")
    return A * (B / c)

def test_basic():
    A, B, c = mp.mpf('1.0'), mp.mpf('2.0'), mp.mpf('3.0')
    got = Z(A, B, c)
    expect = mp.mpf('2.0') / mp.mpf('3.0')
    assert mp.almosteq(got, expect, rel_eps=mp.mpf('1e-30'), abs_eps=mp.mpf('1e-30'))

if __name__ == "__main__":
    test_basic()
    print("ok")
```

- Deterministic seeds (if randomness is used):
- Performance measurements to capture (time, trials-to-hit, memory):

## 7) Expected behavior
- Mathematical/algorithmic statement:
- Numerical targets and tolerances:
- For mesh: expected trials-to-hit, enhancement (%), verifier acceptance rate:

## 8) Actual behavior
- Observed outputs/metrics:
- Logs or minimal outputs that demonstrate the issue:

<details>
<summary>Paste logs/output</summary>

```
# logs here
```

</details>

## 9) Steps to reproduce
1)
2)
3)

## 10) Environment
- OS:
- Python:
- Dependencies (versions): mpmath, numpy, sympy, others
- Hardware (if relevant): CPU/GPU, thread counts

## 11) Risk level and status
- [ ] Hypothesis (unverified)
- [ ] Partially validated
- [ ] Fully validated
- Deviations from guidelines (if any) and justification:

## 12) Additional context
- Diagrams, pseudo-code, or references:
- Related issues/PRs:

## 13) Checklist (submitter)
- [ ] Reproducible test provided (mpmath; target abs err < 1e-16)
- [ ] Domain-specific guards implemented (causality, zero-division, stability)
- [ ] Geometric mapping uses θ′(n,k) with justified k
- [ ] Results cross-checked against datasets/notebooks
- [ ] Clear acceptance criteria and metrics
- [ ] Labeled as Hypothesis if unverified
- [ ] Concise and precise summary