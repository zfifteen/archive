# Test Finding Datasets

This directory contains validation datasets, example data files, test harnesses, and reference datasets used for testing and validation.

## Contents

### Dataset Types
- **Test Harnesses**: Curated datasets for consistent testing
- **Prime Number Sets**: Reference prime sequences and coordinates
- **Validation Data**: Known good results for verification
- **Example Datasets**: Sample data for demonstration purposes
- **Benchmark Data**: Performance testing datasets

### File Formats
- **NPY Files**: NumPy arrays for mathematical computations
- **TXT Files**: Plain text datasets and prime sequences
- **CSV Files**: Structured tabular validation data
- **JSON Files**: Metadata and structured test parameters

## Organization

Datasets are organized by:
- Purpose (validation, testing, benchmarking)
- Mathematical domain (primes, curves, quantum)
- Data size and computational scope

## Usage

Datasets can be loaded using standard Python libraries:
```python
import numpy as np
import pandas as pd

# Load coordinate arrays
coords = np.load('test-finding/datasets/test_harness_coords.npy')

# Load prime sequences
with open('test-finding/datasets/test_harness_primes.txt', 'r') as f:
    primes = f.read().splitlines()
```

## Data Integrity

- All datasets include validation checksums where applicable
- Source and generation methodology documented
- Version control for dataset updates
- Cross-references to generating scripts maintained

## LLM Usage Notes

- Clear naming conventions indicate dataset purpose
- File formats chosen for programmatic accessibility  
- Metadata preserved for reproducibility
- Documentation links to usage examples