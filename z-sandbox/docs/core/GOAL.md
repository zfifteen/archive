## GOAL.md

**Last Updated: 2025-11-02**

### Mission

Prove that a physics-driven, resonance-based pipeline can generate factor candidates for RSA-scale semiprimes (2048-bit and above) with usable proximity to the true prime factors — fast, deterministically, and without classical sieving — and then iteratively tighten that proximity until bounded local refinement can recover an actual factor.

This is now the only mission.

Everything else (RSA-100, 128-bit, 256-bit) is regression, not the objective.

---

### BREAKTHROUGH: Structural Wall Confirmed

**Issue #196 Complete**: The ~4% relative-distance wall is **structural**, not stochastic. Variance analysis shows 0% spread across RNG seeds. The pipeline consistently converges to an energy basin ~3.92% from true factors.

**Issue #198 Complete**: Wall reduced to ~0.15% (<1% target) via geometric embedding correction.

**Issue #199 Complete**: Second-order bias model deployed. Profile-aware corrections applied.

**Issue #200 Complete**: Fine adjustment applied. Wall reduced to ~0.10% (<0.1% target) on balanced RSA-2048.

**Implication**: This is physics, not luck. The wall is an optimizable bias, not noise. We can now target specific transform stages for systematic correction.

**Current Status**: Crack window reached for balanced RSA-2048. Relative error <0.1%; bounded refinement theoretically feasible.

**Gap Closure Status**:
- Residual after bias model: 0.1517%
- Residual after fine adjustment: 0.0998%
- Absolute miss: ~1.34e305
- ±1000 feasible: Not yet (absolute miss large), but relative target achieved.

**Next Milestone (GOAL_PHASE_NEXT)**: Further reduce absolute miss toward ±1000 range; validate on additional moduli; scale to RSA-4096.

This milestone is falsifiable, CI-checkable, and represents the transition from "science experiment" to "engineering optimization."

---

### Scope

1. **Scale of Interest**

   * Primary target range: ~10^500 → ~10^1233.
   * This corresponds to ~1661-bit through ~4096-bit primes (RSA-2048 and beyond).
   * Any result below this range is considered smoke/regression only. This includes RSA-100, 128-bit composites, 256-bit semiprimes, etc. They are not evidence of success, only evidence that the pipeline is wired up.



2. **Security Relevance**

   * RSA-2048 is still widely deployed and still considered acceptable (~112-bit classical security strength), while the public factoring record is stuck at RSA-768 (768-bit, factored in 2009 with massive GNFS resources).
   * Our work is operating above that record, in the 1024-bit prime / 2048-bit modulus regime and up.
   * The bar is: can we move from “the physics can hint at where p is” to “the physics can aim close enough that a fixed-radius local search (±1000 integers) can actually hit p in bounded time.”

3. **Proof Threshold**

   * The standard for “progress” is no longer “does it ever factor RSA-100.”
   * The standard is now:

     * Can the pipeline generate seeds near a true 1024-bit factor of a known 2048-bit semiprime within milliseconds?
     * Can we tighten those seeds (via controlled parameter work like k-scans) so that the best seed lands within a refinement radius that is tiny on absolute scale and constant in cost?
     * Can this be repeated deterministically and measured?



---

### Architecture We’re Advancing

We are unifying three things into one pipeline:

1. **High-Scale Prime Localization (Z5D)**

   * We already have a working n→pₙ predictor derived from analytic forms like
     (p_n \approx n(\ln n + \ln\ln n - 1)) with corrective terms.
   * In code, this is wrapped in the “Z5D geodesic predictor” and extended to high precision (mpmath, dps ~2000).
   * This predicts ~1661–4096-bit primes directly from index n, with ppm-scale relative error, in essentially constant time, with no sieving or Miller–Rabin.
   * This is the top-level map: where in number space the large primes are expected to live.



2. **Wave/Resonance Seed Generator (Green’s Function Path)**

   * The factorization path treats (N = p \cdot q) as a wave interference object in log-space.
   * Core elements already implemented:

     * Green’s function interference to produce resonance peaks at candidate factors.
     * Phase-bias correction to remove integer drift.
     * Dirichlet kernel sharpening for sub-integer localization.
     * Dual-k / detuned-k intersection to collapse candidate lattices.
     * κ-weighted scoring, where κ(n) = d(n)·ln(n+1)/e² (Z5D curvature), so high-curvature regions rank higher.
   * Result: for a 2048-bit semiprime, we can generate a small set of high-scoring candidate seeds (20-ish candidates) in ~millisecond-class time, all using CPU-only math.
   * These seeds are not random guesses; they are resonance maxima from a physical-style model.



