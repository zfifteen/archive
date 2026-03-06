# Cranley-Patterson QMC Variance Reduction: Experiment

**Status:** ✗ HYPOTHESIS FALSIFIED (High Confidence)  
**Date:** 2025-11-19  
**Location:** `experiments/cranley_patterson_qmc_variance/`

## Quick Summary

This experiment tested whether Cranley-Patterson rotations enhance θ′(n,k)-biased Sobol sequences for RSA factorization by reducing candidate variance.

**Verdict: FALSIFIED**

The Cranley-Patterson approach provides:
- ✗ No meaningful variance reduction (0.5-0.9%, claimed 30-80%)
- ✗ No statistical significance (all p > 0.05)
- ✓ No computational overhead (< 5% in all cases)

## Directory Structure

```
experiments/cranley_patterson_qmc_variance/
├── README.md                       # This file
├── SUMMARY.md                      # Executive summary with crystal-clear verdict
├── docs/
│   ├── THEORY.md                   # Cranley-Patterson mathematical foundation
│   └── EXPERIMENT_REPORT.md        # Full charter-compliant report
├── src/
│   ├── baseline_profile.py         # Baseline θ′(n,k)-biased Sobol profiler
│   ├── cranley_patterson.py        # CP rotation implementation
│   ├── comparative_analysis.py     # Statistical comparison & verdict
│   └── visualize_results.py        # Plot generation
├── data/                           # (empty - test cases hardcoded)
└── results/
    ├── baseline_*.json             # Baseline profiles
    ├── cp_static_*.json            # CP-Static profiles
    ├── comparative_analysis.json   # Comparison & verdict
    ├── comparison_plot.png         # Main results visualization
    └── variance_distributions.png  # Distribution histograms
```

## Quick Start

### Prerequisites
```bash
pip install numpy scipy matplotlib
```

### Run Experiment
```bash
cd experiments/cranley_patterson_qmc_variance/src

# Step 1: Profile baseline θ′(n,k)-biased Sobol
python3 baseline_profile.py

# Step 2: Profile Cranley-Patterson rotated Sobol
python3 cranley_patterson.py

# Step 3: Run comparative analysis
python3 comparative_analysis.py

# Step 4: Generate visualizations
python3 visualize_results.py
```

### View Results
```bash
cat ../results/comparative_analysis.json | python3 -m json.tool | grep -A5 '"overall_verdict"'
# Output: "HYPOTHESIS DEFINITIVELY FALSIFIED"
```

## Visualization

![Comparison Plot](results/comparison_plot.png)

The visualization shows:
- **Top Left**: Variance reduction factors - all FAR below claimed 1.3× minimum
- **Top Right**: p-values - all above 0.05 significance threshold (not significant)
- **Bottom Left**: Timing overhead - minimal (all under 5%)
- **Bottom Right**: Summary verdict with falsification criteria

## Key Findings

### Variance Analysis
| Challenge | Baseline Var | CP-Static Var | Reduction | p-value | Significant? |
|-----------|--------------|---------------|-----------|---------|--------------|
| RSA-100   | 0.01908      | 0.01900       | 1.005×    | 0.7722  | ✗ No         |
| RSA-129   | 0.05541      | 0.05490       | 1.009×    | 0.5204  | ✗ No         |
| RSA-155   | 3.27e+41     | 3.27e+41      | 1.000×    | 1.0000  | ✗ No         |

**Conclusion:** No significant variance reduction. Claimed 1.3-1.8× reduction NOT observed.

### Timing Comparison
| Challenge | Baseline (ms) | CP-Static (ms) | Overhead |
|-----------|---------------|----------------|----------|
| RSA-100   | 0.84 ± 0.09   | 0.78 ± 0.09    | 0.935×   |
| RSA-129   | 0.91 ± 0.08   | 0.92 ± 0.08    | 1.013×   |
| RSA-155   | 0.80 ± 0.08   | 0.83 ± 0.08    | 1.040×   |

**Conclusion:** Minimal overhead (< 5%), but no benefit to justify even this small cost.

### Falsifiability Criteria
1. ✗ **Variance Reduction < 1.3×**: 1.000-1.009× vs. claimed 1.3× (FAILED)
2. ✗ **No Significance**: all p > 0.05 (FAILED)
3. ✓ **Overhead < 2.0×**: 0.935-1.040× (PASSED, but irrelevant given failures)

**All falsification criteria met → HYPOTHESIS DEFINITIVELY FALSIFIED**

## Theoretical Background

### What Was Tested
Cranley-Patterson (1976) proposed random shift randomization for QMC:
```
u'_i = (u_i + r) mod 1, where r ~ U[0,1]^d
```

**Hypothesis:** This randomization would:
1. Reduce variance in factor candidate distributions
2. Improve convergence to true factors
3. Enhance θ′(n,k) geometric biasing

