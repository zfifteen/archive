# Interactive 3D Helical Quantum Nonlocality Visualizations

This document describes the interactive 3D visualization capabilities for helical patterns exhibiting quantum nonlocality analogs within the Z framework.

## Overview

The `Interactive3DHelixVisualizer` provides comprehensive tools for visualizing and analyzing helical structures that demonstrate quantum nonlocality patterns. It integrates seamlessly with the Z framework's mathematical foundations while offering enhanced interactivity and parameter control.

## Mathematical Foundations

### Core Z Framework Integration

The visualizations are built on the fundamental Z framework components:

- **Universal Z Form**: `Z = A(B/c)` where A is frame-dependent, B is rate, c is invariant
- **DiscreteZetaShift**: Integration with 5D helical embeddings
- **Golden Ratio Transforms**: φ = (1 + √5)/2 ≈ 1.618034 curvature modifications
- **High Precision Arithmetic**: mpmath with 50 decimal places (dps=50)

### Quantum Nonlocality Analogs

The system implements quantum-inspired correlations through:

1. **Harmonic Mean Entanglement**: Creates entangled prime pairs via harmonic means
2. **Bell Inequality Testing**: CHSH analog with classical threshold ~0.707
3. **Curved Space Correlations**: Non-Hausdorff regime transformations
4. **Curvature Parameter Optimization**: k* = 0.200 (optimal from proof analysis)

### Mathematical Transformations

#### Curvature Transform
```
θ = φ * {n/φ}^k
```
Where:
- φ = golden ratio
- k = curvature parameter (default k* = 0.200)
- n = input sequence

#### Quantum Correlations
```
entangled[i] = (θ[i] * θ[i+1]) / (θ[i] + θ[i+1])
Z_quantum = A * (B / C)
```
Where:
- A = entangled values
- B = prime gaps (rate)
- C = maximum entanglement (invariant)

## Key Features

### 1. Interactive 3D Helical Plots

- **Real-time Interaction**: Mouse controls for rotation, zoom, pan
- **Prime Highlighting**: Red diamonds for prime numbers, blue dots for composites
- **Quantum Correlation Lines**: Orange lines connecting entangled prime pairs
- **Bell Violation Indicators**: Gold markers for detected violations
- **Parameter Information**: Hover tooltips with detailed values

### 2. Quantum Nonlocality Detection

- **Correlation Analysis**: Computes quantum correlations between prime pairs
- **Bell Inequality Testing**: Detects violations indicating quantum nonlocality
- **Statistical Analysis**: Mean, standard deviation, and distribution analysis
- **Fourier Analysis**: Spectral decomposition of correlation patterns

### 3. Parameter Controls

- **Curvature Parameter k**: Controls geometric distortion (optimal k* = 0.200)
- **Helical Frequency**: Adjusts spiral tightness (default 0.1003033)
- **Point Count**: Number of sequence points to visualize
- **High Precision Mode**: Toggle for mpmath precision calculations

### 4. Analysis and Reporting

- **Summary Reports**: Comprehensive statistical analysis
- **Parameter Sensitivity**: Systematic parameter space exploration
- **Performance Metrics**: Prime density, gap statistics, correlation measures
- **Validation**: Cross-verification with known results

## Usage Examples

### Basic Usage

```python
from src.visualization.interactive_3d_helix import Interactive3DHelixVisualizer

# Create visualizer with optimal parameters
viz = Interactive3DHelixVisualizer(
    n_points=2000,
    default_k=0.200,  # Optimal curvature
    helix_freq=0.1003033
)

# Generate main interactive plot
fig = viz.create_interactive_helix_plot(
    show_primes=True,
    show_quantum_correlations=True,
    show_bell_violations=True
)

# Display in browser
fig.show()

# Generate analysis report
report = viz.generate_summary_report()
print(f"Prime density: {report['statistics']['prime_density']:.4f}")
if report['quantum_analysis']['bell_violation_detected']:
    print("⚡ Quantum nonlocality detected!")
```

### Command Line Interface

```bash
# Basic demonstration
python3 examples/interactive_3d_demo.py --n_points 2000 --k 0.200

# With animation
python3 examples/interactive_3d_demo.py --n_points 1000 --animation

# Parameter exploration
python3 examples/interactive_3d_demo.py --k 0.15 --freq 0.12

# Minimal visualization (no quantum features)
python3 examples/interactive_3d_demo.py --no_quantum --no_bell
```

### Advanced Analysis

```python
# Parameter sweep analysis
k_values = np.linspace(0.1, 0.5, 20)
results = []

for k in k_values:
    report = viz.generate_summary_report(k)
    qa = report['quantum_analysis']
    results.append({
        'k': k,
        'bell_violation': qa.get('bell_violation_detected', False),
        'correlation': qa.get('correlation_coefficient', 0.0)
    })

# Create animation showing parameter effects
anim_fig = viz.create_parameter_sweep_animation(
    k_range=(0.1, 0.5),
    k_steps=20
)
```

