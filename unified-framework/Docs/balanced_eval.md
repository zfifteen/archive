# Balanced Semiprime Factorization Evaluation Results

## Summary

- **Total samples**: 100
- **Correlation r(θ'(p), θ'(q))**: -0.7291
- **Evaluation type**: Balanced sampling
- **Nmax**: 1,000,000
- **Target count**: 1,000

## Results

| Heuristic | eps | max_candidates | n | partial_rate | partial_CI95 | full_rate | full_CI95 | avg_candidates |
|-----------|-----|----------------|---|--------------|--------------|-----------|-----------|----------------|
| A:band@1.0 | 1.0 | 1000 | 100 | 1.0000 | (0.963, 1.000) | 0.6100 | (0.512, 0.700) | 35.7 |
| B:dual@1.0 | 1.0 | 1000 | 100 | 1.0000 | (0.963, 1.000) | 0.6100 | (0.512, 0.700) | 35.7 |
| C:minor@1.0 | 1.0 | 1000 | 100 | 0.0800 | (0.041, 0.150) | 0.0500 | (0.022, 0.112) | 3.2 |

## Interpretation

- **partial_rate**: Practical factorization rate (recovering either p or q)
- **full_rate**: Complete factor recovery rate (both p and q)
- **avg_candidates**: Average number of candidates tested per sample
- **Wilson CI95**: 95% confidence intervals using Wilson score method

The partial_rate is the key metric since recovering one factor p allows immediate calculation of q = N/p followed by primality verification.
