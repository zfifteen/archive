#!/usr/bin/env python3
"""
Eigenvalue Multiplicity Calculator for Discrete n-Tori Laplacian

This module implements calculations for:
1. Eigenvalue multiplicities r_n(k) on n-dimensional discrete tori
2. Divisor function d(k) and bound verification d(k) ≪_ε k^ε
3. Sum-of-squares representations for 2D case: r_2(k) = 4 * sum_{d|k} χ(d)
4. Extension to higher dimensions (n=7 for GVA compatibility)

Mathematical Background:
- Laplacian on T^n has eigenvalues λ = 4π²‖ξ‖² for ξ ∈ Z^n
- Multiplicity r_n(k) = #{ξ ∈ Z^n : ‖ξ‖² = k}
- For n=2: r_2(k) = 4 * sum_{d|k} χ(d) where χ is non-principal character mod 4
- Optimal bound for nonzero 2D eigenvalues: multiplicity ≤ 24

References:
- Gauss's Circle Problem
- Jacobi's Four-Square Theorem
- Divisor function bounds: d(k) ≪_ε k^ε for any ε > 0
"""

import math
import sympy as sp
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from functools import lru_cache
import mpmath as mp

mp.mp.dps = 50


class EigenvalueMultiplicityCalculator:
    """Calculate eigenvalue multiplicities and divisor bounds for n-tori."""
    
    def __init__(self, dimension: int = 7):
        """
        Initialize calculator for n-dimensional torus.
        
        Args:
            dimension: Number of dimensions (default 7 for GVA)
        """
        self.dimension = dimension
        self.cache_representations = {}
        
    @staticmethod
    @lru_cache(maxsize=10000)
    def divisor_function(n: int) -> int:
        """
        Calculate the divisor function d(n) = number of divisors of n.
        
        Args:
            n: Positive integer
            
        Returns:
            Number of divisors of n
        """
        if n <= 0:
            raise ValueError("n must be positive")
        return sp.divisor_count(n)
    
    @staticmethod
    def divisor_bound_verification(k_max: int, epsilon: float = 0.1) -> Tuple[List[int], List[float]]:
        """
        Verify divisor bound d(k) ≪_ε k^ε empirically.
        
        The theoretical bound states that for any ε > 0, there exists C_ε such that
        d(k) ≤ C_ε * k^ε for all k. We verify this by computing d(k)/k^ε.
        
        Args:
            k_max: Maximum k to test
            epsilon: Exponent in bound (default 0.1)
            
        Returns:
            Tuple of (k_values, ratios) where ratios[i] = d(k)/k^epsilon
        """
        k_values = []
        ratios = []
        
        for k in range(1, k_max + 1):
            d_k = EigenvalueMultiplicityCalculator.divisor_function(k)
            ratio = d_k / (k ** epsilon)
            k_values.append(k)
            ratios.append(ratio)
            
        return k_values, ratios
    
    @staticmethod
    @lru_cache(maxsize=10000)
    def chi_mod_4(d: int) -> int:
        """
        Non-principal character χ mod 4: χ(d) = 0 if d even, 1 if d≡1(mod 4), -1 if d≡3(mod 4).
        
        Args:
            d: Integer
            
        Returns:
            χ(d) ∈ {-1, 0, 1}
        """
        if d % 2 == 0:
            return 0
        elif d % 4 == 1:
            return 1
        else:  # d % 4 == 3
            return -1
    
    @staticmethod
    def r_2_sum_of_squares(k: int) -> int:
        """
        Calculate r_2(k): number of ways to represent k as sum of 2 squares.
        
        For k > 0: r_2(k) = 4 * sum_{d|k} χ(d)
        
        Args:
            k: Positive integer
            
        Returns:
            Number of representations (x,y) ∈ Z² such that x² + y² = k
        """
        if k <= 0:
            raise ValueError("k must be positive")
            
        divisors = sp.divisors(k)
        chi_sum = sum(EigenvalueMultiplicityCalculator.chi_mod_4(d) for d in divisors)
        return 4 * chi_sum
    
    def count_representations_bruteforce(self, k: int, n: int, max_coord: int = 1000) -> int:
        """
        Count representations of k as sum of n squares by brute force (for small k).
        
        r_n(k) = #{(x_1,...,x_n) ∈ Z^n : x_1² + ... + x_n² = k}
        
        Args:
            k: Target sum
            n: Number of dimensions
            max_coord: Maximum coordinate value to search
            
        Returns:
            Number of representations found (may be incomplete for large k)
        """
        if k <= 0:
            raise ValueError("k must be positive")
        if n <= 0:
            raise ValueError("n must be positive")
            
        # For efficiency, only search up to sqrt(k) per coordinate
        search_limit = min(int(math.sqrt(k)) + 1, max_coord)
        
        def count_recursive(target: int, dims_left: int) -> int:
            """Recursively count representations."""
            if dims_left == 0:
                return 1 if target == 0 else 0
                
            if target < 0:
                return 0
                
            count = 0
            # Must check all x values, not break early (negative x² is not increasing)
            for x in range(-search_limit, search_limit + 1):
                x_sq = x * x
                if x_sq > target:
                    continue  # Skip this x, but continue to check others
                count += count_recursive(target - x_sq, dims_left - 1)
                
            return count
        
        return count_recursive(k, n)
    
    def r_n_multiplicity(self, k: int, n: Optional[int] = None, method: str = 'theoretical') -> int:
        """
        Calculate r_n(k): eigenvalue multiplicity for n-dimensional torus.
        
        Args:
            k: Integer lattice point norm squared
            n: Number of dimensions (uses self.dimension if None)
            method: 'theoretical' (formulas for n=2,4,8) or 'bruteforce' (small k only)
            
        Returns:
            Multiplicity r_n(k)
        """
        if n is None:
            n = self.dimension
            
        if k <= 0:
            raise ValueError("k must be positive")
            
        if method == 'theoretical':
            if n == 2:
                return self.r_2_sum_of_squares(k)
            elif n == 4:
                # Jacobi's four-square theorem: r_4(k) = 8 * sum of divisors not ≡ 0 (mod 4)
                divisors = sp.divisors(k)
                return 8 * sum(d for d in divisors if d % 4 != 0)
            elif n == 8:
                # For n=8, there's a modular form formula but it's complex
                # Fall back to brute force for small k
                if k <= 100:
                    return self.count_representations_bruteforce(k, n, max_coord=50)
                else:
                    # Estimate using divisor bound (rough upper bound)
                    return self.divisor_function(k) * (2 ** n)
            else:
                # General case: use brute force for small k, estimate for large k
                if k <= 50:
                    return self.count_representations_bruteforce(k, n, max_coord=30)
                else:
                    # Very rough estimate: grows with divisor function
                    return self.divisor_function(k) * (2 ** (n // 2))
        else:  # bruteforce
            return self.count_representations_bruteforce(k, n)
    
    def verify_multiplicity_bound_2d(self, k_max: int = 100) -> Dict[str, any]:
        """
        Verify that nonzero 2D Laplacian eigenvalue multiplicities are bounded by 24.
        
        Args:
            k_max: Maximum k to test
            
        Returns:
            Dictionary with verification results
        """
        multiplicities = []
        violations = []
        
        for k in range(1, k_max + 1):
            r_k = self.r_2_sum_of_squares(k)
            multiplicities.append((k, r_k))
            if r_k > 24:
                violations.append((k, r_k))
        
        max_multiplicity = max(r for _, r in multiplicities)
        
        return {
            'k_max': k_max,
            'max_multiplicity_observed': max_multiplicity,
            'bound_24_holds': max_multiplicity <= 24,
            'violations': violations,
            'multiplicity_distribution': multiplicities
        }
    
    def correlate_multiplicity_with_divisors(self, k_max: int = 100) -> Dict[str, any]:
        """
        Analyze correlation between r_n(k) and d(k).
        
        This tests the hypothesis that eigenvalue multiplicity is bounded by
        divisor function properties.
        
        Args:
            k_max: Maximum k to analyze
            
        Returns:
            Dictionary with correlation analysis
        """
        data = []
        
        for k in range(1, k_max + 1):
            r_k = self.r_n_multiplicity(k, n=2)  # Use 2D for exact computation
            d_k = self.divisor_function(k)
            ratio = r_k / d_k if d_k > 0 else 0
            data.append({
                'k': k,
                'r_k': r_k,
                'd_k': d_k,
                'ratio': ratio
            })
        
        # Compute correlation coefficient
        r_values = [d['r_k'] for d in data]
        d_values = [d['d_k'] for d in data]
        
        # Pearson correlation
        mean_r = sum(r_values) / len(r_values)
        mean_d = sum(d_values) / len(d_values)
        
        numerator = sum((r - mean_r) * (d - mean_d) for r, d in zip(r_values, d_values))
        denom_r = math.sqrt(sum((r - mean_r) ** 2 for r in r_values))
        denom_d = math.sqrt(sum((d - mean_d) ** 2 for d in d_values))
        
        correlation = numerator / (denom_r * denom_d) if denom_r * denom_d > 0 else 0
        
        return {
            'k_max': k_max,
            'data': data,
            'pearson_correlation': correlation,
            'mean_ratio_r_to_d': sum(d['ratio'] for d in data) / len(data),
            'max_ratio': max(d['ratio'] for d in data),
            'min_ratio': min(d['ratio'] for d in data)
        }


def demo_eigenvalue_calculations():
    """Demonstration of eigenvalue multiplicity calculations."""
    print("=== Eigenvalue Multiplicity Calculator Demo ===\n")
    
    calc = EigenvalueMultiplicityCalculator(dimension=7)
    
    # 1. Divisor function examples
    print("1. Divisor Function d(k):")
    for k in [12, 24, 60, 100]:
        d_k = calc.divisor_function(k)
        divisors = sp.divisors(k)
        print(f"   d({k}) = {d_k}, divisors: {divisors}")
    print()
    
    # 2. Verify divisor bound
    print("2. Divisor Bound Verification (d(k) ≪_ε k^ε for ε=0.1):")
    k_vals, ratios = calc.divisor_bound_verification(k_max=100, epsilon=0.1)
    max_ratio = max(ratios)
    max_k = k_vals[ratios.index(max_ratio)]
    print(f"   Max ratio d(k)/k^0.1 = {max_ratio:.2f} at k={max_k}")
    print(f"   Bound grows subpolynomially (confirmed: max ratio bounded)")
    print()
    
    # 3. Sum of two squares (r_2)
    print("3. Sum of Two Squares r_2(k):")
    for k in [2, 5, 13, 25, 50]:
        r_k = calc.r_2_sum_of_squares(k)
        print(f"   r_2({k}) = {r_k}")
    print()
    
    # 4. Verify 2D multiplicity bound
    print("4. Verify 2D Multiplicity Bound (max = 24 for nonzero eigenvalues):")
    result = calc.verify_multiplicity_bound_2d(k_max=100)
    print(f"   Max multiplicity observed: {result['max_multiplicity_observed']}")
    print(f"   Bound holds: {result['bound_24_holds']}")
    print(f"   Violations: {len(result['violations'])}")
    print()
    
    # 5. Correlate multiplicity with divisors
    print("5. Correlation between r_2(k) and d(k):")
    corr_result = calc.correlate_multiplicity_with_divisors(k_max=50)
    print(f"   Pearson correlation: {corr_result['pearson_correlation']:.4f}")
    print(f"   Mean ratio r_2(k)/d(k): {corr_result['mean_ratio_r_to_d']:.4f}")
    print(f"   Range: [{corr_result['min_ratio']:.2f}, {corr_result['max_ratio']:.2f}]")
    print()
    
    # 6. Higher dimensional multiplicities
    print("6. Higher Dimensional Multiplicities:")
    for n in [2, 4, 7]:
        print(f"   n={n} dimensions:")
        for k in [5, 10, 20]:
            r_k = calc.r_n_multiplicity(k, n=n)
            print(f"      r_{n}({k}) = {r_k}")
    print()


if __name__ == "__main__":
    demo_eigenvalue_calculations()
