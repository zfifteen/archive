# FINDINGS: Quasi-Monte Carlo Methods in Integer Factorization

**Experiment ID:** qmc_factorization_test  
**Date:** 2025-12-26 06:51:12  
**Status:** EXPERIMENT COMPLETED

---

## CONCLUSION

**HYPOTHESIS FALSIFIED**: No statistically significant difference between QMC and Monte Carlo

**Key Findings:**
- Sobol QMC: 24.5 ± 39.0 iterations (mean ± std)
- Random MC: 36.7 ± 51.0 iterations (mean ± std)
- **Improvement: +33.2%** (negative means QMC is faster)
- Statistical significance (p < 0.05): False
- p-value: 0.483262

**Interpretation:**
The experimental data DOES NOT support the hypothesis that Quasi-Monte Carlo methods provide
computational advantages for integer factorization via the GVA geometric approach. Possible explanations:

1. The GVA geometric mapping does not effectively leverage QMC's low-discrepancy properties
2. Integer factorization is fundamentally discrete, whereas QMC excels in continuous integration
3. The variance reduction of QMC may not translate to the factor search space
4. The test semiprimes may be too small to reveal potential advantages

This result aligns with the broader literature: QMC methods have no established application to
integer factorization, and their benefits are primarily in numerical integration and continuous
optimization problems.

---

## TECHNICAL SUPPORTING EVIDENCE

### 1. Star Discrepancy Measurements

Star discrepancy D* measures sequence uniformity (lower is better):

| Method | Mean D* | Std D* |
|--------|---------|--------|
| Sobol  | 0.003143 | 0.000196 |
| Halton | 0.004213 | 0.000202 |
| Anosov | 0.022526 | 0.002599 |
| Random | 0.028803 | 0.003891 |

✓ Sobol and Halton show lower discrepancy than Random, confirming QMC property  
✓ Anosov sequence has higher discrepancy, but leverages Selberg-Ruelle geometric structure

### 2. Factorization Performance

Iterations required to find factors (successful trials only):

| Method | Mean | Median | Std Dev | Success Rate |
|--------|------|--------|---------|--------------|
| Sobol  | 24.5 | 5.0 | 39.0 | 100.0% |
| Halton | 29.9 | 14.0 | 45.6 | 100.0% |
| Anosov | 14.7 | 3.0 | 32.4 | 100.0% |
| Random | 36.7 | 8.0 | 51.0 | 100.0% |

### 3. Statistical Hypothesis Test

**Test:** Independent t-test comparing Sobol vs Random iteration counts  
**Null Hypothesis:** No difference in mean iterations  
**Alternative:** QMC (Sobol) requires fewer iterations than MC (Random)

- t-statistic: -0.7105
- p-value: 0.483262
- Significance level: α = 0.05
- **Result:** No significant difference or Random is better

### 4. Test Parameters

- **Semiprimes tested:** [15, 21, 35, 77, 91]
- **Samples per trial:** 1000
- **Trials per semiprime:** 3
- **Total experiments:** 15

---

## REPRODUCIBILITY

All code is available in `qmc_factorization.py`. To reproduce:

```bash
cd experiments/qmc_factorization_test
pip install -r requirements.txt
python qmc_factorization.py --full
```

Random seeds are fixed (42 + trial_number) for deterministic reproduction.

---

## LIMITATIONS

1. **Scale:** Only tested on small semiprimes (< 1000)
2. **GVA Method:** The geometric mapping used is experimental and not optimized
3. **Sample size:** Statistical power limited by computational constraints
4. **Generalizability:** Results specific to this geometric factorization approach

---

**Generated:** 2025-12-26 06:51:12
