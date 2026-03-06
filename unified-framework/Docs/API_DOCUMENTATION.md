# Universal Invariant Scoring Engine API Documentation

The Universal Invariant Scoring Engine provides Z-invariant based scoring and density analysis for arbitrary sequences including numerical, biological, and network data.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Python Client](#python-client)
- [Data Types](#data-types)
- [Examples](#examples)
- [Mathematical Background](#mathematical-background)

## Overview

The Z-score API leverages the Z Framework's mathematical foundations to provide:

- **Universal Scoring**: Z-invariant scores comparable across different data domains
- **Density Analysis**: Prime-based algorithms with conditional best-bin uplift under canonical benchmark methodology: N=1,000,000 integers, B=20 bins, k*=0.3, bootstrap 10,000 resamples, seed=42
- **Anomaly Detection**: Geometric and statistical anomaly detection using curvature-based methods
- **Cross-Domain Normalization**: Enables benchmarking between numerical, biological, and network data
- **High-Precision Computing**: Uses mpmath with 50-100 decimal places for numerical stability at ultra-extreme scales

## Quick Start

### 1. Start the API Server

```bash
cd /path/to/unified-framework
export PYTHONPATH=$(pwd)
python3 -m src.api.server
```

The server will start on `http://localhost:5000` by default.

### 2. Test with curl

```bash
# Health check
curl http://localhost:5000/health

# Score a numerical sequence
curl -X POST http://localhost:5000/api/score \
  -H "Content-Type: application/json" \
  -d '{"data": [1, 2, 3, 4, 5], "data_type": "numerical"}'

# Score a biological sequence
curl -X POST http://localhost:5000/api/score \
  -H "Content-Type: application/json" \
  -d '{"data": "ATGCATGC", "data_type": "biological"}'
```

### 3. Use Python Client

```python
from src.api.client import ZScoreAPIClient

# Initialize client
client = ZScoreAPIClient("http://localhost:5000")

# Score different data types
numerical_score = client.score_numerical([1, 2, 3, 4, 5])
biological_score = client.score_biological("ATGCATGC")
network_score = client.score_network([[0, 1], [1, 0]])

print(f"Scores: {numerical_score:.3f}, {biological_score:.3f}, {network_score:.3f}")
```

## API Reference

### Base URL
`http://localhost:5000`

### Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Universal Invariant Scoring Engine",
  "version": "1.0.0"
}
```

#### POST /api/score
Score a single sequence.

**Request Body:**
```json
{
  "data": [1, 2, 3, 4, 5],
  "data_type": "numerical"  // optional: "numerical", "biological", "network", "auto"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "metadata": {
      "type": "numerical",
      "length": 5,
      "mean": 3.0,
      "std": 1.4142135623730951,
      "min": 1.0,
      "max": 5.0
    },
    "z_invariant_score": 54.745542,
    "z_scores": {
      "mean_z": 109.491084,
      "std_z": 0.0,
      "max_z": 109.491084,
      "min_z": 109.491084,
      "universal_invariance": 0.0,
      "composite_score": 54.745542
    },
    "density_metrics": {
      "basic_density": 1.25,
      "cluster_variance": 0.0625,
      "prime_density": 0.0,
      "enhancement_factor": 1.0
    },
    "anomaly_scores": {
      "statistical_anomalies": 0.0,
      "curvature_anomalies": 1.0,
      "frame_anomalies": 0.0,
      "composite_anomaly_score": 0.3333333333333333
    },
    "normalized_sequence": [0.0, 0.25, 0.5, 0.75, 1.0],
    "sequence_length": 5
  }
}
```

#### POST /api/batch_score
Score multiple sequences in batch.

**Request Body:**
```json
{
  "data_list": [
    [1, 2, 3, 4, 5],
    "ATGCATGC",
    [[0, 1], [1, 0]]
  ],
  "data_types": ["numerical", "biological", "network"]  // optional
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "batch_index": 0,
      "metadata": {...},
      "z_invariant_score": 54.745542,
      ...
    },
    ...
  ],
  "total_processed": 3
}
```

#### POST /api/analyze
Comprehensive sequence analysis with detailed breakdown.

**Request Body:**
```json
{
  "data": [1, 2, 3, 4, 5],
  "data_type": "numerical",
  "include_normalized": true,
  "detailed_metrics": true
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "metadata": {...},
    "summary": {
      "z_invariant_score": 54.745542,
      "composite_anomaly_score": 0.333,
      "enhancement_factor": 1.0,
      "sequence_length": 5
    },
    "z_scores": {...},
    "density_metrics": {...},
    "anomaly_scores": {...},
    "normalized_sequence": [0.0, 0.25, 0.5, 0.75, 1.0]
  }
}
```

#### GET /api/info
Get API information and supported data types.

**Response:**
```json
{
  "service": "Universal Invariant Scoring Engine",
  "version": "1.0.0",
  "description": "Z-invariant based scoring and density analysis for arbitrary sequences",
  "supported_data_types": [...],
  "endpoints": [...]
}
```

For complete documentation, examples, and mathematical background, see the full API documentation.

## Python Client

### Installation

The Python client is included with the Z Framework installation:

```python
from src.api.client import ZFrameworkClient

