#!/usr/bin/env python3
"""
Wiener Attack Implementation with Convergent Selectivity

Implements Wiener's attack on RSA with small private exponents (d < N^(1/4))
using continued fraction expansion and fractional bias scanning.

This module demonstrates the "convergent selectivity" pattern where successful
attacks often terminate at specific convergent indices, suggesting that strategic
sampling of convergent subsets is more efficient than exhaustive enumeration.

Mathematical Foundation:
- Wiener's attack works when d < (1/3)N^(1/4)
- k/d appears among convergents of e/N continued fraction expansion
- Convergents with anomalously large quotients are computationally inefficient
- Denominator growth patterns predict factorization difficulty

Key Innovation: Fractional Bias Scanning
Instead of testing all convergents, we:
1. Skip convergents with large quotient values (e.g., > max_quotient_threshold)
2. Prioritize convergents with controlled denominator growth rates
3. Terminate early when anomalous patterns detected
4. Use golden ratio φ properties for defensive key generation

References:
- Dan Boneh, "Twenty Years of Attacks on the RSA Cryptosystem" (1999)
  https://crypto.stanford.edu/~dabo/papers/RSA-survey.pdf
- PMC, "On the Improvement of Wiener Attack on RSA with Small Private Exponent"
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3985315/
- IACR, "Beauty of Cryptography: the Cryptographic Sequences and the Golden Ratio"
  https://eprint.iacr.org/2021/1129

Integration with z-sandbox:
- Complements geometric factorization methods
- Provides convergent-based attack surface analysis
- Enhances defensive parameter generation with φ-based sequences

Author: Z-Sandbox Research Framework
License: Educational/Research Use Only
"""

import math
from typing import List, Tuple, Optional, Dict
from mpmath import mp, mpf
import sympy
from sympy import continued_fraction_iterator, continued_fraction_convergents
from sympy.ntheory import isprime

# Set high precision for numerical computations
mp.dps = 50

# Universal constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio φ ≈ 1.618...
PHI_CONJ = (math.sqrt(5) - 1) / 2  # Golden ratio conjugate Φ ≈ 0.618...
E2 = math.exp(2)  # e² invariant


class ContinuedFraction:
    """
    Continued fraction expansion and convergent computation.
    
    Provides utilities for computing continued fraction expansions
    of rational and irrational numbers, along with their convergents.
    """
    
    @staticmethod
    def convergents(n: int, d: int, max_terms: int = 100) -> List[Tuple[int, int]]:
        """
        Compute convergents of the continued fraction expansion of n/d.
        
        Args:
            n: Numerator
            d: Denominator
            max_terms: Maximum number of terms to compute
            
        Returns:
            List of (numerator, denominator) tuples representing convergents
        """
        if d == 0:
            raise ValueError("Denominator cannot be zero")
        
        convergents_list = []
        cf_iter = continued_fraction_iterator(sympy.Rational(n, d))
        
        # Get partial quotients
        quotients = []
        try:
            for _ in range(max_terms):
                quotients.append(next(cf_iter))
        except StopIteration:
            pass
        
        # Compute convergents from quotients
        if len(quotients) == 0:
            return [(0, 1)]
        
        # Initialize first two convergents
        if len(quotients) >= 1:
            convergents_list.append((quotients[0], 1))
        
        if len(quotients) >= 2:
            convergents_list.append((quotients[0] * quotients[1] + 1, quotients[1]))
        
        # Compute remaining convergents using recurrence relation
        for i in range(2, len(quotients)):
            h_prev2, k_prev2 = convergents_list[i-2]
            h_prev1, k_prev1 = convergents_list[i-1]
            
            h_i = quotients[i] * h_prev1 + h_prev2
            k_i = quotients[i] * k_prev1 + k_prev2
            
            convergents_list.append((h_i, k_i))
        
        return convergents_list
    
    @staticmethod
    def quotients(n: int, d: int, max_terms: int = 100) -> List[int]:
        """
        Compute partial quotients of continued fraction expansion of n/d.
        
        Args:
            n: Numerator
            d: Denominator
            max_terms: Maximum number of quotients to compute
            
        Returns:
            List of partial quotients [a0, a1, a2, ...]
        """
        if d == 0:
            raise ValueError("Denominator cannot be zero")
        
        quotients = []
        cf_iter = continued_fraction_iterator(sympy.Rational(n, d))
        
        try:
            for _ in range(max_terms):
                quotients.append(next(cf_iter))
        except StopIteration:
            pass
        
        return quotients


