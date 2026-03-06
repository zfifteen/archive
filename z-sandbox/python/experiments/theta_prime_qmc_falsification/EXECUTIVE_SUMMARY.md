# Executive Summary: θ′-biased QMC Falsification Experiment

**Experiment ID:** theta-prime-qmc-falsification-2025-11-19  
**Status:** COMPLETE  
**Date:** 2025-11-19  
**Lead:** Z-Sandbox Agent

---

## Results (Up Front)

### Primary Finding: **HYPOTHESIS FALSIFIED**

**Tested Hypothesis:** θ′-biased QMC (Sobol+Owen) with mean-one retiming (α=0.2) increases unique RSA factorization candidates vs MC baseline by >5%.

**Key Results:**
- **Unique Candidates:** MC baseline: 0.20%, Sobol+Owen (all α): 0.20% ⟹ **0% lift**
- **Statistical Significance:** None (p > 0.05 for all α values tested)
- **Discrepancy Improvement:** Sobol shows 96.7% lower discrepancy than MC (0.000290 vs 0.008734)
- **Mean-One Property:** ✓ VERIFIED for all α ∈ {0.05, 0.10, 0.15, 0.20} (error < 0.00002%)

**Conclusion:** While Sobol+Owen demonstrates dramatically superior low-discrepancy properties, this does NOT translate to improved unique candidate generation in the tested factorization scenario. The θ′ bias and mean-one retiming mechanisms provide no measurable advantage over MC baseline for this task.

---

## Summary Statistics

| Metric | MC Baseline | Sobol (α=0.05) | Sobol (α=0.10) | Sobol (α=0.15) | Sobol (α=0.20) |
|--------|-------------|----------------|----------------|----------------|----------------|
| Unique % | 0.20% | 0.20% | 0.20% | 0.20% | 0.20% |
| Lift vs MC | — | +0.00% | +0.00% | +0.00% | +0.00% |
| Factor Hit (p) | 100% | 100% | 100% | 100% | 100% |
| Factor Hit (q) | 100% | 100% | 100% | 100% | 100% |
| Mean Steps to Hit | ~6 | ~6 | ~6 | ~6 | ~6 |

**Test Configuration:**
- N = 899 (29 × 31, 10-bit semiprime)
- Replicates: 50 per configuration
- Samples: 5,000 per trial
- α sweep: {0.05, 0.10, 0.15, 0.20}
- k parameter: 0.3 (θ′ resolution exponent)

---

## Implications

### What This Means
1. **Low-discrepancy ≠ More unique candidates:** QMC's superior uniformity doesn't improve candidate diversity in this integer space
2. **θ′ bias ineffective:** Golden-ratio modulation provided no advantage for distant-factor detection
3. **Mean-one retiming irrelevant:** Interval perturbation (α ≤ 0.2) had zero impact on outcomes
4. **Factor detection identical:** Both methods found factors with equal efficiency

### What This Does NOT Mean
1. NOT claiming QMC is useless for all factorization approaches
2. NOT tested on cryptographically-relevant sizes (only 10-bit demo)
3. NOT evaluated alternative bias mechanisms beyond θ′(n,k)
4. NOT assessed computational cost tradeoffs

---

## Validation Results

### Mean-One Retiming Property ✓
```
α=0.05: Mean=100.000005, Error=0.000005% ✓ PASS
α=0.10: Mean=100.000010, Error=0.000010% ✓ PASS
α=0.15: Mean=100.000015, Error=0.000015% ✓ PASS
α=0.20: Mean=100.000020, Error=0.000020% ✓ PASS
```

### Discrepancy Test ✓
```
MC:         D*=0.008734 (theoretical O(1/√N) = 0.010000)
Sobol+Owen: D*=0.000290 (theoretical O(log N/N) = 0.000921)
Improvement: 96.7% lower discrepancy
```

---

## Next Steps

1. **Scale test:** Evaluate on 64-bit, 128-bit semiprimes to check if pattern holds
2. **Alternative biases:** Test Z=κ(n)·θ′(n,k) combined weight (not just θ′ alone)
3. **Candidate quality:** Analyze factor-proximity distribution, not just count
4. **Computational cost:** Measure overhead of Sobol+Owen vs MC for fair comparison

---

## Artifacts

- **Raw Data:** `results/unique_candidates.json` (250 trials)
- **Analysis:** `results/deltas.json` (statistical summary)
- **Discrepancy:** `results/discrepancy_results.json`
- **Plots:** `plots/bias_adaptive_example.png`
- **Scripts:** `scripts/*.py` (all code reproducible)

---

## Reproducibility Command

```bash
cd experiments/theta_prime_qmc_falsification/scripts
python3 qmc_factorization_analysis.py
```

**Environment:**
- Python 3.12.3
- NumPy 1.26+
- SciPy 1.11+
- z-sandbox infrastructure (qmc_engines.py, z_framework.py)

---

## Mission Charter Compliance

This experiment adheres to the 10-point z-sandbox Mission Charter:

1. ✓ **First Principles:** Z-Framework axioms, κ(n), θ′(n,k) defined
2. ✓ **Ground Truth:** Experiment executed 2025-11-19, N=899 (29×31), full provenance
3. ✓ **Reproducibility:** Fixed seeds (42), exact commands, full environment spec
4. ✓ **Failure Knowledge:** Hypothesis FALSIFIED, limitations documented
5. ✓ **Constraints:** Academic research only, no cryptographic claims
6. ✓ **Context:** z-sandbox research, testing QMC bias mechanisms
7. ✓ **Models & Limits:** Tested only 10-bit demo, NOT cryptographic scale
8. ✓ **Interfaces:** Python scripts, JSON outputs, PNG plots
9. ✓ **Calibration:** α sweep {0.05-0.20}, k=0.3, bootstrap CI (n=2000)
10. ✓ **Purpose:** Falsify θ′-QMC hypothesis with rigorous statistical test

**Compliance Status:** FULL ✓

---

## Contact

**Questions or follow-up:** File issue in z-sandbox repository

**Validation Tool:**
```bash
python3 tools/validate_charter.py experiments/theta_prime_qmc_falsification/EXECUTIVE_SUMMARY.md
```

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-11-19T17:52:00Z  
**Author:** Z-Sandbox Agent
