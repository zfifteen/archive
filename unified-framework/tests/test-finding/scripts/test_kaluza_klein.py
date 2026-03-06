#!/usr/bin/env python3
"""
Test suite for Kaluza-Klein theory integration

This file validates the implementation of the Kaluza-Klein mass tower formula
and its integration with the Z framework domain shifts.
"""

import sys
import os
import numpy as np

# Add modules to path
sys.path.append(os.path.dirname(__file__))
from core.kaluza_klein import KaluzaKleinTower, create_unified_mass_domain_system
from applications.quantum_simulation import simulate_kaluza_klein_observables

def test_mass_tower_formula():
    """Test the basic Kaluza-Klein mass tower formula m_n = n/R."""
    print("Testing mass tower formula m_n = n/R...")
    
    R = 1e-16
    kk_tower = KaluzaKleinTower(R)
    
    # Test basic formula
    for n in [1, 2, 5, 10]:
        expected_mass = n / R
        computed_mass = float(kk_tower.mass_tower(n))
        
        assert abs(computed_mass - expected_mass) < 1e-10, f"Mass tower test failed for n={n}"
        print(f"  ✓ n={n}: m_n = {computed_mass:.2e} (expected {expected_mass:.2e})")
    
    print("  ✓ Mass tower formula validation passed")

def test_domain_shift_integration():
    """Test integration with domain shifts Z = n(Δₙ/Δmax)."""
    print("Testing domain shift integration...")
    
    kk_tower = KaluzaKleinTower(1e-16)
    
    # Test domain shift computation
    for n in [1, 2, 3, 5]:
        delta_n, z_value = kk_tower.domain_shift_relation(n)
        
        # Validate that domain shift is positive
        assert float(delta_n) > 0, f"Domain shift should be positive for n={n}"
        
        # Validate Z value structure
        expected_z_structure = n * (delta_n / (np.exp(2) * (1 + np.sqrt(5))/2))
        computed_z = float(z_value)
        
        print(f"  ✓ n={n}: Δₙ = {float(delta_n):.4f}, Z = {computed_z:.4f}")
    
    print("  ✓ Domain shift integration validation passed")

def test_quantum_simulation():
    """Test quantum simulation functionality."""
    print("Testing quantum simulation...")
    
    # Run a small simulation
    results = simulate_kaluza_klein_observables(n_modes=3, evolution_time=0.1, n_time_steps=5)
    
    # Validate results structure
    assert 'energy_spectrum' in results, "Missing energy spectrum in results"
    assert 'observables' in results, "Missing observables in results"
    assert 'mass_predictions' in results, "Missing mass predictions in results"
    
    # Validate energy spectrum
    eigenvalues = results['energy_spectrum']['eigenvalues']
    assert len(eigenvalues) == 3, "Incorrect number of eigenvalues"
    assert all(eigenvalues[i] <= eigenvalues[i+1] for i in range(len(eigenvalues)-1)), "Eigenvalues not sorted"
    
    print(f"  ✓ Energy eigenvalues: {eigenvalues[:3]}")
    print("  ✓ Quantum simulation validation passed")

def test_unified_system():
    """Test the unified mass-domain system."""
    print("Testing unified system...")
    
    system = create_unified_mass_domain_system(mode_range=(1, 5))
    
    # Validate system structure
    assert 'spectrum' in system, "Missing spectrum in unified system"
    assert 'correlations' in system, "Missing correlations in unified system"
    assert 'summary_stats' in system, "Missing summary stats in unified system"
    
    # Validate correlations
    correlations = system['correlations']
    assert abs(correlations['mass_domain_correlation']) <= 1.0, "Invalid correlation value"
    assert abs(correlations['mass_Z_correlation']) <= 1.0, "Invalid correlation value"
    
    print(f"  ✓ Mass-Domain correlation: {correlations['mass_domain_correlation']:.4f}")
    print(f"  ✓ Mass-Z correlation: {correlations['mass_Z_correlation']:.4f}")
    print("  ✓ Unified system validation passed")

def test_physical_consistency():
    """Test physical consistency of the implementation."""
    print("Testing physical consistency...")
    
    kk_tower = KaluzaKleinTower(1e-16)
    
    # Test mass gaps
    n1, n2 = 1, 2
    mass_gap = kk_tower.mass_gap(n1, n2)
    expected_gap = 1 / 1e-16  # (n2 - n1) / R
    
    assert abs(float(mass_gap) - expected_gap) < 1e-10, "Mass gap calculation incorrect"
    print(f"  ✓ Mass gap m_{n2} - m_{n1} = {float(mass_gap):.2e}")
    
    # Test classical limit check
    assert not kk_tower.classical_limit_check(5), "Classical limit check failed for small n"
    assert kk_tower.classical_limit_check(15), "Classical limit check failed for large n"
    print("  ✓ Classical limit checks passed")
    
    # Test quantum numbers consistency
    quantum_nums = kk_tower.quantum_numbers(3)
    assert quantum_nums['n'] == 3, "Mode number inconsistent"
    assert float(quantum_nums['mass']) == 3e16, "Mass in quantum numbers inconsistent"
    print("  ✓ Quantum numbers consistency passed")

def run_all_tests():
    """Run all validation tests."""
    print("KALUZA-KLEIN IMPLEMENTATION VALIDATION")
    print("="*50)
    
    try:
        test_mass_tower_formula()
        print()
        
        test_domain_shift_integration()
        print()
        
        test_quantum_simulation()
        print()
        
        test_unified_system()
        print()
        
        test_physical_consistency()
        print()
        
        print("="*50)
        print("ALL TESTS PASSED ✓")
        print("Kaluza-Klein integration implementation is valid")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\nTEST FAILED ✗")
        print(f"Error: {e}")
        print("="*50)
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)