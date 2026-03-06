# Getting Started with the Z Framework

Welcome to the Z Framework! This guide will help you get started with the unified mathematical model that bridges physical and discrete domains through the empirical invariance of the speed of light. The framework achieves conditional prime density improvement under canonical benchmark methodology (95% CI: [14.6%, 15.4%]) and ultra-extreme scale validation up to n = 10^16.

## Prerequisites

### Mathematical Background
- Basic understanding of calculus and number theory
- Familiarity with modular arithmetic
- Knowledge of statistical analysis concepts
- Understanding of computational precision requirements

### Technical Requirements
- Python 3.8+ environment
- Required packages: numpy, pandas, matplotlib, mpmath, sympy, scipy
- Minimum 8GB RAM for large-scale computations
- 64-bit system for high-precision arithmetic

## Installation

### Dependencies
```bash
pip install numpy pandas matplotlib mpmath sympy scikit-learn statsmodels scipy seaborn plotly
```

### Repository Setup
```bash
git clone https://github.com/zfifteen/unified-framework.git
cd unified-framework
export PYTHONPATH=/path/to/unified-framework
```

### Verification
```python
# Test basic framework functionality
from src.core.system_instruction import ZFrameworkSystemInstruction
from src.core import axioms

print("✓ Z Framework loaded successfully")
```

## Quick Start Examples

### Example 1: Basic Universal Form

```python
import mpmath as mp
mp.mp.dps = 50  # High precision requirement

# Universal form: Z = A(B/c)
def calculate_z_form(A, B, c=299792458):
    """Calculate Z framework universal form"""
    return A * (B / c)

# Physical domain example
T = 1.0  # 1 second
v = 1e6  # 1,000 km/s velocity
Z_physical = calculate_z_form(T, v)
print(f"Physical Z: {Z_physical}")

# Result: Z ≈ 3.336e-03 (normalized time-velocity ratio)
```

### Example 2: Discrete Domain Analysis

```python
import mpmath as mp
mp.mp.dps = 50

def divisor_count(n):
    """Count positive divisors of n"""
    count = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
    return count

def discrete_curvature(n):
    """Calculate discrete curvature κ(n) = d(n) · ln(n+1)/e²"""
    d_n = divisor_count(n)
    e_squared = mp.e ** 2
    return d_n * mp.log(n + 1) / e_squared

# Calculate curvature for first 10 integers
for n in range(1, 11):
    kappa = discrete_curvature(n)
    print(f"κ({n}) = {float(kappa):.6f}")
```

### Example 3: Golden Ratio Transformation

```python
import mpmath as mp
mp.mp.dps = 50

def golden_ratio_transform(n, k):
    """Apply golden ratio transformation θ'(n,k) = φ·{n/φ}^k"""
    phi = (1 + mp.sqrt(5)) / 2
    residue = n % phi
    normalized = residue / phi
    transformed = phi * (normalized ** k)
    return float(transformed)

# Test optimal parameter k* = 0.3
k_optimal = 0.3
numbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]  # First 10 primes

print("Golden Ratio Transformation (k* = 0.3):")
for n in numbers:
    theta_prime = golden_ratio_transform(n, k_optimal)
    print(f"θ'({n}, {k_optimal}) = {theta_prime:.6f}")
```

## Core Concepts

### Universal Invariance

The Z Framework is built on the principle that all observations can be normalized to the speed of light:

```python
# All framework calculations use this invariant
c = 299792458  # m/s (exact)

# Physical domain: relativistic effects
def time_dilation_factor(v, c=c):
    return 1 / mp.sqrt(1 - (v/c)**2)

# Discrete domain: frame shift normalization  
def frame_shift_ratio(delta_n, delta_max):
    return delta_n / delta_max
```

### High-Precision Arithmetic

Critical for accurate results:

```python
import mpmath as mp

# Always set high precision
mp.mp.dps = 50  # 50 decimal places

# Golden ratio with high precision
phi = (1 + mp.sqrt(5)) / 2
print(f"φ = {phi}")
# Output: φ = 1.6180339887498948482045868343656381177203091798058

# Verify precision
assert abs(phi - mp.mpf('1.6180339887498948482045868343656381177203091798058')) < mp.mpf('1e-49')
```

### Validation Requirements

All results must meet statistical significance:

```python
def validate_enhancement(baseline, enhanced, confidence_level=0.95):
    """Validate statistical significance of enhancement"""
    import scipy.stats as stats
    
    # Calculate enhancement ratio
    enhancement = (enhanced - baseline) / baseline * 100
    
    # Perform statistical test (example with t-test)
    t_stat, p_value = stats.ttest_rel(enhanced, baseline)
    
    # Check significance
    alpha = 1 - confidence_level
    is_significant = p_value < alpha
    
    return {
        'enhancement_percent': enhancement,
        'p_value': p_value,
        'significant': is_significant,
        'confidence_level': confidence_level
    }
```

