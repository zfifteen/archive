## Sampling Protocol (Revised)

To mitigate fixed-N artifacts, we replaced consecutive-gap sampling with fixed log-band windows: Collect gaps from primes in [n0/α, α*n0] (α=2.0). For large windows, use random starting points to generate ~50k gaps per scale (subsampled if needed). This ensures scale-invariant sampling.

## Key Finding: Smooth Transition, Not Sharp Crossover

Contrary to initial findings, there is no sharp phase transition at a specific scale. Instead, the per-gap log-likelihood advantage ε(n) of lognormal over exponential declines monotonically with log n, crossing zero in the range 10^10–10^11. This is invariant across sample sizes N, ruling out artifacts.

| Regime       | ε(n)                  | Interpretation |
|--------------|-----------------------|----------------|
| n < 10^10   | Positive, 0.1–0.8   | Lognormal fits better per-gap (finite-scale structure) |
| n ≈ 10^10–10^11 | Near zero          | Models equally good |
| n > 10^11   | Negative, −0.03 to −0.07 | Exponential fits better per-gap (asymptotic behavior) |

This smooth convergence to exponential aligns with Cramér's conjecture: Gaps become memoryless at large scales, with lognormal providing a finite-n approximation that loses advantage gradually.

## Methodological Contribution

Earlier "crossover scales" (e.g., 10^12) were artifacts of ΔBIC = N * ε(n) - ln(N). By characterizing ε(n) directly, we identified the invariant signal: the continuous function ε(n) → 0.

## Figure: Per-Gap Advantage

![Per-gap log-likelihood advantage ε(n) of lognormal over exponential, showing smooth convergence to Cramér's exponential model. The zero-crossing at 10^10–10^11 is sample-size invariant; previously reported "sharp crossovers" at varying scales reflected the BIC penalty term, not intrinsic structure. Note: 10^5 excluded due to subsampling variance (only ~11k gaps available, causing noisier ε estimate).](epsilon_vs_scale.png)

## Conclusion

This work corrects methodological pitfalls in computational prime gap analysis and provides empirical evidence for gradual convergence to Cramér's model, strengthening the theoretical understanding of prime distributions.