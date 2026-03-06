# User Guide

Comprehensive user guide for the Z Framework.

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Basic Usage
```python
from src.core.z_5d_enhanced import Z5DEnhancedPredictor

z5d = Z5DEnhancedPredictor()
prediction = z5d.z_5d_prediction(100000)
print(f"Z5D prediction: {prediction}")
```

## Framework Concepts

### Universal Form
The Z Framework is based on the universal form Z = A(B/c), where:
- A: Frame-dependent measured quantity
- B: Rate or frame shift  
- c: Universal invariant (speed of light)

### Prime Analysis
The framework achieves conditional prime density improvement under canonical benchmark methodology using:
- Golden ratio transformations: θ'(n,k) = φ·{n/φ}^k
- Optimal curvature parameter: k* ≈ 0.3
- High-precision arithmetic (mpmath, dps=50)

## Advanced Usage

### Statistical Validation
```python
from src.validation import bootstrap_validation

results = bootstrap_validation(samples=1000)
print(f"Confidence interval: {results.confidence_interval}")
```

### Visualization
```python
from src.visualization import plot_enhancement

plot_enhancement(primes, k_values)
```

## Best Practices

- Always use high-precision arithmetic for critical calculations
- Validate results with statistical methods
- Document empirical findings with confidence intervals
- Follow the scientific methodology outlined in the framework

## See Also

- [Getting Started](getting-started.md)
- [Best Practices](best-practices.md)
- [API Reference](../api/reference.md)