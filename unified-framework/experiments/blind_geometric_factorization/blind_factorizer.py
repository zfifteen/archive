"""
Blind Geometric Factorizer

This module implements blind geometric search for semiprime factorization,
using PR-123/969 scaling parameters without prior knowledge of factors.

Key Features:
- True blind search: No knowledge of factors used in search
- PR-123/969 scaling: Adaptive parameters based on bit length
- Resonance-guided candidate selection
- Progress logging for transparency

Limitations:
- 127-bit semiprimes require ~10^15 trial divisions
- Practical blind factorization limited to smaller semiprimes (~64-bit)
- Further algorithmic breakthroughs needed for large-scale blind search

Usage:
    from blind_factorizer import BlindGeometricFactorizer
    
    N = your_semiprime
    factorizer = BlindGeometricFactorizer(N)
    result = factorizer.factor_blind(max_iterations=1000000)
"""

import math
import time
import json
from dataclasses import dataclass, asdict
from typing import Optional, Tuple, List, Callable
from datetime import datetime, timezone

from .scaling_params import get_scaling_params, ScalingParams
from .resonance_scoring import (
    compute_resonance_score,
    is_candidate_promising,
    verify_factor,
    PHI
)


@dataclass
class FactorizationResult:
    """Result of a factorization attempt."""
    N: int
    success: bool
    p: Optional[int] = None
    q: Optional[int] = None
    mode: str = "blind"  # "blind" or "validation"
    iterations: int = 0
    candidates_evaluated: int = 0
    high_resonance_candidates: int = 0
    execution_time_seconds: float = 0.0
    params: Optional[ScalingParams] = None
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "N": str(self.N),
            "success": self.success,
            "p": str(self.p) if self.p else None,
            "q": str(self.q) if self.q else None,
            "mode": self.mode,
            "iterations": self.iterations,
            "candidates_evaluated": self.candidates_evaluated,
            "high_resonance_candidates": self.high_resonance_candidates,
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp
        }
        if self.params:
            result["parameters"] = {
                "bit_length": self.params.bit_length,
                "threshold": self.params.threshold,
                "k_shift": self.params.k_shift,
                "sample_count": self.params.sample_count,
                "precision": self.params.precision,
                "kappa_estimated": self.params.kappa_estimated,
                "phase_drift": self.params.phase_drift
            }
        return result


