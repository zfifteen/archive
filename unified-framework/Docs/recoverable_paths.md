# Recoverable Paths

## Balanced Navigation

### Definition:
Factorization success is measured via `partial_rate` — the fraction of semiprimes N = pq where at least one factor p or q is present in the candidate list.

- Once one factor is found, compute q = N/p and confirm primality (`isprime(q)`).
- `full_rate` (both factors present) is recorded but diagnostic only, relevant for symmetry in balanced cases.

### Observed Results (PR #740, Nmax=10^6, n=200, heuristic A):

| ε | partial_rate | CI95 | full_rate | CI95 | avg_candidates |
|---|---|---|---|---|---|
| 0.02 | 0.015 | [0.005, 0.043] | 0.015 | [0.005, 0.043] | 4.6 |
| 0.03 | 0.015 | [0.005, 0.043] | 0.015 | [0.005, 0.043] | 6.7 |
| 0.04 | 0.015 | [0.005, 0.043] | 0.015 | [0.005, 0.043] | 9.1 |
| 0.05 | 0.015 | [0.005, 0.043] | 0.015 | [0.005, 0.043] | 11.3 |

### Key Point:
`partial_rate` is the **factorization proxy**; `full_rate` tracks heuristic symmetry but is not needed to factor N.

---

## 🔮 Future Extensions (supported by r ≥ 0.85 hypotheses)

- **3BT triage (PR #481):** Fuse into heuristic C to boost `partial_rate` by +10–15%.
- **Scaling:** Extend to N = 10^7 to test Pearson correlation convergence.
- **ROC analysis:** Implement ROC-style plots (partial_rate vs. avg_candidates) using matplotlib in the evaluation harness.

---

## ✅ Assertions / CI Guards

Add CI regression tests to ensure stability of baseline balanced runs:

- For ε = 0.05 (balanced sampling, heuristic A, Nmax=10^6, n≈200):
  - Assert `partial_rate ∈ [0.01, 0.08]` (sanity bounds).
  - If rate drifts outside, flag regression in CI.

---

## 🧭 Context

This update documents **PR #740** and locks in the **Δn invariance per latest geodesics** as the current baseline for recoverable paths. Enhancements (heuristics B/C, ROC plots, scaling) will proceed in future PRs.