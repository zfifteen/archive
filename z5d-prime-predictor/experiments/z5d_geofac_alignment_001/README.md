# Z5D-Geofac Exploratory Alignment Experiment

## Overview

This experiment studies whether a Z5D-derived peak pipeline and Geofac produce overlapping bin structure when driven by the same quasi-Monte Carlo seed stream. It is an exploratory overlap study, not a validation of the active nth-prime predictor.

## What this experiment is and is not

It is:
- a descriptive comparison of two scoring / binning pipelines
- a way to test whether overlap is strong enough to justify more investigation
- a reproducible experiment shell for further study

It is not:
- proof that the active predictor is geometrically validated
- proof that Geofac and the predictor detect the same underlying phenomenon
- a substitute for the predictor's direct parity and benchmark checks

## Important limitation

`tools/run_z5d_peaks.py` can use either:
- the repo's `z5d_cli` binary, or
- a documented surrogate mock path when that binary is unavailable

Results produced through the surrogate path are exploratory convenience outputs, not equivalent evidence for the active predictor implementation.

## Legacy threshold check

This experiment keeps a legacy descriptive threshold:
- `Jaccard >= 0.20`
- `CI lower bound > 0.10`

If a run exceeds those values, read that as "overlap worth further study under this pipeline," not as predictor validation.

## Current committed summary

The committed summary in `docs/EXPERIMENT_SUMMARY_phi_qmc_001_test.md` records one exploratory run with:
- `Jaccard = 0.3067`
- `95% CI = [0.1731, 0.2256]`
- `Top-K hit rate = 43.17%`

That result is descriptive for the recorded pipeline and dataset only.

## Quick start

```bash
cd tools
python run_experiment.py --samples 1000 --max-process 100 --test
```

## Outputs

- `artifacts/seedsets/` - QMC seed sets
- `artifacts/z5d/` - Z5D-derived peak outputs
- `artifacts/geofac/` - Geofac outputs
- `artifacts/alignment/` - overlap reports
- `docs/` - generated human-readable summaries

## Recommended reading order

1. Read the committed summary as an exploratory result.
2. Check whether the run used the active CLI or a surrogate path.
3. Compare the result against direct predictor verification in the root docs before drawing broader conclusions.
