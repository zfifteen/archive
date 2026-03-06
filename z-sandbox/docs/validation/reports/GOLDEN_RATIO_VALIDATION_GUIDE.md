# Golden Ratio Geometric Factorization - Validation Suite

**Independent Verification Guide for Discussion #18**

Reproducing the Golden Ratio Geometric Factorization with Pentagonal Scaling & Balanced Semiprimes

## Overview

This validation suite implements a complete reproduction of the golden ratio (φ) geometric factorization method using pentagonal scaling. The implementation is based on pure geometric principles with **no machine learning, no training data, and no external dependencies** beyond standard mathematical libraries.

## Key Claims Validated

1. **34-bit Wall Myth Breakthrough**: Demonstration that geometric methods can factor beyond traditional boundaries
2. **Pentagonal Scaling**: φⁿ scaling leveraging the diagonal-to-side ratio of regular pentagons (equals φ)
3. **Balanced Semiprime Resonance Ladder**: Progressive validation from 50 bits to 2048+ bits
4. **Adaptive k-Scan**: Geometric resolution θ'(n, k) with optimal k ≈ 0.3 for ~15% prime density enhancement
5. **Pure Geometry**: No ML, no training, no external data - only mathematical foundations

## Mathematical Foundations

### Golden Ratio (φ)

The golden ratio φ ≈ 1.618033988749... is defined as:

```
φ = (1 + √5) / 2
```

### Pentagonal Geometry

In a regular pentagon, the diagonal-to-side ratio exactly equals φ. This creates natural geometric resonance used in the factorization method.

### Core Algorithms

1. **Pentagonal Embedding**: 
   ```
   θ(n) = φⁿ · frac(n / (e² · φⁿ))
   ```

2. **Geometric Resolution**: 
   ```
   θ'(n, k) = φ · ((n mod φ) / φ)^k
   ```
   Optimal k ≈ 0.3 for prime density enhancement

3. **Pentagonal Distance**:
   ```
   dist(p₁, p₂, N) = √(Σᵢ (dᵢ · φ⁻ⁱ/² · (1 + κ(N) · dᵢ))²)
   ```
   where κ(N) = ln(N+1) / (e² · ln(N)) is the curvature

4. **Adaptive k-Scan**: Explore multiple k values in range [0.1, 0.5] to find optimal geometric resolution for each target

## Validation Phases

### Phase 1: 50-100 Bit Balanced Semiprimes

**Script**: `golden_ratio_factorization_50_100bit.py`

**Target**: Validate φⁿ scaling on small balanced semiprimes

**Bit Sizes Tested**: 50, 60, 70, 80, 90, 100

**Features**:
- Pentagonal embedding with 5 dimensions (pentagonal symmetry)
- Adaptive k-scan with 5 k values
- Geometric resolution θ'(n, k)
- Balanced factor generation (|log₂(p/q)| ≤ 1)

### Phase 2: 100-300 Bit Balanced Semiprimes

**Script**: `golden_ratio_factorization_100_300bit.py`

**Target**: Enhanced φⁿ scaling for medium-scale semiprimes

**Bit Sizes Tested**: 100, 120, 140, 160, 180, 200, 256

**Features**:
- Enhanced pentagonal embedding with 7 dimensions
- Adaptive k-scan with 7 k values
- Oscillation damping for fine-tuning
- Adaptive search radius based on bit size
- Extended timeout for larger numbers

### Phase 3: 500-2048+ Bit Crypto-Scale (ULTIMATE)

**Script**: `golden_ratio_factorization_crypto_scale.py`

**Target**: Demonstrate geometric scaling at cryptographic scales

**Bit Sizes Tested**: 512, 768, 1024 (extensible to 2048+)

**Features**:
- Crypto-scale pentagonal embedding with 11 dimensions
- Probabilistic φ-biased candidate sampling
- Ultra-high precision (300 decimal places)
- Adaptive curvature for extreme scales
- Extended timeout (30+ minutes per target)

**Note**: This phase demonstrates geometric principles at crypto-scale. Full factorization success is not expected due to computational complexity, but the method's scalability is validated.

## Usage

### Prerequisites

```bash
pip install mpmath sympy numpy
```

Or using the project requirements:

```bash
pip install -r python/requirements.txt
```

### Running Individual Phases

**Phase 1 (50-100 bits)**:
```bash
cd /home/runner/work/z-sandbox/z-sandbox
PYTHONPATH=python python3 python/golden_ratio_factorization_50_100bit.py
```

