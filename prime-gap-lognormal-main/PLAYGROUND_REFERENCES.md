# Playground References — Lognormal Prime Gap Work

This document provides links and descriptions to all existing lognormal-related experiments and implementations in the `zfifteen/playground` repository. These are the source materials for building the intentional `prime-gap-lognormal` repository.

---

## Core Experiments

### PR-0002_prime_gap_analysis
**The Flagship Experiment**

🔗 **Link:** https://github.com/zfifteen/playground/tree/main/experiments/PR-0002_prime_gap_analysis

**Description:**  
Complete cross-scale analysis (10^6, 10^7, 10^8) establishing three core signatures: PNT accuracy converging to 99.99%, lognormal gap distributions (100% of bands pass statistical tests), and strong autocorrelation (98% of lags significant at 10^8). This is the primary source for the claims in REPO_STORY.md.

**Key Documents:**
- [`RESULTS.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0002_prime_gap_analysis/RESULTS.md) — Complete empirical results with tables, p-values, and interpretation
- [`CROSS_SCALE_ANALYSIS.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0002_prime_gap_analysis/CROSS_SCALE_ANALYSIS.md) — Scale convergence patterns and consistency validation
- [`SPEC.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0002_prime_gap_analysis/SPEC.md) — Technical specification of methods and implementation
- [`README.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0002_prime_gap_analysis/README.md) — Experiment overview and quick start

**What to Port:**
- Core gap analysis logic from `src/`
- Statistical fitting procedures (lognormal, exponential)
- Ljung-Box autocorrelation testing
- Banding and distribution analysis methods
- Result tables and key findings

---

### PR-0002_prime_log_gap_falsification
**Negative Controls & Stress Testing**

🔗 **Link:** https://github.com/zfifteen/playground/tree/main/experiments/PR-0002_prime_log_gap_falsification

**Description:**  
Falsification experiments testing whether random/exponential gap models can reproduce the three signatures (PNT accuracy, lognormal structure, autocorrelation). Demonstrates where Cramér-style random models fail.

**Key Documents:**
- [`FINDINGS.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0002_prime_log_gap_falsification/FINDINGS.md) — Results showing random models cannot reproduce lognormal + ACF patterns
- [`DATA.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0002_prime_log_gap_falsification/DATA.md) — Datasets and synthetic gap generators used

**What to Port:**
- Synthetic gap generation logic
- Comparison framework for real vs. synthetic gaps
- Failure modes of random models

---

### PR-0003_prime_log_gap_optimized
**Performance & Scale Engineering**

🔗 **Link:** https://github.com/zfifteen/playground/tree/main/experiments/PR-0003_prime_log_gap_optimized

**Description:**  
Optimized implementation of gap analysis for larger scales and faster execution. Engineering hardening of the methods from PR-0002.

