# Lognormal Gap Predictor

## Overview

A prime gap prediction system that exploits lognormal distribution and autocorrelation structure to predict the next prime gap size.

## What It Does

Predicts the *next* prime gap size using:
- The lognormal distribution parameters (mean, variance) at the current scale
- Autocorrelation structure from previous gaps (the "memory" in the gap process)

## Why This Is Novel

**Couldn't exist before the lognormal+ACF discovery.**

Random sieve models (Cramér, etc.) assume gaps are independent and exponentially distributed. Under that model, there's no predictive signal—each gap is a fresh random draw with no memory.

The lognormal+autocorrelation findings change everything:
- **Lognormal structure** provides a probabilistic model for gap sizes at any scale
- **Autocorrelation** means previous gaps influence future gaps—the gap process has memory

A predictor that uses ACF structure to weight predictions **couldn't be built** under the old model. It would have no signal to exploit.

## Use Cases

### Prime Generation Algorithms
Estimate "how far to search" for the next prime. Instead of blind incremental testing, use the lognormal model + recent gap history to predict where the next prime is likely to be.

**Example:**  
Current prime: `p = 1,000,003`  
Recent gaps: `[6, 4, 2, 10, 8]`  
Predictor output: "Next gap likely in range [4, 12] with 80% confidence"

### Prime Density Estimation
For cryptographic key generation, estimate how many candidates need to be tested to find a prime of a given bit length.

### Research Tool
Test whether specific prime sequences (e.g., Mersenne primes, twin primes) exhibit different gap autocorrelation patterns than "typical" primes.

## Key Innovation

**This is the first gap predictor that uses structure rather than assuming randomness.**

Classical approaches:
- Assume gap ≈ log(p) (from PNT)
- Assume next gap is independent of previous gaps

This predictor:
- Models gap ~ Lognormal(μ(scale), σ²(scale))
- Uses ACF weights from recent gap history
- Continuously updates parameters as scale changes

## Status

**Concept stage** — awaiting implementation after core `prime_gap` library is complete.

## Technical Requirements

Depends on:
- `prime_gap.lognormal_prefilter` — for gap extraction and normalization
- `prime_gap.gap_analysis` — for lognormal parameter estimation and ACF computation
- Historical gap buffer (configurable depth, e.g., last 40 gaps for ACF)

## Performance Baseline

To demonstrate value, the predictor must outperform:
- **Naive baseline**: Always predict gap = log(p)
- **Historical average**: Predict gap = mean of last N gaps
- **Exponential model**: Sample from Exp(λ) where λ = 1/log(p)

Success metric: Prediction accuracy (within ±2 of actual gap) > 60% on test set (compared to ~40% for exponential baseline).

## Future Enhancements

- **Adaptive ACF depth**: Dynamically adjust how many previous gaps to consider based on scale
- **Contextual models**: Different lognormal parameters for different gap "regimes" (small, typical, large)
- **Integration with Z5D**: Combine gap prediction with Z5D prime predictor for end-to-end prime location forecasting
