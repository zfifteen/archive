#!/usr/bin/env python3
"""
Conic Section Integration with GVA and Monte Carlo Framework

Integrates conic-based factorization methods with existing geometric
factorization approaches (GVA, Monte Carlo, Gaussian lattice).

Key integrations:
- Conic candidate builders for GVA
- Monte Carlo sampling over conic-bounded regions
- Gaussian lattice points on Pell hyperbolas
- Z5D curvature weighting for conic intersections
"""

import math
from typing import List, Tuple, Optional, Dict
from mpmath import mp, mpf
import numpy as np

from conic_sections import (
    ConicFactorization,
    FermatFactorization,
    PellEquation,
    QuadraticForms
)

# Import existing framework components
try:
    from gaussian_lattice import GaussianIntegerLattice
    GAUSSIAN_AVAILABLE = True
except ImportError:
    GAUSSIAN_AVAILABLE = False

try:
    from monte_carlo import FactorizationMonteCarloEnhancer
    MONTE_CARLO_AVAILABLE = True
except ImportError:
    MONTE_CARLO_AVAILABLE = False

try:
    from z5d_axioms import Z5DAxioms
    Z5D_AVAILABLE = True
except ImportError:
    Z5D_AVAILABLE = False

# Constants
PHI = (1 + math.sqrt(5)) / 2
E2 = math.exp(2)


