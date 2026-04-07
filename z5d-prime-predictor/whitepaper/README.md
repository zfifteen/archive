# Z5D Prime Predictor White Paper Draft

This directory holds exploratory writing artifacts around the broader Z5D research framing. It is **not** the current implementation specification for the active predictor.

Current implementation truth lives in:
- `/README.md`
- `/src/c/z5d-predictor-c/README.md`
- `/src/c/z5d-predictor-c/SPEC.md`

## Status

- **Document status:** exploratory draft
- **Coverage:** sections 1 and 2 were drafted under an earlier theory-forward framing
- **Use this directory for:** research notes, historical framing, writing experiments, and possible future papers
- **Do not use this directory for:** the current algorithm contract or the repo's exact supported guarantees

## Current interpretation

The shipped codebase currently implements:
- exact lookup on the committed `10^0 ... 10^18` benchmark grid
- otherwise a calibrated closed-form seed
- followed by forward refinement to a probable prime

Broader geometric, geodesic, or Riemann-inspired narratives in this directory should be read as exploratory context unless they are explicitly restated in the active implementation docs.

## Draft structure

The white paper remains organized into section directories, but the existing completed sections should be treated as draft artifacts, not as final technical truth for the current codebase.

## Guidance for future revisions

If this white paper is extended, it should:
- begin from observable repo facts and current implementation behavior
- clearly separate implemented behavior from hypotheses
- avoid presenting exploratory experiments as validation of the active nth-prime predictor
