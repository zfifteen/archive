# Plan: Scale Benchmarks to n = 10^1233

## Objectives
- Extend both `z5d_prime_predictor_gist.py` and `benchmark.py` so benchmark output meaningfully covers indices up to 10^1233 (the ~1236-digit prime predicted in this repo).
- Keep runtime practical by tiering benchmarks (exactly validated vs. predicted-only ranges) and trimming displayed digits for huge values.
- Reuse one source of reference values to avoid divergence between the gist and benchmark suite.

## Constraints & Assumptions
- No network access; must rely on the existing precomputed predictions embedded in the repo.
- `z5d_gist.py` already supports the heavy computation path; the gist version must adjust precision before calling it.
- Very large `n` (≥10^300) cannot be exhaustively validated; we will report them as predicted, with digit counts and leading/trailing slices for human sanity checks.

## File: z5d_prime_predictor_gist.py
1) Precision scaling
   - Add a helper `set_precision_for(n)` that chooses `mp.mp.dps` based on estimated digit-length of `p_n` (use stored prediction length when available; fallback to PNT estimate with a safety margin ~+50 digits).
   - Call this helper inside `predict_prime` before computing, so CLI/benchmarks automatically raise precision for extreme inputs (up to 10^1233).

2) Reference data cleanup
   - Split `KNOWN_PRIMES` into `EXACT_PRIMES` (10^1..10^18) and `PREDICTED_PRIMES` (10^19..10^1233) so validation can distinguish verified vs. predicted entries.
   - Add lightweight helpers: `get_reference(n)` (returns value and label exact/predicted) and `digits_for_reference(n)` (cached string length to avoid repeated str conversions).

3) Benchmark tiers
   - Replace the fixed `benchmark` CLI path (currently only 10^5..10^9) with tiered runs:
     • `validated`: 10^1..10^18 (exact checks & ppm errors).
     • `extreme`: selected exponents [19,20,21,22,23,24,25,26,27,28,29,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900,1233].
   - For `extreme`, run fewer iterations (e.g., 1–2) and print: index label, digit count, median runtime, and first/last 12 digits instead of full integers.

4) CLI ergonomics
   - Extend `main()` to accept `benchmark [--max-exp 1233] [--tier validated|extreme|all]` and `demo --extreme` so users can cap the highest exponent without editing code.
   - Keep `validate` focused on exact primes; add `validate --predicted` to show self-consistency checks (recompute and compare to stored predicted constants, reporting digit match and delta magnitude).

5) Safety & performance
   - Guard `predict_prime` and formatting code against giant `str()` calls by slicing with a helper `format_huge_int(x, width=12)`.
   - Cache seeds/precision decisions where possible; avoid storing full big-int results when only digit counts are needed.

## File: benchmark.py
1) Single source of truth
   - Import reference data (or a thin accessor) from `z5d_prime_predictor_gist.py` to avoid duplicating the giant `KNOWN_PRIMES` map and to reuse digit-count helpers.

2) Scale coverage
   - Expand `run_scale_benchmarks`/`run_extended_range_benchmarks` to use the same exponent list as above, capped by a `max_exp` argument (default 1233).
   - Keep validation section for exact primes (≤10^18) with ppm errors; treat >10^18 as predicted-only and print digit counts + first/last digits.

3) Precision management
   - Before each call to `z5d_predictor_with_dist_level`, set precision proportionally to expected digit length (reuse the helper imported from the gist or replicate minimal logic if import would create cycles).

4) Output hygiene
   - For extreme scales, show: `index label`, `digit count`, `runtime ms`, and `first...last digits` (avoid full integer printouts).
   - Include a summary footer that reports max exponent actually executed and average runtime per tier.

5) CLI affordances
   - Add optional args: `--max-exp`, `--tier validated|extreme|all`, `--iterations N` for quick vs deep runs; default iterations drop to 1 for n ≥10^50.

## Test/Run Plan (post-change)
- `python z5d_prime_predictor_gist.py validate` (exact range)
- `python z5d_prime_predictor_gist.py validate --predicted --max-exp 1233`
- `python z5d_prime_predictor_gist.py benchmark --tier all --max-exp 1233`
- `python benchmark.py --tier all --max-exp 1233` (or similar flags once added)
- Spot-check a single extreme: `python z5d_prime_predictor_gist.py 10**1233` and confirm digit count + prefix/suffix match the stored constant.

