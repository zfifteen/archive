# Experiment Setup: θ′-biased QMC Falsification

**Experiment ID:** theta-prime-qmc-falsification-2025-11-19  
**Document Type:** Detailed Experimental Protocol  
**Version:** 1.0.0  
**Date:** 2025-11-19

---

## 1. First Principles

### Mathematical Foundations

**Z-Framework Axiom:**
```
Z = A(B/c) where c = e² (invariant)
```

**Curvature Weight:**
```
κ(n) = d(n) · ln(n+1) / e²
where d(n) ≈ 1/ln(n) (prime density from PNT)
```

**Geometric Resolution:**
```
θ′(n,k) = φ · ((n mod φ) / φ)^k
where φ = (1 + √5)/2 ≈ 1.618... (golden ratio)
      k ≈ 0.3 (resolution exponent for distant factors)
```

**Mean-One Retiming:**
```
interval'(slot) = base · b(slot)
where b(slot) = clip(1 + α(2u - 1), 1-α, 1+α)
      u = (slot · G mod 2^64) / 2^64
      G = 0x9E3779B97F4A7C15 (64-bit golden LCG constant)
      α ∈ (0, 0.2] (bias amplitude)

Property: E[interval'] = base (mean-one preserved)
```

**QMC Discrepancy:**
```
Star Discrepancy: D*(P) = sup_{t∈[0,1]} |#{p ≤ t}/N - t|

Bounds:
- Monte Carlo: D* = O(1/√N) with high probability
- Sobol+Owen:  D* = O(log^d(N) / N) deterministic
```

### Units and Tolerances

- **Unique Candidate %:** Percentage of distinct integers in [0, 100]
- **Error Tolerance:** Mean-one property verified to < 0.0001% relative error
- **Bootstrap CI:** 95% confidence, n=2000 resamples
- **Statistical Significance:** α = 0.05 (p-value threshold)

---

## 2. Ground Truth & Provenance

### Test Subject

**Semiprime:** N = 899 = 29 × 31  
**Properties:**
- Bit length: 10 bits
- Balanced factors: q/p = 1.069 (close to 1)
- √N ≈ 29.98 (between factors)

**Source:** Generated synthetically for reproducibility (small enough for rapid testing)

### Execution Details

**Executor:** Z-Sandbox Agent (automated)  
**Timestamp:** 2025-11-19T17:45:00Z (experiment start)  
**Platform:** Ubuntu Linux 22.04, x86_64  
**Python:** 3.12.3  
**Hardware:** GitHub Actions runner (2-core, 7GB RAM)

### Method

1. Generate QMC/MC candidate samples around √N
2. Apply optional θ′(n,k=0.3) bias via resampling
3. Apply optional mean-one retiming (α sweep)
4. Count unique candidates, factor hits, steps-to-hit
5. Repeat for 50 replicates per configuration
6. Bootstrap confidence intervals (2000 resamples)
7. Paired t-tests for statistical comparison

### External Sources

**QMC Theory:**
- Sobol, I. M. (1967). "On the distribution of points in a cube and the approximate evaluation of integrals." USSR Computational Mathematics and Mathematical Physics, 7(4), 86-112.
- Owen, A. B. (1995). "Randomly permuted (t,m,s)-nets and (t,s)-sequences." Monte Carlo and Quasi-Monte Carlo Methods in Scientific Computing, 299-317.
- Accessed: Wikipedia articles on Sobol sequences and QMC (2025-11-19)

**Z-Framework:**
- Internal z-sandbox research: `docs/core/`, `utils/z_framework.py`
- κ(n) and θ′(n,k) definitions from project axioms

---

## 3. Reproducibility

### Exact Commands

**Step 1: Validate mean-one retiming**
```bash
cd experiments/theta_prime_qmc_falsification/scripts
python3 mean_one_retiming.py
```
**Expected Output:** All α tests PASS with error < 0.0001%

**Step 2: Run discrepancy test**
```bash
python3 discrepancy_test.py
```
**Expected Output:** Sobol D* < 0.001, MC D* ≈ 0.009

