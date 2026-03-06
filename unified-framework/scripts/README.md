# Utility Scripts

This directory contains utility and validation scripts for the Z-Framework system maintenance, testing, and analysis.

## Contents

### Validation Scripts
- **`validate_z_embeddings_bootstrap.py`** - Bootstrap validation for Z-embeddings with statistical confidence intervals
- **`test_linear_scaling.py`** - Linear scaling behavior testing and validation
- **`validate_linear_scaling.py`** - Comprehensive linear scaling validation with performance metrics
- **`run_variance_analysis.py`** - Variance analysis execution script with statistical outputs

### Service Scripts
- **`start_api_server.py`** - API server startup utility for web service deployment

## Script Framework

Per KBLLM.txt computational methodologies and validation protocols:

### Bootstrap Validation
- **Statistical Robustness**: 1000-iteration bootstrap confidence interval establishment
- **Z-Embeddings**: 5D helical embedding validation with geometric constraints
- **Confidence Intervals**: Statistical significance testing with p<10^-6 requirements

### Scaling Validation
- **Linear Scaling**: Validation from N=10^3 to N=10^9 with performance tracking
- **Performance Metrics**: Computation time and memory usage analysis
- **Algorithmic Efficiency**: 3.05x improvement verification over Eratosthenes sieve

### Variance Analysis
- **Statistical Analysis**: var(O)~log_log_N relationship validation
- **Mathematical Properties**: Variance minimization through curvature-adaptive geodesics
- **169000x Reduction**: Comprehensive validation of variance improvement claims

### API Services
- **Web Service**: RESTful API for Z-Framework computational services
- **Performance Monitoring**: Real-time metrics and system health monitoring
- **Scalability**: Production-ready deployment utilities

## Usage

### Bootstrap Validation
```bash
# Run bootstrap validation for Z-embeddings
python docs/scripts/validate_z_embeddings_bootstrap.py

# Output: Bootstrap confidence intervals and statistical validation
```

### Scaling Tests
```bash
# Test linear scaling behavior
python docs/scripts/test_linear_scaling.py

# Comprehensive scaling validation
python docs/scripts/validate_linear_scaling.py
```

### Variance Analysis
```bash
# Execute variance analysis
python docs/scripts/run_variance_analysis.py

# Generates variance analysis reports in docs/generated/
```

### API Server
```bash
# Start API server for web services
python docs/scripts/start_api_server.py

# Default: http://localhost:8000/
```

## Technical Implementation

### High-Precision Requirements
- **mpmath dps=50+**: Numerical stability for large-scale computations
- **Error Detection**: Comprehensive numerical instability detection systems
- **Precision Validation**: Delta_n < 10^-16 accuracy requirements

### Statistical Protocols
- **Bootstrap Methodology**: Robust statistical inference with resampling
- **Confidence Intervals**: Uncertainty quantification and error estimation
- **Hypothesis Testing**: Multiple comparison correction and significance testing

### Performance Optimization
- **Parallel Processing**: Multi-core scaling for enhanced computational reliability
- **Memory Management**: Resource optimization for large-N computations
- **Scalability Assessment**: Performance degradation analysis and optimization

## Integration with Framework

These utility scripts support the core Z-Framework validation requirements:

### Computational Validation
- **Numerical Accuracy**: High-precision arithmetic validation
- **Statistical Significance**: p<10^-6 confidence levels for all tests
- **Cross-Platform**: Reproducibility across different systems

### Performance Validation
- **Scaling Behavior**: Linear scaling verification across multiple orders of magnitude
- **Efficiency Metrics**: Computational improvement validation
- **Resource Optimization**: Memory and CPU usage optimization verification

### Service Integration
- **API Deployment**: Production-ready web service capabilities
- **Real-time Processing**: Live computational services and demonstrations
- **Monitoring**: System health and performance tracking

## Requirements

### System Dependencies
- Python 3.8+
- Core scientific libraries: numpy, scipy, matplotlib, mpmath, sympy
- Statistical libraries: scikit-learn, statsmodels
- Web framework dependencies for API server

### Computational Resources
- Minimum 4GB RAM for standard validation
- Minimum 32GB RAM for large-scale testing (N=10^9)
- Multi-core CPU recommended for parallel processing

### Framework Integration
- PYTHONPATH configured for src/ module access
- Core Z-Framework modules properly installed
- Access to validation datasets and test configurations

These utility scripts provide essential infrastructure for maintaining and validating the Z-Framework's mathematical discoveries and computational reliability as documented in the KBLLM knowledge base.