# Code Standards

## Overview

This document outlines the coding standards and style guidelines for the Z Framework project.

## Python Code Style

### General Guidelines
- Follow PEP 8 style guidelines
- Use 4 spaces for indentation
- Maximum line length of 88 characters (Black compatible)
- Use descriptive variable and function names

### Type Hints
- Use type hints for all function parameters and return values
- Import types from `typing` module when needed

### Documentation
- Use docstrings for all functions, classes, and modules
- Follow Google-style docstring format

### High-Precision Mathematics
- Use `mpmath` with `dps=50` for high-precision calculations
- Import `mpmath as mp` for consistency

## Code Organization

### Module Structure
- Place core mathematical functions in `src/core/`
- Place validation code in `src/validation/`
- Place visualization code in `src/visualization/`

### Testing
- Write unit tests for all core functions
- Place tests in `tests/` directory
- Use descriptive test names

## Examples

### Function Definition
```python
import mpmath as mp
from typing import List, Tuple

def golden_ratio_transform(n: int, k: float) -> float:
    """Apply golden ratio transformation to integer n.
    
    Args:
        n: Integer to transform
        k: Curvature parameter
        
    Returns:
        Transformed value using golden ratio
    """
    phi = (1 + mp.sqrt(5)) / 2
    return phi * ((n % phi) / phi) ** k
```

### High-Precision Setup
```python
import mpmath as mp
mp.mp.dps = 50  # Set precision to 50 decimal places
```

## See Also

- [Contributing Guidelines](guidelines.md)
- [Code of Conduct](code-of-conduct.md)