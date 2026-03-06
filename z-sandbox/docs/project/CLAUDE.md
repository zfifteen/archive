# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

z-sandbox is a high-velocity research repository focused on integer factorization using advanced geometric techniques. The primary goal is factorization of large RSA numbers (RSA-260, RSA-2048) through novel methods including:
- High-precision fractional comb sampling
- Z5D prediction with Lorentz Dilation
- Curvature-adaptive geodesic resolution
- Randomized Quasi-Monte Carlo (RQMC) integration achieving O(N^(-3/2+ε)) convergence
- Geodesic Validation Assault (GVA) with torus embeddings

The framework combines Java for core high-performance algorithms and Python for research, analysis, and rapid prototyping.

## Build and Test Commands

### Java Build System (Gradle)
```bash
# Standard build and test
./gradlew build                    # Compile and run tests
./gradlew test                     # Run unit tests only
./gradlew integrationTest          # Long RSA experiments (opt-in, 8GB heap)
./gradlew jacocoTestReport         # Generate coverage report

# Specific test tags
./gradlew test -Pgroups=bigdecimal # Run only BigDecimal tests

# Custom tasks
./gradlew demo                     # Ultra-high scale demo
./gradlew gva                      # Java GVA factorization demo
./gradlew ladder                   # Run rungs 200-260 benchmark
./gradlew rsa260                   # Best builder on RSA-260 with checkpointing
```

### Python Testing
```bash
# Install dependencies first
pip install -r python/requirements.txt

# Run pytest
python -m pytest                   # All tests
python -m pytest -v                # Verbose output
python -m pytest -m "not slow"     # Skip slow tests
python -m pytest tests/test_lorentz_dilation.py  # Specific test

# Integration tests (with PYTHONPATH)
PYTHONPATH=python python3 tests/test_lorentz_dilation.py
PYTHONPATH=python python3 tests/test_gva_128.py

# Run specific Python demos
python3 python/rsa260_z5d_runner.py --dps 2000 --k 0.30 --use-z5d-prior --adaptive-step --line-search
python3 python/examples/transformational_demo.py
```

### CI/CD
The repository uses GitHub Actions with self-hosted runners:
```yaml
# Workflow: .github/workflows/ci.yml
# Runs on: push to main, pull requests
# Tasks: ./gradlew -q test jacocoTestReport
```

## Architecture and Code Organization

### High-Level Structure
```
z-sandbox/
├── python/              # Python research code (175+ files)
│   ├── *.py            # Core modules (flat structure)
│   ├── examples/       # Demonstrations and tutorials
│   ├── experiments/    # Research experiments
│   ├── geom/          # Geometric utilities
│   ├── security/      # TRANSEC encryption protocol
│   ├── visualizations/# Plotting and analysis
│   └── z_correction/  # Z5D correction modules
├── src/
│   ├── main/java/     # Java production code
│   └── test/java/     # JUnit tests
├── tests/             # Python pytest suite (73+ files)
├── docs/              # Research documentation (140+ files)
├── build.gradle       # Gradle build configuration
└── pytest.ini         # Pytest configuration
```

### Key Python Modules
Core factorization and geometric methods are in `python/` (flat namespace):
- **Z5D Framework**: `advanced_z5d_factorization.py`, `high_scale_z5d_validation.py`, `demo_z5d_rsa.py`
- **GVA (Geodesic Validation Assault)**: `gva_factorize.py`, `hybrid_gva_z5d.py`, `parameter_sweep_gva.py`
- **Monte Carlo/QMC**: `monte_carlo.py`, `qmc_engines.py`, `benchmark_qmc_899.py`, `benchmark_oracle_qmc.py`
- **RQMC Control**: `rqmc_control.py`, `rqmc_photonic.py`
- **Pollard's Rho**: `pollard_gaussian_monte_carlo.py`
- **Geometric Primitives**: `barycentric.py`, `coordinate_geometry.py`, `conic_sections.py`
- **Arctan Geodesics**: `arctan_geodesic_primes.py`
- **RSA Challenges**: `rsa260_repro.py`, `benchmark_rsa_challenges.py`

### Java Architecture
Java code (in `src/main/java/unifiedframework/`) implements:
- High-precision algorithms using `BigDecimal` for ultra-high scale computations (up to 10^1233)
- Core factorization with Riemannian geometry, torus embeddings
- Z5D curvature: κ(n) = d(n) * ln(n+1) / e²
- Candidate builders: ZNeighborhood, ResidueFilter, HybridGcd, MetaSelection, GVA strategies
- RSA challenge validation harness (RSA-100 to RSA-250)

### Data Flow
1. **Python generators** create targets and parameters
2. **Java factorizers** perform high-precision computations
3. **Python validators** analyze results via CSV/JSON interchange
4. Logs in `logs/`, plots in `plots/`, results in `results/`

## Mathematical Axioms (Z Framework)

All implementations must follow these core axioms:
```
Z = A(B/c)                          # c = invariant (e.g., e² for curvature)
κ(n) = d(n) * ln(n+1) / e²         # Z5D curvature
θ'(n,k) = φ * ((n mod φ)/φ)^k      # k ≈ 0.3 (geodesic exponent)
```

**Validation Requirements**:
- Empirical precision < 1e-16 (use `mpmath` with appropriate `dps`)
- High-precision: `mpmath` for Python (dps=50+), `BigDecimal` for Java
- Reproducible RNG (seed=42 for tests)