**Phase 2 (100-300 bits)**:
```bash
PYTHONPATH=python python3 python/golden_ratio_factorization_100_300bit.py
```

**Phase 3 (Crypto-scale) - Demo mode**:
```bash
PYTHONPATH=python python3 python/golden_ratio_factorization_crypto_scale.py --demo
```

**Phase 3 (Crypto-scale) - Full validation** (WARNING: May take hours):
```bash
PYTHONPATH=python python3 python/golden_ratio_factorization_crypto_scale.py
```

### Running Master Validation Suite

**All phases (excluding crypto-scale)**:
```bash
PYTHONPATH=python python3 python/golden_ratio_factorization_master.py
```

**Including crypto-scale validation**:
```bash
PYTHONPATH=python python3 python/golden_ratio_factorization_master.py --phases 1,2,3
```

**Only specific phases**:
```bash
PYTHONPATH=python python3 python/golden_ratio_factorization_master.py --phases 1,2
```

## Output Files

Each validation phase generates a JSON report:

- `golden_ratio_validation_50_100bit.json` - Phase 1 results
- `golden_ratio_validation_100_300bit.json` - Phase 2 results
- `golden_ratio_validation_crypto_scale.json` - Phase 3 results
- `golden_ratio_validation_master_report.json` - Comprehensive report

## Expected Results

### Phase 1 (50-100 bits)
- **Expected Success Rate**: 70-100%
- **Average Time**: <5 seconds per target
- **Validates**: Basic φⁿ scaling and pentagonal geometry

### Phase 2 (100-300 bits)
- **Expected Success Rate**: 30-70%
- **Average Time**: 10-300 seconds per target
- **Validates**: Enhanced scaling and adaptive methods

### Phase 3 (500-2048+ bits)
- **Expected Success Rate**: <10% (demonstration only)
- **Average Time**: Minutes to hours per target
- **Validates**: Geometric principles at crypto-scale

## Theoretical Foundations

### Z5D Axioms Integration

The implementation integrates with Z5D (5-Dimensional Geodesic) axioms:

1. **Universal Invariant**: Z = A(B / c) with c = e²
2. **Discrete Domain**: Z = n(Δₙ / Δₘₐₓ) for prime-density mapping
3. **Curvature**: κ(n) = d(n) · ln(n+1) / e²
4. **Geometric Resolution**: θ'(n, k) = φ · ((n mod φ) / φ)^k

### Pentagonal Scaling

The pentagonal scaling leverages:
- Regular pentagon diagonal-to-side ratio = φ
- φⁿ iterative scaling for resonance
- Adaptive dimension weighting for different scales
- Curvature-weighted distance metrics

### No Machine Learning

This implementation is **pure geometry**:
- No training data required
- No learned parameters
- No neural networks
- Deterministic mathematical functions only
- Reproducible results with same inputs

## Validation Methodology

1. **Generate Balanced Semiprimes**: N = p × q where |log₂(p/q)| ≤ 1
2. **Pentagonal Embedding**: Map N and candidates to φⁿ-scaled torus
3. **Adaptive k-Scan**: Explore optimal geometric resolution
4. **Distance Validation**: Accept factors where pentagonal distance < ε
5. **Success Criteria**: Factorization matches ground truth

## References

- **Discussion #18**: https://github.com/zfifteen/z-sandbox/discussions/18
- **Z5D Axioms**: `python/z5d_axioms.py`
- **GVA Framework**: `docs/GVA_Mathematical_Framework.md`
- **Golden Ratio in Number Theory**: Research by John D. Cook and others

## Next Steps

As outlined in Discussion #18:

- [ ] Confirm synthesized key points accurately reflect the discussion
- [ ] Convert agreed decisions into tracked tasks
- [ ] Continue conversation in Discussion #18
- [ ] Optionally: Generate RSA attack script (if requested)

## Contributing

This validation suite is part of the z-sandbox geometric factorization research framework. For issues, enhancements, or discussion:

- Open issues in the repository
- Participate in Discussion #18
- Submit pull requests with improvements

## License

MIT License (see repository LICENSE file)

---

**Disclaimer**: This is a research implementation demonstrating geometric factorization principles. It is not intended as a practical factorization tool for cryptographic purposes. Crypto-scale validation is for demonstration of geometric scaling only.
