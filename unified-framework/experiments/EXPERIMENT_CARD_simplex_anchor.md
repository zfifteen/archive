# EXPERIMENT CARD: Simplex-Anchor A/B Validation

## Overview

**Experiment ID:** `simplex_anchor_ab_validation`  
**Version:** 1.0.0  
**Date Created:** 2025-11-09  
**Status:** Active  
**Assignees:** @copilot

## Objective

Validate and integrate the confirmed 7.84% prime-density enhancement (simplex-anchor: A₄ × Euler × self-duality → E = 1.078437) into two critical pipelines:

1. **RSA Key Generation**: Improve candidate prime density to reduce Miller-Rabin trials
2. **Geometric-Resonance Factorization**: Better early-rank hits to reduce time-to-first-factor

## Hypothesis

The simplex-anchor enhancement factor E = 1.078437 (product of A₄=1.041667, Euler=1.02, self-duality=1.015) will:

- **Keygen**: Reduce median wall-clock time per keypair by ≥5% (95% CI not crossing 0)
- **Resonance**: Reduce median time-to-first-factor (TTF) by ≥10% and increase top-25 precision by ≥5%
- **Ablation**: The product significantly outperforms each component alone

## Mathematical Foundation

### Enhancement Factor Derivation

```
E = A₄ × Euler × Self-dual
E = 1.041667 × 1.02 × 1.015
E = 1.078437
```

### Expected Improvements

**1024-bit RSA:**
- Baseline: ~354.89 candidates/prime
- With E: ~329.09 candidates/prime
- Reduction: 7.27%

**2048-bit RSA:**
- Baseline: ~709.78 candidates/prime
- With E: ~658.18 candidates/prime
- Reduction: 7.27%

## Experimental Design

### A/B Test Conditions

1. **Baseline**: No enhancement (E=1.0)
2. **Simplex**: Full product (E=1.078437)
3. **A4**: A₄ factor only (1.041667)
4. **Euler**: Euler factor only (1.02)
5. **Self-dual**: Self-duality only (1.015)

### Sample Sizes

#### Keygen
- Full suite: 10,000 trials per (bit_length, condition)
- Quick shard: 500 trials (for CI/PR checks)
- Bit lengths: [1024, 2048]

#### Resonance
- Full suite: 50 semiprimes × 100 runs per (band, condition)
- Quick shard: 5 runs (for CI/PR checks)
- Bands: easy (40-60 bits), med (80-100 bits), hard (120-140 bits)

### Fixed Seeds

- **Master seed**: 1337
- **Keygen seeds**: derived via `hash(master_seed || "keygen" || bit_length || condition)`
- **Resonance seeds**: derived via `hash(master_seed || "resonance" || band || condition)`

All RNG states recorded in JSON summaries for full reproducibility.

## Metrics

### Keygen
- **Primary**: Wall-clock time per keypair (milliseconds)
- **Secondary**: 
  - Candidates tested per prime found
  - Miller-Rabin calls per keypair
  - MR time vs total time breakdown

### Resonance
- **Primary**: Time-to-first-factor (TTF) in seconds
- **Secondary**:
  - Top-K precision/recall (K=10, 25, 50)
  - Tail index (heavy-tail characterization)
  - First-quartile hazard rate
  - Success rate within budget

## Statistical Tests

1. **Bootstrap Confidence Intervals**: 1000 iterations, percentile method
2. **Kolmogorov-Smirnov Test**: Distribution differences (α=0.05)
3. **Log-Rank Test**: Survival curve comparison for TTF (α=0.05)
4. **Effect Size**: Cohen's d or Hedges' g for practical significance

## Acceptance Criteria (Definition of Done)

### Keygen
✅ Median wall-clock ↓ ≥ 5% (95% CI not crossing 0)  
✅ No correctness regressions (all primes validate)  
✅ Ablation: Product > components (statistically significant)

### Resonance
✅ Median TTF ↓ ≥ 10% (95% CI not crossing 0)  
✅ Top-25 precision ↑ ≥ 5%  
✅ Lighter tail (lower tail index OR higher first-quartile hazard)  
✅ No correctness regressions (all factors validate)

### Infrastructure
✅ No fallback code paths in resonance pipelines  
✅ All artifacts (CSV/JSON/plots) generated and uploaded  
✅ Experiment deterministic locally and in CI  
✅ Config, seeds, env/versions committed

## Implementation Files

### Core Logic
- `src/z5d/simplex_anchor.py`: Enhancement factor application
- `tests/test_simplex_anchor.py`: Unit tests for correctness

### Keygen Pipeline
- `src/experiments/keygen_ab.py`: A/B test harness
- `cli/keygen_ab.py`: Command-line interface
- `tests/test_keygen_ab.py`: Deterministic validation

### Analysis & Visualization
- `src/analysis/bootstrap.py`: Confidence intervals
- `src/analysis/distributions.py`: KS, log-rank, tail statistics
- `src/plots/keygen.py`: Box plots, CIs, time breakdowns
- `src/plots/resonance.py`: Survival curves, precision/recall

### Configuration
- `configs/simplex_anchor_experiment.json`: All parameters, seeds, thresholds

### CI/CD
- `.github/workflows/experiment_simplex_anchor.yml`: Automated testing

## Results Structure

```
results/
├── keygen_simplex_anchor/
│   ├── baseline_1024/
│   │   ├── metrics.csv
│   │   ├── summary.json
│   │   └── distribution.png
│   ├── simplex_1024/
│   ├── A4_1024/
│   ├── euler_1024/
│   ├── self_dual_1024/
│   └── [same for 2048]
└── resonance_simplex_anchor/
    ├── baseline_easy/
    │   ├── ttf_metrics.csv
    │   ├── summary.json
    │   └── survival_curve.png
    ├── simplex_easy/
    └── [same for med, hard]
```

## CLI Usage Examples

### Quick Keygen Test (CI/PR)
```bash
python -m cli.keygen_ab \
  --bits 1024 \
  --condition baseline \
  --trials 500 \
  --seed 1337 \
  --out-dir results/keygen_simplex_anchor/baseline_1024
```

### Full Keygen Suite (Nightly)
```bash
for bits in 1024 2048; do
  for cond in baseline simplex A4 euler self_dual; do
    python -m cli.keygen_ab \
      --bits $bits \
      --condition $cond \
      --trials 10000 \
      --seed 1337 \
      --out-dir results/keygen_simplex_anchor/${cond}_${bits}
  done
done
```

### Ablation Analysis
```bash
python -m src.analysis.ablation_report \
  --keygen-dir results/keygen_simplex_anchor \
  --output experiments/reports/ablation_summary.md
```

## Notes & Limitations

1. **Scope**: N < 10,000 factorization results are smoke tests only; do not generalize
2. **Runtime**: MR share of keygen varies by stack—report both MR and total time
3. **Precision**: Maintain mpmath dps=50; record in all JSON summaries
4. **Resonance**: This card documents keygen; resonance implementation lives in z-sandbox repo
5. **Fallbacks**: All fallback/hybrid code paths have been removed from resonance pipelines

## References

- Issue #[TBD]: Z5D Simplex-Anchor A/B Validation
- A₄ Symmetry: Alternating group of degree 4
- Euler Factor: Related to Euler's totient function prime density
- Self-Duality: Geometric duality in 5D space

## Change Log

- **2025-11-09**: Initial experiment card created