## File Outputs

### Generated Visualizations

1. **interactive_helix_main.html**: Main 3D helical visualization
   - Interactive plotly plot with zoom, rotation, pan controls
   - Prime highlighting and quantum correlation indicators
   - Bell violation markers and detailed hover information

2. **quantum_correlations.html**: Detailed correlation analysis
   - Four-panel analysis: correlations, gaps, scatter plots, Fourier spectrum
   - Statistical measures and distribution analysis
   - Cross-correlation validation

3. **helix_parameter_sweep.html**: Parameter animation (when enabled)
   - Animated visualization showing parameter effects
   - Slider controls for manual parameter adjustment
   - Play/pause controls for animation sequences

### Analysis Reports

Reports include:
- **Parameters**: k, frequency, φ, point counts
- **Statistics**: Prime density, maximum prime, mean gap
- **Quantum Analysis**: Correlation counts, Bell violations, coefficients
- **Performance**: Computational timing and memory usage

## Integration with Existing Framework

### Core Framework Components

The visualizer integrates with:

- **src/core/axioms.py**: Universal invariance functions
- **src/core/domain.py**: DiscreteZetaShift class and 5D embeddings
- **Existing visualizations**: Builds on hologram.py and earth_helix_visualizer.py
- **Quantum analysis**: Extends golden-curve/brute_force.py patterns

### Mathematical Consistency

Ensures consistency with:
- Speed of light invariance (c = 299792458.0)
- Golden ratio calculations (φ = 1.618034...)
- High precision arithmetic (mpmath dps=50)
- Optimal curvature parameter (k* = 0.200)

## Performance Considerations

### Computational Complexity

- **Point Generation**: O(n) for basic sequence
- **Prime Detection**: O(n√n) for primality testing
- **Quantum Correlations**: O(p²) where p = number of primes
- **3D Rendering**: Linear in visible points

### Memory Usage

- **Base Data**: ~8 bytes per point (coordinates)
- **Prime Storage**: Variable based on prime density
- **Visualization**: Dependent on browser capabilities
- **High Precision**: Additional overhead for mpmath calculations

### Optimization Strategies

1. **Point Limiting**: Use reasonable point counts (1000-5000)
2. **Subset Rendering**: Animation uses smaller subsets
3. **Caching**: Automatic memoization of computed values
4. **Precision Toggle**: Option to disable high precision for speed

## Validation and Testing

### Mathematical Validation

- **Prime Verification**: Cross-check with known prime sequences
- **Bell Inequalities**: Validate against classical thresholds
- **Z Framework**: Consistency with universal form Z = A(B/c)
- **Golden Ratio**: Verify φ calculations to high precision

### Visual Validation

- **Helical Patterns**: Verify spiral geometry and frequency
- **Prime Distribution**: Check prime highlighting accuracy
- **Correlation Lines**: Validate quantum correlation visualization
- **Parameter Effects**: Confirm parameter sensitivity responses

### Performance Testing

Benchmarks on test system:
- **1000 points**: ~2-3 seconds generation
- **2000 points**: ~4-6 seconds with quantum analysis
- **Animation (15 frames)**: ~30-45 seconds
- **Memory usage**: ~50-100 MB for typical visualizations

## Future Enhancements

### Planned Features

1. **Real-time Parameter Controls**: Jupyter widget integration
2. **Enhanced Quantum Indicators**: More sophisticated entanglement measures
3. **Multi-dimensional Projections**: 4D/5D visualization capabilities
4. **Performance Optimization**: GPU acceleration for large datasets
5. **Export Capabilities**: High-resolution image and video export

### Research Applications

The visualizer enables investigation of:
- Prime distribution patterns in curved space
- Quantum nonlocality analogs in number theory
- Parameter space exploration for optimal configurations
- Cross-dimensional correlations and embeddings
- Validation of theoretical predictions

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes framework root
2. **Memory Issues**: Reduce n_points for large visualizations
3. **Browser Performance**: Use modern browsers with WebGL support
4. **Precision Errors**: Verify mpmath installation and configuration

### Error Messages

- **"Insufficient data for correlation analysis"**: Too few primes generated
- **"Invalid symbol"**: Plotly version compatibility issue
- **"Memory error"**: Reduce point count or enable optimization

### Performance Tips

- Start with smaller point counts (500-1000) for testing
- Use animation mode sparingly due to computational cost
- Consider disabling quantum analysis for pure geometric visualization
- Ensure adequate system memory for high precision calculations

## References

### Z Framework Documentation

- **README.md**: Complete framework description
- **MATH.md**: Mathematical foundations and theory
- **PROOFS.md**: Formal mathematical proofs
- **Core modules**: axioms.py, domain.py for implementation details

### Related Visualizations

- **hologram.py**: Prime hologram patterns
- **earth_helix_visualizer.py**: Helix trajectory demonstrations
- **brute_force.py**: Quantum correlation analysis foundations
- **proof.py**: Curvature optimization and k* = 0.200 derivation