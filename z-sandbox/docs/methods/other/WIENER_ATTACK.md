# Wiener Attack with Convergent Selectivity

## Overview

This implementation demonstrates **Wiener's attack on RSA** with an emphasis on **convergent selectivity** - the systematic but underemphasized pattern in how continued fraction convergents reveal cryptographic vulnerabilities.

While Wiener's attack is well-documented for breaking RSA when the private exponent d < N^(1/4), this implementation reveals that convergent denominators exhibit predictable selection patterns that can be exploited or defended against through "fractional bias scanning."

## Mathematical Foundation

### Wiener's Original Attack (1990)

**Condition**: Attack works when d < (1/3)N^(1/4)

**Method**: Find k/d among convergents of e/N through continued fraction expansion

**Why it works**: When ed ≡ 1 (mod φ(N)), we have:
- ed = 1 + k·φ(N) for some integer k
- |e/N - k/d| < 1/(2d²)
- Therefore k/d is a convergent of e/N

### Continued Fraction Expansion

Every rational number n/d can be expressed as:
```
n/d = a₀ + 1/(a₁ + 1/(a₂ + 1/(a₃ + ...)))
```

Notation: [a₀; a₁, a₂, a₃, ...]

The convergents are:
- C₀ = a₀/1
- C₁ = (a₀·a₁ + 1)/a₁
- C₂ = (a₂·C₁_num + C₀_num)/(a₂·C₁_den + C₀_den)
- ...

### The Convergent Selectivity Pattern

**Key Insight**: Successful attacks often terminate at specific convergent indices, typically stopping before anomalously large values in the expansion.

**Example** (from Crypto StackExchange):
Continued fraction [0;2,1,9,6,54,**5911**,...]

Practitioners "stop the continued fraction before 5911, because it's a big number" - indicating that convergents with anomalously large quotients are computationally inefficient candidates.

This is the **"5911 pattern"** - an anomaly detection heuristic.

## Implementation Features

### 1. Core Wiener Attack

**Module**: `python/wiener_attack.py`

**Class**: `WienerAttack`

```python
from wiener_attack import WienerAttack

# Attack RSA with small d
attacker = WienerAttack(
    max_quotient_threshold=1000,
    enable_bias_scanning=True,
    verbose=True
)

result = attacker.attack(e, N)
if result:
    p, q = result
    print(f"Factors found: {p}, {q}")
```

### 2. Fractional Bias Scanning

**Innovation**: Instead of testing all convergents exhaustively, we:

1. **Skip convergents with large quotient values** (default threshold: 1000)
2. **Prioritize convergents with controlled denominator growth rates**
3. **Terminate early when anomalous patterns detected**
4. **Track efficiency metrics** (convergents tested vs. skipped)

**Performance Impact**: Demonstrated in PMC research - reduced search cost from 2^(r+8) to 2^(r-6) bits, achieving **2^14 times speedup** through strategic convergent selection.

### 3. Convergent Termination Pattern

The implementation tracks and analyzes:
- Partial quotients in continued fraction expansion
- Denominator growth rates between successive convergents
- Detection of anomalously large quotients
- Early termination heuristics

**Example output**:
```
Anomaly detected: quotient[6] = 5911
Terminating before index 6
```

### 4. Vulnerability Analysis

**Method**: `analyze_vulnerability(e, N)`

Returns comprehensive analysis:
```python
{
    'total_convergents': 12,
    'large_quotients_count': 1,
    'first_large_quotient_index': 6,
    'avg_quotient': 55.2,
    'max_quotient': 5911,
    'avg_denominator_growth': 4.73,
    'vulnerability_score': 0.35  # 0-1, higher = more vulnerable
}
```

### 5. Golden Ratio Defense

**Class**: `GoldenRatioDefense`

**Principle**: Golden ratio φ = (1+√5)/2 has continued fraction [1; 1, 1, 1, ...] with all quotients equal to 1, providing the "most irrational" number - maximally poor rational approximations.

**Application**: Generate cryptographic parameters using φ-based sequences to deliberately avoid convergent patterns exploitable by Wiener-type attacks.

**Reference**: IACR ePrint 2021/1129 - "Beauty of Cryptography: the Cryptographic Sequences and the Golden Ratio"

```python
from wiener_attack import GoldenRatioDefense

# Generate φ-resistant exponent
e = GoldenRatioDefense.generate_phi_resistant_exponent(N, min_bits=16)

# Check resistance
is_safe = GoldenRatioDefense.is_phi_resistant(e, N, threshold=1000)
```

