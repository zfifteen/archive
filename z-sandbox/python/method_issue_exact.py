#!/usr/bin/env python3
"""
Direct implementation from the issue - exact code as provided.
This is the method.py that was used to produce the result.
"""
from mpmath import mp, mpf, mpc, log, exp, pi, nint, sqrt
import math

mp.dps = 200

def dirichlet_kernel(theta, J=6):
    s = mpc(0)
    for j in range(-J, J+1):
        s += exp(1j * mpf(j) * theta)
    return s

def bias(k):
    return mpf('0.0')

def resonance_candidates(N, num_samples=801, k_lo=0.25, k_hi=0.45, m_span=180, J=6):
    LN = log(N)
    sqrtN = sqrt(N)
    cands = set()
    phi_inv = (mpf(1) + sqrt(5)) / 2 - 1  # Golden ratio conjugate for [0,1)
    for n in range(num_samples):
        u_n = math.modf(n * phi_inv)[0]  # {n / phi}
        k = mpf(k_lo) + mpf(u_n) * (mpf(k_hi) - mpf(k_lo))
        m0 = nint((k * (LN - 2 * log(sqrtN))) / (2 * pi))
        b = bias(k)
        for dm in range(-m_span, m_span + 1):
            m = m0 + dm
            p_hat = exp((LN - (2 * pi * (m + b)) / k) / 2)
            theta = (LN - 2 * log(p_hat)) * k / 2
            if abs(dirichlet_kernel(theta, J=J)) >= (2 * J + 1) * mpf('0.92'):
                p_int = int(nint(p_hat))
                if p_int > 1:
                    cands.add(p_int)
    return sorted(cands)

def factor_by_geometric_resonance(N_int):
    N = mpf(N_int)
    cands = resonance_candidates(N)
    for p in cands:
        if N_int % p == 0:
            q = N_int // p
            return min(p, q), max(p, q)
    return None

N_int = 137524771864208156028430259349934309717
factors = factor_by_geometric_resonance(N_int)
print(factors[0])
print(factors[1])
