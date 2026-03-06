#!/usr/bin/env python3
"""
Conic Sections Module for Integer Factorization

Implements conic section equations (ellipse, parabola, hyperbola) and their
applications to integer factorization via Diophantine equations and lattice methods.

Mathematical Foundation:
- Circle: x² + y² = a²
- Ellipse: x²/a² + y²/b² = 1
- Parabola: y² = 4ax
- Hyperbola: x²/a² - y²/b² = 1

Factorization Applications:
- Fermat's method: x² - y² = N → (x-y)(x+y) = N
- Pell equation: x² - dy² = N
- Multiple forms: mx² ± ny² = N
- Conic intersections for factor discovery

Integration with z-sandbox framework:
- Enhances GVA with conic-based candidate generation
- Extends Gaussian lattice methods with Pell hyperbolas
- Provides group structure for cryptographic applications
- Supports Monte Carlo sampling over conic-bounded regions

References:
- https://onlinelibrary.wiley.com/doi/10.1155/2022/6360264 (Fermat factorization)
- https://www.researchgate.net/publication/297593522_Using_Conic_Sections_to_Factor_Integers
- https://fse.studenttheses.ub.rug.nl/22789/1/bMATH_2020_EelkemaDSL.pdf
- https://www.nature.com/articles/s41598-025-00334-6 (Conic curve cryptography)
"""

import math
from typing import Tuple, List, Optional, Dict, Set
from mpmath import mp, mpf, sqrt as mp_sqrt, power, log
import numpy as np

# Set high precision for numerical computations
mp.dps = 50

# Universal constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio
E2 = math.exp(2)  # e² invariant


class ConicSections:
    """
    Conic section equations and properties.
    
    Implements standard conic forms with focus on integer factorization
    applications via Diophantine solutions and lattice point searches.
    """
    
    def __init__(self, precision_dps: int = 50):
        """
        Initialize conic sections handler.
        
        Args:
            precision_dps: Decimal places for mpmath (default: 50)
        """
        self.precision_dps = precision_dps
        mp.dps = precision_dps
    
    @staticmethod
    def eccentricity(conic_type: str, a: float, b: float = None) -> float:
        """
        Calculate eccentricity of a conic section.
        
        Eccentricity determines the type:
        - e = 0: Circle
        - 0 < e < 1: Ellipse
        - e = 1: Parabola
        - e > 1: Hyperbola
        
        Args:
            conic_type: One of 'circle', 'ellipse', 'parabola', 'hyperbola'
            a: Semi-major axis (or parameter)
            b: Semi-minor axis (for ellipse/hyperbola)
        
        Returns:
            Eccentricity value
        """
        if conic_type == 'circle':
            return 0.0
        elif conic_type == 'parabola':
            return 1.0
        elif conic_type == 'ellipse':
            if b is None or a == 0:
                raise ValueError("Ellipse requires both a and b parameters")
            return math.sqrt(1 - (b**2 / a**2))
        elif conic_type == 'hyperbola':
            if b is None or a == 0:
                raise ValueError("Hyperbola requires both a and b parameters")
            return math.sqrt(1 + (b**2 / a**2))
        else:
            raise ValueError(f"Unknown conic type: {conic_type}")
    
    @staticmethod
    def is_on_circle(x: int, y: int, r: int) -> bool:
        """Check if (x, y) lies on circle x² + y² = r²."""
        return x*x + y*y == r*r
    
    @staticmethod
    def is_on_ellipse(x: float, y: float, a: float, b: float) -> bool:
        """Check if (x, y) lies on ellipse x²/a² + y²/b² = 1."""
        return abs((x*x)/(a*a) + (y*y)/(b*b) - 1.0) < 1e-10
    
    @staticmethod
    def is_on_parabola(x: float, y: float, a: float) -> bool:
        """Check if (x, y) lies on parabola y² = 4ax."""
        return abs(y*y - 4*a*x) < 1e-10
    
    @staticmethod
    def is_on_hyperbola(x: float, y: float, a: float, b: float) -> bool:
        """Check if (x, y) lies on hyperbola x²/a² - y²/b² = 1."""
        return abs((x*x)/(a*a) - (y*y)/(b*b) - 1.0) < 1e-10


