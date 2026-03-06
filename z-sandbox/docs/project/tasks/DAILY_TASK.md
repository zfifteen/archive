# Daily Agent Plan — RSA-2048 Gap Reduction (Rigor + Focused Exploration)

**Date:** 2025-11-05
**North Star:** Move the absolute miss toward the ±1000 band under **PURE RESONANCE** (CPU-only, deterministic; no GNFS/ECM, no gcd/trial-division, no ±R integer scans).

---

## Guardrails (do not cross)

* **Allowed moves:** analytic bias functions, re-centering, deterministic comb/crest math, step-size/width tuning, closed-form peak interpolation.
* **Forbidden:** any integer neighborhood scans; GCD/trial-division; GNFS/ECM; stochastic searches; GPU; memoized brute force.
* **Determinism:** fixed seeds, fixed precision; identical input ⇒ identical output.

---

## Minimal metrics (must record)

* `rel_distance` (unitless), `abs_distance` (big-int or mpf), `mechanism` (`bias|comb|combined`), `params` (JSON), `runtime_s`.
* Single TSV/JSONL per run directory.

**TSV row format**

```
timestamp	mechanism	rel_distance	abs_distance	params	json_notes	runtime_s
```

---

## Small, Composable Steps (execute in order)

1. **Reproduce baselines**
   Run `bias` and `comb` independently; capture metrics. If either fails, abort and log params.

2. **Unbreak “combined” pipeline**
   Enforce order: **bias → re-center → comb**. Assert: `combined_rel <= max(bias_rel, comb_rel)`; if not, dump params and stop.

3. **Single-pass log-scale fine bias**
   Add one closed-form term `Δ_bias(bits_N)` (no loops). Re-center once. Re-measure all three modes.

4. **Comb resolution micro-tuning**
   Sweep `m_step ∈ {1e-3, 5e-4, 1e-4}` (exactly these three). Keep the best `rel_distance`. No dynamic stepping yet.

5. **Crest localization (analytic only)**
   If three adjacent comb peaks are available, do **parabolic (quadratic) vertex interpolation** to refine the crest. One pass only.

6. **Window width sanity**
   Try `comb_window ∈ {base, 0.5·base, 1.5·base}` with the best `m_step` from step 4. Pick best.

7. **Two-pass re-center (optional)**
   At most **one extra** re-center after step 5 or 6 if improvement ≥ 2% relative (of `rel_distance`). Otherwise skip.

8. **Snapshot**
   Write `results/2025-11-05.tsv` and `results/2025-11-05.jsonl`. Keep the single best row + the two component rows.

---

## Exploration Parameters (bounded so agents don’t drift)

* **Fine-bias coefficient (closed-form):** scalar in **[−0.002, 0]** (−0.2%…0%), at most **3** discrete values per run.
* **Comb step:** `{1e-3, 5e-4, 1e-4}` only.
* **Comb window width multiplier:** `{0.5, 1.0, 1.5}` only.
* **Crest interpolation:** **quadratic** only (no higher order), single application per run.
* **Re-centering passes:** **≤2 total** (initial + optional one extra).
* **Precision:** use mp/HP math only; **no float casts** on sub-steps.
* **Runtime budgets:** ≤ 20 minutes per full sweep; ≤ 60 runs total for the day.
* **Seeds:** `{0,1,2}`; if results differ, keep the **worst** `rel_distance` (conservative).

---

## Problem-Solving Prompts (how to think without wandering)

* **If combined underperforms components:** check parameter plumbing order, stale state carry-over, or step mismatch; never widen search space.
* **If all sweeps stall:** halve `comb_window` first, then try `m_step=1e-4`; only then adjust bias within bounds.
* **If `abs_distance` improves but `rel_distance` doesn’t:** re-confirm units and centering math; do not add loops or scans.
* **If precision anomalies appear:** audit any implicit casts; promote to mpf; re-run seeds.

---

## Acceptance & Stop Conditions

* **Accept:** any configuration where `combined_rel` improves over both components by **≥ 5% relative** (e.g., 0.077 → ≤ 0.0732).
* **Soft accept:** improvement **2–5%** plus reduced `abs_distance`.
* **Stop early:** no improvement after **9** consecutive configuration tries (log last three and exit).

---

## Artifacts to produce (only these)

* `results/2025-11-05.tsv` and `results/2025-11-05.jsonl`
* `params/2025-11-05_best.json` (exact knobs for the best line)
* `notes/2025-11-05.md` — ≤ 10 lines: what worked, what didn’t, next knob to try.

