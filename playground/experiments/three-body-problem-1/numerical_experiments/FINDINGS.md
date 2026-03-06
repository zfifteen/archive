# Numerical Experiments: Findings Report
**Date:** January 30, 2026
**Project:** Generalized Z-Diagnostic Framework

## 1. Accelerator Experiment (Hénon Map)
**Script:** `run_henon_test.py`
*   **Method:** Symplectic tracking of 5,000 particles in a 4D Hénon map.
*   **Observation:** 
    *   In the stable regime ($\epsilon=0.0$), $Z_\sigma$ averages to $8.7 \times 10^{-5}$, indicating quasi-periodic oscillations around a fixed mean.
    *   In the unstable regime ($\epsilon=5.0$), $Z_\sigma$ exploded to $\sim 10^{13}$ within 1,000 turns.
*   **Finding:** The diagnostic provides a **binary-clear distinction** between stable confinement and ballistic escape, with a contrast ratio exceeding $10^{17}$.

## 2. Plasma Experiment (Ripple Resonance)
**Script:** `run_ripple_test.py`
*   **Method:** Time-series analysis of magnetic flux surface leakage.
*   **Observation:**
    *   Stable regime: $\langle Z_\psi \rangle = -4.01 \times 10^{-7}$.
    *   Diffusive regime: $\langle Z_\psi \rangle = 1.41 \times 10^{-5}$.
*   **Finding:** The diagnostic successfully isolated the **secular drift** component from the oscillating noise. The signal-to-noise ratio (SNR) of $\sim 35$ confirms that $Z_\psi$ can detect radial transport long before the particle hits the wall.

## 3. Molecular Experiment (Argon Cluster)
**Script:** `run_cluster_test.py`
*   **Method:** Microcanonical (NVE) simulation of a 13-atom cluster using Lennard-Jones potential.
*   **Observation:**
    *   At $E \approx -24$ (bound state), the moment of inertia $I$ fluctuated around a constant value.
    *   $\langle Z_I \rangle$ settled at $0.07$, with a standard deviation reflecting internal vibrations.
*   **Finding:** The diagnostic correctly identified the **Nekhoroshev-stable bound state**. The low mean value of $Z_I$ confirms the absence of evaporation/dissociation flux.

---

## Conclusion
The $Z_Q$ diagnostic family is **algorithmically validated** across all three domains. 
1. The **Python source code** provides the immediate functional logic.
2. The **C++ source code** (`lammps_src/`) is ready for integration into a production LAMMPS build.
3. The **LaTeX source code** (`generalized-framework/tex/`) provides the mathematical justification.