# Initialize client
client = ZFrameworkClient(base_url="http://localhost:5000")
```

### Basic Usage

```python
# Score a numerical sequence
result = client.score([1, 2, 3, 5, 8, 13, 21], data_type="numerical")
print(f"Z-invariant score: {result['z_invariant_score']}")

# Score a biological sequence
bio_result = client.score("ATGCGTACGTAGC", data_type="biological")
print(f"Biological Z-score: {bio_result['z_invariant_score']}")

# Batch scoring
batch_results = client.batch_score([
    [1, 2, 3, 4, 5],
    "ATGCATGC",
    [[0, 1], [1, 0]]
], data_types=["numerical", "biological", "network"])
```

### Advanced Features

```python
# Detailed analysis
analysis = client.analyze([1, 2, 3, 5, 8, 13], 
                         data_type="numerical",
                         include_normalized=True,
                         detailed_metrics=True)

# Access specific metrics
z_score = analysis['z_scores']['composite_score']
anomaly_score = analysis['anomaly_scores']['composite_anomaly_score']
enhancement = analysis['density_metrics']['enhancement_factor']
```

## Data Types

### Supported Input Types

#### Numerical Sequences
- **Type**: `"numerical"`
- **Format**: Array of numbers `[1, 2, 3, 4, 5]`
- **Processing**: Applies Z-invariant transformations and prime-based analysis
- **Example**: `[1, 2, 3, 5, 8, 13, 21, 34]` (Fibonacci sequence)

#### Biological Sequences
- **Type**: `"biological"`
- **Format**: String of nucleotides `"ATGCGTAC"`
- **Processing**: Converts to numerical via ASCII/position encoding
- **Example**: `"ATGCATGCTAGCTAGC"` (DNA sequence)

#### Network/Graph Data
- **Type**: `"network"`
- **Format**: Adjacency matrix `[[0, 1], [1, 0]]`
- **Processing**: Flattens and applies graph-theoretic Z-transformations
- **Example**: `[[0, 1, 0], [1, 0, 1], [0, 1, 0]]` (3-node graph)

### Output Data Structure

All responses include:

```json
{
  "metadata": {
    "type": "string",          // Input data type
    "length": "integer",       // Sequence length
    "mean": "float",           // Statistical mean
    "std": "float",            // Standard deviation
    "min": "float",            // Minimum value
    "max": "float"             // Maximum value
  },
  "z_invariant_score": "float",      // Primary Z-score
  "z_scores": {
    "mean_z": "float",               // Mean Z-score
    "std_z": "float",                // Standard deviation Z-score
    "max_z": "float",                // Maximum Z-score
    "min_z": "float",                // Minimum Z-score
    "universal_invariance": "float", // Invariance measure
    "composite_score": "float"       // Composite Z-score
  },
  "density_metrics": {
    "basic_density": "float",        // Basic density measure
    "cluster_variance": "float",     // Clustering variance
    "prime_density": "float",        // Prime-based density
    "enhancement_factor": "float"    // Enhancement ratio
  },
  "anomaly_scores": {
    "statistical_anomalies": "float",    // Statistical anomalies
    "curvature_anomalies": "float",      // Curvature-based anomalies
    "frame_anomalies": "float",          // Frame-shift anomalies
    "composite_anomaly_score": "float"   // Overall anomaly score
  },
  "normalized_sequence": "array",    // Normalized values [0, 1]
  "sequence_length": "integer"       // Length validation
}
```

## Examples

### Example 1: Prime Number Analysis

```python
# Analyze first 10 primes
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
result = client.score(primes, data_type="numerical")

