# Circle-Tangent Parallelogram Geometric Invariant

## Overview

The circle-tangent parallelogram geometric invariant is a mathematical property where the area of a shaded region formed by tangent lines to a circle remains constant regardless of the circle's diameter, due to the relationship `d × h = constant`.

## Mathematical Foundation

### Setup
- Circle of diameter `d` centered at origin
- Two parallel tangent lines at distance `h` from center
- Parallelogram formed with fixed side length `s`
- **Invariant**: `Area = d × h = constant` (independent of `d`)

### Canonical Case
For the reference implementation with `s = 5` and target area = 25:
- Area = `s × h = 5 × h = 25` → `h = 5`
- Due to tangent perpendicularity: `d × h = 25` for any diameter `d`
- This creates a **scale-independent resonance property**

### Key Properties
1. **Scale Invariance**: Area remains constant across different diameters
2. **Geometric Constraint**: `d × h = constant` defines the relationship
3. **Tangent Perpendicularity**: Tangent lines perpendicular to radius at contact point
4. **Reproducibility**: Results are deterministic and reproducible with fixed seeds

## Implementation

### Monte Carlo Module (`monte_carlo.py`)

#### CircleTangentParallelogramValidator

Main class implementing the geometric invariant with the following features:

```python
from monte_carlo import CircleTangentParallelogramValidator

# Initialize with canonical parameters
validator = CircleTangentParallelogramValidator(
    side_length=5.0,
    target_area=25.0,
    precision_dps=50
)

# Validate scale invariance across different diameters
results = validator.validate_scale_invariance(
    diameters=[1.0, 5.0, 10.0, 25.0, 50.0],
    num_mc_samples=100000,
    seed=42
)

# Compute symbolic area (requires sympy)
area_symbolic = validator.compute_area_symbolic()
```

**Key Methods:**
- `compute_area_symbolic()` - Symbolic area computation using SymPy
- `validate_scale_invariance()` - Monte Carlo validation across diameters
- `geometric_resonance_factor()` - Z5D curvature enhancement
- `tangent_perpendicularity_candidates()` - Factorization candidate generation

### Gaussian Lattice Module (`gaussian_lattice.py`)

#### TangentBasedLatticeEmbedding

Integrates the geometric invariant with Gaussian integer lattice computations:

```python
from gaussian_lattice import TangentBasedLatticeEmbedding

# Initialize embedding
embedding = TangentBasedLatticeEmbedding(
    invariant_constant=25.0,
    precision_dps=50
)

# Enhanced distance metric
distance = embedding.tangent_enhanced_distance(
    z1=0+0j, 
    z2=5+0j,
    lattice_scale=1.0,
    tangent_weight=0.5
)

# Filter candidates by tangent property
filtered = embedding.filter_candidates_by_tangent_property(
    N=143,  # Number to factor
    candidates=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    threshold=0.5
)

# Quality scoring for lattice points
quality = embedding.lattice_point_quality_score(
    z=11+0j,
    reference_point=11+0j
)
```

**Key Methods:**
- `tangent_enhanced_distance()` - Scale-independent distance metric
- `filter_candidates_by_tangent_property()` - Geometric filtering
- `lattice_point_quality_score()` - Candidate ranking

## Applications to Z5D Framework

### 1. Tangent-Based Embeddings for Visualizations

The geometric invariant provides scale-independent reference frames for line-intersection visualizations:

```python
# Use in coordinate geometry visualization
validator = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)
resonance = validator.geometric_resonance_factor(n=143)
```

### 2. Scale-Independent Distance Metrics

Similar to clustering near √N, the invariant provides distance metrics that don't depend on the scale:

```python
embedding = TangentBasedLatticeEmbedding(invariant_constant=25.0)
enhanced_dist = embedding.tangent_enhanced_distance(z1, z2)
```

### 3. Variance Stabilization in Monte Carlo Sampling

The geometric constraint helps stabilize variance in Monte Carlo integration:

```python
# Monte Carlo validation with reduced variance
results = validator.validate_scale_invariance(
    diameters=[1.0, 10.0, 100.0],
    num_mc_samples=100000,
    seed=42
)
# Variance remains low due to geometric constraint
```

### 4. Lattice Optimizations

Enhances Gaussian lattice computations with tangent-based constraints:

