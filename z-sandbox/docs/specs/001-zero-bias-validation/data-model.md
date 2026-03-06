# Data Model: Zero-Bias Resonance Validation

## ZeroBiasRun
- **Fields**
  - `run_id` (string, required) – timestamped identifier (e.g., `legit_20251108_1200UTC`)
  - `commit_sha` (string) – git commit used
  - `jvm_version`, `gradle_version`
  - `precision_digits` (int ≥ 300)
  - `dirichlet_normalized` (bool) – MUST be true
  - `snap_mode` (enum: `phase_corrected_nint`)
  - `bias_present` (bool, const false)
  - `threshold`, `J`, `k_lo`, `k_hi`, `k_step`, `m_span`, `samples`, `seed`
  - `status` (enum: SUCCESS | FAIL)
  - `log_path`, `config_path`, `factors_path`, `provenance_path`
- **Validation Rules**
  - `dirichlet_normalized` must equal true; otherwise run is invalid.
  - `snap_mode` must equal `phase_corrected_nint`.
  - `precision_digits` must be ≥ 300.
  - `bias_present` must be false; any true value invalidates the run.
  - Missing artifacts result in plan/test failure.

## BiasEstimatorResult
- **Fields**
  - `estimator_id` (string)
  - `derived_bias` (decimal) – may be null when zero-bias succeeds
  - `method` (string) – e.g., `curvature_residual_fit`
  - `input_domain` (JSON) – k-grid, residual stats
  - `seed` (int, default 42)
  - `timestamp`, `commit_sha`
  - `notes`
- **Validation Rules**
  - All values must be inferred from N; no p/q data allowed.
  - If estimator is unused, record `status: unused`.

## ControlExperiment
- **Fields**
  - `control_id` (string) – e.g., `gate_tight`, `snap_disabled`
  - `parameter_overrides` (JSON)
  - `expected_outcome` (string)
  - `observed_outcome` (string)
  - `log_path`, `config_path`
  - `verified_by_test` (bool)
- **Validation Rules**
  - Observed outcome must match expectation (i.e., fail). If not, escalate severity.

## NoveltyAuditLog
- **Fields**
  - `audit_id`
  - `grep_terms` (list<string>)
  - `files_scanned` (count)
  - `hits` (list<path>)
  - `generated_at`
  - `output_path`
- **Validation Rules**
  - `hits` must be empty for disallowed algorithms; non-empty triggers CRITICAL alert.

## EvidenceBundle (Derived)
- **Fields**
  - `zero_bias_run` (ZeroBiasRun)
  - `controls` (list<ControlExperiment>)
  - `novelty_audit` (NoveltyAuditLog)
  - `bias_estimator` (BiasEstimatorResult | null)
  - `manifest_path`
- **Validation Rules**
  - Bundle incomplete → Mission Charter validation fails.
  - manifest must reference all included artifacts by path.
