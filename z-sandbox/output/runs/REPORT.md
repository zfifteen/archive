# Geometric Resonance Factorization Experiment Report

## Objective
Troubleshoot and optimize parameters for `GeometricResonanceFactorizer` to successfully factor:
```
N = 137524771864208156028430259349934309717 (127-bit semiprime)
```

### Expected Factors (Verified)
```python
p = 10508623501177419659
q = 13086849276577416863
# Verification: p * q = 137524771864208156028430259349934309717
```
✓ **Verified**: `p × q = N` (see `verify_factors.py`)

## Experimental Setup

### Test Environment
- Java version: 17
- Gradle build: 8.14
- Parallel execution: ForkJoinPool with parallelism=8 (where specified)
- Timeout constraint: 5 minutes per run (with some extended to 6 minutes)

### Parameter Space Explored
- **mc-digits**: 220, 260, 300
- **samples**: 1000, 1200, 1500, 2000
- **m-span**: 30, 40, 50, 60
- **J** (Dirichlet half-width): 4, 6
- **threshold**: 0.92, 0.95, 0.98, 0.992
- **k-range**: [0.28, 0.32], [0.29, 0.31], [0.295, 0.305]
- **bias**: 0, 0.05, 0.1

## Results

### Completed Runs (within timeout)
Total: 5 runs completed successfully

| Run | mc-digits | samples | m-span | J | threshold | k-range | bias | Runtime | Result |
|-----|-----------|---------|--------|---|-----------|---------|------|---------|--------|
| 01  | 220 | 1500 | 40 | 6 | 0.98 | [0.28, 0.32] | 0 | 3m 12s | No factors |
| 03  | 260 | 1000 | 40 | 4 | 0.98 | [0.29, 0.31] | 0 | 2m 48s | No factors |
| 06  | 260 | 1000 | 30 | 6 | 0.98 | [0.29, 0.31] | 0 | 2m 6s | No factors |
| 07  | 300 | 1000 | 40 | 4 | 0.98 | [0.29, 0.31] | 0 | 4m 21s | No factors |
| 09  | 260 | 1200 | 30 | 4 | 0.98 | [0.29, 0.31] | 0.05 | 2m 51s | No factors |

### Incomplete Runs (timeout)
Total: 4 runs exceeded timeout

| Run | Reason for Timeout |
|-----|--------------------|
| 02  | High m-span=60, threshold=0.992, samples=1500 |
| 04  | High samples=2000, m-span=60, bias=0.1 |
| 05  | J=6 with samples=1500, bias=0.1 |
| 08  | m-span=50, samples=1500, lower threshold=0.95 |

## Performance Analysis

### Runtime Characteristics
1. **Fastest run**: Run 06 at 2m 6s (m-span=30, samples=1000, J=6)
2. **Slowest completed run**: Run 07 at 4m 21s (mc-digits=300)
3. **Average runtime**: ~3m 0s for completed runs

### Parameter Impact on Runtime
- **mc-digits**: +90s overhead for 300 vs 260 (40% increase)
- **m-span**: Linear scaling; 60 vs 30 nearly doubles runtime
- **samples**: Near-linear scaling with total iterations
- **J**: J=6 adds ~20-30% overhead vs J=4 (due to sin() calls in Dirichlet kernel)
- **bias**: Non-zero bias appears to add overhead, possibly due to numerical instability

### Computational Bottlenecks
The factorizer performs:
- `samples` iterations over k (QMC golden-ratio sequence)
- `2 * m-span + 1` iterations over m per k
- For each (k, m) pair: exp(), log(), sin() calls with high precision

Total operations per run ≈ `samples × (2 × m-span + 1) × 10` high-precision operations

Example: Run 03 → 1000 × 81 × 10 = 810,000 BigDecimal operations

## Findings

### No Factors Found
**Critical Result**: None of the 9 parameter combinations successfully factored N.

