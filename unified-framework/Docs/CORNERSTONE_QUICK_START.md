# Cornerstone Invariant - Quick Start Guide

## What is the Cornerstone Principle?

The **cornerstone invariant principle** is the fundamental foundation of the Z Framework. It formalizes the introduction of an **invariant** that governs systems across different domains through the **Lorentz-inspired normalization equation**:

```
Z = A(B/c)
```

Where:
- **Z**: Normalized observation or measurement
- **A**: Frame-dependent quantity (scalar or function)
- **B**: Rate, velocity, or domain-specific parameter
- **c**: Universal invariant constant (domain-dependent)

## Why It Matters

1. **Universality**: Same equation works across physics, mathematics, and computation
2. **Consistency**: Provides stable reference point for all observations
3. **Reproducibility**: Enables comparable measurements across domains
4. **Elegance**: Simplifies complex mappings and scaling operations

## Quick Examples

### Physical Domain (Relativity)

```python
from src.core.cornerstone_invariant import PhysicalInvariant

# Create physical invariant (c = speed of light)
phys = PhysicalInvariant()

# Time dilation at 60% speed of light
time_dilated = phys.time_dilation(proper_time=1.0, velocity=0.6 * phys.c)
print(f"Time dilation: {float(time_dilated):.6f} seconds")
# Output: 1.250000 seconds

# Length contraction at 80% speed of light
length = phys.length_contraction(rest_length=10.0, velocity=0.8 * phys.c)
print(f"Contracted length: {float(length):.6f} meters")
# Output: 6.000000 meters
```

### Discrete Mathematical Domain (Prime Densities)

```python
from src.core.cornerstone_invariant import DiscreteInvariant

# Create discrete invariant (c = e²)
discrete = DiscreteInvariant()

# Normalize prime density
normalized = discrete.compute_normalized_density(n=1000, delta_n=0.5)
print(f"Normalized density: {float(normalized):.2f}")
# Output: 67.67

# Compute divisor scaling
scaled = discrete.compute_divisor_scaling(n=5000)
print(f"Divisor scaling: {float(scaled):.2f}")
# Output: 3969.16
```

### Number-Theoretic Domain (Geodesic Transformations)

```python
from src.core.cornerstone_invariant import NumberTheoreticInvariant

# Create number-theoretic invariant (c = golden ratio)
nt = NumberTheoreticInvariant()

# Geodesic transformation
geodesic = nt.compute_geodesic_transform(n=100, k=0.3)
print(f"Geodesic θ'(100, 0.3): {float(geodesic):.6f}")
# Output: 5.575597
```

### Custom Domain

```python
from src.core.cornerstone_invariant import CornerstoneInvariant

# Create custom invariant for your domain
custom = CornerstoneInvariant(c=100.0, domain="my_domain")

# Compute normalized value
result = custom.compute_z(A=10, B=50)
print(f"Custom Z: {float(result):.2f}")
# Output: 5.00 (= 10 * 50/100)
```

## Domain Invariants

| Domain | Invariant (c) | Value | Application |
|--------|---------------|-------|-------------|
| Physical | Speed of light | 299,792,458 m/s | Relativistic transformations |
| Discrete | e² (Euler squared) | ~7.389 | Prime density, integer sequences |
| Number-theoretic | φ (Golden ratio) | ~1.618 | Geodesic optimization |
| Custom | User-defined | Any positive value | Domain-specific needs |

## Validation

The cornerstone principle satisfies five key properties:

```python
from src.core.cornerstone_invariant import validate_cornerstone_principle

validation = validate_cornerstone_principle()

if validation['overall_pass']:
    print("✅ All cornerstone principle checks passed")
    # Universality: ✅
    # Consistency: ✅
    # Reproducibility: ✅
    # Symmetry: ✅
    # Precision: ✅
```

## Integration with Z Framework

The cornerstone invariant integrates seamlessly with:

- **z_baseline**: Baseline predictions using discrete invariant
- **axioms**: Universal Z form alignment
- **z_5d_enhanced**: Enhanced 5D predictions with geodesic transformations
- **geodesic_mapping**: Golden ratio geodesic density transformations

Example integration:

```python
from src.core.cornerstone_invariant import DiscreteInvariant
from math import e, log

# Use discrete invariant matching z_baseline
discrete = DiscreteInvariant(delta_max=e**2)

# Compute dilation factor (compatible with z_baseline)
n = 1000
d_n = log(n)
ln_term = log(n + 1)
delta_n = (d_n * ln_term) / (e**2)

# Normalize using cornerstone invariant
normalized = discrete.compute_normalized_density(n, delta_n)
print(f"Z = {float(normalized):.2f}")
```

## Running Examples

### Built-in Demonstration

```bash
# Run the main cornerstone demo
python src/core/cornerstone_invariant.py

# Expected output:
# ✅ ALL CHECKS PASSED
```

### Cross-Domain Demo

```bash
# Run comprehensive cross-domain examples
python examples/cornerstone_invariant_demo.py

# Shows physical, discrete, and number-theoretic domains
```

### Integration Examples

```bash
# Run integration with existing Z Framework
python examples/cornerstone_integration_example.py

# Demonstrates 5 integration patterns
```

## Testing

```bash
# Run comprehensive test suite (34 tests)
python -m pytest tests/test_cornerstone_invariant.py -v

# All tests should pass:
# ✅ 34 passed in 0.15s
```

## Key Properties

### 1. Invariance is Robust
- Anchors problem-solving around constants immune to transformations
- Results generalize across disciplines

### 2. Elegant Simplicity
- Simplifies complex mappings and normalizations
- Like Lorentz transformations simplify relativity

### 3. Tool for Discovery
- Platform for reproducible validation
- Inspires new derivations and theories

### 4. Geometric Harmony
- Introduces consistent structure
- Drives computational and theoretical innovation

## Next Steps

1. **Read Full Documentation**: [CORNERSTONE_INVARIANT.md](framework/CORNERSTONE_INVARIANT.md)
2. **Explore Examples**: Run demos in `examples/` directory
3. **Review Tests**: See `tests/test_cornerstone_invariant.py`
4. **Integrate**: Use cornerstone invariants in your Z Framework work

## References

- **Lorentz Transformations**: Inspiration from special relativity
- **Z Framework**: Unified framework for cross-domain analysis
- **Cognitive Number Theory**: Prime density applications
- **Golden Ratio Geodesics**: Optimization applications

## Support

For questions or issues:
- Check [CORNERSTONE_INVARIANT.md](framework/CORNERSTONE_INVARIANT.md) for detailed documentation
- Review examples in `examples/` directory
- Run tests to verify installation

---

**The cornerstone invariant principle is the foundation upon which the entire Z Framework is built.**

It provides both:
- **Theoretical profundity**: Deep mathematical insights
- **Practical impact**: Efficient computational implementations

This is the **big picture** and the **critical mechanism** for all Z Framework work.
