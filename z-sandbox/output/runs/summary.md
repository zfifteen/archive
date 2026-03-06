<<<<<<< HEAD
# Geometric Resonance Factorization Troubleshooting Summary

Target N: 137524771864208156028430259349934309717  
Expected Factors: p=10508623501177419659, q=13086849276577416863 (if p*q == N)

## Run Log

| Run ID | Command Args | Runtime | Result |
|--------|--------------|---------|--------|
| baseline_phase1 | --mc-digits=220 --samples=1500 --m-span=40 --J=6 --threshold=0.98 --k-lo=0.28 --k-hi=0.32 --bias=0 | ~2m 45s | No factor found |
| adjusted_phase2 | -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --mc-digits=260 --samples=1500 --m-span=60 --J=4 --threshold=0.992 --k-lo=0.295 --k-hi=0.305 --bias=0 | ~X min | Check log |
| k_widen_bias | -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --mc-digits=260 --samples=2000 --m-span=60 --J=4 --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0.1 | ~X min | Check log |
| precision_bump | -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --mc-digits=300 --samples=1500 --m-span=60 --J=6 --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0.1 | ~X min | Check log |

## Notes
- All runs executed with pinned parallelism where applicable.
- No factors found in completed runs; research ongoing.
- Logs saved in runs/ folder for each run.
=======
# Geometric Resonance Factorization Experiment Runs

**Target:** N = 137524771864208156028430259349934309717  
**Expected Factors (Verified ✓):**
- p = 10508623501177419659
- q = 13086849276577416863
- Verification: `p × q = N` (confirmed via `verify_factors.py`)

## Experiment Runs

| Run | Description | Parameters | Runtime | Result |
|-----|-------------|------------|---------|--------|
| 01 | Phase 1 Baseline | mc-digits=220, samples=1500, m-span=40, J=6, threshold=0.98, k=[0.28,0.32], bias=0 | 3m 12s | No factors |
| 02 | Phase 2 (fast) | mc-digits=260, samples=1500, m-span=60, J=4, threshold=0.992, k=[0.295,0.305], bias=0, parallelism=8 | >6m (timeout) | Incomplete |
| 03 | Reduced params | mc-digits=260, samples=1000, m-span=40, J=4, threshold=0.98, k=[0.29,0.31], bias=0, parallelism=8 | 2m 48s | No factors |
| 04 | Bias test | mc-digits=260, samples=2000, m-span=60, J=4, threshold=0.98, k=[0.29,0.31], bias=0.1, parallelism=8 | >6m (timeout) | Incomplete |
| 05 | J=6 with bias | mc-digits=260, samples=1500, m-span=40, J=6, threshold=0.98, k=[0.29,0.31], bias=0.1, parallelism=8 | >5m (timeout) | Incomplete |
| 06 | Small params | mc-digits=260, samples=1000, m-span=30, J=6, threshold=0.98, k=[0.29,0.31], bias=0, parallelism=8 | 2m 6s | No factors |
| 07 | High precision | mc-digits=300, samples=1000, m-span=40, J=4, threshold=0.98, k=[0.29,0.31], bias=0, parallelism=8 | 4m 21s | No factors |
| 08 | Lower threshold | mc-digits=260, samples=1500, m-span=50, J=4, threshold=0.95, k=[0.29,0.31], bias=0.05, parallelism=8 | >5m (timeout) | Incomplete |
| 09 | Balanced | mc-digits=260, samples=1200, m-span=30, J=4, threshold=0.98, k=[0.29,0.31], bias=0.05, parallelism=8 | 2m 51s | No factors |

## Summary of Findings

### Successfully Completed Runs
All runs that completed within the 5-minute timeout failed to find the factors. The following runs completed:
- Run 01: Phase 1 baseline (3m 12s)
- Run 03: Reduced parameters (2m 48s)
- Run 06: Small parameters (2m 6s)
- Run 07: High precision mc-digits=300 (4m 21s)
- Run 09: Balanced parameters (2m 51s)

### Timeout Issues
Several parameter combinations exceeded the 5-minute timeout:
- Runs 02, 04, 05, 08 timed out
- Common pattern: m-span ≥ 50 or samples ≥ 1500 with bias > 0 tends to timeout

### Parameter Sensitivity Observations
1. **m-span**: Values > 40 significantly increase runtime
2. **samples**: Values > 1500 often lead to timeouts when combined with other intensive parameters
3. **J**: Higher J values (6 vs 4) increase computational cost
4. **mc-digits**: 300 vs 260 adds ~90s overhead for same other parameters
5. **bias**: Non-zero bias appears to increase runtime

### Recommendations for Future Runs
To find factors while staying within 5-minute constraint:
- Keep m-span ≤ 40
- Keep samples ≤ 1500
- Use J=4 for faster runs, J=6 if more filtering needed
- Consider widening k-range beyond [0.29, 0.31]
- Try different threshold values (0.90-0.95 range)
- Experiment with negative bias values

### Current Status
**No factors found** across all completed parameter sweeps. The geometric resonance method has not yet successfully factored this 127-bit semiprime with the parameter ranges tested.
>>>>>>> a73510334277b5e046e2fdd69354e9e66ce2d640
