# Advanced Hologram Visualizations for Z Framework

This document provides comprehensive examples and documentation for the enhanced `hologram.py` module, which supports advanced geometric visualizations relevant to the Z framework.

## Overview

The enhanced hologram visualization system provides:

- **Modular Architecture**: Class-based design with configurable parameters
- **Advanced Visualizations**: Enhanced logarithmic spirals, Gaussian prime spirals, modular tori, and 5D projections
- **Interactive Exploration**: Parameter variation and batch generation capabilities
- **Z Framework Integration**: Uses golden ratio transforms and 5D helical embeddings
- **Comprehensive Documentation**: Full API documentation and examples

## Key Features

### 1. Enhanced Logarithmic Spirals
- Configurable spiral rates and height scaling methods
- Support for 2D and 3D projections
- Prime highlighting with customizable colors and markers

### 2. Gaussian Prime Spirals
- Multiple angle increment schemes (golden ratio, π-based, custom)
- Optional connection lines between prime points
- Helical coordinate mapping

### 3. Modular Tori
- Configurable modular bases and torus parameters
- Residue class filtering and coloring
- Wireframe torus visualization

### 4. 5D Projections
- Helical embeddings using Z framework transforms
- Multiple projection types (helical, orthogonal, perspective)
- Geodesic line visualization between primes

### 5. Interactive Parameter Exploration
- Batch generation with parameter variations
- Automated file saving and organization
- Statistical analysis and reporting

## Quick Start

```python
from hologram import AdvancedHologramVisualizer

# Create visualizer with 1000 data points
visualizer = AdvancedHologramVisualizer(n_points=1000)

# Generate all visualizations and save to files
visualizer.visualize_all(save_plots=True, output_dir="./visualizations")

# Get statistics about the data
stats = visualizer.get_statistics()
print(f"Generated {stats['prime_count']} primes out of {stats['n_points']} points")
```

## Detailed Examples

### Example 1: Basic 3D Prime Geometry

```python
from hologram import AdvancedHologramVisualizer

# Initialize with custom parameters
visualizer = AdvancedHologramVisualizer(
    n_points=2000,
    helix_freq=0.15,
    use_log_scale=True,
    figure_size=(14, 10)
)

# Create basic 3D prime geometry visualization
fig = visualizer.prime_geometry_3d(save_path="prime_geometry.png")
```

### Example 2: Enhanced Logarithmic Spirals

```python
# Different spiral configurations
spiral_configs = [
    {
        'spiral_rate': 0.1,
        'height_scale': 'sqrt',
        'projection': '3d'
    },
    {
        'spiral_rate': 0.2,
        'height_scale': 'log',
        'projection': '3d'
    },
    {
        'spiral_rate': 0.05,
        'height_scale': 'linear',
        'projection': '2d'
    }
]

for i, config in enumerate(spiral_configs):
    fig = visualizer.logarithmic_spiral(
        **config,
        save_path=f"spiral_{i+1}.png"
    )
```

### Example 3: Gaussian Prime Spirals with Different Angle Schemes

```python
# Golden ratio angle increments (recommended)
fig1 = visualizer.gaussian_prime_spiral(
    angle_increment='golden',
    connection_lines=True,
    save_path="gaussian_golden.png"
)

# π-based angle increments
fig2 = visualizer.gaussian_prime_spiral(
    angle_increment='pi',
    connection_lines=False,
    save_path="gaussian_pi.png"
)

# Custom angle increments
fig3 = visualizer.gaussian_prime_spiral(
    angle_increment='custom',
    connection_lines=True,
    save_path="gaussian_custom.png"
)
```

### Example 4: Configurable Modular Tori

```python
# Different modular bases and torus parameters
torus_configs = [
    {
        'mod1': 17,
        'mod2': 23,
        'torus_ratio': 3.0,
        'residue_filter': 6
    },
    {
        'mod1': 11,
        'mod2': 13,
        'torus_ratio': 2.5,
        'residue_filter': 4
    },
    {
        'mod1': 7,
        'mod2': 19,
        'torus_ratio': 4.0,
        'residue_filter': 8
    }
]

for i, config in enumerate(torus_configs):
    fig = visualizer.modular_torus(
        **config,
        save_path=f"torus_{i+1}.png"
    )
```

### Example 5: 5D Projections with Z Framework

```python
# Different 5D projection types
projection_configs = [
    {
        'projection_type': 'helical',
        'dimensions': (0, 1, 2)  # x, y, z coordinates
    },
    {
        'projection_type': 'orthogonal',
        'dimensions': (1, 2, 3)  # y, z, w coordinates
    },
    {
        'projection_type': 'perspective',
        'dimensions': (0, 2, 4)  # x, z, u coordinates
    }
]

for i, config in enumerate(projection_configs):
    fig = visualizer.projection_5d(
        **config,
        save_path=f"projection_5d_{i+1}.png"
    )
```

### Example 6: Riemann Zeta Landscape

```python
# Enhanced zeta landscape with custom parameters
fig = visualizer.riemann_zeta_landscape(
    real_range=(0.1, 1.0),
    imag_range=(10, 100),
    resolution=150,
    save_path="zeta_landscape.png"
)
```

### Example 7: Interactive Parameter Exploration

```python
# Run comprehensive exploration with multiple parameter sets
visualizer.interactive_exploration(
    save_plots=True,
    output_dir="./comprehensive_analysis"
)

# Get detailed statistics
stats = visualizer.get_statistics()
print("Analysis Statistics:")
print(f"- Data points: {stats['n_points']}")
print(f"- Prime count: {stats['prime_count']}")
print(f"- Prime density: {stats['prime_density']:.4f}")
print(f"- Helix frequency: {stats['helix_frequency']}")

if stats['embedding_statistics']:
    print("5D Embedding Statistics:")
    print(f"- Mean coordinates: {stats['embedding_statistics']['mean']}")
    print(f"- Std deviation: {stats['embedding_statistics']['std']}")
```

