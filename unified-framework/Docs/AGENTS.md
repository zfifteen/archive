# Repository Guidelines

## Project Structure & Module Organization
- Core Python lives in `src/` with domain packages such as `src/core`, `src/geometry`, and `src/discrete`.
- Shared utilities are under `src/analysis`, `src/validation`, and CLI entry points in `src/prediction.py`.
- Experiments (e.g., `hash-bounds/`) reside in `experiments/`; reproducible scripts go in `scripts/`.
- Tests belong in `tests/` or `src/tests/`; large datasets live in `data/` or `datasets/`; generated outputs should go to `reports/` or `artifacts/`.

## Build, Test, and Development Commands
- `python -m pip install -e .[dev]` – install the package plus tooling for local development.
- `make` – build the M1-targeted C backends and supporting executables in `src/c`.
- `python -m pytest tests src/tests -q` – run the Python unit suites quickly.
- `make test` – executes C and Python precision harnesses.
- `make bench` – benchmark the hot path predictors.
- `./comprehensive_test.sh` & `python validate_framework_regression.py` – run full end-to-end validations before merging cross-domain changes.

## Coding Style & Naming Conventions
- Python uses Black’s 88-column format (`python -m black src tests`) and Flake8 (`python -m flake8 src tests`).
- Adopt snake_case for modules/functions, CamelCase for classes, and UPPER_SNAKE_CASE for constants; 4-space indentation everywhere.
- Type hints are mandatory for public APIs; check with `python -m mypy src`.
- C sources follow the repository’s K&R brace style with an invariants block at the top.

## Testing Guidelines
- PyTest discovers `test_*.py` files, `Test*` classes, and `test_*` functions; mirror that naming.
- Cover success paths and failure guards, especially around normalization constraints (e.g., invalid inputs for `Z = A(B/c)`).
- Share expensive fixtures via `tests/conftest.py`; keep golden datasets minimal.
- Integrate new C harnesses into the Makefile so `make test` stays authoritative.

## Commit & Pull Request Guidelines
- Format commit messages as `<scope>: <imperative>` (e.g., `geometry: add hyperbolic validator`) and reference issues (`#123`) when applicable.
- PRs should describe intent, list validation commands executed, attach relevant artifacts from `runs/` or `artifacts/`, and flag configuration or data-contract changes before requesting review.

## Security & Configuration Tips
- Store secrets in environment variables; update `.env.example` when adding keys.
- Avoid committing large uncompressed binaries; datasets belong in `data/` or `datasets/` with provenance notes in `README`/`INSTALL.md`.
- Strip PII from artifacts and version generated reports under dated subfolders in `reports/` or `artifacts/`.
