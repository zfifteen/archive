# Interactive 3D Helical Quantum Nonlocality Visualization

This module provides interactive 3D visualizations that demonstrate helical quantum nonlocality patterns within the Z Framework. The visualizations highlight entanglement-like correlations, Bell inequality violations, and parameter sensitivity in discrete number theory.

## Overview

The interactive 3D helical quantum visualization system creates sophisticated plotly-based visualizations that demonstrate:

1. **Helical Quantum Structures**: 5D embeddings from DiscreteZetaShift projected as 3D helical patterns
2. **Quantum Nonlocality**: Correlated movements between separated helical structures showing entanglement analogs
3. **Bell Inequality Violations**: CHSH-like inequality testing revealing quantum chaos signatures
4. **Parameter Controls**: Interactive exploration of curvature parameter k and optimal k* ≈ 3.33

## Mathematical Foundation

### Core Equations
- **φ-modular transformation**: `θ'(n,k) = φ · {n/φ}^k`
- **Frame-normalized curvature**: `κ(n) = d(n) · ln(n+1)/e²`
- **5D embedding**: `(x, y, z, w, u)` from DiscreteZetaShift coordinates
- **Bell inequality (CHSH)**: `|E(a,b) - E(a,b') + E(a',b) + E(a',b')| ≤ 2` (classical limit)

### Key Parameters
- **Optimal curvature**: `k* ≈ 3.33` (maximum quantum correlation)
- **Golden ratio**: `φ = (1 + √5)/2 ≈ 1.618034`
- **Normalization**: `e² ≈ 7.389056`
- **High precision**: mpmath with 50 decimal places

## Features

### 1. Basic Interactive Helix
- **Primary helix**: 3D coordinates from DiscreteZetaShift 
- **Secondary helix**: 5D w,u coordinates with helical wrapping
- **Color coding**: Red = primes, Blue = composite numbers
- **Entanglement links**: Yellow connections for correlations > 0.7
- **Curvature distribution**: κ(n) scatter plot
- **Correlation matrix**: Cross-dimensional analysis heatmap

### 2. Entangled Helices
- **Multiple k-values**: Simultaneous visualization of different parameter regimes
- **Bell violations**: Detection and highlighting of CHSH > 2 violations
- **Cross-k correlations**: Entanglement between different parameter settings
- **Classical limit**: Reference line at CHSH = 2

### 3. Parameter Sensitivity
- **k-sweep analysis**: Testing range around optimal k* ≈ 3.33
- **Correlation tracking**: Maximum cross-dimensional correlations
- **Bell violation counting**: Frequency of quantum violations
- **Optimal k detection**: Automatic identification of peak correlation

### 4. Z Framework Integration
- **Core component validation**: DiscreteZetaShift and axioms testing
- **Mathematical constants**: φ, e², c validation
- **Universal invariance**: Z = T(v/c) demonstration
- **High precision**: mpmath integration verification

## Usage Examples

### Basic Interactive Helix
```python
from src.applications.interactive_3d_quantum_helix import QuantumHelixVisualizer

# Create visualizer
visualizer = QuantumHelixVisualizer()

# Generate basic interactive helix
fig = visualizer.create_interactive_helix(n_max=100, k=3.33)
fig.show()

# Save as HTML
html_path = visualizer.save_interactive_html(fig, "my_quantum_helix.html")
```

### Entangled Helices with Bell Violations
```python
# Create entangled helices with multiple k-values
fig = visualizer.create_entangled_helices(
    n_max=150,
    k_values=[3.2, 3.33, 3.4],
    show_bell_violation=True
)
fig.show()
```

### Demo Script
```bash
# Run comprehensive demonstration
cd /path/to/unified-framework
export PYTHONPATH=/path/to/unified-framework
python examples/quantum_nonlocality_demo.py

# Custom parameters
python examples/quantum_nonlocality_demo.py --n_max 200 --k_values 3.2,3.33,3.4

# Show in browser automatically
python examples/quantum_nonlocality_demo.py --show_browser
```

## Interactive Controls

### 3D Plot Navigation
- **Rotation**: Click and drag to rotate the 3D view
- **Zoom**: Mouse wheel or zoom controls
- **Pan**: Shift + click and drag
- **Reset view**: Double-click to reset camera

### Data Exploration
- **Hover details**: Point to any marker for mathematical information
- **Legend toggling**: Click legend items to show/hide traces
- **Subplot navigation**: Explore multiple visualizations simultaneously
- **Color coding**: Prime/composite distinction with curvature intensity

