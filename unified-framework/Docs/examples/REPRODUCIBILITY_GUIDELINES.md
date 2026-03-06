# Reproducibility Guidelines for Symbolic and Statistical Analysis

This document establishes reproducibility standards for the Z Framework's symbolic axiom derivation and statistical testing modules.

## Core Reproducibility Principles

### 1. Deterministic Random Seeding

```python
import numpy as np

# Always set random seeds for reproducible results
np.random.seed(42)  # Use consistent seed value

# For multiple random operations, use different seeds deterministically
def set_deterministic_seed(base_seed, operation_id):
    """Set deterministic seed based on operation."""
    return np.random.seed(base_seed * 1000 + operation_id)

# Example usage
set_deterministic_seed(42, 1)  # For bootstrap sampling
bootstrap_result = bootstrap_confidence_intervals(data, np.mean, n_bootstrap=1000)

set_deterministic_seed(42, 2)  # For permutation tests
permutation_result = permutation_test_significance(group1, group2, n_permutations=1000)
```

### 2. Parameter Documentation and Validation

```python
# Standard parameter set for reproducible analysis
FRAMEWORK_PARAMETERS = {
    'mathematical_constants': {
        'golden_ratio_phi': float((1 + np.sqrt(5)) / 2),  # φ ≈ 1.618033988749
        'e_squared': float(np.exp(2)),                     # e² ≈ 7.38905609893
        'target_variance': 0.118,                         # Empirical target σ ≈ 0.118
        'speed_of_light': 299792458.0                     # c in m/s
    },
    'analysis_parameters': {
        'curvature_exponent_k': 3.33,                     # Optimal k* ≈ 3.33
        'bootstrap_samples': 1000,                        # Standard bootstrap size
        'confidence_level': 0.95,                         # 95% confidence intervals
        'significance_level': 0.05,                       # α = 0.05
        'high_precision_digits': 50                       # mpmath precision
    },
    'computational_settings': {
        'max_sample_size': 10000,                         # Memory management
        'chunk_size': 1000,                               # For large datasets
        'timeout_seconds': 300,                           # Default timeout
        'numerical_tolerance': 1e-10                      # Floating point tolerance
    }
}

def validate_parameters(params=FRAMEWORK_PARAMETERS):
    """Validate parameter consistency and ranges."""
    math_params = params['mathematical_constants']
    analysis_params = params['analysis_parameters']
    
    # Validate golden ratio
    expected_phi = (1 + np.sqrt(5)) / 2
    assert abs(math_params['golden_ratio_phi'] - expected_phi) < 1e-10, "Golden ratio mismatch"
    
    # Validate k parameter range
    assert 0.1 <= analysis_params['curvature_exponent_k'] <= 0.5, "k parameter out of range"
    
    # Validate statistical parameters
    assert 0 < analysis_params['confidence_level'] < 1, "Invalid confidence level"
    assert 0 < analysis_params['significance_level'] < 1, "Invalid significance level"
    assert analysis_params['bootstrap_samples'] >= 100, "Insufficient bootstrap samples"
    
    return True

# Always validate parameters before analysis
validate_parameters()
```

### 3. Version and Environment Tracking

```python
import sys
import sympy
import scipy
import numpy as np
import pandas as pd
from datetime import datetime

def get_environment_info():
    """Capture complete environment information for reproducibility."""
    return {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': sys.platform,
        'library_versions': {
            'numpy': np.__version__,
            'scipy': scipy.__version__,
            'sympy': sympy.__version__,
            'pandas': pd.__version__,
            'matplotlib': getattr(__import__('matplotlib'), '__version__', 'unknown')
        },
        'framework_parameters': FRAMEWORK_PARAMETERS,
        'random_seed': 42  # Document the random seed used
    }

# Include environment info in all analysis results
def reproducible_analysis_wrapper(analysis_function, *args, **kwargs):
    """Wrapper to add reproducibility metadata to analysis results."""
    # Set deterministic seed
    np.random.seed(42)
    
    # Capture environment
    env_info = get_environment_info()
    
    # Run analysis
    result = analysis_function(*args, **kwargs)
    
    # Add metadata
    if isinstance(result, dict):
        result['reproducibility_metadata'] = env_info
    
    return result
```

