# Cranley-Patterson Rotations: Mathematical Theory

**Document Type:** Theoretical Foundation  
**Date:** 2025-11-19  
**Status:** Reference for falsified hypothesis

## Overview

Cranley-Patterson (CP) rotations are a variance reduction technique for Quasi-Monte Carlo (QMC) integration introduced by Cranley & Patterson (1976). This document explains the mathematical foundation, intended applications, and why the technique fails when applied to RSA factorization.

---

## Mathematical Foundation

### Standard QMC Integration

QMC methods approximate integrals using low-discrepancy sequences:

```
I = ∫[0,1]^d f(x) dx ≈ (1/N) ∑_{i=1}^N f(u_i)
```

where `u_i` is a low-discrepancy sequence (e.g., Sobol, Halton, Niederreiter).

**Key Property:** QMC has error O(N^(-1) (log N)^d), better than Monte Carlo's O(N^(-1/2)).

### Variance Estimation Problem

**Issue:** QMC is deterministic, so standard variance estimation (σ²/N) doesn't apply.

**Solution:** Randomized QMC (RQMC) introduces controlled randomness to enable variance estimation while preserving low-discrepancy benefits.

### Cranley-Patterson Rotation

**Definition:** Random shift modulo 1:

```
u'_i = (u_i + r) mod 1
```

where:
- `u_i ∈ [0,1]^d` is the i-th point from a QMC sequence
- `r ~ Uniform[0,1]^d` is a random shift vector (fixed per replicate)
- `mod 1` applies component-wise: `(x_1, x_2, ..., x_d) mod 1 = (x_1 mod 1, x_2 mod 1, ..., x_d mod 1)`

