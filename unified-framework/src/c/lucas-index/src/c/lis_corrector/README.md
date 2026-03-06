# LIS Corrector — Proof of Concept

Correct the n‑th prime using a Z5D seed and LIS (Lucas/Fibonacci pre‑filter)
with Miller–Rabin verification.

What it does
- Seeds with Z5D: `p0 = z5d_prime(n, auto)`, providing a principled starting point.
- Uses a simple `π̂(x)` approximation to choose search direction only.
- Scans odd candidates within a bounded window around `p0`, counting:
  - Baseline (wheel‑210 presieve survivors)
  - MR calls (after LIS pre‑filter passes)
- Verifies primality with deterministic 64‑bit Miller–Rabin.
- Stops when the exact n‑th prime is reached; returns `(p_true, mr_calls, baseline)`.

Single metric
- MR‑call reduction vs baseline = `1 − MR_calls / wheel210_candidates`.

Dependencies
- Z5D (libz5d) under `src/c/lib`
- LIS PoC (liblis) under `src/c/lis/lib`
- MPFR/GMP (detected via common Homebrew/Unix locations)

Build
```bash
make -C src/c shared                     # libz5d (if not already built)
make -C src/c/lis                        # liblis
make -C src/c/lis_corrector              # liblis_corrector
```

Notes
- Proof of Concept: 64‑bit scope, PoC defaults; bounded window; not a full enumerator.
- Z5D provides the mathematical foundation for `p0(n)`; LIS accelerates convergence to the exact prime.

