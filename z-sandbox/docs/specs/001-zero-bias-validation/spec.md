# Feature Specification: Zero-Bias Resonance Validation

**Feature Branch**: `001-zero-bias-validation`  
**Created**: 2025-11-08  
**Status**: Draft  
**Input**: User description: "Regarding GPT‑5’s “bias” critique…zero-bias (or N-only auto-bias) run with documented controls."

## Constitution Alignment Snapshot *(complete before drafting stories)*

1. **Invariants**: This feature touches all three invariants (`Z`, `κ(n)`, `θ'(n,k)`) because the zero-bias run must prove the resonance method respects them without hidden offsets. Validation harnesses `mpmath` 1e-16 tolerance checks inside new regression tests for each invariant calculation.
2. **Precision Plan**: Java factorizer will operate with `BigDecimal` precision ≥ 300 digits and Python harnesses will set `mp.mp.dps = 300`. RNG seed stays fixed at 42 when sampling mode/scans. Invalid inputs (missing N, negative precision) raise `ValueError` (Python) or throw `IllegalArgumentException` (Java) and log context.
3. **Testing Scope**: New JUnit tests cover zero-bias execution and control failures; pytest suites verify bias estimator math plus documentation manifests. Integration tests replay the gradle command line recorded in validation docs and assert that removing snap or tightening the Dirichlet gate causes expected failures.
4. **Data Exchange**: Analyzer reports (CSV/JSON) documenting the zero-bias run will publish schemas under `docs/methods/zero-bias-validation/`. All generated evidence (logs, manifests) lives in `specs/001-zero-bias-validation/validation/` with deterministic column ordering for downstream Python validators.
5. **Observability & Charter**: Every run outputs structured logs to `logs/zero-bias-validation/` capturing JVM info, precision, seed, gate params, and pass/fail state. Final documentation references Mission Charter sections and includes validator output from `python tools/validate_charter.py specs/001-zero-bias-validation/report.md`.

## Mission Charter Sections *(complete all 10 elements before submission)*

### First Principles
- Resonance proof must rely solely on N and Z-Framework axioms (`Z = A(B/e²)`, `κ(n) = d(n)·ln(n+1)/e²`, `θ'(n,k) = φ·((n mod φ)/φ)^k`).  
- Zero-bias workflow may not include any parameter derived from p or q; all bias or phase adjustments stem from invariant relationships using N alone.

### Ground Truth & Provenance
- **Target**: Semiprime `N = 137524771864208156028430259349934309717` (balanced 127-bit).  
- **Executors**: Codex agent + CI runners; manifest must identify who ran each experiment.  
- **Timestamps**: ISO 8601 with timezone for every run and control.  
- **Sources**: Link to `GeometricResonanceFactorizer.java`, prior PR #224 docs, and Mission Charter for compliance. All external math references require citation with access dates.

### Reproducibility
- **Commands**: Document gradle invocation for zero-bias success (`./gradlew run --args="N --mc-digits=300 --samples=... --threshold=0.972 ..."`) with **no bias flag provided**, plus failure controls and validation suites.  
- **Environment**: Java 17+, Gradle 8.14, Python 3.12.3 for analysis scripts, Apple M1 Max baseline.  
- **Configuration**: Provide YAML/JSON capturing gate thresholds, k-grid ranges, snap toggles, and bias estimator choices stored in `specs/001-zero-bias-validation/config/`.  
- **Output Expectations**: Successful run prints `FOUND` with p/q and verification lines while emitting artifacts that explicitly include `dirichlet_normalized`, `snap=phase_corrected+nint`, `threshold`, `J`, `k_lo`, `k_hi`, `k_step`, `m_span`, `precision`, `seed`, and commit SHA; controls log explicit failure messages.

### Failure Knowledge
- Identify failure modes: insufficient sampling density, mis-normalized Dirichlet gate, disabled snap, or bias estimator divergence.  
- For each, document diagnostics (logs, numeric residuals) and mitigation (increase samples, renormalize, restore snap).  
- Keep incident log under `specs/001-zero-bias-validation/failures.md`.