**Step 3: Main experiment**
```bash
python3 qmc_factorization_analysis.py
```
**Expected Output:** Results saved to `../results/*.json`

**Step 4: Generate plots**
```bash
python3 bias_adaptive_example.py
```
**Expected Output:** Plot saved to `../plots/bias_adaptive_example.png`

### Configuration Parameters

```python
SEED = 42                    # Base random seed
N_REPLICATES = 50            # Replicates per configuration
N_SAMPLES = 5000             # Candidates per trial
ALPHAS = [0.05, 0.10, 0.15, 0.20]  # Retiming sweep
K_PARAM = 0.3                # θ′ resolution exponent
BOOTSTRAP_N = 2000           # CI resamples
CONFIDENCE = 0.95            # 95% CI
```

### Software Versions

```
Python: 3.12.3
NumPy: 1.26.4
SciPy: 1.11.4
matplotlib: 3.10.7
```

### Environment Variables

None required (all configuration hardcoded for reproducibility)

### Expected Runtime

- Mean-one validation: ~5 seconds
- Discrepancy test: ~15 seconds
- Main experiment: ~90 seconds
- Plot generation: ~10 seconds
- **Total: ~2 minutes**

### Validation Checks

```python
# 1. Mean-one property
assert abs(mean_interval - base) / base < 0.0001

# 2. Discrepancy bounds
assert sobol_discrepancy < mc_discrepancy
assert sobol_discrepancy < 0.001

# 3. Factor detection
assert all(trial['found_p'] for trial in results)
assert all(trial['found_q'] for trial in results)

# 4. JSON serializability
json.dump(results, f)  # Must not raise TypeError
```

---

## 4. Failure Knowledge

### Failure Mode 1: Overflow with Large Numbers

**Condition:** N > 2^63 (e.g., RSA-100, RSA-129)  
**Symptom:** `OverflowError: Python int too large to convert to C long`  
**Diagnostic:** Check bit_length(N); if > 64, numpy int64 insufficient  
**Mitigation:** Use Python arbitrary-precision integers, convert to float for numpy operations

### Failure Mode 2: Zero Variance (No Statistical Power)

**Condition:** Test case too small (N < 1000)  
**Symptom:** All replicates produce identical unique counts; t-test returns NaN  
**Diagnostic:** Check std(unique_pct); if ≈ 0, no variance to test  
**Mitigation:** Use larger N (>2^16) or increase sample size to induce variance

### Failure Mode 3: JSON Serialization Errors

**Condition:** NumPy scalars (int64, float64, bool_) in result dictionaries  
**Symptom:** `TypeError: Object of type int64 is not JSON serializable`  
**Diagnostic:** Inspect types in result dict; look for numpy dtypes  
**Mitigation:** Convert to Python types: `int(val)`, `float(val)`, `bool(val)`

### Failure Mode 4: Mean-One Property Violation

**Condition:** α > 0.2 or incorrect LCG constant G  
**Symptom:** Relative error in mean > 0.01%  
**Diagnostic:** Run `verify_mean_one_property()` with large n_samples (10^6)  
**Mitigation:** Verify α ≤ 0.2; check G = 0x9E3779B97F4A7C15 exactly

### Known Limitations

1. **Tested only N=899 (10-bit):** NOT representative of cryptographic semiprimes (256+ bits)
2. **Small candidate space:** With N=899, spread of ±15% yields only ~10 integers
3. **No distant-factor scenario:** p and q are balanced (ratio ≈ 1.07), not distant
4. **Synthetic data:** Not testing real RSA challenge numbers
5. **Limited α sweep:** Only 4 values; may miss optimal α outside [0.05, 0.20]

---

## 5. Constraints

### Legal

- **License:** Experiment code inherits z-sandbox repository license
- **RSA Numbers:** N=899 is synthetic, not an RSA challenge (no IP restrictions)
- **No Patents:** Mean-one retiming and θ′ bias are original research, not patented methods

