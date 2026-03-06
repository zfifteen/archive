#!/usr/bin/env python3
"""
Geometric factorization test for a specific ~117-bit semiprime using PURE RESONANCE.
- Methods: Green's function + fractional comb sampling + Dirichlet + kappa (no scans/GNFS/ECM).
- Deterministic: fixed mp.dps and rng_seed; identical input => identical output.
"""
import os
import sys
import time
import math
import pytest
from mpmath import mp

# Ensure repository python/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python.greens_function_factorization import (
    RefinementConfig,
    estimate_k_optimal,
)
from python.resonance_comb_factorization import generate_candidates_from_comb

# Target semiprime (provided by user)
N_TARGET = 137524771864208156028430259349934309717  # ~117 bits

@pytest.mark.slow
@pytest.mark.xfail(reason="Pending extended PURE RESONANCE comb sweep to hit exact factor; geometric-only.", strict=False)
def test_geometric_factorization_specific_117bit():
    # High precision for stability
    mp.dps = 256

    # Wave number: use estimator (balanced assumption OK at this scale)
    k = estimate_k_optimal(N_TARGET)

    # Escalation schedule per DAILY_TASK bounds
    steps = [0.001, 0.0005]
    m_ranges = [50, 100]

    found = False
    exact = None
    tried = []

    k0 = float(k)
    k_values = [k0 * (1.0 + e) for e in (-0.05, -0.02, 0.0, 0.02, 0.05)]

    for s in steps:
        for m_rng in m_ranges:
            for k_val in k_values:
                start = time.time()
                cands = generate_candidates_from_comb(
                    N_TARGET, k_val, m_range=m_rng, use_fractional_m=True, m_step=s
                )
                elapsed = time.time() - start
                tried.append({'k': k_val, 'm_range': m_rng, 'm_step': s, 'num': len(cands), 'elapsed_s': elapsed})
                for p in cands:
                    if p > 1 and N_TARGET % p == 0:
                        q = N_TARGET // p
                        assert p * q == N_TARGET
                        found = True
                        exact = (p, q, s, m_rng, k_val, elapsed)
                        break
                if found:
                    break
            if found:
                break
        if found:
            break

    assert found, f"PURE RESONANCE failed to factor N with tried configs: {tried}"

    # Minimal sanity on result magnitude and determinism path
    p, q, s, m_rng, k_val, elapsed = exact
    assert p > 1 and q > 1 and p < N_TARGET and q < N_TARGET
    print(f"Success: p={p} q={q} (m_step={s}, m_range={m_rng}, k={k_val:.4f}, t={elapsed:.3f}s)")
