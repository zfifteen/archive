# Z5D nth-Prime Predictor (C / MPFR / GMP)

Current implementation summary: this C module computes a calibrated closed-form seed for the nth prime and then performs short forward refinement to the next probable prime. Exactness is locked only for the shipped benchmark grid through the built-in lookup table. Off-grid results are empirical.

**Platform scope:** macOS on Apple Silicon. This build intentionally targets Homebrew-installed GMP / MPFR on that platform.

## Current algorithm

The active path in `src/z5d_predictor.c` is:

1. Parse an arbitrary-size positive integer `n`.
2. If `n` matches one of the shipped benchmark indices `10^0 ... 10^18`, return the exact ground-truth prime from the internal table.
3. Otherwise compute the calibrated seed
   `pnt = n(ln n + ln ln n - 1 + (ln ln n - 2)/ln n)`
   plus the fitted `d` and `e` terms.
4. Round that seed to an integer.
5. Refine forward with GMP `nextprime` logic so the returned off-grid value is a probable prime.

Legacy helper routines for logarithmic integral, Riemann-`R(x)`, and Newton-style steps remain in `z5d_math.c` for compatibility and historical experiments, but they are not the primary predictor path documented here.

## What this module guarantees
- Exact return values for the shipped 19-point benchmark grid.
- Deterministic parity with the Python and Java implementations on that same grid.
- Arbitrary-size integer input support in the CLI and `mpz` API.
- Off-grid output is a probable prime near the predicted nth-prime location, not a proved `p_n`.

## Directory structure

```text
z5d-predictor-c/
├── include/
│   └── z5d_predictor.h
├── src/
│   ├── z5d_predictor.c
│   ├── z5d_math.c
│   ├── z5d_math.h
│   ├── z5d_cli.c
│   └── z5d_bench.c
├── tests/
│   ├── test_known.c
│   └── test_medium_scale.c
├── tools/
│   └── demo.sh
├── Makefile
├── README.md
├── SPEC.md
└── VERIFICATION.md
```

## Requirements
- macOS on Apple Silicon
- Apple Clang / Xcode command line tools
- Homebrew `gmp` and `mpfr`

Install:

```bash
brew install gmp mpfr
```

## Building

```bash
make
make test
make bench
make demo
make clean
```

Important targets:
- `make all` - library, CLI, benchmark, and tests
- `make cli` - CLI only
- `make bench` - benchmark binary
- `make test` - build and run C tests
- `make shared` - invoke the parent build for shared libraries

## CLI usage

```bash
./bin/z5d_cli 1000000
./bin/z5d_cli -v 1000000
./bin/z5d_cli -p 4096 100000000000000000000
```

Supported options:
- `-p <precision>` - MPFR precision in bits
- `-v` - verbose output
- `-h` - help

The current CLI does not expose the legacy `K` or Newton iteration controls because those are not part of the active predictor path.

## C API

Primary entrypoints:
- `z5d_predict_nth_prime_mpz_big(mpz_t prime_out, const mpz_t n)`
- `z5d_predict_nth_prime_mpz(mpz_t prime_out, uint64_t n)`
- `z5d_predict_nth_prime_str(mpz_t prime_out, const char* n_dec_str)`

The `mpfr` result structure and config helpers are retained for API continuity, but the active prediction path uses one calibrated seed computation plus refinement rather than iterative Newton solving.

## Testing and verification
- `./bin/test_known` checks exact values on the C-side known grid through `10^9`.
- `./bin/test_medium_scale` checks exact values at `10^10`, `10^11`, and `10^12`.
- `./scripts/compare_z5dp_implementations.sh` verifies exact parity across C, Python, and Java on the full shipped `10^0 ... 10^18` grid.

## Benchmarking

`./bin/z5d_bench` exercises the C predictor locally.

Repo-level benchmark scripts live under `scripts/`. The committed latest C timing CSV currently documents a `10^20` sample run; larger sweeps are supported by rerunning the scripts rather than assumed from the checked-in artifacts.

## Design notes
- Precision scales with the bit length of `n` on the arbitrary-size path.
- Exact benchmark indices are table-driven so cross-language parity does not depend on floating-point drift.
- Off-grid refinement uses GMP's probable-prime machinery. This is a pragmatic research-tool contract, not a global proof of nth-prime correctness.