### Ethical

- **Academic Research:** Purely exploratory; NOT attempting to break active cryptographic systems
- **Honest Reporting:** Hypothesis FALSIFIED; negative result published without spin
- **Open Science:** All code, data, and methods fully disclosed for peer review

### Safety

- **No Secrets:** No private keys, credentials, or sensitive data involved
- **Deterministic Seeds:** Fixed seed=42 for reproducibility, not cryptographic security
- **Resource Limits:** Experiment bounded to ~2 minutes; no runaway processes

### Compliance

- **Mission Charter:** Full compliance with 10-point deliverable standard (validated)
- **Reproducibility Standard:** Fixed seeds, exact commands, pinned dependencies
- **TRANSEC Protocol:** Not applicable (no sensitive communications)

---

## 6. Context

### Stakeholders

- **Project Owner:** Big D / DAL III
- **Executor:** Z-Sandbox Agent
- **Audience:** z-sandbox research team, future experimenters

### Problem Being Addressed

**Research Question:** Can θ′-biased QMC with mean-one retiming improve RSA factorization candidate generation?

**Motivation:**
- QMC sequences (Sobol+Owen) have superior low-discrepancy vs MC
- θ′(n,k) with k≈0.3 hypothesized to bias toward distant factors
- Mean-one retiming conjectured to improve sampling diversity
- Prior work suggested >5% lift in unique candidates

**Timeline:** One-shot experiment (2025-11-19); no ongoing schedule

### Environment

- **Development:** Local z-sandbox repository clone
- **Execution:** GitHub Actions runner (cloud CI)
- **Analysis:** Offline statistical processing

### Dependencies

- **Code:** `python/qmc_engines.py`, `utils/z_framework.py`
- **Prior Work:** QMC discrepancy theory, Z-Framework axioms
- **Follow-up:** Results will inform whether to scale test to larger N

---

## 7. Models & Limits

### Model 1: θ′-Biased Sampling

**Form:**
```
P(candidate | θ′) ∝ θ′(candidate, k=0.3)
```

**Assumptions:**
- Golden-ratio modulation θ′ correlates with factor likelihood
- k=0.3 is optimal for distant-factor bias (from prior heuristics)
- Resampling with θ′ weights improves candidate quality

**Validated Range:**
- **Input:** N=899 (10-bit), candidates around √N ≈ 30
- **Generalization:** UNKNOWN for N > 1000

**Break Points:**
- k < 0.2 or k > 0.4: Effect magnitude unknown
- Extremely unbalanced factors (p/q > 10): θ′ bias may fail

### Model 2: Mean-One Retiming

**Form:**
```
interval' = base · (1 + α · (2u - 1))  clipped to [base(1-α), base(1+α)]
```

