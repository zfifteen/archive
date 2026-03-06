# Symbolic Axiom Derivation and Statistical Testing Integration

This document provides comprehensive documentation for the newly integrated SymPy-based symbolic axiom derivation and SciPy-based statistical testing modules in the Z Framework.

## Overview

The integration adds two major capabilities to the Z Framework:

1. **Symbolic Module** (`symbolic/`): SymPy-based symbolic derivation and manipulation of mathematical axioms
2. **Statistical Module** (`statistical/`): SciPy-based statistical hypothesis testing and validation

## Installation and Setup

### Prerequisites

```bash
pip3 install numpy pandas matplotlib mpmath sympy scikit-learn statsmodels scipy seaborn plotly
```

### Environment Setup

```python
# Set Python path for imports
export PYTHONPATH=/home/runner/work/unified-framework/unified-framework

# Or prefix commands when working outside repository root
PYTHONPATH=/home/runner/work/unified-framework/unified-framework python3 script.py
```

## Symbolic Module Usage

### Core Symbolic Derivations

#### Universal Invariance Axiom

```python
from symbolic.axiom_derivation import derive_universal_invariance

# Derive the universal invariance axiom Z = A(B/c)
result = derive_universal_invariance()

print("Universal form:", result['universal_form'])
print("Relativistic form:", result['relativistic_form'])
print("Discrete form:", result['discrete_form'])
print("Dimensional constraint:", result['dimensional_constraint'])
```

#### Curvature Formula Derivation

```python
from symbolic.axiom_derivation import derive_curvature_formula

# Derive κ(n) = d(n) * ln(n+1) / e²
curvature_result = derive_curvature_formula()

print("Curvature formula:", curvature_result['curvature_formula'])
print("5D curvature vector:", curvature_result['curvature_5d'])
print("Normalization factor:", curvature_result['normalization_factor'])
```

#### Golden Ratio Transformation

```python
from symbolic.axiom_derivation import derive_golden_ratio_transformation

# Derive θ'(n,k) = φ * {n/φ}^k
golden_result = derive_golden_ratio_transformation()

print("Golden ratio exact:", golden_result['phi_exact'])
print("Transformation formula:", golden_result['theta_prime_formula'])
print("Asymmetry measure:", golden_result['asymmetry_measure'])
```

#### e² Invariant from Trigonometric Limit

```python
from symbolic.axiom_derivation import derive_e_squared_trigonometric_limit

# Derive e² from canonical analytic limit
e_squared_result = derive_e_squared_trigonometric_limit()

print("Trigonometric expression:", e_squared_result['trigonometric_expression'])
print("Symbolic limit:", e_squared_result['symbolic_limit'])
print("Numerical value:", float(e_squared_result['symbolic_limit']))

# Demonstrate reproducible calculation
import sympy as sp
x = sp.symbols('x')
expr = sp.tan(sp.pi/4 + x)**(1/x)
limit_val = sp.limit(expr, x, 0)
print("Reproduced limit:", limit_val)  # e**2

# Numerical convergence test
convergence_points = [10**(-i) for i in range(3, 8)]
for point in convergence_points:
    numerical_value = float(expr.subs(x, point))
    print(f"x = {point}: {numerical_value}")
```

### Formula Manipulation

```python
from symbolic.formula_manipulation import (
    simplify_zeta_shift, expand_geometric_series, 
    transform_golden_ratio_expressions
)

# Simplify complex expressions
expression = "phi * ((n % phi) / phi) ** k"
simplified = simplify_zeta_shift(expression, target_form='factored')

# Expand for asymptotic analysis
series_result = expand_geometric_series(expression, order=5)

# Transform golden ratio expressions
golden_transform = transform_golden_ratio_expressions(expression, form='exact')
```

### Symbolic Verification

