# Lognormal Pre-Filter for Factorization

## Overview

A factorization algorithm that uses the lognormal prime-gap model as a pre-filter and search policy for finding factors of semiprimes N = pq.

## What It Does

Given a semiprime N = pq, generates a **search policy** that prioritizes candidate prime factors based on gap likelihood from the lognormal distribution.

Instead of searching linearly or with fixed sieves, samples candidate factors **from the lognormal distribution** of gaps around √N.

## Why This Is Novel

**Couldn't exist before the lognormal discovery.**

Traditional trial division and factor sieves:
- Search linearly (2, 3, 5, 7, 11, ...) or with fixed modular patterns
- Treat all candidates as equally likely
- Have no model for where primes are more/less likely to appear

The lognormal gap model changes this:
- Provides a **probability distribution** for gap sizes at any scale
- Enables sampling candidates weighted by their statistical likelihood
- Reduces search space by focusing on high-probability regions

This is PR-0004 from the playground in production form.

## Use Cases

### Small-to-Medium Semiprime Factorization
Factor semiprimes where trial division or ECM would otherwise search blindly. Lognormal sampling provides better-than-random search efficiency for N up to ~40-60 bits.

**Example:**  
Semiprime: `N = 1,073,676,287` (30-bit)  
√N ≈ 32,767  
Traditional: Test all primes near √N linearly  
Lognormal: Sample candidates from Lognormal(μ(√N), σ²(√N)), focusing on most likely gap sizes

### Cryptanalysis Research
Test whether specific semiprime generation methods (e.g., RSA key generation) produce factors with exploitable gap patterns.

### Hybrid Factorization
Use lognormal pre-filter as first pass, then fall back to ECM or quadratic sieve for harder cases.

## Key Innovation

**This is the first factorization algorithm that uses prime gap structure.**

Classical approaches:
- Trial division: Linear search, no structure
- Pollard's rho: Birthday paradox, no prime-specific knowledge
- ECM: Smooth number exploitation, ignores gap patterns

This approach:
- Exploits lognormal gap distribution
- Samples from probability model rather than searching deterministically
- Better-than-random efficiency for appropriate scales

## Status

**Proof-of-concept exists** in `playground/experiments/PR-0004_lognormal_factorization`.  
Awaiting port to clean `prime_gap` library and performance benchmarking.

## Technical Requirements

Depends on:
- `prime_gap.lognormal_prefilter` — for gap distribution parameters at scale √N
- `prime_gap.gap_analysis` — for lognormal parameter estimation
- Prime sieve (for generating candidate set)
- Probabilistic sampling from lognormal distribution

## Performance Baseline

To demonstrate value, must outperform:
- **Trial division baseline**: Linear search from 2 to √N
- **Wheel factorization**: Fixed modular sieve (2, 3, 5 wheel)
- **Random sampling**: Uniform random candidate selection

Success metric: Factor N in < 80% of trial division operations for semiprimes N < 2^40.

## Limitations

- **Not competitive with ECM/QS for large N**: This is a trial-division enhancement, not a subexponential algorithm
- **Requires accurate lognormal parameters**: Performance degrades if gap model is miscalibrated
- **Best for specific scale range**: Most effective for 30-50 bit semiprimes where trial division is still viable

## Future Enhancements

- **Adaptive sampling**: Dynamically adjust lognormal parameters based on search progress
- **Multi-scale prefiltering**: Use different gap models for p and q separately
- **Integration with ECM**: Use lognormal prefilter to generate ECM curve parameters