### Why It Failed
1. **Wrong problem domain:** CP is for continuous integration, not discrete factorization
2. **Already randomized:** Owen scrambling in Sobol already provides variance reduction
3. **No factor structure:** Random rotations don't encode prime factorization properties
4. **Mismatch in variance sources:** Integration variance ≠ factorization candidate variance

**Insight:** QMC variance reduction for numerical integration DOES NOT transfer to discrete cryptographic optimization.

## Documentation

### Full Reports
- **Theory:** `docs/THEORY.md` - Mathematical foundations of Cranley-Patterson rotations
- **Results:** `docs/EXPERIMENT_REPORT.md` - Charter-compliant 10-point report with full analysis
- **Summary:** `SUMMARY.md` - Executive summary with clear verdict

### Mission Charter Compliance
This experiment follows the z-sandbox **10-Point Mission Charter**:
1. ✓ First Principles (QMC theory, CP rotations, θ′(n,k) bias)
2. ✓ Ground Truth & Provenance (named RSA challenges, sources, timestamps)
3. ✓ Reproducibility (commands, configs, seeds)
4. ✓ Failure Knowledge (3 failure modes, diagnostics, postmortem)
5. ✓ Constraints (legal, ethical, safety - only named RSA challenges)
6. ✓ Context (who, what, when, where, why)
7. ✓ Models & Limits (assumptions tested and falsified)
8. ✓ Interfaces & Keys (CLIs, I/O paths, no secrets)
9. ✓ Calibration (parameters documented, sensitivity noted)
10. ✓ Purpose (goals, metrics, falsification criteria pre-specified)

See `docs/EXPERIMENT_REPORT.md` for full compliance manifest.

## Reproducibility

### Random Seed
All experiments use `seed=42` for reproducible Sobol sequence generation and Owen scrambling.

### Test Cases (Named RSA Challenges Only)
- **RSA-100** (330-bit): N = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
- **RSA-129** (426-bit): N = 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541
- **RSA-155** (512-bit): N = 1094173864157052742180970732204035761200373294544920599091384213147635041906079937988

All factors are publicly known. Tests measure variance and timing, not factorization success.

### Environment
- **Python**: 3.12
- **numpy**: 2.3.5
- **scipy**: 1.16.3
- **matplotlib**: 3.10.7
- **Platform**: Linux x86_64 (GitHub Actions CI)

### Configuration
- **Trials:** 30 per treatment (sufficient for t-test, α=0.05, power=0.8)
- **Candidates:** 1000 per trial (standard QMC batch size)
- **k parameter:** 0.3 (standard for θ′(n,k) distant-factor bias)
- **Scrambling:** Owen scrambling enabled (baseline Sobol)
- **Rotation:** Static random (r ~ U[0,1], seed=42)

## Lessons Learned

### Positive Outcomes
1. ✓ Rigorous empirical falsification of cross-domain claim
2. ✓ Ruled out unproductive research direction
3. ✓ Demonstrated importance of domain-specific validation
4. ✓ Established that integration QMC ≠ factorization QMC

### Negative Result ≠ Failure
This is a **successful falsification**, not a failed experiment. Negative results have scientific value:
- Prevents wasted effort on CP rotations for RSA
- Shows that mathematical elegance (CP theory) ≠ practical benefit
- Provides falsification template for future QMC enhancement claims
- Highlights need for domain-specific benchmarking

### Future Directions (Not CP Rotations)
Instead of generic QMC enhancements, consider:
- **Domain-specific bias:** θ′(n,k) and κ(n) already encode factorization structure
- **Algebraic methods:** Lattice reduction, elliptic curves
- **Hybrid approaches:** QMC + deterministic search
- **Better distance metrics:** Factorization-aware similarity measures

## References

### Internal
- **Z-Framework Core:** `docs/core/`
- **QMC Engines:** `python/qmc_engines.py`
- **θ′(n,k) Bias:** `utils/z_framework.py`
- **Mission Charter:** `MISSION_CHARTER.md`

### External
- Cranley, R., & Patterson, T. N. L. (1976). Randomization of number theoretic methods for multiple integration. *SIAM Journal on Numerical Analysis*, 13(6), 904-914.
- Owen, A. B. (1995). Randomly permuted (t,m,s)-nets and (t,s)-sequences. In *Monte Carlo and Quasi-Monte Carlo Methods in Scientific Computing* (pp. 299-317). Springer.
- Sobol', I. M. (1967). On the distribution of points in a cube and the approximate evaluation of integrals. *USSR Computational Mathematics and Mathematical Physics*, 7(4), 86-112.

---

**Conclusion:** Cranley-Patterson rotations do **NOT** enhance RSA factorization QMC. The hypothesis is definitively falsified with HIGH confidence across all three RSA challenges tested. Baseline θ′(n,k)-biased Sobol remains the recommended approach.
