# Experiment Setup Template

## Prime Statistics Standards (Issue #696)

This template codifies the statistical testing requirements for the Z Framework to ensure robust, reliable results. All statistical experiments should follow these guidelines to avoid noise and ensure meaningful signal detection.

## Statistical Testing Requirements

### K Value Standards

**Minimum Statistical Threshold: k ≥ 10⁵ (100,000)**

- **Rationale**: Small primes (k ≤ 10³) introduce noise due to:
  - Low prime density creating insufficient samples
  - Boundary effects distorting statistical measures  
  - Insufficient statistical power for reliable signal detection
  - Making them unreliable for predictive models like Z_5D

**Optimal Range: k ≈ 10⁵ to 10⁶ (100,000 to 1,000,000)**

- **Benefits**: Essential for robust signals while balancing:
  - Computational feasibility with meaningful variance
  - Prime gaps ~ln k ≈ 11.5-13.8 providing adequate resolution
  - Validation of enhancements like ~15% prime density via geodesic θ'(n, k* ≈ 0.3)
  - Bootstrap confidence intervals [14.6%, 15.4%] with statistical rigor

### Statistical Testing Contexts

The following analysis contexts **require** k ≥ 10⁵:

1. **Density Enhancement Analysis**
   - Prime concentration measurements
   - Geodesic clustering validation
   - Bootstrap confidence interval calculations

2. **Z_5D Predictor Validation**  
   - Accuracy measurements (<0.01% error requirement)
   - Error envelope validation (≤200 ppm)
   - Comparative performance analysis

3. **Prime Gap Analysis**
   - Gap distribution measurements  
   - Variance analysis
   - Correlation studies

4. **Bootstrap Confidence Testing**
   - Statistical significance validation
   - Confidence interval calculations
   - Resampling validation

5. **Geodesic Clustering Analysis**
   - Curvature effect measurements
   - Bin concentration analysis
   - Enhancement percentage validation

6. **Correlation Analysis**
   - Prime-zeta zero correlations
   - Cross-domain validation
   - Signal detection studies

## Implementation Guidelines

### Parameter Validation

Use the built-in validation functions from `src.core.params`:

```python
from src.core.params import validate_k_statistical, validate_k_nth

# For statistical analysis contexts
k_value = validate_k_statistical(k_input, context="density_enhancement")

# For nth prime calculations in statistical contexts  
k_nth = validate_k_nth(k_input, context="z5d_validation")
```

### Experimental Design

**Required Elements:**

1. **Sample Size**: N ≥ 10⁶ integers for robust statistics
2. **Bootstrap Resamples**: B ≥ 1,000 for confidence intervals  
3. **Random Seed**: Fixed seed for reproducibility
4. **k Value**: k ≥ 10⁵ for all statistical tests
5. **Documentation**: Clear parameter specifications and context

**Example Setup:**

```python
# Statistical experiment configuration
EXPERIMENT_CONFIG = {
    'k_min': 100000,           # Minimum k for statistical validity
    'k_max': 1000000,          # Maximum k for optimal range
    'sample_size': 1000000,    # N ≥ 10⁶ for robust statistics
    'bootstrap_samples': 1000, # B ≥ 1,000 for CI calculation  
    'bins': 20,                # Equal-probability bins
    'seed': 42,                # Fixed for reproducibility
    'context': 'density_enhancement'  # Statistical context
}
```

### Reporting Standards

**Required Reporting:**

- k value and validation status
- Sample size (N) and bootstrap iterations (B) 
- Statistical context and methodology
- Warning acknowledgment if k < 10⁵ used
- Confidence intervals with [low, high] bounds
- Reproducibility metadata (seed, parameters)

**Example Output:**

```
Prime Density Enhancement Validation
====================================
k_value: 100,000 (✓ meets statistical standards)
Sample Size: N=1,000,000 integers
Bootstrap Samples: B=1,000 resamples  
Context: density_enhancement
Enhancement: 15.2% [14.6%, 15.4%] (95% CI)
Seed: 42 (reproducible)
```

## Validation and Compliance

### Automated Checks

The framework automatically:
- Validates k ≥ 10⁵ for statistical contexts
- Issues warnings for k < 10⁵ usage
- Provides guidance on optimal ranges
- Documents violations for review

### Manual Review Required

For experiments using k < 10⁵:
- Explicit justification required
- Non-statistical use case confirmation
- Alternative methodology documentation  
- Results labeled as preliminary/exploratory

## Historical Context

**Issue #696 Resolution**: These standards address empirical findings showing that:
- Mid-range testing (k ≈ 10⁵ to 10⁶) provides balanced computation/variance
- Prime gaps at this scale (~ln k ≈ 11.5-13.8) offer meaningful statistical resolution
- Geodesic θ'(n, k* ≈ 0.3) transformations achieve validated 15% density enhancement
- Bootstrap confidence intervals [14.6%, 15.4%] require adequate sample density

**Framework Integration**: Synchronized with:
- `src/core/params.py` parameter definitions
- Validation functions and warning systems
- Documentation standards and reporting templates
- Z_5D predictor accuracy requirements (<0.01% error for k ≥ 10⁵)

---

**Attribution**: Created by Dionisio A. Lopez ("Big D"), Z Framework Developer  
**Version**: 1.0 (Issue #696 Resolution)  
**Updated**: December 2024