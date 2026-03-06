# Inverse Mersenne Probe RSA Benchmark Report

**Generated:** 2025-09-05 00:40:09

**Parameters:**
- κ_geo: 0.30769
- Repetitions per test: 2
- Total results: 24

## Executive Summary

- **Success Rate:** 0.0% (0/24 tests)
- **Mean Time:** 0.8ms (95% CI: [0.2, 1.5])
- **Mean Z5D Predictions:** 192.0 (95% CI: [165.3, 218.7])

## Detailed Results by RSA Number

### RSA-100

**Number of bits:** 330

**Window Size 128:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 128.0 (95% CI: [128.0, 128.0])

**Window Size 256:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 256.0 (95% CI: [256.0, 256.0])

### RSA-110

**Number of bits:** 364

**Window Size 128:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 128.0 (95% CI: [128.0, 128.0])

**Window Size 256:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 256.0 (95% CI: [256.0, 256.0])

### RSA-120

**Number of bits:** 397

**Window Size 128:**
- Successes: 0/2
- Time: 3.0ms (95% CI: [3.0, 3.0])
- Z5D Predictions: 128.0 (95% CI: [128.0, 128.0])

**Window Size 256:**
- Successes: 0/2
- Time: 5.9ms (95% CI: [5.9, 5.9])
- Z5D Predictions: 256.0 (95% CI: [256.0, 256.0])

### RSA-129

**Number of bits:** 426

**Window Size 128:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 128.0 (95% CI: [128.0, 128.0])

**Window Size 256:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 256.0 (95% CI: [256.0, 256.0])

### RSA-130

**Number of bits:** 423

**Window Size 128:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 128.0 (95% CI: [128.0, 128.0])

**Window Size 256:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 256.0 (95% CI: [256.0, 256.0])

### RSA-140

**Number of bits:** 440

**Window Size 128:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 128.0 (95% CI: [128.0, 128.0])

**Window Size 256:**
- Successes: 0/2
- Time: 0.1ms (95% CI: [0.1, 0.1])
- Z5D Predictions: 256.0 (95% CI: [256.0, 256.0])

## Statistical Analysis

**Bootstrap Methodology:** 1000 resamples with replacement for 95% confidence intervals.

**Success Criteria:**
- ≥40% median reduction in search space vs uniform scan
- Reproducibility across platforms
- Statistical significance with p < 0.05

### Search Efficiency Analysis

| RSA Number | Window Size | Mean Time (ms) | 95% CI Lower | 95% CI Upper | Z5D Predictions | Success Rate |
|------------|-------------|----------------|--------------|--------------|-----------------|---------------|
| RSA-100 | 128 | 0.1 | 0.1 | 0.1 | 128.0 | 0.0% |
| RSA-100 | 256 | 0.1 | 0.1 | 0.1 | 256.0 | 0.0% |
| RSA-110 | 128 | 0.1 | 0.1 | 0.1 | 128.0 | 0.0% |
| RSA-110 | 256 | 0.1 | 0.1 | 0.1 | 256.0 | 0.0% |
| RSA-120 | 128 | 3.0 | 3.0 | 3.0 | 128.0 | 0.0% |
| RSA-120 | 256 | 5.9 | 5.9 | 5.9 | 256.0 | 0.0% |
| RSA-129 | 128 | 0.1 | 0.1 | 0.1 | 128.0 | 0.0% |
| RSA-129 | 256 | 0.1 | 0.1 | 0.1 | 256.0 | 0.0% |
| RSA-130 | 128 | 0.1 | 0.1 | 0.1 | 128.0 | 0.0% |
| RSA-130 | 256 | 0.1 | 0.1 | 0.1 | 256.0 | 0.0% |
| RSA-140 | 128 | 0.1 | 0.1 | 0.1 | 128.0 | 0.0% |
| RSA-140 | 256 | 0.1 | 0.1 | 0.1 | 256.0 | 0.0% |

**Note:** This is a hypothesis test. Crypto relevance claims require p < 10⁻¹⁰ evidence.
