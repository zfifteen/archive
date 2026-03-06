#!/usr/bin/env python3
"""
Mid-Scale Validation Runner for Z-Sandbox Framework

Executes comprehensive validation of hybrid geometric-wave factorization
methods on 512-768 bit balanced semiprimes. Integrates:

1. Geometric embeddings (golden-ratio tori in 11+ dimensions)
2. Perturbation corrections (Laguerre polynomials, anisotropy)
3. Hybrid sampling (RQMC with Sobol' sequences, Z5D axioms)
4. Performance metrics and benchmarking

User Story: ZSB-VALID-512
Epic: Scalability Demonstrations for Hybrid Geometric-Wave Factorization
"""

import argparse
import json
import time
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import csv

# Import z-sandbox modules
from mid_scale_semiprime_generator import generate_mid_scale_suite, validate_target
from monte_carlo import FactorizationMonteCarloEnhancer
from perturbation_theory import (
    PerturbationTheoryIntegrator,
    PerturbationCoefficients,
    LaguerrePolynomialBasis
)
from z5d_axioms import Z5DAxioms
from rqmc_control import ScrambledSobolSampler, AdaptiveRQMCSampler

try:
    import sympy
except ImportError:
    print("Warning: sympy not available, factorization verification will be limited")
    sympy = None


@dataclass
class ValidationMetrics:
    """Metrics for a single factorization attempt."""
    target_id: str
    N_bits: int
    success: bool
    p_found: Optional[int]
    q_found: Optional[int]
    
    # Timing breakdown
    total_time_sec: float
    embedding_time_sec: float
    perturbation_time_sec: float
    sampling_time_sec: float
    verification_time_sec: float
    
    # Resource usage
    num_candidates: int
    num_samples: int
    variance_reduction_factor: float
    
    # Method details
    embedding_dims: int
    perturbation_config: str
    sampling_mode: str
    
    # Success metrics
    factor_rank: Optional[int] = None  # Rank of factor in candidate list
    attempts: int = 1