### Constraints
- Zero reliance on classical factoring helpers (ECM, Pollard rho, etc.); repository-wide grep plus runtime assertions must confirm they are not invoked, and novelty audit artifacts must record the grep output (e.g., `results/legit_checks/no_classical_java.txt`).  
- Feature remains read-only against historical artifacts; new evidence stored under `specs/001-zero-bias-validation/`.  
- Observability requirements mandate logging of seeds/precision; missing logs are CRITICAL per constitution.  
- Compliance reviewers require two negative controls plus the successful zero-bias run before sign-off.

### Context
- **Primary stakeholders**: Research lead validating novelty, GPT‑5 advisor requesting bias-proof evidence, compliance reviewers for Mission Charter.  
- **Problem**: Prior successes used bias derived from true factors, undermining independence claims.  
- **Timeline**: Immediate blocker before pursuing RSA-260; must land prior to next release milestone.  
- **Dependencies**: Existing GeometricResonanceFactorizer implementation, infrastructure for logs/tests, Mission Charter validator.

### Models & Limits
- Model remains geometric resonance with Dirichlet kernel gating and nearest-integer snap.  
- Validity: Balanced semiprimes up to 260 bits, but current scope limited to 127-bit proof-of-record.  
- Known limits: extremely narrow k/bias windows require high precision; zero-bias success depends on correct normalization and dense mode scanning.  
- Document approximations (e.g., tolerance for Dirichlet magnitude) with explicit numeric bounds.

### Interfaces & Keys
- CLI options for `GeometricResonanceFactorizer` (bias, k, J, samples, m-span).  
- Python helpers for auto-bias estimator (file paths under `python/zero_bias/`).  
- Environment variables: `ZERO_BIAS_LOG_DIR`, `SPECKIT_FEATURE`, `PYTHONPATH`.  
- Secrets: none; ensure no sensitive keys printed in logs.

- ### Calibration
- Parameters to calibrate: Dirichlet threshold (0.92*(2J+1) baseline), m-span, sample count, optional auto-bias prior (available **only** in the P2 fallback flow after zero-bias failure).  
- Tuning method: coarse sweep with RNG seed 42, followed by deterministic refinement explained in documentation.  
- Validation: replicate success three times, include standard deviation of candidate counts, and log gate amplitude statistics.

### Purpose
- Demonstrate that geometric resonance alone (with zero or N-only bias) factors the 127-bit semiprime, providing defensible novelty evidence.  
- Deliverable includes success run, two controlled failures, repository-wide grep proof, and updated documentation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Zero-Bias Success Path (Priority: P1)
Research lead needs a documented gradle command that runs **without any bias flag** and still recovers p and q with full verification logs.

**Why this priority**: Establishes independence from hidden calibration; blocks further research if unmet.

**Independent Test**: Run `./gradlew run --args="N --mc-digits=320 --samples=1800 --k-lo=0.24 --k-hi=0.32 --k-step=0.0001 --m-span=7 --J=6 --threshold=0.972"` (no bias flag), capture stdout/stderr, assert presence of `FOUND` lines plus verification that `p*q == N` and both primes. Tests fail if any parameter deviates, if `biasPresent=true`, or if snap/gate misconfigured.

**Acceptance Scenarios**:
1. Given zero bias, normalized gate, and snap enabled, when the factorizer runs, then it prints `FOUND` with correct p/q and exits success.
2. Given zero bias but corrupted normalization, when the run executes, then it fails and logs diagnostic, which tests detect.

---

### User Story 2 - N-Only Bias Estimator (Priority: P2)
Engineers require an automatic bias estimator derived solely from N to recover success when bias=0 run fails.

**Why this priority**: Provides reproducible fallback while preserving independence.

**Independent Test**: Execute estimator script generating bias candidates from curvature residuals, feed output into factorizer, assert success without referencing p/q ground truth.

**Acceptance Scenarios**:
1. Given estimator output stored in `specs/.../auto_bias.json`, when factorizer consumes it, then it finds factors and logs estimator metadata.
2. Given estimator configured incorrectly, when verification runs, then tests confirm failure and instruct to revisit estimator parameters.
3. Any estimator-driven run must log `biasSource=N-only` and `biasPresent=true` only within the fallback manifest.

---

