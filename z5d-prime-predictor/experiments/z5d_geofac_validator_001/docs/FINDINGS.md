# FINDINGS: Z5D / Geofac Exploratory Cross-Check

**Date:** 2025-12-14 21:44:51 UTC  
**Run ID:** `z5d_validator_test_20251214_214450`  
**Status:** inconclusive exploratory result

## Strongest supported finding

This committed test run shows that the two scoring systems produced some measurable overlap, but it did **not** establish Z5D as a useful validator for Geofac. The most important limiting fact is that the run recovered **zero true factors**.

## Summary statistics

- **Semiprimes tested:** 5
- **Average Jaccard index:** 0.176
- **Average agreement rate:** 0.972
- **True factors found:** 0

## Interpretation

- The agreement-rate statistic shows that the current scoring rules often move in the same broad direction on the tested candidate sets.
- The Jaccard value indicates only moderate overlap in top-K rankings.
- Zero recovered true factors means the committed result does not justify claiming practical validator utility.

## Per-run descriptive metrics

Each committed semiprime run reported the same descriptive pattern:
- **Total pairs evaluated:** 501
- **Jaccard index:** 0.176
- **Agreement rate:** 0.972
- **Spearman correlation:** 0.321 (`p = 1.94e-13`)
- **True factors found:** 0

## What this artifact supports

It supports:
- further exploratory work on candidate scoring and sensitivity analysis
- examination of whether the two systems are measuring partially overlapping signals

It does not support:
- "Z5D validates Geofac"
- "false positives are reduced"
- "production tuning is justified"

## Recommended next steps

1. Increase the candidate-set and semiprime coverage.
2. Track actual factor recovery before making utility claims.
3. Test whether the high agreement-rate statistic survives scoring changes.
4. Re-evaluate the ranking overlap thresholds after larger runs.

## References

- Z5D predictor code: `/src/python/z5d_predictor/`
- Shared utilities: `tools/z_shared.py`
- Z5D adapter: `tools/z5d_adapter.py`
- Geofac scorer: `tools/geofac_scorer.py`
- Proposed experimental thresholds: `/docs/VALIDATION_GATES.md`
