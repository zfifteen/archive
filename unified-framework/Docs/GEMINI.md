# GEMINI — You are here: `unified-framework`

**Purpose**: A unified mathematical framework for quantum and number-theoretic systems using 5-dimensional geometric principles, with advanced Stadlmann distribution level integration. This is the main, parent repository from which other child repos have been spawned.

**Note (2025-11-23)**: Previous biological claims have been retracted following falsification experiment `codon_mutation_falsification_v1`. θ = 0.525 remains validated exclusively in number-theoretic applications.

## TL;DR Build/Run
```bash
# Install Python dependencies
pip install mpmath numpy

# Clone and install
git clone https://github.com/zfifteen/unified-framework
cd unified-framework
pip install -e .

# Run Z5D Prime Predictor demo
python gists/z5d_prime_predictor_gist.py
```

## Common Tasks (copy/paste)

*   Predict the billionth prime: `python gists/z5d_prime_predictor_gist.py 1000000000`
*   Build and run all tests: `./gradlew test`
*   Run RSA challenge tests: `./gradlew test --tests "unifiedframework.TestRSAChallenges"`

## Key Files & Dirs (minimal map)

*   `src/` — Core Python and Java source code for the framework.
*   `docs/` — Extensive documentation on mathematical details, Z5D, etc.
*   `gists/` — Quick start scripts and demos.
*   `examples/` — Comprehensive examples of framework usage.
*   `tests/` — Unit and integration tests.

## Pointers

*   **Parent map**: [`../GEMINI.md`](../GEMINI.md)
*   **Children/Related**: [`../z-sandbox/GEMINI.md`](../z-sandbox/GEMINI.md), [`../ArctanGeodesic/GEMINI.md`](../ArctanGeodesic/GEMINI.md), [`../wave-crispr-signal/GEMINI.md`](../wave-crispr-signal/GEMINI.md)

## Ask Gemini (do this, not that)

*   “Explain the core principles of the Z5D framework as implemented here.”
*   “Show me how the Stadlmann distribution level integration enhances prime prediction.”
*   “Find the implementation of `predict_prime` in the Z5D Prime Predictor.”
