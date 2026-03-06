# PR-0006: Hypothesis Falsification Test

## Experiment Overview

This experiment tests the core hypothesis about the AI-augmented scientific falsification pipeline in the zfifteen/playground repository.

## Hypothesis Being Tested

**Primary Hypothesis:**
> The repository pioneers an AI-augmented scientific falsification pipeline for prime gap modeling, revealing inconsistencies in traditional exponential distributions via iterative experiments that integrate high-precision prime generation, potentially enabling more robust cryptographic prime selection by identifying fractal-like cascades and hybrid patterns in gap sequences.

**Secondary Hypothesis:**
> It showcases a reversed hierarchy discovery mechanism in experimental analysis, where bottom-up pattern detection (starting from raw prime data) outperforms top-down assumptions, leading to fewer false positives in distribution falsification and suggesting a novel abstraction for scalable statistical validation in computational number theory.

## Experimental Design

### Components

1. **Falsification Pipeline Validation**
   - Tests effectiveness of iterative falsification approach
   - Measures detection rate of distribution inconsistencies
   - Validates integration with high-precision prime generation

2. **Distribution Testing**
   - Compares exponential vs lognormal distribution fits
   - Uses information criteria (AIC, BIC) for model selection
   - Performs goodness-of-fit tests (KS, Anderson-Darling)

3. **Fractal Cascade Detection**
   - Tests for self-similar structure in prime gaps
   - Estimates Hurst exponent across magnitude strata
   - Validates variance scaling relationships

4. **Approach Comparison: Bottom-Up vs Top-Down**
   - Bottom-up: Starts from raw data, detects patterns empirically
   - Top-down: Starts from theoretical assumptions (Cramér model)
   - Compares false positive rates and convergence efficiency

### Falsification Criteria

The hypothesis will be **FALSIFIED** if:

1. Lognormal distribution does NOT significantly outperform exponential (ΔBIC < 10) in >50% of trials
2. No fractal cascade structure detected (Hurst exponent H not stable around 0.8)
3. Bottom-up approach does NOT show fewer false positives than top-down
4. Reversed hierarchy pattern (from PR-0005) does NOT replicate in new data

The hypothesis will be **SUPPORTED** if:

1. Lognormal consistently outperforms exponential distribution
2. Fractal cascade structure detected with stable Hurst exponent
3. Bottom-up approach shows measurably better performance
4. Reversed hierarchy pattern replicates consistently

## Running the Experiment

```bash
cd experiments/PR-0006_hypothesis_falsification_test
python3 run_experiment.py
```

### Output Files

- `results/experiment_results.json` - Complete experimental data
- `FINDINGS.md` - Human-readable findings (conclusion first)
- `data/config.json` - Experiment configuration used
- `results/summary.txt` - Quick summary of key results

## Methodology

### Data Collection
- Prime gaps extracted from multiple ranges (10^6 to 10^8)
- Multiple independent trials per range for statistical robustness
- Reproducible with fixed random seed

### Statistical Methods
- Kolmogorov-Smirnov test for distribution fitting
- Anderson-Darling test for tail behavior
- AIC/BIC for model comparison
- Log-log regression for Hurst exponent estimation
- Moment-based convergence analysis

### Reproducibility
- All random seeds fixed (seed=42)
- Complete configuration saved
- Code is self-contained within this directory
- No modifications to parent repository experiments

## Expected Timeline

- Implementation: Incremental (following agent protocol)
- Execution: ~10-30 minutes depending on prime ranges
- Analysis: Automated via analysis pipeline
- Documentation: Auto-generated FINDINGS.md

## References

Related experiments in this repository:
- `PR-0005_reversed_hierarchy_discovery` - Reversed hierarchy pattern
- `falsify/fractal-cascade-structure` - Fractal cascade testing
- `falsify/lognormal-vs-exponential` - Distribution comparison
- `PR-0003_prime_log_gap_optimized` - Prime generation utilities

## Status

- [x] Experiment design complete
- [x] Directory structure created
- [x] Main framework skeleton implemented
- [ ] Component implementations (incremental)
- [ ] Execution and data collection
- [ ] Results analysis
- [ ] FINDINGS.md generation
