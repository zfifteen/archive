# Blind Geometric Factorization Experiment

This experiment implements a **true blind search** for semiprime factorization using
the PR-123/969 scaling infrastructure. Unlike the validation mode in PR-971 which
uses known factors to verify the infrastructure, this implementation attempts to
**discover** factors without any prior knowledge.

## Background

### What PR-971 Achieves (Validation Mode)
- Validates the geometric factorization infrastructure and scaling formulas
- Confirms parameter computations (T(N), k(N), samples, precision) work correctly
- Uses known Gate-127 factors (p, q) to verify the pipeline
- **Does NOT** demonstrate blind discovery of factors

### What This Experiment Addresses (Blind Mode)
- Implements true blind search around √N
- Uses PR-123/969 scaling parameters for resonance-guided search
- Demonstrates factorization capability for smaller semiprimes
- Quantifies the computational challenge for 127-bit blind factorization

## Technical Implementation

### Scaling Formulas (from PR-123)

```
Threshold: T(N) = 0.92 - 0.10 × log₂(bitLen/30)
k-shift:   k(N) = 0.35 + 0.0302 × ln(bitLen/30)
Samples:   samples(N) = round(30000 × (bitLen/60)), min 5000
Precision: precision(N) = 4 × bitLen + 200
```

### Resonance Scoring

Candidates are scored using geodesic and curvature contributions:
- **θ'(x, k)** = φ × ((x mod φ) / φ)^k  (geodesic angle)
- **κ(x)** = log(x + 1) / e²  (curvature contribution)
- Score = (θ' / φ) × (1 + κ × curvature) × distance_weight

### Search Strategy

1. Start at √N (geometric center)
2. Search outward in both directions
3. Check odd candidates only (even factors detected separately)
4. Use trial division as ground truth verification
5. Resonance scores guide candidate prioritization

## Usage

```python
from experiments.blind_geometric_factorization import BlindGeometricFactorizer

# Factor a small semiprime blindly
N = 55049  # 131 × 419
factorizer = BlindGeometricFactorizer(N, verbose=True)
result = factorizer.factor_blind(max_iterations=100000)

if result.success:
    print(f"Found factors: {result.p} × {result.q}")
```

## Results

### Small Semiprimes (≤48 bits)
- Successfully factored via blind search
- Reasonable execution times (<1 minute)
- Demonstrates infrastructure works correctly

### Gate-127 (127-bit)
- **Not feasible** with current blind search
- Requires ~10^15+ operations
- Would take ~3+ years at 10M ops/second
- Further algorithmic breakthroughs needed

## Complexity Analysis

| Bits | √N (approx) | Worst Case Time |
|------|-------------|-----------------|
| 32   | 46,341      | <1 second       |
| 48   | 16.7M       | ~2 seconds      |
| 64   | 4.3B        | ~7 minutes      |
| 127  | 1.2×10^19   | ~38,000 years   |

## Key Insight

The current geometric factorization approach:
1. ✅ Provides correct scaling infrastructure
2. ✅ Works for small-scale blind factorization
3. ❌ Does not yet provide polynomial-time factorization
4. ❌ Requires breakthrough for 127-bit blind discovery

## Next Steps for Advancement

1. **Resonance Enhancement**: Improve scoring to better identify factor regions
2. **Search Pruning**: Use geometric patterns to skip unlikely regions
3. **Parallel Search**: Distribute search across multiple workers
4. **Hybrid Approaches**: Combine with other factorization heuristics

## Files

- `scaling_params.py` - PR-123/969 parameter computation
- `resonance_scoring.py` - Geodesic resonance calculations
- `blind_factorizer.py` - Main blind search implementation
- `demo_blind_factorization.py` - Demonstration script

## References

- [PR-123](https://github.com/zfifteen/geofac/pull/123): Curvature drift & scaling laws
- [PR-969](https://github.com/zfifteen/unified-framework/pull/969): Parameter pipeline
- [PR-971](https://github.com/zfifteen/unified-framework/pull/971): Validation mode implementation
