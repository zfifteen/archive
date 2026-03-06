# Gemini Reproduction Attempts — PR #224 (127‑bit Geometric Resonance)

**Date:** 2025-11-07 02:08:25

## Purpose
Record exactly what was attempted with **Gemini** to reproduce the PR #224 127‑bit pure‑resonance factorization and the outcomes. Conclusion: **not reproduced**; efforts with Gemini are stopped.

## Context
- Target: 127‑bit geometric‑resonance factorization (PR #224).
- Modulus: `N = 137524771864208156028430259349934309717`.
- Expected factors: `p = 10508623501177419659`, `q = 13086849276577416863`.
- Pure‑resonance constraints:
  - All math in `mpmath` (`mp.mpf/mp.mpc`), `mp.dps = 200`.
  - Golden‑ratio sweep for `k ∈ [0.25, 0.45]` (or tighter when specified).
  - Dirichlet gate with order `J` and threshold on `|(2J+1)·threshold|`.
  - Integer snap **before** phase computation; phase `θ` computed from `p_int` (to avoid the `θ=πm` tautology).
  - **No** Pollard/ECM/NFS; `%` only on final integer candidates.

---

## Attempt Log

### Attempt 1 — Baseline runner (initial)
- **Action:** Ran `reproduce_127bit.py` (original baseline).
- **Issue discovered:** Phase `θ` was computed from `p_hat` (continuous), which enforces `θ=π(m+bias)` and degenerates the gate.
- **Outcome:** Not reproduced.

### Attempt 2 — Minor bugfix
- **Action:** Fixed a minor typo (`mp.mp.dps` → `mp.dps`).
- **Outcome:** Not reproduced.

### Attempt 3 — Stability + Corrected gating
- **Changes applied:**
  - Replaced summation kernel with **closed‑form Dirichlet**: `D_J(θ) = sin((J+1/2)θ)/sin(θ/2)` with a small‑angle limit.
  - **Moved integer snap before the gate** and computed `θ` from `p_int` (breaking the tautology).
- **Command:** `python3 reproduce_127bit.py`
- **Outcome:** Not reproduced.

### Attempt 4 — Stricter phase gate
- **Command:**  
  ```bash
  python3 reproduce_127bit.py --k-lo 0.28 --k-hi 0.36 --J 8 --threshold 0.94
  ```
- **Outcome:** Not reproduced.

### Attempt 5 — Code minimization
- **Action:** Removed non‑essential lines/print/debug clutter to isolate logic; kept all pure‑resonance components intact.
- **Outcome:** Not reproduced.

---

## Final Artifact Bundle (from Attempt 4)

**config.json**
```json
{
  "dps": 200,
  "J": 8,
  "k_lo": 0.28,
  "k_hi": 0.36,
  "num_samples": 801,
  "m_span": 180,
  "threshold": 0.94
}
```

**metrics.json**
```json
{
  "scanned_combinations": 289161,
  "accepted_gate_logged": 50,
  "unique_candidates": 73388,
  "elapsed_seconds": 14.619379997253418,
  "mp_dps": 200,
  "J": 8,
  "k_lo": 0.28,
  "k_hi": 0.36,
  "num_samples": 801,
  "m_span": 180,
  "threshold_multiplier": 0.94
}
```

**run.log** (first 10 entries)
```
# First up-to-50 accepted entries: n, k, m, theta_from_pint, |D_J|, p_hat, p_int
0  0.280000000000000027    -180    -565.486677646162783    17.0    1.47324535066932360212976e+896
  1473245350669323602129759172660577842052302992739005660873624617100070543755867957273133096600994694297248100269994132137825053491621009510041930415448749888670446255789099926114106143004
  2572544793785218475633791499233203365342586929225731269897552329873899909754968059312787465043313080655737201643554381387617101609028673839967813630576688250081552569550636893966230411416
  1682649319554703518812424485214438938524915998327452303810501173162174895286021039163800413573099169770188263177114263651646234769814927728213162913828354229350774935311688789167515366877
  5550346940824649949692824237511665888741606891052498933175298797922629073947957897115697283879786514097072410760700160281247019111985043627941489005998436355020108191935133121070211336145
  97621602006173560028176255527239116068933865950438242781451419274533838787370756190943635548429896006524200455482688580388663093439062467745901707264
3 0  0.280000000000000027    -178    -559.203492338983196    17.0    2.64685222198878595815491e+886
  2646852221988785958154906868320788680018697861851883372849253547489573477287748835769319553747651174816547530329429683628657067212377423408302983260461384771168182207725441388541391656046
  3770857579809785618068735090626857443390281273912044228074865864991797920850607274255320355077606538982492278156287502020027357550418974743687197485986747400545920858210408463444826064228
  6622365549840481253105307145591013821800141647108513006443289183172744824835270439351926111315677830463121853849151308079983439208079242922251374956990637649444044846457535199302701124203
  2983753724391060316151688461862849538273634544303383551159531469094936161929089725331606656339059232444689869480657415837906582469703416980571763809037191060708250046844519719017557979208
  2136749149933968919181802606475332590700417608980950237727320174351429090114451091892632100216855169604791804219267221566284636288828047360
```
*(The remaining entries and `candidates.txt` list ~73k unique post‑gate candidates.)*

---

## Observations
- After fixing the phase tautology and using the closed‑form Dirichlet kernel, the gate **remains highly permissive** across the scanned `m` window, yielding ~73k unique `p_int`.
- No candidate in the accepted set divides `N` under the pure‑resonance constraints.
- The very large `p_hat` values in the log reflect the raw continuous estimate; candidates are gated using `p_int` (snapped), so the magnitude of `p_hat` is not itself the failure cause.

## Conclusion
Despite corrective changes and stricter gating, **Gemini failed to reproduce the factorization**. We are ceasing attempts with Gemini.

## Notes on Likely Causes (for post‑mortem only)
- Potential divergence from PR‑specific nuances (e.g., subtle **phase‑bias correction**, **comb centering**, or **Dirichlet sharpening** parameters) not captured in the simplified runner.
- Environment differences (e.g., transcendental function implementations/rounding) could alter the exact acceptance set near gate thresholds.
- The pure‑resonance gate as parameterized here may still be insufficiently selective without PR‑specific refinements.

## Handoff (if non‑Gemini follow‑up is desired)
- Use the repo’s exact function set and constants (e.g., `fine_bias_log`, any `phase_bias_correction`, `quadratic crest interpolation`) from PR #224’s implementation.
- Add a lightweight **distance‑to‑√N** filter (log‑distance band) while keeping gate logic intact, to reduce false candidates prior to divisibility checks.
- Persist `k, m, θ, |D_J|` for **all** accepted candidates to enable deterministic replay of specific acceptance regions.
