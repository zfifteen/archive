# Fractal Cascade Structure Falsification Test

This experiment tests the claim that prime log-gaps exhibit recursive log-normal structure within magnitude strata, suggesting multiplicative cascade dynamics.

## Overview

The experiment:
1. Generates primes in specified disjoint ranges.
2. Stratifies log-gaps by magnitude (quintiles/deciles).
3. Fits log-normal distributions to each stratum.
4. Tests for power-law variance scaling ($\sigma_k \sim \mu_k^H$) to estimate the Hurst exponent $H$.
5. Compares results against null models (Cramér/Random, Cascade).

## Running the Experiment

### Prerequisites

Install dependencies:

```bash
pip install -r requirements.txt
```

### Execution

Run the experiment with default settings:

```bash
python run_experiment.py
```

Customize ranges and strata:

```bash
python run_experiment.py --ranges "1e7:2e7,2e7:3e7" --strata 20 --output results_custom/
```

### Output

The script produces:
- `results.json`: Detailed metrics for strata and ranges.
- `report.md`: Human-readable summary and falsification verdict.
- `scaling_*.png`: Variance scaling plots.

## Falsification Criteria

The claim is **falsified** if:
- Within-stratum log-normality fails (<50% pass KS test).
- Hurst exponent is unstable or outside [0.6, 1.0].
- Simple null models (Cramér) reproduce the structure.