```python
from symbolic.verification import (
    verify_axiom_consistency, verify_dimensional_analysis,
    verify_golden_ratio_properties, comprehensive_symbolic_verification
)

# Verify axiom consistency
consistency = verify_axiom_consistency()
print("Axioms consistent:", consistency['is_consistent'])

# Verify dimensional analysis
dimensions = verify_dimensional_analysis()
print("Dimensional consistency:", dimensions['dimensional_consistency'])

# Comprehensive verification
verification = comprehensive_symbolic_verification()
print("Overall verification:", verification['verification_complete'])
```

## Statistical Module Usage

### Hypothesis Testing

#### Prime Enhancement Hypothesis

```python
from statistical.hypothesis_testing import test_prime_enhancement_hypothesis
import numpy as np
from sympy import isprime

# Generate test data
primes = [p for p in range(2, 1000) if isprime(p)]
composites = [n for n in range(4, 1000) if not isprime(n)][:len(primes)]

# Apply golden ratio transformation
phi = (1 + np.sqrt(5)) / 2
k = 0.3

def transform(n):
    return phi * ((n % phi) / phi) ** k

prime_transformed = [transform(p) for p in primes[:100]]
composite_transformed = [transform(c) for c in composites[:100]]

# Test hypothesis
result = test_prime_enhancement_hypothesis(prime_transformed, composite_transformed)

print("Hypothesis rejected:", result['hypothesis_test']['rejected_null'])
print("Enhancement significant:", result['hypothesis_test']['enhancement_significant'])
print("Cohen's d:", result['effect_sizes']['cohens_d'])
```

#### Optimal k Parameter Discovery

```python
from statistical.hypothesis_testing import test_optimal_k_hypothesis

# Test data with peak around k=0.3
k_values = np.linspace(0.1, 0.5, 20)
enhancement_values = 100 * np.exp(-10 * (k_values - 0.3)**2) + np.random.normal(0, 5, 20)

result = test_optimal_k_hypothesis(k_values, enhancement_values)

print("Optimal k exists:", result['hypothesis_test']['optimal_k_exists'])
print("Empirical k*:", result['empirical_results']['k_optimal_empirical'])
print("Fitted k*:", result['fitted_models']['quadratic']['k_optimal_fitted'])
```

#### Variance Minimization Testing

```python
from statistical.hypothesis_testing import test_variance_minimization

# Test against target variance σ ≈ 0.118
curvature_data = np.random.normal(0.5, 0.11, 1000)

result = test_variance_minimization(curvature_data)

print("Target achieved:", result['hypothesis_test']['target_achieved'])
print("Sample variance:", result['sample_statistics']['sample_variance'])
print("Within tolerance:", result['tolerance_test']['within_tolerance'])
```

### Distribution Analysis

```python
from statistical.distribution_analysis import (
    analyze_prime_distribution, fit_distribution_models, test_normality_assumptions
)

# Analyze prime gaps distribution
primes = [p for p in range(2, 10000) if isprime(p)]
prime_gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]

dist_analysis = analyze_prime_distribution(prime_gaps[:1000])
print("Best distribution:", dist_analysis['best_distribution']['name'])
print("AIC score:", dist_analysis['best_distribution']['aic'])

# Fit Gaussian Mixture Model
gmm_result = fit_distribution_models(prime_gaps[:500], model_type='gmm', n_components=3)
print("GMM components:", gmm_result['n_components'])
print("Log likelihood:", gmm_result['model_scores']['log_likelihood'])

# Test normality assumptions
normality = test_normality_assumptions(prime_gaps[:1000])
print("Overall recommendation:", normality['summary']['overall_recommendation'])
```

### Correlation Analysis

```python
from statistical.correlation_analysis import (
    correlate_zeta_zeros_primes, regression_analysis_enhancement
)

# Test zeta zeros - prime correlation
zeta_data = np.random.normal(0, 1, 100)
prime_data = 0.9 * zeta_data + 0.1 * np.random.normal(0, 1, 100)  # r ≈ 0.9

correlation_result = correlate_zeta_zeros_primes(zeta_data, prime_data)
print("Pearson correlation:", correlation_result['correlation_analysis']['pearson']['correlation'])
print("Claim supported:", correlation_result['documentation_validation']['claim_supported'])

# Regression analysis for k-enhancement relationship
k_vals = np.linspace(0.1, 0.5, 20)
enhancement_vals = 100 * np.exp(-10 * (k_vals - 0.3)**2)

regression_result = regression_analysis_enhancement(k_vals, enhancement_vals)
print("Best model:", regression_result['best_model']['name'])
print("R²:", regression_result['best_model']['details']['r_squared'])
```

