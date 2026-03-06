# Stadlmann Distribution Level Falsification Experiment

## Overview

This experiment attempts to falsify the hypothesis that Stadlmann's distribution level θ ≈ 0.525 (from arXiv:2212.10867) operates as a "tunable density dial" providing meaningful density enhancements in the Z5D framework.

## Files

- **falsification_experiment.py** - Main experiment implementation with 5 comprehensive tests
- **results.json** - Raw numerical results from the experiment run (seed=42)
- **EXECUTIVE_SUMMARY.md** - Detailed analysis and findings (READ THIS FIRST)

## Quick Results

**Status:** ⚠️ **PARTIAL FALSIFICATION**

- **Supported (4/5 tests):** Parameter functions as a "dial" (monotonic, scale-invariant, non-arbitrary)
- **Falsified (1/5 tests):** **Claimed 1-2% density boost is FALSE** - measured boost is only ~0.20% (5-10× smaller)

## Key Finding

The core practical claim is **falsified**: The claimed 1-2% density enhancement with CI [0.8%, 2.2%] is not supported by empirical testing. The actual measured boost is approximately **0.20%** with CI [0.20%, 0.20%].

## Running the Experiment

### Requirements

```bash
pip install numpy sympy scipy mpmath matplotlib
```

### Execution

```bash
python falsification_experiment.py --seed 42
```

### Expected Runtime

- Test 1 (Independence): ~10 seconds (100 predictions)
- Test 2 (Monotonicity): ~2 seconds (10 predictions)
- Test 3 (Claimed Boost): ~120 seconds (1,000 bootstrap × 10,000 primes)
- Test 4 (Scale Invariance): ~5 seconds (3 scales)
- Test 5 (Randomness): ~3 seconds (20 random values)

**Total:** ~2-3 minutes

## Test Descriptions

### Test 1: Independence Test
Verifies that changing θ actually affects predictions (not a no-op parameter).

### Test 2: Monotonicity Test
Checks if increasing θ produces monotonically increasing predictions (validates "dial" metaphor).

### Test 3: Claimed Boost Validation ⚠️
**FALSIFIED** - Tests the specific claim of 1-2% density boost with bootstrap CI.

### Test 4: Scale Invariance Test
Verifies that θ effects are consistent across different scales (10⁴ to 10⁶).

### Test 5: Randomness Test
Tests if θ=0.525 is special compared to random values in the valid range.

## Falsification Methodology

Each test has a clear **falsification criterion**:
- If the criterion is met, the test is marked **FALSIFIED**
- Otherwise, the test is marked **SUPPORTED**

The overall hypothesis status:
- **HYPOTHESIS_FALSIFIED**: ≥50% tests falsified
- **PARTIAL_FALSIFICATION**: Some tests falsified (1-49%)
- **HYPOTHESIS_SUPPORTED**: No tests falsified (0%)

## Statistical Rigor

- **Deterministic:** All tests use seed=42 for full reproducibility
- **Bootstrap CIs:** 1,000 resamples for confidence intervals (Test 3)
- **Large samples:** 100+ k values, 10,000 primes
- **Multiple scales:** 10⁴, 10⁵, 10⁶ for robustness
- **Clear thresholds:** Pre-defined falsification criteria (not post-hoc)

## Results Summary

| Test | Status | Key Metric | Falsification Criterion |
|------|--------|------------|------------------------|
| Independence | ✅ SUPPORTED | 0.84% effect size | <0.01% effect |
| Monotonicity | ✅ SUPPORTED | 0 direction changes | ≥2 changes |
| Claimed Boost | ❌ **FALSIFIED** | **0.20% boost** | **Outside [1%, 2%]** |
| Scale Invariance | ✅ SUPPORTED | CV=0.163 | CV>0.5 |
| Randomness | ✅ SUPPORTED | 0% similar | >50% similar |

## Interpretation

The Stadlmann distribution level **does** function as a "tunable dial" technically, but the **claimed practical benefit is grossly overstated**:

- ✅ Technical implementation is correct
- ✅ Parameter affects predictions measurably
- ✅ Behavior is monotonic and scale-invariant
- ❌ **Claimed 1-2% boost is FALSE** (actual: ~0.20%)
- ❌ **"First-class primitive" framing is misleading**

The 0.20% effect is:
- **5× smaller than claimed CI lower bound** (0.8%)
- **10× smaller than claimed minimum** (1.0%)
- Too weak for most practical applications

## Recommendations

1. **Update Documentation** - Correct the 1-2% claim to ~0.2%
2. **Review Benchmarks** - Re-examine existing validation methodology
3. **Clarify Theory** - Explain gap between Stadlmann's result and practical density
4. **Test at Ultra-Scales** - Perhaps effects emerge at k > 10⁶?

## References

- **Stadlmann 2023:** arXiv:2212.10867 - "On the level of distribution of primes in smooth arithmetic progressions"
- **Issue #931:** Original hypothesis description
- **Benchmarks:** `benchmarks/stadlmann_extended_validation.py`
- **Implementation:** `src/core/z_5d_enhanced.py`, `src/core/params.py`

## Citation

If you use this falsification experiment, please cite:

```
Stadlmann Distribution Level Falsification Experiment
Z Framework - github.com/zfifteen/unified-framework
experiments/stadlmann_falsification/
Date: 2025-11-18
```

## License

MIT License - Same as parent repository
