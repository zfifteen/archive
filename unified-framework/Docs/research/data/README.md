# Research Data

Research datasets and data management for the Z Framework.

## Overview

This directory contains datasets, data processing scripts, and data management protocols for Z Framework research.

## Dataset Categories

### Prime Number Datasets
- **Small Primes**: Primes up to 10⁶ for development and testing
- **Large Primes**: Primes up to 10⁹ for large-scale validation
- **Prime Gaps**: Gap sequences and statistical distributions

### Mathematical Constants
- **Riemann Zeta Zeros**: High-precision zero locations and spacings
- **Golden Ratio**: High-precision φ calculations and derived values
- **Physical Constants**: c, e, π with validation-grade precision

### Validation Data
- **Bootstrap Samples**: Resampled datasets for statistical validation
- **Cross-Validation**: Partitioned datasets for robustness testing
- **Reference Results**: Known mathematical results for verification

## Data Management

### Storage Standards
- **Format**: JSON, CSV, HDF5 for different data types
- **Precision**: Full precision maintenance for mathematical data
- **Metadata**: Complete provenance and processing history
- **Version Control**: Git LFS for large datasets

### Quality Control
- **Validation**: Automated data quality checks
- **Documentation**: Complete data dictionaries
- **Reproducibility**: Documented data generation procedures
- **Integrity**: Checksums and validation protocols

### Access Protocols
- **Programmatic**: API access for computational workflows
- **Direct**: File system access for analysis scripts
- **Remote**: Download protocols for external validation
- **Cached**: Local caching for performance optimization

## Usage Guidelines

### Data Loading
```python
from src.data import load_dataset

primes = load_dataset('primes_1e9')
zeros = load_dataset('riemann_zeros')
```

### Data Validation
```python
from src.data import validate_dataset

validation_result = validate_dataset(data, schema='prime_sequence')
```

## See Also

- [Validation Protocols](../validation.md)
- [Experiments](../experiments/README.md)
- [API Documentation](../../api/README.md)