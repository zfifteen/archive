# Implementation Plan: Initial Analysis

**Branch**: `001-initial-analysis` | **Date**: 2025-11-08 | **Spec**: [specs/001-initial-analysis/spec.md](spec.md)  
**Input**: Feature specification from `/specs/001-initial-analysis/spec.md`

**Note**: This plan prepares the analyzer workflow before `/speckit.tasks` validation.

## Summary

Build a deterministic analyzer that inspects `spec.md`, `plan.md`, and `tasks.md` for each feature,
highlighting coverage gaps, Constitution or Mission Charter violations, and producing a structured
report plus compliance manifest. The solution runs as a Python CLI under `tools/initial_analysis.py`,
parses Markdown into structured inventories, and emits Markdown + JSON artifacts under the feature
directory while remaining read-only toward source documents.

## Technical Context

**Language/Version**: Python 3.12.3 (CLI + analysis pipeline); Java 11.0.16 indirectly via Gradle hooks  
**Primary Dependencies**: `mpmath` (tolerance checks), `sympy` (symbolic validation), `numpy`
(deterministic sampling), `pandas` (table shaping), `pytest` (test harness)  
**Storage**: Local filesystem outputs (`specs/<id>/analysis/`) and structured logs in `logs/`  
**Testing**: `pytest` suites under `tests/analysis/` plus integration scenarios referencing
`tests/test_lorentz_dilation.py` data to ensure invariant detection  
**Target Platform**: Apple M1 Max (ARM64) dev machines and CI runners  
**Project Type**: Single repository tooling (Python CLI + supporting modules under `tools/`)  
**Performance Goals**: Complete analysis of up to 200 tasks in <3 minutes; produce reports <200 KB  
**Constraints**: Read-only access to specs/plans/tasks; deterministic RNG seed 42; CSV/JSON schemas
stored under `docs/methods/` for any exported summaries  
**Scale/Scope**: Supports forthcoming feature directories by default; tested against at least 10
historical specs for regression confidence

## Constitution Check

- **Invariant Coverage**: Analyzer does not alter invariants but must ensure every inspected spec
  restates `Z`, `κ(n)`, or `θ'(n,k)` where applicable and validates tolerance via `mpmath` 1e-16
  checks embedded in regression tests.
- **Precision Discipline**: All stochastic sampling (e.g., prioritizing findings) must fix RNG seed 42
  and raise `ValueError` with logged context for invalid or missing artifacts; CLI options expose the
  precision level for derived numeric summaries.
- **Testing Strategy**: TDD enforced through new `tests/analysis/test_requirement_mapping.py`,
  golden-file integration tests covering Markdown parsing, and regression suites triggered via
  `pytest` plus `./gradlew test` (ensuring Java-side compatibility for mixed flows).
- **Data Governance**: Inputs remain in `specs/<id>/`; analyzer exports CSV/JSON under
  `docs/methods/initial-analysis/` with deterministic column ordering so Python validators remain
  stable. Modules live under `tools/` with namespace-respecting imports.
- **Observability & Charter**: Structured logs streamed to `logs/initial-analysis/*.log` include
  feature ID, timestamps, seeds, and exit codes. Generated reports cite Mission Charter sections and
  attach validator output from `python tools/validate_charter.py <report>`.
- **Charter Sections & Manifest**: Plan, spec, and upcoming tasks keep all 10 sections. Analyzer
  emits `analysis_manifest.json` conforming to schema v1.0.0 and records PASS/FAIL status.

Gate Result: ✅ All Constitution mandates satisfied pre-design.

## Project Structure

### Documentation (this feature)

```text
specs/001-initial-analysis/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── analyzer.yaml
├── checklists/
│   └── requirements.md
└── tasks.md              # to be created by /speckit.tasks
```

### Source Code (repository root)

```text
tools/
├── __init__.py
├── initial_analysis.py        # CLI entrypoint
├── analysis/
│   ├── parsers.py
│   ├── coverage.py
│   ├── findings.py
│   └── manifest.py
logs/
└── initial-analysis/          # structured logs

tests/
├── analysis/
│   ├── test_requirement_mapping.py
│   ├── test_manifest_generation.py
│   └── fixtures/
│       └── sample_feature/
├── integration/
│   └── test_initial_analysis_cli.py
└── regression/
    └── test_historical_features.py
```

**Structure Decision**: Extend existing `tools/` namespace with dedicated `analysis` package to keep
CLI + helper modules isolated, while tests mirror package layout under `tests/analysis/`.

## Complexity Tracking

No Constitution violations anticipated; table intentionally empty.

### Post-Design Constitution Check

- Phase 0 research resolved all uncertainties without altering invariants.
- Phase 1 artifacts (data-model, contracts, quickstart, agent context) preserve deterministic
  precision, document CSV/JSON schemas, and maintain Mission Charter sections.

Gate Result: ✅ Ready to advance to `/speckit.tasks`.
