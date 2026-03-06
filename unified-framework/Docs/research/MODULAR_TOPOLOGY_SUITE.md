# Modular Topology Visualization Suite

A comprehensive visualization suite for discrete data using helical and modular-geodesic embeddings, built on the Z Framework's mathematical foundations.

## Features

- **Generalized θ′(n, k) Embedding**: Extends the golden ratio modular transformation for arbitrary discrete datasets
- **3D/5D Helical Visualizations**: Interactive helical and spiral plots using Plotly
- **Pattern Analysis**: Automated detection of clusters, symmetries, and anomalies in geometric space
- **Web Interface**: Flask/Dash-based interactive web application
- **Data Export**: Publication-quality export functionality for coordinates, images, and analysis reports
- **High Precision**: Mathematical computations with mpmath (50 decimal precision)

## Components

### Core Classes

1. **GeneralizedEmbedding**: Implements θ′(n, k) transformations and coordinate generation
2. **TopologyAnalyzer**: Detects patterns, clusters, symmetries, and anomalies
3. **VisualizationEngine**: Creates interactive 3D/5D visualizations
4. **DataExporter**: Handles export of coordinates, reports, and images

### Applications

1. **modular_topology_suite.py**: Core mathematical and visualization functionality
2. **topology_web_interface.py**: Interactive web interface using Dash
3. **cli_demo.py**: Command-line interface for batch processing

## Usage

### Command Line Interface

```bash
# Analyze prime numbers with cluster detection
python3 cli_demo.py --dataset primes --limit 200 --k 0.3 --analyze-clusters --show-summary

# Analyze Fibonacci sequence with full analysis
python3 cli_demo.py --dataset fibonacci --limit 100 --analyze-clusters --analyze-symmetries --analyze-anomalies --export-coords --export-report

# Custom dataset analysis
python3 cli_demo.py --dataset custom --file data.txt --k 0.25 --modulus 2.718 --export-images
```

### Web Interface

```bash
# Launch web interface
python3 src/applications/topology_web_interface.py
# Open browser to http://localhost:8050
```

### Python API

```python
from modular_topology_suite import GeneralizedEmbedding, TopologyAnalyzer, VisualizationEngine

# Initialize components
embedding = GeneralizedEmbedding(modulus=1.618)
analyzer = TopologyAnalyzer()
visualizer = VisualizationEngine()

# Generate data and embeddings
sequence = [2, 3, 5, 7, 11, 13, 17, 19, 23]
theta_transformed = embedding.theta_prime_transform(sequence, k=0.3)
coordinates = embedding.helical_5d_embedding(sequence, theta_transformed)

# Analyze patterns
clusters, stats = analyzer.detect_clusters(coordinates)
symmetries = analyzer.detect_symmetries(coordinates)
anomalies, scores = analyzer.detect_anomalies(coordinates)

# Create visualizations
fig_3d = visualizer.plot_3d_helical_embedding(coordinates)
fig_clusters = visualizer.plot_cluster_analysis(coordinates, clusters, stats)
```

## Mathematical Foundations

### θ′(n, k) Transformation

The generalized modular-geodesic embedding:

```
θ′(n, k) = modulus · ((n mod modulus)/modulus)^k
```

Where:
- `n` is the input sequence value
- `k` is the curvature parameter (typically 0.3 for optimal prime enhancement)
- `modulus` is the modular base (φ ≈ 1.618 for golden ratio)

### 5D Helical Embedding

Maps discrete sequences to 5D helical coordinates:

```
x = a * cos(θ_D)
y = a * sin(θ_E) 
z = κ(n) = d(n) · ln(n+1)/e²
w = normalized intensity
u = normalized transformed values
```

### Curvature Function

Frame-normalized curvature for geodesic analysis:

```
κ(n) = d(n) · ln(n+1)/e²
```

Where `d(n)` is the number of divisors of `n`.

## Applications

### Prime Number Analysis
- Reveals clustering patterns in prime distributions
- Detects geometric anomalies and symmetries
- Optimal curvature parameter k* ≈ 0.3 for conditional prime density improvement under canonical benchmark methodology

### Integer Sequence Visualization
- Fibonacci sequences show golden ratio spiral patterns
- Mersenne numbers exhibit exponential growth visualizations
- Custom sequences reveal hidden geometric structures

### Network Data Analysis
- Node connectivity patterns in helical space
- Community detection through geometric clustering
- Anomaly detection in network topologies

## Export Capabilities

### Coordinate Data
- CSV format for spreadsheet analysis
- JSON format for web applications
- HDF5 format for large datasets

### Visualizations
- PNG/PDF for publications
- HTML for interactive web sharing
- SVG for vector graphics

### Analysis Reports
- Comprehensive JSON reports with:
  - Cluster statistics and properties
  - Symmetry analysis results
  - Anomaly detection metrics
  - Coordinate statistics

## Testing

Run the comprehensive test suite:

```bash
export PYTHONPATH=/path/to/unified-framework
python3 tests/test_modular_topology_suite.py
```

The test suite covers:
- Mathematical accuracy of transformations
- Visualization component functionality
- Data export/import capabilities
- Performance with large datasets
- Integration workflows

## Dependencies

- numpy: Numerical computations
- matplotlib: 2D plotting backend
- plotly: Interactive 3D visualizations
- dash: Web interface framework
- pandas: Data manipulation
- scikit-learn: Machine learning algorithms
- scipy: Scientific computing
- mpmath: High-precision arithmetic
- sympy: Symbolic mathematics

## Performance

- **Small datasets** (< 100 points): Sub-second processing
- **Medium datasets** (100-1000 points): ~2 seconds
- **Large datasets** (1000+ points): Scales linearly with high precision maintained

## Integration with Z Framework

The visualization suite extends the existing Z Framework capabilities:

- Builds upon `src/core/domain.py` DiscreteZetaShift embeddings
- Uses `src/core/axioms.py` mathematical foundations
- Integrates with existing hologram visualizations in `src/number-theory/prime-curve/`
- Maintains high-precision arithmetic standards (mpmath dps=50)

## Educational Applications

- Interactive exploration of number theory concepts
- Visualization of modular arithmetic properties
- Geometric interpretation of prime distributions
- Pattern recognition in discrete sequences

## Research Applications

- Analysis of prime number distributions
- Investigation of integer sequence properties
- Network topology analysis
- Anomaly detection in discrete data
- Publication-ready visualization generation

## Future Extensions

- Support for complex number sequences
- Additional clustering algorithms
- Real-time data streaming capabilities
- Machine learning pattern classification
- Integration with mathematical databases