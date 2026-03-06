# BASELINE_WALL_4_PERCENT

**Issue**: #196 - Break the 4% Wall and Prove Path to RSA  
**Date**: November 2, 2025  
**Purpose**: Frozen baseline for the ~4% relative distance wall in RSA-2048 seed accuracy. All future improvements must beat this control.

## Baseline Conditions (Frozen)
- **N**: Known RSA-2048 balanced semiprime (hardcoded in `rsa_k_sweep.py`)
- **k Range**: 0.250 to 0.350 (11 values, step 0.010)
- **Detunes**: ±0.5% per k_base (k_plus = k_base * 1.005, k_minus = k_base * 0.995)
- **Pipeline**: Green's function resonance with phase-bias, Dirichlet sharpening, κ-weighting, dual-k intersection
- **Refinements**: None (pure resonance only)
- **RNG Seed**: 1337 (deterministic)
- **Max Candidates**: 20 per k run
- **Hardware**: CPU-only, single-process

## Baseline Results
- **Global Best k_base**: 0.250
- **Global Best Relative Distance**: ~3.92% (to smaller factor)
- **Global Best Absolute Distance**: ~10^305 integers
- **Stability**: Consistent across runs with fixed seed
- **Interpretation**: Resonance seeds are ~4% away from true factors; ±1000 refinement cannot hit at this distance.

## Validation
- Run `python3 python/examples/rsa_k_sweep.py` with above conditions.
- Assert global_best_rel_distance ≈ 0.0392.
- CI test: `assert baseline_distance < 0.05` (wall exists).

## Future Improvements
Any method beating 3.92% relative distance demonstrates wall-breaking. Track progress here.

**Note**: This baseline is locked. Changes to conditions invalidate comparisons.