```python
# Filter candidates using geometric properties
filtered = embedding.filter_candidates_by_tangent_property(N, candidates)
```

### 5. Z5D-Guided Factorization

Treats parallelogram projection as a resonance ladder step:

```python
# Compute geometric resonance for Z5D curvature
resonance = validator.geometric_resonance_factor(n=899)

# Generate candidates using tangent perpendicularity
candidates = validator.tangent_perpendicularity_candidates(
    N=143,
    num_samples=100,
    seed=42
)
```

## Integration with Factorization Framework

### Candidate Generation

The tangent perpendicularity constraint provides an alternative sampling mode for factorization:

```python
validator = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)

# Generate candidates for N = 143 (11 × 13)
candidates = validator.tangent_perpendicularity_candidates(
    N=143,
    num_samples=100,
    seed=42
)

# Check if factors found
if 11 in candidates or 13 in candidates:
    print("✓ Factor found using tangent-based method!")
```

### Error Bound Reduction

The geometric invariant can potentially reduce error bounds in high-bit RSA challenges:

1. **Scale Independence**: Provides consistent metric across bit lengths
2. **Geometric Filtering**: Reduces candidate space while preserving factors
3. **Quality Ranking**: Scores candidates based on invariant properties
4. **Complementary to φ-biasing**: Works alongside existing QMC methods

### Integration with Z5D Curvature

Enhances standard Z5D curvature κ(n) = d(n)·ln(n+1)/e^2 with geometric resonance:

```python
# Standard Z5D curvature
kappa_standard = d_n * log(n+1) / e^2

# Enhanced with geometric resonance
resonance = validator.geometric_resonance_factor(n)
# resonance = kappa_standard * (1 + phase * area / 100)
```

## Testing

Comprehensive test suite in `tests/test_circle_tangent_parallelogram.py`:

```bash
# Run tests
PYTHONPATH=python python3 tests/test_circle_tangent_parallelogram.py

# Expected output:
# Test Results: 10 passed, 0 failed
# ✓ All tests passed!
```

**Test Coverage:**
- Validator initialization
- Symbolic area computation (with SymPy)
- Scale invariance property (d×h = constant)
- Geometric resonance factor
- Tangent-perpendicularity candidate generation
- Tangent-based lattice embedding
- Candidate filtering
- Quality scoring
- Reproducibility with fixed seeds
- Integration with Monte Carlo framework

## Demonstrations

### Monte Carlo Demonstration

```bash
PYTHONPATH=python python3 python/monte_carlo.py
```

Shows:
- Symbolic area computation
- Scale invariance validation across 6 different diameters
- Application to Z5D factorization
- Tangent-perpendicularity candidate generation
- Key insights and applications

### Gaussian Lattice Demonstration

```bash
PYTHONPATH=python python3 python/gaussian_lattice.py
```

Shows:
- Tangent-enhanced distance metric
- Candidate filtering by tangent property
- Lattice point quality scoring
- Integration with Epstein zeta framework

## Performance Characteristics

- **Computational Complexity**: O(N) for candidate generation
- **Memory Usage**: O(N) for candidate storage
- **Precision**: mpmath with 50 decimal places (target < 1e-16 error)
- **Reproducibility**: Deterministic with fixed seeds (PCG64 RNG)

## Future Enhancements

Potential areas for extension:

1. **Multi-Scale Analysis**: Analyze invariant properties across multiple scales simultaneously
2. **Higher Dimensions**: Extend to 3D/4D tangent-based constraints
3. **Adaptive Thresholds**: Dynamic threshold adjustment based on N's properties
4. **Parallel Sampling**: Multi-threaded candidate generation
5. **GPU Acceleration**: CUDA/OpenCL for large-scale Monte Carlo validation
6. **Benchmark Suite**: Compare with existing factorization methods on RSA challenges

## References

- Monte Carlo Integration Theory: Law of large numbers, O(1/√N) convergence
- Geometric Invariants: Scale-independent properties in projective geometry
- Z5D Framework: Discrete domain normalization Z = n(Δₙ / Δₘₐₓ)
- Gaussian Integer Lattice: ℤ[i] = {a + bi : a, b ∈ ℤ}
- Tangent Perpendicularity: Fundamental property of circle tangents

## License

Part of the z-sandbox repository. See repository LICENSE for details.