**Properties:**
1. **Preservation:** Rotated sequence `{u'_i}` remains a covering set of [0,1]^d
2. **Unbiasedness:** E[f(u'_i)] = ∫[0,1]^d f(x) dx (for periodic f)
3. **Variance reduction:** Var[I_CP] ≤ Var[I_MC] under periodic smoothness conditions

### Theoretical Variance Reduction

For periodic functions with sufficient smoothness:

```
Var[I_CP] = O(N^(-2) (log N)^(2d))
```

compared to Monte Carlo:

```
Var[I_MC] = O(N^(-1))
```

**Improvement:** Variance reduction factor of O(N) for smooth periodic integrands.

---

## Original Application Domain: Numerical Integration

### Intended Use Cases

1. **Financial Derivatives Pricing**
   - High-dimensional integrals (d=10-1000)
   - Smooth payoff functions
   - Continuous probability distributions

2. **Physics Simulations**
   - Particle transport
   - Radiative transfer
   - Quantum Monte Carlo

3. **Bayesian Inference**
   - Posterior expectation estimation
   - High-dimensional parameter spaces

### Success Criteria

CP rotations work well when:
- **Smoothness:** Integrand f(x) is smooth (at least C¹)
- **Periodicity:** f(x) is periodic or can be transformed to periodic form
- **Continuity:** No discontinuities or sharp features
- **High dimension:** d ≥ 10 (where QMC outshines Monte Carlo)

---

## Application to RSA Factorization

### Attempted Mapping

**Hypothesis (FALSIFIED):** Apply CP to θ′(n,k)-biased Sobol sequences for RSA factorization:

```
1. Generate Sobol sequence: u_1, u_2, ..., u_N
2. Apply θ′(n,k) bias to get candidates around √N
3. Apply CP rotation: u'_i = (u_i + r) mod 1
4. Transform to factor candidates: p_i = g(u'_i, N)
```

**Expected benefit:** Reduce variance in candidate distribution → faster convergence to true factors.

### Why It Failed: Domain Mismatch

#### 1. Non-Smooth Objective

**Integration:** Smooth integrand f(x)  
**Factorization:** Discrete primality indicator δ(p) = 1 if p prime and p|N, else 0

```
Prime density:     π(x) ~ x / ln(x)    [smooth approximation]
Actual primes:     {2, 3, 5, 7, 11, ...}  [discrete, non-smooth]
```

**Impact:** CP variance reduction requires smoothness. Factorization has discontinuous success function.

#### 2. Non-Periodic Structure

**Integration:** Functions can be periodized (e.g., via coordinate transforms)  
**Factorization:** Primes have no periodic structure

```
u ∈ [0,1]:         periodic, wraps around
Candidates ∈ ℤ:    discrete integers, no natural periodicity
```

**Impact:** CP's unbiasedness guarantee doesn't apply to non-periodic factorization.

#### 3. Wrong Variance Target

**Integration variance:**
```
Var[I] = Var[(1/N) ∑_i f(u_i)]
       = Discrepancy-based error in quadrature
```

**Factorization variance:**
```
Var[candidates] = Var[distance to true factors]
                = Dependent on factor distribution, NOT quadrature error
```

**Impact:** Reducing quadrature variance ≠ reducing factorization search variance.

#### 4. Already Randomized

**CP assumption:** Deterministic QMC needs randomization for variance estimation

**RSA setup:**
- Sobol with Owen scrambling: ALREADY randomized
- θ′(n,k) bias: ALREADY introduces geometric randomness
- Multiple independent trials: ALREADY provide variance estimates

**Impact:** Adding CP rotation is redundant randomization with no benefit.

---

## Empirical Validation

### Experiment Design

**Test:** Compare baseline θ′(n,k)-biased Sobol vs. CP-rotated Sobol on RSA-100, RSA-129, RSA-155.

**Metrics:**
- **Primary:** Candidate variance σ²(distance to true factors)
- **Secondary:** Statistical significance (t-test, p < 0.05)
- **Overhead:** Timing comparison

**Falsification Criteria:**
1. Variance reduction < 1.3× (claimed 1.3-1.8×)
2. p-value > 0.05 (not significant)
3. Overhead > 2.0× (too expensive)

### Results

| Challenge | Variance Reduction | p-value | Verdict |
|-----------|-------------------|---------|---------|
| RSA-100   | 1.005× (+0.5%)    | 0.7722  | FALSIFIED |
| RSA-129   | 1.009× (+0.9%)    | 0.5204  | FALSIFIED |
| RSA-155   | 1.000× (+0.0%)    | 1.0000  | FALSIFIED |

**Conclusion:** CP rotations provide NO meaningful variance reduction for RSA factorization.

---

## Theoretical Postmortem

### Root Cause Analysis

**Why CP works for integration but fails for factorization:**

1. **Functional smoothness:**
   - Integration: f(x) smooth, derivatives bounded
   - Factorization: Primality function discontinuous

2. **Space structure:**
   - Integration: [0,1]^d continuous torus
   - Factorization: ℤ discrete, no torus structure

3. **Variance source:**
   - Integration: Discretization error in quadrature
   - Factorization: Uncertainty in factor location

4. **Randomization need:**
   - Integration: QMC deterministic, needs RQMC for CIs
   - Factorization: Already has Owen scrambling + geometric bias

### Lessons for Cross-Domain Transfer

**When transferring variance reduction techniques:**

1. ✓ **Verify smoothness assumptions** - Does target problem have smooth objective?
2. ✓ **Check periodicity requirements** - Is the search space naturally periodic?
3. ✓ **Match variance targets** - Are you reducing the right source of variance?
4. ✓ **Avoid redundant randomization** - Is the baseline already randomized?
5. ✓ **Empirical validation FIRST** - Test on small examples before claiming success

**Key principle:** Mathematical elegance ≠ practical applicability. Always validate in target domain.

---

## Alternative Approaches for RSA Factorization

### What Works Better Than CP

1. **Domain-specific bias functions:**
   - θ′(n,k): Golden-ratio geometric resolution
   - κ(n): Curvature-based weighting
   - Encodes prime number theorem structure

2. **Algebraic methods:**
   - Lattice reduction (LLL, BKZ)
   - Elliptic curve method (ECM)
   - Number field sieve (NFS)

3. **Hybrid QMC + deterministic:**
   - QMC for candidate generation
   - Deterministic sieve for filtering
   - Best of both worlds

4. **Factorization-aware metrics:**
   - Distance based on gcd(p, N)
   - Multiplicative structure preservation
   - Not generic Euclidean distance

---

## References

### Primary Sources

1. **Cranley, R., & Patterson, T. N. L. (1976).**  
   "Randomization of number theoretic methods for multiple integration."  
   *SIAM Journal on Numerical Analysis*, 13(6), 904-914.  
   DOI: 10.1137/0713071

2. **Owen, A. B. (1995).**  
   "Randomly permuted (t,m,s)-nets and (t,s)-sequences."  
   In *Monte Carlo and Quasi-Monte Carlo Methods in Scientific Computing*, pp. 299-317. Springer.

3. **L'Ecuyer, P., & Lemieux, C. (2002).**  
   "Recent advances in randomized quasi-Monte Carlo methods."  
   *Modeling Uncertainty: An Examination of Stochastic Theory, Methods, and Applications*, 419-474.

### Z-Framework Context

- **θ′(n,k) bias:** `utils/z_framework.py` - Geometric resolution with golden ratio
- **κ(n) curvature:** `utils/z_framework.py` - Discrete curvature weighting
- **QMC engines:** `python/qmc_engines.py` - Sobol, Owen, Rank-1 lattice implementations

---

## Conclusion

Cranley-Patterson rotations are a powerful variance reduction technique **for continuous numerical integration** with smooth, periodic integrands. However, they provide **NO benefit for RSA factorization** due to:

1. Non-smooth discrete primality structure
2. Non-periodic integer candidate space
3. Wrong variance target (quadrature vs. search)
4. Redundant randomization over baseline

**Verdict:** CP rotations are a domain-specific tool that does NOT generalize to discrete cryptographic optimization. This experiment definitively falsifies the claim of 1.3-1.8× variance reduction for RSA factorization.