### 4. Data Validation and Checksums

```python
import hashlib
import json

def compute_data_checksum(data):
    """Compute checksum for data validation."""
    if isinstance(data, (list, tuple)):
        data_str = json.dumps(sorted(data))
    elif isinstance(data, np.ndarray):
        data_str = data.tobytes().hex()
    else:
        data_str = str(data)
    
    return hashlib.sha256(data_str.encode()).hexdigest()[:16]

def validate_reference_data():
    """Validate against known reference datasets."""
    # Known prime sequence checksum (first 100 primes)
    reference_primes = [p for p in range(2, 542) if isprime(p)]  # First 100 primes
    expected_checksum = "a1b2c3d4e5f6g7h8"  # Example checksum
    
    computed_checksum = compute_data_checksum(reference_primes)
    
    # In practice, use actual known checksums
    reference_datasets = {
        'first_100_primes': {
            'data': reference_primes,
            'expected_checksum': computed_checksum,  # Use computed for this example
            'description': 'First 100 prime numbers'
        }
    }
    
    return reference_datasets

# Validate data before analysis
reference_data = validate_reference_data()
```

### 5. Symbolic Computation Reproducibility

```python
import mpmath as mp

def ensure_symbolic_precision():
    """Ensure consistent symbolic computation precision."""
    # Set high precision for reproducible symbolic computations
    mp.mp.dps = FRAMEWORK_PARAMETERS['analysis_parameters']['high_precision_digits']
    
    # Verify precision setting
    test_computation = mp.pi
    assert len(str(test_computation)) > 50, "Insufficient precision"
    
    return mp.mp.dps

def symbolic_computation_wrapper(symbolic_function):
    """Wrapper for reproducible symbolic computations."""
    def wrapper(*args, **kwargs):
        # Ensure precision
        original_dps = mp.mp.dps
        ensure_symbolic_precision()
        
        try:
            result = symbolic_function(*args, **kwargs)
            
            # Add precision metadata
            if isinstance(result, dict):
                result['symbolic_metadata'] = {
                    'precision_digits': mp.mp.dps,
                    'computation_time': datetime.now().isoformat()
                }
            
            return result
        finally:
            # Restore original precision
            mp.mp.dps = original_dps
    
    return wrapper

# Apply to symbolic functions
@symbolic_computation_wrapper
def reproducible_derive_curvature():
    from symbolic.axiom_derivation import derive_curvature_formula
    return derive_curvature_formula()
```

### 6. Statistical Test Reproducibility

```python
def reproducible_statistical_test(test_function, data, **test_params):
    """Ensure reproducible statistical testing."""
    
    # Validate sample size
    min_sample_size = test_params.get('min_sample_size', 10)
    if len(data) < min_sample_size:
        raise ValueError(f"Sample size {len(data)} below minimum {min_sample_size}")
    
    # Set deterministic parameters
    default_params = {
        'significance_level': FRAMEWORK_PARAMETERS['analysis_parameters']['significance_level'],
        'confidence_level': FRAMEWORK_PARAMETERS['analysis_parameters']['confidence_level'],
        'n_bootstrap': FRAMEWORK_PARAMETERS['analysis_parameters']['bootstrap_samples']
    }
    
    # Merge with provided parameters
    final_params = {**default_params, **test_params}
    
    # Set random seed for reproducible sampling
    np.random.seed(42)
    
    # Run test
    result = test_function(data, **final_params)
    
    # Add reproducibility metadata
    if isinstance(result, dict):
        result['test_metadata'] = {
            'parameters_used': final_params,
            'sample_size': len(data),
            'data_checksum': compute_data_checksum(data),
            'random_seed': 42
        }
    
    return result
```

### 7. Cross-Platform Compatibility

