# Experiment Summary

## Quick Start

To review the experiment findings:
```bash
cat FINDINGS.md
```

To re-run the experiment:
```bash
pip install -r requirements.txt
python3 run_experiment.py
```

## What This Experiment Tests

This experiment was designed to definitively test the core hypothesis about the zfifteen/playground repository:

> The repository pioneers an AI-augmented scientific falsification pipeline for prime gap modeling, revealing inconsistencies in traditional exponential distributions via iterative experiments that integrate high-precision prime generation.

## Key Results

**VERDICT: FALSIFIED (high confidence)**

While the experiment confirmed that prime gaps are better modeled by lognormal distributions than exponential distributions (100% win rate), the more complex claims about fractal cascades and reversed hierarchy patterns did not replicate at the tested scales.

### What Was Confirmed (1/4 components)
- ✓ Lognormal distribution outperforms exponential (ΔBIC > 10 in all trials)

### What Was Not Confirmed (3/4 components)
- ✗ Fractal cascade structure (0% detection rate)
- ✗ Bottom-up analysis advantage (top-down won all comparisons)
- ✗ Reversed hierarchy pattern (did not replicate at tested scales)

## Scientific Interpretation

This is a **valid and important scientific result**. It shows that:

1. The basic distribution claim is robust and replicates
2. The more complex structural patterns may be:
   - Scale-dependent (requiring larger n values)
   - Artifacts of specific analysis methods
   - Present but requiring different detection methods

The experiment successfully demonstrates a rigorous falsification approach where not all claims are supported, which is exactly what good science should do.

## Files Generated

- `FINDINGS.md` - Complete findings document (conclusion first, as required)
- `results/experiment_results.json` - Full experimental data
- `results/summary.txt` - Quick summary statistics
- `data/config.json` - Experiment configuration used

## Reproducibility

- Random seed: 42 (fixed)
- Prime ranges: [100k, 1M] and [1M, 5M]
- Trials per range: 3
- All code self-contained in this directory
- No modifications to parent repository

## References

This experiment integrates concepts from:
- `PR-0005_reversed_hierarchy_discovery` - Reversed hierarchy testing
- `falsify/fractal-cascade-structure` - Fractal cascade detection
- `falsify/lognormal-vs-exponential` - Distribution comparison methodology
- `PR-0003_prime_log_gap_optimized` - Prime generation approach
