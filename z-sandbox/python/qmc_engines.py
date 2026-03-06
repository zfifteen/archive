#!/usr/bin/env python3
"""
QMC Engines for Factorization Analysis

Implements various Quasi-Monte Carlo (QMC) engines for RSA factorization:
- Monte Carlo (MC): Baseline uniform random sampling
- Sobol + Owen: Low-discrepancy sequence with Owen scrambling
- Rank-1 Lattice (Korobov): Lattice-based QMC

Supports Z-Framework bias integration via κ(n) and θ′(n,k).
"""

import numpy as np
import math
from typing import List, Tuple, Optional, Dict
from scipy.stats.qmc import Sobol
try:
    from utils.z_framework import apply_z_bias, kappa, theta_prime
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.z_framework import apply_z_bias, kappa, theta_prime


class QMCEngine:
    """Base class for QMC engines."""
    
    def __init__(self, dimension: int = 1, seed: Optional[int] = None):
        """
        Initialize QMC engine.
        
        Args:
            dimension: Dimensionality of the sampling space
            seed: Random seed for reproducibility
        """
        self.dimension = dimension
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
    
    def generate(self, n_samples: int) -> np.ndarray:
        """
        Generate QMC points.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Array of shape (n_samples, dimension) with values in [0, 1]
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    def generate_candidates(
        self, 
        N: int, 
        n_samples: int, 
        bias: Optional[str] = None,
        k: float = 0.3
    ) -> np.ndarray:
        """
        Generate factorization candidates around √N.
        
        Args:
            N: RSA modulus to factor
            n_samples: Number of candidates to generate
            bias: Bias type ('z-framework' or None)
            k: Resolution exponent for θ′(n,k) (default: 0.3)
            
        Returns:
            Array of candidate integers around √N
        """
        # Generate base QMC points
        points = self.generate(n_samples)
        
        # Apply Z-bias if requested
        if bias == 'z-framework':
            candidates = apply_z_bias(points, N, k)
        else:
            # Standard scaling around √N
            sqrt_N = float(N ** 0.5) if N > 2**53 else math.sqrt(N)
            bit_length = N.bit_length()
            
            if bit_length <= 64:
                spread = 0.15
            elif bit_length <= 128:
                spread = 0.10
            else:
                spread = 0.05
            
            candidates = sqrt_N * (1 - spread + 2 * spread * points[:, 0])
        
        # Convert to integers and ensure uniqueness
        # For large RSA numbers, use Python integers to avoid overflow
        if N > 2**63:
            # Use object dtype for large integers
            candidates_int = [int(x) for x in candidates]
            candidates = np.array(sorted(set(candidates_int)))
        else:
            candidates = np.unique(candidates.astype(int))
        
        return candidates


class MCEngine(QMCEngine):
    """Monte Carlo engine with uniform random sampling."""
    
    def generate(self, n_samples: int) -> np.ndarray:
        """Generate uniform random samples in [0, 1]^d."""
        return np.random.random((n_samples, self.dimension))


class SobolOwenEngine(QMCEngine):
    """Sobol sequence with Owen scrambling for low-discrepancy sampling."""
    
    def __init__(self, dimension: int = 1, seed: Optional[int] = None, scramble: bool = True):
        """
        Initialize Sobol+Owen engine.
        
        Args:
            dimension: Dimensionality of the sampling space
            seed: Random seed for scrambling
            scramble: Whether to apply Owen scrambling (default: True)
        """
        super().__init__(dimension, seed)
        self.scramble = scramble
        self.sobol = Sobol(d=dimension, scramble=scramble, seed=seed)
    
    def generate(self, n_samples: int) -> np.ndarray:
        """Generate Sobol sequence points with optional Owen scrambling."""
        return self.sobol.random(n_samples)


class Rank1LatticeEngine(QMCEngine):
    """Rank-1 lattice (Korobov) QMC engine."""
    
    def __init__(self, dimension: int = 1, seed: Optional[int] = None, lattice_type: str = 'korobov'):
        """
        Initialize Rank-1 Lattice engine.
        
        Args:
            dimension: Dimensionality of the sampling space
            seed: Random seed for generator vector selection
            lattice_type: Type of lattice ('korobov' or 'fibonacci')
        """
        super().__init__(dimension, seed)
        self.lattice_type = lattice_type
        self.generator = self._compute_generator()
    
    def _compute_generator(self) -> np.ndarray:
        """Compute generator vector for rank-1 lattice."""
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        
        if self.lattice_type == 'korobov':
            # Korobov generator: a^k mod n for some good a
            # Use golden ratio-based selection
            a = int(phi * 1000) % 997  # Use a prime close to sqrt(n)
            return np.array([pow(a, k, 997) / 997.0 for k in range(self.dimension)])
        elif self.lattice_type == 'fibonacci':
            # Fibonacci-based generator
            return np.array([1.0 / ((k + 1) * phi) % 1.0 for k in range(self.dimension)])
        else:
            raise ValueError(f"Unknown lattice type: {self.lattice_type}")
    
    def generate(self, n_samples: int) -> np.ndarray:
        """Generate rank-1 lattice points."""
        points = np.zeros((n_samples, self.dimension))
        for i in range(n_samples):
            for j in range(self.dimension):
                points[i, j] = (i * self.generator[j]) % 1.0
        return points


def create_engine(
    engine_type: str,
    dimension: int = 1,
    seed: Optional[int] = None,
    scramble: Optional[bool] = None,
    lattice_type: Optional[str] = None
) -> QMCEngine:
    """
    Factory function to create QMC engines.
    
    Args:
        engine_type: Type of engine ('mc', 'sobol', 'rank1')
        dimension: Dimensionality of the sampling space
        seed: Random seed
        scramble: Whether to scramble (for Sobol)
        lattice_type: Type of lattice (for Rank-1)
        
    Returns:
        Configured QMC engine
    """
    engine_type = engine_type.lower()
    
    if engine_type == 'mc':
        return MCEngine(dimension=dimension, seed=seed)
    elif engine_type == 'sobol':
        scramble = scramble if scramble is not None else True
        return SobolOwenEngine(dimension=dimension, seed=seed, scramble=scramble)
    elif engine_type == 'rank1':
        lattice_type = lattice_type if lattice_type is not None else 'korobov'
        return Rank1LatticeEngine(dimension=dimension, seed=seed, lattice_type=lattice_type)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")


if __name__ == "__main__":
    print("QMC Engines Demo")
    print("=" * 60)
    
    # Test parameters
    N = 899  # 29 × 31
    n_samples = 100
    seed = 42
    
    # Test each engine
    engines = {
        'MC': create_engine('mc', seed=seed),
        'Sobol+Owen': create_engine('sobol', seed=seed, scramble=True),
        'Rank-1 Korobov': create_engine('rank1', seed=seed, lattice_type='korobov')
    }
    
    for name, engine in engines.items():
        print(f"\n{name} Engine:")
        
        # Generate without bias
        candidates_base = engine.generate_candidates(N, n_samples, bias=None)
        print(f"  Without Z-bias: {len(candidates_base)} unique candidates")
        print(f"    Range: [{candidates_base.min():.0f}, {candidates_base.max():.0f}]")
        print(f"    √N = {math.sqrt(N):.2f}")
        
        # Generate with Z-bias
        candidates_z = engine.generate_candidates(N, n_samples, bias='z-framework', k=0.3)
        print(f"  With Z-bias: {len(candidates_z)} unique candidates")
        print(f"    Range: [{candidates_z.min():.0f}, {candidates_z.max():.0f}]")
        
        # Check if factors are in candidates
        factors = [29, 31]
        found_base = [f for f in factors if f in candidates_base]
        found_z = [f for f in factors if f in candidates_z]
        print(f"  Factors found (base): {found_base}")
        print(f"  Factors found (Z): {found_z}")
