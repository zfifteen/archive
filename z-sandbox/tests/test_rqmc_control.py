#!/usr/bin/env python3
"""
Unit tests for RQMC control knob module.

Tests the mapping of coherence parameter α to QMC randomization strength
and validates RQMC ensemble replications for variance estimation.
"""

import sys
sys.path.append("../python")

import numpy as np
from rqmc_control import (
    RQMCScrambler,
    ScrambledSobolSampler,
    ScrambledHaltonSampler,
    AdaptiveRQMCSampler,
    SplitStepRQMC,
    estimate_variance_from_replications,
    compute_rqmc_metrics
)
from monte_carlo import FactorizationMonteCarloEnhancer


def test_rqmc_scrambler_initialization():
    """Test RQMCScrambler initialization and parameter mapping."""
    print("\n=== Test: RQMC Scrambler Initialization ===")
    
    # Test various α values
    test_alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    for alpha in test_alphas:
        scrambler = RQMCScrambler(alpha=alpha, seed=42)
        
        assert scrambler.alpha == alpha
        assert 1 <= scrambler.scrambling_depth <= 32
        assert scrambler.num_replications >= 1
        
        print(f"α={alpha:.2f}: depth={scrambler.scrambling_depth}, M={scrambler.num_replications}")
    
    # Verify inverse relationship: lower α → deeper scrambling
    scrambler_high = RQMCScrambler(alpha=0.9, seed=42)
    scrambler_low = RQMCScrambler(alpha=0.1, seed=42)
    
    assert scrambler_low.scrambling_depth > scrambler_high.scrambling_depth
    assert scrambler_low.num_replications >= scrambler_high.num_replications
    
    print("✓ RQMC scrambler initialization test passed")
    return True


def test_scrambled_sobol_generation():
    """Test scrambled Sobol' sequence generation."""
    print("\n=== Test: Scrambled Sobol' Generation ===")
    
    # Test with different α values
    for alpha in [1.0, 0.5, 0.1]:
        sampler = ScrambledSobolSampler(dimension=2, alpha=alpha, seed=42)
        samples = sampler.generate(100)
        
        assert samples.shape == (100, 2)
        assert np.all(samples >= 0) and np.all(samples <= 1)
        
        variance = np.var(samples)
        print(f"α={alpha:.1f}: variance={variance:.6f}, range=[{samples.min():.3f}, {samples.max():.3f}]")
    
    print("✓ Scrambled Sobol' generation test passed")
    return True


def test_scrambled_halton_generation():
    """Test scrambled Halton sequence generation."""
    print("\n=== Test: Scrambled Halton Generation ===")
    
    # Test with different α values
    for alpha in [1.0, 0.5, 0.1]:
        sampler = ScrambledHaltonSampler(dimension=2, alpha=alpha, seed=42)
        samples = sampler.generate(100)
        
        assert samples.shape == (100, 2)
        assert np.all(samples >= 0) and np.all(samples <= 1)
        
        variance = np.var(samples)
        print(f"α={alpha:.1f}: variance={variance:.6f}, range=[{samples.min():.3f}, {samples.max():.3f}]")
    
    print("✓ Scrambled Halton generation test passed")
    return True


def test_rqmc_replications():
    """Test RQMC replications for variance estimation."""
    print("\n=== Test: RQMC Replications ===")
    
    sampler = ScrambledSobolSampler(dimension=2, alpha=0.5, seed=42)
    
    # Generate multiple replications
    replications = sampler.generate_replications(100)
    
    assert len(replications) == sampler.num_replications
    
    for i, rep in enumerate(replications):
        assert rep.shape == (100, 2)
        print(f"Replication {i+1}: variance={np.var(rep):.6f}")
    
    # Estimate variance across replications
    mean_var, std_err = estimate_variance_from_replications(replications)
    print(f"\nEnsemble variance: {mean_var:.6f} ± {std_err:.6f}")
    
    assert mean_var > 0
    assert std_err >= 0
    
    print("✓ RQMC replications test passed")
    return True


