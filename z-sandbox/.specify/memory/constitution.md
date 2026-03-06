# z-sandbox Constitution

Authoritative, enforceable rules for development, documentation, testing, and agent conduct in the z-sandbox repository. This Constitution and the Mission Charter together govern all deliverables and workflows.

## Authority & Scope
- Mission Charter (MISSION_CHARTER.md) and this Constitution are binding. Charter defines the 10 deliverable elements; this Constitution defines project-wide MUST/SHOULD rules and quality gates.
- Applies to all contributors (humans and agents) and all deliverables (specs, plans, code, PRs, reports, research notes).

## Core Principles (NON-NEGOTIABLE)

### P1. Charter Compliance
- All deliverables MUST include and satisfy the 10 Charter elements.
- Every deliverable MUST pass `python tools/validate_charter.py <file>` in strict mode.

### P2. Mathematical Invariants & Precision
- Invariants are immutable: `Z = A(B / e²)`, `κ(n) = d(n)·ln(n+1)/e²`, `θ'(n,k) = φ·((n mod φ)/φ)^k`, k≈0.30.
- Numerical checks MUST use `mpmath` with tolerance < 1e-16.
- Invalid numeric inputs (e.g., n ≤ 0) MUST raise `ValueError` (Python) or equivalent.
- Java kernels MUST use BigDecimal for high precision; Python MUST use `mpmath`/`sympy`.

### P3. Determinism & Reproducibility
- RNG seeds MUST default to 42; deterministic output is required for unchanged inputs.
- Environments SHOULD match: Python 3.12.3; Java 11.0.16+ (ARM64-friendly on Apple M1 Max).
- Commands, versions, seeds, and expected outputs MUST be documented for reproduction.

### P4. Test-First Discipline
- TDD is REQUIRED: write tests first, see them fail, then implement.
- Unit tests live under `tests/`; integration tests MAY reference Java/Python boundaries.

### P5. Build/Test Gates (Local before Push)
- Before pushing or opening PRs, the following MUST pass locally:
  - `./gradlew build test`
  - `python -m pytest`
  - `python tools/validate_charter.py <deliverable>` for any docs/specs/PR bodies
- Any inability to run these MUST halt work and request remediation.

### P6. Documentation Governance
- Documentation MUST live under `docs/` (taxonomy respected: `docs/core/`, `docs/methods/*`, `docs/project/`).
- Allowed root context files: `AGENTS.md`, `RULES.md`, `MISSION_CHARTER.md`.
- Schemas and analyzer methods MUST reside under `docs/methods/<area>/` with deterministic column ordering for CSV/JSON.

### P7. Interfaces & Paths
- CLIs MUST expose text I/O (human + JSON) and be runnable offline by default.
- Standard env: `PYTHONPATH=python` (legacy) is supported; new modules SHOULD live in `tools/` or `python/`. Migration to `src/python` MAY be proposed with a plan.
- Cross-language exchange via CSV is RECOMMENDED; Python consumers SHOULD use `pandas.read_csv`.

### P8. Observability
- Structured logs MUST be written under `logs/` (feature tools under `logs/<tool>/`).
- Each run SHOULD record timestamp (ISO 8601 UTC), seeds, versions, and exit status.

### P9. Simplicity (YAGNI)
- Prefer the simplest implementation that satisfies requirements; avoid over-engineering and speculative abstractions.

### P10. Security, Legal, and Ethics
- No proprietary datasets auto-fetched; external sources MUST be cited per Charter.
- Secrets MUST NOT be committed or logged; use env vars; redact outputs.

## Development Workflow & Quality Gates
- Branch naming MUST follow `^[0-9]{3}-[a-z0-9-]+$` for feature work (e.g., `001-initial-analysis`).
- Feature specs live in `specs/<id>-<name>/` and MUST include `spec.md`, `plan.md`, and `tasks.md` before implementation.
- Analyzers and governance tools MUST operate read-only on source artifacts and write outputs to feature-local `analysis/` directories and `logs/`.
- Deterministic behavior MUST be verified via repeated runs; any non-determinism MUST be documented as Failure Knowledge with mitigation.

## Agent Output Policy
- Agents MUST honor Charter and this Constitution.
- Default agent output SHOULD be concise (≤500 characters) unless the user explicitly requests more.
- Agents MUST reference file paths and avoid dumping large code blocks unless solicited. For code changes, prefer repository diffs/patches.
- Agents MUST NOT propose commits that break local build/test gates.

## Governance
- Precedence: Mission Charter > this Constitution > other guidance. Conflicts with the Charter are CRITICAL and MUST be resolved by revising specs/plans/tasks (not by diluting Charter/Constitution).
- Amendments: Require version bump, rationale, and migration notes in a PR; update ratification dates below.
- Compliance: Reviewers MUST verify gates and Charter compliance. Complexity MUST be justified.

**Version**: 1.0.0 | **Ratified**: 2025-11-09 | **Last Amended**: 2025-11-09