### User Story 3 - Controls & Reproducibility Evidence (Priority: P3)
Compliance reviewers must see negative controls and proof no classical methods participated.

**Why this priority**: Validates novelty, addresses GPT‑5 critique, and satisfies Mission Charter.

**Independent Test**: Produce two failing control runs (e.g., removing snap or over-tightening gate) plus repo grep log; tests ensure controls fail as expected and grep output lists allowed methods only.

**Acceptance Scenarios**:
1. Given snap disabled, when factorizer runs, then it fails and logs “snap required”; test checks for failure signature.
2. Given gate threshold set above theoretical limit, when run executes, then it logs “Dirichlet gate too strict” and returns no factors; grep log shows no ECM/NFS references.

---

### Edge Cases
- Zero-bias run exceeding time limit (≥5 minutes) must be flagged.
- Auto-bias estimator returning NaN or ±∞ should abort run with diagnostics.
- Controls accidentally succeeding (unexpected factor discovery) must be treated as CRITICAL bug.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Java factorizer MUST run with **no bias flag supplied** (implicit zero bias) and document a successful factorization or provide actionable diagnostics explaining failure.
- **FR-002**: The system MUST implement an N-only bias estimator and expose its calculations (JSON + markdown report) without referencing true factors.
- **FR-003**: Two control experiments (tight gate, snap removal) MUST be executed and recorded, each demonstrating failure with logged reasons.
- **FR-004**: A repository-wide grep/log MUST prove that no classical factoring routines are invoked by scanning for `ECM|ecm|ellcurves|Pollard|pollard|rho|NFS|nfs|MPQS|msieve|qsieve|yafu|nextProbablePrime|probablePrime`. The log is stored at `specs/001-zero-bias-validation/audit/no_classical_java.txt`.
- **FR-005**: Documentation MUST include commands, outputs, manifest, and validation evidence stored under `specs/001-zero-bias-validation/`, with each artifact explicitly listing `dirichlet_normalized`, `snap`, `threshold`, `J`, `k` bounds/step, `m_span`, `precision`, `seed`, and commit SHA.
- **FR-006**: All deliverables MUST pass Mission Charter validation via `python tools/validate_charter.py <report>`.

### Non-Functional Requirements

- **NFR-001**: Zero-bias run MUST complete within 5 minutes on Apple M1 Max using Gradle run target.
- **NFR-002**: Logs MUST capture JVM version, precision, sample count, gate parameters, snap/gate normalization flags, and seeds for every experiment.
- **NFR-003**: Bias estimator computations MUST be deterministic (seed 42) and reproducible via documented script.
- **NFR-004**: All evidence files MUST be ASCII/UTF-8 to ensure portability across review tooling.

### Key Entities *(include if feature involves data)*

- **ZeroBiasRun**: Metadata for the primary success attempt (parameters, timestamps, output logs).
- **BiasEstimatorResult**: Stores derived bias, method, residual metrics, and provenance.
- **ControlExperiment**: Captures parameter overrides, expected failure reason, and observed outcome.
- **NoveltyAuditLog**: Consolidates grep results and compliance attestations.

## Success Criteria *(mandatory)*

- **SC-001**: Zero-bias Gradle run produces correct p/q with verification lines and attached logs.
- **SC-002**: Auto-bias estimator (N-only) yields success when zero bias fails, with documented derivation and manifest.
- **SC-003**: Both control experiments fail as expected and are archived with diagnostics.
- **SC-004**: Novelty audit confirms absence of classical factoring methods and is referenced in the final report.
- **SC-005**: Success artifacts explicitly assert `biasPresent=false` (in config/log/manifest); any true value invalidates the run.

### Assumptions

- GeometricResonanceFactorizer already contains hooks for bias, gate normalization, and snap toggles.
- Access to high-precision math libraries (BigDecimal/BigInteger, mpmath) is available on all target environments.
- Reviewers accept structured logs and manifests stored under `specs/001-zero-bias-validation/`.

### Dependencies

- Existing Java factorizer source (`src/main/java/org/zfifteen/sandbox/GeometricResonanceFactorizer.java`).
- Gradle tooling, Mission Charter validator, and logging infrastructure.
- Access to prior validation artifacts for comparison (PR #224).
