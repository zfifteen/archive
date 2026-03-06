# Installation Guide

This document provides instructions for installing the Z Framework with Spinor Geodesic Curvature functionality.

## Quick Installation

### Using pip with pyproject.toml (Recommended)

```bash
# Clone the repository
git clone https://github.com/zfifteen/unified-framework.git
cd unified-framework

# Install in development mode with all dependencies
pip install -e .

# Verify installation
python test_dependencies.py
```

### Using requirements.txt (Alternative)

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation  
python test_dependencies.py
```

## Verification

After installation, verify everything works:

```bash
# Run the spinor geodesic demonstration
python demo_spinor_geodesic.py

# Run comprehensive tests
python -m pytest src/tests/test_spinor_geodesic.py -v

# Validate CI artifacts
python validate_ci_artifacts.py
```

## Dependencies

The framework requires:

### Core Dependencies
- **qutip~=5.2.0** - Quantum Toolbox for spinor operations
- **numpy~=2.3.2** - Numerical computing foundation
- **scipy~=1.16.1** - Scientific computing library
- **matplotlib~=3.10.5** - Plotting and visualization
- **mpmath~=1.3.0** - High-precision arithmetic
- **sympy~=1.14.0** - Symbolic mathematics

### Additional Dependencies
- **pandas~=2.3.1** - Data analysis and manipulation
- **scikit-learn~=1.7.1** - Machine learning tools
- **statsmodels~=0.14.5** - Statistical modeling
- **pytest~=8.4.1** - Testing framework
- **biopython>=1.83,<2.0** - Biological sequence analysis
- **nltk** - Natural language processing
- **sentence-transformers** - Semantic embedding models

## Hardware Requirements

- **RAM**: Minimum 4GB, recommended 8GB for large parameter sweeps
- **CPU**: Multi-core recommended for statistical validation
- **GPU**: Optional, CUDA support available through PyTorch backend

## Troubleshooting

### Common Issues

1. **QuTiP installation fails**:
   ```bash
   # Install QuTiP dependencies first
   pip install cython numpy scipy
   pip install qutip
   ```

2. **CUDA errors with PyTorch**:
   ```bash
   # Install CPU-only version if no GPU
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Import errors**:
   ```bash
   # Ensure proper installation
   pip install -e . --force-reinstall
   ```

## Development Installation

For development work:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run full test suite
pytest
```

## Version Compatibility

- **Python**: 3.8 or higher
- **NumPy**: 2.x series (pinned ~=2.3.2)
- **SciPy**: 1.x series (pinned ~=1.16.1)
- **QuTiP**: 5.x series (pinned ~=5.2.0)

The version pins ensure numerical stability and reproducible results across different environments.