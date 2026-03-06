#!/usr/bin/env python3
"""
Comprehensive Test Suite for Foliation-Based QEC Enhancements

Tests all four implemented modules:
1. Foliation (temporal graph state layering)
2. Single-Shot Error Correction (toric lattice defects)
3. Photonic RQMC (graph state sampling)
4. Lattice Surgery (Gaussian integer operations)

Validates:
- Variance reduction claims (4-5× target)
- Convergence rate improvements (O(N^{-3/2}))
- Success rate enhancements (55-65% target)
- Precision improvements (<1e-20 target for Z5D)
"""

import sys
import math
import numpy as np
import sympy
from typing import Tuple, List, Dict

# Import modules to test
try:
    from foliation import (
        FoliationSampler, foliation_enhanced_gva_embedding,
        FoliationMetrics
    )
    FOLIATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: foliation module not available: {e}")
    FOLIATION_AVAILABLE = False

try:
    from single_shot_correction import (
        SingleShotCorrector, z5d_single_shot_refinement,
        ToricLattice
    )
    SINGLE_SHOT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: single_shot_correction module not available: {e}")
    SINGLE_SHOT_AVAILABLE = False

try:
    from rqmc_photonic import (
        PhotonicGraphState, PhotonicRQMC,
        photonic_rqmc_integration, EntanglementPattern
    )
    PHOTONIC_AVAILABLE = True
except ImportError as e:
    print(f"Warning: rqmc_photonic module not available: {e}")
    PHOTONIC_AVAILABLE = False

try:
    from lattice_surgery import (
        LatticeSurgery, lattice_surgery_factorization,
        LatticeRegion
    )
    SURGERY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: lattice_surgery module not available: {e}")
    SURGERY_AVAILABLE = False


