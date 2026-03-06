# Research: Initial Analysis

## R1. Deterministic Markdown Parsing Strategy
- **Decision**: Use `mistune`-style tokenization implemented via the lightweight `markdown-it-py` parser
  configured for deterministic ordering, wrapped inside `tools/analysis/parsers.py`.
- **Rationale**: Provides structural access (headings, lists, tables) required for requirement/user-story
  extraction while remaining pure-Python and deterministic across runs.
- **Alternatives Considered**:
  - `beautifulsoup4` over HTML-converted Markdown — rejected due to extra conversion step and
    non-deterministic attribute ordering.
  - Regex-only parsing — brittle for nested lists and tables.

## R2. Coverage Mapping Data Model
- **Decision**: Represent requirements and tasks as `dataclasses` (`RequirementRecord`, `TaskRecord`)
  persisted in-memory, then exported to CSV for downstream analysis.
- **Rationale**: Aligns with spec entities, keeps objects type-safe, and simplifies mapping logic in
  `coverage.py`.
- **Alternatives Considered**:
  - Pandas DataFrame as primary structure — heavier dependency footprint for simple mapping.
  - JSON-only representation — harder to enforce validation and typing.

## R3. Severity Heuristics Calibration
- **Decision**: Encode severity thresholds as declarative rules (YAML file under
  `docs/methods/initial-analysis/rules.yaml`) and validate them through regression tests.
- **Rationale**: Keeps adjustments auditable, matches Mission Charter emphasis on transparency, and
  allows reviewers to tweak heuristics without editing code.
- **Alternatives Considered**:
  - Hard-coded constants inside Python — less flexible, harder to audit.
  - ML-based classifier — overkill for deterministic governance rules.

## R4. Log & Manifest Generation
- **Decision**: Use Python’s `logging` module with JSON formatter targeting `logs/initial-analysis/`
  plus a dedicated `manifest.py` helper emitting schema-compliant JSON.
- **Rationale**: Meets observability requirements, integrates with existing logging directories, and
  supports Mission Charter manifest validation.
- **Alternatives Considered**:
  - Custom plain-text logs — insufficient for downstream tooling.
  - External logging services — violates offline, read-only constraint.

## R5. Toolchain & Dependency Best Practices
- **Decision**: Depend only on repository-standard scientific libraries (`mpmath`, `sympy`, `numpy`,
  `pandas`) and add `markdown-it-py` for parsing; document any new dependency in `docs/methods/`.
- **Rationale**: Matches project guidance, ensures ARM64 compatibility, and keeps reproducibility.
- **Alternatives Considered**:
  - Introducing heavy NLP frameworks — unnecessary and increases runtime.
  - Writing custom Markdown parser — higher maintenance cost.

*All identified clarifications resolved; no outstanding NEEDS CLARIFICATION markers remain.*
