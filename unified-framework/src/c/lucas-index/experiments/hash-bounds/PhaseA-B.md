# LIS Micro‑Efficiency Validation — Phase A/B Plan (PoC)

## Objectives
- Quantify whether LIS (Lucas/Fibonacci pre‑filter) delivers consistent MR‑call reduction vs a realistic baseline (wheel‑210) across index ranges used in hash‑bounds.
- Keep a single primary endpoint and a clear, reproducible protocol.

## Primary Endpoint
- MR‑call reduction vs baseline = `1 − (MR_calls / wheel210_candidates)`
- Report per‑band mean with 95% CI; success if CI lower bound > 0.

## Stratification & Sampling
- Five log‑spaced bands of prime indices `n`:
  - Small: `10^3–10^4`
  - Medium‑1: `10^4–10^5`
  - Medium‑2: `10^5–10^6`
  - Large‑1: `10^6–10^7`
  - Large‑2: `10^7–10^8`
- Phase A: ≥10,000 sampled `n` per band (≥50k total).
- Phase B: 50,000–100,000 `n` per band (250k–500k total) for tighter CIs.

## Truth & Baseline
- Truth (exact `p(n)`): LIS Corrector (Z5D seed → LIS + deterministic 64‑bit MR).
- Baseline: wheel‑210 presieve candidates; do not change baseline.

## Protocol
- For each sampled `n` in a band:
  1) Seed `p0 = z5d_prime(n, auto)` (C Z5D lib).
  2) Correct to exact `p(n)` within a bounded window using wheel‑210 → LIS → MR.
  3) Record `baseline_wheel210`, `mr_calls`, and compute `reduction`.
- Operational controls:
  - Fixed window (e.g., 100k). Log and count window‑exceed cases.
  - Fixed LIS batch size (e.g., 8k) for stable throughput logging.

## Analysis
- Per band: mean reduction and 95% CI (bootstrap, 5k resamples).
- One‑sided test H0: mean reduction ≤ 0 at α=0.01.
- Across bands: report stability (std/median of per‑band means). Optional: trend vs `log10(n)`.

## Reporting
- Per band (table): `n`‑band, samples, mean reduction (%), 95% CI, throughput, window‑exceed rate.
- One‑line headline: pooled reduction `%` with 95% CI.
- Artifacts: JSONL/CSV per run + summary CSV.

## Commands (examples)
- Build (once): `make -C src/c shared && make -C src/c/lis && make -C src/c/lis_corrector`
- Runner with LIS‑correct truth: `python3 experiments/hash-bounds/hash_bounds.py --start A --stop B --lis-correct --output out.jsonl`
- LIS metric (range): `python3 experiments/hash-bounds/hash_bounds.py --lis-start N1 --lis-end N2`

## Runtime Estimates (laptop)
- Phase A (~50k `n` total): ~16–20 minutes.
- Phase B (250k–500k `n` total): ~1.5–4.0 hours.
- LIS‑only metric (cheap): seconds (1–2 s per 1M integers).

## Acceptance Criteria
- Per‑band 95% CI lower bound > 0 for reduction.
- Pooled reduction > 20% with CI lower bound > 10% (example target).

