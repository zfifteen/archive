# Balanced Semiprime Factorization Evaluation Results

## Summary

- **Total samples**: 1000
- **Correlation r(θ'(p), θ'(q))**: -0.7346
- **Evaluation type**: Balanced sampling
- **Nmax**: 1,000,000
- **Target count**: 1,000

## Results

| Heuristic | eps | max_candidates | n | partial_rate | partial_CI95 | full_rate | full_CI95 | avg_candidates |
|-----------|-----|----------------|---|--------------|--------------|-----------|-----------|----------------|
| A:band@0.02 | 0.02 | 1000 | 1000 | 0.0120 | (0.007, 0.021) | 0.0120 | (0.007, 0.021) | 4.5 |
| A:band@0.03 | 0.03 | 1000 | 1000 | 0.0180 | (0.011, 0.028) | 0.0180 | (0.011, 0.028) | 6.8 |
| A:band@0.04 | 0.04 | 1000 | 1000 | 0.0230 | (0.015, 0.034) | 0.0220 | (0.015, 0.033) | 9.1 |
| A:band@0.05 | 0.05 | 1000 | 1000 | 0.0280 | (0.019, 0.040) | 0.0280 | (0.019, 0.040) | 11.3 |
| B:dual@0.02 | 0.02 | 1000 | 1000 | 0.0360 | (0.026, 0.049) | 0.0120 | (0.007, 0.021) | 7.0 |
| C:minor@0.02 | 0.02 | 1000 | 1000 | 0.0070 | (0.003, 0.014) | 0.0070 | (0.003, 0.014) | 2.7 |
| B:dual@0.03 | 0.03 | 1000 | 1000 | 0.0580 | (0.045, 0.074) | 0.0180 | (0.011, 0.028) | 10.5 |
| C:minor@0.03 | 0.03 | 1000 | 1000 | 0.0120 | (0.007, 0.021) | 0.0110 | (0.006, 0.020) | 4.1 |
| B:dual@0.04 | 0.04 | 1000 | 1000 | 0.0760 | (0.061, 0.094) | 0.0220 | (0.015, 0.033) | 14.0 |
| C:minor@0.04 | 0.04 | 1000 | 1000 | 0.0130 | (0.008, 0.022) | 0.0130 | (0.008, 0.022) | 5.5 |
| B:dual@0.05 | 0.05 | 1000 | 1000 | 0.1000 | (0.083, 0.120) | 0.0280 | (0.019, 0.040) | 17.5 |
| C:minor@0.05 | 0.05 | 1000 | 1000 | 0.0180 | (0.011, 0.028) | 0.0180 | (0.011, 0.028) | 6.8 |

## Interpretation

- **partial_rate**: Practical factorization rate (recovering either p or q)
- **full_rate**: Complete factor recovery rate (both p and q)
- **avg_candidates**: Average number of candidates tested per sample
- **Wilson CI95**: 95% confidence intervals using Wilson score method

The partial_rate is the key metric since recovering one factor p allows immediate calculation of q = N/p followed by primality verification.
