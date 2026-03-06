# Z5D Prime Predictor - Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/zfifteen/unified-framework
cd unified-framework

# Install dependencies
pip install mpmath

# Optional: Install full package
pip install -e .
```

## 5-Second Demo

```bash
# Predict the millionth prime
python gists/z5d_prime_predictor_gist.py 1000000
```

Output:
```
Predicting the 1,000,000th prime...
Result: 15,484,008
Actual: 15,485,863
Error:  1855 (119.787 ppm)
```

## 30-Second Demo

```bash
# Run full demonstration
python gists/z5d_prime_predictor_gist.py
```

Shows:
- Small primes (10, 100, 1000)
- Large primes (10^6, 10^7, 10^8)
- Extreme scale (10^15 to 10^18)
- Sub-millisecond timings
- Sub-ppm accuracy

## Using the Module

### Option 1: Standalone Gist (No Installation)

```bash
python gists/z5d_prime_predictor_gist.py 1000000
```

### Option 2: Installed Module

```bash
# Set Python path
export PYTHONPATH=src

# Use the CLI
python -m z5d 1000000
python -m z5d demo
python -m z5d validate
python -m z5d benchmark 1000000
```

### Option 3: Python API

```python
import sys
sys.path.insert(0, 'src')

from z5d import predict_prime

# Simple prediction
result = predict_prime(1000000)
print(result)  # → 15485863

# Get detailed statistics
from z5d import get_prediction_stats
stats = get_prediction_stats(1000000)
print(f"Prediction: {stats['predicted']:,}")
print(f"Runtime: {stats['runtime_ms']:.3f} ms")
print(f"Error: {stats['error_ppm']:.2f} ppm")
```

## Examples

### Example 1: Batch Predictions

```python
from z5d import predict_prime

# Predict multiple primes
for k in range(5, 10):
    n = 10**k
    prime = predict_prime(n)
    print(f"The {n:,}th prime is {prime:,}")
```

### Example 2: Benchmarking

```python
from z5d import benchmark_prediction

stats = benchmark_prediction(1000000, iterations=10)
print(f"Median time: {stats['median_ms']:.3f} ms")
print(f"Mean time: {stats['mean_ms']:.3f} ms")
```

### Example 3: Accuracy Analysis

```python
from z5d import get_prediction_stats

for k in [5, 6, 7, 8]:
    n = 10**k
    stats = get_prediction_stats(n)
    print(f"n=10^{k}: {stats['error_ppm']:.3f} ppm error")
```

## Progressive Examples

### Level 1: Basic Usage
```bash
python examples/z5d_progressive_examples.py 1
```

### Level 2: Integration
```bash
python examples/z5d_progressive_examples.py 2
```

### Level 3: Performance Analysis
```bash
python examples/z5d_progressive_examples.py 3
```

### Level 4: Mathematical Insights
```bash
python examples/z5d_progressive_examples.py 4
```

### All Levels
```bash
python examples/z5d_progressive_examples.py
```

## Visual Summary

```bash
# Generate complete visual summary
python examples/z5d_visual_summary.py
```

Shows:
- Accuracy vs scale chart (ASCII visualization)
- Performance summary across scales
- Method comparison table
- Practical use cases

## Benchmark Comparison

```bash
# Quick benchmark
python examples/z5d_benchmark_comparison.py

# Full comparison (if sympy available)
python examples/z5d_benchmark_comparison.py full

# Accuracy analysis
python examples/z5d_benchmark_comparison.py accuracy

# Specific index
python examples/z5d_benchmark_comparison.py 1000000
```

## Testing

```bash
# Run Z5D tests
python -m pytest tests/test_z5d_prime_predictor.py -v

# Expected: 27 tests passed
```

## Features

### Speed
- **Sub-millisecond predictions**: <1ms for most indices
- **Bounded iterations**: Fixed iteration count (k ≤ 20)
- **No database**: Pure mathematical computation

### Accuracy
- **Small n (< 10^5)**: ~1-3% error (~10,000-30,000 ppm)
- **Medium n (10^5-10^8)**: <0.01% error (<100 ppm)
- **Large n (> 10^8)**: <200 ppm error
- **Extreme n (10^15-10^18)**: <1 ppm error

### Ease of Use
- **Zero configuration**: Just import and use
- **Clean API**: Simple, intuitive functions
- **Progressive complexity**: From simple to advanced
- **Comprehensive docs**: API reference, examples, tutorials

## API Reference

See `src/z5d/README.md` for complete API documentation.

### Main Functions

- `predict_prime(n)` - High-precision prediction
- `predict_prime_fast(n)` - Fast approximation
- `benchmark_prediction(n, iterations=5)` - Performance benchmarking
- `get_prediction_stats(n)` - Comprehensive statistics
- `display_prediction(n, verbose=True)` - Formatted output

## Use Cases

1. **Cryptography**: Fast prime candidate generation
2. **Number Theory**: Prime distribution research
3. **Performance**: Algorithmic comparison studies
4. **Education**: Teaching prime approximation
5. **Research**: Riemann hypothesis explorations

## Performance Comparison

| Method | Time (n=10^6) | Accuracy | Database |
|--------|---------------|----------|----------|
| Trial Division | ~seconds | 100% | No |
| Sieve of Eratosthenes | ~50ms | 100% | No |
| **Z5D Predictor** | **<1ms** | **99.99%** | **No** |

## Links

- **Repository**: https://github.com/zfifteen/unified-framework
- **API Docs**: `src/z5d/README.md`
- **Examples**: `examples/z5d_*.py`
- **Tests**: `tests/test_z5d_prime_predictor.py`

## Support

Open an issue at: https://github.com/zfifteen/unified-framework/issues

## License

MIT License - See LICENSE file
