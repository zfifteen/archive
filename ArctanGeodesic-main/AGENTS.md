 # Repository Guidelines
 
 This document provides guidelines for contributing to the ArctanGeodesic repository, a Python library for arctan identities and geodesic mappings, with implementations in C and Java.
 
 ## Project Structure & Module Organization
 
 The repository follows a modular structure:
 - `src/`: Source code organized by language (e.g., `src/python/arctangeodesic/` for the main Python package).
 - `tests/`: Unit and integration tests mirroring source structure.
 - `examples/`: Sample scripts demonstrating usage.
 - `benchmarks/`: Code for performance evaluations.
 - `docs/`: Documentation, including classical references and related frameworks.
 - `lab/` and `context/`: Experimental files and additional context.
 - Root files like `README.md`, `LICENSE`, and generated assets (e.g., `test_certs/`) for project metadata and demos.
 
 Modules in `src/python/arctangeodesic/` use standard Python packaging.
 
 ## Build, Test, and Development Commands
 
 This is a pure Python project with no formal build system:
 - Install dependencies: Use `pip install sympy mpmath` for symbolic and high-precision math validations (standard library suffices otherwise).
 - Run tests: `python -m pytest tests/` (requires pytest: `pip install pytest`).
 - Run examples: `python examples/example_script.py`.
 - Development: Edit files in `src/`, test interactively with `python -c "import sys; sys.path.insert(0, 'src/python'); from arctangeodesic import module"`.
 
 ## Coding Style & Naming Conventions
 
 Adhere to PEP8 for Python code:
 - Indentation: 4 spaces, no tabs.
 - Naming: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
 - Line length: 79 characters.
 - No enforced linting/formatting tools; optionally use `black` for consistency: `black src/`.
 
 For C/Java, follow language-specific standards (e.g., Google C++ Style for C).
 
 ## Testing Guidelines
 
 Use pytest for testing:
 - Test files in `tests/`, named `test_module.py` corresponding to `src/python/arctangeodesic/module.py`.
 - Function naming: `test_function_name()`.
 - Coverage: Target 80%+; measure with `pytest --cov=arctangeodesic --cov-report=html`.
 - Include edge cases for mathematical computations and validations.
 
 ## Commit & Pull Request Guidelines
 
 - Commits: Use descriptive messages starting with a verb (e.g., "Add geodesic mapping function"). Keep changes focused.
 - Pull Requests: Provide a clear title and description, link related issues, include code examples or screenshots for demos. Squash trivial commits.
 
 ## Security & Configuration Tips
 
 Given the cryptographic elements (e.g., RSA, certificates):
 - Never commit private keys or sensitive data; use `generate_weak_certs.py` only for testing.
 - Validate inputs to prevent injection; use secure random for keys.
 - Configure environments securely; avoid exposing certs in public repos.
