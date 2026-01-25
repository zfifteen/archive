# Prime Gap Lognormal — Repository Story

## The Premise

For centuries, prime numbers have been studied through their **counts** — how many exist below a threshold. The Prime Number Theorem (PNT) tells this story with near-perfect accuracy: by 10^8, prime counts match PNT predictions to 99.99%.

But primes also tell a second story through their **gaps** — the distances between consecutive primes. This repository reveals that story: **prime gaps follow lognormal distributions and exhibit strong autocorrelation**, patterns incompatible with classical random sieve models.

## The Discovery

From experiments spanning 10^6 to 10^8, two discoveries emerge with brutal consistency:




1. **Lognormal structure**: Gap distributions are lognormal across all scales and bands — 100% of 6 tested bands pass distributional tests with p-values > 0.05. This implies **multiplicative randomness** in gap formation.

2. **Autocorrelation**: Gaps exhibit memory. At 10^8, 98% of tested lags show significant autocorrelation (Ljung-Box p < 0.05). Gaps are not independent events.
## The Conflict

These findings collide with the Cramér random model, which assumes gaps behave like independent exponential variables drawn from a Poisson process. If gaps were truly random:
- They would follow exponential distributions (they follow lognormal).
- They would be uncorrelated (they exhibit strong autocorrelation).
- They would lack multiplicative structure (they demonstrate it consistently).

This contradiction matters. Cryptographic systems, prime generation algorithms, and factorization complexity all rest on assumptions about gap behavior. If gaps have **memory and structure**, those assumptions require re-examination.

## The Concepts

This repository introduces and validates several core concepts through rigorous computational experiments:

### loglog_kernel
The analytical lens for viewing prime phenomena on doubly-logarithmic scales. Stabilizes structure across magnitude ranges and reveals scale-invariant patterns.

### lognormal_prefilter
The transformation pipeline: extract gaps → log-transform → normalize → analyze. Reveals the multiplicative randomness underlying additive prime distributions.

### Gap Process vs Count Process
- **Count process**: Additive, PNT-governed, nearly deterministic at scale.
- **Gap process**: Multiplicative, lognormal, autocorrelated, exhibits memory.

Understanding primes requires understanding both processes and their interplay.

## The Experiments

This repository contains:

- **PR-0002_prime_gap_analysis**: The flagship cross-scale validation (10^6, 10^7, 10^8) establishing PNT accuracy, lognormal distributions, and autocorrelation patterns.

- **PR-0002_prime_log_gap_falsification**: Negative controls demonstrating where random/exponential gap models fail to reproduce the three signatures.

- **PR-0003_prime_log_gap_optimized**: Engineering hardening for larger scales and faster execution.

- **PR-0004_lognormal_factorization**: Bridge from gap statistics to factorization structure and semiprime landscapes.

Each experiment is reproducible, documented, and validates a facet of the core claim.

## The Implications

**For number theory**: A challenge to random sieve models and an invitation to explore the generating process for multiplicative gap structure.

**For cryptography**: Gap autocorrelation may affect assumptions in prime-dependent systems (RSA key generation, primality testing, security proofs).

**For prediction**: Structured, autocorrelated gaps open doors to predictive modeling approaches that exploit memory in the gap process.

## The Vision

This is not a collection of scripts — it's the beginning of a **Prime Gap Program**:
- A clean, intentional library (`loglog_kernel`, `lognormal_prefilter`, `gap_analysis`).
- A curated suite of canonical experiments demonstrating reproducible phenomena.
- Documentation that reads like a paper, not a lab notebook.

The goal: make the lognormal + autocorrelation story accessible, reproducible, and actionable for anyone studying prime structure, cryptographic primitives, or predictive frameworks.

---

**Current status**: Repository bootstrapped. REPO_STORY.md established. Next: implement core library, port flagship experiments, write methods documentation.

**Origin**: Distilled from brutal red-team validation in `playground/experiments/PR-0002_prime_gap_analysis`. This repo is the intentional second edition — same discoveries, cleaner narrative, higher quality artifacts.