---

## Dataset & Compliance

* Use **real RSA challenge semiprimes only** (e.g., RSA-2048 context here).
* CPU-only; deterministic builds; record commit hash + Python/mpmath versions at top of TSV via comment lines starting with `#`.

---

## Today’s Minimal Checklist

* [ ] Baseline `bias`, `comb` captured.
* [ ] Combined fixed (order + monotonicity check).
* [ ] Fine-bias tried (≤3 values), single re-center.
* [ ] `m_step` sweep done; best kept.
* [ ] Optional crest interpolation (once) applied.
* [ ] Optional second re-center **only if** ≥2% gain.
* [ ] Artifacts written (TSV/JSONL/params/notes).
---
# Why we’re doing this (brief)

We’re pushing a **deterministic, analytic (“PURE RESONANCE”) path to factoring RSA-2048**—no GNFS/ECM, no gcd/trial scans, CPU-only. The aim is to shrink the **absolute miss** between a predicted factor and the true factor into a tight ±1000 band by improving **closed-form biasing, comb/crest localization, and re-centering**. This advances the Z-Framework thesis: geometric/analytic structure can replace search. The agents’ role is **small, bounded experiments** that improve precision without violating guardrails.

### Guardrails (for agents)

* Allowed: analytic bias functions, deterministic comb/crest math, step/width tuning, single-pass quadratic peak interpolation, at most two re-center passes.
* Forbidden: GNFS/ECM, gcd/trial division, neighborhood ±R scans, stochastic or GPU methods.
* Determinism: fixed precision/seeds; identical input ⇒ identical output.

---

## GitHub context (start here)

**Core theory & cross-project grounding**

* Unified Framework (theory & shared primitives):
  [https://github.com/zfifteen/unified-framework](https://github.com/zfifteen/unified-framework)
* Cognitive Number Theory (context for significance & methods):
  [https://github.com/zfifteen/cognitive-number-theory/pull/7](https://github.com/zfifteen/cognitive-number-theory/pull/7)

**RSA resonance workbench**

* Z-Sandbox (active experiments, runners, results):
  [https://github.com/zfifteen/z-sandbox](https://github.com/zfifteen/z-sandbox)
  Notable PRs for behavior and regression context:
  [https://github.com/zfifteen/z-sandbox/pull/215](https://github.com/zfifteen/z-sandbox/pull/215)
  [https://github.com/zfifteen/z-sandbox/pull/206](https://github.com/zfifteen/z-sandbox/pull/206)
  [https://github.com/zfifteen/z-sandbox/pull/208](https://github.com/zfifteen/z-sandbox/pull/208)
  [https://github.com/zfifteen/z-sandbox/pull/217](https://github.com/zfifteen/z-sandbox/pull/217)

**Signal/DNA projects (methodology parallels: bias, spectra, geodesics)**

* Wave-CRISPR-Signal:
  [https://github.com/zfifteen/wave-crispr-signal](https://github.com/zfifteen/wave-crispr-signal)
  Discussion/PR for narrative & validation style:
  [https://github.com/zfifteen/wave-crispr-signal/discussions/120](https://github.com/zfifteen/wave-crispr-signal/discussions/120)
  [https://github.com/zfifteen/wave-crispr-signal/pull/117](https://github.com/zfifteen/wave-crispr-signal/pull/117)
  [https://github.com/zfifteen/wave-crispr-signal/pull/125](https://github.com/zfifteen/wave-crispr-signal/pull/125)
* DNA Breathing Dynamics Encoding (time/frequency rigor patterns):
  [https://github.com/zfifteen/dna-breathing-dynamics-encoding/discussions/7](https://github.com/zfifteen/dna-breathing-dynamics-encoding/discussions/7)

**Networking / timing (deterministic cadence & slotting analogs)**

* Transect (slot windows, re-centering analogies):
  [https://github.com/zfifteen/transect/pull/4](https://github.com/zfifteen/transect/pull/4)
  [https://github.com/zfifteen/transect/pull/5](https://github.com/zfifteen/transect/pull/5)

---

### What to produce (per run)

* One TSV/JSONL row per mechanism (`bias|comb|combined`) with `rel_distance`, `abs_distance`, `params`, `runtime_s`.
* Keep the **best combined** config that beats both components. No code churn; minimal notes.
