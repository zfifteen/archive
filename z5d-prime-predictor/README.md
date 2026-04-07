# Z5D Prime Predictor

Cross-language nth-prime predictor (C / Python / Java) built around a calibrated analytic seed ("closed-form" estimator) plus a short forward refinement search. The repository guarantees exact parity on the shipped 19-point benchmark grid `n = 10^0 ... 10^18`; beyond that grid, behavior is empirical and the off-grid contract is "probable prime near the predicted nth prime," not a proof of nth-prime correctness.

## How it works
- **Exact grid lookup**: for the shipped benchmark indices `10^0 ... 10^18`, each implementation returns the same hard-coded ground-truth prime.
- **Closed-form seed**: for other `n`, the predictor evaluates
  `pnt = n(ln n + ln ln n - 1 + (ln ln n - 2)/ln n)`
  with calibrated `d` and `e` terms using `c = -0.00016667` and `kappa_star = 0.06500`.
- **Forward refinement**: the seed is rounded and refined with `next_prime` / `nextProbablePrime` style logic so the returned off-grid value is a probable prime.

## Scope and guarantees
- The predictor accepts positive integer `n`.
- The repo is exact on the shipped 19 benchmark indices in `data/KNOWN_PRIMES.md`.
- The off-grid path is empirical. It returns a probable prime derived from the calibrated seed, not a proved `p_n`.
- Off-grid outputs are probable primes: GMP and Java use strong probable-prime routines; Python uses `gmpy2.next_prime`.
- The calibration script defaults to fitting coefficients on rows with `n >= 10_000`. That cutoff is a calibration choice, not a predictor input restriction.
- The committed latest big-`n` timing CSVs currently document `n = 10^20` runs across C, Python, and Java. Larger sweeps require rerunning the benchmark scripts.

## Layout
- `src/c/z5d-predictor-c` - MPFR/GMP implementation, CLI, tests, and C-specific docs.
- `src/python/z5d_predictor` - `gmpy2` implementation used for parity checks.
- `src/java/src/main/java/z5d/predictor` - `BigInteger` implementation and CLI entrypoint.
- `scripts/` - parity harness, calibration tooling, and big-`n` benchmark scripts.
- `experiments/` - exploratory research artifacts; these are not the source of truth for the active predictor.
- `whitepaper/` - exploratory/historical writing drafts; current implementation truth lives in the repo docs, not the draft white paper.

## Prerequisites
- **C**: macOS Apple Silicon with Homebrew `mpfr` and `gmp`.
- **Python**: Python 3.10+ with `gmpy2`.
- **Java**: JDK 17+.

## Build
- C all: `./src/c/build_all.sh`
- C predictor only: `cd src/c/z5d-predictor-c && make`
- Python tests: `python3 -m unittest src/python/z5d_predictor/test_predictor.py`
- Java classes/tests: `cd src/java && ./gradlew test`

## Run the predictors
- **C CLI**
  `src/c/z5d-predictor-c/bin/z5d_cli 1000000000`
- **Python**
  ```bash
  PYTHONPATH=src/python python3 - <<'PY'
  from z5d_predictor import predict_nth_prime
  print(predict_nth_prime(10**20).prime)
  PY
  ```
- **Java**
  ```bash
  cd src/java
  ./gradlew -q testClasses
  java -cp build/classes/java/main z5d.predictor.Z5DMain 1000000
  ```

## Compliance / parity harness
Run all three implementations against the 19-case grid:
`./scripts/compare_z5dp_implementations.sh`

Expected result: `19/19 PASS` across C, Python, and Java. CSV and environment metadata are written under `scripts/output/`.

## Big-`n` benchmarking scripts
- C: `./scripts/benchmark_big_n.sh`
- Python: `./scripts/benchmark_big_n_python.sh`
- Java: `./scripts/benchmark_big_n_java.sh`

These scripts are designed for arbitrary-size `n` sweeps. The committed latest CSVs in `scripts/output/` currently show `10^20` sample timings for each implementation.

## Calibration
Calibrate the closed-form coefficients `c` and `kappa_star` against the shipped benchmark grid:

```bash
./scripts/calibrate_de_terms.py --c-bounds -0.01 0.01 --k-bounds 0 0.2 --c-steps 25 --k-steps 25 --refine --compare --filter-below-min
```

Outputs:
- `scripts/output/calibration_errors.csv`
- `scripts/output/calibration_comparison.csv`

## Notes
- The C build is intentionally macOS / Apple Silicon scoped. Python and Java remain more portable, but this repo does not claim equal tuning or support across every platform.
- Some legacy helper code and older documents still mention Riemann-`R(x)` / Newton-based ideas. Those are historical or compatibility artifacts, not the active predictor path described here.