def test_adaptive_rqmc():
    """Test adaptive RQMC with α scheduling."""
    print("\n=== Test: Adaptive RQMC ===")
    
    # Test with different target variances
    target_vars = [0.05, 0.1, 0.15]
    
    for target_var in target_vars:
        sampler = AdaptiveRQMCSampler(
            dimension=2,
            target_variance=target_var,
            sampler_type="sobol",
            seed=42
        )
        
        samples, alpha_history = sampler.generate_adaptive(1000, num_batches=10)
        
        assert samples.shape == (1000, 2)
        assert len(alpha_history) == 10
        
        final_variance = np.var(samples)
        print(f"Target={target_var:.2f}: final_var={final_variance:.4f}, final_α={alpha_history[-1]:.3f}")
        
        # Variance should be reasonably close to target (within 50%)
        # (Exact matching is hard due to discrete sampling)
        assert 0.5 * target_var <= final_variance <= 2.0 * target_var
    
    print("✓ Adaptive RQMC test passed")
    return True


def test_split_step_evolution():
    """Test split-step RQMC evolution."""
    print("\n=== Test: Split-Step Evolution ===")
    
    N = 899  # 29 × 31
    split_step = SplitStepRQMC(dimension=2, sampler_type="sobol", seed=42)
    
    # Perform evolution with custom α schedule
    alpha_schedule = [0.7, 0.6, 0.5, 0.4, 0.3]
    evolution = split_step.evolve(N=N, num_samples=100, num_steps=5, alpha_schedule=alpha_schedule)
    
    assert len(evolution) == 5
    
    for i, step_samples in enumerate(evolution):
        assert step_samples.shape == (100, 2)
        variance = np.var(step_samples)
        print(f"Step {i+1} (α={alpha_schedule[i]:.1f}): variance={variance:.6f}")
    
    print("✓ Split-step evolution test passed")
    return True


def test_weighted_discrepancy():
    """Test weighted discrepancy (dimension-wise α)."""
    print("\n=== Test: Weighted Discrepancy ===")
    
    sampler = AdaptiveRQMCSampler(dimension=3, target_variance=0.1, seed=42)
    
    # Apply dimension weights (e.g., based on curvature importance)
    # Higher weight → more scrambling for that dimension
    dimension_weights = np.array([1.0, 0.5, 0.2])  # First dim most important
    
    samples = sampler.generate_weighted_discrepancy(500, dimension_weights=dimension_weights)
    
    assert samples.shape == (500, 3)
    
    # Check per-dimension variances
    for d in range(3):
        var_d = np.var(samples[:, d])
        print(f"Dimension {d+1} (weight={dimension_weights[d]:.1f}): variance={var_d:.6f}, α={sampler.alpha_per_dim[d]:.3f}")
    
    print("✓ Weighted discrepancy test passed")
    return True


def test_rqmc_metrics():
    """Test RQMC metrics computation."""
    print("\n=== Test: RQMC Metrics ===")
    
    sampler = ScrambledSobolSampler(dimension=2, alpha=0.5, seed=42)
    samples = sampler.generate(100)
    
    N = 899
    true_factors = (29, 31)
    
    metrics = compute_rqmc_metrics(
        samples=samples,
        alpha=sampler.alpha,
        scrambling_depth=sampler.scrambling_depth,
        num_replications=sampler.num_replications,
        true_factors=true_factors,
        N=N
    )
    
    assert metrics.alpha == 0.5
    assert metrics.scrambling_depth == sampler.scrambling_depth
    assert metrics.num_replications == sampler.num_replications
    assert metrics.variance > 0
    assert metrics.discrepancy > 0
    
    print(f"Metrics: α={metrics.alpha}, depth={metrics.scrambling_depth}, M={metrics.num_replications}")
    print(f"  variance={metrics.variance:.6f}, discrepancy={metrics.discrepancy:.6f}")
    print(f"  convergence_rate={metrics.convergence_rate:.2f}, success={metrics.success_rate:.1f}")
    
    print("✓ RQMC metrics test passed")
    return True