class ConicGVAIntegration:
    """
    Integration of conic section methods with Geodesic Validation Assault (GVA).
    
    Combines hyperbola-based candidate generation with GVA's geometric
    distance metrics for enhanced factorization.
    """
    
    def __init__(self, precision_dps: int = 50):
        """
        Initialize conic-GVA integration.
        
        Args:
            precision_dps: Decimal places for mpmath
        """
        self.precision_dps = precision_dps
        mp.dps = precision_dps
        
        self.conic_fact = ConicFactorization(precision_dps)
        
        if Z5D_AVAILABLE:
            self.z5d = Z5DAxioms(precision_dps)
        else:
            self.z5d = None
    
    def conic_candidates_with_z5d_curvature(
        self,
        N: int,
        num_candidates: int = 100,
        k: float = 0.3
    ) -> List[Tuple[int, float]]:
        """
        Generate conic-based candidates with Z5D curvature weighting.
        
        Combines:
        - Hyperbola lattice points (x² - y² = N)
        - Z5D curvature κ(n) = d(n)·ln(n+1)/e²
        - Geometric resolution θ'(n, k)
        
        Args:
            N: Integer to factor
            num_candidates: Number of candidates to generate
            k: Geometric resolution parameter (default: 0.3)
        
        Returns:
            List of (candidate, weight) tuples ordered by geometric importance
        """
        # Get base conic candidates
        candidates = self.conic_fact.generate_conic_candidates(N, num_candidates * 2)
        
        # Apply Z5D weighting if available
        weighted_candidates = []
        
        for c in candidates:
            if self.z5d:
                # Approximate prime density: d(n) ≈ 1/ln(n)
                d_n = 1.0 / math.log(max(c, 3))
                
                # Compute Z5D curvature
                kappa = float(self.z5d.curvature(c, mpf(d_n)))
                
                # Compute geometric resolution
                theta_prime = float(self.z5d.geometric_resolution(c, k))
                
                # Combined weight (higher is better)
                weight = kappa * theta_prime
            else:
                # Fallback: distance from √N
                sqrt_n = math.sqrt(N)
                weight = 1.0 / (1.0 + abs(c - sqrt_n))
            
            weighted_candidates.append((c, weight))
        
        # Sort by weight (descending)
        weighted_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return weighted_candidates[:num_candidates]
    
    def factorize_with_conic_gva(
        self,
        N: int,
        max_candidates: int = 1000,
        strategies: List[str] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Attempt factorization using combined conic + GVA approach.
        
        Args:
            N: Integer to factor
            max_candidates: Maximum candidates to try
            strategies: Conic strategies to use
        
        Returns:
            (p, q) factors if found, None otherwise
        """
        # Try direct conic factorization first
        result = self.conic_fact.factorize_via_conics(N, strategies)
        if result is not None:
            return result
        
        # Get Z5D-weighted candidates
        weighted_candidates = self.conic_candidates_with_z5d_curvature(
            N, num_candidates=max_candidates
        )
        
        # Try each candidate
        for candidate, weight in weighted_candidates:
            if candidate > 1 and N % candidate == 0:
                other = N // candidate
                if other > 1:
                    return (min(candidate, other), max(candidate, other))
        
        return None


class ConicMonteCarloIntegration:
    """
    Integration of conic sections with Monte Carlo sampling.
    
    Implements Monte Carlo sampling over conic-bounded regions for
    variance-reduced candidate generation.
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize conic-Monte Carlo integration.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.fermat = FermatFactorization()
    
    def sample_on_hyperbola(
        self,
        N: int,
        num_samples: int = 1000,
        sampling_mode: str = 'uniform'
    ) -> List[Tuple[int, int]]:
        """
        Monte Carlo sampling of lattice points near hyperbola x² - y² = N.
        
        Args:
            N: The constant value
            num_samples: Number of samples to generate
            sampling_mode: 'uniform', 'phi-biased', or 'stratified'
        
        Returns:
            List of (x, y) approximate lattice points
        """
        sqrt_n = math.sqrt(N)
        samples = []
        
        # Sample x values around √N
        if sampling_mode == 'uniform':
            x_samples = self.rng.uniform(sqrt_n, sqrt_n + 100, num_samples)
        elif sampling_mode == 'phi-biased':
            # φ-biased sampling for better coverage
            x_samples = sqrt_n + self.rng.exponential(PHI, num_samples)
        elif sampling_mode == 'stratified':
            # Stratified sampling
            strata = 10
            per_stratum = num_samples // strata
            x_samples = []
            for i in range(strata):
                low = sqrt_n + i * 10
                high = sqrt_n + (i + 1) * 10
                x_samples.extend(self.rng.uniform(low, high, per_stratum))
        else:
            raise ValueError(f"Unknown sampling mode: {sampling_mode}")
        
        # For each x, compute corresponding y from hyperbola
        for x in x_samples:
            x_int = int(round(x))
            y_squared = x_int * x_int - N
            
            if y_squared >= 0:
                y_int = int(round(math.sqrt(y_squared)))
                
                # Verify it's close to the hyperbola
                if abs(x_int * x_int - y_int * y_int - N) < 100:
                    samples.append((x_int, y_int))
        
        return samples
    
    def monte_carlo_conic_candidates(
        self,
        N: int,
        num_samples: int = 1000,
        mode: str = 'phi-biased'
    ) -> List[int]:
        """
        Generate candidates using Monte Carlo sampling on conics.
        
        Args:
            N: Integer to factor
            num_samples: Number of Monte Carlo samples
            mode: Sampling mode
        
        Returns:
            List of candidate factors
        """
        # Sample points on hyperbola
        samples = self.sample_on_hyperbola(N, num_samples, mode)
        
        # Extract candidate factors
        candidates = set()
        for x, y in samples:
            p = x - y
            q = x + y
            
            if p > 1 and p < N:
                candidates.add(p)
            if q > 1 and q < N:
                candidates.add(q)
        
        # Sort by proximity to √N
        sqrt_n = math.sqrt(N)
        candidates_list = sorted(list(candidates), key=lambda c: abs(c - sqrt_n))
        
        return candidates_list


class ConicGaussianLatticeIntegration:
    """
    Integration of conic sections with Gaussian integer lattice ℤ[i].
    
    Extends Pell hyperbolas to Gaussian integers and applies Epstein
    zeta functions for lattice-enhanced factorization.
    """
    
    def __init__(self, precision_dps: int = 50):
        """
        Initialize conic-Gaussian lattice integration.
        
        Args:
            precision_dps: Decimal places for mpmath
        """
        self.precision_dps = precision_dps
        mp.dps = precision_dps
        
        if GAUSSIAN_AVAILABLE:
            self.lattice = GaussianIntegerLattice(precision_dps)
        else:
            self.lattice = None
    
    def gaussian_pell_solutions(
        self,
        d: int,
        num_solutions: int = 10
    ) -> List[Tuple[complex, float]]:
        """
        Find Pell equation solutions in Gaussian integers.
        
        Extends x² - dy² = 1 to ℤ[i] for enhanced factorization.
        
        Args:
            d: Pell parameter
            num_solutions: Number of solutions to find
        
        Returns:
            List of (z, norm) where z ∈ ℤ[i] and norm = |z|²
        """
        try:
            pell = PellEquation(d)
            solutions_real = pell.generate_solutions(num_solutions)
            
            # Convert to Gaussian integers
            gaussian_solutions = []
            for x, y in solutions_real:
                # Create Gaussian integer z = x + yi
                z = complex(x, y)
                norm = abs(z) ** 2
                gaussian_solutions.append((z, norm))
            
            return gaussian_solutions
        
        except (ValueError, OverflowError):
            return []
    
    def lattice_enhanced_conic_distance(
        self,
        candidate: int,
        N: int,
        lattice_scale: float = 0.5
    ) -> float:
        """
        Compute lattice-enhanced distance for conic candidates.
        
        Combines:
        - Euclidean distance to √N
        - Gaussian lattice structure via Epstein zeta
        
        Args:
            candidate: Candidate factor
            N: Number being factored
            lattice_scale: Lattice contribution weight
        
        Returns:
            Enhanced distance metric
        """
        sqrt_n = math.sqrt(N)
        
        # Base Euclidean distance
        euclidean_dist = abs(candidate - sqrt_n)
        
        if self.lattice is None:
            return euclidean_dist
        
        # Gaussian lattice enhancement
        z1 = complex(candidate, 0)
        z2 = complex(sqrt_n, 0)
        
        lattice_dist = self.lattice.lattice_enhanced_distance(
            z1, z2, lattice_scale
        )
        
        return float(lattice_dist)


def demonstrate_conic_integration():
    """
    Demonstrate conic section integration with existing framework.
    """
    print("=" * 70)
    print("Conic Section Framework Integration Demonstration")
    print("=" * 70)
    
    test_cases = [
        (143, "11 × 13"),
        (899, "29 × 31"),
        (10403, "101 × 103"),
    ]
    
    # Test GVA integration
    print("\n--- Conic-GVA Integration ---")
    gva_integration = ConicGVAIntegration()
    
    for N, expected in test_cases:
        result = gva_integration.factorize_with_conic_gva(N, max_candidates=100)
        if result:
            p, q = result
            print(f"✓ N={N}: {p} × {q} (expected: {expected})")
        else:
            print(f"✗ N={N}: No factors found")
        
        # Show Z5D-weighted candidates
        if Z5D_AVAILABLE:
            weighted = gva_integration.conic_candidates_with_z5d_curvature(N, num_candidates=5)
            print(f"  Top 5 Z5D-weighted candidates:")
            for i, (c, w) in enumerate(weighted[:5]):
                is_factor = "✓" if N % c == 0 else " "
                print(f"    {is_factor} {i+1}. {c} (weight: {w:.6f})")
    
    # Test Monte Carlo integration
    print("\n--- Conic-Monte Carlo Integration ---")
    mc_integration = ConicMonteCarloIntegration(seed=42)
    
    for N, expected in test_cases[:2]:  # Test on smaller cases
        candidates = mc_integration.monte_carlo_conic_candidates(N, num_samples=500)
        print(f"N={N}: Generated {len(candidates)} Monte Carlo candidates")
        
        # Check if factors are in candidates
        sqrt_n = int(math.sqrt(N))
        factors_found = [c for c in candidates[:20] if N % c == 0]
        if factors_found:
            print(f"  ✓ Found factors: {factors_found}")
        else:
            print(f"  - No factors in top 20 candidates")
    
    # Test Gaussian lattice integration
    if GAUSSIAN_AVAILABLE:
        print("\n--- Conic-Gaussian Lattice Integration ---")
        lattice_integration = ConicGaussianLatticeIntegration()
        
        for N in [143, 899]:
            sqrt_n = int(math.sqrt(N))
            
            # Compute lattice-enhanced distance for candidates
            candidates = [sqrt_n - 2, sqrt_n - 1, sqrt_n, sqrt_n + 1, sqrt_n + 2]
            
            print(f"N={N} (√N ≈ {sqrt_n}):")
            for c in candidates:
                dist = lattice_integration.lattice_enhanced_conic_distance(c, N)
                is_factor = "✓" if N % c == 0 else " "
                print(f"  {is_factor} {c}: distance = {dist:.6f}")


if __name__ == "__main__":
    demonstrate_conic_integration()
