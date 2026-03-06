# AGENTS Playbook for z-sandbox

## Mission Profile
This repository advances high-precision integer factorization for RSA-scale targets (RSA-260, RSA-2048) through geometric methods: fractional comb sampling, Z5D prediction with Lorentz Dilation, and curvature-adaptive geodesic resolution. Java hosts the core factorization engine, while Python orchestrates generation, orchestration, validation, and analytics.

## System Topography
- **java/** – Riemannian-inspired factorization logic (BigDecimal arithmetic, Monte Carlo/QMC sampling, torus embeddings, κ(n) = d(n) · ln(n+1) / e²).
- **python/** & **files/** – Z5D predictors, geometric toolkits, batch pipelines, RSA verification.
- **docs/** – Theory notes, implementation reports, validation studies.
- **tests/** – JUnit (Java) and pytest (Python) suites such as `tests/test_lorentz_dilation.py`.
- **build.gradle** – Gradle coordination for Java targets.
- Data flow: Python generators → Java factorizers → Python validators (CSV/JSON interchange).

## Core Workflows
- **Build** – `./gradlew build` (Java); `pip install mpmath sympy numpy` (Python deps).
- **Test** – `./gradlew test`; `python -m pytest` (add `pytest-cov` for coverage).
- **Debug** – Inspect `logs/`, visualize in `plots/`, run Java with `-Djava.util.logging.config.file=logging.properties`.
- **Factorization Demo** – `python3 python/rsa260_z5d_runner.py --dps 2000 --k 0.30 --use-z5d-prior --adaptive-step --line-search`.
- **Integration Targets** – `PYTHONPATH=python python3 tests/test_lorentz_dilation.py` and `tests/test_gva_128.py`; validate RSA with `python/factor_256bit.py`.

## Coding Protocols
- **Mathematical invariants** – Maintain Z = A(B / c) (c = e²), κ(n) = d(n)·ln(n+1)/e², θ'(n,k) = φ*((n mod φ)/φ)^k with k ≈ 0.3; confirm via `mpmath` (<1e-16 tolerance).
- **Precision** – Java BigDecimal for high-precision kernels; Python uses `mpmath` and `sympy`.
- **Imports** – Java: `java.math.BigDecimal`; Python: `import sympy, numpy, mpmath`.
- **Errors** – Throw `ValueError` for invalid (n ≤ 0); log warnings for approximations.
- **Testing Discipline** – Store unit tests in `tests/`, integration in `python/`; fix RNG seeds (42).
- **Mission Charter** – All deliverables (specs, PRs, research notes, reports, plans) MUST conform to the 10-point Mission Charter (see `MISSION_CHARTER.md`). Use `tools/validate_charter.py` to verify compliance before submission.

## Integration Practices
- Cross-language exchange via CSV; Python consumes using `pandas.read_csv`.
- Manage Java deps with Gradle, Python with pip (sympy, numpy, mpmath).
- External accelerants: GMP-ECM invoked from Python subprocesses.

## Agent Operating Environment
- **Platform** – Apple M1 Max (ARM64); ensure language runtimes respect ARM builds.
- **Performance** – Prefer parallel/vectorized paths; mind thermal/battery cost.
- **Toolchain** – Default Python 3.12.3 REPL for execution; limit web/search chatter; batch file ops.

## Project-Specific Directives
- Python modules live under `src/python`.
- C99 artifacts placed in `src/c`.
- Visual gists belong in `gists/`.
- Always guarantee Gradle builds before proposing commits.
- Documentation must stay under `docs/` (see subdirectories for taxonomy, e.g., `docs/core/`, `docs/methods/*`, `docs/project/`), with root-level context files (e.g., `AGENTS.md`, `RULES.md`) allowed for LLM discovery.

## Automation Alignment
- Apply the project-specific layout rules across sibling projects.
- Default output limit: 500 characters (hard cap) unless the user explicitly requests more.
- Never print code to the user; do not include code blocks or snippets—reference file paths or describe changes instead.
- Prefer `gh` for Git/GitHub interactions when scripted tooling needs repository context.

## Reference Ledger
- **Parent map** – `GEMINI.md`
- **Siblings** – `transec/GEMINI.md`, `unified-framework/GEMINI.md`
- **Key docs** – `docs/GOAL.md`, `docs/IMPLEMENTATION_SUMMARY_256BIT.md`
- **Mission Charter** – `MISSION_CHARTER.md` (10-point deliverable standard)

## Active Technologies
- Python 3.12.3 (CLI + analysis pipeline); Java 11.0.16 indirectly via Gradle hooks + `mpmath` (tolerance checks), `sympy` (symbolic validation), `numpy` (001-initial-analysis)
- Local filesystem outputs (`specs/<id>/analysis/`) and structured logs in `logs/` (001-initial-analysis)

## Recent Changes
- 001-initial-analysis: Added Python 3.12.3 (CLI + analysis pipeline); Java 11.0.16 indirectly via Gradle hooks + `mpmath` (tolerance checks), `sympy` (symbolic validation), `numpy`