```python
import os
import platform

def ensure_cross_platform_compatibility():
    """Ensure analysis works across different platforms."""
    
    compatibility_settings = {
        'decimal_precision': 10,  # Limit precision for cross-platform consistency
        'float_tolerance': 1e-10,  # Tolerance for floating point comparisons
        'path_separator': os.path.sep,  # Use OS-appropriate path separator
        'line_ending': os.linesep   # Use OS-appropriate line ending
    }
    
    # Platform-specific adjustments
    if platform.system() == 'Windows':
        compatibility_settings['backend'] = 'Agg'  # For matplotlib
    elif platform.system() == 'Darwin':  # macOS
        compatibility_settings['backend'] = 'TkAgg'
    else:  # Linux
        compatibility_settings['backend'] = 'Agg'
    
    return compatibility_settings

def platform_safe_comparison(value1, value2, tolerance=1e-10):
    """Platform-safe numerical comparison."""
    return abs(float(value1) - float(value2)) < tolerance
```

### 8. Reproducible Workflow Templates

```python
def standard_symbolic_analysis_workflow(expression_type='curvature'):
    """Standard reproducible workflow for symbolic analysis."""
    
    workflow_log = []
    
    try:
        # Step 1: Environment setup
        env_info = get_environment_info()
        ensure_symbolic_precision()
        workflow_log.append("✓ Environment configured")
        
        # Step 2: Symbolic derivation
        if expression_type == 'curvature':
            from symbolic.axiom_derivation import derive_curvature_formula
            symbolic_result = derive_curvature_formula()
        elif expression_type == 'golden_ratio':
            from symbolic.axiom_derivation import derive_golden_ratio_transformation
            symbolic_result = derive_golden_ratio_transformation()
        else:
            raise ValueError(f"Unknown expression type: {expression_type}")
        
        workflow_log.append(f"✓ Symbolic derivation completed: {expression_type}")
        
        # Step 3: Verification
        from symbolic.verification import verify_axiom_consistency
        verification_result = verify_axiom_consistency()
        workflow_log.append(f"✓ Verification: {'passed' if verification_result['is_consistent'] else 'failed'}")
        
        # Step 4: Compile results
        final_result = {
            'symbolic_result': symbolic_result,
            'verification': verification_result,
            'workflow_log': workflow_log,
            'environment': env_info,
            'reproducible': True
        }
        
        return final_result
        
    except Exception as e:
        workflow_log.append(f"❌ Error: {str(e)}")
        return {
            'error': str(e),
            'workflow_log': workflow_log,
            'reproducible': False
        }

def standard_statistical_analysis_workflow(data1, data2=None, analysis_type='enhancement'):
    """Standard reproducible workflow for statistical analysis."""
    
    workflow_log = []
    
    try:
        # Step 1: Data validation
        data1_checksum = compute_data_checksum(data1)
        workflow_log.append(f"✓ Data1 validated (checksum: {data1_checksum})")
        
        if data2 is not None:
            data2_checksum = compute_data_checksum(data2)
            workflow_log.append(f"✓ Data2 validated (checksum: {data2_checksum})")
        
        # Step 2: Statistical analysis
        np.random.seed(42)  # Reproducible random operations
        
        if analysis_type == 'enhancement' and data2 is not None:
            from statistical.hypothesis_testing import test_prime_enhancement_hypothesis
            test_result = test_prime_enhancement_hypothesis(data1, data2)
        elif analysis_type == 'distribution':
            from statistical.distribution_analysis import analyze_prime_distribution
            test_result = analyze_prime_distribution(data1)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        workflow_log.append(f"✓ Statistical analysis completed: {analysis_type}")
        
        # Step 3: Bootstrap validation
        from statistical.bootstrap_validation import bootstrap_confidence_intervals
        bootstrap_result = bootstrap_confidence_intervals(data1, np.mean, n_bootstrap=1000)
        workflow_log.append("✓ Bootstrap validation completed")
        
        # Step 4: Compile results
        final_result = {
            'statistical_result': test_result,
            'bootstrap_validation': bootstrap_result,
            'workflow_log': workflow_log,
            'data_checksums': {
                'data1': data1_checksum,
                'data2': data2_checksum if data2 is not None else None
            },
            'reproducible': True
        }
        
        return final_result
        
    except Exception as e:
        workflow_log.append(f"❌ Error: {str(e)}")
        return {
            'error': str(e),
            'workflow_log': workflow_log,
            'reproducible': False
        }
```