**Key Documents:**
- [`RESULTS_AT_SCALE.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0003_prime_log_gap_optimized/RESULTS_AT_SCALE.md) — Performance benchmarks and scalability data
- [`PERFORMANCE_ANALYSIS.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0003_prime_log_gap_optimized/PERFORMANCE_ANALYSIS.md) — Optimization strategies and runtime profiling
- [`PROFILING_SUMMARY.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0003_prime_log_gap_optimized/PROFILING_SUMMARY.md) — Detailed profiling results

**What to Port:**
- Optimized gap extraction and processing
- Memory-efficient banding strategies
- Performance benchmarks for documentation

---

### PR-0004_lognormal_factorization
**Factorization Bridge**

🔗 **Link:** https://github.com/zfifteen/playground/tree/main/experiments/PR-0004_lognormal_factorization

**Description:**  
Connects lognormal gap structure to factorization and semiprime landscapes. Uses lognormal prime-gap model as a pre-filter/search policy for factorization algorithms.

**Key Documents:**
- [`README.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0004_lognormal_factorization/README.md) — Overview of lognormal pre-filter factorization pipeline
- [`ABSTRACT.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0004_lognormal_factorization/ABSTRACT.md) — Conceptual framework
- [`TEST_RESULTS.md`](https://github.com/zfifteen/playground/blob/main/experiments/PR-0004_lognormal_factorization/TEST_RESULTS.md) — Empirical validation results

**What to Port:**
- Lognormal pre-filter logic
- Connection between gap structure and factorization complexity
- Conceptual framework for implications section

---

## Core Libraries & Tools

### loglog_kernel
**Doubly-Logarithmic Transform Library**

🔗 **Link:** https://github.com/zfifteen/playground/tree/main/experiments/loglog_kernel

**Description:**  
A clean, self-contained C99 library for computing log(log(x)) using arbitrary-precision arithmetic with GMP and MPFR. Provides the analytical lens for viewing prime phenomena on doubly-logarithmic scales. Stabilizes structure across magnitude ranges and reveals scale-invariant patterns.

**Key Documents:**
- [`README.md`](https://github.com/zfifteen/playground/blob/main/experiments/loglog_kernel/README.md) — Library overview and API documentation
- `loglog_mpfr.c` / `loglog_mpfr.h` — Core implementation
- `benchmark_loglog.c` — Performance benchmarks

**What to Port:**
- Core loglog transform implementation
- Precision management logic
- API design for Python bindings or reimplementation

---

### lognormal_prefilter
**Gap Transformation Pipeline**

🔗 **Link:** https://github.com/zfifteen/playground/tree/main/experiments/lognormal_prefilter

**Description:**  
The transformation pipeline: extract gaps → log-transform → normalize → analyze. Reveals the multiplicative randomness underlying additive prime distributions. Also serves as a factorization pipeline for semiprimes N = pq that uses a lognormal prime-gap model as a pre-filter/search policy.

**Key Documents:**
- [`README.md`](https://github.com/zfifteen/playground/blob/main/experiments/lognormal_prefilter/README.md) — Pipeline overview
- [`IMPLEMENTATION_SUMMARY.md`](https://github.com/zfifteen/playground/blob/main/experiments/lognormal_prefilter/IMPLEMENTATION_SUMMARY.md) — Technical details
- `example.py` — Usage examples

**What to Port:**
- Gap extraction and log-transformation logic
- Normalization procedures
- Prefilter API for integration with gap_analysis

---

## Additional Context

### Related Experiments (Non-Lognormal)
These experiments in `playground` are not directly lognormal-focused but may provide context:

- **`selberg-tutorial`** — Selberg sieve implementation (context for random sieve models)
- **`semiprime_triangle`** — Geometric visualization of semiprime structure (related to factorization implications)

---

## Usage Notes

When porting code from `playground` to `prime-gap-lognormal`:

1. **Extract, don't copy**: Pull only the minimal logic needed for the new repo's API
2. **Upgrade names**: Refactor variable/function names for clarity and consistency
3. **Consolidate outputs**: Unify JSON schemas and output formats across all scales
4. **Document origins**: Reference specific playground files in comments for traceability

---

## Key Results to Reference

From PR-0002_prime_gap_analysis:

| Scale | N Primes | Mean gap/log(p) | Slope | ACF Significance | Lognormal Bands Pass |
|-------|----------|-----------------|-------|------------------|---------------------|
| 10^6  | 78,498   | 1.001663        | -0.003442 | 63% lags | 100% (6/6) |
| 10^7  | 664,579  | 1.000730        | -0.003462 | 85% lags | 100% (6/6) |
| 10^8  | 5,761,455| 1.000335        | -0.003518 | 98% lags | 100% (6/6) |

**Interpretation:**  
- PNT accuracy: 99.83% → 99.93% → 99.99%
- Lognormal fit: Consistent across all scales and bands
- Autocorrelation: Strengthens with scale (memory in gap process)

---

**Repository:** https://github.com/zfifteen/playground  
**Created:** December 2025  
**Purpose:** Laboratory notebook and experimental workspace for computational number theory research