## Development Patterns

### Python Script Organization
- **New prototypes**: Create in subdirectory under `python/` (though main modules are currently flat)
- **Gists (public demos)**: Create in subdirectory under `gists/` with emphasis on 2D/3D visualizations
- **Keep artifacts together**: All related files in same directory

### Documentation (Markdown files)
NEVER create .md files in repository root. Always use `docs/` structure:
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

### Java Development
- **Always ensure Gradle build succeeds** before committing
- Use `BigDecimal` for ultra-high scale arithmetic
- JUnit 5 for tests (Jupiter API)
- Code coverage via JaCoCo

### Testing Strategy
- **Java**: JUnit tests in `src/test/java/unifiedframework/`
  - Unit tests run via `./gradlew test`
  - Integration tests tagged with `@Tag("integration")`
  - Tag-based filtering: `-Pgroups=bigdecimal`
- **Python**: pytest tests in `tests/`
  - Marker for slow tests: `@pytest.mark.slow`
  - Deselect slow: `-m "not slow"`
  - PYTHONPATH setup: `PYTHONPATH=python python3 tests/test_*.py`

### Precision and Imports
**Java**:
```java
import java.math.BigDecimal;
import org.apache.commons.math3.*;
```

**Python**:
```python
import mpmath      # High-precision floats
import sympy       # Symbolic math
import numpy       # Numerical arrays
from mpmath import mp
mp.dps = 50        # Decimal places (adjust as needed)
```

### Error Handling
- Use `ValueError` for invalid inputs (e.g., n ≤ 0)
- Log warnings for approximations
- Guard against division by zero, domain violations

### Environment Awareness (Apple Silicon M1 Max)
- **ARM64 architecture**: All code must be compatible with aarch64
- **Performance**: Leverage 8 performance cores + 2 efficiency cores via multiprocessing/threading
- **Memory**: 32 GB RAM supports large-scale computations
- **GPU**: Integrated GPU (32 cores) - consider Metal backend for TensorFlow/PyTorch if applicable
- **Dependencies**: Use Homebrew for macOS tools, native ARM builds preferred over Rosetta 2

## Common Workflows

### Running RSA-260 Factorization
```bash
python3 python/rsa260_z5d_runner.py --dps 2000 --k 0.30 --use-z5d-prior --adaptive-step --line-search
```

### Running GVA Experiments
```bash
# Python GVA on 128-bit targets
PYTHONPATH=python python3 tests/test_gva_128.py

# Java GVA demo
./gradlew gva
```

### Batch Factorization
```bash
# Generate 256-bit targets
python3 python/generate_256bit_targets.py

# Factor them
python3 python/factor_256bit.py
```

### Benchmarking
```bash
# Java benchmarks
./gradlew ladder                    # Rungs 200-260
./gradlew rsa260                    # RSA-260 with best builder

# Python benchmarks
python3 python/benchmark_rsa_challenges.py
python3 python/benchmark_oracle_qmc.py
```

### Transformational RQMC Demo
```bash
PYTHONPATH=python python3 python/examples/transformational_demo.py
```

## Key Research Concepts

### RQMC (Randomized Quasi-Monte Carlo)
- Achieves O(N^(-3/2+ε)) convergence (vs O(N^(-1/2)) for standard MC)
- 32× fewer samples for same accuracy on smooth problems
- Implemented in `rqmc_control.py`, `rqmc_photonic.py`

### GVA (Geodesic Validation Assault)
- Torus embeddings with Riemannian geometry
- Success rates: 64-bit: 12%, 128-bit: 5%, 256-bit: >0%
- Enhanced with Epstein zeta functions over ℤ[i] (Gaussian integers)

### Z5D Framework
- Five-dimensional geometric projection for factorization
- Adaptive k-tuning (0.3 ± 0.01 based on variance feedback)
- Parallel QMC-biased Pollard's Rho with multiprocessing
- 40-55% success on 256-bit semiprimes

### TRANSEC Protocol
- Time-synchronized encryption for zero-RTT messaging
- Prime optimization: 25-88% curvature reduction
- Implemented in `python/security/`

## Documentation

- **Research notes**: `docs/` (140+ files)
- **Implementation summaries**: `docs/IMPLEMENTATION_SUMMARY_*.md`
- **Quick references**: `docs/256BIT_QUICK_REFERENCE.md`
- **Agent guidelines**: `.github/agents/z-sandbox-agent.md` (detailed operating procedures)
- **GEMINI.md**: Guidelines for Gemini AI interaction (short output mode, use `gh` tool)

## Dependencies

### Python (python/requirements.txt)
- mpmath>=1.3.0
- numpy>=2.0.0
- scipy>=1.13.0
- sympy>=1.13.0
- pandas>=2.2.0
- matplotlib>=3.9.0
- PyNaCl>=1.6.0
- cryptography>=42.0.0
- plotly>=5.18.0
- qutip>=4.7.0

### Java (build.gradle)
- Java 17
- JUnit Jupiter 5.11.0
- Apache Commons Math3 3.6.1
- JMH 1.37 (microbenchmarking)
- Jackson (CSV/JSON)

## Output and Artifacts

- **Logs**: `logs/` directory
- **Plots**: `plots/` directory
- **Results**: `results/` directory, CSV files in root
- **Performance logs**: `z5d_performance_log.csv` (uploaded to CI artifacts)
- **Coverage reports**: `build/reports/jacoco/` after `jacocoTestReport`