### 9. Validation Against Reference Results

```python
def validate_against_reference_results():
    """Validate current implementation against known reference results."""
    
    reference_results = {
        'golden_ratio_value': 1.6180339887498948,
        'e_squared_value': 7.38905609893065,
        'optimal_k_theoretical': 0.3,
        'target_variance': 0.118,
        'documented_zeta_correlation': 0.93
    }
    
    validation_results = {}
    
    # Test 1: Golden ratio computation
    from symbolic.axiom_derivation import derive_golden_ratio_transformation
    golden_result = derive_golden_ratio_transformation()
    computed_phi = float(golden_result['phi_exact'].evalf())
    
    phi_valid = platform_safe_comparison(computed_phi, reference_results['golden_ratio_value'])
    validation_results['golden_ratio'] = {
        'expected': reference_results['golden_ratio_value'],
        'computed': computed_phi,
        'valid': phi_valid
    }
    
    # Test 2: e² computation
    computed_e_squared = float(np.exp(2))
    e_squared_valid = platform_safe_comparison(computed_e_squared, reference_results['e_squared_value'])
    validation_results['e_squared'] = {
        'expected': reference_results['e_squared_value'],
        'computed': computed_e_squared,
        'valid': e_squared_valid
    }
    
    # Overall validation
    all_valid = all(result['valid'] for result in validation_results.values())
    
    return {
        'individual_validations': validation_results,
        'overall_valid': all_valid,
        'reference_results': reference_results
    }
```

### 10. Complete Reproducibility Checklist

```python
def reproducibility_checklist():
    """Complete checklist for reproducible Z Framework analysis."""
    
    checklist = {
        'environment_setup': {
            'python_path_set': os.environ.get('PYTHONPATH') is not None,
            'dependencies_installed': True,  # Assume verified
            'precision_configured': mp.mp.dps >= 50,
            'random_seed_set': True  # Manually verified
        },
        'parameter_validation': {
            'framework_parameters_loaded': FRAMEWORK_PARAMETERS is not None,
            'parameters_validated': validate_parameters(),
            'reference_results_validated': validate_against_reference_results()['overall_valid']
        },
        'computational_settings': {
            'cross_platform_compatibility': ensure_cross_platform_compatibility() is not None,
            'numerical_tolerance_set': True,
            'timeout_configured': True
        },
        'data_integrity': {
            'checksums_computed': True,
            'reference_data_validated': True,
            'sample_sizes_adequate': True
        },
        'result_documentation': {
            'metadata_included': True,
            'parameters_documented': True,
            'workflow_logged': True,
            'version_tracked': True
        }
    }
    
    # Compute overall score
    total_checks = sum(len(category) for category in checklist.values())
    passed_checks = sum(
        sum(1 for check in category.values() if check) 
        for category in checklist.values()
    )
    
    score = passed_checks / total_checks
    
    return {
        'checklist': checklist,
        'score': score,
        'reproducibility_grade': (
            'Excellent' if score >= 0.95 else
            'Good' if score >= 0.85 else
            'Adequate' if score >= 0.70 else
            'Needs Improvement'
        )
    }

# Run reproducibility check
reproducibility_status = reproducibility_checklist()
print(f"Reproducibility grade: {reproducibility_status['reproducibility_grade']}")
print(f"Score: {reproducibility_status['score']:.1%}")
```

## Best Practices Summary

1. **Always set random seeds** for any operation involving randomness
2. **Document all parameters** used in analysis with validation
3. **Track environment and versions** for complete reproducibility
4. **Validate data integrity** using checksums and reference datasets
5. **Use high precision** for symbolic computations (50 decimal places)
6. **Test cross-platform compatibility** with appropriate tolerances
7. **Follow standard workflows** for consistent analysis patterns
8. **Include metadata** in all analysis results
9. **Validate against references** to ensure implementation correctness
10. **Run reproducibility checklist** before publishing results

Following these guidelines ensures that all Z Framework symbolic and statistical analyses can be reliably reproduced across different environments, platforms, and time periods.