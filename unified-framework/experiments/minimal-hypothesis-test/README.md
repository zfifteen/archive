# Minimal Hypothesis Test

This experiment implements the smallest, decisive check of the claim:

Hypothesis (H1): fractional-part “bounds” around `frac(sqrt(p̂_m))` capture the true `frac(sqrt(p_m))` more often than expected under a random baseline of independent uniforms.

Null (H0): observed coverage equals the random baseline expectation given the same per-sample widths.

Test procedure
- Input: JSONL file produced by earlier runs (default `hash_bounds_results.txt` at repo root). Each line must include `bound_width`, `within_bounds`, `frac_true`.
- Statistic: Let hits be the number of `within_bounds=True`. Let widths be `w_i`. The random-baseline expected successes is μ = Σ w_i, variance σ² = Σ w_i(1−w_i) (Poisson-binomial). We compute z = (hits − μ)/sqrt(σ²) and a one-sided p-value via the normal tail (conservative for small w_i).
- Decision: Reject H0 at α=0.01 if p < α (evidence of structure). Otherwise fail to reject (no lift beyond random baseline for this dataset).

Usage
- Run: `python run_test.py` (defaults to `../../hash_bounds_results.txt`).
- Options: `--input <path>` to point at a different JSONL; `--alpha 0.01` to change significance.

Notes
- This test neither proves independence nor cryptographic properties; it only checks for measurable lift over a matched-width random baseline.
- Keep the dataset generation separate (e.g., from `experiments/hash-bounds/`). This folder contains only the minimal verifier and docs.
