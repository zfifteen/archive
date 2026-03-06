# Copilot Instructions for z-sandbox

## Architecture Overview
This is a high-velocity research repository pushing the boundaries of integer factorization using advanced geometric techniques. The primary focus is on the factorization of large RSA numbers, including RSA-260 and RSA-2048, by developing and applying novel methods like high-precision fractional comb sampling, Z5D prediction with Lorentz Dilation, and curvature-adaptive geodesic resolution.

The framework combines Java for core algorithms and Python for analysis and scripting.

- **Java (`java/`)**: Core factorization algorithms using Riemannian geometry, Monte Carlo/QMC integration, torus embeddings, and Z5D curvature (κ(n) = d(n) * ln(n+1) / e²). High-precision components are implemented in Java.
- **Python (`python/`, `files/`)**: Core Python source code for factorization, Z5D prediction, geometric methods, target generation, batch processing, statistical analysis, and RSA validation.
- **Docs (`docs/`)**: Research notes, implementation summaries, and validation reports.
- **Tests (`tests/`)**: Unit and integration tests, including `test_lorentz_dilation.py`. JUnit for Java, pytest for Python.
- **Build (`build.gradle`)**: Gradle build file for Java components.

Data flows from Python generators to Java factorizers and then to Python validators, with CSV/JSON used for data interchange.

## Key Workflows
- **Build**: `./gradlew build` (Java), `pip install mpmath sympy numpy` (Python).
- **Test**: `./gradlew test` (Java), `python -m pytest` (Python, with coverage via pytest-cov).
- **Debug**: Logs in `logs/`, plots in `plots/`, use `java -Djava.util.logging.config.file=logging.properties` for verbose output.
- **Factorization Demo**: `python3 python/rsa260_z5d_runner.py --dps 2000 --k 0.30 --use-z5d-prior --adaptive-step --line-search` for the latest RSA-260 geometric factorization.
- **Integration Tests**: `PYTHONPATH=python python3 tests/test_lorentz_dilation.py` for Lorentz Dilation, `PYTHONPATH=python python3 tests/test_gva_128.py` for GVA on 128-bit targets.
- **RSA Validation**: Run `python/factor_256bit.py` on generated targets from `python/generate_256bit_targets.py`.

## Coding Conventions
- **Math Axioms**: Always use Z = A(B/c) with c=invariant (e.g., e² for curvature), κ(n)=d(n)*ln(n+1)/e², θ'(n,k)=φ*((n mod φ)/φ)^k (k≈0.3). Validate empirically with mpmath (precision <1e-16).
- **Precision**: Java uses BigDecimal for ultra-high scale; Python uses mpmath for high-precision floats, sympy for symbolic.
- **Imports**: Java: `import java.math.BigDecimal;`, Python: `import sympy, numpy, mpmath`.
- **Error Handling**: Use ValueError for invalid inputs (e.g., n≤0), log warnings for approximations.
- **Testing**: Unit tests in `tests/`, integration in `python/`, require reproducible RNG (seed=42).
- **Mission Charter Compliance**: All deliverables (specs, PRs, research notes, implementation summaries, reports, plans, guides) MUST include the 10 charter elements defined in `MISSION_CHARTER.md`. Validate with `tools/validate_charter.py` before finalizing. Templates available in `docs/templates/`.

## Integration Patterns
- **Cross-Language**: Java exports results to CSV; Python reads for analysis (e.g., `pandas.read_csv`).
- **Dependencies**: Gradle for Java (BigDecimal, logging), pip for Python (sympy, numpy, mpmath).
- **External Tools**: GMP-ECM for ECM factoring, integrated via subprocess in Python scripts.

## Implementation Guidelines
You are an advanced coding assistant optimized for a local development environment on a MacBook Pro with an Apple M1 Max chip (ARM64 architecture).

### Environment Awareness:
- **Architecture**: All code must be compatible with ARM64.
- **Performance**: Leverage parallelization and GPU acceleration where possible.
- **Efficiency**: Be mindful of battery and power consumption.

### Tool Usage Guidelines:
- **Code Execution**: Use the stateful Python 3.12.3 REPL environment.
- **Web and Search**: Keep queries concise and targeted.
- **File Handling**: Be specific with file names and pages.
- **Efficiency**: Batch tool calls, chain tools logically, and avoid redundancy.

### Project-Specific Guidelines
- **Python Scripts**: Create in `src/python` subdirectories.
- **Gists**: Create in `gists` subdirectories, with emphasis on visualizations.
- **Java**: Ensure Gradle build succeeds before committing.
- **C99**: Create in `src/c` subdirectories.
- **Documentation (Markdown files)**: Default to the `docs/` structure for new docs; use root-level Markdown only for required context manifests discoverable by automation/LLMs (e.g., `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `RULES.md`):
  - `docs/core/` - Framework foundations (Z Framework axioms, coordinate geometry)
  - `docs/methods/geometric/` - GVA, elliptic billiards, conic sections
  - `docs/methods/monte-carlo/` - QMC, RQMC, low-discrepancy sampling
  - `docs/methods/z5d/` - Z5D factorization techniques
  - `docs/methods/other/` - Other methods (Pollard, perturbation, hash bounds)
  - `docs/implementations/` - Build guides, integration summaries (IMPLEMENTATION_SUMMARY_*.md)
  - `docs/validation/by-size/` - Results by size (40bit, 64bit, 128bit, 256bit, RSA)
  - `docs/validation/reports/` - Victory reports, breakthrough studies
  - `docs/guides/` - Quickstarts, usage guides (*_QUICKSTART.md, *_README.md, *_GUIDE.md)
  - `docs/project/` - Build plans, PR reviews, issue tracking
  - `docs/security/` - TRANSEC protocol, cryptography (SECURITY*.md, TRANSEC*.md)
  - `docs/research/` - Exploratory analysis, research papers, RFCs

## Gemini Interaction Guidelines
- The "Project-Specific Guidelines" apply to all projects.
- Default output mode is 500 characters; only give full details when asked.
- Never show code or markdown output; always display modified files instead.
- Use the `gh` tool as the primary means of interacting with Git and GitHub.

## Pointers
- **Parent map**: `../GEMINI.md`
- **Siblings**: `../transec/GEMINI.md`, `../unified-framework/GEMINI.md`
- **Mission Charter**: `../MISSION_CHARTER.md` (10-point deliverable standard)

Reference: `docs/GOAL.md` for goals, `docs/IMPLEMENTATION_SUMMARY_256BIT.md` for pipeline examples.
