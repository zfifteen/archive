# Feature Specification: Initial Analysis

**Feature Branch**: `001-initial-analysis`  
**Created**: 2025-11-08  
**Status**: Draft  
**Input**: User description: "Initial analysis"

## Constitution Alignment Snapshot *(complete before drafting stories)*

1. **Invariants**: No numerical invariants (`Z`, `κ(n)`, `θ'(n,k)`) are modified. The feature verifies that referenced specs cite these invariants and flags omissions so automated `mpmath` checks remain mandated at 1e-16 tolerance.
2. **Precision Plan**: Analysis operates on textual artifacts only; nevertheless, deterministic parsing with fixed RNG seed 42 is required for any sampling (e.g., prioritizing findings). Inputs that cannot be parsed must raise `ValueError` equivalents with logged context.
3. **Testing Scope**: Unit tests will cover requirement extraction, coverage mapping, and severity grading. Integration tests replay representative repositories (including `tests/test_lorentz_dilation.py` references) to ensure the analyzer blocks releases when invariants or Mission Charter sections are missing.
4. **Data Exchange**: The command inspects local Markdown/JSON artifacts under `specs/`, `plan.md`, and `tasks.md`; any summary CSV/JSON exports must store schemas in `docs/methods/initial-analysis-schema.md` and maintain deterministic column ordering for Python validators.
5. **Observability & Charter**: All runs emit structured logs to `logs/initial-analysis/` including feature ID, timestamp, seeds, and validation status. Each generated report references the Mission Charter sections it verified and attaches a manifest validated via `python tools/validate_charter.py`.

## Mission Charter Sections *(complete all 10 elements before submission)*

### First Principles
- Uphold Z-Framework axioms by ensuring every inspected spec restates `Z = A(B / e²)`, `κ(n) = d(n) · ln(n+1) / e²`, and `θ'(n,k) = φ · ((n mod φ) / φ)^k` when applicable.  
- Measurements and tolerances mirror repository standards: ppm-scale error metrics, precision verified via `mpmath` with tolerance < 1e-16, and deterministic seed 42 for stochastic sampling.

### Ground Truth & Provenance
- **Artifacts Analyzed**: `spec.md`, `plan.md`, `tasks.md`, and Constitution file committed to the same feature directory.  
- **Executor Identity**: Named agent (e.g., "Z-Sandbox Analyzer") recorded in each manifest.  
- **Timestamps**: ISO 8601 with timezone (UTC).  
- **Sources**: Internal repository documents plus any cited references; analyzer must capture title, author, domain, locator, and access time for each external source referenced within the inspected documents.

### Reproducibility
- **Commands**:  
  1. `git checkout <feature-branch>`  
  2. `PYTHONPATH=python SPECKIT_FEATURE=<id> python -m tools.initial_analysis --spec specs/<id>/spec.md --plan specs/<id>/plan.md --tasks specs/<id>/tasks.md`  
  3. `python tools/validate_charter.py specs/<id>/outputs/initial-analysis.md`
- **Environment**: Python 3.12.3, Java 11+ (for Gradle hooks), Apple M1 Max baseline.  
- **Expected Output**: Markdown report with findings table, coverage summary, manifest JSON, exit code 0 on success.  
- **Validation**: Compare generated manifest against schema version 1.0.0; rerun until deterministic identical output for repeated executions.

### Failure Knowledge
- **Missing Artifact**: If any of spec/plan/tasks is absent, the analyzer emits CRITICAL failure with remediation guidance (rerun `/speckit.tasks`).  
- **Parsing Error**: Malformed Markdown sections trigger diagnostics pinpointing offending line and recommended fix. Mitigation: provide fallback plain-text scan plus direct file path references.  
- **Constitution Drift**: When Constitution hash differs from expected version range, analyzer blocks with instructions to rerun after syncing `.specify/memory/constitution.md`.
- **Known Limitations**: Does not rewrite files; manual edits required. Analyzer assumes English-language artifacts.