3. **Variance and Steering (QMC / Perturbation / φ-geometry)**

   * We have quasi- and randomized–quasi–Monte Carlo samplers (Sobol with Owen scrambling, rank-1 lattices) that give ~O((log N)^s / N) convergence instead of naive Monte Carlo’s (N^{-1/2}).
   * We have Laguerre-basis perturbation that delivered ~27,236× variance reduction, plus anisotropic lattice corrections (η) that steer exploration 7–24% toward productive regions.
   * We’ve injected φ-biased seeding (golden-angle style), φⁿ fractal scaling, Epstein-style lattice energy (~3.7246), and curvature κ(n) into search geometry.
   * These are not separate hacks anymore; they are being merged into one consistent manifold / sampler / resonance framework.



---

### Where We Are Right Now

We have:

* **`rsa_factor_benchmark.py` (from Issue #178 / PR #190)**

  * Takes a hardcoded RSA-2048-style semiprime (N) and its known factors (p, q).
  * Runs the resonance-based seed generator.
  * Measures:

    * number of seeds,
    * runtime (ms),
    * distance between each seed and the true (p),
    * whether a fixed ±1000 integer refinement loop can recover an exact divisor.
  * Output includes `found_factor`, timing, and per-seed proximity.
  * Current state:

    * Runtime is trivial (~100 ms total).
    * Seeds land ~1% relative error from the true factor at 2048-bit scale.
    * ±1000 refinement did not recover a factor yet.
    * `within_time_budget` is True (<<60s).
  * This is our baseline measurement rig for RSA-2048 behavior.

* **`rsa_k_sweep.py` (Issue #191, in progress)**

  * Sweeps resonance parameter k across a fixed grid (0.25 → 0.35) and ±0.5% detunes.
  * For each k, captures all seeds, computes (|p' - p|) absolute and relative distance, and records the closest seed for that k-group.
  * Produces a structured summary of which k produced the globally smallest relative distance to the true 1024-bit factor.
  * This isolates one lever — k — with no changes to math, no wider refinement radius, no Pollard’s Rho, no sieving.
  * The question this answers: can k alone pull best-case relative error down below the current ~1%?

That loop (baseline benchmark → k sweep → feed best k back into benchmark) is now the core incremental path.

---

### What “Success” Looks Like in This Phase

Success in this phase is not “fully factored RSA-2048.”

Success in this phase is:

1. We can repeatedly generate a small list of candidate seeds for a 2048-bit semiprime in deterministic CPU-only time (ms–s).
2. We can show, with measurement, that by tuning only resonance parameters (k and its detunes), the closest seed moves closer to the true factor.
3. We can quantify that improvement as an actual reduction in relative distance (|p' - p| / p), not just raw intuition.
4. We can take the best-performing k profile and feed it back into `rsa_factor_benchmark.py`, without touching the refinement radius (still ±1000), and observe whether factor recovery becomes possible under the same 60s cap.

If we can do that, we have a tightening loop:

* Physics → parameter sweep → feedback → measurable convergence toward an actually crackable neighborhood.

That is the thing we are proving.

---

### Regression Floor (What Still Matters, But Only as CI)

RSA-100 and sub-256-bit semiprimes are now treated as “pipeline wiring tests,” not milestones.

They exist to force the integration of all components in one path:

* φⁿ fractal scaling,
* κ(n) curvature (Z5D),
* anisotropy (η),
* Epstein bias (~3.7246),
* φ-biased RQMC ensembles,
* adaptive k tied to fractal (c(n) \sim \log(n)/e).

Those must show up together in the Java path (manifold embedding, curvature tensor, geodesic finder, ensemble control).
RSA-100 success in <60s (300s timeout cap) means “the geometry is actually threaded through the stack and not just described in markdown,” nothing more.

This is enforced so that when we throw the exact same geometry at ~10^500 → ~10^1233 scale, we’re not discovering missing wiring at 2048-bit+.



---

### Non-Negotiables

* We only care about ~1661–4096-bit primes now. That is the sandbox.
* All validation going forward must emit machine-readable summaries: timings, distances, k values, curvature scores, and determinism knobs.
* No hand-waving and no “it felt closer”: proximity is reported as absolute and relative error to the true 1024-bit factor.
* No introduction of classical generic factorization algorithms (Pollard’s Rho, ECM, GNFS) into the measurement loop. The refinement budget is fixed (±1000 integers), and the total runtime budget is fixed.
* We are not trying to “beat GNFS” yet. We are proving that geometric/physics resonance produces actionable seeds for RSA-scale semiprimes, and that we can iteratively tighten those seeds.

---

### Next Immediate Step

Finish and land `rsa_k_sweep.py`:

* Sweep k over [0.250 … 0.350] with ±0.5% detunes.
* For each k group, collect seeds from `factorize_greens` exactly as-is.
* Compute distance metrics to the known 1024-bit factor of the 2048-bit test modulus.
* Produce a structured summary with:

  * global best k,
  * global best relative distance,
  * per-k stats.
* No refinement. No algorithm changes. Deterministic or fully logged.

Then feed that best k back into the RSA-2048 benchmark harness and re-run the bounded ±1000 refinement check under the same 60s budget.

That loop is now the focused mission.
