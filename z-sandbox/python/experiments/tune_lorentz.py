#!/usr/bin/env python3
"""
Tune Lorentz parameters eta and beta for Z5D predictor on tail primes.
"""

import sys
sys.path.insert(0, 'python')
from z5d_predictor import z5d_predict
import sympy
import numpy as np
import math

def tune_eta_beta(L_true: np.ndarray, L0_pred: np.ndarray, tail_mask: np.ndarray, etas: list, betas: list) -> dict:
    L_t = L_true[tail_mask]
    L0_t = L0_pred[tail_mask]
    best = None
    for beta in betas:
        gamma = 1 + 0.5 * (L0_t / ((math.e**4) + beta * L0_t))**2
        lg = np.log(gamma)
        for eta in etas:
            Lc = L0_t - eta * lg
            err = np.abs(np.exp(Lc) - np.exp(L_t)) / np.exp(L_t)  # relative error
            score = np.mean(err)
            if best is None or score < best[0]:
                best = (score, eta, beta)
    return {"eta": best[1], "beta": best[2], "score": best[0]}

# Generate tail data
primes = list(sympy.primerange(1_000_000, 1_001_000))  # small subset
k_values = [sympy.primepi(p) for p in primes]
L_true = np.log(np.array(primes, dtype=float))
L0_pred = np.array([math.log(z5d_predict(k, eta=0)) for k in k_values])
tail_mask = np.ones(len(primes), dtype=bool)  # all are tail
# Tune
etas = [0.5, 0.75, 1.0, 1.25, 1.5]
betas = [24, 27, 30.34, 33, 36]
params = tune_eta_beta(L_true, L0_pred, tail_mask, etas, betas)
print("Tuned parameters:", params)