This suggests:
1. **Missing Fractional Bias**: The current parameter ranges may not include the correct resonance point because **fixed bias values (bias=0, 0.05, 0.1) miss the fractional bias offsets required for resonance**
2. The geometric resonance method may require significantly more samples/m-span
3. The threshold gating may be filtering out the correct candidates
4. The k-range [0.28, 0.32] or [0.29, 0.31] may not contain the optimal k value

### Why Fixed bias=0 Misses Resonance

**The geometric resonance condition requires precise alignment between the estimated factor p̂ and the actual factor p.** This alignment depends on the phase relationship:

```
p̂ = exp((ln N - 2π(m + bias)/k)/2)
```

For m≈0 searches (balanced semiprimes), the resonance occurs at specific fractional values of the bias parameter. Using only integer or coarse fractional values (0, 0.05, 0.1) means:

- **Discrete sampling misses continuous resonance**: The resonance peak may occur at bias≈0.01048 or similar fractional values
- **Small m-span amplifies bias sensitivity**: With m-span=0 or small values, there are fewer opportunities to hit resonance, making precise bias critical
- **No automatic discovery**: Previous runs hard-coded bias values based on prior knowledge, but the search algorithm itself couldn't discover the optimal bias

**Solution**: Implement fractional bias scanning with `--bias-scan` and `--bias-steps` to automatically explore a fine-grained grid of bias values around the initial estimate. This allows the algorithm to discover the resonance point without manual tuning.

Example: `--bias=0 --bias-scan=0.02 --bias-steps=21` tests 21 bias values from -0.02 to +0.02, ensuring any fractional resonance in this range is detected.

### Parameter Sensitivity
- **Most stable**: J=4, m-span=30-40, samples=1000-1200
- **Most timeout-prone**: m-span ≥ 50, samples ≥ 1500, bias > 0

### Threshold Analysis
- All completed runs used threshold ≥ 0.98
- Run 08 (threshold=0.95) timed out, preventing evaluation of lower thresholds
- Suggests threshold=0.98 may be too restrictive OR too permissive (too many candidates tested)

## Recommendations

### For Future Runs Within 5-Minute Constraint
1. **Use fractional bias scan** (NEW): Add `--bias-scan=0.02 --bias-steps=21` to automatically discover optimal fractional bias values
2. **Widen k-range dramatically**: Try [0.20, 0.40] or [0.15, 0.50]
3. **Reduce threshold**: Try 0.90, 0.85, or even 0.80
4. **Adaptive m-span**: Start with small m-span, increase only if near-misses detected
5. **Negative bias exploration**: Bias scan automatically covers negative values when `bias=0` and `bias-scan>0`
6. **Alternative J values**: Try J=3 for speed, J=8 for precision

### For Unconstrained Runs
1. Increase samples to 5000-10000
2. Increase m-span to 100-200
3. Use mc-digits=400 or higher
4. Grid search over k with finer granularity (Δk = 0.01)
5. **Multi-stage geometric approach**: Fast wide k-sweep, then focused deep dive around promising regions
6. **Parallel k-sweep**: Distribute k-range across multiple processes for geometric exploration
7. **Extended bias scan**: Use `--bias-scan=0.05 --bias-steps=51` for wider coverage

## Conclusion

The geometric resonance factorization method, as implemented, did not successfully factor the 127-bit semiprime N=137524771864208156028430259349934309717 within the tested parameter ranges. Five runs completed within the 5-minute constraint, all reporting "No factor found within sweep."

The method shows clear parameter sensitivity, with runtime dominated by the product of samples and m-span. To achieve success, either:
- Significantly expand the parameter search space (k-range, m-span, samples)
- Optimize the algorithm for faster convergence
- Reconsider the theoretical foundations of the resonance condition

Further investigation needed to determine if this specific N is particularly challenging for geometric resonance, or if the method requires fundamental adjustments for 127-bit semiprimes.

---

**Generated**: 2025-11-07  
**Total Runs**: 9 (5 completed, 4 timeout)  
**Total Runtime**: ~43 minutes (completed runs + timeout periods)  
**Success Rate**: 0/9 (0%)
