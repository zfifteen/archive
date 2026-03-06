#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

# Data from collapsed ε(n) across N=5k, 50k, 500k
scales = [1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11, 1e12, 1e13]
epsilon = [
    0.26,
    0.84,
    0.54,
    0.34,
    0.24,
    0.06,
    -0.07,
    -0.03,
    -0.03,
]  # Collapsed values, excluding 1e5 anomaly

plt.figure(figsize=(8, 5))
plt.semilogx(scales, epsilon, "o-", markersize=8, label="Per-gap advantage ε(n)")
plt.axhline(0, color="red", linestyle="--", label="ε = 0 (model equivalence)")
plt.xlabel("Scale n")
plt.ylabel("Per-gap advantage ε(n)")
plt.title("Invariant Log-Likelihood Ratio: Lognormal vs Exponential")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("epsilon_vs_scale.png", dpi=150)
plt.close()
print("Plot saved as epsilon_vs_scale.png")