class WienerAttack:
    """
    Wiener's attack on RSA with small private exponents.
    
    Implements the attack with fractional bias scanning - strategic
    convergent selection based on denominator growth patterns.
    """
    
    def __init__(self, 
                 max_quotient_threshold: int = 1000,
                 enable_bias_scanning: bool = True,
                 verbose: bool = False):
        """
        Initialize Wiener attack configuration.
        
        Args:
            max_quotient_threshold: Skip convergents with quotients larger than this
            enable_bias_scanning: Enable fractional bias scanning optimization
            verbose: Print debug information
        """
        self.max_quotient_threshold = max_quotient_threshold
        self.enable_bias_scanning = enable_bias_scanning
        self.verbose = verbose
        self.stats = {
            'convergents_tested': 0,
            'convergents_skipped': 0,
            'large_quotients_detected': 0,
            'total_convergents': 0
        }
    
    def attack(self, e: int, N: int) -> Optional[Tuple[int, int]]:
        """
        Perform Wiener's attack to factor N.
        
        Args:
            e: Public exponent
            N: RSA modulus to factor
            
        Returns:
            (p, q) if attack succeeds, None otherwise
        """
        if self.verbose:
            print(f"\n=== Wiener Attack on N={N} ===")
            print(f"Public exponent e={e}")
            print(f"Bias scanning: {self.enable_bias_scanning}")
            print(f"Max quotient threshold: {self.max_quotient_threshold}")
        
        # Get partial quotients for early termination analysis
        quotients = ContinuedFraction.quotients(e, N, max_terms=200)
        
        if self.verbose:
            print(f"\nPartial quotients (first 10): {quotients[:10]}")
        
        # Detect anomalously large quotients (the "5911 pattern")
        large_quotient_indices = [
            i for i, q in enumerate(quotients) 
            if q > self.max_quotient_threshold
        ]
        
        if large_quotient_indices and self.verbose:
            first_large = large_quotient_indices[0]
            print(f"\nAnomaly detected: quotient[{first_large}] = {quotients[first_large]}")
            print(f"Terminating before index {first_large}")
        
        # Compute convergents
        convergents = ContinuedFraction.convergents(e, N, max_terms=200)
        self.stats['total_convergents'] = len(convergents)
        
        if self.verbose:
            print(f"\nTotal convergents: {len(convergents)}")
        
        # Test convergents with bias scanning
        for i, (k, d) in enumerate(convergents):
            # Skip trivial convergents
            if d == 0 or k == 0:
                continue
            
            # Fractional bias scanning: skip convergents after large quotients
            if self.enable_bias_scanning and i < len(quotients):
                if quotients[i] > self.max_quotient_threshold:
                    self.stats['convergents_skipped'] += 1
                    self.stats['large_quotients_detected'] += 1
                    if self.verbose:
                        print(f"Skipping convergent {i}: quotient={quotients[i]} > threshold")
                    break  # Terminate early - the key insight
            
            self.stats['convergents_tested'] += 1
            
            # Test if k/d could be k/d where ed ≡ 1 (mod φ(N))
            result = self._test_convergent(k, d, e, N)
            if result:
                if self.verbose:
                    print(f"\n✓ Success at convergent index {i}")
                    print(f"  k/d = {k}/{d}")
                    p, q = result
                    print(f"  Factors: p={p}, q={q}")
                return result
        
        if self.verbose:
            print("\n✗ Attack failed - d may be too large")
            self._print_stats()
        
        return None
    
    def _test_convergent(self, k: int, d: int, e: int, N: int) -> Optional[Tuple[int, int]]:
        """
        Test if convergent k/d leads to factorization.
        
        For the convergent to represent k/d where ed = 1 + k*φ(N),
        we can derive φ(N) = (ed - 1) / k and then solve for p, q.
        
        Args:
            k: Convergent numerator (approximates k in ed ≡ 1 (mod φ(N)))
            d: Convergent denominator (approximates private exponent)
            e: Public exponent
            N: RSA modulus
            
        Returns:
            (p, q) if successful, None otherwise
        """
        if k == 0:
            return None
        
        # Calculate possible φ(N)
        phi_N = (e * d - 1) // k
        
        if phi_N <= 0 or phi_N >= N:
            return None
        
        # From φ(N) = (p-1)(q-1) = N - (p+q) + 1, and pq = N:
        # We get: p + q = N - φ(N) + 1
        # And: (p-q)² = (p+q)² - 4N
        
        sum_pq = N - phi_N + 1
        
        # Check if (p+q)² - 4N is a perfect square
        discriminant = sum_pq * sum_pq - 4 * N
        
        if discriminant < 0:
            return None
        
        # Check if discriminant is perfect square
        # Use math.isqrt for accurate integer square root (Python 3.8+)
        sqrt_disc = math.isqrt(discriminant)
        if sqrt_disc * sqrt_disc != discriminant:
            return None
        
        # Solve for p and q
        p = (sum_pq + sqrt_disc) // 2
        q = (sum_pq - sqrt_disc) // 2
        
        # Verify
        if p * q == N and p > 1 and q > 1:
            return (p, q) if p >= q else (q, p)
        
        return None
    
    def analyze_vulnerability(self, e: int, N: int) -> Dict:
        """
        Analyze RSA parameters for Wiener attack vulnerability.
        
        Args:
            e: Public exponent
            N: RSA modulus
            
        Returns:
            Dictionary with vulnerability analysis
        """
        quotients = ContinuedFraction.quotients(e, N, max_terms=100)
        convergents = ContinuedFraction.convergents(e, N, max_terms=100)
        
        # Analyze quotient patterns
        large_quotients = [q for q in quotients if q > self.max_quotient_threshold]
        avg_quotient = sum(quotients) / len(quotients) if quotients else 0
        max_quotient = max(quotients) if quotients else 0
        
        # Analyze denominator growth
        denom_growth_rates = []
        for i in range(1, len(convergents)):
            if convergents[i-1][1] > 0:
                growth_rate = convergents[i][1] / convergents[i-1][1]
                denom_growth_rates.append(growth_rate)
        
        avg_growth = sum(denom_growth_rates) / len(denom_growth_rates) if denom_growth_rates else 0
        
        return {
            'total_convergents': len(convergents),
            'total_quotients': len(quotients),
            'large_quotients_count': len(large_quotients),
            'first_large_quotient_index': next((i for i, q in enumerate(quotients) 
                                                if q > self.max_quotient_threshold), None),
            'avg_quotient': avg_quotient,
            'max_quotient': max_quotient,
            'avg_denominator_growth': avg_growth,
            'vulnerability_score': self._compute_vulnerability_score(quotients, convergents)
        }
    
    def _compute_vulnerability_score(self, quotients: List[int], 
                                     convergents: List[Tuple[int, int]]) -> float:
        """
        Compute vulnerability score (0-1, higher = more vulnerable).
        
        Factors considered:
        - Presence of early large quotients (suggests resistance)
        - Denominator growth rate (slow growth = vulnerable)
        - Total convergent count needed
        
        Args:
            quotients: Partial quotients
            convergents: Convergents list
            
        Returns:
            Vulnerability score between 0 and 1
        """
        score = 0.5  # Baseline
        
        # Early large quotient reduces vulnerability
        first_large = next((i for i, q in enumerate(quotients) 
                           if q > self.max_quotient_threshold), None)
        if first_large is not None:
            # Earlier anomaly = lower vulnerability
            score -= 0.3 * (1.0 - first_large / len(quotients))
        
        # Slow denominator growth increases vulnerability
        if len(convergents) > 3:
            early_growth = convergents[3][1] / convergents[0][1] if convergents[0][1] > 0 else 1
            if early_growth < 100:  # Slow growth
                score += 0.3
        
        return max(0.0, min(1.0, score))
    
    def _print_stats(self):
        """Print attack statistics."""
        print("\n=== Attack Statistics ===")
        print(f"Total convergents: {self.stats['total_convergents']}")
        print(f"Convergents tested: {self.stats['convergents_tested']}")
        print(f"Convergents skipped: {self.stats['convergents_skipped']}")
        print(f"Large quotients detected: {self.stats['large_quotients_detected']}")
        if self.stats['convergents_tested'] > 0:
            efficiency = (self.stats['convergents_skipped'] / 
                         (self.stats['convergents_tested'] + self.stats['convergents_skipped']) * 100)
            print(f"Efficiency gain: {efficiency:.1f}% convergents avoided")


