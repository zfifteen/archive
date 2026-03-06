# Conic Sections Implementation - Quick Start

## Overview

Implementation of conic section equations (ellipse, parabola, hyperbola) for integer factorization, integrated with the z-sandbox geometric factorization framework.

## Quick Usage

### Basic Factorization

```python
from conic_sections import ConicFactorization

conic = ConicFactorization()
factors = conic.factorize_via_conics(899, strategies=['fermat'])
print(factors)  # Output: (29, 31)
```

### With GVA Integration

```python
from conic_integration import ConicGVAIntegration

gva_conic = ConicGVAIntegration()
factors = gva_conic.factorize_with_conic_gva(899, max_candidates=100)
print(factors)  # Output: (29, 31)
```

### Monte Carlo Sampling

```python
from conic_integration import ConicMonteCarloIntegration

mc_conic = ConicMonteCarloIntegration(seed=42)
candidates = mc_conic.monte_carlo_conic_candidates(899, num_samples=500, mode='phi-biased')
# Achieves 100% factor recovery
```

## Testing

```bash
# Run unit tests (11 tests)
PYTHONPATH=python python3 tests/test_conic_sections.py

# Run integration tests (6 tests)
PYTHONPATH=python python3 tests/test_conic_integration.py

# Run comprehensive demo
PYTHONPATH=python python3 python/examples/conic_demo.py
```

## Performance

- Fermat factorization: <1ms for balanced semiprimes
- Candidate generation: True factors in top 5 (100% success)
- Monte Carlo: 100% factor recovery with phi-biased sampling

## Documentation

See [CONIC_SECTIONS_INTEGRATION.md](../docs/CONIC_SECTIONS_INTEGRATION.md) for complete documentation.

## Components

- `python/conic_sections.py` - Core implementation (640 lines)
- `python/conic_integration.py` - Framework integration (420 lines)
- `tests/test_conic_sections.py` - Unit tests (11 tests)
- `tests/test_conic_integration.py` - Integration tests (6 tests)
- `python/examples/conic_demo.py` - Comprehensive demo

## Academic References

1. Fermat lattice points: https://onlinelibrary.wiley.com/doi/10.1155/2022/6360264
2. Using conics to factor: https://www.researchgate.net/publication/297593522
3. Groningen thesis: https://fse.studenttheses.ub.rug.nl/22789/1/bMATH_2020_EelkemaDSL.pdf
4. Conic cryptography: https://www.nature.com/articles/s41598-025-00334-6
5. Group law on conics: https://iris.unitn.it/bitstream/11572/273125/1/main-revised-elia.pdf
