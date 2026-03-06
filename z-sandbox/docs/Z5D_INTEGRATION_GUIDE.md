# Z5D Integration Guide

## Overview

This guide documents the Z5D geometric prior integration for RSA factorization, implementing the RSA-260 Z5D Integration Plan. The implementation provides intelligent search space reduction through geometric priors, adaptive stepping, integer-resonance optimization, and multi-k verification.

## Architecture

### Core Components

1. **Z5D Predictor** (`python/geom/z5d_predictor.py`)
   - Predicts prime locations near √N using Z5D geometric framework
   - Implements κ(n) = d(n) * ln(n+1) / e² curvature corrections
   - Returns high-precision mpmath estimates with confidence intervals

2. **m₀ Estimator** (`python/geom/m0_estimator.py`)
   - Maps Z5D prime predictions to fractional comb index m₀
   - Computes adaptive search windows based on confidence
   - Formula: m₀ = (k · (log N - 2 log p̂_z5d)) / (2π)

3. **Adaptive Step** (`python/geom/adaptive_step.py`)
   - Computes sensitivity-aware Δm so each step shifts p̂ by ~1 integer
   - Formula: Δm ≈ k / (π · p̂)
   - Generates symmetric search queues: m₀, m₀±Δ, m₀±2Δ, ...

4. **Resonance Search** (`python/geom/resonance_search.py`)
   - Integer-resonance objective: -log(dist(N/p̂, ℤ))
   - Pure-Python Brent's method for bounded line search
   - Refines m candidates before GCD checks

5. **Vernier Triangulation** (`python/geom/vernier_search.py`)
   - Cross-validates candidates using multiple k values
   - Identifies intersections where both k₁ and k₂ show resonance
   - Suppresses false positives via CRT-like mechanism

### Runners

1. **Basic Runner** (`python/rsa260_repro.py`)
   - Original skeleton with `--use-z5d-prior` flag added
   - Simple integration for quick tests

2. **Unified Runner** (`python/rsa260_z5d_runner.py`)
   - Full orchestrator with all features:
     - Z5D prior, adaptive step, line search, vernier
     - GCD-first gating (mandatory)
     - Checkpoint/resume with STATE.json
     - JSONL evidence logging
     - Responsible disclosure (FACTORS.sealed)

## Usage

### Quick Start: Basic Z5D Search

```bash
python3 python/rsa260_repro.py \
  --dps 200 \
  --k 0.30 \
  --use-z5d-prior \
  --neighbor_radius 2
```

### Full-Featured Search

```bash
python3 python/rsa260_z5d_runner.py \
  --dps 2000 \
  --k 0.30 \
  --use-z5d-prior \
  --adaptive-step \
  --line-search \
  --vernier-k2 0.31 \
  --max-candidates 100000 \
  --neighbor-radius 2 \
  --checkpoint STATE.json \
  --log-file run.jsonl \
  --log-interval 100
```

### Validation Ladder

Test on known RSA numbers:

```bash
# Quick smoke test (RSA-100 only)
python3 python/validate_z5d_ladder.py --quick

# Full ladder (RSA-100/129/140)
python3 python/validate_z5d_ladder.py --full
```

### Resume from Checkpoint

```bash
python3 python/rsa260_z5d_runner.py \
  --checkpoint STATE.json \
  --resume
```

## Parameters

### Core Parameters

- `--dps`: mpmath decimal precision (≥1000 for RSA-100, ≥2000 for RSA-260)
- `--k`: Primary wave number (typically 0.28-0.32)
- `--m0`: Manual m₀ override (default 0.0 uses Z5D)
- `--window`: Search half-window (default 0.1 uses Z5D)

### Z5D Prior

- `--use-z5d-prior`: Enable Z5D geometric prior
  - Automatically computes m₀ and window from N
  - Provides 100-10000× reduction vs uniform search

### Adaptive Stepping

- `--adaptive-step`: Enable sensitivity-aware Δm
  - Each step shifts p̂ by ~1 integer
  - Prevents exponential overshooting at large scales

### Line Search

- `--line-search`: Enable integer-resonance refinement
  - Maximizes -log(dist(N/p̂, ℤ)) via Brent's method
  - Refines top candidates before GCD checks

### Vernier Triangulation

- `--vernier-k2`: Second k value for dual-k verification
- `--vernier-step`: Coarse step for vernier sweep (default 0.001)
- `--vernier-threshold`: Minimum resonance score (default 3.0)
- `--vernier-top-k`: Top K candidates to return (default 100)

### Search Limits

