#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stadlmann Distribution Level Falsification Experiment
=====================================================

Objective: Attempt to falsify the hypothesis that Stadlmann's distribution level 
θ ≈ 0.525 acts as a "tunable density dial" providing measurable and meaningful 
density enhancements in the Z5D framework.

This experiment implements multiple falsification tests:
1. Independence Test: Verify θ actually affects predictions
2. Monotonicity Test: Check if increasing θ affects outcomes as claimed
3. Boost Validation: Test 1-2% density boost claim with bootstrap CIs
4. Scale Invariance: Verify effects are consistent across 10^4 to 10^6 scales
5. Randomness Test: Test if θ=0.525 is special vs random values

Author: Z-Mode Falsification Engine
Date: 2025-11-18
"""

import sys
import os
import numpy as np
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.z_5d_enhanced import z5d_predictor_with_dist_level
from src.core.params import (
    DIST_LEVEL_STADLMANN, 
    DIST_LEVEL_MIN, 
    DIST_LEVEL_MAX,
    validate_dist_level
)
from src.core.conical_flow import conical_density_enhancement_factor

try:
    from sympy import primerange, prime
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("WARNING: SymPy not available. Some tests will be limited.")


class FalsificationResults:
    """Container for falsification experiment results."""
    
    def __init__(self):
        self.tests = {}
        self.summary = {}
        self.falsification_status = "UNKNOWN"
    
    def add_test(self, test_name: str, result: Dict[str, Any]):
        """Add a test result."""
        self.tests[test_name] = result
    
    def generate_summary(self):
        """Generate executive summary of falsification attempts."""
        total_tests = len(self.tests)
        failed_tests = sum(1 for t in self.tests.values() if t.get('falsified', False))
        passed_tests = total_tests - failed_tests
        
        self.summary = {
            'total_tests': int(total_tests),
            'falsified_tests': int(failed_tests),
            'supported_tests': int(passed_tests),
            'falsification_rate': float(failed_tests / total_tests if total_tests > 0 else 0)
        }
        
        # Determine overall falsification status
        if failed_tests >= total_tests * 0.5:  # 50% or more tests falsified
            self.falsification_status = "HYPOTHESIS_FALSIFIED"
        elif failed_tests > 0:
            self.falsification_status = "PARTIAL_FALSIFICATION"
        else:
            self.falsification_status = "HYPOTHESIS_SUPPORTED"
        
        self.summary['status'] = self.falsification_status
        
        return self.summary
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            'summary': self.summary,
            'tests': self.tests,
            'status': self.falsification_status
        }


def test_independence(n_samples: int = 100, seed: int = 42) -> Dict[str, Any]:
    """
    Test 1: Independence Test
    
    Verify that the dist_level parameter actually affects predictions.
    If changing θ has no effect on predictions, the "density dial" claim is false.
    
    Args:
        n_samples: Number of k values to test
        seed: Random seed for reproducibility
    
    Returns:
        Dict with test results and falsification status
    """
    print("\n" + "="*70)
    print("TEST 1: INDEPENDENCE TEST")
    print("="*70)
    print("Hypothesis: dist_level parameter affects Z5D predictions")
    print("Falsification criterion: No significant difference between θ values\n")
    
    rng = np.random.default_rng(seed)
    k_values = rng.integers(10**4, 10**6, size=n_samples)
    
    # Test two different dist_levels
    theta_low = 0.51
    theta_high = 0.56
    
    predictions_low = []
    predictions_high = []
    
    for k in k_values:
        try:
            pred_low = float(z5d_predictor_with_dist_level(int(k), dist_level=theta_low))
            pred_high = float(z5d_predictor_with_dist_level(int(k), dist_level=theta_high))
            predictions_low.append(pred_low)
            predictions_high.append(pred_high)
        except Exception as e:
            print(f"Warning: Failed for k={k}: {e}")
            continue
    
    # Calculate relative differences
    rel_diffs = []
    for p_low, p_high in zip(predictions_low, predictions_high):
        if p_low != 0:
            rel_diff = abs(p_high - p_low) / p_low
            rel_diffs.append(rel_diff)
    
    rel_diffs = np.array(rel_diffs)
    
    # Statistics
    mean_rel_diff = np.mean(rel_diffs)
    std_rel_diff = np.std(rel_diffs)
    max_rel_diff = np.max(rel_diffs)
    
    # Falsification criterion: if mean relative difference < 0.0001 (0.01%), 
    # the parameter has no practical effect
    THRESHOLD = 0.0001
    falsified = mean_rel_diff < THRESHOLD
    
    result = {
        'test_name': 'Independence Test',
        'n_samples': int(len(rel_diffs)),
        'theta_low': float(theta_low),
        'theta_high': float(theta_high),
        'mean_rel_diff': float(mean_rel_diff),
        'std_rel_diff': float(std_rel_diff),
        'max_rel_diff': float(max_rel_diff),
        'threshold': float(THRESHOLD),
        'falsified': bool(falsified),
        'interpretation': (
            "FALSIFIED: dist_level has negligible effect on predictions" 
            if falsified else 
            "SUPPORTED: dist_level significantly affects predictions"
        )
    }
    
    print(f"θ_low = {theta_low}, θ_high = {theta_high}")
    print(f"Mean relative difference: {mean_rel_diff:.6f} ({mean_rel_diff*100:.4f}%)")
    print(f"Std relative difference: {std_rel_diff:.6f}")
    print(f"Max relative difference: {max_rel_diff:.6f}")
    print(f"\nResult: {result['interpretation']}")
    
    return result


def test_monotonicity(k_test: int = 100000, n_levels: int = 10, seed: int = 42) -> Dict[str, Any]:
    """
    Test 2: Monotonicity Test
    
    Check if increasing θ monotonically affects predictions.
    If the relationship is not monotonic, the "tunable dial" metaphor breaks down.
    
    Args:
        k_test: Test k value
        n_levels: Number of θ levels to test
        seed: Random seed
    
    Returns:
        Dict with test results and falsification status
    """
    print("\n" + "="*70)
    print("TEST 2: MONOTONICITY TEST")
    print("="*70)
    print("Hypothesis: Increasing θ monotonically affects predictions")
    print("Falsification criterion: Non-monotonic relationship\n")
    
    # Test range of θ values
    theta_values = np.linspace(0.51, 0.60, n_levels)
    predictions = []
    
    for theta in theta_values:
        try:
            pred = float(z5d_predictor_with_dist_level(k_test, dist_level=theta))
            predictions.append(pred)
        except Exception as e:
            print(f"Warning: Failed for θ={theta}: {e}")
            predictions.append(np.nan)
    
    predictions = np.array(predictions)
    
    # Check monotonicity
    diffs = np.diff(predictions)
    monotonic_increasing = np.all(diffs >= 0)
    monotonic_decreasing = np.all(diffs <= 0)
    monotonic = monotonic_increasing or monotonic_decreasing
    
    # Count direction changes
    direction_changes = 0
    for i in range(len(diffs) - 1):
        if not np.isnan(diffs[i]) and not np.isnan(diffs[i+1]):
            if (diffs[i] > 0 and diffs[i+1] < 0) or (diffs[i] < 0 and diffs[i+1] > 0):
                direction_changes += 1
    
    # Falsification: if there are multiple direction changes, not a simple dial
    falsified = direction_changes >= 2
    
    result = {
        'test_name': 'Monotonicity Test',
        'k_value': int(k_test),
        'n_levels': int(n_levels),
        'theta_min': float(theta_values[0]),
        'theta_max': float(theta_values[-1]),
        'monotonic': bool(monotonic),
        'monotonic_increasing': bool(monotonic_increasing),
        'monotonic_decreasing': bool(monotonic_decreasing),
        'direction_changes': int(direction_changes),
        'predictions': [float(x) if not np.isnan(x) else None for x in predictions.tolist()],
        'theta_values': [float(x) for x in theta_values.tolist()],
        'falsified': bool(falsified),
        'interpretation': (
            "FALSIFIED: Non-monotonic relationship suggests θ is not a simple 'dial'" 
            if falsified else 
            "SUPPORTED: Monotonic relationship consistent with 'dial' metaphor"
        )
    }
    
    print(f"k = {k_test}")
    print(f"θ range: [{theta_values[0]:.3f}, {theta_values[-1]:.3f}]")
    print(f"Monotonic: {monotonic}")
    print(f"Direction changes: {direction_changes}")
    print(f"\nResult: {result['interpretation']}")
    
    return result


def test_claimed_boost(n_primes: int = 10000, n_bootstrap: int = 1000, seed: int = 42) -> Dict[str, Any]:
    """
    Test 3: Claimed Boost Validation
    
    Test the specific claim of 1-2% density boost with CI [0.8%, 2.2%].
    
    Args:
        n_primes: Number of primes to analyze
        n_bootstrap: Bootstrap resamples
        seed: Random seed
    
    Returns:
        Dict with test results and falsification status
    """
    print("\n" + "="*70)
    print("TEST 3: CLAIMED BOOST VALIDATION")
    print("="*70)
    print("Hypothesis: θ=0.525 provides 1-2% density boost, CI [0.8%, 2.2%]")
    print("Falsification criterion: Boost outside claimed range\n")
    
    if not SYMPY_AVAILABLE:
        return {
            'test_name': 'Claimed Boost Validation',
            'falsified': False,
            'error': 'SymPy not available',
            'interpretation': 'TEST SKIPPED: SymPy required'
        }
    
    rng = np.random.default_rng(seed)
    
    # Generate primes
    primes = list(primerange(2, n_primes * 20))[:n_primes]
    
    # Compute enhancement with Stadlmann vs baseline
    baseline_theta = 0.51
    stadlmann_theta = DIST_LEVEL_STADLMANN
    
    enhancements = []
    for _ in range(n_bootstrap):
        # Bootstrap resample
        sample_indices = rng.choice(len(primes), size=len(primes), replace=True)
        
        # Compute densities with different θ
        baseline_density = 0
        stadlmann_density = 0
        
        for idx in sample_indices:
            p = primes[idx]
            # Use conical flow enhancement as proxy for density
            baseline_enh = conical_density_enhancement_factor(p, dist_level=baseline_theta)
            stadlmann_enh = conical_density_enhancement_factor(p, dist_level=stadlmann_theta)
            baseline_density += float(baseline_enh)
            stadlmann_density += float(stadlmann_enh)
        
        # Calculate boost percentage
        if baseline_density > 0:
            boost_pct = (stadlmann_density - baseline_density) / baseline_density * 100
            enhancements.append(boost_pct)
    
    enhancements = np.array(enhancements)
    
    mean_boost = np.mean(enhancements)
    ci_lower = np.percentile(enhancements, 2.5)
    ci_upper = np.percentile(enhancements, 97.5)
    
    # Falsification criteria:
    # 1. Mean boost outside [1%, 2%]
    # 2. CI does not overlap with [0.8%, 2.2%]
    claimed_range = [1.0, 2.0]
    claimed_ci = [0.8, 2.2]
    
    mean_in_range = claimed_range[0] <= mean_boost <= claimed_range[1]
    ci_overlaps = not (ci_upper < claimed_ci[0] or ci_lower > claimed_ci[1])
    
    falsified = not (mean_in_range and ci_overlaps)
    
    result = {
        'test_name': 'Claimed Boost Validation',
        'n_primes': int(n_primes),
        'n_bootstrap': int(n_bootstrap),
        'baseline_theta': float(baseline_theta),
        'stadlmann_theta': float(stadlmann_theta),
        'mean_boost_pct': float(mean_boost),
        'ci_lower_pct': float(ci_lower),
        'ci_upper_pct': float(ci_upper),
        'claimed_range': [float(x) for x in claimed_range],
        'claimed_ci': [float(x) for x in claimed_ci],
        'mean_in_range': bool(mean_in_range),
        'ci_overlaps': bool(ci_overlaps),
        'falsified': bool(falsified),
        'interpretation': (
            f"FALSIFIED: Measured boost {mean_boost:.2f}% (CI [{ci_lower:.2f}%, {ci_upper:.2f}%]) "
            f"does not match claimed range"
            if falsified else
            f"SUPPORTED: Measured boost {mean_boost:.2f}% (CI [{ci_lower:.2f}%, {ci_upper:.2f}%]) "
            f"consistent with claims"
        )
    }
    
    print(f"Baseline θ = {baseline_theta}, Stadlmann θ = {stadlmann_theta}")
    print(f"Mean boost: {mean_boost:.4f}%")
    print(f"95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%]")
    print(f"Claimed range: {claimed_range}")
    print(f"Claimed CI: {claimed_ci}")
    print(f"\nResult: {result['interpretation']}")
    
    return result


def test_scale_invariance(scales: List[int] = None, seed: int = 42) -> Dict[str, Any]:
    """
    Test 4: Scale Invariance Test
    
    Verify that the θ effect is consistent across different scales (10^4 to 10^6).
    
    Args:
        scales: List of k scales to test
        seed: Random seed
    
    Returns:
        Dict with test results and falsification status
    """
    print("\n" + "="*70)
    print("TEST 4: SCALE INVARIANCE TEST")
    print("="*70)
    print("Hypothesis: θ effects are consistent across 10^4 to 10^6 scales")
    print("Falsification criterion: Large variation in effects across scales\n")
    
    if scales is None:
        scales = [10**4, 10**5, 10**6]
    
    baseline_theta = 0.51
    stadlmann_theta = DIST_LEVEL_STADLMANN
    
    rel_diffs_by_scale = {}
    
    for scale in scales:
        try:
            pred_baseline = float(z5d_predictor_with_dist_level(scale, dist_level=baseline_theta))
            pred_stadlmann = float(z5d_predictor_with_dist_level(scale, dist_level=stadlmann_theta))
            
            rel_diff = abs(pred_stadlmann - pred_baseline) / pred_baseline
            rel_diffs_by_scale[scale] = rel_diff
            
            print(f"Scale 10^{int(np.log10(scale))}: rel_diff = {rel_diff:.6f} ({rel_diff*100:.4f}%)")
        except Exception as e:
            print(f"Warning: Failed for scale {scale}: {e}")
            rel_diffs_by_scale[scale] = np.nan
    
    rel_diffs = np.array([v for v in rel_diffs_by_scale.values() if not np.isnan(v)])
    
    if len(rel_diffs) > 1:
        # Calculate coefficient of variation
        cv = np.std(rel_diffs) / np.mean(rel_diffs) if np.mean(rel_diffs) > 0 else np.inf
        
        # Falsification: if CV > 0.5, effects are not scale-invariant
        falsified = cv > 0.5
    else:
        cv = np.nan
        falsified = False
    
    result = {
        'test_name': 'Scale Invariance Test',
        'scales': [int(s) for s in scales],
        'baseline_theta': float(baseline_theta),
        'stadlmann_theta': float(stadlmann_theta),
        'rel_diffs_by_scale': {int(k): float(v) if not np.isnan(v) else None for k, v in rel_diffs_by_scale.items()},
        'coefficient_of_variation': float(cv) if not np.isnan(cv) else None,
        'falsified': bool(falsified),
        'interpretation': (
            f"FALSIFIED: High variation (CV={cv:.3f}) suggests scale-dependent effects"
            if falsified else
            f"SUPPORTED: Low variation (CV={cv:.3f}) suggests scale-invariant effects"
        )
    }
    
    print(f"\nCoefficient of Variation: {cv:.4f}")
    print(f"Result: {result['interpretation']}")
    
    return result


def test_randomness(n_random: int = 20, seed: int = 42) -> Dict[str, Any]:
    """
    Test 5: Randomness Test
    
    Test if θ=0.525 is actually special compared to random θ values in the valid range.
    
    Args:
        n_random: Number of random θ values to test
        seed: Random seed
    
    Returns:
        Dict with test results and falsification status
    """
    print("\n" + "="*70)
    print("TEST 5: RANDOMNESS TEST")
    print("="*70)
    print("Hypothesis: θ=0.525 is special (not arbitrary)")
    print("Falsification criterion: Random θ values perform equally well\n")
    
    rng = np.random.default_rng(seed)
    k_test = 100000
    
    # Generate random theta values
    random_thetas = rng.uniform(0.51, 0.60, size=n_random)
    stadlmann_theta = DIST_LEVEL_STADLMANN
    
    # Get predictions for all thetas
    predictions = {}
    predictions[stadlmann_theta] = float(z5d_predictor_with_dist_level(k_test, dist_level=stadlmann_theta))
    
    for theta in random_thetas:
        try:
            pred = float(z5d_predictor_with_dist_level(k_test, dist_level=theta))
            predictions[theta] = pred
        except Exception as e:
            print(f"Warning: Failed for θ={theta}: {e}")
    
    # Calculate how many random thetas produce similar predictions to Stadlmann
    stadlmann_pred = predictions[stadlmann_theta]
    
    similar_count = 0
    SIMILARITY_THRESHOLD = 0.0001  # 0.01% relative difference
    
    for theta, pred in predictions.items():
        if theta != stadlmann_theta:
            rel_diff = abs(pred - stadlmann_pred) / stadlmann_pred
            if rel_diff < SIMILARITY_THRESHOLD:
                similar_count += 1
    
    similar_fraction = similar_count / n_random if n_random > 0 else 0
    
    # Falsification: if > 50% of random values are equally good, Stadlmann value is not special
    falsified = similar_fraction > 0.5
    
    result = {
        'test_name': 'Randomness Test',
        'k_value': int(k_test),
        'stadlmann_theta': float(stadlmann_theta),
        'n_random': int(n_random),
        'similar_count': int(similar_count),
        'similar_fraction': float(similar_fraction),
        'similarity_threshold': float(SIMILARITY_THRESHOLD),
        'falsified': bool(falsified),
        'interpretation': (
            f"FALSIFIED: {similar_fraction*100:.1f}% of random θ values equally good - "
            f"θ=0.525 not special"
            if falsified else
            f"SUPPORTED: Only {similar_fraction*100:.1f}% of random θ values equally good - "
            f"θ=0.525 appears special"
        )
    }
    
    print(f"Stadlmann θ = {stadlmann_theta}")
    print(f"Random θ values tested: {n_random}")
    print(f"Similar predictions: {similar_count} ({similar_fraction*100:.1f}%)")
    print(f"\nResult: {result['interpretation']}")
    
    return result


def run_all_tests(seed: int = 42) -> FalsificationResults:
    """
    Run all falsification tests.
    
    Args:
        seed: Random seed for reproducibility
    
    Returns:
        FalsificationResults object with all test results
    """
    print("\n" + "="*80)
    print(" STADLMANN DISTRIBUTION LEVEL FALSIFICATION EXPERIMENT")
    print("="*80)
    print(f"Random seed: {seed}")
    print(f"Stadlmann θ value: {DIST_LEVEL_STADLMANN}")
    print(f"Valid θ range: ({DIST_LEVEL_MIN}, {DIST_LEVEL_MAX}]")
    
    results = FalsificationResults()
    
    # Test 1: Independence
    try:
        test1 = test_independence(n_samples=100, seed=seed)
        results.add_test('independence', test1)
    except Exception as e:
        print(f"\nERROR in Independence Test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Monotonicity
    try:
        test2 = test_monotonicity(k_test=100000, n_levels=10, seed=seed)
        results.add_test('monotonicity', test2)
    except Exception as e:
        print(f"\nERROR in Monotonicity Test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Claimed Boost
    try:
        test3 = test_claimed_boost(n_primes=10000, n_bootstrap=1000, seed=seed)
        results.add_test('claimed_boost', test3)
    except Exception as e:
        print(f"\nERROR in Claimed Boost Test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Scale Invariance
    try:
        test4 = test_scale_invariance(scales=[10**4, 10**5, 10**6], seed=seed)
        results.add_test('scale_invariance', test4)
    except Exception as e:
        print(f"\nERROR in Scale Invariance Test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Randomness
    try:
        test5 = test_randomness(n_random=20, seed=seed)
        results.add_test('randomness', test5)
    except Exception as e:
        print(f"\nERROR in Randomness Test: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate summary
    results.generate_summary()
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Stadlmann Distribution Level Falsification Experiment'
    )
    parser.add_argument('--seed', type=int, default=42, 
                       help='Random seed for reproducibility')
    parser.add_argument('--output', type=str, 
                       default='experiments/stadlmann_falsification/results.json',
                       help='Output file for results')
    
    args = parser.parse_args()
    
    # Run all tests
    results = run_all_tests(seed=args.seed)
    
    # Print executive summary
    print("\n" + "="*80)
    print(" EXECUTIVE SUMMARY")
    print("="*80)
    
    summary = results.summary
    print(f"\nTotal tests: {summary['total_tests']}")
    print(f"Falsified tests: {summary['falsified_tests']}")
    print(f"Supported tests: {summary['supported_tests']}")
    print(f"Falsification rate: {summary['falsification_rate']*100:.1f}%")
    print(f"\nOVERALL STATUS: {summary['status']}")
    
    if summary['status'] == "HYPOTHESIS_FALSIFIED":
        print("\n⚠️  CRITICAL: The hypothesis has been FALSIFIED.")
        print("The Stadlmann 'density dial' claim does not hold under scrutiny.")
    elif summary['status'] == "PARTIAL_FALSIFICATION":
        print("\n⚠️  WARNING: Partial falsification detected.")
        print("Some aspects of the hypothesis do not hold.")
    else:
        print("\n✓ The hypothesis is SUPPORTED by the tests.")
        print("The Stadlmann 'density dial' claim appears valid.")
    
    # Save results
    output_file = args.output
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results.to_dict(), f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    print("\n" + "="*80)
    print(" EXPERIMENT COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
