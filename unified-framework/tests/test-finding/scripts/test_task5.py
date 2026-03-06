"""
Test script for Task 5: Cross-Domain Correlations (Orbital, Quantum)
=====================================================================

Validates the core functionality and key metrics of the Task 5 implementation.
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

import json
import numpy as np
from experiments.task5_cross_domain_correlations import Task5CrossDomainCorrelations

def test_task5_basic_functionality():
    """Test basic initialization and functionality."""
    print("Testing Task 5 basic functionality...")
    
    # Initialize
    task5 = Task5CrossDomainCorrelations()
    
    # Check orbital data
    assert len(task5.ratios) >= 10, f"Expected >=10 orbital ratios, got {len(task5.ratios)}"
    assert len(task5.exoplanet_periods) >= 10, f"Expected >=10 exoplanets, got {len(task5.exoplanet_periods)}"
    
    # Check ratio ranges
    assert np.min(task5.ratios) > 0, "All ratios should be positive"
    assert np.max(task5.ratios) < 1000, "Ratios should be reasonable (< 1000)"
    
    print(f"✓ Orbital data: {len(task5.ratios)} ratios from {len(task5.exoplanet_periods)} exoplanets")
    
    # Test small-scale data generation
    primes, zetas = task5.generate_primes_and_zetas(N=10000, M=20)
    assert len(primes) > 1000, f"Expected >1000 primes, got {len(primes)}"
    assert len(zetas) == 20, f"Expected 20 zeta zeros, got {len(zetas)}"
    
    print(f"✓ Data generation: {len(primes)} primes, {len(zetas)} zeta zeros")
    
    # Test path integral simulation
    integrals, convergence = task5.path_integral_simulation()
    assert len(integrals) > 0, "Path integrals should be computed"
    assert len(convergence) > 0, "Convergence steps should be recorded"
    assert np.all(convergence > 0), "All convergence steps should be positive"
    
    print(f"✓ Path integrals: {len(integrals)} computed, convergence {np.mean(convergence):.1f} steps")
    
    # Test chiral integration
    chiral_steps, efficiency_gains = task5.chiral_integration()
    assert len(efficiency_gains) > 0, "Efficiency gains should be computed"
    assert 15 <= np.mean(efficiency_gains) <= 35, f"Efficiency gain should be 15-35%, got {np.mean(efficiency_gains):.1f}%"
    
    print(f"✓ Chiral integration: {np.mean(efficiency_gains):.1f}% efficiency gain")
    
    print("All basic functionality tests passed!")
    return True

def test_task5_correlation_requirements():
    """Test correlation requirements."""
    print("\nTesting Task 5 correlation requirements...")
    
    # Load results from full run
    results_file = '/home/runner/work/unified-framework/unified-framework/experiments/task5_results.json'
    
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        metrics = results['metrics']
        
        # Test key requirements
        r_orbital_zeta = metrics['r_orbital_zeta']
        efficiency_gain = metrics['efficiency_gain']
        resonance_count = metrics['resonance_count']
        
        print(f"r_orbital_zeta: {r_orbital_zeta:.6f} (target: ≈0.996)")
        print(f"efficiency_gain: {efficiency_gain:.2f}% (target: 20-30%)")
        print(f"resonance_count: {resonance_count} (target: >0)")
        
        # Validation
        assert r_orbital_zeta >= 0.9, f"r_orbital_zeta should be ≥0.9, got {r_orbital_zeta:.3f}"
        assert 20 <= efficiency_gain <= 30, f"Efficiency gain should be 20-30%, got {efficiency_gain:.1f}%"
        assert resonance_count > 0, f"Should find resonance clusters, got {resonance_count}"
        
        # Check for κ≈0.739 resonance
        mean_kappa = metrics.get('mean_resonance_kappa', 0)
        assert 0.7 <= mean_kappa <= 0.8, f"Mean resonance κ should be ≈0.739, got {mean_kappa:.3f}"
        
        print("✓ All correlation requirements met!")
        return True
    else:
        print("⚠ Results file not found, skipping correlation tests")
        return False

def test_task5_outputs():
    """Test expected outputs."""
    print("\nTesting Task 5 outputs...")
    
    # Check file existence
    expected_files = [
        '/home/runner/work/unified-framework/unified-framework/experiments/task5_cross_domain_correlations.py',
        '/home/runner/work/unified-framework/unified-framework/experiments/task5_results.json',
        '/home/runner/work/unified-framework/unified-framework/experiments/task5_cross_domain_results.png'
    ]
    
    for file_path in expected_files:
        assert os.path.exists(file_path), f"Expected file not found: {file_path}"
        print(f"✓ Found: {os.path.basename(file_path)}")
    
    # Check JSON structure
    with open('/home/runner/work/unified-framework/unified-framework/experiments/task5_results.json', 'r') as f:
        results = json.load(f)
    
    # Required keys
    required_keys = ['metrics', 'report', 'correlations', 'resonance_clusters']
    for key in required_keys:
        assert key in results, f"Missing key in results: {key}"
    
    # Required metrics
    required_metrics = ['r_orbital_zeta', 'efficiency_gain', 'resonance_count']
    for metric in required_metrics:
        assert metric in results['metrics'], f"Missing metric: {metric}"
    
    print("✓ All expected outputs present!")
    return True

def main():
    """Run all Task 5 tests."""
    print("=" * 60)
    print("TASK 5: CROSS-DOMAIN CORRELATIONS - VALIDATION TESTS")
    print("=" * 60)
    
    try:
        # Run tests
        test_task5_basic_functionality()
        test_task5_correlation_requirements()
        test_task5_outputs()
        
        print("\n" + "=" * 60)
        print("✓ ALL TASK 5 TESTS PASSED")
        print("✓ Task 5 implementation successfully meets requirements")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)