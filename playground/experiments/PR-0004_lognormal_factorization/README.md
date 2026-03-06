# Lognormal Pre-Filter Factorization Pipeline

This experiment implements a factorization pipeline for semiprimes \(N = pq\) using a lognormal prime-gap model as a pre-filter in front of standard algorithms (Fermat-style and Pollard Rho). The goal is to bias search efforts near \(\sqrt{N}\) without compromising mathematical correctness, potentially improving efficiency for semiprimes in empirically fitted ranges.

## Overview

### Core Concept
Prime gaps (differences between consecutive primes) follow a lognormal distribution in certain ranges, as shown by empirical analysis of primes up to \(10^9\). This pipeline uses pre-computed lognormal parameters to generate candidate offsets around \(\sqrt{N}\), guiding factorization attempts before falling back to classical methods.

### Model Bands
The model is divided into 4 bands based on prime sizes, with hardcoded lognormal shape/scale parameters derived from KS-minimal fits:
- **Band 1**: \(10^5 \leq p < 10^6\) (shape=1.309, scale=2.796e-05)
- **Band 2**: \(10^6 \leq p < 10^7\) (shape=1.329, scale=3.166e-06)
- **Band 3**: \(10^7 \leq p < 10^8\) (shape=1.344, scale=3.544e-07)
- **Band 4**: \(10^8 \leq p \leq 10^9\) (shape=1.358, scale=3.920e-08)

For \(p\) outside these ranges, the closest band is used as an approximation.

### Pipeline Stages
1. **Lognormal-Guided Fermat**: Sample offsets from lognormal distribution, test Fermat candidates.
2. **Candidate Pre-Filter**: Generate offset list, test direct factors with primality checks.
3. **Pollard Rho Fallback**: Classical factorization with multiple polynomial starts.

### Key Features
- **Correctness**: Always finds factors via fallback; model only biases search order.
- **Reproducibility**: Deterministic RNG via seeds.
- **Configurable**: Adjustable steps, scales, modes.
- **Research-Oriented**: Designed for benchmarking lognormal vs classical performance.

## Installation

### Prerequisites
- Python 3.8+ (for `math.isqrt`)
- No external dependencies (stdlib only)

### Setup
Clone the repository and navigate to the experiment:
```bash
git clone https://github.com/zfifteen/playground.git
cd playground/experiments/PR-0004_lognormal_factorization
```

## Usage

### Python API
```python
from src.pipeline import factor_with_lognormal_prefilter
from src.model import ModelStore
from src.config import SearchPolicyConfig

# Initialize
model = ModelStore()
cfg = SearchPolicyConfig(max_steps=10000, radius_scale=1.0, direction_mode="ALTERNATE", seed=42)

# Factor
factor = factor_with_lognormal_prefilter(77, model, cfg)  # Returns 7 or 11
if factor:
    print(f"Factor found: {factor}")
else:
    print("No factor found")
```

### CLI
For quick factorization:
```bash
python factor_cli.py <N> [--max-steps INT] [--radius-scale FLOAT] [--direction-mode ALTERNATE|RANDOM] [--seed INT]
```

Examples:
- `python factor_cli.py 77` → `7 11`
- `python factor_cli.py 1000036000099 --max-steps 20000` → `1000033 1000003`

### Benchmarking
- **Functional Smoke Test**: `python run_experiment.py` (tests on small semiprimes)
- **Performance by Band**: `python performance_benchmark.py` (timing for fitted bands)

## Implementation Details

### Files
- `src/model.py`: Band dataclass and ModelStore
- `src/config.py`: SearchPolicyConfig with RNG
- `src/utils.py`: Sampling, clamping, Pollard Rho
- `src/fermat.py`: Lognormal-guided Fermat stage
- `src/prefilter.py`: Candidate offset generation and testing
- `src/pipeline.py`: Main pipeline assembly
- `factor_cli.py`: CLI wrapper
- `performance_benchmark.py`: Band-wise timing benchmark
- `run_experiment.py`: Functional smoke test
- `TEST_RESULTS.md`: Detailed factorization logs

### RNG and Determinism
- Uses `random.Random` instance in `SearchPolicyConfig` for reproducibility.
- Seeds control all randomness; same seed produces identical results.

### Limitations
- Effective for semiprimes with \(p, q\) in fitted bands.
- Large N (>10^12) may require more steps or optimized fallbacks.
- Prime generation for high bands is slow; consider pre-caching.

## Testing

Run the full test suite:
```bash
python -m pytest tests/ -v
```

### Test Coverage
- Model band selection
- Sampling and clamping
- Fermat stage on small semiprimes
- Prefilter candidate generation
- Pipeline end-to-end
- Utilities (perfect squares, Pollard Rho)

All 12 tests pass, ensuring correctness.

## Results

See `TEST_RESULTS.md` for detailed logs, including:
- Small validation sets (77, 91, etc.)
- Mid-band successes (10^12 scale)
- Upper-band edges (near 10^6, 10^7)
- Performance summaries (pipeline vs classical timing)

### Performance Baseline
For Bands 1-2 (1 semiprime each):
- Band 1: Pipeline ~0.14s, Classical ~0.002s, Speedup ~0.01x
- Band 2: Pipeline ~0.15s, Classical ~0.002s, Speedup ~0.01x

Low speedup due to small N overhead; expect improvements for larger fitted N.

## Contributing

This is an experimental implementation. For extensions:
- Add more bands or dynamic model loading.
- Optimize prime generation for higher bands.
- Compare with other pre-filter strategies.

## References
- Lognormal distribution for prime gaps: Empirical fits from prime analysis up to 10^9.
- Pollard Rho: Brent variant with multiple polynomial starts.
- Fermat factorization: Guided by sampled offsets.

Closes issue #23.

## Parameters

Bands are hardcoded from empirical fits (results-10-6.json to 10-9.json):
- Band 1: \(10^5 \leq p < 10^6\)
- Band 2: \(10^6 \leq p < 10^7\)
- Band 3: \(10^7 \leq p < 10^8\)
- Band 4: \(10^8 \leq p \leq 10^9\)

## Testing

Run tests: `pytest tests/`

Run functional smoke test: `python run_experiment.py`

Run performance benchmark on fitted bands: `python performance_benchmark.py`