---

description: "Task list for Initial Analysis feature implementation"

---

# Tasks: Initial Analysis

**Input**: Design documents from `/specs/001-initial-analysis/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Each user story includes mandatory failing tests (Gradle + pytest) per constitution; only mark `[P]` when the task can run in parallel without dependency conflicts.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Core CLI + modules under `tools/` (e.g., `tools/initial_analysis.py`, `tools/analysis/*.py`)
- Tests under `tests/analysis/`, `tests/integration/`, `tests/regression/`
- Docs & schemas under `docs/methods/initial-analysis/`
- Feature outputs under `specs/001-initial-analysis/analysis/`

## Constitution Hooks

- [ ] T001 Add invariant validation helper enforcing `Z`, `κ(n)`, `θ'(n,k)` checks (1e-16 tolerance) in `tools/analysis/validators/invariants.py`
- [ ] T002 Implement deterministic precision + RNG seed 42 configuration module in `tools/analysis/config.py`
- [ ] T003 Define structured logging schema and rotation policy in `logs/initial-analysis/README.md`
- [ ] T004 Publish CSV/JSON schema + Mission Charter manifest doc in `docs/methods/initial-analysis/schema.md`

## Phase 1: Setup (Shared Infrastructure)

- [ ] T005 Create analysis package scaffold (`tools/analysis/__init__.py`, `tools/analysis/__main__.py`)
- [ ] T006 Add CLI entrypoint stub with argparse wiring in `tools/initial_analysis.py`
- [ ] T007 Document and pin `markdown-it-py` dependency in `requirements.txt`
- [ ] T008 Scaffold analysis test suite directories (`tests/analysis/__init__.py`, `tests/analysis/fixtures/__init__.py`)

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T009 Implement dataclasses `RequirementRecord`, `TaskRecord`, `Finding`, `ManifestEntry` in `tools/analysis/models.py`
- [ ] T010 Build deterministic Markdown parser utilities in `tools/analysis/parsers.py`
- [ ] T011 Create severity rules loader backed by `docs/methods/initial-analysis/rules.yaml` in `tools/analysis/rules.py`
- [ ] T012 Configure JSON logging helper and sink setup in `tools/analysis/logging_config.py`
- [ ] T013 Seed reusable sample feature fixtures under `tests/analysis/fixtures/sample_feature/`

## Phase 3: User Story 1 - Research Lead Requests Readiness Signal (Priority: P1) 🎯 MVP

**Goal**: Provide a CLI that inspects completed spec/plan/tasks artifacts and produces readiness findings plus coverage summary for decision makers.  
**Independent Test**: Execute `python tools/initial_analysis.py --feature specs/sample-feature` and confirm a Markdown report + manifest are generated with CRITICAL findings on missing artifacts.

### Tests for User Story 1 (MANDATORY - write first) ⚠️

- [ ] T014 [P] [US1] Write failing CLI argument + artifact presence tests in `tests/analysis/test_initial_analysis_cli.py`
- [ ] T015 [P] [US1] Add end-to-end regression test ensuring report generation for fixture feature in `tests/integration/test_initial_analysis_cli.py`

### Implementation for User Story 1

- [ ] T016 [US1] Implement CLI orchestration + argument validation in `tools/initial_analysis.py`
- [ ] T017 [P] [US1] Build artifact loader that resolves absolute paths and raises `ValueError` in `tools/analysis/artifact_loader.py`
- [ ] T018 [US1] Implement findings aggregator + Markdown report writer in `tools/analysis/report.py`
- [ ] T019 [US1] Wire analyzer outputs (report, manifest, logs) into `specs/<feature>/analysis/` directory creation logic

## Phase 4: User Story 2 - Spec Author Reviews Coverage Mapping (Priority: P2)

**Goal**: Ensure every functional/non-functional requirement is mapped to tasks, with CSV exports that highlight gaps.  
**Independent Test**: Run analyzer on fixture where one requirement lacks tasks; expect coverage summary marking `has_task=false` plus entry in findings table.

### Tests for User Story 2 (MANDATORY - write first) ⚠️

- [ ] T020 [P] [US2] Create failing unit tests for coverage map generation in `tests/analysis/test_requirement_mapping.py`
- [ ] T021 [P] [US2] Add CSV/JSON export tests covering missing-task flags in `tests/analysis/test_coverage_export.py`

### Implementation for User Story 2

- [ ] T022 [US2] Implement coverage computation engine in `tools/analysis/coverage.py`
- [ ] T023 [US2] Build CSV + JSON exporters referencing `docs/methods/initial-analysis/coverage-schema.md`
- [ ] T024 [P] [US2] Integrate coverage results into report rendering + table formatting in `tools/analysis/report.py`
- [ ] T025 [US2] Update documentation with coverage interpretation guide in `docs/methods/initial-analysis/coverage-schema.md`

## Phase 5: User Story 3 - Compliance Reviewer Needs Charter Evidence (Priority: P3)

**Goal**: Guarantee Mission Charter checks, manifest generation, validator execution, and structured logging for audits.  
**Independent Test**: Remove a charter section from fixture spec, run analyzer, and confirm CRITICAL severity plus manifest entry with `present=false`.

### Tests for User Story 3 (MANDATORY - write first) ⚠️

- [ ] T026 [P] [US3] Write failing manifest + charter detection tests in `tests/analysis/test_manifest_generation.py`
- [ ] T027 [P] [US3] Add logging output verification tests in `tests/analysis/test_logging_output.py`

### Implementation for User Story 3

- [ ] T028 [US3] Implement Mission Charter manifest builder in `tools/analysis/manifest.py`
- [ ] T029 [US3] Implement charter section detector + constitution gate checks in `tools/analysis/charter_checks.py`
- [ ] T030 [P] [US3] Add validator invocation + exit handling in `tools/analysis/cli_runner.py`
- [ ] T031 [US3] Configure structured logging pipeline and document usage in `specs/001-initial-analysis/quickstart.md`

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T032 Document analyzer quickstart validation steps and sample commands in `specs/001-initial-analysis/quickstart.md`
- [ ] T033 Capture sample analyzer output (`report.md`, `analysis_manifest.json`) for reference in `specs/001-initial-analysis/analysis/`
- [ ] T034 Record final validation evidence (pytest + validator logs) in `specs/001-initial-analysis/verification.md`

## Dependencies & Execution Order

- Setup (Phase 1) must finish before Foundational work begins.  
- Foundational tasks (Phase 2) block all user stories because they provide parsers, models, and fixtures.  
- User Story order: **US1 (P1) → US2 (P2) → US3 (P3)**. Later stories rely on CLI + report scaffolding from US1, and coverage logic from US2 feeds compliance outputs in US3.  
- Polish phase executes after all desired stories are complete to finalize documentation and artifacts.

## Parallel Execution Examples

- During Constitution Hooks, T001–T004 can run concurrently because they touch independent files.  
- In Setup, T005/T006 serialize, but T007 and T008 can proceed in parallel once the package scaffold exists.  
- Within US1, tasks tagged `[P]` (T014, T015, T017) may run simultaneously after Foundational completion. Similar parallelism applies to `[P]` tasks in US2 and US3 (tests before implementation).  
- CSV export integration (T024) can start as soon as coverage engine (T022) exposes interfaces; logging + validator work (T030–T031) can overlap after manifest builder (T028) lands.

## Implementation Strategy

1. **MVP (US1)**: Deliver CLI that validates artifact presence, generates findings + coverage summary stubs, and writes manifest placeholders.  
2. **Increment 2 (US2)**: Add full coverage mapping, CSV/JSON exports, and richer reporting to unblock spec authors.  
3. **Increment 3 (US3)**: Layer on Mission Charter enforcement, manifest schema compliance, and structured logging to satisfy compliance reviewers.  
4. **Polish**: Capture sample outputs, finalize quickstart + verification logs, and prep for `/speckit.implement`.
