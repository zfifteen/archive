# Z5D-Geofac Exploratory Alignment Report

## Executive Summary

**Result: one exploratory run exceeded the legacy overlap threshold**

This document records a committed exploratory run comparing a Z5D-derived peak pipeline with Geofac under a shared QMC seed stream. The overlap metrics in this note describe that pipeline, dataset, and binning setup. They do **not** by themselves validate the active nth-prime predictor.

### Recorded metrics

| Metric | Value | Reading |
|--------|-------|---------|
| **Jaccard Index** | **0.3067** | Descriptive overlap for this run |
| **95% Confidence Interval** | [0.1731, 0.2256] | Above the legacy lower-bound threshold |
| **Top-K Hit Rate** | 43.17% | 43.17% of Z5D bins also appeared in Geofac |
| **Spearman ρ** | -0.1456 | Weak / no rank agreement |

## Interpretation

The recorded run shows non-trivial overlap in binned outputs, but the same run also shows weak rank correlation. That combination supports further investigation of the pipeline. It does not establish that the active predictor is validated by Geofac, or that both systems encode the same structure for general use.

Read this report as:
- evidence that this overlap experiment produced a measurable signal
- motivation for follow-up work on method sensitivity
- an exploratory artifact rather than a final validation statement

## Legacy threshold check

Historical threshold used in this experiment:
- `Jaccard >= 0.20`
- `CI lower bound > 0.10`

Recorded result:
- `Jaccard = 0.3067`
- `CI lower bound = 0.1731`

That threshold was exceeded in this run. In this repository, that means "worth studying further," not "predictor validated."

## Method note

This summary reflects the experiment pipeline committed under `experiments/z5d_geofac_alignment_001/`. Depending on execution environment, that pipeline may use the active CLI or a documented surrogate path for the Z5D-derived side of the comparison. The report should therefore be read as experiment-specific.

## Practical takeaway

The active predictor should still be evaluated primarily through:
- the exact `10^0 ... 10^18` parity grid
- direct unit and integration tests
- benchmark scripts rerun against current code

This report belongs to the exploratory layer above those checks.