class FermatFactorization:
    """
    Fermat's factorization method using hyperbola x² - y² = N.
    
    For odd composite N, find integers x, y such that:
        x² - y² = N
        (x - y)(x + y) = N
    
    This corresponds to finding lattice points on the hyperbola.
    """
    
    def __init__(self):
        """Initialize Fermat factorization engine."""
        pass
    
    @staticmethod
    def factorize(N: int, max_iterations: int = 10000) -> Optional[Tuple[int, int]]:
        """
        Factor N using Fermat's method (hyperbola x² - y² = N).
        
        Algorithm:
        1. Start with x = ceil(√N)
        2. Compute y² = x² - N
        3. If y is integer, factors are (x-y, x+y)
        4. Otherwise, increment x and repeat
        
        Args:
            N: Odd composite integer to factor
            max_iterations: Maximum iterations (default: 10000)
        
        Returns:
            (p, q) factors if found, None otherwise
        """
        if N <= 1:
            return None
        
        # N must be odd for standard Fermat method
        if N % 2 == 0:
            return (2, N // 2)
        
        # Start at ceiling of sqrt(N)
        x = int(math.ceil(math.sqrt(N)))
        
        for _ in range(max_iterations):
            y_squared = x * x - N
            
            # Check if y_squared is a perfect square
            if y_squared < 0:
                x += 1
                continue
            
            y = int(math.sqrt(y_squared))
            
            # Verify it's a perfect square
            if y * y == y_squared:
                # Found factors
                p = x - y
                q = x + y
                
                # Validate
                if p * q == N and p > 1 and q > 1:
                    return (min(p, q), max(p, q))
            
            x += 1
        
        return None
    
    @staticmethod
    def lattice_points_on_hyperbola(N: int, max_x: int = None) -> List[Tuple[int, int]]:
        """
        Find integer lattice points (x, y) on hyperbola x² - y² = N.
        
        Args:
            N: The constant value
            max_x: Maximum x value to search (default: 2*√N)
        
        Returns:
            List of (x, y) lattice points
        """
        if max_x is None:
            max_x = int(2 * math.sqrt(N)) + 100
        
        points = []
        x_start = int(math.ceil(math.sqrt(N)))
        
        for x in range(x_start, max_x):
            y_squared = x * x - N
            if y_squared < 0:
                continue
            
            y = int(math.sqrt(y_squared))
            if y * y == y_squared:
                points.append((x, y))
        
        return points


class PellEquation:
    """
    Pell equation solver: x² - dy² = 1 (or N for generalized form).
    
    The Pell equation forms a hyperbola structure useful for factorization
    and provides group operations analogous to elliptic curves.
    
    Applications:
    - Integer factorization via Pell hyperbolas
    - Cryptographic group structures
    - Diophantine approximations
    """
    
    def __init__(self, d: int):
        """
        Initialize Pell equation solver.
        
        Args:
            d: The parameter in x² - dy² = 1
        """
        if d <= 0:
            raise ValueError("d must be positive")
        if self._is_perfect_square(d):
            raise ValueError("d must not be a perfect square")
        
        self.d = d
    
    @staticmethod
    def _is_perfect_square(n: int) -> bool:
        """Check if n is a perfect square."""
        if n < 0:
            return False
        root = int(math.sqrt(n))
        return root * root == n
    
    def find_fundamental_solution(self) -> Optional[Tuple[int, int]]:
        """
        Find the fundamental solution (x₁, y₁) to x² - dy² = 1.
        
        Uses continued fraction expansion of √d.
        
        Returns:
            (x, y) fundamental solution or None if not found
        """
        # Continued fraction expansion of sqrt(d)
        m, d_val, a = 0, 1, int(math.sqrt(self.d))
        a0 = a
        
        # Track convergents
        p_prev, p_curr = 1, a
        q_prev, q_curr = 0, 1
        
        # Iterate until we find a solution
        for _ in range(1000):  # Safety limit
            m = d_val * a - m
            d_val = (self.d - m * m) // d_val
            a = (a0 + m) // d_val
            
            # Update convergents
            p_prev, p_curr = p_curr, a * p_curr + p_prev
            q_prev, q_curr = q_curr, a * q_curr + q_prev
            
            # Check if (p_curr, q_curr) is a solution
            if p_curr * p_curr - self.d * q_curr * q_curr == 1:
                return (p_curr, q_curr)
        
        return None
    
    def generate_solutions(self, num_solutions: int = 10) -> List[Tuple[int, int]]:
        """
        Generate multiple solutions using the fundamental solution.
        
        If (x₁, y₁) is fundamental, then:
        (xₙ, yₙ) = (x₁, y₁)^n via group operation
        
        Args:
            num_solutions: Number of solutions to generate
        
        Returns:
            List of (x, y) solutions
        """
        fundamental = self.find_fundamental_solution()
        if fundamental is None:
            return []
        
        x1, y1 = fundamental
        solutions = [(x1, y1)]
        
        xn, yn = x1, y1
        for _ in range(num_solutions - 1):
            # Group operation: (xₙ, yₙ) * (x₁, y₁)
            xn_new = x1 * xn + self.d * y1 * yn
            yn_new = x1 * yn + y1 * xn
            
            solutions.append((xn_new, yn_new))
            xn, yn = xn_new, yn_new
        
        return solutions
    
    def factorize_using_pell(self, N: int, max_solutions: int = 50) -> Optional[Tuple[int, int]]:
        """
        Attempt to factor N using Pell equation solutions.
        
        Strategy: Use solutions to x² - dy² = 1 to find factors of N
        via gcd(x ± y√d, N) calculations.
        
        Args:
            N: Integer to factor
            max_solutions: Maximum Pell solutions to try
        
        Returns:
            (p, q) factors if found, None otherwise
        """
        solutions = self.generate_solutions(max_solutions)
        
        for x, y in solutions:
            # Try various combinations
            for candidate in [x - y, x + y, abs(x - y * int(math.sqrt(self.d)))]:
                if candidate <= 1 or candidate >= N:
                    continue
                
                factor = math.gcd(candidate, N)
                if 1 < factor < N:
                    return (factor, N // factor)
        
        return None


class QuadraticForms:
    """
    Multiple quadratic forms mx² ± ny² = N for factorization.
    
    Expressing N in different quadratic forms enables factorization
    through conic intersections and Diophantine analysis.
    """
    
    def __init__(self):
        """Initialize quadratic forms solver."""
        pass
    
    @staticmethod
    def represent_as_sum_of_squares(N: int, max_val: int = None) -> List[Tuple[int, int]]:
        """
        Find all representations of N as x² + y².
        
        Args:
            N: Integer to represent
            max_val: Maximum value to search (default: √N)
        
        Returns:
            List of (x, y) pairs where x² + y² = N
        """
        if max_val is None:
            max_val = int(math.sqrt(N)) + 1
        
        representations = []
        
        for x in range(max_val + 1):
            y_squared = N - x * x
            if y_squared < 0:
                break
            
            y = int(math.sqrt(y_squared))
            if y * y == y_squared:
                representations.append((x, y))
        
        return representations
    
    @staticmethod
    def represent_as_difference_of_squares(N: int, max_val: int = None) -> List[Tuple[int, int]]:
        """
        Find all representations of N as x² - y² (Fermat method).
        
        Args:
            N: Integer to represent
            max_val: Maximum x value to search
        
        Returns:
            List of (x, y) pairs where x² - y² = N
        """
        return FermatFactorization.lattice_points_on_hyperbola(N, max_val)
    
    @staticmethod
    def represent_as_mx2_plus_ny2(N: int, m: int, n: int, max_val: int = None) -> List[Tuple[int, int]]:
        """
        Find representations of N as mx² + ny².
        
        Args:
            N: Integer to represent
            m, n: Coefficients
            max_val: Maximum value to search
        
        Returns:
            List of (x, y) pairs where mx² + ny² = N
        """
        if max_val is None:
            max_val = int(math.sqrt(N / min(m, n))) + 10
        
        representations = []
        
        for x in range(max_val + 1):
            remainder = N - m * x * x
            if remainder < 0:
                break
            
            if remainder % n == 0:
                y_squared = remainder // n
                y = int(math.sqrt(y_squared))
                if y * y == y_squared:
                    representations.append((x, y))
        
        return representations
    
    @staticmethod
    def represent_as_mx2_minus_ny2(N: int, m: int, n: int, max_val: int = None) -> List[Tuple[int, int]]:
        """
        Find representations of N as mx² - ny².
        
        Args:
            N: Integer to represent
            m, n: Coefficients
            max_val: Maximum value to search
        
        Returns:
            List of (x, y) pairs where mx² - ny² = N
        """
        if max_val is None:
            max_val = int(math.sqrt(N / m)) + 100
        
        representations = []
        
        for x in range(int(math.sqrt(N / m)), max_val + 1):
            remainder = m * x * x - N
            if remainder < 0:
                continue
            
            if remainder % n == 0:
                y_squared = remainder // n
                y = int(math.sqrt(y_squared))
                if y * y == y_squared:
                    representations.append((x, y))
        
        return representations


class ConicFactorization:
    """
    Factorization using conic section intersections and multiple forms.
    
    Strategy:
    1. Express N in multiple quadratic forms
    2. Find conic intersections
    3. Extract factors via Diophantine solutions
    """
    
    def __init__(self, precision_dps: int = 50):
        """
        Initialize conic factorization engine.
        
        Args:
            precision_dps: Decimal places for mpmath
        """
        self.precision_dps = precision_dps
        mp.dps = precision_dps
        self.fermat = FermatFactorization()
        self.quadratic = QuadraticForms()
    
    def factorize_via_conics(self, N: int, strategies: List[str] = None) -> Optional[Tuple[int, int]]:
        """
        Attempt factorization using multiple conic-based strategies.
        
        Args:
            N: Integer to factor
            strategies: List of strategies to try (default: all)
                - 'fermat': Standard Fermat method
                - 'pell': Pell equation approach
                - 'sum_of_squares': x² + y² forms
                - 'multiple_forms': Try various mx² ± ny² forms
        
        Returns:
            (p, q) factors if found, None otherwise
        """
        if strategies is None:
            strategies = ['fermat', 'pell', 'sum_of_squares', 'multiple_forms']
        
        # Try Fermat factorization
        if 'fermat' in strategies:
            result = self.fermat.factorize(N)
            if result is not None:
                return result
        
        # Try Pell equation for various d values
        if 'pell' in strategies:
            for d in [2, 3, 5, 6, 7, 10]:
                try:
                    pell = PellEquation(d)
                    result = pell.factorize_using_pell(N, max_solutions=20)
                    if result is not None:
                        return result
                except (ValueError, OverflowError):
                    continue
        
        # Try sum of squares representations
        if 'sum_of_squares' in strategies:
            reps = self.quadratic.represent_as_sum_of_squares(N)
            for x, y in reps:
                if x > 0 and y > 0:
                    # Check if this leads to factorization
                    factor = math.gcd(x + y, N)
                    if 1 < factor < N:
                        return (factor, N // factor)
        
        # Try multiple quadratic forms
        if 'multiple_forms' in strategies:
            for m in [1, 2, 3]:
                for n in [1, 2, 3]:
                    # Try mx² + ny²
                    reps = self.quadratic.represent_as_mx2_plus_ny2(N, m, n)
                    for x, y in reps:
                        if x > 0 and y > 0:
                            factor = math.gcd(m*x + n*y, N)
                            if 1 < factor < N:
                                return (factor, N // factor)
                    
                    # Try mx² - ny²
                    reps = self.quadratic.represent_as_mx2_minus_ny2(N, m, n)
                    for x, y in reps:
                        if x > 0 and y > 0:
                            p = m*x - n*y
                            q = m*x + n*y
                            if p > 1 and q > 1 and p * q == N:
                                return (min(p, q), max(p, q))
        
        return None
    
    def generate_conic_candidates(self, N: int, num_candidates: int = 100) -> List[int]:
        """
        Generate factorization candidates using conic-based methods.
        
        Strategy:
        1. Find lattice points on hyperbola x² - y² ≈ N
        2. Extract candidate factors from (x-y, x+y)
        3. Order by proximity to √N
        
        Args:
            N: Integer to factor
            num_candidates: Number of candidates to generate
        
        Returns:
            List of candidate factors ordered by proximity to √N
        """
        candidates_with_priority = []
        sqrt_n = int(math.sqrt(N))
        
        # Fermat-style candidates from hyperbola (higher priority)
        points = self.fermat.lattice_points_on_hyperbola(N, max_x=sqrt_n + num_candidates)
        for x, y in points:
            p = x - y
            q = x + y
            if p > 1 and p < N:
                dist = abs(p - sqrt_n)
                candidates_with_priority.append((dist, p, 0))  # priority 0 = highest
            if q > 1 and q < N:
                dist = abs(q - sqrt_n)
                candidates_with_priority.append((dist, q, 0))
        
        # Add nearby values to √N (lower priority)
        for delta in range(-num_candidates//2, num_candidates//2):
            candidate = sqrt_n + delta
            if candidate > 1 and candidate < N:
                dist = abs(candidate - sqrt_n)
                candidates_with_priority.append((dist, candidate, 1))  # priority 1 = lower
        
        # Sort by (distance, priority, value) - closer first, then by priority
        candidates_with_priority.sort(key=lambda x: (x[0], x[2], x[1]))
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for dist, candidate, priority in candidates_with_priority:
            if candidate not in seen:
                seen.add(candidate)
                result.append(candidate)
                if len(result) >= num_candidates:
                    break
        
        return result


def demonstrate_conic_factorization():
    """
    Demonstrate conic section factorization methods.
    """
    print("=" * 70)
    print("Conic Sections Factorization Demonstration")
    print("=" * 70)
    
    # Test cases
    test_cases = [
        (143, "11 × 13"),
        (899, "29 × 31"),
        (1003, "17 × 59"),
        (10403, "101 × 103"),
    ]
    
    conic_fact = ConicFactorization()
    
    for N, expected in test_cases:
        print(f"\n--- Factoring N = {N} (expected: {expected}) ---")
        
        # Try Fermat method
        result = conic_fact.fermat.factorize(N)
        if result:
            p, q = result
            print(f"✓ Fermat method: {p} × {q}")
        else:
            print("✗ Fermat method: No factors found")
        
        # Try conic-based candidates
        candidates = conic_fact.generate_conic_candidates(N, num_candidates=20)
        print(f"Generated {len(candidates)} conic-based candidates")
        
        # Verify if true factors are in candidates
        sqrt_n = int(math.sqrt(N))
        for c in candidates[:10]:
            if N % c == 0:
                print(f"✓ Found factor {c} in candidates (rank: {candidates.index(c)})")
                break


if __name__ == "__main__":
    demonstrate_conic_factorization()
