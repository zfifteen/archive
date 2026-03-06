# Precision Hardening & Benchmark Scaling (10^1233) — Worklog

## Current state (before changes)
- `z5d_prime_predictor_gist.py`: global `mp.mp.dps = 60`; mixes mp.mpf/int with some float risk; large `KNOWN_PRIMES` includes computed values up to 10^1233.
- `benchmark.py`: imports `z5d_gist.py` (float-based, low precision); claims extend to 10^300/10^1233 but precision is insufficient; prints full ints for huge outputs.
- `z5d_gist.py`: float-based seed/NR + math.log; validated only to ~1e12 realistically.
- Latest commit on main: `54f2b609 Add scaling plan for extending benchmarks to 10^1233`.

## Plan to complete
1) Precision helper
   - Implement `required_dps(n, margin=80, floor=80, cap=2000)` ≈ ceil(log10(n) + log10 log n) + margin.
   - Add `set_precision_for(n)` that bumps `mp.mp.dps` per call and caches last value.
2) High-precision predictor
   - Keep all math in mpmath (no float casts); ensure Stadlmann correction uses mp.log.
   - Add `format_huge_int(x, width=12)` to emit prefix/suffix only.
3) Reference data
   - Split into `EXACT_PRIMES` (10^1..10^18) and `PREDICTED_PRIMES` (10^19..10^1233).
   - Provide helper `get_reference(n)` + `digits_for_reference(n)` to avoid duplication.
4) Benchmark refactor
   - Make benchmark import high-precision helpers (or minimal copy) instead of `z5d_gist.py`.
   - Add CLI flags: `--tier validated|extreme|all`, `--max-exp`, `--iterations`.
   - For extreme tier use exponent list: 19,20,21,22,23,24,25,26,27,28,29,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900,1233.
   - For outputs: show index label, digit count, median runtime, prefix...suffix (12 digits).
5) Validation & stress runs (no timeout limit)
   - `python z5d_prime_predictor_gist.py validate` (exact range).
   - `python z5d_prime_predictor_gist.py validate --predicted --max-exp 1233`.
   - `python z5d_prime_predictor_gist.py benchmark --tier all --max-exp 1233`.
   - `python benchmark.py --tier all --max-exp 1233`.
   - Stability check: run 10^30, 10^100, 10^300, 10^600, 10^900, 10^1233 twice at fixed dps; verify identical digit counts/prefix/suffix.
   - Margin sweep (e.g., margin 60/80/100) for 10^1233 to balance runtime vs stability.
6) Docs
   - Update README and scaling_plan.md to match precision policy, tiers, and flags.
7) Deliverables
   - Code changes committed + summary of runtime/precision findings.

## Notes/commands to resume quickly
- Repo root: `/Users/velocityworks/IdeaProjects/unified-framework`
- Workdir: `gists/z5d_prime_predictor`
- Helpful commands:
  - `python z5d_prime_predictor_gist.py validate`
  - `python z5d_prime_predictor_gist.py benchmark --tier all --max-exp 1233`
  - `python benchmark.py --tier all --max-exp 1233`
- Key files to edit: `z5d_prime_predictor_gist.py`, `benchmark.py`, `README.md`, `scaling_plan.md`.

