# Build Plan for Issue #196: Break the 4% Wall and Prove Path to RSA

**Document Version**: 1.0  
**Date**: November 2, 2025  
**Author**: AI Assistant (based on pre-work clarifications)  
**Confidence**: 10/10 (all uncertainties resolved via user answers)  
**Estimated Timeline**: 5-8 days (assuming 4-6 hours/day; includes testing and iteration)  
**Dependencies**: Existing codebase (e.g., `factorize_greens`, `RefinementConfig`, k-sweep tools); Python 3.x with mpmath/big-int support.  
**Risks Mitigated**: Determinism via unit tests/seeding; parameter exposure via config updates; edges via tagging/metrics; purity via CI assertions.

This build plan outlines the step-by-step process to implement Issue #196, focusing on formalizing the ~4% relative distance "wall," characterizing variance, mapping curvature via sweeps, generalizing across moduli, splitting finisher phases, and enforcing rules with CI. It adheres to the acceptance criteria, ensuring deterministic, physics-sourced progress without classical methods or radius widening. The plan is modular for incremental validation.

I'll execute this plan sequentially, using tools (e.g., Edit for code changes, Bash for runs/tests, TodoWrite for tracking). Progress will be tracked via a todo list, with commits pushed to a feature branch (`feat/break-4pct-wall`).

---

## **High-Level Phases**
1. **Preparation (Days 1-2)**: Setup config extensions, determinism tests, and baseline locking.
2. **Core Implementation (Days 2-4)**: Build variance script, sweeps, generalization harness, and finisher script.
3. **Testing & Validation (Days 4-6)**: Run on diverse moduli, add CI guards, iterate based on results.
4. **Documentation & Closure (Days 6-8)**: Final reports, README updates, PR creation.

## **Detailed Steps**

### **Phase 1: Preparation**
- **Step 1.1: Create Feature Branch**
  - Run: `git checkout -b feat/break-4pct-wall`
  - Purpose: Isolate work; track changes.

- **Step 1.2: Extend RefinementConfig**
  - File: `python/greens_function_factorization.py` (or config module).
  - Changes: Add `rng_seed: int = None` (for randomness control); expose secondary params if needed (e.g., `kappa_weight_scale: float = 1.0`, `phi_bias: float = 1.618`, `dirichlet_window: int = 100`).
  - Validation: Ensure no internals modified; test config overrides don't break `factorize_greens`.

- **Step 1.3: Add Determinism Unit Test**
  - File: `tests/test_greens_function_factorization.py` (new or existing).
  - Code: Run `factorize_greens` twice with fixed `(N, k, config, rng_seed=1337)`; assert outputs identical (serialize to JSON and compare).
  - If fails: Debug and plumb `rng_seed` through subroutines (e.g., QMC samplers).

- **Step 1.4: Lock Baseline Wall**
  - Create: `docs/BASELINE_WALL_4_PERCENT.md`.
  - Content: Record ~4% distance, harness conditions (k-range, detunes, seed=1337, CPU-only).
  - Add CI test: Assert baseline script reports expected ~4% on known N.

### **Phase 2: Core Implementation**
- **Step 2.1: Build Variance Sweep Script**
  - New File: `python/examples/rsa_k_sweep_variance.py`.
  - Logic: Extend k-sweep; repeat for seeds `{1337, 1338, 1339, 1340}`; compute min/median/max rel_distance per k_base.
  - Output: Add stability metrics (spread, 95% CI via bootstrap).
  - Integration: Use extended config with `rng_seed`.

- **Step 2.2: Implement Curvature Mapping Sweeps**
  - New File: `python/examples/rsa_curvature_mapping.py`.
  - Sweeps:
    - Fine k-zoom: Around best k (e.g., 0.245–0.255, step 0.0005).
    - Wider detunes: ±2% in steps (use `DETUNE_PCT_VALUES` constant).
    - Secondary params: Sweep κ-weight/φ-bias/Dirichlet window with fixed k.
  - Guards: Catch NaNs/exceptions; log "unstable".
  - Output: Best rel_distance per knob; identify wall-bending params.

- **Step 2.3: Generalize Harness**
  - Update: `python/examples/rsa_k_sweep.py` (or new `rsa_general_harness.py`).
  - Changes: Accept arbitrary `(N, p_true, q_true)` triples; tag profiles (e.g., "balanced_2048"); log abs/rel to smaller factor.
  - Test on: 1 additional RSA-2048, skewed variant, 256/512-bit from repo.
  - Output: Table of best_rel_distance vs. profile.

- **Step 2.4: Split Finisher Phase**
  - New File: `python/examples/rsa_seed_refine_window.py`.
  - Logic: Take best seed from sweeps; run ±R (1000) divisibility; log R, found_factor, offset.
  - Separation: Explicit `PHASE = "FINISHER_ASSISTED"`; no resonance mixing.

### **Phase 3: Testing & Validation**
- **Step 3.1: Run & Iterate**
  - Execute scripts on test moduli; log results to `results/wall_break_YYYYMMDD.txt`.
  - Analyze: Compute shrink ratios; check if wall bends (e.g., <4% on some knobs/moduli).
  - Iterate: If variance high, refine seeding; if no bending, log for future phases.

- **Step 3.2: Add CI Guards**
  - Files: Update `tests/` with phase assertions (e.g., `assert config.allow_local_refine == False` for pure).
  - CI: Add job checking phase strings/config flags; fail on bleed (e.g., refinement in pure script).

- **Step 3.3: Edge Case Testing**
  - Run on unbalanced/pathological moduli; verify metrics/tagging handle skew without crashes.

### **Phase 4: Documentation & Closure**
- **Step 4.1: Update Docs**
  - Files: `docs/ROADMAP.md` (add wall analysis); READMEs for new scripts (phases, usage, metrics).
  - Content: Distinguish phases; include table of results vs. moduli.

- **Step 4.2: Final Validation & PR**
  - Confirm: All criteria met (baseline locked, variance quantified, wall bent/generalized, finisher separated, CI enforced).
  - Create PR: From `feat/break-4pct-wall` to main; include findings summary.
  - If success: Proceed to RSA-4096 eval; else, pivot to next knob (e.g., new physics models).

## **Todo Tracking**
I'll use TodoWrite to track progress. Initial todos:
- Create branch and config extensions.
- Add determinism test.
- Build variance script.
- Etc. (detailed in phases).

## **Execution Notes**
- **Branch**: `feat/break-4pct-wall`.
- **Commits**: Granular (e.g., "Add variance script" per step) with descriptive messages.
- **Tools**: Use Edit for code, Bash for runs/tests, Grep/Glob for inspections.
- **Validation Runs**: Pilot each script early; log outputs for reproducibility.
- **Fallback**: If issues (e.g., unexposed params), pause and query for clarification.

This plan is executable and aligned with your answers—starting implementation now. First step: Create branch.