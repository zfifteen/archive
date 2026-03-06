---
description: "Task list for the Zero-Bias Resonance Validation feature (revised)"
---

# Tasks: Zero-Bias Resonance Validation — Revised

**Input**: Design documents from `/specs/001-zero-bias-validation/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/zero-bias-cli.yaml, quickstart.md

**Tests**: Mandatory failing tests precede implementation for each user story (per constitution). `[P]` denotes parallel-safe tasks.

**Organization**: Tasks are grouped by user story to keep increments independently testable.

## Format: `[ID] [P?] [Story?] Description with file path`

## Constitution Hooks (complete before Setup)

- [ ] **T000A** Define **zero-bias contract invariant**: update `specs/001-zero-bias-validation/contracts/zero-bias-cli.yaml` to **forbid any bias input** and require `biasPresent: false` in request/manifest.
- [ ] **T000B** Add **runtime bias guard** in Java: fail fast if a bias arg/key is detected anywhere (CLI/env/config). Always emit `biasPresent=false` in the manifest.
- [ ] **T001** Define invariant validation helpers ensuring `Z`, `κ(n)`, `θ'(n,k)` tolerances within `mpmath` 1e-16 in `python/zero_bias/invariant_checks.py`
- [ ] **T002** Implement precision + RNG seed guardrail module in `tools/analysis/config.py` reused by CLI/estimator
- [ ] **T003** Document CSV/JSON schemas for zero-bias artifacts in `docs/methods/zero-bias-validation/schema.md`
- [ ] **T004** Add structured logging guidelines (fields: commit SHA, precision, `dirichlet_normalized`, `snap_mode`, seeds) to `logs/zero-bias-validation/README.md`

## Phase 1: Setup (Shared Infrastructure)

- [ ] **T005** Create validation directories (`specs/001-zero-bias-validation/validation/legit_template/`, `specs/001-zero-bias-validation/validation/controls/`, `specs/001-zero-bias-validation/audit/`) and placeholder `.gitkeep` files
- [ ] **T006** Scaffold `python/zero_bias/__init__.py`, `auto_bias_estimator.py`, `novelty_audit.py`, and `invariant_checks.py`
- [ ] **T007** Add Gradle task `zeroBiasRun` and output location wiring in `build.gradle`
- [ ] **T008** Update quickstart with frozen-context script references (precision/JVM/log paths) in `specs/001-zero-bias-validation/quickstart.md`; **explicitly remove any `--bias=0` examples** (zero-bias runs must omit the flag entirely).

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] **T009** Implement normalized `DirichletGate` and `SnapKernel` classes under `src/main/java/org/zfifteen/sandbox/resonance/`
- [ ] **T010** Refactor `GeometricResonanceFactorizer` to consume new gate/snap utilities and **reject** any bias flag/setting (`src/main/java/org/zfifteen/sandbox/GeometricResonanceFactorizer.java`)
- [ ] **T010A** Add `DirichletNormalizationAssert` in Java to assert normalized form at runtime; log `dirichlet_normalized=true`.
- [ ] **T010B** Add `PhaseCorrectedSnapAssert` in Java to assert phase-corrected nearest-integer snap; log `snap_mode=phase_corrected_nint`.
- [ ] **T011** Prefer **artifact emission from Java** (config.json, factors.txt, provenance.txt) for determinism; keep `tools/analysis/artifact_writer.py` optional for post-run analysis.
- [ ] **T012** Seed reusable fixtures for 127-bit target under `tests/analysis/fixtures/zero_bias/`
- [ ] **T013** Create pytest utilities for reading config/factor logs in `tests/analysis/conftest.py`

## Phase 3: User Story 1 – Zero-Bias Success Path (Priority: P1) 🎯 MVP

**Goal**: Prove the Java factorizer succeeds **without any bias flag**, emitting required artifacts.

**Independent Test**: Execute `./gradlew zeroBiasRun` (no bias option); assert `biasPresent=false`, `dirichlet_normalized=true`, `snap_mode=phase_corrected_nint`, and `FOUND` lines referencing p/q.

### Tests (write-first)

- [ ] **T014** [P] [US1] Add regression test verifying zero-bias CLI invocation and artifact completeness in `tests/regression/test_zero_bias_cli.py`
- [ ] **T015** [P] [US1] Extend `org.zfifteen.sandbox.GeometricResonanceFactorizerTest` to assert success without bias flag and log fields
- [ ] **T015A** [US1] Add **runtime budget assertion** (≤ 5 min on M1 Max); fail the test if exceeded.

### Implementation

- [ ] **T016** [US1] Implement CLI context freezer to capture commit/JVM/precision in `tools/analysis/context_freezer.py`
- [ ] **T017** [P] [US1] Add artifact emission (config.json, factors.txt, provenance.txt, run.log) to Gradle run pipeline in `build.gradle`
- [ ] **T018** [US1] Update `specs/001-zero-bias-validation/validation/report.md` template with instructions and placeholders
- [ ] **T019** [P] [US1] Wire structured logging to `logs/zero-bias-validation/zero_bias_success.log`
- [ ] **T020** [US1] Document verification procedure and attach sample outputs in `docs/validation/reports/zero_bias_success.md`

## Phase 4: User Story 2 – N-Only Bias Estimator (Priority: P2)

**Goal**: Provide fallback estimator derived solely from N that can recover success when zero-bias misses.

