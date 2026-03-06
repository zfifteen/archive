# Comparison: Falsification vs Existing Benchmark

## Overview

This document compares the results from our falsification experiment with the existing `benchmarks/stadlmann_extended_validation.py` benchmark.

## Key Finding: **Both Show ~0.2% Enhancement**

### Our Falsification Experiment
```
Test 3: Claimed Boost Validation
- Measured boost: 0.2025%
- 95% CI: [0.2021%, 0.2029%]
- Method: Bootstrap with conical_density_enhancement_factor
```

### Existing Benchmark
```
Distribution Level Analysis (θ = 0.525)
- Enhancement: 0.1000%
- 95% CI: [0.1000%, 0.1000%]
- Method: Bootstrap with BOOST_SCALING_FACTOR
```

### Scale Dependence Test (Both)
```
Our Test (Test 4):
- 10^4: 0.179%
- 10^5: 0.223%
- 10^6: 0.268%

Existing Benchmark:
- 10^4: 0.179%  (identical!)
- 10^5: 0.223%  (identical!)
- 10^6: 0.268%  (identical!)
```

## Agreement Between Tests

**Perfect agreement on scale dependence:**
- Both show ~0.18% at 10^4
- Both show ~0.22% at 10^5
- Both show ~0.27% at 10^6

**Slight difference in bootstrap test:**
- Our test: 0.20% (using full conical flow calculation)
- Existing: 0.10% (using simplified scaling factor)

The difference is likely due to:
1. Different sample sizes (10K primes vs 10K subset)
2. Different baseline (0.51 vs 0.5)
3. Different calculation method

## Claimed vs Measured

### Documentation Claims
From `benchmarks/README.md`:
```
Claims Tested:
- 1-2% density boost with CI [0.8%, 2.2%] for k ≥ 10^5
```

From `src/core/z_5d_enhanced.py:319`:
```python
# Notes:
#     - dist_level default (0.525) provides 1-2% hypothesized density boost 
#       (CI [0.8%, 2.2%])
```

### Actual Measurements

**Both experiments agree:**
- Measured: **0.1-0.27%** (depending on scale and method)
- Claimed: **1-2%** with CI [0.8%, 2.2%]
- **Discrepancy: 5-10× smaller than claimed**

## Why the Existing Benchmark Didn't Catch This

Looking at `benchmarks/stadlmann_extended_validation.py:130-142`:

```python
# Only check claims if verify_claims is True
if verify_claims:
    within_range = (0.8 <= result['mean_enhancement'] <= 2.2)
    status = "✓ PASS" if within_range else "  FAIL"
else:
    # Just check if pipeline runs and statistics are well-formed
    within_range = True  # Assume pass for now
    status = "✓ RUN"
```

**The existing benchmark has a `--verify-claims` flag that is OFF by default!**

Let's run it with the flag enabled:

```bash
python benchmarks/stadlmann_extended_validation.py --seed 42 --max-n 100000 --verify-claims
```

Expected result: **All tests will FAIL** because measured enhancement is ~0.1%, not in [0.8%, 2.2%].

## The Bootstrap Calculation

### Existing Benchmark Method
From `benchmarks/stadlmann_extended_validation.py:44-87`:

```python
def bootstrap_density_enhancement(primes, dist_level, n_bootstrap=1000, rng=None):
    # Simplified model based on the dist_level parameter
    BOOST_SCALING_FACTOR = 0.04  # ~2% at θ=0.55
    boost_factor = 1.0 + (dist_level - DIST_LEVEL_MIN) * BOOST_SCALING_FACTOR
    enhanced_count = baseline_count * boost_factor
    enhancement_pct = (enhanced_count - baseline_count) / baseline_count * 100
```

**Issues:**
1. Uses hardcoded `BOOST_SCALING_FACTOR = 0.04` ("~2% at θ=0.55")
2. This is a **linear extrapolation**, not actual density calculation
3. The 2% claim is **baked into the test itself**!

For θ = 0.525:
```
boost_factor = 1.0 + (0.525 - 0.5) * 0.04
             = 1.0 + 0.025 * 0.04
             = 1.001
             = 0.1% boost
```

**This explains the 0.1% result!** The benchmark is using a simplified linear model, not the actual conical flow enhancement.

### Our Falsification Method

We use the **actual conical_density_enhancement_factor()** function:

```python
for idx in sample_indices:
    p = primes[idx]
    baseline_enh = conical_density_enhancement_factor(p, dist_level=baseline_theta)
    stadlmann_enh = conical_density_enhancement_factor(p, dist_level=stadlmann_theta)
    baseline_density += float(baseline_enh)
    stadlmann_density += float(stadlmann_enh)

boost_pct = (stadlmann_density - baseline_density) / baseline_density * 100
```

This directly measures what the framework's actual implementation produces.

## Conclusion

### The Discrepancy is Real

Both tests agree: **~0.2% enhancement, not 1-2%**

The existing benchmark:
- ✅ Correctly measures scale dependence (matches our results exactly)
- ✅ Has `--verify-claims` flag to catch this issue
- ❌ Runs without verification by default (prints "✓ RUN" instead of "✓ PASS"/"FAIL")
- ❌ Uses simplified linear model instead of actual conical flow calculation

### Where the 1-2% Claim Came From

**Hypothesis:** The claim may have originated from:

1. **Linear extrapolation error:**
   ```
   BOOST_SCALING_FACTOR = 0.04  # ~2% at θ=0.55
   ```
   This suggests someone calculated: "If θ=0.55 gives 2%, then θ=0.525 gives 1%"
   
   But this is **not validated** - it's a guess baked into the test!

2. **Conflation with other enhancements:**
   - Geodesic enhancement: ~15-20% (different technique)
   - Z5D error improvement: <0.01% (different metric)
   - These were likely mixed up with θ enhancement

3. **Theoretical misinterpretation:**
   - Stadlmann's θ ≈ 0.5253 is an **error term exponent**
   - Someone may have incorrectly translated this to "0.5253 provides 2% density boost"

### Recommendations

1. **Fix the benchmark:**
   ```python
   # Replace hardcoded BOOST_SCALING_FACTOR with actual calculation
   - BOOST_SCALING_FACTOR = 0.04  # ~2% at θ=0.55
   + # Use actual conical_density_enhancement_factor
   ```

2. **Enable verification by default:**
   ```python
   - parser.add_argument('--verify-claims', action='store_true')
   + parser.add_argument('--verify-claims', action='store_true', default=True)
   + parser.add_argument('--no-verify', action='store_false', dest='verify_claims')
   ```

3. **Update all documentation** to reflect true ~0.2% enhancement

## Running the Corrected Benchmark

```bash
# With claim verification (will fail)
python benchmarks/stadlmann_extended_validation.py --seed 42 --verify-claims

# Expected output:
# θ=0.525: 0.1000% - FAIL (outside [0.8%, 2.2%])
```

This would have caught the issue immediately if run with `--verify-claims`.

---

**Prepared by:** Z-Mode Falsification Engine  
**Date:** 2025-11-18  
**Status:** Both experiments agree - claims are falsified
