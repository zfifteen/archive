# Z5D Factorization Shortcut Results Summary (Skewed Mode, k=0.3)

## Parameters
- N_max: 721,541
- Samples: 500
- Mode: Skewed semiprimes
- k: 0.3 (legacy single mode)
- Epsilon Range: 0.02 to 0.05

## Summary Table
| Epsilon (ε) | Success Rate (95% CI) | Avg Divisions Until Success | Efficiency Gain |
|-------------|-----------------------|-----------------------------|-----------------|
| 0.02       | 10.2% (7.8-13.2)     | 30.4                       | 4.8x faster    |
| 0.03       | 14.4% (11.6-17.7)    | 44.2                       | 3.3x faster    |
| 0.04       | 18.2% (15.1-21.8)    | 58.8                       | 2.5x faster    |
| 0.05       | 22.2% (18.8-26.0)    | 69.3                       | 2.1x faster    |

## Key Insights
- Single-pass mode with k=0.3 shows success rates from 10.2% to 22.2% across epsilon values.
- Geometric method reduces candidates: 23.6 - 57.8 avg vs ~146 for naive.
- Computational savings: 60% - 83% reduction.
- Matches reference implementation closely for ε=0.02 (10.2% vs 11.8% partial rate).

This run uses the legacy single k-value mode to approximate the reference Python implementation.