**Independent Test**: Run `python python/zero_bias/auto_bias_estimator.py --N <value>` and ensure output JSON contains only N-derived metrics; supply that JSON to the factorizer (separate command) and assert success with `biasSource="N-only"` in manifest.

### Tests

- [ ] **T021** [P] [US2] Create pytest coverage for bias estimator residual math in `tests/analysis/test_auto_bias_estimator.py`
- [ ] **T022** [P] [US2] Add integration test ensuring fallback manifest documents `biasSource="N-only"` in `tests/regression/test_auto_bias_flow.py`
- [ ] **T022A** [US2] Add runtime budget assertion (≤ 2 min on M1 Max) for estimator execution.

### Implementation

- [ ] **T023** [US2] Implement curvature residual sampling + spline fit in `python/zero_bias/auto_bias_estimator.py`
- [ ] **T024** [US2] Extend Gradle CLI to accept **only** the estimator JSON input (no CLI bias); log `biasSource="N-only"` in manifest in `build.gradle`
- [ ] **T025** [US2] Update data manifest schema for estimator outputs `specs/001-zero-bias-validation/validation/auto_bias.json`
- [ ] **T026** [US2] Document fallback instructions + guardrails in `specs/001-zero-bias-validation/quickstart.md`

## Phase 5: User Story 3 – Controls & Novelty Evidence (Priority: P3)

**Goal**: Demonstrate reproducibility via two failing controls and a novelty audit proving no classical factoring paths.

**Independent Test**: Run control commands (tight gate, snap disabled) and novelty audit script; ensure logs report expected failures and grep output is empty.

### Tests

- [ ] **T027** [P] [US3] Add pytest verifying control logs contain failure markers + parameters in `tests/analysis/test_zero_bias_controls.py`
- [ ] **T028** [P] [US3] Create audit test that checks grep script flags disallowed keywords in `tests/analysis/test_novelty_audit.py`
- [ ] **T028A** [US3] Add runtime budget assertion (≤ 2 min on M1 Max) for control runs and audit script.

### Implementation

- [ ] **T029** [US3] Implement control runner helper that toggles parameters and saves logs under `specs/001-zero-bias-validation/validation/controls/` via `tools/analysis/control_runner.py`
- [ ] **T030** [US3] Implement `python/zero_bias/novelty_audit.py` scanning for `ECM|ecm|ellcurves|Pollard|pollard|rho|NFS|nfs|MPQS|msieve|qsieve|yafu|nextProbablePrime|probablePrime` and writing `specs/001-zero-bias-validation/audit/no_classical_java.txt`; **allow** `BigInteger.isProbablePrime` only in a separate verifier, **deny** in factorization path.
- [ ] **T031** [US3] Update documentation with control summaries + audit evidence references in `docs/validation/reports/zero_bias_controls.md`

## Phase N: Polish & Cross-Cutting Concerns

- [ ] **T032** Generate final validation bundle (success + controls + audit) and attach manifest in `specs/001-zero-bias-validation/validation/report.md`
- [ ] **T033** Run `python tools/validate_charter.py specs/001-zero-bias-validation/validation/report.md` and capture results
- [ ] **T034** Update PR #224 description emphasizing zero-bias success, calibration caveat, and attach artifacts/logs
- [ ] **T035** Replace any remaining docs/examples that show `--bias=0` with **no bias arg** in zero-bias runs (avoid ambiguity).
- [ ] **T036** Add a **CI job** that runs: zero-bias success, both failing controls, novelty audit; emit artifacts as PR build outputs with retention policy and failure alerting.
- [ ] **T037** [P] Update AGENTS.md with zero-bias goals and allowed tooling once design solidifies.

## Dependencies & Execution Order

- Setup → Foundational → User Story phases (US1 P1 → US2 P2 → US3 P3) → Polish.
- US2 depends on US1 completion (fallback only needed once zero-bias pipeline exists).
- US3 depends on US1 infrastructure for logging/artifacts; controls reuse same runner.

## Parallel Execution Examples

- Constitution hooks T000A–T004 can proceed concurrently.
- Setup T006/T007/T008 can run in parallel once directories created (after T005).
- In US1, T017 and T019 are parallel-safe after T016; tests T014/T015 run independently.
- US2 estimator tasks T023/T024 can progress in parallel with documentation T026 once data model ready.
- US3 audit implementation (T030) can run parallel to control runner (T029).

## Implementation Strategy

1. **MVP**: Complete US1 to produce zero-bias success artifacts (blocks everything else).
2. **Controls/Audit**: Build US3 next to satisfy compliance requirements while success context is fresh.
3. **Fallback Estimator**: Implement US2 only if zero-bias shows instability; otherwise ship as optional capability.
4. **Polish**: Bundle evidence, run charter validator, and refresh PR narrative.

## Risk Mitigation Notes

- **Zero-bias failure**: If US1 fails, immediately activate US2 estimator fallback; log diagnostic residuals for gap analysis.
- **Runtime exceedance**: Profile Dirichlet kernel and parallelize samples; reduce k-step or m-span as last resort.
- **Artifact incompleteness**: Automate emission via Gradle task with validation hooks; treat missing artifacts as critical failures.
- **Novelty skepticism**: Cross-link audit output in PR and CI artifacts; prepare rebuttal evidence for any false positives.