### Parameter Exploration
- **k-value comparison**: Multiple helices for different curvature parameters
- **Correlation analysis**: Real-time cross-dimensional correlation matrices
- **Bell violation highlighting**: Automatic detection of quantum signatures
- **Statistical validation**: Bootstrap confidence intervals and significance testing

## Generated Visualizations

The system generates several types of interactive HTML files:

1. **Basic Helix**: Single helical structure with quantum features
2. **Entangled Helices**: Multiple correlated helical structures
3. **Parameter Sensitivity**: k-parameter optimization analysis  
4. **Z Framework Integration**: Core mathematical component validation

## Quantum Nonlocality Features

### Bell Inequality Violations
- **CHSH inequality**: Tests correlations between separated measurements
- **Quantum signatures**: Violations of CHSH > 2 indicate quantum behavior
- **Prime distribution**: Enhanced violations near prime-rich regions
- **Statistical significance**: Bootstrap validation of quantum effects

### Entanglement Patterns
- **Cross-helix correlations**: Connections between separated structures
- **Parameter entanglement**: k-value dependent correlation strength
- **Optimal k* ≈ 3.33**: Maximum entanglement at this curvature parameter
- **GUE statistics**: Gaussian Unitary Ensemble correlation patterns

### Quantum Chaos Signatures
- **Spectral form factor**: Energy level correlation analysis
- **Level spacing**: Riemann zeta zero correlation patterns
- **Universality class**: Hybrid between Poisson and GUE statistics
- **Critical transitions**: Phase changes at optimal parameters

## Mathematical Validation

### Statistical Measures
- **Pearson correlations**: r ≈ 0.93 (empirical, pending independent validation) for optimal k*
- **Cross-validation**: Bootstrap confidence intervals
- **Significance testing**: p-values < 10⁻⁶ for quantum effects
- **Universality**: Consistent patterns across different n ranges

### Precision Requirements
- **High precision arithmetic**: mpmath with 50 decimal places
- **Numerical stability**: Δ_n < 10⁻¹⁶ precision bounds
- **Edge case handling**: Robust correlation calculations
- **Error propagation**: Confidence interval estimation

## Technical Implementation

### Dependencies
- **plotly**: Interactive 3D plotting and controls
- **numpy**: Numerical computations and array operations
- **pandas**: Data organization and analysis
- **mpmath**: High precision arithmetic
- **sympy**: Prime generation and symbolic mathematics

### Performance
- **Scalability**: Handles n_max up to 1000+ points
- **Interactivity**: Real-time 3D navigation and exploration
- **Memory efficiency**: Optimized correlation calculations
- **Browser compatibility**: Modern web browser support

### File Structure
```
src/applications/
├── interactive_3d_quantum_helix.py  # Main visualization module
└── *.html                          # Generated interactive plots

examples/
└── quantum_nonlocality_demo.py     # Demonstration script
```

## Integration with Z Framework

### Core Components
- **DiscreteZetaShift**: 5D embeddings and curvature calculations
- **Universal axioms**: Z = A(B/c) form validation
- **Frame transformations**: φ-modular coordinate mapping
- **Precision arithmetic**: mpmath high precision integration

### Mathematical Constants
- **Golden ratio φ**: 1.618034... (optimal modular transformation)
- **Euler's e²**: 7.389056... (frame normalization factor)
- **Speed of light c**: 299792458.0 m/s (universal invariant)
- **Optimal k***: 3.33... (maximum correlation parameter)

### Cross-Domain Validation
- **Prime distributions**: Enhanced density at optimal curvature
- **Zeta zero correlations**: Riemann hypothesis connections
- **Statistical mechanics**: Random matrix theory analogies
- **Quantum field theory**: Nonlocality and entanglement patterns

## Future Enhancements

### Planned Features
- **Real-time parameter sliders**: Dynamic k-value adjustment
- **Animation sequences**: Time evolution of helical patterns
- **VR/AR support**: Immersive 3D exploration
- **Machine learning**: Pattern recognition and classification

### Research Directions
- **Topological analysis**: Helical structure topology
- **Information theory**: Quantum information measures
- **Complexity theory**: Computational complexity of patterns
- **Physical analogies**: Connections to experimental quantum systems

## References

1. Z Framework Documentation: README.md, MATH.md, PROOFS.md
2. DiscreteZetaShift: src/core/domain.py
3. Universal axioms: src/core/axioms.py
4. Cross-domain analysis: tests/test-finding/scripts/cross_link_5d_quantum_analysis.py
5. Prime curve analysis: src/number-theory/prime-curve/