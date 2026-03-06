# Research Notes: Zero-Bias Resonance Validation

## R1. Zero-Bias Parameter Envelope
- **Decision**: Use `k ∈ [0.24, 0.32]` with fixed step `1e-4`, `m_span = ±7`, `J = 6`,
  `threshold = 0.972 * (2J + 1)`, `samples = 1800`, `precision = 320`.
- **Rationale**: Shrinking `m_span` keeps runtime <5 minutes while still covering enough modes when
  snap is applied; higher precision compensates for narrower sweep.
- **Alternatives Considered**:
  - `m_span = ±20` (slower, redundant modes).
  - `threshold ≥ 0.985` (used for control, expected to fail).

## R2. Dirichlet Normalization & Snap
- **Decision**: Implement `DirichletGate` returning magnitude normalized to `(2J + 1)` and record
  `dirichlet_normalized=true` in every config/log. Snap uses `phase_corrected + nint`, i.e.,
  compute `p_hat`, adjust phase using ln(N) residual, then apply nearest integer.
- **Rationale**: Meets GPT‑5 requirement and clarifies gate behavior; logs allow auditors to verify.
- **Alternatives Considered**:
  - Legacy unnormalized gate (ambiguous, rejected).
  - Snap via simple `round(p_hat)` (ignored phase, less accurate).

## R3. Artifact Schema
- **Decision**: Store success artifacts under `results/legit_<timestamp>/` with:
  - `config.json`: commit SHA, JVM info, precision, `dirichlet_normalized`, `snap_mode`,
    `threshold`, `J`, `k_lo`, `k_hi`, `k_step`, `m_span`, `samples`, `seed`.
  - `factors.txt`: p, q, verification check.
  - `provenance.txt`: command, environment, feature ID.
  - `run.log`: stdout/stderr capture.
- **Rationale**: Aligns with FR-005 requirements and enables downstream review.
- **Alternatives Considered**: Embedding all data in a single markdown file—rejected for tooling ease.

## R4. Control Experiments
- **Decision**: Two controls:
  1. `threshold=0.985 * (2J + 1)` (too strict) with snap enabled.
  2. Snap disabled (Dirichlet passes but candidate fails due to incorrect rounding).
  Both expect “No factor found” and log reason.
- **Rationale**: Directly matches spec acceptance criteria and GPT‑5 request.
- **Alternatives Considered**: Additional control toggling RNG seed—deemed redundant.

## R5. Novelty Audit
- **Decision**: Python script `python/zero_bias/novelty_audit.py` runs a repo-wide grep for
  `ECM|ecm|Pollard|rho|NFS|MPQS|qsieve|factorint` within `src/main/java` and `python/` (excluding
  vendored docs) and writes results to `results/legit_checks/no_classical_java.txt`.
- **Rationale**: Provides auditable proof aligning with FR-004/SC-004.
- **Alternatives Considered**: Manual grep (error-prone), static code analysis (overkill).

## R6. Auto-Bias Estimator (Fallback)
- **Decision**: If zero-bias fails, run `python/zero_bias/auto_bias_estimator.py` which:
  - Samples k-grid residuals derived solely from `ln(N)` and curvature estimates.
  - Fits a spline to residual vs. mode mismatch.
  - Outputs `auto_bias.json` containing derived bias and metadata.
- **Rationale**: Provides N-only path without referencing true factors; stored separately from
  zero-bias success to avoid confusion.
- **Alternatives Considered**: Using historical bias (invalid) or machine learning inference (overkill).