class MidScaleValidator:
    """
    Mid-scale validation framework integrating all z-sandbox components.
    """
    
    def __init__(
        self,
        embedding_dims: int = 11,
        perturbation_coeffs: Optional[PerturbationCoefficients] = None,
        sampling_mode: str = "rqmc_sobol",
        variance_target: float = 0.1,
        num_samples: int = 10000,
        seed: int = 42
    ):
        """
        Initialize validator with configuration.
        
        Args:
            embedding_dims: Dimensions for geometric embedding (11+ recommended)
            perturbation_coeffs: Perturbation theory coefficients
            sampling_mode: RQMC sampling mode ('rqmc_sobol', 'rqmc_adaptive', etc.)
            variance_target: Target normalized variance (default: 0.1 = 10%)
            num_samples: Number of samples to generate per trial
            seed: Random seed for reproducibility
        """
        self.embedding_dims = embedding_dims
        self.perturbation_coeffs = perturbation_coeffs or PerturbationCoefficients(
            anisotropic=0.05,
            aspheric=0.02,
            nonparaxial=0.01,
            curvature_coupling=1.0
        )
        self.sampling_mode = sampling_mode
        self.variance_target = variance_target
        self.num_samples = num_samples
        self.seed = seed
        
        # Initialize components
        self.z5d = Z5DAxioms(precision_dps=50)
        self.mc_enhancer = FactorizationMonteCarloEnhancer(seed=seed)
        self.perturbation_integrator = PerturbationTheoryIntegrator(
            self.perturbation_coeffs
        )
        
        # Initialize RQMC samplers based on mode
        if sampling_mode == "rqmc_sobol":
            self.rqmc_sampler = ScrambledSobolSampler(
                dimension=2, alpha=0.5, seed=seed
            )
        elif sampling_mode == "rqmc_adaptive":
            self.rqmc_sampler = AdaptiveRQMCSampler(
                dimension=2, target_variance=variance_target, seed=seed
            )
        else:
            self.rqmc_sampler = None
    
    def embed_geometric(self, N: int) -> Tuple[List[float], float]:
        """
        Embed N in geometric manifold using golden-ratio tori.
        
        Args:
            N: Semiprime to embed
            
        Returns:
            Tuple of (embedding_coords, embedding_time_sec)
        """
        start_time = time.time()
        
        # Use Z5D geometric resolution for embedding
        k = 0.3  # Optimal k for prime density enhancement
        theta_prime, kappa, bias = self.z5d.z5d_biased_prime_selection(
            target_index=N,
            k=k
        )
        
        # Generate embedding coordinates
        # Using golden ratio modulation across dimensions
        phi = (1 + math.sqrt(5)) / 2
        coords = []
        
        x = float(N) / math.exp(2)  # Normalize by e²
        for dim in range(self.embedding_dims):
            # Iterated fractional mapping with phi
            x_frac = (x % phi) / phi
            x = phi * (x_frac ** k)
            coords.append(x % 1.0)
        
        elapsed = time.time() - start_time
        return coords, elapsed
    
    def apply_perturbations(
        self,
        N: int,
        base_candidates: List[int]
    ) -> Tuple[List[int], float]:
        """
        Apply perturbation theory corrections to candidate list.
        
        Args:
            N: Target semiprime
            base_candidates: Initial candidate list
            
        Returns:
            Tuple of (enhanced_candidates, perturbation_time_sec)
        """
        start_time = time.time()
        
        try:
            # Use perturbation integrator for enhancement
            enhanced = self.perturbation_integrator.enhance_candidate_generation(
                N,
                base_candidates,
                variance_target=self.variance_target
            )
        except Exception as e:
            print(f"  Warning: Perturbation enhancement failed: {e}")
            print(f"  Continuing with base candidates only")
            enhanced = base_candidates
        
        elapsed = time.time() - start_time
        return enhanced, elapsed
    
    def generate_rqmc_samples(self, N: int) -> Tuple[List[int], float, float]:
        """
        Generate candidate samples using RQMC with Z5D bias.
        
        Args:
            N: Target semiprime
            
        Returns:
            Tuple of (candidates, sampling_time_sec, variance_reduction_factor)
        """
        start_time = time.time()
        
        # Use Monte Carlo enhancer with configured sampling mode
        candidates = self.mc_enhancer.biased_sampling_with_phi(
            N=N,
            num_samples=self.num_samples,
            mode=self.sampling_mode
        )
        
        elapsed = time.time() - start_time
        
        # Estimate variance reduction factor
        # In RQMC, we measure effectiveness by unique candidate coverage
        # compared to theoretical uniform random sampling
        # This is a proxy metric; true variance reduction requires
        # multiple replications (see RQMC_CONTROL_KNOB.md)
        unique_count = len(set(candidates))
        # Expected unique from uniform sampling: n * (1 - exp(-n/m)), where n = num_samples, m = N
        expected_uniform = int(N * (1 - math.exp(-self.num_samples / N)))
        # Variance reduction proxy: higher unique count = better coverage
        variance_reduction_proxy = unique_count / max(1, expected_uniform)
        
        return candidates, elapsed, variance_reduction_proxy
    
    def verify_factorization(
        self,
        N: int,
        candidates: List[int]
    ) -> Tuple[bool, Optional[int], Optional[int], float, Optional[int]]:
        """
        Verify if any candidate is a factor of N.
        
        Args:
            N: Target semiprime
            candidates: List of candidate factors
            
        Returns:
            Tuple of (success, p, q, verification_time, factor_rank)
        """
        start_time = time.time()
        
        for rank, candidate in enumerate(candidates):
            if candidate <= 1 or candidate >= N:
                continue
            
            if N % candidate == 0:
                p = candidate
                q = N // candidate
                
                # Verify primality if sympy available
                if sympy:
                    if sympy.isprime(p) and sympy.isprime(q):
                        elapsed = time.time() - start_time
                        return True, p, q, elapsed, rank
                else:
                    # Without sympy, just verify factorization
                    if p * q == N:
                        elapsed = time.time() - start_time
                        return True, p, q, elapsed, rank
        
        elapsed = time.time() - start_time
        return False, None, None, elapsed, None
    
    def validate_single_target(self, target: Dict) -> ValidationMetrics:
        """
        Validate factorization on a single target.
        
        Args:
            target: Target dictionary with N, p, q, metadata
            
        Returns:
            ValidationMetrics for this attempt
        """
        start_total = time.time()
        
        N = int(target['N'])
        N_bits = N.bit_length()
        target_id = target['id']
        
        print(f"\n{'='*80}")
        print(f"Validating {target_id} ({N_bits} bits)")
        print(f"{'='*80}")
        
        # Phase 1: Geometric embedding
        print("Phase 1: Geometric embedding...")
        embedding_coords, embedding_time = self.embed_geometric(N)
        print(f"  ✓ Embedded in {self.embedding_dims}D manifold ({embedding_time:.3f}s)")
        
        # Phase 2: Generate base candidates around √N
        sqrt_N = int(math.sqrt(N))
        radius = min(10000, int(0.01 * sqrt_N))  # 1% radius or 10k, whichever is smaller
        base_candidates = list(range(sqrt_N - radius, sqrt_N + radius + 1))
        print(f"  Base candidates: {len(base_candidates)} around √N")
        
        # Phase 3: Apply perturbation corrections
        print("Phase 2: Perturbation corrections...")
        enhanced_candidates, perturbation_time = self.apply_perturbations(
            N, base_candidates
        )
        print(f"  ✓ Enhanced {len(enhanced_candidates)} candidates ({perturbation_time:.3f}s)")
        
        # Phase 4: RQMC sampling
        print("Phase 3: RQMC sampling...")
        sampled_candidates, sampling_time, variance_reduction = self.generate_rqmc_samples(N)
        print(f"  ✓ Generated {len(sampled_candidates)} samples ({sampling_time:.3f}s)")
        print(f"  Variance reduction factor: {variance_reduction:.1f}×")
        
        # Combine candidates (remove duplicates, keep order)
        all_candidates = []
        seen = set()
        for c in enhanced_candidates + sampled_candidates:
            if c not in seen and c > 1 and c < N:
                all_candidates.append(c)
                seen.add(c)
        
        print(f"  Total unique candidates: {len(all_candidates)}")
        
        # Phase 5: Verification
        print("Phase 4: Verification...")
        success, p_found, q_found, verify_time, factor_rank = self.verify_factorization(
            N, all_candidates
        )
        
        total_time = time.time() - start_total
        
        if success:
            print(f"  ✓ SUCCESS! Found factors: {p_found} × {q_found}")
            print(f"  Factor rank in candidate list: {factor_rank}")
        else:
            print(f"  ✗ FAILED - No factors found")
        
        print(f"  Total time: {total_time:.2f}s")
        
        # Create metrics object
        metrics = ValidationMetrics(
            target_id=target_id,
            N_bits=N_bits,
            success=success,
            p_found=p_found,
            q_found=q_found,
            total_time_sec=total_time,
            embedding_time_sec=embedding_time,
            perturbation_time_sec=perturbation_time,
            sampling_time_sec=sampling_time,
            verification_time_sec=verify_time,
            num_candidates=len(all_candidates),
            num_samples=self.num_samples,
            variance_reduction_factor=variance_reduction,
            embedding_dims=self.embedding_dims,
            perturbation_config=str(self.perturbation_coeffs),
            sampling_mode=self.sampling_mode,
            factor_rank=factor_rank
        )
        
        return metrics
    
    def validate_suite(
        self,
        targets: List[Dict],
        output_file: str = "mid_scale_results.csv"
    ) -> List[ValidationMetrics]:
        """
        Validate entire suite of targets.
        
        Args:
            targets: List of target dictionaries
            output_file: Path to save results CSV
            
        Returns:
            List of ValidationMetrics
        """
        results = []
        
        print(f"\n{'='*80}")
        print(f"MID-SCALE VALIDATION SUITE")
        print(f"{'='*80}")
        print(f"Targets: {len(targets)}")
        print(f"Embedding: {self.embedding_dims}D")
        print(f"Sampling: {self.sampling_mode}")
        print(f"Samples per target: {self.num_samples:,}")
        print(f"{'='*80}\n")
        
        for i, target in enumerate(targets):
            print(f"\nTarget {i+1}/{len(targets)}")
            metrics = self.validate_single_target(target)
            results.append(metrics)
        
        # Save results to CSV
        if output_file:
            self._save_results(results, output_file)
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _save_results(self, results: List[ValidationMetrics], output_file: str):
        """Save results to CSV file."""
        output_path = Path(output_file)
        
        with open(output_path, 'w', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=asdict(results[0]).keys())
                writer.writeheader()
                for metrics in results:
                    writer.writerow(asdict(metrics))
        
        print(f"\n{'='*80}")
        print(f"✓ Results saved to {output_path}")
    
    def _print_summary(self, results: List[ValidationMetrics]):
        """Print summary statistics."""
        if not results:
            return
        
        total = len(results)
        successful = sum(1 for r in results if r.success)
        success_rate = 100.0 * successful / total if total > 0 else 0.0
        
        avg_time = sum(r.total_time_sec for r in results) / total
        avg_variance_reduction = sum(r.variance_reduction_factor for r in results) / total
        
        print(f"\n{'='*80}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total targets:          {total}")
        print(f"Successful:             {successful}")
        print(f"Failed:                 {total - successful}")
        print(f"Success rate:           {success_rate:.1f}%")
        print(f"Average time:           {avg_time:.2f}s")
        print(f"Avg variance reduction: {avg_variance_reduction:.1f}×")
        print(f"{'='*80}\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Mid-Scale Validation Runner for Z-Sandbox Framework"
    )
    
    # Target generation options
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate new targets before validation"
    )
    parser.add_argument(
        "--num-targets", "-n",
        type=int,
        default=10,
        help="Number of targets to generate (default: 10)"
    )
    parser.add_argument(
        "--min-bits",
        type=int,
        default=512,
        help="Minimum bit length (default: 512)"
    )
    parser.add_argument(
        "--max-bits",
        type=int,
        default=768,
        help="Maximum bit length (default: 768)"
    )
    
    # Input/output
    parser.add_argument(
        "--targets",
        type=str,
        default="mid_scale_targets.json",
        help="Input targets file (default: mid_scale_targets.json)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="mid_scale_results.csv",
        help="Output results file (default: mid_scale_results.csv)"
    )
    
    # Validation configuration
    parser.add_argument(
        "--dims",
        type=int,
        default=11,
        help="Embedding dimensions (default: 11)"
    )
    parser.add_argument(
        "--sampling-mode",
        type=str,
        default="rqmc_sobol",
        choices=["rqmc_sobol", "rqmc_adaptive", "rqmc_halton", "qmc_phi_hybrid"],
        help="RQMC sampling mode (default: rqmc_sobol)"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=10000,
        help="Number of samples per target (default: 10000)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)"
    )
    
    args = parser.parse_args()
    
    # Generate targets if requested
    if args.generate:
        print("Generating mid-scale targets...")
        generate_mid_scale_suite(
            num_targets=args.num_targets,
            bit_range=(args.min_bits, args.max_bits),
            output_file=args.targets
        )
    
    # Load targets
    targets_path = Path(args.targets)
    if not targets_path.exists():
        print(f"Error: Targets file not found: {targets_path}")
        print("Use --generate to create new targets")
        sys.exit(1)
    
    with open(targets_path, 'r') as f:
        data = json.load(f)
    
    targets = data['targets']
    
    # Initialize validator
    validator = MidScaleValidator(
        embedding_dims=args.dims,
        sampling_mode=args.sampling_mode,
        num_samples=args.num_samples,
        seed=args.seed
    )
    
    # Run validation
    results = validator.validate_suite(targets, output_file=args.output)
    
    return 0 if any(r.success for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
