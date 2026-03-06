# θ′-biased QMC Falsification Experiment

**Status:** ✅ COMPLETE  
**Result:** ❌ HYPOTHESIS FALSIFIED  
**Date:** 2025-11-19

---

## TL;DR

**Question:** Does θ′-biased QMC (Sobol+Owen) with mean-one retiming improve RSA factorization candidate generation by >5% vs Monte Carlo?

**Answer:** **NO.** Despite Sobol+Owen achieving 96.7% lower discrepancy than MC, unique candidate counts were identical (0.20%). The hypothesis that low-discrepancy QMC improves integer-space candidate diversity was **falsified**.

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/z-sandbox.git
cd z-sandbox/experiments/theta_prime_qmc_falsification

# Install dependencies
pip install numpy scipy matplotlib

# Run complete experiment (2 minutes)
cd scripts
python3 mean_one_retiming.py      # Validate mean-one property
python3 discrepancy_test.py        # Compare MC vs Sobol D*
python3 qmc_factorization_analysis.py  # Main experiment
python3 bias_adaptive_example.py   # Generate plots

# View results
ls ../results/*.json
ls ../plots/*.png
```

---

## Experiment Structure

```
theta_prime_qmc_falsification/
├── EXECUTIVE_SUMMARY.md           # Results-first summary
├── EXPERIMENT_SETUP.md            # Detailed protocol (10-point charter)
├── CHARTER_COMPLIANCE.json        # Machine-readable compliance
├── README.md                      # This file
├── scripts/
│   ├── __init__.py
│   ├── mean_one_retiming.py              # Golden LCG retiming implementation
│   ├── qmc_factorization_analysis.py     # Main experiment runner
│   ├── discrepancy_test.py               # Star discrepancy comparison
│   ├── bias_adaptive_example.py          # Adaptive α visualization
│   └── generate_synthetic_semiprimes.py  # Semiprime generator
├── results/
│   ├── unique_candidates.json     # Raw trial data (250 entries)
│   ├── deltas.json                # Statistical analysis
│   └── discrepancy_results.json   # QMC quality metrics
└── plots/
    └── bias_adaptive_example.png  # Adaptive α demonstration
```

---

## Key Results

| Metric | MC Baseline | Sobol (α=0.20) | Lift |
|--------|-------------|----------------|------|
| **Unique Candidates %** | 0.20% | 0.20% | **0%** |
| **Discrepancy D\*** | 0.00873 | 0.00029 | **-96.7%** |
| **Factor Hit Rate** | 100% | 100% | 0% |
| **Mean Steps to Hit** | ~6 | ~6 | 0 |

**Conclusion:** Low discrepancy does NOT imply more unique candidates in integer-space problems.

---

## What Was Tested

### Hypothesis
> θ′-biased QMC (Sobol+Owen) with mean-one retiming (α=0.2) increases unique RSA factorization candidates vs MC baseline, especially for distant factors; Z=κ(n)·θ′(n,k) as sampling weight yields >5% lift without scaling noise.

### Test Configuration
- **N:** 899 = 29 × 31 (10-bit balanced semiprime)
- **Samples:** 5,000 candidates per trial
- **Replicates:** 50 per configuration (MC + 4 α values)
- **α sweep:** {0.05, 0.10, 0.15, 0.20}
- **k parameter:** 0.3 (θ′ resolution exponent)
- **Seed:** 42 (deterministic)

### Mechanisms Tested
1. **Sobol+Owen QMC:** Low-discrepancy sequence (D\* = O(log N / N))
2. **θ′(n,k) bias:** Golden-ratio modulation for distant-factor emphasis
3. **Mean-one retiming:** Deterministic interval perturbation (E[interval'] = base)
4. **Combined Z=κ(n)·θ′(n,k):** (In θ′ resampling step)

---

## What We Learned

### ✅ Validated
1. **Mean-one property:** Verified to <0.00002% error for all α ∈ [0.05, 0.20]
2. **Discrepancy advantage:** Sobol D\* 96.7% lower than MC (0.00029 vs 0.00873)
3. **Deterministic reproducibility:** Fixed seed produces identical results

### ❌ Falsified
1. **Hypothesis:** Sobol+Owen provides NO lift in unique candidate count (0%)
2. **Assumption:** Low discrepancy does NOT translate to integer-space diversity
3. **Bias effectiveness:** θ′(n,k) had zero measurable impact

### ⚠️ Limitations
1. **Test scale:** Only N=899 (10-bit) tested, NOT cryptographic sizes (256+ bits)
2. **Balanced factors:** p/q ≈ 1.07, NOT distant-factor scenario (untested)
3. **Single k:** k=0.3 fixed, no ablation study performed
4. **Zero variance:** All trials produced identical counts (no statistical power)

---

## Scripts Overview

### `mean_one_retiming.py`
Implements deterministic φ-based interval biasing:
```python
def golden_u64(slot: int) -> float:
    """64-bit golden LCG: u = (slot * G mod 2^64) / 2^64"""
    return ((slot * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF) / 2**64

def interval_biased(base_ms: float, slot: int, alpha: float = 0.2) -> float:
    """Mean-one retiming: E[interval'] = base"""
    u = golden_u64(slot)
    b = 1.0 + alpha * (2 * u - 1)  # Mean-one
    return base_ms * clip(b, 1-alpha, 1+alpha)
```

**Validation:** Generates 100K intervals, verifies mean = base ± 0.01%

### `qmc_factorization_analysis.py`
Main experiment runner:
1. Generates QMC/MC candidates around √N
2. Applies optional θ′(n,k=0.3) bias via resampling
3. Applies optional mean-one retiming (α sweep)
4. Counts unique candidates, factor hits, steps-to-hit
5. Bootstraps 95% CIs (n=2000 resamples)
6. Performs paired t-tests

**Output:** `results/unique_candidates.json`, `results/deltas.json`

### `discrepancy_test.py`
Computes star discrepancy D\*(P) for MC vs Sobol sequences:
```
D*(P) = max_{t∈[0,1]} |#{p ≤ t}/N - t|
```

**Result:** Sobol D\* < 0.001, MC D\* ≈ 0.009 (96.7% improvement)

### `bias_adaptive_example.py`
Demonstrates adaptive α based on local curvature κ(n):
```python
α(n) = α_base * (1 + scale_factor * κ(n))
```

**Output:** `plots/bias_adaptive_example.png` (3-panel visualization)

### `generate_synthetic_semiprimes.py`
Generates balanced/moderate/large-separation semiprimes for testing.  
**Note:** Used for demonstration; main experiment uses hardcoded N=899.

---

## Reproducibility

### Full Run
```bash
cd experiments/theta_prime_qmc_falsification/scripts
python3 mean_one_retiming.py && \
python3 discrepancy_test.py && \
python3 qmc_factorization_analysis.py && \
python3 bias_adaptive_example.py
```
**Expected Runtime:** ~2 minutes  
**Expected Output:** All tests PASS, results in `../results/`, plots in `../plots/`

### Validation Checks
```bash
# 1. Mean-one property passes
python3 mean_one_retiming.py | grep "✓ PASS" | wc -l
# Expected: 4 (one per α)

# 2. Sobol discrepancy < MC
python3 -c "import json; d=json.load(open('../results/discrepancy_results.json')); print(d['ratio'])"
# Expected: <0.1

# 3. Zero lift confirmed
python3 -c "import json; d=json.load(open('../results/deltas.json')); print([d['sobol_configs'][k]['lift_pct'] for k in d['sobol_configs']])"
# Expected: [0.0, 0.0, 0.0, 0.0]
```

---

## Next Steps

### Immediate Follow-ups
1. **Scale to 64-bit:** Test N ≈ 2^64 to check if pattern holds
2. **Distant factors:** Generate p/q ≈ 100 semiprimes to test θ′ bias claim
3. **Ablate k parameter:** Sweep k ∈ [0.2, 0.5] to find optimal (if any)
4. **Combined weight:** Test Z = κ(n) · θ′(n,k) directly (not via resampling)

### Research Questions
1. Why does low discrepancy NOT improve integer-space diversity?
2. Is there a QMC variant that DOES help (Halton, Hammersley, etc.)?
3. Can candidate quality (factor proximity) improve even if count doesn't?
4. What is computational overhead of Sobol+Owen vs MC for this task?

---

## Mission Charter Compliance

This experiment adheres to the z-sandbox 10-point Mission Charter:

1. ✅ **First Principles:** Z=A(B/c), κ(n), θ′(n,k), mean-one retiming defined
2. ✅ **Ground Truth:** N=899 (29×31), executed 2025-11-19, full provenance
3. ✅ **Reproducibility:** Fixed seed=42, exact commands, 2-min runtime
4. ✅ **Failure Knowledge:** 4 failure modes documented with mitigations
5. ✅ **Constraints:** Academic research, honest negative result reporting
6. ✅ **Context:** Research question, stakeholders, motivation clear
7. ✅ **Models & Limits:** 3 models with assumptions (1 falsified)
8. ✅ **Interfaces:** Commands, I/O paths, no secrets
9. ⚠️ **Calibration:** Only α swept; k=0.3 adopted but not tuned
10. ✅ **Purpose:** Hypothesis test with success criteria (FALSIFIED)

**Compliance Status:** FULL (with calibration note)

Validation:
```bash
python3 ../../../tools/validate_charter.py EXPERIMENT_SETUP.md
# Expected: PASS with 1 warning (calibration)
```

---

## Contact

**Questions:** File issue in z-sandbox repository  
**Experiment Owner:** Z-Sandbox Agent  
**Project Owner:** Big D / DAL III

---

## License

Inherits z-sandbox repository license.

---

**README Version:** 1.0.0  
**Last Updated:** 2025-11-19
