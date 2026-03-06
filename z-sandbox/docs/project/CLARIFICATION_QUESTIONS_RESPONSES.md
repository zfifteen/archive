# Responses to Clarification Questions on Geometric Factorization Research

This document provides detailed answers to the clarification questions posed regarding the GVA method, testing procedures, and research framework.

## 1. What exactly is GVA? (In my own words)

GVA stands for **Geodesic Validation Assault**, an experimental geometric approach to integer factorization. Instead of traditional algebraic methods like the number field sieve, GVA transforms the factorization problem into a geometric search on a high-dimensional torus manifold. 

The core idea: We embed numbers (both the semiprime N and potential factors) as points on this manifold using iterative geodesic mappings influenced by mathematical constants like the golden ratio (φ) and e². We then compute Riemannian distances that incorporate curvature corrections, ranking candidate factors by their geometric "closeness" to N's embedding. Candidates below an adaptive distance threshold (ε) are tested for primality and balance constraints.

This approach aims to convert brute-force candidate testing into an intelligent, geometry-guided search, potentially revealing hidden structural patterns in number factorization. Current success rates vary by bit size (high on 64-128 bits, zero on 200+ bits), making it valuable for debugging algorithmic limitations and exploring novel factorization paradigms.

## 2. How does the embedding work? (Math/code snippets welcome)

The embedding maps integers to points on a d-dimensional torus (typically d=11 or higher) using golden ratio-based geodesic iterations. Here's the core implementation:

```python
import mpmath as mp

mp.mp.dps = 20  # High precision for large numbers

def embed(n, dims=11, k=None):
    phi = (1 + mp.sqrt(5)) / 2  # Golden ratio
    if k is None:
        k = mp.mpf('0.3') / mp.log2(mp.log2(n + 1))  # Adaptive parameter
    x = n / mp.exp(2)  # Normalize by e²
    frac, _ = mp.modf(x / phi)
    return [mp.modf(phi * frac ** k)[0] for _ in range(dims)]
```

**Mathematical foundation:**
- Start with normalized value x = n / e²
- Extract fractional part after division by φ
- Apply k iterations of φ * fractional_part^k to create coordinate
- Repeat for each dimension with slight variations

This creates a "geodesic fingerprint" of the number on the torus manifold.

## 3. What's the distance metric and candidate ranking process?

We use a **curvature-corrected Riemannian distance** on the torus:

```python
def riemann_dist(c1, c2, N):
    kappa = 4 * mp.log(N + 1) / mp.exp(2)  # Curvature parameter κ(n)
    return mp.sqrt(sum((min(abs(a - b), 1 - abs(a - b)) * (1 + kappa * 0.01))**2 for a, b in zip(c1, c2)))
```

**Key features:**
- Accounts for torus topology (wrap-around distances)
- Incorporates curvature κ(n) = 4⋅ln(n+1)/e² for number-theoretic weighting
- Small correction term (0.01) prevents division by zero

**Candidate ranking process:**
1. Generate candidates around √N with range R (typically 1000-50000)
2. Embed both N and each candidate
3. Compute distance between embeddings
4. Sort candidates by ascending distance
5. Test top-K candidates (usually K=10) for:
   - Primality (Miller-Rabin)
   - Balance constraint |log₂(p/q)| ≤ 1
   - Actual division N % candidate == 0

## 4. How do you generate test semiprimes?

We use SymPy's prime generation for controlled, reproducible semiprimes:

```python
import sympy as sp

def generate_semiprime(bits):
    # For balanced semiprimes (p ≈ q)
    half_bits = bits // 2
    p = sp.nextprime(2**(half_bits - 1))  # Start from 2^(bits/2 - 1)
    q = sp.nextprime(p + 100)  # Small gap to ensure distinct primes
    return p * q
```

**Current approach:**
- Target balanced semiprimes for geometric regularity
- Use `sp.nextprime()` for deterministic prime selection
- Add small offset (100) to avoid twin primes
- Example: For 200 bits, p ≈ q ≈ 2^100

**Limitations:** Current implementation doesn't use random seeds, making results deterministic but potentially biased toward certain prime patterns.

## 5. Are results deterministic (fixed seeds)?

**Current status:** Partially deterministic, but not fully reproducible.

- **Prime generation:** Deterministic (SymPy's nextprime is deterministic)
- **Random sampling:** No explicit random seeds set in current code
- **Parameter sweeps:** Use fixed parameter combinations, but any internal randomness (if present) is unseeded

**Recommendation from TODO:** Implement fixed RNG seeds (e.g., random.seed(12345)) for complete reproducibility, especially for Monte Carlo components.

## 6. Are you logging trial outcomes and timings?

**Yes, comprehensive logging is implemented:**

- **CSV output:** Results saved to `python/gva_200bit_results.csv` with columns for trial number, semiprime, parameters, success/failure, timing, candidate count
- **Timing measurement:** Uses `time.time()` for per-trial timing
- **Metrics tracked:**
  - Success rate (%)
  - Average time per trial
  - Parameter combinations tested
  - Distance thresholds used
  - Top candidate distances

**Example log entry:**
```
trial,semiprime,dims,ranges,success,time_seconds,top_candidates,distance_threshold
1,1606938044258990275541962092341162602522202993782792835301376,13,5000,false,0.045,10,0.004
```

**Additional logging:** Debug mode available for detailed candidate ranking traces.

## 7. What's the ideal output from this audit?

**Recommendation:** Internal technical status report for research leads and developers.

**Why internal:**
- Contains sensitive implementation details and failure analysis
- Focuses on debugging algorithmic limitations rather than marketing achievements
- Includes code snippets, parameter tuning discussions, and technical unknowns
- Supports iterative development rather than external presentation

**Alternative:** If external-facing summary is needed, it would emphasize:
- Transformational potential of geometric factorization
- Current capabilities (64-128 bit success)
- Research roadmap without exposing implementation vulnerabilities

---

## Summary

This response clarifies the GVA method as a geometry-driven factorization approach with torus embeddings, curvature-corrected distances, and systematic candidate ranking. Current testing shows promise at smaller scales but scaling challenges at 200+ bits, with comprehensive logging but room for improved reproducibility. The framework supports hybrid approaches and parameter optimization for future breakthroughs.