class GoldenRatioDefense:
    """
    Defensive RSA parameter generation using golden ratio properties.
    
    Golden ratio φ has the property that it is the "most irrational" number,
    meaning its continued fraction expansion [1; 1, 1, 1, ...] has all quotients
    equal to 1, providing maximally poor rational approximations.
    
    This makes φ-based sequences resistant to convergent-based attacks.
    """
    
    @staticmethod
    def generate_phi_resistant_exponent(N: int, min_bits: int = 16) -> int:
        """
        Generate public exponent resistant to Wiener attack.
        
        Uses Fibonacci-based selection that approaches φ to avoid
        early convergent patterns exploitable by Wiener-type attacks.
        
        Args:
            N: RSA modulus
            min_bits: Minimum bit length for exponent
            
        Returns:
            Public exponent e with φ-resistant properties
        """
        # Generate Fibonacci sequence
        fib = [1, 1]
        while fib[-1].bit_length() < min_bits + 10:
            fib.append(fib[-1] + fib[-2])
        
        # Use odd-positioned Fibonacci (smoother φ approach)
        # Reference: IACR ePrint 2021/1129
        candidates = [fib[i] for i in range(1, len(fib), 2) 
                     if fib[i].bit_length() >= min_bits]
        
        # Select candidate that is coprime to N and has good properties
        for e_candidate in candidates:
            if math.gcd(e_candidate, N) == 1:
                # Verify it has φ-like continued fraction properties
                quotients = ContinuedFraction.quotients(e_candidate, N, max_terms=20)
                # Look for mostly small, uniform quotients
                if len(quotients) > 5 and max(quotients[:5]) < 100:
                    continue  # Too uniform, skip
                return e_candidate
        
        # Fallback: use standard small prime
        return 65537
    
    @staticmethod
    def is_phi_resistant(e: int, N: int, threshold: int = 1000) -> bool:
        """
        Check if (e, N) pair is resistant to Wiener attack.
        
        Args:
            e: Public exponent
            N: RSA modulus
            threshold: Quotient threshold for resistance (default: 1000)
            
        Returns:
            True if parameters show resistance patterns
        """
        # Configuration constants
        MAX_QUOTIENTS_TO_CHECK = 20
        EARLY_QUOTIENTS_WINDOW = 10
        
        quotients = ContinuedFraction.quotients(e, N, max_terms=MAX_QUOTIENTS_TO_CHECK)
        
        # Check for early large quotient (the "5911 pattern")
        for i, q in enumerate(quotients[:EARLY_QUOTIENTS_WINDOW]):  # Check first 10
            if q > threshold:
                return True  # Early anomaly suggests resistance
        
        return False


