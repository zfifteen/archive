# Autocorrelation-Aware Prime Sieve

## Overview

A prime sieve that uses gap autocorrelation to predict where the next primes are likely to cluster, dynamically adjusting sieving effort based on recent gap history.

## What It Does

An enhanced prime sieve (extending Sieve of Eratosthenes) that:
- Tracks recent gap history as it sieves
- Uses autocorrelation structure to predict likely prime locations
- Dynamically focuses computational effort on high-probability regions
- Reduces wasted work in sparse prime regions

## Why This Is Novel

**Couldn't exist before the autocorrelation discovery.**

Classical sieves (Eratosthenes, Atkin, etc.):
- Mechanically eliminate all composites
- Treat all regions uniformly
- Have no adaptive strategy based on recent primes found
- Assume primes are independently distributed

Gap autocorrelation changes this:
- **Gaps have memory** — recent gap sizes influence future gaps
- **Clustering is predictable** — ACF structure reveals where primes will bunch vs. spread
- **Adaptive focus** — Allocate more effort to predicted dense regions, less to sparse regions

This is the first sieve that learns from what it's already found.

## Use Cases

### High-Performance Prime Generation
Generate large prime lists faster by reducing unnecessary elimination operations in low-probability regions.

**Example:**  
Sieving range: [10^9, 10^9 + 10^6]  
Recent gaps: [14, 8, 6, 10, 4] (shorter than average → expect clustering)  
ACF-aware sieve: Focus more effort on next 50k candidates, reduce effort on candidates 50k-100k away

### Cryptographic Prime Search
Generate cryptographic primes (e.g., 2048-bit RSA primes) with better performance by exploiting gap structure rather than uniform searching.

### Prime Density Verification
Test whether ACF-aware sieving matches theoretical predictions, validating the autocorrelation model in practice.

## Key Innovation

**This is the first adaptive sieve that uses gap memory.**

Classical approaches:
- Sieve of Eratosthenes: Eliminate all multiples, no adaptation
- Wheel factorization: Fixed patterns (mod 2, 3, 5), no learning
- Segmented sieves: Memory optimization, not probability-based

This approach:
- Tracks gap history buffer (e.g., last 40 gaps)
- Computes ACF weights on-the-fly
- Adjusts sieve intensity based on predicted prime density
- Learns and adapts as it progresses

## Status

**Concept stage** — awaiting implementation after core `prime_gap` library is complete.

## Technical Requirements

Depends on:
- `prime_gap.gap_analysis` — for on-the-fly ACF computation
- `prime_gap.lognormal_prefilter` — for gap normalization
- Fast sieve implementation (baseline: segmented sieve)
- Circular buffer for gap history (configurable depth)

## Performance Baseline

To demonstrate value, must outperform:
- **Standard Eratosthenes**: Baseline sieve with no adaptation
- **Wheel-factorized sieve**: Sieve with fixed mod-30 or mod-210 patterns
- **Segmented sieve**: Memory-optimized but non-adaptive sieve

Success metric: Generate N primes in < 90% of operations compared to baseline sieve, for N in range [10^6, 10^9].

## Implementation Strategy

1. **Baseline sieve**: Start with standard segmented Eratosthenes
2. **Add gap tracking**: Maintain circular buffer of last K gaps
3. **Compute ACF on-the-fly**: Lightweight ACF computation every M primes
4. **Adaptive intensity**: Scale elimination effort by predicted density
   - High ACF → expect clustering → sieve intensively
   - Low/negative ACF → expect sparse region → sieve lightly
5. **Benchmark**: Compare operations vs. baseline

## Limitations

- **Overhead**: ACF computation adds cost; must be amortized over many primes
- **Scale-dependent**: ACF patterns change with scale; sieve must adapt parameters
- **Memory**: Gap buffer adds memory overhead (mitigated by circular buffer)

## Future Enhancements

- **Multi-scale ACF**: Use different ACF windows for different prime magnitudes
- **Parallel sieves**: Split work across threads based on predicted density zones
- **Hybrid with wheel**: Combine ACF adaptation with fixed modular patterns
