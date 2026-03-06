# Balanced Semiprime Factorization Evaluation Results

## Summary

- **Total samples**: 1000
- **Correlation r(θ'(p), θ'(q))**: -0.1128
- **Evaluation type**: Balanced sampling
- **Nmax**: 1,000,000
- **Target count**: 1,000

## Results

| Heuristic | eps | max_candidates | n | partial_rate | partial_CI95 | full_rate | full_CI95 | avg_candidates |
|-----------|-----|----------------|---|--------------|--------------|-----------|-----------|----------------|
| A:band@0.02 | 0.02 | 1000 | 1000 | 0.0300 | (0.021, 0.043) | 0.0280 | (0.019, 0.040) | 2.5 |
| A:band@0.03 | 0.03 | 1000 | 1000 | 0.0470 | (0.036, 0.062) | 0.0470 | (0.036, 0.062) | 3.8 |
| A:band@0.04 | 0.04 | 1000 | 1000 | 0.0640 | (0.050, 0.081) | 0.0630 | (0.050, 0.080) | 5.0 |
| A:band@0.05 | 0.05 | 1000 | 1000 | 0.0720 | (0.058, 0.090) | 0.0700 | (0.056, 0.088) | 6.3 |
| B:dual@0.02 | 0.02 | 1000 | 1000 | 0.0450 | (0.034, 0.060) | 0.0280 | (0.019, 0.040) | 3.8 |
| C:minor@0.02 | 0.02 | 1000 | 1000 | 0.0170 | (0.011, 0.027) | 0.0170 | (0.011, 0.027) | 1.5 |
| B:dual@0.03 | 0.03 | 1000 | 1000 | 0.0720 | (0.058, 0.090) | 0.0470 | (0.036, 0.062) | 5.8 |
| C:minor@0.03 | 0.03 | 1000 | 1000 | 0.0270 | (0.019, 0.039) | 0.0250 | (0.017, 0.037) | 2.2 |
| B:dual@0.04 | 0.04 | 1000 | 1000 | 0.1040 | (0.087, 0.124) | 0.0630 | (0.050, 0.080) | 7.8 |
| C:minor@0.04 | 0.04 | 1000 | 1000 | 0.0360 | (0.026, 0.049) | 0.0360 | (0.026, 0.049) | 3.0 |
| B:dual@0.05 | 0.05 | 1000 | 1000 | 0.1270 | (0.108, 0.149) | 0.0700 | (0.056, 0.088) | 9.7 |
| C:minor@0.05 | 0.05 | 1000 | 1000 | 0.0470 | (0.036, 0.062) | 0.0470 | (0.036, 0.062) | 3.8 |

## Interpretation

- **partial_rate**: Practical factorization rate (recovering either p or q)
- **full_rate**: Complete factor recovery rate (both p and q)
- **avg_candidates**: Average number of candidates tested per sample
- **Wilson CI95**: 95% confidence intervals using Wilson score method

The partial_rate is the key metric since recovering one factor p allows immediate calculation of q = N/p followed by primality verification.