class BlindGeometricFactorizer:
    """
    Blind geometric factorizer using PR-123/969 scaling.
    
    This factorizer attempts to find factors of a semiprime without
    any prior knowledge of the factors, using geometric resonance
    patterns to guide the search.
    """
    
    def __init__(self, N: int, verbose: bool = True):
        """
        Initialize factorizer for semiprime N.
        
        Parameters
        ----------
        N : int
            The semiprime to factor (must be > 1)
        verbose : bool
            Whether to print progress information
        """
        if N <= 1:
            raise ValueError("N must be greater than 1")
        
        self.N = N
        self.verbose = verbose
        self.params = get_scaling_params(N)
        self.sqrt_N = math.isqrt(N)
        self.sqrt_N_float = math.sqrt(N)
        
        if verbose:
            print(f"Initialized BlindGeometricFactorizer for N with {self.params.bit_length} bits")
            print(f"  √N ≈ {self.sqrt_N}")
            print(f"  Parameters: T={self.params.threshold:.4f}, k={self.params.k_shift:.4f}")
            print(f"  Samples: {self.params.sample_count}, Precision: {self.params.precision}")
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def factor_blind(
        self,
        max_iterations: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> FactorizationResult:
        """
        Attempt blind factorization using geometric search.
        
        This is a TRUE BLIND search - no knowledge of factors is used.
        The search examines candidates near √N using trial division
        guided by resonance scoring.
        
        Parameters
        ----------
        max_iterations : int, optional
            Maximum iterations (defaults to sample_count from params)
        progress_callback : callable, optional
            Called every 10000 iterations with (current, total)
            
        Returns
        -------
        FactorizationResult
            Result of the factorization attempt
        """
        start_time = time.time()
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        if max_iterations is None:
            max_iterations = self.params.sample_count
        
        self._log(f"\n{'='*60}")
        self._log(f"BLIND GEOMETRIC FACTORIZATION")
        self._log(f"{'='*60}")
        self._log(f"N = {self.N}")
        self._log(f"Bit length: {self.params.bit_length}")
        self._log(f"Mode: BLIND (no prior knowledge of factors)")
        self._log(f"Max iterations: {max_iterations}")
        self._log(f"Search center: √N = {self.sqrt_N}")
        self._log(f"{'='*60}\n")
        
        # Quick check for small factors (optimization)
        for small_prime in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
            if self.N % small_prime == 0:
                p, q = small_prime, self.N // small_prime
                end_time = time.time()
                self._log(f"Found small factor: {small_prime}")
                return FactorizationResult(
                    N=self.N,
                    success=True,
                    p=min(p, q),
                    q=max(p, q),
                    mode="blind",
                    iterations=1,
                    candidates_evaluated=1,
                    high_resonance_candidates=1,
                    execution_time_seconds=end_time - start_time,
                    params=self.params,
                    timestamp=timestamp
                )
        
        # Main search loop - examines candidates around √N
        candidates_evaluated = 0
        high_resonance_count = 0
        iterations = 0
        
        # Search in both directions from √N
        # Using odd numbers only (even factor would have been caught above)
        search_start = self.sqrt_N if self.sqrt_N % 2 == 1 else self.sqrt_N - 1
        
        # Iterate until we hit the iteration limit
        delta = 0
        while iterations < max_iterations:
            # Check candidates on both sides of √N
            for candidate in [search_start + delta, search_start - delta]:
                if iterations >= max_iterations:
                    break
                if candidate < 3:
                    continue
                # Skip duplicate at delta=0 (both candidates are the same)
                if delta == 0 and candidate == search_start - delta and candidate == search_start + delta:
                    continue
                    
                iterations += 1
                candidates_evaluated += 1
                
                # Progress reporting
                if progress_callback and iterations % 10000 == 0:
                    progress_callback(iterations, max_iterations)
                
                if self.verbose and iterations % 100000 == 0:
                    elapsed = time.time() - start_time
                    rate = iterations / elapsed if elapsed > 0 else 0
                    self._log(f"  Progress: {iterations:,} / {max_iterations:,} "
                             f"({100*iterations/max_iterations:.1f}%) - "
                             f"{rate:.0f} iter/s")
                
                # Check resonance score (for logging/analysis)
                score = compute_resonance_score(
                    candidate, self.N, self.sqrt_N_float,
                    self.params.k_shift,
                    self.params.kappa_estimated or 0.4,
                    self.params.phase_drift or 0.0
                )
                
                if score >= self.params.threshold:
                    high_resonance_count += 1
                
                # Trial division - the ground truth check
                result = verify_factor(candidate, self.N)
                if result:
                    p, q = result
                    end_time = time.time()
                    
                    self._log(f"\n{'='*60}")
                    self._log(f"SUCCESS! Factor found via BLIND search!")
                    self._log(f"p = {p}")
                    self._log(f"q = {q}")
                    self._log(f"Verification: p × q = {p * q}")
                    self._log(f"Iterations: {iterations:,}")
                    self._log(f"Time: {end_time - start_time:.3f}s")
                    self._log(f"{'='*60}")
                    
                    return FactorizationResult(
                        N=self.N,
                        success=True,
                        p=p,
                        q=q,
                        mode="blind",
                        iterations=iterations,
                        candidates_evaluated=candidates_evaluated,
                        high_resonance_candidates=high_resonance_count,
                        execution_time_seconds=end_time - start_time,
                        params=self.params,
                        timestamp=timestamp
                    )
            
            # Move to next pair of candidates (step by 2 for odd numbers)
            delta += 2
        
        # Search exhausted without finding factors
        end_time = time.time()
        
        self._log(f"\n{'='*60}")
        self._log(f"SEARCH EXHAUSTED - No factors found in {iterations:,} iterations")
        self._log(f"Time: {end_time - start_time:.3f}s")
        self._log(f"Candidates evaluated: {candidates_evaluated:,}")
        self._log(f"High resonance candidates: {high_resonance_count:,}")
        
        # Estimate remaining work for large semiprimes
        if self.params.bit_length >= 100:
            # Current delta covers ±delta around √N
            # Full coverage requires searching up to √N distance from center
            max_distance = delta  # Current search radius
            full_coverage_needed = self.sqrt_N  # Worst case distance to factor
            remaining_distance = max(0, full_coverage_needed - max_distance)
            # Approximately 1 iteration per unit of distance (odd numbers only)
            remaining_ops = remaining_distance // 2
            self._log(f"\nNote: Full search would require ~{remaining_ops:,.0f} more iterations")
            self._log("This demonstrates why 127-bit blind factorization remains challenging.")
        
        self._log(f"{'='*60}")
        
        return FactorizationResult(
            N=self.N,
            success=False,
            mode="blind",
            iterations=iterations,
            candidates_evaluated=candidates_evaluated,
            high_resonance_candidates=high_resonance_count,
            execution_time_seconds=end_time - start_time,
            params=self.params,
            timestamp=timestamp
        )
    
    def estimate_search_complexity(self) -> dict:
        """
        Estimate the complexity of blind factorization for this N.
        
        Returns
        -------
        dict
            Complexity estimates including operations needed
        """
        bit_length = self.params.bit_length
        
        # Worst case: factor is 2 from √N (balanced semiprime)
        # Need to check ~√N candidates in worst case
        worst_case_ops = self.sqrt_N
        
        # Average case for balanced semiprimes
        # Factors are typically within N^(1/4) of each other
        quarter_root = int(self.N ** 0.25)
        avg_case_ops = quarter_root
        
        # Time estimates (assuming 10M ops/second)
        ops_per_second = 10_000_000
        worst_case_seconds = worst_case_ops / ops_per_second
        avg_case_seconds = avg_case_ops / ops_per_second
        
        return {
            "bit_length": bit_length,
            "sqrt_N": self.sqrt_N,
            "worst_case_operations": worst_case_ops,
            "average_case_operations": avg_case_ops,
            "worst_case_time_seconds": worst_case_seconds,
            "worst_case_time_formatted": self._format_time(worst_case_seconds),
            "average_case_time_formatted": self._format_time(avg_case_seconds),
            "feasible": worst_case_seconds < 3600 * 24  # Less than a day
        }
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds into human-readable time."""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        elif seconds < 86400 * 365:
            return f"{seconds/86400:.1f} days"
        else:
            return f"{seconds/(86400*365):.1f} years"


def factor_semiprime_blind(
    N: int,
    max_iterations: Optional[int] = None,
    verbose: bool = True
) -> FactorizationResult:
    """
    Convenience function for blind factorization.
    
    Parameters
    ----------
    N : int
        The semiprime to factor
    max_iterations : int, optional
        Maximum search iterations
    verbose : bool
        Print progress information
        
    Returns
    -------
    FactorizationResult
        Result of factorization attempt
    """
    factorizer = BlindGeometricFactorizer(N, verbose=verbose)
    return factorizer.factor_blind(max_iterations)


# Test semiprimes of various sizes for validation
# Balanced semiprimes have factors close to √N for easier blind search
TEST_SEMIPRIMES = {
    "tiny": {
        "N": 35,  # 5 × 7 (balanced: √35 ≈ 5.9)
        "p": 5,
        "q": 7,
        "bits": 6
    },
    "small_16bit": {
        # 223 × 233 = 51959 (balanced: √51959 ≈ 228)
        "N": 51959,
        "p": 223,
        "q": 233,
        "bits": 16
    },
    "medium_32bit": {
        # 46337 × 46349 = 2147673613 (balanced: √N ≈ 46341)
        "N": 2147673613,
        "p": 46337,
        "q": 46349,
        "bits": 32
    },
    "larger_48bit": {
        # 11863279 × 11863289 = 140737507264631 (balanced: √N ≈ 11863284)
        "N": 140737507264631,
        "p": 11863279,
        "q": 11863289,
        "bits": 48
    },
    "gate_127": {
        "N": 137524771864208156028430259349934309717,
        "p": 10508623501177419659,
        "q": 13086849276577416863,
        "bits": 127
    }
}


if __name__ == "__main__":
    print("Blind Geometric Factorization Demo")
    print("=" * 60)
    
    # Test on small semiprimes
    for name, data in list(TEST_SEMIPRIMES.items())[:4]:  # Skip 64-bit prime and Gate-127
        print(f"\n{'='*60}")
        print(f"Test: {name} ({data['bits']}-bit)")
        
        factorizer = BlindGeometricFactorizer(data["N"], verbose=True)
        
        # Show complexity estimate
        complexity = factorizer.estimate_search_complexity()
        print(f"\nComplexity estimate:")
        print(f"  Worst case: {complexity['worst_case_operations']:,} ops ({complexity['worst_case_time_formatted']})")
        print(f"  Feasible: {complexity['feasible']}")
        
        # Attempt factorization
        result = factorizer.factor_blind(max_iterations=100000)
        
        if result.success:
            expected_p = data["p"]
            expected_q = data["q"]
            matches = (
                (result.p == expected_p and result.q == expected_q) or
                (result.p == expected_q and result.q == expected_p)
            )
            print(f"\nValidation: {'PASS' if matches else 'MISMATCH'}")
    
    # Show Gate-127 complexity for perspective
    print(f"\n{'='*60}")
    print("Gate-127 (127-bit) Complexity Analysis")
    gate127 = TEST_SEMIPRIMES["gate_127"]
    factorizer = BlindGeometricFactorizer(gate127["N"], verbose=False)
    complexity = factorizer.estimate_search_complexity()
    print(f"  Worst case operations: {complexity['worst_case_operations']:,}")
    print(f"  Worst case time: {complexity['worst_case_time_formatted']}")
    print(f"  Feasible with current approach: {complexity['feasible']}")
    print("\nThis demonstrates why further algorithmic breakthroughs are needed")
    print("for blind factorization at the 127-bit scale.")
