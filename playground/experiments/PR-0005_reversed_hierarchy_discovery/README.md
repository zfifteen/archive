# The Reversed Hierarchy Discovery

## Overview

This experiment explores a counterintuitive phenomenon in the convergence of prime gap moments to their exponential distribution asymptotes: **higher-order moments converge FASTER than lower-order moments**.

This contradicts standard statistical theory, where higher moments should be more volatile due to outlier sensitivity.

## Abstract

We demonstrate that the reversal arises from the factorial normalization `k!` in the exponential moment formula, which "absorbs" tail contributions more effectively for higher k. The finding reveals that prime gaps have more regular extremes than their average behavior suggests, pointing to deep constraints from the multiplicative sieve structure.

## Key Findings

### Main Result: Reversed Convergence Hierarchy

At large n, we observe:
```
|A_4(n)| < |A_3(n)| < |A_2(n)| < |A_1(n)|
```

Where `A_k(n) = μ'_{k,n} / [k! × (log n)^k] - 1` is the relative deviation from the exponential asymptote.

### Theoretical Background

The k-th moment of the first n prime gaps satisfies:
```
μ'_{k,n} ~ k! × (log n)^k   as n → ∞
```

This matches the k-th moment of Exp(1/log n), suggesting gaps behave asymptotically like exponential random variables.

### The Paradox

Standard statistical theory predicts that higher moments:
- Require larger samples for accurate estimation
- Are more sensitive to extreme values
- Should converge SLOWER to population values

**But for prime gaps, the OPPOSITE holds!**

## Running the Analysis

```bash
cd experiments/PR-0005_reversed_hierarchy_discovery
python3 reversed_hierarchy_analysis.py
```

The script will output:
1. Theoretical foundation
2. Verification of the reversed hierarchy across 12 data points
3. Convergence rate analysis
4. Mechanistic explanation of the factorial effect
5. Variability analysis
6. Testable predictions
7. Implications for number theory
8. Related work and open questions
9. Conclusions

## Data Source

The analysis uses empirical data from Cohen & Wolf (2024), consisting of moments computed from actual prime gap sequences at 12 different scales ranging from n = 3,510 to n = 8.7 × 10^12.

## Implications

This finding has profound implications for:
- **Cramér's Model**: Shows it captures tails better than bulk behavior
- **Sieve Theory**: Suggests constraints are stronger in tails than averages
- **Random Matrix Theory**: Potential connections to spectral rigidity
- **Testing Methods**: Higher moments are better diagnostics for exponential convergence

## Open Questions

1. Can the reversal be proven rigorously (not just empirically)?
2. What is the exact asymptotic form of A_k(n) as n → ∞?
3. Does the Riemann Hypothesis affect convergence rates?
4. Does the pattern extend to higher moments (k=5,6,7,...)?
5. Do other prime subsets (twin primes, Sophie Germain primes) show the same reversal?

## Citation

```
Reversed Convergence Hierarchy in Prime Gap Moments (2025)
Analysis based on Cohen & Wolf empirical data
```

## Related Work

- Cohen & Wolf (2024): Empirical verification of moment asymptotics
- Cramér (1936): Random model for prime gaps
- Maier (1985): Local irregularities violate Cramér's model
- Granville (1995): Heuristics for maximal gaps
- Soundararajan (2007): Distributions not exponential despite moments