print(f"Prime sequence Z-score: {result['z_invariant_score']:.3f}")
print(f"Enhancement factor: {result['density_metrics']['enhancement_factor']:.3f}")
print(f"Anomaly score: {result['anomaly_scores']['composite_anomaly_score']:.3f}")
```

### Example 2: Biological Sequence Analysis

```python
# Analyze DNA sequence
dna = "ATGCGTACGTAGCTACGATCGATCGTAGCTAGC"
bio_result = client.score(dna, data_type="biological")

print(f"DNA Z-score: {bio_result['z_invariant_score']:.3f}")
print(f"Sequence length: {bio_result['metadata']['length']}")
print(f"Normalized sequence: {bio_result['normalized_sequence'][:5]}...")
```

### Example 3: Network Analysis

```python
# Analyze small network
adjacency_matrix = [
    [0, 1, 1, 0],
    [1, 0, 1, 1], 
    [1, 1, 0, 1],
    [0, 1, 1, 0]
]
network_result = client.score(adjacency_matrix, data_type="network")

print(f"Network Z-score: {network_result['z_invariant_score']:.3f}")
print(f"Curvature anomalies: {network_result['anomaly_scores']['curvature_anomalies']:.3f}")
```

### Example 4: Batch Processing

```python
# Process multiple sequences
sequences = [
    [1, 1, 2, 3, 5, 8, 13],           # Fibonacci
    "ATGCATGCATGC",                   # DNA
    [[0, 1], [1, 0]]                  # Simple graph
]

batch_results = client.batch_score(sequences, 
                                  data_types=["numerical", "biological", "network"])

for i, result in enumerate(batch_results['results']):
    print(f"Sequence {i+1}: Z-score = {result['z_invariant_score']:.3f}")
```

## Mathematical Background

### Z-Invariant Theory

The Universal Invariant Scoring Engine is based on the Z Framework's mathematical foundation:

#### Universal Form
```
Z = A(B/c)
```
Where:
- **A**: Frame-dependent measured quantity  
- **B**: Rate or frame shift
- **c**: Universal invariant (speed of light constant)

#### Domain-Specific Applications

**Physical Domain:**
```
Z = T(v/c)
```
- T: Measured time interval
- v: Velocity
- Validated through relativistic effects

**Discrete Domain:**
```  
Z = n(Δₙ/Δₘₐₓ)
```
- n: Frame-dependent integer
- Δₙ: Measured frame shift at n
- Δₘₐₓ: Maximum shift (bounded by e² or φ)

#### Prime Density Enhancement

The framework achieves empirically validated conditional best-bin uplift using:

```
θ'(n, k) = φ · {n/φ}^k where {x} denotes the fractional part of x
```

Where:
- **φ**: Golden ratio ≈ 1.618
- **k***: Optimal curvature parameter ≈ 0.3
- **Enhancement**: 15% (CI [14.6%, 15.4%])

#### Statistical Validation

- **Confidence Interval**: Bootstrap CI [14.6%, 15.4%]
- **Statistical Significance**: p < 10⁻⁶
- **Cross-Domain Correlation**: r ≈ 0.93 (empirical, pending independent validation) with Riemann zeta zeros
- **High-Precision Implementation**: mpmath with dps=50

#### Curvature-Based Anomaly Detection

Frame-normalized curvature:
```
κ(n) = d(n) · ln(n+1)/e²
```
- d(n): Divisor function
- Minimizes variance (σ ≈ 0.118)
- Enables geometric anomaly detection

### Computational Implementation

- **High-Precision Arithmetic**: mpmath (dps=50) for numerical stability
- **Parallel Processing**: Multi-core scaling for large datasets
- **Statistical Protocols**: Bootstrap validation with 1000+ samples
- **Cross-Validation**: Independent verification across N ranges

### References

- [Framework Documentation](framework/README.md) - Complete mathematical foundations
- [Research Papers](research/papers.md) - Peer-reviewed publications
- [Validation Results](validation/README.md) - Empirical validation protocols