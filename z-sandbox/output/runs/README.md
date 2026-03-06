# Geometric Resonance Factorization Experiments - README

## Overview
This directory contains the complete results of troubleshooting the `GeometricResonanceFactorizer` for the 127-bit semiprime:
```
N = 137524771864208156028430259349934309717
Expected factors (verified ✓): p = 10508623501177419659, q = 13086849276577416863
```

### Parameter Space Tested
- **k-range**: [0.28, 0.32], [0.29, 0.31], [0.295, 0.305]
- **J** (Dirichlet half-width): 4, 6
- **threshold**: 0.92, 0.95, 0.98, 0.992
- **mc-digits**: 220, 260, 300
- **samples**: 1000-2000
- **m-span**: 30-60
- **bias**: 0, 0.05, 0.1

### Fastest Configuration (Run 06)
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=260 --samples=1000 --m-span=30 --J=6 \
  --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0"
```
**Runtime**: 2m 6s | **Result**: No factors found

## Files

### Documentation
- **REPORT.md** - Comprehensive 5-page analysis with performance metrics, findings, and recommendations
- **summary.md** - Quick reference table of all 9 runs with parameters and outcomes
- **commands.md** - Copy-paste ready commands for reproducing all experiments

### Logs
- **run_01_baseline.log** through **run_09_mspan30.log** - Individual output logs for each experiment
  - Runs 01, 03, 06, 07, 09: Completed successfully (no factors found)
  - Runs 02, 04, 05, 08: Incomplete (exceeded 5-6 minute timeout)

### Scripts
- **run_experiments.sh** - Bash automation script for executing and logging runs
- **verify_factors.py** - Python script to verify expected factors (p × q = N)

## Quick Start

### Verify Expected Factors
```bash
python3 verify_factors.py
```

### Rerun Phase 1 Baseline
```bash
cd /home/runner/work/z-sandbox/z-sandbox
./gradlew run --args="137524771864208156028430259349934309717 \
  --mc-digits=220 --samples=1500 --m-span=40 --J=6 \
  --threshold=0.98 --k-lo=0.28 --k-hi=0.32 --bias=0"
```

### View All Commands
See `commands.md` for all 9 experimental configurations.

## Results Summary

**Total Runs**: 9  
**Completed**: 5 (within 2-5 minute range)  
**Timeout**: 4 (exceeded 5-6 minute limit)  
**Success Rate**: 0/9 - No factors found

### Best Performing Configuration (Fastest)
- Run 06: 2m 6s
- Parameters: mc-digits=260, samples=1000, m-span=30, J=6, threshold=0.98

### Parameter Sweet Spot (for <3min runs)
- mc-digits: 260
- samples: 1000-1200
- m-span: 30-40
- J: 4-6
- threshold: 0.98
- bias: 0

## Key Takeaways

1. **No factors found** in current parameter space
2. Runtime scales with **samples × m-span** (linear)
3. **mc-digits=300** adds 40% overhead vs 260
4. **m-span ≥ 50** OR **samples ≥ 1500** with bias > 0 causes timeout
5. Need to explore **wider k-range** (beyond [0.28, 0.32])

## Next Steps

See **REPORT.md** section "Recommendations" for:
- Expanded parameter ranges
- Multi-stage adaptive search strategies
- Alternative algorithmic approaches
- Hybrid factorization methods

---

**Experiment Date**: 2025-11-07  
**Total Experiment Time**: ~43 minutes  
**Expected Factors**: p = 10508623501177419659, q = 13086849276577416863 (verified ✓)
