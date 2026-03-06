# Z5D Filtered Factor Candidate Generator (N-Aware) for Balanced Semiprime Factorization
## Technical Specification v2.4 (Correctness-First)

**Document Type:** High-Level Design Specification  
**Date:** December 28, 2025  
**Scope:** N-aware candidate stream for factor discovery; **sound constraints only** (no false negatives).

---

## 1. Purpose

Define a specialized Z5D-based generator that accepts a semiprime-like integer **N** at initialization and produces **factor candidates** for downstream scoring/verification. The generator’s primary contract is:

> **Soundness:** no enabled filter may reject a true factor `p` **with `p` in the active p-window**.

**Scope condition:** when balanced-mode (windowing) is enabled, “no false negatives” is guaranteed only for candidates within the active window. If the true factor lies outside the configured window, it is out of scope by design.

Outside the active p-window, the generator makes **no completeness guarantees**.

This component is a *candidate source* for downstream ranking (e.g., Geofac resonance). It is not, by itself, a complete factorization algorithm.

---

## 2. Core Concept

The generator is a stateful object that precomputes **necessary arithmetic constraints implied by N** and then emits only candidates that satisfy those constraints.

Key correction vs. v2.0: candidates are generated primarily for **p**. A corresponding **q** is produced only when it is derived from N via divisibility or gcd discovery. Generating p and q “independently” wastes work.

---

## 3. Initialization Behavior

### 3.1 Integer-First Arithmetic (No Floating-Point Requirement)

All required operations can be performed with **exact integers** (GMP `mpz_t`):
- `s = ⌊√N⌋` via integer square root
- modular residues (mod 9, mod 10, mod small primes)
- gcd and modular exponentiation for Jacobi/Legendre tests
- window bounds as integer multiplications/divisions

**MPFR is optional** and should only be used if a later scoring stage truly needs high-precision reals.

### 3.2 Preconditions and Scope Guards

The generator must validate:
- N is an integer > 3
- N is odd
- N is not a perfect square

**Balanced-mode is an explicit precondition** when enabled (see §3.3). If balanced-mode is enabled and the true factors are outside the window, the generator will not find them. This is not a bug; it is scope.

### 3.3 Window Computation (Balanced-Mode)

Let `s = ⌊√N⌋`. Balanced-mode defines a multiplicative window around s:

- Lower window for p: `p ∈ [⌊s / α⌋, s]`
- Upper window is implicit via `q = N/p` when divisibility holds

Where `α ≥ 1` is derived from a **max ratio** constraint:

If you want to target `q/p ≤ R_max`, then set:
- `α = √R_max`

Example:
- `R_max = 1.06` ⇒ `α ≈ 1.029563...`

**Default (recommended):**
- `R_max = 1.20` (less brittle than RSA-100-specific tuning)
- `α = √1.20 ≈ 1.095445...`

### 3.4 Terminal Digit Constraints (mod 10)

Let `tN = N mod 10`. Precompute a set of allowed last digits for p (and implicitly q). This is a cheap necessary condition for odd primes (1,3,7,9) and for factors 5 (if allowed).

Store:
- `allowed_last_digits_p ⊆ {1,3,5,7,9}`

### 3.5 Digital Root Constraints (mod 9)

Let `dN = digital_root(N)` (equivalently `N mod 9`, mapping 0→9). Precompute allowed digital roots for p:

Store:
- `allowed_dr_p ⊆ {1..9}` such that `dr(p) * dr(q) ≡ dr(N) (mod 9)` has at least one feasible partner.

Note: digital root constraints are necessary but weak. They are cheap and safe.

### 3.6 Small Prime Presieve Constraint

Compute:
- `P = ∏_{p ∈ S} p` for small primes set S (default S = {2,3,5,7,11,13,17,19,23})
- `g0 = gcd(N, P)`

If `g0 > 1`, you already have a factor (return it immediately; initialization can short-circuit).

If `g0 == 1`, then **a true factor of N cannot be divisible by any prime in S**. That yields a safe rejection rule:
- reject candidate x if `gcd(x, P) > 1`.

### 3.7 Deterministic Sampling State

If a seed is provided, initialize a deterministic PRNG used only for choosing positions in the window (or for choosing offsets). Seeded runs must be reproducible.

---

## 4. Candidate Generation API

### 4.1 Method Signatures

Provide two explicit APIs to avoid relying on configuration flags for semantics:

- `next_prime_candidate()` → returns a single candidate `x` (probable prime) that satisfies all enabled filters **except** the final `gcd(x,N)` verification step.
  This API **never returns factors**; it returns only prime candidates (or empty/exception on budget exhaustion).
