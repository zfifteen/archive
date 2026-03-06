#!/usr/bin/env python3
"""
Mid-Scale Validation Demo

Quick demonstration of the mid-scale validation framework on a smaller
example to verify functionality before running full 512-768 bit validation.

This demo:
1. Generates a 128-bit balanced semiprime (much faster than 512-bit)
2. Runs the full validation pipeline
3. Reports results with timing breakdown
"""

import sys
import json
import tempfile
from pathlib import Path

# Note: sys.path modification is used for demo/testing convenience only.
# For production use, install the package properly with setup.py or use PYTHONPATH.
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from mid_scale_semiprime_generator import generate_balanced_semiprime
from mid_scale_validation_runner import MidScaleValidator


def main():
    """Run demo validation."""
    print("=" * 80)
    print(" " * 20 + "MID-SCALE VALIDATION DEMO")
    print("=" * 80)
    print()
    print("This demo uses a 128-bit semiprime for fast validation.")
    print("Full 512-768 bit validation will take significantly longer.")
    print()
    
    # Generate a test semiprime
    print("Step 1: Generating 128-bit balanced semiprime...")
    print("-" * 80)
    
    try:
        N, p, q, metadata = generate_balanced_semiprime(128)
        print(f"✓ Generated semiprime:")
        print(f"  N = {N}")
        print(f"  p = {p} ({p.bit_length()} bits)")
        print(f"  q = {q} ({q.bit_length()} bits)")
        print(f"  Factorization: {p} × {q} = {N}")
        print(f"  Balance: ±{metadata['balance_diff']} bits")
        print(f"  Generation time: {metadata['generation_time_sec']:.3f}s")
    except Exception as e:
        print(f"✗ Failed to generate semiprime: {e}")
        return 1
    
    # Create target dictionary
    target = {
        "id": "DEMO-128b-01",
        "N": str(N),
        "p": str(p),
        "q": str(q),
        "metadata": metadata
    }
    
    # Initialize validator with reduced sample count for speed
    print("\nStep 2: Initializing validator...")
    print("-" * 80)
    print("Configuration:")
    print("  - Embedding dimensions: 11")
    print("  - Sampling mode: rqmc_sobol")
    print("  - Number of samples: 1,000 (reduced for demo)")
    print("  - Perturbation corrections: enabled")
    
    validator = MidScaleValidator(
        embedding_dims=11,
        sampling_mode="rqmc_sobol",
        num_samples=1000,  # Reduced for demo speed
        seed=42
    )
    
    # Run validation
    print("\nStep 3: Running validation pipeline...")
    print("-" * 80)
    
    try:
        metrics = validator.validate_single_target(target)
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Print detailed results
    print("\n" + "=" * 80)
    print(" " * 25 + "VALIDATION RESULTS")
    print("=" * 80)
    
    print(f"\nTarget: {metrics.target_id}")
    print(f"Bit length: {metrics.N_bits}")
    print(f"Success: {'✓ YES' if metrics.success else '✗ NO'}")
    
    if metrics.success:
        print(f"\nFactors found:")
        print(f"  p = {metrics.p_found}")
        print(f"  q = {metrics.q_found}")
        print(f"  Verification: {metrics.p_found} × {metrics.q_found} = {N}")
        print(f"  Factor rank: {metrics.factor_rank} (position in candidate list)")
    
    print(f"\nTiming breakdown:")
    print(f"  Geometric embedding:     {metrics.embedding_time_sec:.3f}s")
    print(f"  Perturbation theory:     {metrics.perturbation_time_sec:.3f}s")
    print(f"  RQMC sampling:           {metrics.sampling_time_sec:.3f}s")
    print(f"  Verification:            {metrics.verification_time_sec:.3f}s")
    print(f"  ─────────────────────────────────────")
    print(f"  Total time:              {metrics.total_time_sec:.3f}s")
    
    print(f"\nPerformance metrics:")
    print(f"  Total candidates:        {metrics.num_candidates:,}")
    print(f"  Samples generated:       {metrics.num_samples:,}")
    print(f"  Variance reduction:      {metrics.variance_reduction_factor:.1f}×")
    
    print(f"\nConfiguration:")
    print(f"  Embedding dimensions:    {metrics.embedding_dims}")
    print(f"  Sampling mode:           {metrics.sampling_mode}")
    
    print("\n" + "=" * 80)
    
    if metrics.success:
        print("\n✓ Demo completed successfully!")
        print("\nNext steps:")
        print("  1. Run full validation on 512-768 bit targets:")
        print("     python3 python/mid_scale_validation_runner.py --generate --num-targets 10")
        print("  2. Adjust configuration for optimal performance")
        print("  3. Compare against baseline methods (ECM, Pollard's Rho)")
    else:
        print("\n⚠ Demo did not find factors")
        print("\nThis is expected for some targets. The framework is designed for")
        print("statistical validation across multiple targets to achieve >50% success rate.")
        print("\nNext steps:")
        print("  1. Try different sampling modes (--sampling-mode rqmc_adaptive)")
        print("  2. Increase sample count (--num-samples 50000)")
        print("  3. Increase embedding dimensions (--dims 15)")
    
    print("=" * 80)
    
    return 0 if metrics.success else 1


if __name__ == "__main__":
    sys.exit(main())