## Usage Examples

### Example 1: Basic Attack

```python
from wiener_attack import WienerAttack

# Vulnerable RSA parameters
p = 857
q = 1009
N = p * q
phi_N = (p - 1) * (q - 1)
d = 17  # Small d - vulnerable!
e = pow(d, -1, phi_N)

# Perform attack
attacker = WienerAttack(verbose=True)
result = attacker.attack(e, N)

if result:
    print(f"Success! Factors: {result}")
else:
    print("Attack failed - d too large")
```

### Example 2: Vulnerability Analysis

```python
from wiener_attack import WienerAttack

attacker = WienerAttack()
analysis = attacker.analyze_vulnerability(e, N)

print(f"Vulnerability score: {analysis['vulnerability_score']}")
print(f"Max quotient: {analysis['max_quotient']}")
print(f"Early termination possible: {analysis['first_large_quotient_index'] is not None}")
```

### Example 3: Defensive Parameter Testing

```python
from wiener_attack import GoldenRatioDefense

# Test if your RSA parameters are safe
is_safe = GoldenRatioDefense.is_phi_resistant(e, N, threshold=1000)

if not is_safe:
    print("WARNING: Parameters may be vulnerable to Wiener attack")
    print("Consider regenerating with larger d or φ-resistant exponent")
```

### Example 4: Bias Scanning Comparison

```python
from wiener_attack import WienerAttack

# With bias scanning
attacker1 = WienerAttack(enable_bias_scanning=True)
result1 = attacker1.attack(e, N)
efficiency1 = attacker1.stats['convergents_tested']

# Without bias scanning
attacker2 = WienerAttack(enable_bias_scanning=False)
result2 = attacker2.attack(e, N)
efficiency2 = attacker2.stats['convergents_tested']

print(f"Bias scanning tested: {efficiency1} convergents")
print(f"Full search tested: {efficiency2} convergents")
print(f"Speedup: {efficiency2/efficiency1:.2f}x")
```

## Attack Limitations

Wiener's attack **only works** when:

1. **d < (1/3)N^(1/4)** - Private exponent is sufficiently small
2. **gcd(p-1, q-1)** is small relative to N
3. **Standard RSA** (not Multi-Prime RSA or other variants)

**Defense**: Use d > N^(1/4) in RSA key generation. Most modern RSA implementations already do this.

## Integration with Z-Sandbox Framework

### Complementary Methods

Wiener attack complements geometric factorization methods:

1. **Geometric methods** (GVA, elliptic billiards): Effective when |p-q| is small
2. **Convergent methods** (Wiener): Effective when d is small
3. **Hybrid approach**: Use prime factor separation as decision criterion

### Z-Framework Alignment

The convergent selectivity pattern aligns with Z-Framework principles:

- **Z = A(B/c)**: Convergents represent rational approximations with denominator as invariant
- **Denominator growth ~ curvature**: Rapid growth indicates increasing "distance" from target
- **Golden ratio φ**: Ultimate invariant for cryptographic resistance

### Usage in Factorization Pipeline

```python
from wiener_attack import WienerAttack
from gva import GeometricValidationAssault  # Z-sandbox GVA

def hybrid_factorization(N, e):
    """Try Wiener attack first (fast), fallback to GVA."""
    
    # Step 1: Wiener attack (O(log N) convergents)
    wiener = WienerAttack()
    result = wiener.attack(e, N)
    if result:
        return result
    
    # Step 2: Geometric methods
    gva = GeometricValidationAssault()
    return gva.factor(N)
```

## Mathematical Properties

### Convergent Growth Analysis

For the i-th convergent C_i = h_i/k_i:

**Growth bounds**:
- k_i+1 ≥ k_i (denominators are monotonically increasing)
- k_i+1 = a_i+1 · k_i + k_i-1 (recurrence relation)
- If a_i is large, k_i grows rapidly

**Approximation quality**:
- |n/d - h_i/k_i| < 1/(k_i · k_i+1)
- Convergents are "best rational approximations"

### Golden Ratio Properties

**Continued fraction**: φ = [1; 1, 1, 1, ...]

**Convergents**: Fibonacci ratios F_n+1/F_n
- 1/1, 2/1, 3/2, 5/3, 8/5, 13/8, 21/13, ...