- `next_factor_or_candidate()` → returns either:
  - a non-trivial factor `(p,q)` when discovered via `gcd(x,N)>1`, or
  - a single candidate `x` (probable prime) when no factor is found on that call.

Both APIs must never “invent” q independently; q is returned only when derived exactly as `N / p`.

### 4.2 Generation Process (Single-Candidate Loop for p)

**Attempt budgeting:** each API call must enforce an `attempt_limit_per_call` (default 1000). Optionally, a session-wide `attempt_limit_total` may cap total work across calls. When the per-call limit is exceeded without returning a candidate or factor, the call returns empty or raises, per configuration.

For each attempt:

1. **Position sampling:** sample an integer `x` in the p-window.

   Sampling distribution must be explicit and testable:
   - `uniform`: uniform integer sampling over the window, or
   - `z5d_weighted`: a documented, deterministic weighting function `w(x;N,params)` used to bias draws.

   Under a fixed seed, the sequence of samples must be reproducible.

2. **Odd enforcement:** force odd (skip even).

3. **Terminal digit check (mod 10):** reject if `x mod 10` not allowed.

4. **Digital root check (mod 9):** reject if `dr(x)` not allowed.

5. **Small prime presieve:** if `gcd(N,P)==1`, reject if `gcd(x,P)>1`.

6. **Quadratic character filter (sound):**
   - First compute `g = gcd(x, N)`. If `1 < g < N`, return factor immediately (and derive `q = N / g`).
   - Else (so `g == 1`), ensure `x` is odd and compute Jacobi symbol `(N|x)`.
   - If `(N|x) == -1`, reject `x` (sound: a true factor cannot yield -1; a true factor yields symbol 0).
   - If `(N|x) ∈ {0, +1}`, continue.

   Note: for prime `x`, Jacobi equals Legendre. Placing this step before MR avoids paying primality cost on candidates that are arithmetically incompatible with N.

7. **Primality testing for x:** run MR + Lucas/BPSW (configurable).  
   If composite, reject.

8. **Verification step (cheap and decisive):**
   - Compute `g = gcd(x, N)`. If `g > 1`, return `g` (factor found).  
   - Else reject (x is prime but not a divisor).

This loop produces a stream of **prime** candidates that are also **arithmetically compatible** with N, and it reports real factors when discovered.

### 4.3 Optional Pair Output

If you return pairs, only do so when you have divisibility:
- If `g = gcd(x,N)` yields a non-trivial factor `p = g`, set `q = N / p` and return `(p,q)`.
- Otherwise return only `x` (candidate) or empty.

---

## 5. Filter Ordering Rationale (Corrected)

Recommended order (cheapest → most expensive) while preserving soundness:

1) `mod 10` last-digit constraint  
2) `mod 9` digital root constraint  
3) `gcd(x, P)` small-prime presieve  
4) **Jacobi/Legendre symbol** screen (reject if -1)  
5) MR/Lucas primality test  
6) `gcd(x, N)` decisive verification

The key correction: **Jacobi/Legendre belongs before MR**, because it can reject many candidates without paying primality.

---

## 6. Output Characteristics

### 6.1 Candidate Properties

For emitted prime candidate `x`:
- `x` is within the configured p-window (balanced-mode) or within a configured broader region (non-balanced mode)
- satisfies precomputed congruence constraints (mod 10, mod 9)
- passes small-prime presieve (when applicable)
- satisfies quadratic character constraint: `(N|x) != -1`
- is probable prime under configured primality tests

For returned factor `(p,q)`:
- `p*q == N` exactly (derived), with `1 < p < N`.

### 6.2 Duplicate Prevention

No internal duplicate tracking by default. Caller may deduplicate if desired.

---

## 7. Statistics and Diagnostics

Maintain counters:
- total attempts
- rejections by stage (digit, mod9, smallprime, jacobi, primality, verify_fail)
- factors found
- acceptance rates pre/post primality
- mean attempts per returned prime candidate

Expose via `get_stats()`.

**Recommended per-attempt log (CSV) for experiments:**
`attempt_idx,x,stage_rejected,jacobi_value,is_probable_prime,gcd_value,returned_factor`

`attempt_idx` must be monotonically increasing over the generator’s lifetime (not per-call), so logs from multiple calls can be concatenated without ambiguity.

Where:
- `stage_rejected` ∈ {none,digit,mod9,smallprime,jacobi,primality,verify_fail}
- `jacobi_value` ∈ {-1,0,+1,NA}
- `gcd_value` is 1 unless a factor is discovered.

