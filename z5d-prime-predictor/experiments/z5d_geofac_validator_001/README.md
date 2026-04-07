# Z5D as Geofac Cross-Check Experiment

## Overview

This experiment explores whether a Z5D-derived ranking can serve as a useful descriptive cross-check against Geofac resonance scores. It is not an established validator for Geofac, and it is not part of the active nth-prime predictor contract.

## Current committed reading

The committed findings are inconclusive:
- moderate top-K overlap
- high agreement-rate statistics under the current scoring rules
- zero recovered true factors in the small committed test set

That combination does not establish validator utility. At most, it suggests a cross-check pipeline that may warrant more study.

## Use this experiment for

- exploring whether two ranking systems co-vary
- generating calibration or ROC-style descriptive plots
- stress-testing candidate-set scoring ideas

## Do not use this experiment for

- claiming that Z5D already validates Geofac
- claiming false-positive reduction has been established
- inferring new guarantees for the active predictor

## Quick start

```bash
cd tools
python run_experiment.py --test
```

## Output artifacts

- `docs/FINDINGS.md` - committed descriptive summary
- `artifacts/outputs/` - CSV / JSON metrics
- `artifacts/analysis/` - calibration and ROC artifacts

## Recommended interpretation

Treat thresholds in this experiment as exploratory heuristics. If later runs show stronger overlap and actual factor recovery, that would justify a deeper implementation pass. The current committed state does not reach that bar.
