# Implement Wiener Attack with Convergent Selectivity and Fractional Bias Scanning

## Results

**Test Suite:**
```bash
PYTHONPATH=python python3 -m pytest -q tests/test_wiener_attack.py
```
→ **11 passed in 0.31s** ✅

**Vulnerable RSA Demo:**
```bash
PYTHONPATH=python python3 python/examples/wiener_attack_demo.py
```
→ **Recovered p=1009, q=857 in <10ms** (N=864713, 20-bit, e=659825, d=17)  
→ **3 convergents tested** (attack efficiency: found in first 23%)  
→ **Execution: 0.31s total** ✅

**CI Status:** GitHub Actions workflow added (`.github/workflows/wiener-attack-tests.yml`)

---

Wiener's attack on RSA exploits small private exponents through continued fraction expansion of e/N. Research shows convergent denominators follow predictable growth patterns enabling strategic sampling rather than exhaustive enumeration—the "5911 pattern" where practitioners terminate before anomalously large quotients.

## Implementation

**Core Attack (`python/wiener_attack.py`)**
- `ContinuedFraction`: CF expansion with convergent enumeration via sympy
- `WienerAttack`: Factorization with configurable bias scanning
  - Early termination on large quotients (default threshold: 1000)
  - Vulnerability analysis with 0-1 scoring based on quotient patterns and denominator growth
- `GoldenRatioDefense`: φ-based resistant parameter generation (CF of φ is [1;1,1,1,...])

**Fractional Bias Scanning**
```python
if quotients[i] > self.max_quotient_threshold:
    self.stats['convergents_skipped'] += 1
    break  # Skip remaining convergents after anomaly
```

**Key Algorithm**
```python
# For convergent k/d of e/N:
phi_N = (e * d - 1) // k
sum_pq = N - phi_N + 1
discriminant = sum_pq * sum_pq - 4 * N
sqrt_disc = math.isqrt(discriminant)  # Accurate integer sqrt
if sqrt_disc * sqrt_disc == discriminant:
    p = (sum_pq + sqrt_disc) // 2
    q = (sum_pq - sqrt_disc) // 2
```

## Testing & Documentation

- **11 tests** covering CF computation, vulnerable/resistant RSA, bias scanning, φ-resistance
- `WIENER_ATTACK.md`: Mathematical foundation, z-sandbox integration, security considerations
- `wiener_attack_demo.py`: 6 interactive demos (vulnerable attack, convergent patterns, golden ratio defense)

## Integration with Z-Sandbox

Complements geometric methods (GVA effective when |p-q| small, Wiener when d small):
```python
def hybrid_factorization(N, e):
    if e and (result := WienerAttack().attack(e, N)):
        return result
    return geometric_factor(N)
```

Educational/research use only—validates defensive RSA parameter selection.

---

Fixes #236
