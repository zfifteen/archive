# Z5D Stability Enhancement Documentation

## Overview

This document describes the stability enhancements added to the Z5D framework to address Issue #431: "Hidden Instability in High-Order Z5D Approximations". These enhancements provide robust monitoring and validation mechanisms to detect and prevent numerical instability before it becomes problematic.

## Key Features

### 1. Precision Monitoring System

**Purpose**: Detect numerical precision degradation for extremely large N values and automatically recommend precision scaling.

**Implementation**: 
- `_detect_precision_degradation()` function tests current vs higher precision computations
- Automatic precision scaling when degradation detected
- Warning system for potential numerical issues

**Usage**:
```python
from z_framework.discrete.z5d_predictor import z5d_prime

# Enable precision monitoring (default for k > 10^6)
result = z5d_prime(1e9, enable_precision_monitoring=True)

# Manual precision testing
from z_framework.discrete.z5d_predictor import _detect_precision_degradation
degradation_detected, recommended_dps, error_magnitude = _detect_precision_degradation(1e10)
```

### 2. Enhanced Statistical Validation

**Purpose**: Provide rigorous cross-validation for statistical significance claims, especially around critical correlation thresholds like r ≈ 0.93.

**Implementation**:
- Bootstrap confidence interval estimation (1000 samples by default)
- Outlier-robust correlation analysis
- Multiple validation criteria for statistical significance

**Usage**:
```python
from z_framework.discrete.z5d_predictor import _enhanced_statistical_validation

# Test correlation robustness
validation = _enhanced_statistical_validation(
    values1, values2, 
    correlation_threshold=0.93,
    significance_level=0.01
)

print(f"Correlation: {validation['correlation']:.3f}")
print(f"Bootstrap CI: {validation['bootstrap_ci']}")
print(f"Significance validated: {validation['significance_validated']}")
```

### 3. Non-Euclidean Perturbation Detection

**Purpose**: Identify when linear invariance assumptions break down under non-Euclidean perturbations.

**Implementation**:
- Linearity analysis in log-log space
- Residual pattern detection (autocorrelation, heteroscedasticity)
- Recommendation engine for addressing perturbations

**Usage**:
```python
from z_framework.discrete.z5d_predictor import _detect_nonlinear_perturbations

# Analyze for perturbations
result = _detect_nonlinear_perturbations(k_values, predictions)

print(f"Linearity score: {result['linearity_score']:.3f}")
print(f"Perturbations detected: {result['perturbation_detected']}")
print(f"Recommendation: {result['recommendation']}")
```

### 4. Comprehensive Stability Analysis

**Purpose**: Unified analysis combining all stability checks for production readiness assessment.

**Implementation**:
- Integrated precision, statistical, and perturbation analysis
- Overall stability scoring (0-1 scale)
- Risk level assessment and recommendations

**Usage**:
```python
from z_framework.discrete.z5d_predictor import comprehensive_stability_analysis

# Full stability assessment
results = comprehensive_stability_analysis(
    k_values, 
    true_primes=known_primes,  # optional
    enable_all_checks=True
)

print(f"Stability score: {results['stability_score']:.3f}")
print(f"Risk level: {results['overall_risk_level']}")
print(f"Recommendations: {results['recommendations']}")
```

## Enhanced Z5D Function Parameters

The main `z5d_prime()` function now includes additional stability parameters:

```python
z5d_prime(
    k,                              # Input k values
    c=None,                         # Dilation parameter (optional)
    k_star=None,                    # Curvature parameter (optional)
    auto_calibrate=True,            # Auto parameter selection
    precision_threshold=None,       # High-precision threshold
    force_backend=None,             # Force numpy/mpmath backend
    enable_precision_monitoring=True,    # NEW: Precision monitoring
    enable_perturbation_detection=False  # NEW: Perturbation detection
)
```

## Production Usage Guidelines

### 1. Basic Usage with Safety Features

```python
# Recommended for production use
result = z5d_prime(
    large_k_values,
    enable_precision_monitoring=True,      # Detect precision issues
    enable_perturbation_detection=False    # Disable for performance
)
```

### 2. Comprehensive Analysis Before Deployment

```python
# Run before production deployment
stability_results = comprehensive_stability_analysis(
    test_k_values,
    true_primes=validation_data,
    enable_all_checks=True
)

if stability_results['overall_risk_level'] == 'HIGH':
    print("⚠️ Review required before deployment")
    for flag in stability_results['risk_flags']:
        print(f"  - {flag}")
```

### 3. Monitoring Critical Correlations

```python
# For validating statistical claims
validation = _enhanced_statistical_validation(
    predicted_values,
    true_values,
    correlation_threshold=0.93,
    significance_level=0.01
)

if not validation['significance_validated']:
    print("⚠️ Statistical significance concerns detected")
    for warning in validation['warning_flags']:
        print(f"  - {warning}")
```

## Performance Considerations

### Precision Monitoring
- **Overhead**: Minimal for k < 10^6, moderate for larger k
- **Recommendation**: Enable by default, disable only for performance-critical applications

### Perturbation Detection
- **Overhead**: Moderate computational cost for analysis
- **Recommendation**: Enable for validation/testing, consider disabling for production

### Comprehensive Analysis
- **Overhead**: Significant for large datasets
- **Recommendation**: Use for pre-deployment validation, not real-time processing

## Configuration Constants

```python
# Precision monitoring constants
DEFAULT_PRECISION_DPS = 50           # Default mpmath precision
MAX_PRECISION_DPS = 200              # Maximum precision before warning
PRECISION_DEGRADATION_THRESHOLD = 1e-12  # Error threshold for precision increase

# Statistical validation constants
CORRELATION_BOOTSTRAP_SAMPLES = 1000  # Bootstrap samples for CI estimation

# Precision switching threshold
DEFAULT_PRECISION_THRESHOLD = 1e12   # k > 10^12 switches to mpmath
```

## Warning Interpretation

### Precision Warnings
```
"Precision degradation detected at k=1.00e+09 (error magnitude: 1.23e-13). 
Recommended precision: 75 dps. Consider using higher precision for k >= 1.00e+09."
```
**Action**: Consider increasing mpmath precision for better accuracy.

### Statistical Warnings
```
"p-value 1.23e-02 >= 0.01"
"High bootstrap variability (std=0.067)"
```
**Action**: Review sample size, check for outliers, validate correlation claims.

### Perturbation Warnings
```
"Non-linear perturbations detected: Strong non-linear effects detected. 
Consider non-linear calibration or segmented regression. Linearity score: 0.678"
```
**Action**: Review calibration parameters, consider non-linear modeling approaches.

## Backward Compatibility

All new features are **completely backward compatible**:
- Existing code continues to work unchanged
- New parameters have sensible defaults
- Warning system is non-intrusive
- Performance impact is minimal when features are disabled

## Testing

Comprehensive test suite available in `tests/test_z5d_stability_enhancement.py`:

```bash
# Run stability enhancement tests
python -m pytest tests/test_z5d_stability_enhancement.py -v

# Run demonstration script
python scripts/z5d_stability_demo.py
```

## References

- **Issue #431**: "Hidden Instability in High-Order Z5D Approximations"
- **Z5D Predictor Documentation**: `src/z_framework/discrete/z5d_predictor.py`
- **Validation Results**: `docs/research/validation.md`