### Bootstrap Validation

```python
from statistical.bootstrap_validation import (
    bootstrap_confidence_intervals, validate_reproducibility, 
    permutation_test_significance
)

# Bootstrap confidence intervals
data = np.random.normal(10, 2, 100)
ci_result = bootstrap_confidence_intervals(data, np.mean, n_bootstrap=1000)
print("95% CI:", ci_result['confidence_interval'])
print("Bootstrap bias:", ci_result['bootstrap_summary']['bias'])

# Reproducibility validation
def example_experiment(n=100):
    return np.mean(np.random.normal(5, 1, n))

repro_result = validate_reproducibility(example_experiment, n_replications=50)
print("Reproducible:", repro_result['reproducibility_assessment']['highly_reproducible'])

# Permutation test
group1 = np.random.normal(10, 2, 50)
group2 = np.random.normal(12, 2, 50)

perm_result = permutation_test_significance(group1, group2, n_permutations=1000)
print("Significant difference:", perm_result['test_results']['significant'])
print("Effect size:", perm_result['test_results']['effect_size'])
```

## Integration Examples

### Symbolic-Statistical Integration

```python
# 1. Derive transformation symbolically
from symbolic.axiom_derivation import derive_golden_ratio_transformation
golden_result = derive_golden_ratio_transformation()

# 2. Extract numerical parameters
phi_value = float((1 + np.sqrt(5)) / 2)
k_value = 0.3

# 3. Apply to real data
primes = [p for p in range(2, 1000) if isprime(p)]
transformed_primes = [phi_value * ((p % phi_value) / phi_value) ** k_value for p in primes[:100]]

# 4. Statistical validation
from statistical.distribution_analysis import analyze_prime_distribution
from statistical.bootstrap_validation import bootstrap_confidence_intervals

dist_analysis = analyze_prime_distribution(transformed_primes)
boot_ci = bootstrap_confidence_intervals(transformed_primes, np.mean)

print("Distribution analysis complete:", 'best_distribution' in dist_analysis)
print("Bootstrap CI:", boot_ci['confidence_interval'])
```

### End-to-End Validation Pipeline

```python
def complete_validation_pipeline():
    """Complete validation using both symbolic and statistical modules."""
    
    # Step 1: Symbolic derivation
    curvature_formula = derive_curvature_formula()
    golden_transform = derive_golden_ratio_transformation()
    
    # Step 2: Generate test data
    primes = [p for p in range(2, 1000) if isprime(p)][:100]
    composites = [n for n in range(4, 1000) if not isprime(n)][:100]
    
    # Step 3: Apply transformations
    phi = float((1 + np.sqrt(5)) / 2)
    k = 0.3
    
    prime_transformed = [phi * ((p % phi) / phi) ** k for p in primes]
    composite_transformed = [phi * ((c % phi) / phi) ** k for c in composites]
    
    # Step 4: Statistical validation
    enhancement_test = test_prime_enhancement_hypothesis(prime_transformed, composite_transformed)
    dist_analysis = analyze_prime_distribution(prime_transformed)
    bootstrap_ci = bootstrap_confidence_intervals(prime_transformed, np.mean)
    
    # Step 5: Compile results
    return {
        'symbolic_derivation': 'curvature_formula' in curvature_formula,
        'transformation_applied': len(prime_transformed) == len(primes),
        'enhancement_significant': enhancement_test['hypothesis_test']['enhancement_significant'],
        'distribution_analyzed': 'best_distribution' in dist_analysis,
        'bootstrap_valid': 'confidence_interval' in bootstrap_ci
    }

# Run complete pipeline
pipeline_result = complete_validation_pipeline()
print("Pipeline results:", pipeline_result)
```

