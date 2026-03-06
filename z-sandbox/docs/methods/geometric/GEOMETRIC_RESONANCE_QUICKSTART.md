# Geometric Resonance Factorization - Quick Start

## Overview

Geometric resonance is a wave-based approach to integer factorization that uses constructive interference patterns to locate prime factors.

## Key Files

- **Implementation:** `python/geometric_resonance_127bit.py`
- **Protocol:** `docs/methods/geometric/GEOMETRIC_RESONANCE_PROTOCOL.md`
- **Tests:** `tests/test_geometric_resonance_127bit.py`
- **127-bit Challenge:** `docs/validation/reports/127BIT_GEOMETRIC_RESONANCE_CHALLENGE.md`

## Quick Start

### 1. Verify the 127-bit Result

```bash
cd z-sandbox
python3 python/verify_factors_127bit.py
```

Expected output:
```
N = 137524771864208156028430259349934309717
p (claimed) = 10508623501177419659
q (claimed) = 13086849276577416863

p × q = 137524771864208156028430259349934309717
Match: True
...
p is prime: True
q is prime: True
```

### 2. Run Tests

```bash
python3 tests/test_geometric_resonance_127bit.py
```

All tests should pass (✓).

### 3. Factor a Number (Example)

```python
from python.geometric_resonance_127bit import factor_by_geometric_resonance

# Factor a semiprime
N = 137524771864208156028430259349934309717

# Configure (optional, uses defaults if not provided)
config = {
    'num_samples': 801,      # k samples
    'k_lo': 0.25,            # k lower bound
    'k_hi': 0.45,            # k upper bound
    'm_span': 180,           # mode range
    'J': 6                   # Dirichlet order
}

# Run factorization
p, q, metadata = factor_by_geometric_resonance(N, config)

if p is not None:
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"Time: {metadata['total_time']:.2f}s")
    print(f"Candidates: {metadata['candidates_generated']}")
```

## Method Overview

### 1. Comb Formula

Predicts prime locations:
```
p_m = exp((ln N - 2πm/k) / 2)
```

### 2. Dirichlet Kernel

Sharpens resonance peaks:
```
D_J(θ) = Σ_{j=-J}^{J} exp(ijθ)
|D_J(θ)| ≥ 0.92 × (2J+1)  → keep candidate
```

### 3. Golden-Ratio QMC

Low-discrepancy k sampling:
```
u_n = {n / φ}
k_n = k_lo + u_n × (k_hi - k_lo)
```

## Artifacts

For the 127-bit challenge validation:

```
results/
├── geometric_resonance_127bit_config.json    # Parameters
├── geometric_resonance_127bit_method.py      # Implementation
├── geometric_resonance_127bit_candidates.txt # Candidate list
└── geometric_resonance_127bit_metrics.json   # Performance data
```

## Configuration Guide

### Precision

Higher precision for larger numbers:
- 64-100 bits: `mp.dps = 100`
- 100-150 bits: `mp.dps = 200`
- 150-200 bits: `mp.dps = 300`
- 200+ bits: `mp.dps = 500+`

### k-Range

Typical range: `[0.25, 0.45]`

For specific optimizations:
- Balanced semiprimes: `[0.28, 0.42]`
- Near √N factors: `[0.32, 0.38]`
- Wide factor gap: `[0.25, 0.50]`

### Mode Span

Larger N needs wider span:
- 40-64 bits: `m_span = 50`
- 64-100 bits: `m_span = 100`
- 100-127 bits: `m_span = 180`
- 127-150 bits: `m_span = 200`
- 150+ bits: `m_span = 250+`

### Sampling

More samples = higher success probability:
- Quick test: `num_samples = 101`
- Standard: `num_samples = 801`
- High confidence: `num_samples = 2001`
- Exhaustive: `num_samples = 5001+`

### Dirichlet Order

Higher J = sharper discrimination:
- Fast/loose: `J = 4`
- Balanced: `J = 6` (recommended)
- Precise: `J = 8`
- Ultra-precise: `J = 10+`

## Performance

### Expected Runtime (127-bit)

| Samples | m_span | J | Expected Time |
|---------|--------|---|---------------|
| 101     | 50     | 4 | 5-15s         |
| 401     | 100    | 6 | 30-90s        |
| 801     | 180    | 6 | 60-300s       |
| 2001    | 200    | 8 | 300-900s      |

### Memory Usage

- Candidates: < 10,000 typical
- Memory: < 1 MB
- Storage: Config + candidates + metrics < 100 KB

## Troubleshooting

### "No factors found"

- Increase `num_samples` (try 2-3× current)
- Widen `m_span` (try +50)
- Lower Dirichlet threshold (try 0.88 instead of 0.92)
- Check if N is actually a semiprime

### "Too slow"

- Reduce `num_samples` initially
- Reduce `m_span` (try -50)
- Lower `J` (try 4 instead of 6)
- Use parallel processing (split k samples)

### "Too many candidates"

- Increase Dirichlet threshold (try 0.95)
- Increase `J` (try 8 or 10)
- Reduce `m_span` slightly

## Validation Checklist

Before accepting a result:

- [ ] Multiplication: p × q = N
- [ ] Divisibility: N % p = 0
- [ ] Primality: both p and q are prime
- [ ] Bit lengths match expectation
- [ ] Method used pure geometric resonance
- [ ] No ECM/NFS/Pollard in search loop
- [ ] Config and artifacts provided

## Next Steps

1. **Review Protocol:** Read `docs/methods/geometric/GEOMETRIC_RESONANCE_PROTOCOL.md`
2. **Study 127-bit Case:** Read `docs/validation/reports/127BIT_GEOMETRIC_RESONANCE_CHALLENGE.md`
3. **Run Tests:** Execute `tests/test_geometric_resonance_127bit.py`
4. **Try Own Examples:** Modify and run `python/geometric_resonance_127bit.py`

## References

- **Protocol:** `docs/methods/geometric/GEOMETRIC_RESONANCE_PROTOCOL.md`
- **127-bit Validation:** `docs/validation/by-size/127BIT_GEOMETRIC_RESONANCE_VALIDATION.md`
- **Challenge Summary:** `docs/validation/reports/127BIT_GEOMETRIC_RESONANCE_CHALLENGE.md`
- **Z Framework:** `docs/core/` (foundation theory)

## Support

For questions or issues:
1. Check the protocol document
2. Review the 127-bit validation report
3. Run the test suite for examples
4. Open an issue in the repository

---

**Last Updated:** 2025-11-06  
**Version:** 1.0  
**Status:** Validated ✓