### Constraints
- No modifications to source documents; analyzer operates strictly read-only.  
- Reports may reference sensitive research, so outputs inherit repository confidentiality and must remain within version control.  
- Compliance with Mission Charter is mandatory; analyzer must fail fast when mandatory sections or manifests are missing.  
- Legal constraints: reuse only internal or properly cited public sources; no proprietary datasets pulled automatically.

### Context
- **Who**: Research leads, compliance reviewers, and implementation teams needing a go/no-go signal before `/speckit.plan` or coding work.  
- **What**: Automated initial analysis producing findings on inconsistencies, coverage, and constitution alignment.  
- **When**: Triggered immediately after `/speckit.tasks` completes and before `/speckit.implement`.  
- **Where**: Runs inside z-sandbox repository, typically in CI or local CLI.  
- **Why**: Prevent costly rework by catching missing requirements, charter violations, or coverage gaps early.  
- **Dependencies**: Requires completed spec/plan/tasks set, up-to-date Constitution, and Mission Charter manifest schema.

### Models & Limits
- **Finding Classification Model**: Rule-based severity assignment (Critical/High/Medium/Low) derived from constitution mandates and requirement coverage heuristics.  
- **Assumptions**: Input documents follow template headings; sections absent are treated as issues.  
- **Validity Range**: Works for feature directories generated via `/speckit.specify`; behavior undefined for ad-hoc folders.  
- **Break Points**: More than 50 findings triggers overflow summary; analyzer must note truncated list.

### Interfaces & Keys
- **Primary Interface**: CLI command `/speckit.analyze` (alias of the analyzer script). Arguments include `--feature`, `--report`, `--manifest`, and optional `--max-findings`.  
- **Inputs**: Paths to spec, plan, tasks; Constitution and Mission Charter read from repository root; optional config file `specs/<id>/analyze.yaml`.  
- **Outputs**: Markdown report, JSON manifest (schema v1.0.0), structured log entries in `logs/initial-analysis/`.  
- **Environment Variables**: `SPECKIT_FEATURE`, `PYTHONPATH`, `Z_ANALYSIS_LOG_LEVEL`.  
- **Permissions**: Read access to repository files; write access limited to feature directory outputs and logs.

### Calibration
- **Severity Thresholds**:  
  - Critical: Constitution violation or missing artifacts.  
  - High: Requirement conflicts or untestable stories.  
  - Medium: Terminology drift or missing non-functional coverage.  
  - Low: Style and minor redundancies.  
- **Tuning Method**: Retrospective analysis of the last 10 features; adjust rules until reviewers agree ≥95% with suggested severity.  
- **Validation**: Evaluate analyzer on historical specs; expect ≥90% recall on known issues and ≤10% false positives for Critical findings.

### Purpose
- Provide a deterministic readiness report that confirms artifacts satisfy Mission Charter and Constitution requirements before development starts.  
- Enable stakeholders to make informed go/no-go decisions with quantified findings, coverage percentage, and unresolved clarifications documented.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Research Lead Requests Readiness Signal (Priority: P1)
The research lead runs the analyzer right after `/speckit.tasks` to confirm the feature is ready for detailed planning.

**Why this priority**: Prevents wasted design/implementation cycles.

**Independent Test**: Execute analyzer on a complete feature directory; verify it produces findings table, coverage summary, and PASS manifest without manual edits.

**Acceptance Scenarios**:

1. **Given** spec/plan/tasks exist, **When** the analyzer runs, **Then** it reports coverage ≥95% or calls out missing mappings explicitly.
2. **Given** a constitution violation, **When** the analyzer executes, **Then** it flags the issue as CRITICAL and exits non-zero.

---

### User Story 2 - Spec Author Reviews Coverage Mapping (Priority: P2)
The spec author wants confirmation that every functional requirement has at least one task before handoff.

**Why this priority**: Ensures requirements do not slip into implementation without coverage.

**Independent Test**: Provide a feature directory with intentionally missing tasks; analyzer must pinpoint exact requirement keys lacking tasks.

**Acceptance Scenarios**:

