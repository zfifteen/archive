# I Ching-Z Mashup Against RSA-4096

## Experiment Overview

This experiment tests the hypothesis that embedding I Ching hexagram state mutations into the Z5D recursive factorization framework can enhance RSA-4096 semiprime factorization efficiency through yang-balance optimization and φ-scaled depth control.

## Hypothesis

**Core Claim**: Recursive reduction mirrors I Ching turnover cycles (~1000 steps ≈ φ^11), with hexagram mutations branching like line changes, and yang-balance optimizing reduction paths to prune dead branches 38% faster than standard approaches.

## Methodology

### I Ching Integration Components

1. **Hexagram State Space**: 64 states (000000 → 111111) mapped to factorization candidates
2. **Trigram Weights**: Five-element weights applied as geometric scaling factors 
3. **Yang-Balance Heuristic**: ~0.618 ratio optimization for branch pruning
4. **Recursive Depth Control**: Maximum 1000 levels with φ-based reduction
5. **Golden Ratio Scaling**: r_i = trigram_weight(hex) * σ * φ^(depth % 6)

### Technical Implementation

- **Base Framework**: Extended Z5D factorization from `src/c/rsa-4096-solver/z5d_factorization_shortcut.c`
- **Precision**: MPFR 256-bit for high-precision calculations
- **Mutation Logic**: Hexagram line changes drive candidate generation
- **Convergence**: gcd(N, trial) via golden Weyl trial = floor(φ * prev + hex_int) % floor(sqrt(N))

## Files

- `iching_hexagram.py` - Core I Ching hexagram state management
- `z_iching_integration.py` - Z Framework integration with I Ching logic
- `rsa4096_test_harness.py` - RSA-4096 factorization test framework
- `minimal_validation.py` - Minimal proof-of-concept test
- `results/` - Experimental results and validation data

## Validation Criteria

**Success Metrics**:
- Factor discovery within 1000 recursive steps
- 38% improvement in branch pruning efficiency vs. standard methods
- Empirical validation with bootstrap confidence intervals
- Statistical significance (p < 0.05) for yang-balance optimization claims

**Falsification Criteria**:
- No factors found within computational limits
- No measurable efficiency improvement over baseline Z5D
- Yang-balance optimization shows no statistical significance