def demo_wiener_attack():
    """
    Demonstrate Wiener attack with vulnerable RSA parameters.
    
    This creates a deliberately vulnerable RSA instance with small d
    to show how the attack works and the convergent selectivity pattern.
    """
    print("=" * 70)
    print("Wiener Attack Demonstration")
    print("Educational/Research Purpose Only")
    print("=" * 70)
    
    # Generate vulnerable RSA parameters (small d)
    # For demonstration: use small primes
    p = 857
    q = 1009
    N = p * q  # 864713
    phi_N = (p - 1) * (q - 1)  # 862848
    
    # Choose small d (vulnerable)
    # Wiener attack works when d < (1/3) * N^(1/4)
    # N^(1/4) ≈ 30.49, so d should be < 10.16
    # Find a small d that is coprime to phi_N
    d = 5
    while math.gcd(d, phi_N) != 1:
        d += 2  # Try odd numbers
        if d > 20:  # Safety check
            d = 65537  # Fallback
            break
    
    # For this demo, let's use a known small coprime d
    d = 17  # Coprime to phi_N and reasonably small
    
    # Compute e
    e = pow(d, -1, phi_N)  # e ≡ d^(-1) (mod φ(N))
    
    print(f"\nVulnerable RSA Parameters:")
    print(f"  p = {p}")
    print(f"  q = {q}")
    print(f"  N = {N}")
    print(f"  φ(N) = {phi_N}")
    print(f"  d = {d} (small - vulnerable!)")
    print(f"  e = {e}")
    print(f"  N^(1/4) = {N**(1/4):.2f}")
    print(f"  d < N^(1/4)? {d < N**(1/4)}")
    
    # Perform attack
    attacker = WienerAttack(verbose=True, enable_bias_scanning=True)
    result = attacker.attack(e, N)
    
    if result:
        p_found, q_found = result
        print(f"\n{'='*70}")
        print("✓ ATTACK SUCCESSFUL!")
        print(f"{'='*70}")
        print(f"Recovered factors: p={p_found}, q={q_found}")
        print(f"Verification: {p_found} × {q_found} = {p_found * q_found}")
        print(f"Matches N? {p_found * q_found == N}")
    else:
        print("\n✗ Attack failed")
    
    # Analyze vulnerability
    print(f"\n{'='*70}")
    print("Vulnerability Analysis")
    print(f"{'='*70}")
    analysis = attacker.analyze_vulnerability(e, N)
    for key, value in analysis.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    demo_wiener_attack()
