# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This directory contains 12 GitHub projects spanning mathematical frameworks, cryptography, bioinformatics, and specialized computing. The projects range from high-performance mathematical computing to Apple Silicon hardware research.

### Project Categories

**Mathematical Frameworks (Python + C):**
- `unified-framework`, `2025-08-13-unified-framework` - Z Framework for prime prediction and cross-domain analysis
- `lightprimes` - Holographic numberspace framework with neural forecasting
- `prime_curve` - Golden ratio-based prime clustering analysis
- `universal_frame_shift_transformer` - Frame shift observations and optimizations

**Bioinformatics (Python):**
- `crispr-wave`, `wave-crispr-signal` - Signal-theoretic DNA mutation analysis using complex-valued waveforms

**Security/Cryptography (Python + C++):**
- `Ciphey` - Automated decryption/decoding tool with AI

**Development Tools (Go):**
- `z-mcp-server` - MCP (Model Context Protocol) server tools

**Hardware Research (C/Assembly):**
- `z-amx` - Apple AMX instruction documentation and research

## Common Build Commands

### Universal Commands (Most Projects)
```bash
# Discover project type
find . -name "requirements.txt" -o -name "pyproject.toml" -o -name "go.mod" -o -name "Makefile" | head -1

# Check CI/CD setup
ls -la .github/workflows/
```

### Python Projects (Mathematical Frameworks, Bioinformatics)
```bash
# Standard workflow
pip install -r requirements.txt
python -m pytest tests/

# If Makefile present (unified-framework family)
make deps          # Install system dependencies (macOS Homebrew)
make               # Build C components
make test          # Run comprehensive tests
make clean         # Clean build artifacts
make bench         # Performance benchmarks

# For Poetry projects (Ciphey)
poetry install
poetry run pytest
```

### C/C++ Projects
```bash
# Build and test cycle
make deps && make && make test

# High-performance mathematical projects use MPFR/GMP
# Check for Apple Silicon optimizations on M1/M2 Macs
```

### Go Projects (z-mcp-server)
```bash
go mod tidy               # Update dependencies
go build ./cmd/...        # Build all commands
go test ./...             # Run tests
go run ./cmd/mcpcurl      # Run specific tool
```

## Architecture Patterns

### Mathematical Frameworks Architecture
- **Hybrid Python/C structure** for performance-critical calculations
- **High-precision arithmetic** using mpmath (dps=50) and MPFR (256-bit)
- **Apple Silicon optimizations** with AMX utilization
- **Parameter standardization** through `src/core/params.py`
- **Empirical validation** requirements with statistical rigor

**Key Components:**
```
project/
├── src/
│   ├── core/           # Fundamental framework components
│   ├── analysis/       # Mathematical analysis modules
│   └── applications/   # Practical applications
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── performance/   # Performance benchmarks
├── examples/          # Code examples and demos
├── scripts/           # Utility and build scripts
└── docs/             # Comprehensive documentation
```

### Scientific Computing Standards
- **Exact version pinning** in requirements.txt
- **Bootstrap confidence intervals** (1000+ resamples) for statistical claims
- **Empirical validation** distinguishing validated results from hypotheses
- **Cross-platform compatibility** with Apple Silicon considerations

### Bioinformatics (CRISPR/DNA Analysis)
- **Human genome data only** (GRCh38/hg38)
- **Strict nucleotide validation** (A/C/G/T/N for DNA, A/C/G/U/N for RNA)
- **Statistical rigor** with pre-registered endpoints and leakage control
- **Reproducibility requirements** with seed control and environment persistence

## Testing Strategies

### Python Testing
```bash
# Standard patterns
pytest tests/              # Basic test run
python -m pytest -v       # Verbose output
make test                  # Makefile-driven comprehensive tests

# Performance testing (mathematical projects)
make bench                 # Built-in benchmarks
```

### Test File Organization
- **Unit tests:** `tests/unit/test_*.py`
- **Integration tests:** `tests/integration/test_*.py`
- **Performance tests:** `tests/performance/test_*.py`
- **Test fixtures:** `tests/fixtures/`