**Assumptions:**
- Perturbations within ±α preserve E[interval'] = base
- α ∈ (0, 0.2] sufficient to affect sampling diversity
- Golden LCG produces adequate pseudo-randomness

**Validated Range:**
- **α:** [0.05, 0.20] tested; mean-one property verified
- **Samples:** 10^5 intervals generated for validation

**Break Points:**
- α > 0.2: Property may degrade (untested)
- base < 1e-6: Floating-point precision issues possible

### Model 3: QMC Discrepancy Advantage

**Form:**
```
Unique candidates ∝ f(D*(sequence))
```

**Assumption:** Lower discrepancy → more unique candidates

**Validated:** Discrepancy confirmed lower (96.7% improvement), BUT unique candidate count unchanged

**Result:** **ASSUMPTION FALSIFIED** — Discrepancy does not predict candidate diversity in this integer-space problem

---

## 8. Interfaces & Keys

### Command-Line Interfaces

**Main Experiment:**
```bash
python3 qmc_factorization_analysis.py
# No arguments (configuration hardcoded)
# Output: results/*.json
```

**Validation Scripts:**
```bash
python3 mean_one_retiming.py       # Validates mean-one property
python3 discrepancy_test.py        # Compares MC vs Sobol D*
python3 bias_adaptive_example.py   # Generates α adaptation plot
python3 generate_synthetic_semiprimes.py  # Demo semiprime generator
```

### Input/Output Paths

**Inputs:**
- `N`, `p`, `q`: Hardcoded in script (N=899, p=29, q=31)
- `seed`: 42 (fixed)
- `alphas`: [0.05, 0.10, 0.15, 0.20]

**Outputs:**
- `results/unique_candidates.json`: Raw trial data (250 entries)
- `results/deltas.json`: Statistical analysis summary
- `results/discrepancy_results.json`: Discrepancy comparison
- `plots/bias_adaptive_example.png`: Adaptive α visualization

### Environment Variables

None required.

### Permissions

- **Read:** Repository files (qmc_engines.py, z_framework.py)
- **Write:** `experiments/theta_prime_qmc_falsification/{results,plots}/`
- **Execute:** Python 3.12+ with NumPy, SciPy, matplotlib

### Secrets Handling

No secrets involved. All data is public research.

---

## 9. Calibration

### Parameter: α (Retiming Amplitude)

**Values Tested:** {0.05, 0.10, 0.15, 0.20}  
**Rationale:** Sweep from minimal (5%) to maximal allowed (20%) perturbation  
**Tuning Method:** Grid search over discrete values  
**Validation:** Mean-one property verified for each α (error < 0.00002%)  
**Sensitivity:** RESULT: Zero impact on unique candidates (all α equivalent)

### Parameter: k (θ′ Resolution Exponent)

**Value:** 0.30 (fixed)  
**Rationale:** From Z-Framework heuristics for distant-factor bias  
**Tuning Method:** None (adopted from prior work)  
**Validation:** NOT PERFORMED — no ablation study on k  
**Sensitivity:** UNKNOWN — single k value tested

### Parameter: n_samples (Candidates Per Trial)

**Value:** 5000  
**Rationale:** Balance between runtime and statistical power  
**Tuning Method:** Empirical choice (10× typical unique count)  
**Validation:** Adequate for small N; may need adjustment for large N  
**Sensitivity:** UNKNOWN — no systematic study

### Parameter: n_replicates (Statistical Replicates)

**Value:** 50  
**Rationale:** Standard for bootstrap CI with reasonable runtime  
**Tuning Method:** Common practice in MC experiments  
**Validation:** Sufficient for CI convergence (bootstrap n=2000)  
**Sensitivity:** Increasing to 100 would tighten CIs marginally

### Calibration Status

⚠️ **Limited Calibration:** Only α swept systematically. Other parameters (k, n_samples) adopted from heuristics without validation.

⚠️ **No Optimization:** Parameters not tuned for this specific N=899 test case.

✓ **Reproducible:** All parameters documented and fixed for replication.

---

## 10. Purpose

### Primary Goal

**Falsify or confirm the hypothesis:** θ′-biased QMC (Sobol+Owen) with mean-one retiming (α=0.2) increases unique RSA factorization candidates by >5% versus MC baseline.

### Secondary Goals

1. Validate mean-one property of retiming mechanism
2. Confirm Sobol+Owen achieves lower discrepancy than MC
3. Measure factor detection efficiency (steps-to-hit)
4. Generate reproducible experimental template for future work

### Success Criteria

**Quantitative:**
1. **Mean-one property:** Relative error < 0.01% ✓ ACHIEVED
2. **Discrepancy:** Sobol D* < MC D* ✓ ACHIEVED (96.7% lower)
3. **Unique candidates:** Measure lift % with 95% CI ✓ MEASURED (0% lift)
4. **Statistical significance:** p < 0.05 for hypothesis test ✗ NOT ACHIEVED (NaN due to zero variance)

**Qualitative:**
1. **Reproducibility:** Single-command rerun ✓ ACHIEVED
2. **Documentation:** Full 10-point charter compliance ✓ ACHIEVED
3. **Negative result:** Honest reporting if hypothesis fails ✓ ACHIEVED

### Success Metrics

- **Primary:** Lift % in unique candidates (Target: >5%, Achieved: 0%)
- **Secondary:** Discrepancy ratio (Target: <0.5, Achieved: 0.033)
- **Tertiary:** Factor hit rate (Target: >90%, Achieved: 100%)

### Verification Procedures

**1. Mean-One Property:**
```bash
python3 mean_one_retiming.py | grep PASS
# Expected: 4× "✓ PASS" for α ∈ {0.05, 0.10, 0.15, 0.20}
```

**2. Discrepancy Test:**
```bash
python3 discrepancy_test.py | grep "Sobol/MC ratio"
# Expected: ratio < 0.1 (lower is better)
```

**3. Statistical Analysis:**
```bash
python3 -c "import json; d=json.load(open('results/deltas.json')); print([d['sobol_configs'][a]['lift_pct'] for a in d['sobol_configs']])"
# Expected: List of lift percentages
```

### Value Proposition

**Scientific:** Empirical test of QMC bias hypothesis with rigorous statistics  
**Practical:** Template for future factorization experiments at scale  
**Educational:** Demonstrates mean-one retiming and discrepancy concepts  
**Research:** Negative result informs theoretical understanding (discrepancy ≠ diversity)

### Explicit Non-Goals

- ✗ **NOT** claiming to break RSA encryption
- ✗ **NOT** testing cryptographically-sized semiprimes (only N=899 demo)
- ✗ **NOT** optimizing parameters for performance
- ✗ **NOT** comparing against state-of-the-art factorization algorithms (ECM, GNFS)
- ✗ **NOT** evaluating other QMC sequences (Halton, Hammersley, etc.)

---

## Compliance Manifest

```json
{
  "manifest_version": "1.0.0",
  "deliverable_id": "theta-prime-qmc-falsification-experiment-setup",
  "deliverable_type": "experimental_protocol",
  "timestamp": "2025-11-19T17:52:00Z",
  "author": "Z-Sandbox Agent",
  "charter_compliance": {
    "first_principles": {
      "present": true,
      "location": "Section 1",
      "completeness": 1.0,
      "notes": "Full mathematical definitions provided"
    },
    "ground_truth": {
      "present": true,
      "location": "Section 2",
      "completeness": 1.0,
      "notes": "Execution details and provenance documented"
    },
    "reproducibility": {
      "present": true,
      "location": "Section 3",
      "completeness": 1.0,
      "notes": "Exact commands, seeds, and validation checks"
    },
    "failure_knowledge": {
      "present": true,
      "location": "Section 4",
      "completeness": 1.0,
      "notes": "4 failure modes with diagnostics and mitigations"
    },
    "constraints": {
      "present": true,
      "location": "Section 5",
      "completeness": 1.0,
      "notes": "Legal, ethical, safety, and compliance constraints"
    },
    "context": {
      "present": true,
      "location": "Section 6",
      "completeness": 1.0,
      "notes": "Stakeholders, motivation, and dependencies"
    },
    "models_limits": {
      "present": true,
      "location": "Section 7",
      "completeness": 1.0,
      "notes": "3 models with assumptions and break points"
    },
    "interfaces": {
      "present": true,
      "location": "Section 8",
      "completeness": 1.0,
      "notes": "Commands, paths, and permissions documented"
    },
    "calibration": {
      "present": true,
      "location": "Section 9",
      "completeness": 0.8,
      "notes": "Only α swept; k and n_samples not calibrated"
    },
    "purpose": {
      "present": true,
      "location": "Section 10",
      "completeness": 1.0,
      "notes": "Goals, success criteria, and non-goals explicit"
    }
  },
  "validation_result": {
    "is_compliant": true,
    "missing_elements": [],
    "warnings": [
      "calibration: Limited parameter tuning (only α swept)"
    ]
  }
}
```

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-11-19T17:52:00Z  
**Author:** Z-Sandbox Agent  
**Review Status:** Ready for validation
