# RSA Tuning Scaling Experiment - Reproduction Notes

## Quick Repro Steps
1. Run tuning for RSA-129: `python tune_z5d_129.py`
   - Output: c ≈ 1.42e44 (vs RSA-100's -4.67e30), confirming non-universal scaling.

2. Check RSA-100 success: `python rsa100_factorization.py`
   - Should factor with tuned params.

3. Test scaling failure: Try on RSA-129 with same params.
   - Predictions inaccurate; need adaptive c(n).

4. Proposed fix: `python rsa_factorization_optimized.py`
   - Implements logarithmic search + adaptive tuning.

## Files
- docs/rsa_tuning_scaling_experiment.md: Full doc in repo.
- tune_z5d_129.py: Retuning script.
- rsa_factorization_optimized.py: Optimized version.

## Horizon
- Fit c(n) model for universal tuning.
- Test on larger RSA.