### Scientific Validation Testing
- **Statistical hypothesis testing** (t-tests, p-values < 0.05)
- **Bootstrap confidence intervals** for all statistical claims
- **Cross-validation across scales** (N=10⁴ to 10⁷ minimum)
- **Reproducibility checks** with documented seeds and environments

## Key Development Patterns

### Dependency Management
- **Python:** Exact version pinning (e.g., `numpy==1.26.4`)
- **C/C++:** Homebrew-based on macOS (`make deps`)
- **Go:** Standard go.mod with semantic versioning
- **Virtual environments:** `.venv` directories present

### Parameter Standardization (Mathematical Projects)
```python
# Always import from centralized params
from src.core.params import (
    KAPPA_GEO_DEFAULT,    # Geodesic exponent (0.3)
    KAPPA_STAR_DEFAULT,   # Z_5D calibration (0.04449)
    validate_kappa_geo,   # Parameter validation
)

# Use standardized naming
# kappa_geo = 0.3     # Geodesic mapping exponent
# kappa_star = 0.04449 # Z_5D calibration parameter
```

### Apple Silicon Optimizations
- **Homebrew path detection** (`/opt/homebrew` vs `/usr/local`)
- **AMX instruction utilization** for matrix operations
- **Memory optimization** for high-precision calculations
- **Platform-specific compiler flags**

## Project-Specific Quick Starts

### unified-framework
```bash
make deps && make && make test    # Full build cycle
./bin/geodesic_z5d_search 37124508045065437 5  # Example usage
```

### Ciphey
```bash
poetry install && poetry run pytest
ciphey "encrypted_text_here"      # Usage example
```

### CRISPR/DNA Analysis Projects
```bash
# Validate with smoke test
make smoke                       # <5s validation
python proof_pack/quick_validation_demo.py  # ~2min demo

# Full validation suite
python proof_pack/run_validation.py
```

### z-mcp-server
```bash
go build ./cmd/mcpcurl && go test ./...
./mcpcurl --stdio-server-cmd="command" tools --help
```

## Quality Assurance

### Code Quality Standards
- **Black formatting** (88 character line limit)
- **Flake8 linting** compliance
- **MyPy type annotations**
- **isort import organization**

### Mathematical Precision Requirements
- **High-precision arithmetic** (mpmath dps=50, MPFR 256-bit)
- **Numerical stability** monitoring for large-scale computations
- **Guard conditions** for division by zero and domain validation
- **Performance regression testing** with benchmarks

### Scientific Rigor Requirements
- **Empirical validation** over hypothetical claims
- **Consistent notation** using universal Z = A(B/c) framework
- **Statistical significance** testing for all claims
- **Clear labeling** of validated vs. extrapolated results

## Documentation Requirements

### Structure
- **README.md:** Project overview and quick start
- **Technical docs:** In project-specific `docs/` directories
- **API documentation:** Auto-generated where applicable
- **Research notes:** In `docs/research/` subdirectories

### Scientific Documentation Standards
- **Mathematical foundations** with proper citations
- **Empirical validation** methodology and results
- **Parameter optimization** protocols and rationale
- **Reproducibility** instructions with environment specifications

## Apple Silicon Considerations

When working on M1/M2/M3/M4 Macs:
- Check for **AMX instruction optimizations** in mathematical projects
- Use **Homebrew paths** (`/opt/homebrew`) for dependencies
- Leverage **high memory capacity** for large-scale computations
- Consider **Metal compute shaders** for GPU acceleration opportunities

## Common Debugging Patterns

### Mathematical Projects
```bash
# Check precision settings
python -c "import mpmath; print(mpmath.mp.dps)"

# Verify parameter values
python -c "from src.core.params import *; print(KAPPA_GEO_DEFAULT)"

# Run minimal validation
make test | grep -E "(PASS|FAIL|ERROR)"
```

### Build Issues
```bash
# Check system dependencies (macOS)
brew list | grep -E "(mpfr|gmp|openmp)"

# Verify Python environment
pip list | grep -E "(numpy|scipy|mpmath)"

# Platform detection
uname -m && echo $PATH | tr ':' '\n' | grep -E "(homebrew|local)"
```

This guidance reflects the actual development patterns, build systems, and scientific rigor requirements found across the project portfolio.