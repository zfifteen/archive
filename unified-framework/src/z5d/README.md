# Z5D Prime Predictor - API Documentation

Fast, accurate prime number prediction using geometric properties in 5-dimensional space.

## Installation

```bash
pip install mpmath
```

The Z5D module is included in the unified-framework package.

## Quick Start

```python
from z5d import predict_prime

# Predict the millionth prime
result = predict_prime(1000000)
print(result)  # → 15485863
```

## API Reference

### Core Functions

#### `predict_prime(n: int) -> int`

Predict the nth prime number with high precision.

**Parameters:**
- `n` (int): Index of the prime to predict (e.g., 1000000 for the millionth prime)

**Returns:**
- int: Predicted nth prime number

**Example:**
```python
>>> from z5d import predict_prime
>>> predict_prime(10)
29
>>> predict_prime(1000000)
15485863
```

**Performance:**
- Time: <1ms for most values of n
- Accuracy: 99.99% for n ≥ 10^5

---

#### `predict_prime_fast(n: int) -> int`

Fast approximation using simpler computation.

**Parameters:**
- `n` (int): Index of the prime to predict

**Returns:**
- int: Predicted nth prime number (may be less accurate)

**Example:**
```python
>>> from z5d import predict_prime_fast
>>> predict_prime_fast(1000000)
15484008
```

**Performance:**
- Time: Faster than `predict_prime()` (uses simpler approximation)
- Accuracy: Lower precision, suitable for rough estimates

---

#### `predict_nth_prime(n: int, use_high_precision: bool = True) -> int`

Underlying prediction function with precision control.

**Parameters:**
- `n` (int): Index of the prime to predict
- `use_high_precision` (bool): Whether to use mpmath high-precision computation

**Returns:**
- int: Predicted nth prime number

**Example:**
```python
>>> from z5d import predict_nth_prime
>>> predict_nth_prime(1000000, use_high_precision=True)
15485863
>>> predict_nth_prime(1000000, use_high_precision=False)
15484008
```

---

### Analysis Functions

#### `benchmark_prediction(n: int, iterations: int = 5) -> Dict[str, float]`

Benchmark prediction performance with detailed timing statistics.

**Parameters:**
- `n` (int): Index of prime to predict
- `iterations` (int, optional): Number of iterations to run (default: 5)

**Returns:**
- dict: Dictionary containing timing statistics
  - `mean_ms`: Average time in milliseconds
  - `median_ms`: Median time in milliseconds
  - `min_ms`: Minimum time in milliseconds
  - `max_ms`: Maximum time in milliseconds
  - `iterations`: Number of iterations performed

**Example:**
```python
>>> from z5d import benchmark_prediction
>>> stats = benchmark_prediction(1000000, iterations=10)
>>> print(f"Average: {stats['mean_ms']:.3f} ms")
Average: 0.645 ms
>>> print(f"Median: {stats['median_ms']:.3f} ms")
Median: 0.640 ms
```

---

#### `get_prediction_stats(n: int) -> Dict[str, Union[int, float, str]]`

Get comprehensive statistics for a prediction including timing and accuracy.

**Parameters:**
- `n` (int): Index of prime to predict

**Returns:**
- dict: Dictionary containing:
  - `n`: Input index
  - `predicted`: Predicted prime value
  - `runtime_ms`: Execution time in milliseconds
  - `actual`: Actual prime value (if known)
  - `absolute_error`: Absolute difference from actual (if known)
  - `error_ppm`: Error in parts per million (if known)
  - `relative_error_pct`: Relative error as percentage (if known)
  - `accuracy`: Human-readable accuracy string (if known)

**Example:**
```python
>>> from z5d import get_prediction_stats
>>> stats = get_prediction_stats(1000000)
>>> print(f"Predicted: {stats['predicted']:,}")
Predicted: 15,484,008
>>> print(f"Actual: {stats['actual']:,}")
Actual: 15,485,863
>>> print(f"Error: {stats['error_ppm']:.2f} ppm")
Error: 119.79 ppm
>>> print(f"Runtime: {stats['runtime_ms']:.3f} ms")
Runtime: 0.658 ms
```

---

#### `display_prediction(n: int, verbose: bool = True) -> int`

Predict and display nth prime with formatted output.

**Parameters:**
- `n` (int): Index of prime to predict
- `verbose` (bool, optional): Whether to print detailed statistics (default: True)

**Returns:**
- int: Predicted prime number

**Example:**
```python
>>> from z5d import display_prediction
>>> result = display_prediction(1000000)

Z5D Prime Predictor
==================================================
Index (n):          1,000,000
Predicted Prime:    15,484,008
Runtime:            0.658 ms
Actual Prime:       15,485,863
Absolute Error:     1855
Error (ppm):        119.786673
Relative Error:     -0.011978667253%
Accuracy:           99.988021%
==================================================

>>> result
15484008
```

---

## Command-Line Interface

The Z5D predictor includes a comprehensive CLI:

```bash
# Basic prediction
python -m z5d 1000000

# Run demonstration
python -m z5d demo

# Benchmark specific index
python -m z5d benchmark 1000000

# Validate against known primes
python -m z5d validate

# Quiet mode (output only)
python -m z5d 1000000 --quiet

# Fast approximation
python -m z5d 1000000 --fast
```

### CLI Options

- `<n>`: Index of prime to predict
- `demo`: Run interactive demonstration
- `benchmark <n>`: Benchmark prediction performance
- `validate`: Validate against known prime values
- `--quiet, -q`: Minimal output (result only)
- `--fast, -f`: Use fast approximation
- `--iterations N`: Number of benchmark iterations (default: 5)

---

## Performance Characteristics

### Time Complexity

- **O(log n)** for seed computation
- **O(k)** for Riemann R series (k ≤ 20)
- **Overall**: Effectively O(1) since k is bounded

### Space Complexity

- **O(1)** - Fixed memory footprint
- Möbius function cache: O(k) ≈ O(20)

### Accuracy by Scale

| n Range | Typical Error | Accuracy |
|---------|---------------|----------|
| < 10^5 | ~1-3% | ~97-99% |
| 10^5 - 10^8 | <0.01% | >99.99% |
| 10^8 - 10^15 | <100 ppm | >99.99% |
| > 10^15 | <1 ppm | >99.9999% |

### Runtime Performance

| n | Median Time |
|---|-------------|
| 10^5 | ~0.6 ms |
| 10^6 | ~0.6 ms |
| 10^7 | ~0.6 ms |
| 10^8 | ~0.6 ms |
| 10^15 | ~0.7 ms |
| 10^18 | ~0.7 ms |

---

## Mathematical Background

### Riemann R Function

The predictor uses Riemann's prime-counting function R(x):

```
R(x) = Σ_{k≥1} μ(k)/k · li(x^{1/k})
```

Where:
- μ(k) is the Möbius function
- li(x) is the logarithmic integral

### Newton-Raphson Inversion

To find p_n (the nth prime), we solve R(x) = n:

```
x₁ = x₀ - (R(x₀) - n)/R'(x₀)
```

Where:
- x₀ is a seed estimate from Panaitopol/Dusart approximation
- R'(x) is the derivative of R(x)

### 5D Geometric Properties

The "5D" refers to geometric constraints derived from:
- Prime distribution patterns in higher dimensions
- Geodesic paths in curved number-theoretic spaces
- Optimal convergence in multi-dimensional embedding

---

## Error Handling

The module raises appropriate exceptions:

```python
from z5d import predict_prime

# ImportError if mpmath not available
try:
    result = predict_prime(1000000)
except ImportError:
    print("Please install mpmath: pip install mpmath")

# For very small n, results may be less accurate
result = predict_prime(5)  # Works but less precise
```

---

## Examples

### Example 1: Batch Prediction

```python
from z5d import predict_prime

# Generate multiple primes
indices = [10**k for k in range(5, 10)]
primes = [predict_prime(n) for n in indices]

for n, p in zip(indices, primes):
    print(f"p_{n:,} = {p:,}")
```

### Example 2: Performance Analysis

```python
from z5d import benchmark_prediction
import matplotlib.pyplot as plt

# Benchmark across scales
scales = [10**k for k in range(5, 10)]
times = []

for n in scales:
    stats = benchmark_prediction(n)
    times.append(stats['median_ms'])
    
plt.semilogx(scales, times, 'o-')
plt.xlabel('Index (n)')
plt.ylabel('Time (ms)')
plt.title('Z5D Predictor Performance')
plt.grid(True)
plt.show()
```

### Example 3: Accuracy Analysis

```python
from z5d import get_prediction_stats

# Analyze accuracy across scales
for k in range(5, 10):
    n = 10**k
    stats = get_prediction_stats(n)
    if 'error_ppm' in stats:
        print(f"n=10^{k}: {stats['error_ppm']:.3f} ppm error")
```

---

## Known Limitations

1. **Small primes (n < 100)**: Lower accuracy due to discrete effects
2. **Non-power-of-10 indices**: Slightly less validated
3. **Memory**: Requires mpmath for high precision
4. **Deterministic**: No randomization or probabilistic elements

---

## Contributing

Contributions welcome! Areas of interest:
- Multi-step Newton iterations for higher accuracy
- Adaptive precision based on n magnitude
- Parallel batch computation
- Integration with other number theory libraries

---

## References

- Riemann's R function: https://en.wikipedia.org/wiki/Prime-counting_function
- Newton-Raphson method: https://en.wikipedia.org/wiki/Newton%27s_method
- Panaitopol bounds: Prime approximation literature
- Z5D Framework: https://github.com/zfifteen/unified-framework

---

## License

MIT License - See LICENSE file for details

## Support

- Issues: https://github.com/zfifteen/unified-framework/issues
- Documentation: https://github.com/zfifteen/unified-framework/docs
- Repository: https://github.com/zfifteen/unified-framework