## Usage Patterns and Best Practices

### 1. Symbolic Derivation Workflow

```python
# Standard workflow for symbolic analysis
def symbolic_analysis_workflow(expression):
    # 1. Derive symbolic form
    symbolic_result = derive_universal_invariance()
    
    # 2. Simplify and manipulate
    simplified = simplify_zeta_shift(expression)
    
    # 3. Verify consistency
    verification = verify_axiom_consistency()
    
    # 4. Extract numerical values for computation
    numerical_params = extract_numerical_parameters(symbolic_result)
    
    return {
        'symbolic': symbolic_result,
        'simplified': simplified,
        'verified': verification['is_consistent'],
        'parameters': numerical_params
    }
```

### 2. Statistical Validation Workflow

```python
# Standard workflow for statistical validation
def statistical_validation_workflow(data1, data2):
    # 1. Test hypotheses
    enhancement_test = test_prime_enhancement_hypothesis(data1, data2)
    
    # 2. Analyze distributions
    dist1 = analyze_prime_distribution(data1)
    dist2 = analyze_prime_distribution(data2)
    
    # 3. Bootstrap validation
    ci1 = bootstrap_confidence_intervals(data1, np.mean)
    ci2 = bootstrap_confidence_intervals(data2, np.mean)
    
    # 4. Correlation analysis
    correlation = correlate_zeta_zeros_primes(data1, data2)
    
    return {
        'hypothesis_test': enhancement_test,
        'distributions': (dist1, dist2),
        'confidence_intervals': (ci1, ci2),
        'correlation': correlation
    }
```

### 3. Error Handling and Robustness

```python
def robust_analysis(data):
    """Example of robust analysis with error handling."""
    results = {}
    
    try:
        # Symbolic analysis
        symbolic_result = derive_universal_invariance()
        results['symbolic'] = symbolic_result
    except Exception as e:
        results['symbolic_error'] = str(e)
    
    try:
        # Statistical analysis
        if len(data) >= 10:  # Minimum sample size
            dist_analysis = analyze_prime_distribution(data)
            results['distribution'] = dist_analysis
        else:
            results['distribution_error'] = 'Insufficient sample size'
    except Exception as e:
        results['distribution_error'] = str(e)
    
    try:
        # Bootstrap with adequate sample size
        if len(data) >= 20:
            bootstrap_result = bootstrap_confidence_intervals(data, np.mean, n_bootstrap=1000)
            results['bootstrap'] = bootstrap_result
        else:
            results['bootstrap_error'] = 'Sample too small for bootstrap'
    except Exception as e:
        results['bootstrap_error'] = str(e)
    
    return results
```

## Reproducibility Guidelines

### 1. Random Seed Management

```python
import numpy as np

# Set seeds for reproducible results
np.random.seed(42)

# For reproducible bootstrap
bootstrap_result = bootstrap_confidence_intervals(
    data, np.mean, n_bootstrap=1000
)

# For reproducible validation
validation_result = validate_reproducibility(
    experiment_function, n_replications=100
)
```

### 2. Parameter Documentation

```python
# Always document parameters used
analysis_parameters = {
    'golden_ratio_phi': float((1 + np.sqrt(5)) / 2),
    'curvature_exponent_k': 0.3,
    'target_variance': 0.118,
    'bootstrap_samples': 1000,
    'confidence_level': 0.95,
    'significance_level': 0.05
}

# Include in results for reproducibility
results['parameters'] = analysis_parameters
```

### 3. Version Tracking

```python
import sympy
import scipy
import numpy

# Track library versions
version_info = {
    'sympy_version': sympy.__version__,
    'scipy_version': scipy.__version__,
    'numpy_version': numpy.__version__,
    'python_version': sys.version
}

results['version_info'] = version_info
```

## Performance Considerations

### 1. Symbolic Computation Optimization

