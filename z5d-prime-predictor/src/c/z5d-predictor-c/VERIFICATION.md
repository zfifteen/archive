# Z5D nth-Prime Predictor - Current Verification Notes

This verification note describes what the repository currently demonstrates. It intentionally separates exact checked claims from empirical or historical claims.

## Verified scope

### Platform
- C build target: macOS on Apple Silicon with Homebrew GMP / MPFR

### Exactness that is currently checked
- `tests/test_known.c` checks exact C outputs from `10^2` through `10^9`
- `tests/test_medium_scale.c` checks exact C outputs at `10^10`, `10^11`, and `10^12`
- `scripts/compare_z5dp_implementations.sh` checks exact C / Python / Java parity on the full shipped grid `10^0 ... 10^18`

### Off-grid behavior that is currently checked
- The predictor computes a calibrated closed-form seed and refines it to a probable prime
- The repo does not claim a general proof that the off-grid result equals the exact nth prime

## Current implementation statement

The active predictor path is:
- exact lookup on the shipped grid
- otherwise closed-form calibrated seed
- then forward probable-prime refinement

It is no longer accurate to describe the current predictor as an active Newton / Riemann-`R(x)` inversion pipeline, even though historical helper code for those ideas remains in the tree.

## Repository-level checks used for this pass

The intended verification commands are:

```bash
python3 -m unittest src/python/z5d_predictor/test_predictor.py
cd src/c/z5d-predictor-c && make test
cd src/java && ./gradlew test
./scripts/compare_z5dp_implementations.sh
```

These checks establish:
- Python unit tests pass
- C exact-value tests pass
- Java tests pass
- Grid parity remains exact across all three implementations

## What this note does not claim

It does not claim:
- proof of nth-prime correctness beyond the shipped grid
- benchmark superiority over exact sieving methods from a single illustrative run
- validation of the broader geometric / geofac experiments as implementation truth for the active predictor

## Committed artifact boundaries

The repository currently ships:
- exact ground-truth values through `10^18`
- cross-language parity tooling
- calibration scripts
- latest big-`n` timing CSVs with `10^20` sample rows for C, Python, and Java

Larger benchmark claims must be re-established by rerunning the scripts; they should not be inferred from documentation alone.
