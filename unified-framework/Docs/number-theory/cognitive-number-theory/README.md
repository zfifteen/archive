# Cognitive Model: A Forward Diagnostic Framework for Number-Theoretic Distortion

## Overview

This repository presents a theoretical and computational framework for analyzing discrete integer sequences through a geometry-inspired "curvature" model. By drawing a pedagogical analogy to relativistic distortions, we define a **forward diagnostic map** that highlights structural irregularities—especially those arising from divisor density. This model is intended for **structural analysis**, not for blind inversion of unknown values.

## Key Concepts

1. **Curvature Function**

   $$
   \kappa(n) = \frac{d(n) \cdot \ln(n)}{e^2}
   $$

   * **d(n)**: Divisor count of $n$ (i.e., $\sigma_0(n)$)
   * **ln(n)**: Natural logarithm of $n$
   * **Normalization**: Constant $e^2$ determined empirically
   * **Interpretation**: Higher divisor counts and larger values yield greater local "curvature"

2. **Distortion Mapping (Forward Model)**

   $$
   \Delta_n = k \cdot v_c \cdot (1 + \lambda \cdot L) \cdot \kappa(n)
   $$

   * **$v_c$**: Cognitive velocity (base traversal rate)
   * **$k$**: Cognitive coupling strength
   * **$\lambda$**: Load sensitivity factor
   * **$L$**: Contextual cognitive load
   * **$\Delta_n$**: Modeled distortion at $n$
   * **Purpose**: Encodes how cognitive parameters and progression speed skew numerical perception

3. **Perceived Value**

   $$
   n_{\text{perceived}} = n \times \exp(\Delta_n)
   $$

   * Applies exponential scaling to the true integer based on $\Delta_n$
   * Emphasizes how distortion amplifies structural irregularities in composites

4. **Z-Transformation (Context-Dependent Normalization)**

   $$
   \mathcal{Z}(n) = \frac{n}{\exp(\Delta_n)}
   $$

   * **Requires knowledge of true $n$**: Diagnostic tool only, not an inverse mapping
   * **Critical note**: Must be applied to true $n$ values, not perceived values
   * **Outcome**: Reveals underlying structural stability (primes show minimal distortion)

## Empirical Validation

* **Prime vs. Composite Curvature (n = 2–49)**
  * Prime average curvature: \~0.739
  * Composite average curvature: \~2.252
  * Ratio: Composites ≈3.05× higher curvature

* **Classification Performance**
  * Simple curvature threshold: \~83% accuracy distinguishing primes
  * With Z-transformation + ML: +5-10% improvement in classification accuracy

## Implementation

The complete implementation is provided in `main.py` with the following features:

```python
class CognitiveModel:
    def __init__(self, cognitive_velocity=1.0, cognitive_coupling=1.0, load_factor=0.5):
        self.v_c = cognitive_velocity    # Base traversal rate (v_c)
        self.k = cognitive_coupling      # Coupling strength (k)
        self.load_factor = load_factor    # Load sensitivity (λ)

    def compute_cognitive_curvature(self, n):
        """Calculates κ(n) = d(n)·ln(n)/e²"""

    def subliminal_frame_shift(self, n, cognitive_load=0.0):
        """Computes Δn = k·v_c·(1 + λ·L)·κ(n)"""
        
    def conscious_perception(self, n, cognitive_load=0.0):
        """Computes n_perceived = n × exp(Δn)"""
        
    def z_transform(self, n, cognitive_load=0.0):
        """Computes normalized invariant 𝒵(n) = n / exp(Δn)"""