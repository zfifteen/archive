# Implementation Plan: Zero-Bias Resonance Validation

**Branch**: `001-zero-bias-validation` | **Date**: 2025-11-08 | **Spec**: [specs/001-zero-bias-validation/spec.md](spec.md)  
**Input**: Feature specification describing zero-bias validation, N-only bias estimator, and novelty controls.

**Note**: This plan executes before `/speckit.tasks`; artifacts created here feed later phases.

## Summary

Deliver a reproducible Java-based factorization of `N = 137524771864208156028430259349934309717`
that succeeds **without** any bias flag, accompanied by automated failure controls and a novelty audit.
Scope includes: (1) zero-bias success run with normalized Dirichlet gate and phase-corrected snap,
(2) optional N-only bias estimator fallback if zero bias misses, (3) two negative controls
(tightened gate, snap disabled), and (4) repository-wide proof that no classical algorithms are
invoked. Outputs land under `specs/001-zero-bias-validation/validation/` plus reference logs in
`logs/zero-bias-validation/`.

## Technical Context

**Language/Version**: Java 17 (Gradle 8.14 wrapper) for factorizer; Python 3.12.3 for bias estimator & audits  
**Primary Dependencies**: `ch.obermuhlner:big-math:2.3.2`, `mpmath 1.3.0`, `sympy 1.12`, `numpy 1.26`, `pytest`, JUnit 5  
**Storage**: Local filesystem (`specs/001-zero-bias-validation/validation/`, `results/legit_<ts>/`, `logs/zero-bias-validation/`)  
**Testing**: `./gradlew test --tests org.zfifteen.sandbox.GeometricResonanceFactorizerTest`, `pytest tests/zero_bias`  
**Target Platform**: Apple M1 Max (ARM64) with macOS; CI parity on x86_64 Linux  
**Project Type**: Single repo toolchain (Java CLI + Python utilities)  
**Performance Goals**: Factorization runtime ≤ 5 minutes; controls complete ≤ 2 minutes; audit scripts ≤ 1 minute  
**Constraints**: High precision (≥300 digits) BigDecimal contexts; deterministic RNG seed 42; read-only access to prior artifacts  
**Scale/Scope**: Only 127-bit semiprime but pipeline must generalize to future RSA-scale experiments

## Constitution Check

- **Invariant Coverage**: Zero-bias workflow recomputes `Z`, `κ(n)`, and angular `θ'(n,k)` per run.
  Regression tests assert 1e-16 tolerance using `mpmath`; documentation cites formulas explicitly.
- **Precision Discipline**: CLI enforces `--mc-digits ≥ 300`, logs actual context, fixes RNG seed 42
  for any sampling, and raises explicit errors for invalid ranges.
- **Testing Strategy**: TDD adds JUnit cases for zero-bias success/failure, pytest suites for bias
  estimator math, integration harness replicating gradle commands, and failing tests for each control.
- **Data Governance**: All generated CSV/JSON artifacts store schema under
  `docs/methods/zero-bias-validation/` with deterministic column ordering, and evidence sits inside
  `specs/001-zero-bias-validation/validation/`.
- **Observability & Charter**: Structured logs go to `logs/zero-bias-validation/` capturing JVM,
  precision, seeds, gate parameters, `dirichlet_normalized`, `snap mode`, and commit SHA. Every
  deliverable runs `python tools/validate_charter.py`.
- **Charter Sections & Manifest**: Plan, spec, and forthcoming tasks include all 10 Charter sections.
  Validation report emits `analysis_manifest.json` referencing success + controls.

Gate Result (pre-design): ✅ Requirements satisfied; proceed to research & design.

## Project Structure

### Documentation (this feature)

```text
specs/001-zero-bias-validation/
├── plan.md
├── spec.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── zero-bias-cli.yaml
├── validation/
│   ├── legit_<timestamp>/
│   └── controls/
├── audit/
│   └── no_classical_java.txt
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/main/java/org/zfifteen/sandbox/
├── GeometricResonanceFactorizer.java
└── resonance/
    ├── DirichletGate.java
    └── SnapKernel.java

python/zero_bias/
├── __init__.py
├── auto_bias_estimator.py
└── novelty_audit.py

tests/
├── java/org/zfifteen/sandbox/GeometricResonanceFactorizerTest.java
├── analysis/test_zero_bias_controls.py
└── regression/test_zero_bias_cli.py

logs/zero-bias-validation/
results/
└── legit_<timestamp>/...
```

**Structure Decision**: Extend existing Java package for gating/snap helpers, keep Python utilities in
`python/zero_bias/`, and store generated evidence under `specs/001-zero-bias-validation/validation/`.

## Complexity Tracking

No Constitution violations anticipated; table intentionally empty.

## Phase 0 – Research & Unknown Resolution

1. Review prior successful calibration run to extract only invariant-based reasoning (no ln(q/p)).
2. Validate normalized Dirichlet formulae and phase-corrected snap math via `mpmath` notebooks.
3. Determine feasible k-range/step (0.24–0.32 with 1e-4) and minimal m-span (±7) to keep runtime <5m.
4. Specify schema for `config.json`, `factors.txt`, `provenance.txt`, and control logs.
5. Define novelty-audit grep queries (ECM, Pollard, rho, NFS, ecm, gmp-ecm, pari, mpqs).

Output: `research.md` detailing decisions, rationales, and alternatives.

## Phase 1 – Design & Contracts

1. **Data Model**: Capture `ZeroBiasRun`, `BiasEstimatorResult`, `ControlExperiment`, and
   `NoveltyAuditLog` entities (fields + validation).
2. **Contracts**: Author `contracts/zero-bias-cli.yaml` describing CLI inputs/outputs for success and
   control runs, plus schema references.
3. **Quickstart**: Step-by-step doc showing how to run success and control experiments, gather
   artifacts, and execute novelty audit + charter validation.
4. **Agent Context**: Update agent guidance (AGENTS.md) once design solidifies to reflect zero-bias
   goals and allowed tooling.

Gate Result (post-design): Pending – will reassess after artifacts generated.

## Implementation Strategy (pre-tasks)

1. **MVP (Zero-bias run)**: Ensure factorizer honors normalized gate + snap, produce success bundle.
2. **Controls**: Introduce parameter toggles for gate tightening & snap disable; confirm expected fail.
3. **Novelty audit**: Automate grep + manifest creation.
4. **Auto-bias fallback**: Only if zero-bias fails; uses estimator script fed by N-only data.
5. **Documentation**: Update validation reports & PR description with artifacts + controls.

## Risk & Mitigation

- **Zero-bias still fails**: Implement estimator fallback; include diagnostic metrics to justify gap.
- **Runtime exceeds 5 min**: Reduce k-step or m-span, profile Dirichlet kernel, parallelize samples.
- **Evidence incompleteness**: Automate artifact creation via Gradle task that writes JSON/log bundle.
- **Novelty skepticism**: Ensure grep log is part of CI artifacts and cross-link in PR template.

---

Post-design Constitution Check will be appended after research/data/contract artifacts exist.
