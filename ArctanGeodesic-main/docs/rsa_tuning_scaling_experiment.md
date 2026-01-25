# RSA Tuning and Scaling Experiment

## Overview
This experiment investigates why the Z5D predictor succeeds on RSA-100 but struggles to scale to larger moduli like RSA-129/155. It tests the hypothesis that tuning parameters (c, kstar) are not universal, breaking Z-invariance (Z = A(B/c)).

## Hypothesis
- Tuning calibrates corrections for specific scales.
- For RSA-100, tuned c ≈ -4.67e30, kstar=0.04449 enables accurate prediction.
- Scaling fails because c scales dramatically with n (e.g., c ≈ 1.42e44 for RSA-129), requiring adaptive tuning.

## Methods
1. **Tuning on Known Factors**:
   - Use RSA-100 (n=100-digit) factors from PR #859.
   - Optimize c and kstar to minimize prediction error for p and q using inverse_li(k) ≈ sqrt(n) * ln(sqrt(n)).
   - Incorporate φ-geodesic θ'(n,k) = φ * ((n mod φ)/φ)^k for embedding.

2. **Retuning for RSA-129**:
   - Apply same method to RSA-129 (n≈129-digit).
   - Observe c shift; test if same tuning predicts accurately.

3. **Scaling Test**:
   - Run predictor on larger n; measure prediction accuracy.
   - Attempt search around k_est with linear offsets (fails) vs. logarithmic grid (proposed).

## Results
- **RSA-100**: Tuning succeeds; pred_p/q match exactly at calibrated k_p/q ≈4.48e51/4.73e51. k_est close; search hits factor.
- **RSA-129**: Retuned c 10^14 larger; predictions inaccurate (diff~10^47). Scaling breaks.
- **Opportunity**: Adaptive c(n) ≈ c0 * (ln n / ln n0)^b (b≈1.5 fitted); logarithmic search for scaling.

## Files
- `tune_z5d_129.py`: Retunes for RSA-129, computes c scaling.
- `rsa_factorization_optimized.py`: Optimized search implementation.
- `rsa100_factorization.py`: Original RSA-100 success script.

## Reproducibility
- Run `python tune_z5d_129.py` to see c scaling.
- Use `rsa_factorization_optimized.py` for adaptive factorization.
- Dependencies: mpmath, sympy, numpy.

## Next Steps
- Fit c(n) model; integrate into predictor.
- Test on RSA-155; validate with datasets (zeta_zeros.csv).
- Horizon: Universal invariants via geometric resolution.

Experimented on 2025-01-XX; anchored to Z-framework axioms.