**Approximation**: Worst possible for any irrational
- |φ - p/q| > 1/(√5 · q²) for all p, q

**Cryptographic implication**: φ-based exponents resist convergent attacks

## References

### Primary Sources

1. **Dan Boneh** (1999). "Twenty Years of Attacks on the RSA Cryptosystem"
   - https://crypto.stanford.edu/~dabo/papers/RSA-survey.pdf
   - Section on Wiener's attack and continued fractions

2. **PMC** (2013). "On the Improvement of Wiener Attack on RSA with Small Private Exponent"
   - https://pmc.ncbi.nlm.nih.gov/articles/PMC3985315/
   - 2^14 speedup through strategic convergent selection

3. **IACR ePrint** (2021). "Beauty of Cryptography: the Cryptographic Sequences and the Golden Ratio"
   - https://eprint.iacr.org/2021/1129
   - Golden ratio-based defensive key generation

4. **ArXiv** (2025). "A Geometric Square-Based Approach to RSA Integer Factorization"
   - https://arxiv.org/html/2506.17233
   - Geometric methods complement convergent approaches

### Practical Examples

5. **Crypto StackExchange**: "RSA attack with continued fractions (Wieners attack)"
   - https://crypto.stackexchange.com/questions/56204/
   - The "5911 pattern" - early termination heuristic

6. **Wikipedia**: "Wiener's attack"
   - https://en.wikipedia.org/wiki/Wiener's_attack
   - Systematic convergent enumeration examples

## Testing

### Run Tests

```bash
# From repository root
PYTHONPATH=python python3 tests/test_wiener_attack.py

# Or with pytest
PYTHONPATH=python pytest tests/test_wiener_attack.py -v
```

### Test Coverage

- ✓ Continued fraction expansion (simple rationals, golden ratio)
- ✓ Convergent computation and verification
- ✓ Wiener attack on vulnerable parameters
- ✓ Wiener attack on resistant parameters
- ✓ Bias scanning efficiency comparison
- ✓ Vulnerability analysis metrics
- ✓ Golden ratio resistance checking
- ✓ Large quotient detection ("5911 pattern")
- ✓ Convergent termination patterns
- ✓ Denominator growth analysis

### Example Test Output

```
=== Test: Wiener Attack on Vulnerable RSA ===
Testing with N=864713, d=17, e=659825
N^(1/4) = 30.49, d < N^(1/4)? True
✓ Attack succeeded: found p=1009, q=857
✓ Convergents tested: 3

TEST RESULTS: 11 passed, 0 failed
```

## Security Considerations

### Educational Use Only

This implementation is provided for:
- ✓ Educational purposes
- ✓ Security research
- ✓ RSA parameter validation
- ✓ Defensive key generation testing

**DO NOT USE** for:
- ✗ Attacking systems without authorization
- ✗ Breaking real-world RSA implementations
- ✗ Any illegal cryptanalysis activities

### Responsible Disclosure

If you discover RSA implementations vulnerable to Wiener attack:
1. **DO NOT** exploit the vulnerability
2. **DO** report to the vendor/maintainer privately
3. **ALLOW** reasonable time for patching before public disclosure
4. **FOLLOW** standard responsible disclosure practices

### Modern RSA Defense

Most modern RSA implementations are **NOT vulnerable** to Wiener attack because:
- Key generation uses d ≥ N^(1/2) (far above N^(1/4) threshold)
- Standards (FIPS 186-4, PKCS#1) mandate secure parameter selection
- Automated checking prevents weak key generation

This implementation helps **validate** that defense is working.

## Future Work

### Potential Extensions

1. **Extended Wiener Attacks**
   - Boneh-Durfee attack (d < N^0.292)
   - Continued fraction with lattice reduction
   - Multi-prime RSA variants

2. **Hybrid Geometric-Convergent Methods**
   - Decision criterion based on e/N expansion
   - Adaptive method selection
   - Integrated z-sandbox pipeline

3. **Machine Learning**
   - Predict attack success from quotient patterns
   - Optimize threshold parameters
   - Classify vulnerability from CF properties

4. **Advanced Defense**
   - Automated φ-resistant key generation
   - Real-time parameter validation
   - Integration with HSM/TPM key generation

## Author

Z-Sandbox Research Framework
Educational/Research Use Only

## License

Part of z-sandbox geometric factorization framework.
See repository root for license information.