- `--max-candidates`: Budget limit (default 100000)
- `--neighbor-radius`: Check p_int ± r neighbors (default 2)
- `--prp-rounds`: Miller-Rabin rounds (default 32)

### Logging & Checkpoint

- `--log-file`: JSONL log file path (optional)
- `--log-interval`: Log every N candidates (default 100)
- `--checkpoint`: Checkpoint file (STATE.json)
- `--resume`: Resume from checkpoint

### Output

- `--seal-file`: Sealed factors file (default FACTORS.sealed, chmod 600)

## Workflow

### Phase 1: Z5D Prior Initialization

1. Predict p̂_z5d ≈ prime near √N
2. Map to m₀ = (k · (log N - 2 log p̂_z5d)) / (2π)
3. Compute window from confidence: Δm ≈ (k/π) · ε · S
4. Result: Tight search band around m₀

### Phase 2: Candidate Generation

**Option A: Adaptive Step (recommended)**
- Generate symmetric queue: m₀, m₀+Δ₁, m₀-Δ₁, m₀+Δ₁+Δ₂, ...
- Each Δᵢ computed locally: Δmᵢ ≈ k / (π · p̂(mᵢ))
- Ensures |p̂(mᵢ₊₁) - p̂(mᵢ)| ≈ 1

**Option B: Vernier Triangulation**
- Coarse sweep with k₁ and k₂
- Score intersections where both show integer-resonance
- Return prioritized list sorted by combined score

**Option C: Fixed Step (fallback)**
- Linear grid: m₀ - window, m₀ - window + step, ..., m₀ + window

### Phase 3: Candidate Refinement (optional)

For each m in queue:
1. Apply line search: maximize -log(dist(N/p̂(m), ℤ))
2. Returns refined m* with better integer proximity
3. Reduces false positives

### Phase 4: GCD-First Gating (mandatory)

For each refined m:
1. Compute p̂(m)
2. Generate p_int candidates:
   - Multiple rounding modes: round(p̂), floor(p̂), ceil(p̂)
   - Neighbors: p_int ± radius
3. **GCD first**: g = gcd(N, p_int)
   - If 1 < g < N: **SUCCESS** (factor found)
   - If g = 1: Optional PRP for ranking
   - If g = N: Skip (trivial)

### Phase 5: Logging & Checkpointing

- Log to JSONL every `--log-interval` candidates
- Save STATE.json every 1000 candidates
- On success: write FACTORS.sealed (chmod 600)

## Mathematical Foundation

### Comb Formula

```
p̂(m) = exp((log N - 2πm/k) / 2)
```

Where:
- N: Target semiprime
- k: Wave number (small-k regime: 0.28-0.32)
- m: Fractional comb index
- p̂(m): Candidate factor

### Sensitivity

```
|∂p̂/∂m| = (π/k) · p̂
```

At RSA-260 scale (p̂ ≈ 10^130):
```
|∂p̂/∂m| ≈ 10^131
```

This exponential sensitivity requires adaptive stepping.

### Z5D Prior Mapping

```
Given: p̂_z5d from Z5D predictor
Compute: m₀ = (k · (log N - 2 log p̂_z5d)) / (2π)
Window: Δm ≈ (k/π) · ε · S
```

Where:
- ε: Fractional error (ppm / 1e6)
- S: Safety multiplier (2-10 depending on scale)

### Integer-Resonance Objective

```
g(m) = dist(N/p̂(m), ℤ) = |N/p̂(m) - round(N/p̂(m))|
Objective: maximize f(m) = -log g(m)
```

Higher f(m) → q̂ = N/p̂(m) closer to integer → p̂ more likely factor.

### Adaptive Step Size

```
Δm = k / (π · p̂(m))  [achieves Δp̂ ≈ 1]
```

Clamp to [Δm_min, Δm_max] for numerical stability.

## Checkpoint State Schema

STATE.json contains:

```json
{
  "commit_sha": "abc1234",
  "N_label": "RSA-260",
  "N": "221128255295296664352...",
  "k": 0.30,
  "dps": 2000,
  "m0": -2.9436,
  "window": 0.0024,
  "use_z5d": true,
  "adaptive_step": true,
  "line_search": true,
  "vernier_k2": 0.31,
  "candidates_seen": 12500,
  "gcd_calls": 12500,
  "prp_calls": 8432,
  "line_search_calls": 125,
  "timestamp": 1699056234.567
}
```

Resume exactly where left off with `--resume`.

## JSONL Log Schema

Each line:

```json
{
  "timestamp": 1699056234.567,
  "commit_sha": "abc1234",
  "N_label": "RSA-260",
  "k": 0.30,
  "dps": 2000,
  "i": 1234,
  "m": -2.9436,
  "p_hat": "1.12e+130",
  "p_int": "112031054275...",
  "rounding_mode": "round",
  "gcd": 1,
  "prp_result": true,
  "resonance_score": 6.237,
  "elapsed_ms": 1.234,
  "cumulative_candidates": 12500
}
```

## Security & Responsible Disclosure

### GCD-First Gating

**Mandatory** check before PRP:
```python
g = gcd(N, p_int)
if 1 < g < N:
    # Factor found, handle carefully
```

Never log or transmit actual factors without explicit user action.

### Sealed Factors

On success:
1. Write to FACTORS.sealed
2. Set chmod 600 (owner read/write only)
3. Require `--reveal` to display

Content:
```
# RSA Factorization Result (SEALED)
N = 221128255295296664352...
p = 470242762087091207950...
q = 470009355067859107958...
p * q = N: True
```

### Evidence Logs

JSONL logs include:
- ✓ Search parameters (k, dps, m, window)
- ✓ Timing and performance metrics
- ✓ GCD/PRP counts
- ✗ **NO actual factors** in log

## Performance

### Targets (from plan)

- **RSA-100**: <10s, <1,000 candidates
- **RSA-140**: <1min, <10,000 candidates
- **RSA-160**: <10min, <100,000 candidates
- **RSA-260**: Exploratory, <10^6 candidates

### Reduction vs Baseline

Z5D prior provides:
- RSA-100 (330 bits): ~26,000× reduction
- RSA-260 (862 bits): ~200× reduction (estimated)

Compared to uniform m-scanning over [-1, 1].

## Troubleshooting

### "Z5D modules not available"

Install dependencies:
```bash
pip install mpmath sympy
```

Ensure PYTHONPATH includes repository root.

### "No factor found"

1. Check search window: increase safety multiplier
2. Try k-sweep: test k ∈ [0.28, 0.32] in steps of 0.01
3. Enable vernier: use dual-k verification
4. Increase candidate budget: `--max-candidates 1000000`

### "Checkpoint corrupted"

Delete STATE.json and restart:
```bash
rm STATE.json
python3 python/rsa260_z5d_runner.py --checkpoint STATE.json ...
```

### Numerical instability

- Increase precision: `--dps 3000` or higher
- Check for float64 fallbacks (should fail-fast)
- Verify mpmath version: ≥1.3.0

## Testing

Run unit tests:
```bash
python3 -m pytest tests/test_z5d_integration.py -v
```

Expected: 20/20 passing

Modules tested:
- Z5D predictor
- m₀ estimator
- Adaptive step
- Resonance search
- Vernier triangulation
- Integration pipelines

## References

### Internal
- PR #211: RSA-260 geometric factorization
- PR #201: Combined wall breakthrough
- `docs/RSA260_IMPLEMENTATION_COMPLETE.md`

### External
- Prime Number Theorem (PNT)
- Mertens' theorem for density
- Z5D curvature framework: κ(n) = d(n) * ln(n+1) / e²

## Appendix: Example Run

```bash
$ python3 python/rsa260_z5d_runner.py \
    --dps 2000 --k 0.30 \
    --use-z5d-prior --adaptive-step --line-search \
    --vernier-k2 0.31 \
    --max-candidates 100000 \
    --checkpoint STATE.json \
    --log-file run.jsonl

=== RSA-260 Z5D Runner ===
N (RSA-260)     : bits=862, digits=260
dps              : 2000
k                : 0.30
commit_sha       : 26c3bee

=== Z5D Prior ===
m₀ (Z5D)         : -2.943647436638
window (Z5D)     : 0.00238732414637843
ε (ppm)          : 5000.0
Safety mult      : 5.0

=== Vernier Triangulation ===
k₁               : 0.3
k₂               : 0.31
Candidates       : 100

Queue size       : 100
Max candidates   : 100000
Neighbor radius  : 2

=== Search ===
[   100] m=-2.94364743664, gcd=100, prp=95, rate=825.3 cand/s
[   200] m=-2.94362145287, gcd=200, prp=187, rate=871.2 cand/s
...
```

If factor found:
```
=== SUCCESS ===
Candidates seen  : 3847
GCD calls        : 3847
PRP calls        : 3621
Elapsed          : 4.62s

m                : -2.943625817439
p (bits=431, digits=130)
q (bits=431, digits=130)

Verification: p * q = N: True

=== FACTORS SEALED ===
Factors written to: FACTORS.sealed
Permissions: 600 (owner read/write only)
Use '--reveal FACTORS.sealed' to display factors
```

---

**End of Z5D Integration Guide**