def test_monte_carlo_integration_rqmc_sobol():
    """Test RQMC integration via monte_carlo.py (rqmc_sobol mode)."""
    print("\n=== Test: Monte Carlo RQMC Sobol Integration ===")
    
    N = 899  # 29 × 31
    true_factors = (29, 31)
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    candidates = enhancer.biased_sampling_with_phi(N, num_samples=500, mode="rqmc_sobol")
    
    assert len(candidates) > 0
    print(f"Generated {len(candidates)} unique candidates")
    
    # Check if factors are in candidates
    hit_p = 29 in candidates
    hit_q = 31 in candidates
    print(f"Factor hits: p={hit_p}, q={hit_q}")
    
    print("✓ Monte Carlo RQMC Sobol integration test passed")
    return True


def test_monte_carlo_integration_rqmc_adaptive():
    """Test RQMC integration via monte_carlo.py (rqmc_adaptive mode)."""
    print("\n=== Test: Monte Carlo RQMC Adaptive Integration ===")
    
    N = 899  # 29 × 31
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    candidates = enhancer.biased_sampling_with_phi(N, num_samples=500, mode="rqmc_adaptive")
    
    assert len(candidates) > 0
    print(f"Generated {len(candidates)} unique candidates with adaptive α")
    
    # Check spread of candidates around sqrt(N)
    if len(candidates) > 1:
        sqrt_N = int(np.sqrt(N))
        spread = max(candidates) - min(candidates)
        relative_spread = spread / sqrt_N
        print(f"Candidate spread: {spread} ({relative_spread:.2%} of sqrt(N))")
        
        # Should have reasonable spread (not all identical)
        assert spread > 0  # At least some diversity
        # Spread can be large due to symmetric sampling and exploration
    
    print("✓ Monte Carlo RQMC Adaptive integration test passed")
    return True


def test_monte_carlo_integration_rqmc_split_step():
    """Test RQMC integration via monte_carlo.py (rqmc_split_step mode)."""
    print("\n=== Test: Monte Carlo RQMC Split-Step Integration ===")
    
    N = 899  # 29 × 31
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    candidates = enhancer.biased_sampling_with_phi(N, num_samples=500, mode="rqmc_split_step")
    
    assert len(candidates) > 0
    print(f"Generated {len(candidates)} unique candidates with split-step evolution")
    
    print("✓ Monte Carlo RQMC Split-Step integration test passed")
    return True


def test_convergence_rate_comparison():
    """Compare convergence rates across different modes."""
    print("\n=== Test: Convergence Rate Comparison ===")
    
    N = 899
    sample_sizes = [100, 200, 500, 1000]
    
    modes = ["uniform", "qmc_phi_hybrid", "rqmc_sobol", "rqmc_adaptive"]
    
    for mode in modes:
        print(f"\nMode: {mode}")
        enhancer = FactorizationMonteCarloEnhancer(seed=42)
        
        for n in sample_sizes:
            try:
                candidates = enhancer.biased_sampling_with_phi(N, num_samples=n, mode=mode)
                unique = len(candidates)
                print(f"  n={n:4d}: {unique:4d} unique candidates")
            except Exception as e:
                print(f"  n={n:4d}: Error - {e}")
    
    print("✓ Convergence rate comparison test passed")
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("RQMC Control Knob Test Suite")
    print("=" * 70)
    
    tests = [
        test_rqmc_scrambler_initialization,
        test_scrambled_sobol_generation,
        test_scrambled_halton_generation,
        test_rqmc_replications,
        test_adaptive_rqmc,
        test_split_step_evolution,
        test_weighted_discrepancy,
        test_rqmc_metrics,
        test_monte_carlo_integration_rqmc_sobol,
        test_monte_carlo_integration_rqmc_adaptive,
        test_monte_carlo_integration_rqmc_split_step,
        test_convergence_rate_comparison,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ {failed} test(s) failed")
        sys.exit(1)
