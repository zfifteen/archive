# I Ching-Z RSA-4096 Framework: As-Is Baseline Report

## Overview
This report establishes the baseline performance of the current implementation in `rsa4096_test_harness.py`. The framework integrates I Ching hexagrams with geometric scaling (Z = A(B / φ)) for theoretical RSA factorization. Tests focus on geometric scaling mutations and Z5D θ' shortcuts on small semiprimes.

## Methodology
- **Runs**: 10 independent executions of the harness.
- **Metrics**:
  - Geometric Scaling Success Rate: Percentage of hexagram mutations (depth 1-10) achieving yang_balance ≈ 0.618.
  - Z5D Success Rate: Percentage of small semiprimes (77, 5959, 12347) where θ' embedding finds a factor.
- **Reproducibility**: All runs produced identical results, indicating deterministic behavior despite apparent randomness (likely due to fixed seeds or hardcoded inputs).
- **Environment**: OSX, Python 3.x, mpmath dps=50.

## Results
### Average Performance (10 runs)
- **Geometric Scaling Success Rate**: 30.0% (3 out of 10 depths per run).
- **Z5D θ' Shortcut Success Rate**: 66.7% (2 out of 3 semiprimes per run: succeeds for 77 and 5959, fails for prime 12347).

### Raw Data
All runs yielded:
- Scaling: 30.0%
- Z5D: 66.7%

### Detailed Output Sample
```
🔄 Testing Geometric Scaling with Hexagram Mutations:
Overall success rate: 30.0%

🔍 Testing Z5D θ' Shortcut on small semiprimes:
Z5D success rate: 66.7%

🔐 Theoretical RSA-4096 Framework:
  - N ≈ 2^4096, sqrt(N) ≈ 2^2048
  - Hexagram state space: 64 states for branching
  - Weyl trials: floor(φ * prev + hex_int) % sqrt(N)
  - Pruning: Yang-balance heuristic (target ~0.618)
  - Convergence: gcd(N, trial) in ~1000 steps (φ^11)
  - Security: Relies on φ-chaos for unpredictability
```

## Analysis
- **Strengths**: Z5D shortcut effective on semiprimes (geometric embedding via θ'(n,k) = φ · ((n mod φ)/φ)^k with k=0.3).
- **Weaknesses**: Geometric scaling pruning heuristic (yang-balance) only achieves 30% success; demo pruning shows 0% efficiency (no branches pruned).
- **Hypothesis Status**: UNVERIFIED. Claims of 38% speedup and φ^11 steps lack empirical support beyond small-scale tests.
- **Gaps**: No large-N testing; pruning needs refinement (e.g., statistical thresholds).

## Next Steps
- Refine yang-balance heuristic with Monte Carlo on known semiprimes.
- Bootstrap simulations for convergence estimates.
- Cross-validate with datasets (e.g., prime gaps, zeta_zeros.csv).