1. **Given** FR-IDs in spec, **When** analyzer runs, **Then** it lists associated task IDs or identifies gaps.
2. **Given** duplicate or conflicting requirements, **When** analyzer runs, **Then** it groups them and recommends consolidation.

---

### User Story 3 - Compliance Reviewer Needs Charter Evidence (Priority: P3)
Compliance reviewer must ensure Mission Charter sections and manifest exist before approving planning work.

**Why this priority**: Charter violations block delivery sign-off.

**Independent Test**: Remove Mission Charter section from spec and rerun analyzer; expect CRITICAL findings referencing the missing section.

**Acceptance Scenarios**:

1. **Given** all 10 Charter sections are present, **When** analyzer executes, **Then** it confirms compliance in the manifest.
2. **Given** missing manifest or validation logs, **When** analyzer runs, **Then** it marks the feature as non-compliant with remediation steps.

---

### Edge Cases

- Feature directory missing `plan.md` or `tasks.md`.
- Sections intentionally not applicable (must be removed, not left empty).
- Excess findings (>50) require overflow summary.
- Analyzer executed on stale Constitution version.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The analyzer MUST verify the existence and completeness of spec, plan, and tasks files generated for the feature.
- **FR-002**: The analyzer MUST produce a findings table categorizing issues into Duplication, Ambiguity, Underspecification, Constitution Alignment, Coverage Gaps, and Inconsistency.
- **FR-003**: The analyzer MUST map every functional and non-functional requirement to at least one task or flag the lack of coverage.
- **FR-004**: The analyzer MUST detect missing Mission Charter sections and Constitution mandates, labeling them CRITICAL in the report.
- **FR-005**: The analyzer MUST output a coverage summary table enumerating each requirement key, task linkage, and notes.
- **FR-006**: The analyzer MUST generate a JSON compliance manifest conforming to the Mission Charter schema v1.0.0 and record validation status.
- **FR-007**: The analyzer MUST operate read-only, never modifying source artifacts, and place outputs under `specs/<id>/analysis/`.

### Non-Functional Requirements

- **NFR-001**: Runtime MUST remain under 3 minutes for feature directories containing up to 200 tasks on Apple M1 Max hardware.
- **NFR-002**: Repeated analyzer runs on unchanged inputs MUST yield identical findings and manifest (deterministic output).
- **NFR-003**: Logs MUST include timestamp, feature ID, issue counts, and exit status for auditability.
- **NFR-004**: Analyzer MUST handle Markdown sections with international characters without data loss.

### Key Entities *(include if feature involves data)*

- **RequirementRecord**: Captures requirement key, description, originating section (spec or plan), and priority.
- **TaskRecord**: Represents a task ID, description, phase, parallel marker, and referenced file paths.
- **Finding**: Structured object containing category, severity, location references, summary, and remediation guidance.
- **ManifestEntry**: JSON structure linking charter element compliance flags to document locations and validation notes.

## Success Criteria *(mandatory)*

- **SC-001**: ≥95% of functional requirements in analyzed specs report at least one mapped task (coverage) or are explicitly flagged.
- **SC-002**: 100% of Mission Charter sections and manifest validations are checked each run, with CRITICAL severity assigned on failure.
- **SC-003**: Analyzer report is generated within 3 minutes for directories up to 200 tasks, enabling inclusion in CI pipelines.
- **SC-004**: Reviewers report ≤5% false positives in Critical/High findings across pilot features, indicating meaningful signal.

### Assumptions

- Feature directories follow templates generated by `/speckit.specify`, `/speckit.plan`, and `/speckit.tasks`.
- Researchers have already populated spec, plan, and tasks with initial content before running the analyzer.
- Constitution and Mission Charter files present in repository root represent the current authoritative versions.

### Dependencies

- Mission Charter manifest schema (`MISSION_CHARTER.md`) and validator script `tools/validate_charter.py`.
- Constitution stored at `z-sandbox/.specify/memory/constitution.md`.
- Existing logging infrastructure under `logs/`.
