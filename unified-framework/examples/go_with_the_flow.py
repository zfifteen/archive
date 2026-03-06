#!/usr/bin/env python3
# ======================================================================
# One-step Newton inversion of R(x) to estimate p_n at n = 10^k (k = 1…18)
# ======================================================================
# What this script does (self-documenting overview)
# - Computes a single Newton update x₁ = x₀ − (R(x₀) − n)/R′(x₀) to estimate the n-th prime p_n.
# - Evaluates ONLY n = 10^k for k = 1…18.
# - Verifies estimates against hardcoded ground truths p_{10^k} embedded below (no network, no files).
# - Produces a Markdown table with: log10(n), n, estimate, runtime_ms, error_ppm, rel_err_%.
#   Each value is the median of 5 runs to stabilize timing and estimate variability.
#
# Number-theoretic model
# - Riemann R function expansion:
#     R(x)  = Σ_{k≥1} μ(k)/k · li(x^{1/k})
#     R′(x) = (1/log x) · Σ_{k≥1} μ(k)/k · x^{1/k−1}
# - Seed (Panaitopol/Dusart-style):
#     x₀ = n · (L + log L − 1 + (log L − 2)/L), with L = log n
#
# Implementation notes
# - Precision: mpmath with 60 decimal digits (mp.mp.dps = 60).
# - μ(k) (Möbius) is memoized; trial-division is sufficient for k ≤ 20 used here.
# - Series truncation: automatic via a simple tail proxy; loop capped at k ≤ 20.
# - Deterministic, file-local, and benchmark-focused; no sieving, no refits, no I/O.
#
# Ground truth scope
# - The dictionary KNOWN below contains exact p_{10^k} for k = 1…18
#   (values sourced from the referenced gist and standard tables).
#
# How to run
#   pip install mpmath
#   python this_script.py
#
# Output columns (high precision formatting)
# - error_ppm  = |estimate − truth| / truth · 1e6       (parts per million)
# - rel_err_%  = (estimate − truth) / truth · 100       (signed, percent)
#
# Reproducibility
# - Single code path; all constants are local; no randomness.
# - Median-of-5 repetition reduces timing jitter from OS scheduling.
#
# ======================================================================
# Newton–R inversion of R(x) for p_n
# ----------------------------------
# R(x)  = sum_{k>=1} μ(k)/k * li(x^{1/k})
# R'(x) = (1/log x) * sum_{k>=1} μ(k)/k * x^{1/k - 1}
# Seed  = n*(L + log L - 1 + (L2 - 2)/L),  L = log n, L2 = log L

from functools import lru_cache
import mpmath as mp
import time, statistics as stats
from typing import Tuple

mp.mp.dps = 60

# Ground truth for p_{10^k}, k=1..18
KNOWN = {
    10**1: 29,
    10**2: 541,
    10**3: 7919,
    10**4: 104729,
    10**5: 1299709,
    10**6: 15485863,
    10**7: 179424673,
    10**8: 2038074743,
    10**9: 22801763489,
    10**10: 252097800623,
    10**11: 2760727302517,
    10**12: 29996224275833,
    10**13: 323780508946331,
    10**14: 3475385758524527,
    10**15: 37124508045065437,
    10**16: 394906913903735329,
    10**17: 4185296581467695669,
    10**18: 44211790234832169331,
}

@lru_cache(None)
def mu(k: int) -> int:
    if k == 1:
        return 1
    m, p, cnt = k, 2, 0
    while p*p <= m:
        if m % p == 0:
            cnt += 1
            m //= p
            if m % p == 0:
                return 0
            while m % p == 0:
                m //= p
        p += 1 if p == 2 else 2
    if m > 1:
        cnt += 1
    return -1 if (cnt % 2) else 1

def seed(n: int) -> mp.mpf:
    n_f = mp.mpf(n)
    L = mp.log(n_f); L2 = mp.log(L)
    return n_f * (L + L2 - 1 + (L2 - 2)/L)

def R_and_Rp(x: mp.mpf, n_f: mp.mpf) -> Tuple[mp.mpf, mp.mpf, int]:
    ln_x = mp.log(x)
    S = mp.mpf('0'); Spp = mp.mpf('0')
    last_abs_T = None; last_abs_Tp = None
    eta = mp.mpf(10) ** (-int(0.8 * mp.mp.dps))
    K_eff = 0

    for k in range(1, 21):
        mk = mu(k)/mp.mpf(k)
        x1k = x ** (mp.mpf(1)/k)
        T  = mk * mp.li(x1k)
        Tp = mk * (x ** (mp.mpf(1)/k - 1))
        S += T; Spp += Tp; K_eff = k

        if k >= 2 and Spp != 0:
            aT, aTp = mp.fabs(T), mp.fabs(Tp)
            if (last_abs_T or 0) == 0 or (last_abs_Tp or 0) == 0:
                tail_R, tail_Rp = aT, aTp
            else:
                r  = min(max(aT  / last_abs_T,  mp.mpf('0')), mp.mpf('0.99'))
                rp = min(max(aTp / last_abs_Tp, mp.mpf('0')), mp.mpf('0.99'))
                tail_R  = aT  / (1 - r)
                tail_Rp = aTp  / (1 - rp)

            Rv  = S
            Rpv = Spp / ln_x
            fx  = Rv - n_f
            Ex  = mp.fabs(tail_R / (Rpv if Rpv != 0 else mp.mpf('inf'))) + \
                  mp.fabs((fx * tail_Rp) / ((Rpv**2) if Rpv != 0 else mp.mpf('inf')))
            if Ex / mp.fabs(x) <= eta:
                break
            last_abs_T, last_abs_Tp = aT, aTp
        else:
            last_abs_T, last_abs_Tp = mp.fabs(T), mp.fabs(Tp)

    return S, Spp/ln_x, K_eff

def pn(n: int) -> mp.mpf:
    n_f = mp.mpf(n)
    x0 = seed(n)
    Rv, Rpv, _ = R_and_Rp(x0, n_f)
    if Rpv == 0:
        return x0
    return x0 - (Rv - n_f)/Rpv

def run():
    print("| log10(n) | n | estimate | runtime_ms | error_ppm | rel_err_% |")
    print("|---------:|--:|---------:|-----------:|----------:|----------:|")
    for k in range(1, 19):
        n = 10**k
        _ = pn(n)  # warm-up
        times = []; vals = []
        for _ in range(5):
            t0 = time.perf_counter_ns(); v = pn(n); t1 = time.perf_counter_ns()
            times.append((t1 - t0)/1e6); vals.append(v)
        v = mp.mpf(stats.median(vals)); t_ms = stats.median(times)
        tv = mp.mpf(KNOWN[n])
        rel = (v - tv) / tv
        ppm = float(abs(rel) * 1e6)
        rel_pct = float(rel * 100)
        print(f"| {k} | {n} | {int(mp.nint(v))} | {t_ms:.3f} | {ppm:.6f} | {rel_pct:.12f} |")

if __name__ == "__main__":
    run()