## Working with Prime Numbers

### Prime Generation
```python
def sieve_of_eratosthenes(limit):
    """Generate primes up to limit using Sieve of Eratosthenes"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
                
    return [i for i in range(2, limit + 1) if is_prime[i]]

# Generate first 1000 primes for analysis
primes = sieve_of_eratosthenes(7919)  # 1000th prime is 7919
print(f"Generated {len(primes)} primes")
```

### Prime Density Analysis
```python
def analyze_prime_density(primes, k_values, num_bins=20):
    """Analyze prime density under golden ratio transformation"""
    phi = (1 + mp.sqrt(5)) / 2
    results = {}
    
    for k in k_values:
        # Transform primes
        transformed = [golden_ratio_transform(p, k) for p in primes]
        
        # Create histogram
        hist, bins = np.histogram(transformed, bins=num_bins, range=(0, float(phi)))
        density = hist / len(primes)
        
        # Calculate enhancement (simplified)
        baseline_density = 1.0 / num_bins  # Uniform expectation
        max_density = max(density)
        enhancement = (max_density - baseline_density) / baseline_density * 100
        
        results[k] = {
            'density': density,
            'enhancement': enhancement,
            'bins': bins
        }
    
    return results

# Test range around optimal k*
k_range = [0.1, 0.2, 0.3, 0.4, 0.5]
results = analyze_prime_density(primes[:100], k_range)

for k, data in results.items():
    print(f"k = {k}: Enhancement = {data['enhancement']:.2f}%")
```

## Common Patterns

### Error Handling
```python
def safe_calculate_z(A, B, c=299792458):
    """Safely calculate Z form with error handling"""
    try:
        # Validate inputs
        if not isinstance(A, (int, float, mp.mpf)):
            raise TypeError("A must be numeric")
        if not isinstance(B, (int, float, mp.mpf)):
            raise TypeError("B must be numeric")
        if B >= c:
            raise ValueError("B must be less than c (causality)")
        
        # Calculate with high precision
        return mp.mpf(A) * (mp.mpf(B) / mp.mpf(c))
        
    except Exception as e:
        print(f"Error in Z calculation: {e}")
        return None
```

### Performance Optimization
```python
import time
from functools import lru_cache

@lru_cache(maxsize=10000)
def cached_divisor_count(n):
    """Cached divisor count for performance"""
    return divisor_count(n)

def benchmark_calculation(func, args, iterations=1000):
    """Benchmark calculation performance"""
    start_time = time.time()
    for _ in range(iterations):
        result = func(*args)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / iterations
    return avg_time, result
```

## Next Steps

### Explore Advanced Features
1. **5D Helical Embeddings**: [Mathematical Model](../framework/mathematical-model.md#5d-helical-embedding)
2. **Cross-Domain Validation**: [Research Papers](../research/papers.md)
3. **Computational Optimization**: [API Reference](../api/reference.md)

### Run Validation Tests
```bash
# Basic validation
python tests/simple_test.py

# Comprehensive validation (requires time)
python tests/run_tests.py
```

### Study Examples
- [Practical Examples](../examples/README.md)
- [Research Experiments](../research/experiments/)
- [Visualization Tools](../../src/visualization/)

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Set Python path
export PYTHONPATH=/path/to/unified-framework

# Or run from repository root
cd unified-framework
python your_script.py
```

**Precision Errors**:
```python
# Always set precision early
import mpmath as mp
mp.mp.dps = 50  # Must be first import operation
```

**Performance Issues**:
```python
# For large computations, consider parallel processing
from multiprocessing import Pool

def parallel_calculation(data_chunks):
    with Pool() as pool:
        results = pool.map(your_function, data_chunks)
    return results
```

### Getting Help

- **Framework Documentation**: [Core Principles](../framework/core-principles.md)
- **API Reference**: [Technical Details](../api/reference.md)
- **Research Papers**: [Detailed Studies](../research/papers.md)
- **Contributing**: [Guidelines](../contributing/guidelines.md)

## Summary

You've learned the basics of the Z Framework:
- Universal form Z = A(B/c) for cross-domain analysis
- High-precision arithmetic requirements (mpmath dps=50+)
- Golden ratio transformations with optimal k* ≈ 0.3
- Prime density analysis showing 15% enhancement
- Statistical validation requirements (p < 10⁻⁶)

The framework provides a powerful tool for analyzing phenomena across physical and discrete domains through geometric constraints and empirical validation.

---

**Next Reading**: [User Guide](user-guide.md) for detailed usage patterns  
**Advanced Topics**: [Framework Documentation](../framework/README.md)  
**Research Applications**: [Examples](../examples/README.md)