# Z-Sandbox: Research on Geometric Approaches to Integer Factorization

![Z-Sandbox Banner](https://github.com/zfifteen/z-sandbox/blob/main/docs/images/z-sandbox-banner.png?raw=true)

[![Build Status](https://img.shields.io/github/actions/workflow/status/zfifteen/z-sandbox/ci.yml?branch=main)](https://github.com/zfifteen/z-sandbox/actions)
[![License](https://img.shields.io/badge/License-Not%20Specified-lightgrey.svg)](https://github.com/zfifteen/z-sandbox)

This repository is a research environment for exploring novel geometric and number-theoretic approaches to integer factorization, with a focus on challenging RSA moduli.

## Core Concepts

This project is built on a foundation of several key mathematical and algorithmic ideas:

*   **Z-Framework:** A set of axioms defining a 5-dimensional geodesic space for mapping prime numbers and their properties. The core axioms include:
    *   `Z = A(B/c)` (Universal Invariant)
    *   `κ(n) = d(n) * ln(n+1) / e²` (Discrete Curvature)
    *   `θ'(n,k) = φ * ((n mod φ) / φ)^k` (Geometric Resolution)
*   **Geodesic Validation Assault (GVA):** A method that embeds numbers into a high-dimensional torus and uses Riemannian geometry to find factors by measuring geodesic distances.
*   **Quasi-Monte Carlo (QMC):** Advanced sampling techniques, including Sobol sequences and Owen scrambling, to reduce variance and improve the efficiency of stochastic searches for factors.

## Getting Started

### Prerequisites

*   Python 3.7+
*   Java 11+
*   Gradle

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/zfifteen/z-sandbox.git
    cd z-sandbox
    ```

2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running a Demo

To see the QMC factorization analysis in action, run the following command:

```bash
python scripts/qmc_factorization_analysis.py
```

## Repository Structure

*   `src/`: Core Java source code
*   `python/`: Python source code, including implementations of the core mathematical concepts
*   `scripts/`: Python scripts for running experiments and analyses
*   `docs/`: Detailed documentation of the various methods and research findings
*   `tests/`: Unit and integration tests for both Python and Java code
*   `tools/`: Utility tools including charter compliance validator

## Documentation

For a deep dive into the mathematical frameworks, experimental results, and implementation details, please refer to the extensive documentation in the `docs/` directory. The `docs/TOC.md` file provides a comprehensive table of contents.

For an overview of the project's context and goals, see `GEMINI.md`.

### Mission Charter
### Project Constitution
The project adheres to the Constitution at `.specify/memory/constitution.md`, outlining core principles including Empirical Validation First, Domain-Specific Forms, Geometric Resolution, and Style and Tools.
All deliverables in this repository must conform to the **10-Point Mission Charter** to ensure rigor, reproducibility, and consistency. See `MISSION_CHARTER.md` for detailed requirements and `docs/templates/` for compliant deliverable templates.

## Contributing

This is a research project, and contributions are welcome. Please open an issue to discuss any proposed changes. A formal `CONTRIBUTING.md` file will be added in the future.

**Note:** All contributions (PRs, specs, research notes, reports) must be charter-compliant. Use `python tools/validate_charter.py <your-file>` to validate your deliverables before submission.

## License

A `LICENSE` file has not yet been added to this repository.