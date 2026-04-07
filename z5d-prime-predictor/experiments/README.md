# Exploratory Experiments

This directory contains exploratory research artifacts around Z5D-adjacent ideas. These experiments are useful for hypothesis testing and tooling, but they are **not** the source of truth for the active nth-prime predictor contract.

## Current experiments

### `z5d_geofac_validator_001`

- **Status:** exploratory, inconclusive
- **Purpose:** explore whether Z5D-derived scoring and Geofac resonance rankings co-vary on the same candidate sets
- **Current committed result:** moderate overlap, high agreement-rate metrics, zero recovered true factors in the small committed test set
- **Interpretation:** descriptive cross-check only; no established validator utility

### `z5d_geofac_alignment_001`

- **Status:** exploratory artifact
- **Purpose:** measure overlap between a Z5D-derived peak pipeline and Geofac bins under shared QMC seeds
- **Current committed summary:** one run reports `Jaccard = 0.3067` with `95% CI [0.1731, 0.2256]`
- **Interpretation:** descriptive overlap for that pipeline and dataset, not validation of the active nth-prime predictor

### `theta_contour_map_001`

- **Status:** exploratory visualization
- **Purpose:** inspect contour structure around a theory-motivated parameter surface
- **Interpretation:** plotting and calibration support, not predictor verification

## How to read this directory

- Treat thresholds and "gates" in experiment docs as proposed research criteria, not product guarantees.
- Treat committed summaries as descriptive artifacts of the pipelines that produced them.
- If an experiment can run with a surrogate or mock path, results from that path are exploratory and not equivalent evidence for the active predictor implementation.

## Relationship to the active predictor

The active predictor contract is documented in the root README and C implementation docs. Use this directory for questions like:
- what hypotheses were tested
- what exploratory overlap was observed
- what follow-up experiments might be worth running

Do not use this directory alone to infer the exact guarantees of the shipped nth-prime predictor.