## Advanced Usage

### Custom Visualization Parameters

```python
# Customize visualization appearance
visualizer = AdvancedHologramVisualizer(n_points=5000)

# Modify color scheme
visualizer.prime_color = 'gold'
visualizer.prime_marker = '^'
visualizer.prime_size = 75
visualizer.nonprime_color = 'darkblue'
visualizer.nonprime_alpha = 0.4

# Generate visualization with custom colors
fig = visualizer.prime_geometry_3d()
```

### Integrating with Z Framework Core Modules

```python
# Use with Z framework core modules (when available)
try:
    from core.domain import UniversalZetaShift
    from core.axioms import universal_invariance
    
    # Create custom zeta shifts for specific analysis
    zeta_shift = UniversalZetaShift(10, 20, 30)
    z_value = zeta_shift.compute_z()
    
    # Integrate with hologram visualizations
    visualizer = AdvancedHologramVisualizer(n_points=1000)
    fig = visualizer.projection_5d(projection_type='helical')
    
except ImportError:
    print("Core Z framework modules not available - using local implementations")
```

### Batch Processing and Analysis

```python
# Analyze different scales and parameters
scales = [500, 1000, 2000, 5000]
results = {}

for scale in scales:
    visualizer = AdvancedHologramVisualizer(n_points=scale)
    stats = visualizer.get_statistics()
    results[scale] = stats
    
    # Generate scaled visualizations
    output_dir = f"./analysis_scale_{scale}"
    visualizer.interactive_exploration(save_plots=True, output_dir=output_dir)

# Compare results across scales
for scale, stats in results.items():
    print(f"Scale {scale}: {stats['prime_density']:.4f} prime density")
```

## API Reference

### AdvancedHologramVisualizer Class

#### Constructor Parameters
- `n_points` (int): Number of data points to generate (default: 5000)
- `helix_freq` (float): Frequency for helical coordinates (default: 0.1003033)
- `use_log_scale` (bool): Use logarithmic scaling for y-axis (default: False)
- `figure_size` (tuple): Size for matplotlib figures (default: (12, 8))

#### Key Methods

##### `prime_geometry_3d(save_path=None)`
Create 3D prime geometry visualization with ZetaShift transforms.

##### `logarithmic_spiral(spiral_rate=0.1, height_scale='sqrt', projection='3d', save_path=None)`
Enhanced logarithmic spiral with configurable parameters.
- `spiral_rate`: Rate of spiral growth
- `height_scale`: Height scaling method ('sqrt', 'log', 'linear')
- `projection`: Projection type ('3d', '2d')

##### `gaussian_prime_spiral(angle_increment='golden', connection_lines=True, save_path=None)`
Gaussian prime spirals with configurable angle increments.
- `angle_increment`: Angle increment type ('golden', 'pi', 'custom')
- `connection_lines`: Whether to draw lines between primes

##### `modular_torus(mod1=17, mod2=23, torus_ratio=3.0, residue_filter=6, save_path=None)`
Modular torus visualization with configurable parameters.
- `mod1`, `mod2`: Modular bases
- `torus_ratio`: Ratio of minor to major radius
- `residue_filter`: Residue class filter

##### `projection_5d(projection_type='helical', dimensions=(0,1,2), save_path=None)`
5D projections using helical embeddings from Z framework.
- `projection_type`: Type of projection ('helical', 'orthogonal', 'perspective')
- `dimensions`: Which 3 dimensions to project

##### `riemann_zeta_landscape(real_range=(0.1,1.0), imag_range=(10,50), resolution=100, save_path=None)`
Enhanced Riemann zeta landscape visualization.

##### `interactive_exploration(save_plots=False, output_dir="./hologram_output")`
Interactive exploration of all visualization types with parameter variations.

##### `get_statistics()`
Get statistical information about computed data including prime counts, density, and 5D embedding statistics.

## Mathematical Background

### Golden Ratio Transforms
The visualizations use golden ratio curvature transformations:
```
θ'(n,k) = φ·{n/φ}^k
```
where φ ≈ 1.618 is the golden ratio and k is the curvature parameter.

### 5D Helical Embeddings
Points are embedded in 5D space using:
- x = √n · cos(θ_D)
- y = √n · sin(θ_E)  
- z = Z/(e²) (frame normalized)
- w = log(n+1) (invariant dimension)
- u = n/c (relativistic dimension)

### Z Framework Integration
The system integrates with the Z framework's universal form Z = A(B/c) where:
- A is frame-dependent quantity
- B is rate
- c is the universal invariant (speed of light)

## Performance Notes

- For large datasets (n_points > 10,000), some visualizations may take several minutes
- 5D projections are computationally intensive and recommended for n_points < 5,000
- File saving adds overhead but enables batch analysis
- Memory usage scales approximately O(n_points) for most visualizations

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the correct directory and PYTHONPATH is set
2. **Memory Issues**: Reduce n_points for large visualizations
3. **Slow Performance**: Use smaller datasets for testing, larger for final analysis
4. **Missing Plots**: Check that matplotlib backend is properly configured for your environment

### Environment Setup

```bash
# Set up environment
cd /path/to/unified-framework/src/number-theory/prime-curve
export PYTHONPATH=/path/to/unified-framework

# Install dependencies
pip install numpy matplotlib scipy

# Run basic test
python3 -c "from hologram import AdvancedHologramVisualizer; v = AdvancedHologramVisualizer(100); print('Success!')"
```

This enhanced hologram visualization system provides powerful tools for exploring geometric phenomena in number theory through the lens of the Z framework, enabling both mathematical research and educational visualization.