```python
# Cache symbolic results to avoid recomputation
_symbolic_cache = {}

def cached_symbolic_derivation(formula_type):
    if formula_type not in _symbolic_cache:
        if formula_type == 'curvature':
            _symbolic_cache[formula_type] = derive_curvature_formula()
        elif formula_type == 'golden_ratio':
            _symbolic_cache[formula_type] = derive_golden_ratio_transformation()
    
    return _symbolic_cache[formula_type]
```

### 2. Statistical Computation Scaling

```python
# Adaptive bootstrap sample size
def adaptive_bootstrap(data, statistic_func, min_samples=1000, max_samples=10000):
    """Bootstrap with adaptive sample size based on data size."""
    data_size = len(data)
    
    if data_size < 50:
        n_bootstrap = min_samples
    elif data_size < 500:
        n_bootstrap = min_samples * 2
    else:
        n_bootstrap = max_samples
    
    return bootstrap_confidence_intervals(data, statistic_func, n_bootstrap=n_bootstrap)
```

### 3. Memory Management

```python
# Process large datasets in chunks
def chunked_analysis(large_dataset, chunk_size=1000):
    """Analyze large datasets in manageable chunks."""
    results = []
    
    for i in range(0, len(large_dataset), chunk_size):
        chunk = large_dataset[i:i+chunk_size]
        chunk_result = analyze_prime_distribution(chunk)
        results.append(chunk_result)
    
    return results
```

## Integration with Existing Framework

### 1. Core Module Integration

```python
# Integration with existing core modules
from core.axioms import curvature, theta_prime
from symbolic.axiom_derivation import derive_curvature_formula

# Validate numerical vs symbolic implementations
def validate_implementation(n, d_n):
    # Numerical implementation
    numerical_kappa = curvature(n, d_n)
    
    # Symbolic implementation
    symbolic_result = derive_curvature_formula()
    # Extract and evaluate symbolic formula
    
    # Compare results
    return abs(numerical_kappa - symbolic_kappa) < 1e-10
```

### 2. Test Integration

```python
# Add to existing test suite
def test_symbolic_statistical_integration():
    """Integration test for symbolic and statistical modules."""
    
    # Use existing test patterns from validation_tests.py
    from test_finding.scripts.validation_tests import ValidationTests
    
    validator = ValidationTests(N_max=1000)
    
    # Combine with new symbolic/statistical capabilities
    symbolic_result = derive_universal_invariance()
    statistical_result = test_prime_enhancement_hypothesis(
        validator.primes[:50], 
        [n for n in range(4, 200) if not isprime(n)][:50]
    )
    
    return {
        'symbolic_integration': symbolic_result is not None,
        'statistical_integration': statistical_result['hypothesis_test']['rejected_null']
    }
```

## Troubleshooting and Common Issues

### 1. Import Errors

```python
# Always use absolute imports and check PYTHONPATH
import sys
sys.path.append('/home/runner/work/unified-framework/unified-framework')

try:
    from symbolic import derive_universal_invariance
    from statistical import test_prime_enhancement_hypothesis
except ImportError as e:
    print(f"Import error: {e}")
    print("Check PYTHONPATH and dependencies")
```

### 2. Numerical Precision Issues

```python
# Use high precision for symbolic computations
import mpmath as mp
mp.mp.dps = 50  # 50 decimal places

# Handle numerical conversion carefully
def safe_float_conversion(symbolic_expr):
    try:
        return float(symbolic_expr.evalf())
    except:
        return None
```

### 3. Sample Size Requirements

```python
# Check minimum sample sizes for statistical tests
def check_sample_requirements(data1, data2=None):
    """Check if sample sizes are adequate for analysis."""
    requirements = {
        'distribution_analysis': len(data1) >= 30,
        'bootstrap_ci': len(data1) >= 20,
        'hypothesis_test': len(data1) >= 10 and (data2 is None or len(data2) >= 10),
        'normality_test': len(data1) >= 8
    }
    
    return requirements
```

This comprehensive documentation provides the foundation for using the new symbolic and statistical capabilities effectively within the Z Framework analysis pipeline.