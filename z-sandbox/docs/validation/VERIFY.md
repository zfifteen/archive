# VERIFY — PR #224 (127-bit Geometric Resonance Reproduction)

This guide verifies the **pure resonance** factorization from PR #224 by reproducing the 127-bit result with a deterministic runner.

---

## What this verifies

- Reproduces the candidate search exactly as specified in PR #224, with a critical correction that removes a phase tautology:
  - Golden-ratio low-discrepancy sweep for **k** in \[0.25, 0.45\]
  - **Dirichlet kernel** gate with **J = 6** and threshold **≥ 0.92 × (2J + 1)**
  - **Integer snap *before* the gate**, and compute θ from **`p_int`** (not `p_hat`)
  - **No** ECM/NFS/Pollard/Rho—only `%` is used to test divisibility of the final candidates
- Confirms the expected factors of  
  \(N = 137524771864208156028430259349934309717\) are  
  \(p = 10508623501177419659\), \(q = 13086849276577416863\)
- Emits an **artifact bundle** (config + metrics + run log + candidate list) to make diffs trivial

---

## Prereqs

```bash
python3 --version   # 3.9+ recommended
python3 -m pip install mpmath
```

---

## How to run

```bash
# Default run: try to reproduce; emit artifacts only if failure
python3 reproduce_127bit.py

# Always emit artifacts (even on success), to aid comparison
python3 reproduce_127bit.py --emit-artifacts
```

**Output on success** (example):
```
Status: SUCCESS — factors found
p = 10508623501177419659 (probable prime: True)
q = 13086849276577416863 (probable prime: True)
Check: p*q == N ? True
Scanned combos: 288,360  |  Accepted (gate):  XXX  |  Unique candidates: YYY
mp.dps=200, J=6, k∈[0.25,0.45], samples=801, m_span=180, threshold=0.92
```

If factors are **not** found, an **artifact bundle** directory (default: `artifacts_127bit/`) is created containing:
- `config.json` — All parameters used (including `mp.dps`)
- `metrics.json` — Counts & timing
- `candidates.txt` — Unique post-gate integer candidates (one per line)
- `run.log` — First 50 accepted entries with `(n, k, m, θ_from_pint, |D_J|, p_hat, p_int)`

---

## Why the gate must be after integer snap

If you compute `θ` from the *continuous* `p_hat` derived from the same phase equation,
you get `θ = π(m + bias)`, so the Dirichlet kernel becomes a constant at even `m` (|D| = 2J+1),
making the gate meaningless and flooding candidates.  
Computing `θ` from `p_int` **breaks this tautology** and makes the resonance test informative.

---

## Troubleshooting

1) **Precision loss** — ensure there are *no* `float(...)` casts; everything stays in `mp`.
2) **Too many candidates** — this usually means θ was computed from `p_hat` instead of `p_int`.
3) **Still failing** — try `--k-lo 0.28 --k-hi 0.36` and/or `--J 8 --threshold 0.94` to tighten the gate; keep `mp.dps=200`.

---

Happy verifying!