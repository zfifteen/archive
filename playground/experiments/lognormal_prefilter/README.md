# Lognormal Pre-Filter Factorization Pipeline

A factorization pipeline for semiprimes **N = pq** that uses a **lognormal prime-gap model** as a pre-filter / search policy in front of standard factorization algorithms.

## Overview

This implementation builds on empirical prime gap data up to 10^9 and uses fitted lognormal distributions to bias the search near sqrt(N) without changing the mathematical correctness of the backend factorization algorithms.

### Key Features

- **Model-driven search**: Uses lognormal prime-gap distributions fitted from empirical data
- **Multiple strategies**: Combines Fermat-style search, direct division, and Pollard's rho
- **Configurable**: Supports different search policies and parameters
- **Correct by construction**: The model only biases search order, never compromises correctness

## Structure

```
lognormal_prefilter/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── model.py             # Band and ModelStore (lognormal parameters)
│   ├── config.py            # SearchPolicyConfig
│   ├── sampling.py          # Lognormal sampling utilities
│   ├── fermat.py            # Lognormal-guided Fermat stage
│   ├── prefilter.py         # Candidate list pre-filter
│   └── pipeline.py          # Top-level factorization pipeline
├── tests/
│   ├── __init__.py
│   ├── test_model.py        # Model layer tests
│   ├── test_sampling.py     # Sampling utilities tests
│   ├── test_fermat.py       # Fermat stage tests
│   ├── test_prefilter.py    # Prefilter tests
│   ├── test_pipeline.py     # Pipeline integration tests
│   └── run_all_tests.py     # Test runner
└── README.md                # This file
```

## Model Parameters

The model is initialized with 4 bands covering different prime ranges, each with lognormal parameters (shape, scale) extracted from empirical fits:

| Band | Prime Range | Shape | Scale | KS Statistic |
|------|-------------|-------|-------|--------------|
| 1 | 10^5 to 10^6 | 1.2867 | 2.415e-4 | 0.0573 |
| 2 | 10^6 to 10^7 | 1.3091 | 2.796e-5 | 0.0516 |
| 3 | 10^7 to 10^8 | 1.3291 | 3.166e-6 | 0.0466 |
| 4 | 10^8 to 10^9 | 1.3579 | 3.920e-8 | 0.0421 |

These parameters are derived from:
- `experiments/PR-0003_prime_log_gap_optimized/results/10^6/results-10-6.json`
- `experiments/PR-0003_prime_log_gap_optimized/results/10^7/results-10-7.json`
- `experiments/PR-0003_prime_log_gap_optimized/results/10^8/results-10-8.json`
- `experiments/PR-0003_prime_log_gap_optimized/results/10^9/results-10-9.json`

## Usage

### Basic Usage

```python
from src.model import create_default_model_store
from src.config import SearchPolicyConfig
from src.pipeline import factor_with_lognormal_prefilter

# Create model and config
model_store = create_default_model_store()
config = SearchPolicyConfig(max_steps=10000, random_seed=42)

# Factor a semiprime
N = 10007 * 10009  # Example semiprime
factor = factor_with_lognormal_prefilter(N, model_store, config)

if factor:
    other_factor = N // factor
    print(f"{N} = {factor} × {other_factor}")
else:
    print(f"Could not factor {N}")
```

### Configuration Options

```python
from src.config import SearchPolicyConfig

# Default configuration
config = SearchPolicyConfig()

# Custom configuration
config = SearchPolicyConfig(
    max_steps=5000,           # Maximum search iterations
    radius_scale=1.0,         # Scale factor for gap-to-offset conversion
    direction_mode="ALTERNATE",  # "ALTERNATE" or "RANDOM"
    random_seed=42            # For reproducibility
)
```

### Using Individual Components

```python
from src.model import create_default_model_store
from src.config import SearchPolicyConfig
from src.fermat import lognormal_fermat_stage
from src.prefilter import factor_with_candidate_prefilter

model_store = create_default_model_store()
config = SearchPolicyConfig(random_seed=42)

N = 10007 * 10009

# Try just the Fermat stage
factor = lognormal_fermat_stage(N, model_store, config)

# Or try just the candidate prefilter
factor = factor_with_candidate_prefilter(N, model_store, config)
```

## Algorithm Description

### 1. Lognormal-Guided Fermat Stage

This stage performs a Fermat-style search where candidate x values near floor(sqrt(N)) are chosen based on lognormal gap sampling:

1. Compute p0 = floor(sqrt(N))
2. Get the appropriate lognormal band for p0
3. For each iteration:
   - Sample gap g from lognormal(shape, scale)
   - Clamp g to valid range
   - Update cumulative offset
   - Compute x_candidate = p0 + direction × round(cumulative_offset)
   - Test if x_candidate^2 - N is a perfect square
   - If yes, extract factors a = x - y and b = x + y

### 2. Candidate Pre-Filter

This stage generates a list of candidate offsets based on the lognormal model and tests them directly:

1. Generate list of offsets using the same lognormal sampling
2. For each offset, compute q_candidate = p0 + offset
3. Test if N % q_candidate == 0
4. If no factor found, fall back to Pollard's rho

### 3. Full Pipeline

The full pipeline tries strategies in order:

1. Lognormal-guided Fermat stage
2. Lognormal candidate prefilter + direct division
3. Classical Pollard's rho fallback

This ensures correctness even if the lognormal model is unhelpful.

## Testing

Run all tests:

```bash
cd tests
python3 run_all_tests.py
```

Or run individual test suites:

```bash
python3 test_model.py
python3 test_sampling.py
python3 test_fermat.py
python3 test_prefilter.py
python3 test_pipeline.py
```

### Test Coverage

- **Model selection**: Verifies band lookup for different p0 values
- **Lognormal sampling**: Ensures samples are always positive and correctly distributed
- **Fermat stage**: Tests factorization on small and medium semiprimes
- **Candidate prefilter**: Verifies offset generation and direct division
- **Pipeline integration**: Tests end-to-end correctness on various inputs

## Performance Characteristics

- **Best case**: Factors close to sqrt(N) are found quickly by the Fermat stage
- **Average case**: The lognormal model biases search towards likely gap sizes
- **Worst case**: Falls back to Pollard's rho for reliable (if slower) factorization

The lognormal pre-filter provides the most benefit when:
- N is a semiprime with factors in the supported range (10^5 to 10^9)
- The factors are relatively close to each other (near sqrt(N))

## Future Extensions

Potential improvements:

1. **Dynamic band parameters**: Update bands based on online learning
2. **Adaptive radius_scale**: Adjust based on search progress
3. **Parallel candidate testing**: Test multiple candidates simultaneously
4. **Extended range**: Add bands for larger primes (10^10, 10^11, etc.)
5. **Hybrid approaches**: Combine with other factorization methods (ECM, QS)

## References

Based on empirical prime gap analysis from:
- `experiments/PR-0003_prime_log_gap_optimized/`

## License

Part of the zfifteen/playground repository.