---

## 8. Configuration Options (Corrected)

### 8.1 Balanced-Mode Parameters
- `R_max` (max allowed q/p). Default 1.20
- `α = √R_max`
- optional `margin_pct` to pad window bounds

### 8.2 Primality Strength

- MR rounds (default 40 for ~4096-bit; adjustable)
- Lucas / BPSW toggle

**Primality oracle is pluggable:** any drop-in probable-prime predicate may be used (e.g., GMP `mpz_probab_prime_p`, a fixed-base MR for bounded bit-sizes, or a BPSW implementation), provided it preserves the “probable prime” semantics. This does not change the generator’s soundness constraints; it only changes false-positive probability and runtime.

### 8.3 Filter Toggles
Each filter can be disabled for experimentation, but **soundness must be maintained**:
- disabling digit/mod9/presieve only increases work (safe)
- disabling jacobi increases work (safe)
- disabling primality changes semantics (unsafe unless caller expects composites)
- disabling gcd verification turns this into a pure candidate stream (safe but not a factor finder)

### 8.4 Seed
Deterministic seed for reproducible sampling.

---

## 9. Error Conditions

- invalid N (non-positive, even, perfect square, too small)
- balanced-mode window empty (misconfiguration)
- attempt budget exceeded (per-call `attempt_limit_per_call` or optional session-wide `attempt_limit_total`)

---

## 10. Integration with Resonance Scoring (Clean Interface)

Typical workflow:
1. init generator with N
2. repeatedly request prime candidates `x`
3. score `x` (resonance)
4. if score passes threshold, run decisive verification `gcd(x,N)` (or let generator do it)
5. stop when factor found or budget exhausted

Generator does not depend on scoring; scoring does not depend on generator internals.

---

## 11. Performance Targets (Realistic)

Targets depend on the relative placement of Jacobi vs MR and on window width.

Minimum measurable targets:
- ≥70% rejection before MR (with digit/mod9/presieve/jacobi enabled)
- MR calls per returned candidate reduced vs naive scanning
- deterministic reproducibility under fixed seed

---

## 12. Summary of Corrections vs v2.0

- Balanced-window is now a **declared precondition** via `R_max` (no RSA-100 magic constants).
- Integer-first design; MPFR is optional.
- Jacobi/Legendre moved **before** MR.
- No independent q generation; q is derived only via divisibility/gcd.
- Added decisive `gcd(x,N)` step and init short-circuit when `gcd(N,P)>1`.
- Clarified “RSA compliance” is **not** a safe filter unless proven necessary for the target dataset.


---

## Appendix A. Concrete Config Layout (1:1 mapping to code)

A minimal configuration record that maps directly to a C struct (or a Python dataclass):

### A.1 Required fields
- `balanced_mode` (bool)
- `R_max` (double, default 1.20)  
- `margin_pct` (double, default 0.0)
- `attempt_limit_per_call` (uint64, default 1000)
- `attempt_limit_total` (uint64, default 0 meaning “no session cap”)
- `seed` (uint64, default 0 meaning “unseeded”; if non-zero, deterministic)
- `sampling_mode` (enum: UNIFORM, Z5D_WEIGHTED)

### A.2 Filter toggles (soundness-safe unless noted)
- `enable_digit_mod10` (bool, default true)
- `enable_mod9` (bool, default true)
- `enable_smallprime_presieve` (bool, default true)
- `enable_jacobi` (bool, default true)
- `enable_primality` (bool, default true) **(changes semantics if false)**
- `enable_verify_gcd` (bool, default true) **(controls factor-return behavior)**

### A.3 Small-prime presieve parameters
- `small_primes_set` (fixed array; default {2,3,5,7,11,13,17,19,23})
- `small_primes_product_P` (mpz, derived at init)

### A.4 Primality oracle configuration
- `prp_backend` (enum: GMP_MR, BPSW, CUSTOM)
- `mr_rounds` (uint32, default 40 for ~4096-bit candidates)
- `enable_lucas` (bool, default true)

### A.5 Derived values (computed at init, not user-set)
**Note:** derived fields are internal/read-only and must not be mutated after initialization.

- `s = floor_sqrt(N)` (mpz)
- `alpha = sqrt(R_max)` (double or rational approximation)
- `p_window_lo, p_window_hi` (mpz)
- `allowed_last_digits_p` (bitset over {1,3,5,7,9})
- `allowed_dr_p` (bitset over {1..9})
- `g0 = gcd(N, P)` (mpz)
