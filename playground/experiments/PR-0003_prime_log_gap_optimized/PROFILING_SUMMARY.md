# Performance Profiling Summary

**Date:** December 22, 2025  
**Analysis Tool:** `profiling/profile_experiment.py`  
**Detailed Report:** `PERFORMANCE_ANALYSIS.md`

## Executive Summary

Detailed performance profiling of the PR-0003 prime log-gap analysis experiment reveals that the claimed "sub-linear scaling with efficiency factor ~0.86" is **misleading**. The truth is more nuanced:

### Actual Scaling Behavior (10^6 → 10^7):

| Aspect | Scaling Exponent | Classification | Notes |
|--------|------------------|----------------|-------|
| **Core Computation** | **1.39** | **SUPER-LINEAR** | Dominated by Ljung-Box test |
| With Visualization | ~0.91 | Near-linear | Visualization is sub-linear |
| Time Ratio | 7.0x / 8.5x = 0.82 | "Efficiency" | Not a scaling exponent! |

### Component Breakdown:

| Component | Time @ 10^6 | Time @ 10^7 | Exponent | Notes |
|-----------|-------------|-------------|----------|-------|
| **Ljung-Box** | 0.58s | 44.5s | **2.03** | **Quadratic bottleneck** |
| KS Tests | 2.3s | 16.3s | 0.91 | Linear as expected |
| Prime Gen | 0.21s | 2.2s | 0.56 | Sub-linear (caching) |
| Binning | 0.06s | 0.09s | 0.21 | Sub-linear (fixed bins) |
| ACF/PACF | 0.08s | 0.53s | 0.92 | Linear (FFT-based) |
| **Total Compute** | **3.7s** | **61.6s** | **1.39** | **Super-linear** |
| Visualization | ~10s | ~33s | ~0.63 | Sub-linear (downsampling) |
| **Total Pipeline** | **~13.5s** | **~95s** | **~0.91** | Near-linear |

## Key Findings

### 1. The "0.86 Efficiency Factor" is Misleading

**Claimed:** "Execution scales sub-linearly (7x time for 8.5x data)"

**Reality:** 
- This is a simple ratio: 7.0 / 8.5 = 0.82
- NOT a scaling exponent
- Includes visualization which scales at ~0.63 (genuinely sub-linear due to downsampling)
- Core computation scales at 1.39 (super-linear)

### 2. Ljung-Box Test is the Bottleneck

The `statsmodels.stats.diagnostic.acorr_ljungbox()` function exhibits **O(n²) complexity**:

- 10^6: 0.58s (18% of compute time)
- 10^7: 44.5s (72% of compute time)
- **77x increase for only 8.5x more data**

This single component **destroys** any sub-linear scaling claim.

### 3. Impact on Larger Scales

Original estimates assumed sub-linear scaling across all components. **Corrected estimates:**

| Scale | Original Estimate | Corrected (with Ljung-Box) | Corrected (without Ljung-Box) |
|-------|-------------------|----------------------------|-------------------------------|
| 10^8 | ~15 minutes | **~50 minutes** | ~20 minutes |
| 10^9 | ~3 hours | **~40-50 HOURS** | ~3 hours |

**Recommendation:** For scales beyond 10^7, either:
1. Remove Ljung-Box test
2. Replace with approximate/sampled autocorrelation
3. Accept very long runtimes

### 4. What IS Sub-linear?

**Genuinely sub-linear components:**
1. **Binning analysis** (0.21 exponent) - Uses fixed 100 bins regardless of data size
2. **Linear regression** (0.01 exponent) - Always fits line to 100 bin means
3. **Visualization** (~0.63 exponent) - Downsamples to fixed resolutions

**Appears sub-linear due to caching:**
1. Prime generation (0.56) - Disk cache eliminates recomputation
2. Gap computation (0.61) - Disk cache eliminates recomputation

## Recommendations

### For Future Work:
1. **Update documentation** to clarify that "sub-linear" refers to total pipeline including visualization
2. **Separate "computational scaling" from "total pipeline scaling"** in performance claims
3. **Acknowledge Ljung-Box bottleneck** explicitly
4. **Provide estimates both with and without Ljung-Box**

### For Scaling Beyond 10^7:
1. **Replace Ljung-Box** with alternative autocorrelation approach:
   - Sample-based testing (test on random subset)
   - Approximate methods with linear complexity
   - Or remove autocorrelation testing entirely
2. **Consider parallel processing** for independent components
3. **Use more aggressive caching** strategies

## How to Verify

Run the profiling yourself:

```bash
cd experiments/PR-0003_prime_log_gap_optimized
python3 profiling/profile_experiment.py --scales 1e6,1e7 --bins 100
```

Results are saved to `profiling_results.json` with detailed timing for each component.

For comprehensive analysis, see `PERFORMANCE_ANALYSIS.md` which includes:
- Complete program flow documentation
- Algorithm complexity analysis
- Memory profiling
- Detailed explanations of each component's scaling behavior

## Conclusion

The PR-0003 experiment demonstrates excellent engineering (segmented sieve, caching, 100-bin strategy) and produces valid statistical results. However, the performance claims need clarification:

✅ **True:** Visualization scales sub-linearly due to downsampling  
✅ **True:** Some components (binning, regression) are genuinely sub-linear  
❌ **False:** Core computation scales sub-linearly (actually 1.39, super-linear)  
❌ **Misleading:** "Efficiency factor ~0.86" (this is a ratio, not an exponent, and includes visualization)

The correct statement would be: **"Total pipeline time scales near-linearly (0.91 exponent) due to sub-linear visualization offsetting super-linear statistical tests. Core computation scales at 1.39 exponent, dominated by the quadratic Ljung-Box autocorrelation test."**
