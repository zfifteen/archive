# Quasi-Monte Carlo Methods in Integer Factorization: Hypothesis Test

**Experiment ID:** qmc_factorization_test  
**Author:** GitHub Copilot Agent  
**Date:** December 26, 2025  
**Status:** In Progress

---

## Executive Summary

This experiment tests the hypothesis that Quasi-Monte Carlo (QMC) methods, specifically when integrated with geometric approaches and the Z-Framework axioms, can provide computational advantages for integer factorization compared to standard Monte Carlo methods.

---

## Hypothesis

**Title:** Novel Integration of Quasi-Monte Carlo Methods in Geometric Approaches to Integer Factorization

**Statement:** QMC methods (e.g., Sobol sequences, Owen scrambling) combined with Geodesic Validation Assault (GVA) and Riemannian geometry on high-dimensional tori enable lower-variance stochastic searches for factors of RSA moduli compared to standard Monte Carlo approaches.

---

## Experimental Design

### Test Components

1. **QMC Sequence Generators**
   - Sobol sequences
   - Halton sequences  
   - Anosov automorphism-based sequences (from Selberg framework)

2. **Factorization Methods**
   - GVA geometric approach with QMC sampling
   - GVA geometric approach with standard Monte Carlo
   - Baseline factorization (trial division for validation)

3. **Test Cases**
   - Small semiprimes (2-4 digits)
   - Medium semiprimes (6-8 digits)
   - Large semiprimes (10-12 digits)

4. **Metrics**
   - Convergence rate (iterations to factor)
   - Variance in factor search
   - Star discrepancy of sampling sequences
   - Success rate across multiple runs

### Z-Framework Integration

The experiment will leverage existing Z-Framework axioms:
- κ(n) = d(n) · ln(n+1) / e² (curvature metric)
- Geodesic transformations on toroidal embeddings
- Anosov matrix selection based on Selberg zeta moments

---

## Implementation Plan

See `qmc_factorization.py` for the complete implementation with incremental development protocol.

---

## Expected Outcomes

If the hypothesis is TRUE:
- QMC methods should show 20-50% lower variance in factor searches
- Convergence rate should improve for higher-entropy Anosov matrices
- Star discrepancy should correlate with factorization efficiency

If the hypothesis is FALSE:
- No significant difference between QMC and MC variance
- Random sampling performs comparably to low-discrepancy sequences
- Geometric structure doesn't provide computational advantage

---

## Dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Run full experimental suite
python qmc_factorization.py --full

# Run quick validation
python qmc_factorization.py --quick

# Generate visualizations
python qmc_factorization.py --visualize
```

---

## Related Work

- **Selberg-Ruelle Framework:** `../selberg-tutorial/`
- **Z-Framework Axioms:** `../001/kk_semiprime_test.py`
- **GVA Background:** Referenced in Selberg tutorial README

---

## References

1. Wikipedia: Quasi-Monte Carlo method - https://en.wikipedia.org/wiki/Quasi-Monte_Carlo_method
2. arXiv:2502.03644v1 - QMC convergence and error bounds
3. z-sandbox repository (referenced) - Z-Framework and GVA methods

---

**Status:** Implementation in progress following incremental coder protocol
