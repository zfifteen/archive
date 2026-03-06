# API Reference

Complete API reference documentation for the Z Framework.

## Overview

This section provides detailed API documentation for all Z Framework modules and functions.

## Core Modules

### Z5DEnhancedPredictor
- **Module**: `src.core.z_5d_enhanced`
- **Description**: Enhanced Z_5D predictor with calibrated parameters

### GeodesicMapper  
- **Module**: `src.core.geodesic_mapping`
- **Description**: Geometric resolution and prime density enhancement

### BaselinePredictor
- **Module**: `src.core.z_baseline`
- **Description**: Baseline PNT+dilation implementation

## Functions

### Core Functions
- `z_5d_prediction(k)`: Generate Z5D prediction for value k
- `compute_density_enhancement(primes)`: Calculate density enhancement for prime list
- `golden_ratio_transform(n, k)`: Apply golden ratio transformation

### Validation Functions
- `bootstrap_validation()`: Statistical bootstrap validation
- `cross_domain_correlation()`: Cross-domain correlation analysis
- `performance_benchmark()`: Performance benchmarking

## Usage Examples

```python
from src.core.z_5d_enhanced import Z5DEnhancedPredictor
from src.core.geodesic_mapping import GeodesicMapper

# Initialize predictors
z5d = Z5DEnhancedPredictor()
geodesic = GeodesicMapper()

# Generate predictions
prediction = z5d.z_5d_prediction(100000)
enhancement = geodesic.compute_density_enhancement([2, 3, 5, 7, 11])
```

## See Also

- [Framework Documentation](../framework/README.md)
- [Getting Started Guide](../guides/getting-started.md)
- [Examples](../examples/README.md)