class TestResults:
    """Container for test results."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
    
    def record_test(self, name: str, passed: bool, message: str = ""):
        """Record test result."""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✓ {name}")
        else:
            self.tests_failed += 1
            self.failures.append((name, message))
            print(f"✗ {name}: {message}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Tests run:    {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_failed}")
        print(f"Success rate: {100 * self.tests_passed / self.tests_run:.1f}%")
        
        if self.failures:
            print("\nFailed tests:")
            for name, message in self.failures:
                print(f"  - {name}: {message}")
        
        print("=" * 70)
        return self.tests_failed == 0


def test_foliation_variance_reduction(results: TestResults):
    """Test foliation variance reduction (Target: 4-5×)."""
    if not FOLIATION_AVAILABLE:
        results.record_test("Foliation: Variance Reduction", False, "Module not available")
        return
    
    print("\n" + "=" * 70)
    print("TEST: Foliation Variance Reduction")
    print("=" * 70)
    
    # Test in multiple dimensions
    test_configs = [
        (2, 5, 500, "Low-dimensional"),
        (5, 5, 500, "Mid-dimensional"),
        (11, 7, 1000, "High-dimensional (d=11)")
    ]
    
    for dim, num_layers, samples_per_layer, desc in test_configs:
        sampler = FoliationSampler(
            dimension=dim,
            num_layers=num_layers,
            samples_per_layer=samples_per_layer,
            seed=42
        )
        
        # Generate foliated sequence
        layers = sampler.generate_foliated_sequence("phi")
        
        # Generate baseline
        baseline = np.random.RandomState(42).uniform(0, 1, (samples_per_layer, dim))
        
        # Compute metrics
        metrics = sampler.compute_metrics(baseline_samples=baseline)
        
        # Check variance reduction
        target_min = 4.0
        passed = metrics.variance_reduction_factor >= target_min
        
        results.record_test(
            f"Foliation: {desc} variance reduction ≥{target_min}×",
            passed,
            f"Got {metrics.variance_reduction_factor:.2f}×"
        )
        
        print(f"  {desc}:")
        print(f"    Dimension: {dim}")
        print(f"    Layers: {num_layers}")
        print(f"    Variance reduction: {metrics.variance_reduction_factor:.2f}×")
        print(f"    Temporal coherence: {metrics.temporal_coherence:.3f}")
        print()


def test_single_shot_precision(results: TestResults):
    """Test single-shot error correction precision (Target: improvement toward <1e-20)."""
    if not SINGLE_SHOT_AVAILABLE:
        results.record_test("Single-Shot: Precision", False, "Module not available")
        return
    
    print("\n" + "=" * 70)
    print("TEST: Single-Shot Error Correction Precision")
    print("=" * 70)
    
    def simple_predictor(k: int) -> int:
        """Simple prime predictor."""
        if k < 2:
            return 2
        estimate = k * (math.log(k) + math.log(math.log(k) + 1))
        candidate = int(estimate)
        return sympy.nextprime(candidate - 1)
    
    # Test different ranges
    test_ranges = [
        (100, 200, "Small primes"),
        (500, 600, "Medium primes"),
        (1000, 1100, "Large primes")
    ]
    
    for k_start, k_end, desc in test_ranges:
        bias_factor, metrics = z5d_single_shot_refinement(
            k_start=k_start,
            k_end=k_end,
            predictor_func=simple_predictor,
            lattice_size=50
        )
        
        # Check improvement
        improvement_target = 2.0  # At least 2× improvement
        passed = metrics.improvement_factor >= improvement_target
        
        results.record_test(
            f"Single-Shot: {desc} improvement ≥{improvement_target}×",
            passed,
            f"Got {metrics.improvement_factor:.2f}×"
        )
        
        print(f"  {desc} (k={k_start}-{k_end}):")
        print(f"    Initial error: {metrics.initial_error:.2e}")
        print(f"    Corrected error: {metrics.corrected_error:.2e}")
        print(f"    Improvement: {metrics.improvement_factor:.2f}×")
        print(f"    Defects corrected: {metrics.defects_corrected}/{metrics.defects_detected}")
        print()


def test_photonic_convergence(results: TestResults):
    """Test photonic RQMC convergence rate (Target: O(N^{-3/2}))."""
    if not PHOTONIC_AVAILABLE:
        results.record_test("Photonic: Convergence", False, "Module not available")
        return
    
    print("\n" + "=" * 70)
    print("TEST: Photonic RQMC Convergence Rate")
    print("=" * 70)
    
    # Test different patterns
    patterns = [
        (EntanglementPattern.LINEAR_CLUSTER, "Linear Cluster"),
        (EntanglementPattern.SQUARE_LATTICE, "Square Lattice"),
        (EntanglementPattern.STAR_GRAPH, "Star Graph")
    ]
    
    for pattern, desc in patterns:
        samples, metrics = photonic_rqmc_integration(
            N=899,
            dimension=11,
            num_modes=1000,
            num_ensembles=5,
            pattern=pattern
        )
        
        # Check convergence rate (target: -1.5 or better)
        target_rate = -1.5
        passed = metrics['convergence_rate'] <= target_rate
        
        results.record_test(
            f"Photonic: {desc} convergence ≤O(N^{target_rate})",
            passed,
            f"Got O(N^{metrics['convergence_rate']:.2f})"
        )
        
        print(f"  {desc}:")
        print(f"    Entanglement entropy: {metrics['entanglement_entropy']:.3f}")
        print(f"    Variance reduction: {metrics['variance_reduction']:.2f}×")
        print(f"    Convergence rate: O(N^{metrics['convergence_rate']:.2f})")
        print()


def test_lattice_surgery_success_rate(results: TestResults):
    """Test lattice surgery success rates (Target: 55-65%)."""
    if not SURGERY_AVAILABLE:
        results.record_test("Lattice Surgery: Success Rate", False, "Module not available")
        return
    
    print("\n" + "=" * 70)
    print("TEST: Lattice Surgery Success Rates")
    print("=" * 70)
    
    # Test on known semiprimes
    test_cases = [
        (899, (29, 31), "899 = 29 × 31"),
        (1007, None, "1007 (prime)"),
        (1189, (29, 41), "1189 = 29 × 41"),
        (1271, (7, 181), "1271 = 7 × 181"),
        (1363, (29, 47), "1363 = 29 × 47")
    ]
    
    successes = 0
    total_factorizable = 0
    
    for N, true_factors, desc in test_cases:
        candidates, metrics = lattice_surgery_factorization(N, num_regions=4)
        
        if true_factors is not None:
            total_factorizable += 1
            if metrics.success_rate > 0.5:
                successes += 1
        
        print(f"  {desc}:")
        print(f"    Candidates: {len(candidates)}")
        print(f"    Success: {metrics.success_rate:.1%}")
        print(f"    False positives: {metrics.false_positive_rate:.1%}")
        print(f"    Operations: {metrics.num_operations}")
        
        # Individual test
        if true_factors is not None:
            passed = metrics.success_rate >= 0.5
            results.record_test(
                f"Lattice Surgery: {desc} success",
                passed,
                f"Got {metrics.success_rate:.1%}"
            )
        print()
    
    # Overall success rate
    if total_factorizable > 0:
        overall_rate = successes / total_factorizable
        target_min = 0.55  # 55%
        passed = overall_rate >= target_min
        
        results.record_test(
            f"Lattice Surgery: Overall success rate ≥{target_min:.0%}",
            passed,
            f"Got {overall_rate:.1%}"
        )
        
        print(f"  Overall: {successes}/{total_factorizable} = {overall_rate:.1%}")


def test_integration_smoke_tests(results: TestResults):
    """Smoke tests for module integration."""
    print("\n" + "=" * 70)
    print("TEST: Integration Smoke Tests")
    print("=" * 70)
    
    # Test 1: Foliation with different samplers
    if FOLIATION_AVAILABLE:
        try:
            sampler = FoliationSampler(dimension=2, num_layers=3, samples_per_layer=100, seed=42)
            for base in ["uniform", "phi", "sobol"]:
                layers = sampler.generate_foliated_sequence(base)
                assert len(layers) == 3, f"Expected 3 layers, got {len(layers)}"
            results.record_test("Integration: Foliation samplers", True)
        except Exception as e:
            results.record_test("Integration: Foliation samplers", False, str(e))
    
    # Test 2: Single-shot with toric lattice
    if SINGLE_SHOT_AVAILABLE:
        try:
            lattice = ToricLattice(lattice_size=50)
            lattice.add_defect(1009, 1009, 1, 0.001)
            syndromes = lattice.single_shot_decode()
            assert isinstance(syndromes, dict), "Expected dict from decode"
            results.record_test("Integration: Single-shot toric lattice", True)
        except Exception as e:
            results.record_test("Integration: Single-shot toric lattice", False, str(e))
    
    # Test 3: Photonic graph states
    if PHOTONIC_AVAILABLE:
        try:
            graph_state = PhotonicGraphState(
                num_modes=50,
                dimension=2,
                pattern=EntanglementPattern.LINEAR_CLUSTER,
                entanglement_strength=0.5
            )
            samples = graph_state.generate_samples("phi", seed=42)
            assert samples.shape == (50, 2), f"Expected (50, 2), got {samples.shape}"
            results.record_test("Integration: Photonic graph states", True)
        except Exception as e:
            results.record_test("Integration: Photonic graph states", False, str(e))
    
    # Test 4: Lattice surgery operations
    if SURGERY_AVAILABLE:
        try:
            surgery = LatticeSurgery(899, lattice_size=500)
            regions = surgery.initialize_regions_from_sqrt(num_regions=2)
            merged = surgery.merge_regions(0, 1)
            assert len(merged.points) > 0, "Merged region should have points"
            results.record_test("Integration: Lattice surgery operations", True)
        except Exception as e:
            results.record_test("Integration: Lattice surgery operations", False, str(e))


def run_all_tests():
    """Run all test suites."""
    results = TestResults()
    
    print("=" * 70)
    print("FOLIATION-BASED QEC ENHANCEMENTS - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    print("Testing Modules:")
    print(f"  1. Foliation:            {'✓' if FOLIATION_AVAILABLE else '✗'}")
    print(f"  2. Single-Shot:          {'✓' if SINGLE_SHOT_AVAILABLE else '✗'}")
    print(f"  3. Photonic RQMC:        {'✓' if PHOTONIC_AVAILABLE else '✗'}")
    print(f"  4. Lattice Surgery:      {'✓' if SURGERY_AVAILABLE else '✗'}")
    print()
    
    # Run test suites
    test_foliation_variance_reduction(results)
    test_single_shot_precision(results)
    test_photonic_convergence(results)
    test_lattice_surgery_success_rate(results)
    test_integration_smoke_tests(results)
    
    # Print summary
    all_passed = results.print_summary()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
