"""
Test Suite for Z Framework System Instruction Compliance
========================================================

This test suite validates that the Z Framework system instruction is properly
implemented and enforced across all core components.

Tests cover:
1. Universal invariant formulation validation
2. Domain-specific form compliance  
3. Geometric resolution verification
4. Operational guidance enforcement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import numpy as np
import mpmath as mp
from src.core.system_instruction import (
    ZFrameworkSystemInstruction, 
    get_system_instruction,
    enforce_system_instruction,
    validate_system_constants,
    SYSTEM_CONSTANTS
)

def test_system_constants_validation():
    """Test that system constants meet Z Framework requirements."""
    print("Testing system constants validation...")
    
    validation = validate_system_constants()
    
    assert validation['constants_valid'], f"System constants validation failed: {validation['errors']}"
    assert validation['precision_adequate'], "Precision requirement not met (dps < 50)"
    
    # Check specific constants
    constants = validation['constants']
    
    # Speed of light should be approximately 299792458
    c_value = constants['c']['value']
    assert abs(c_value - 299792458.0) < 1.0, f"Speed of light constant incorrect: {c_value}"
    
    # Golden ratio should be approximately 1.618
    phi_value = constants['phi']['value'] 
    assert abs(phi_value - 1.618033988) < 0.001, f"Golden ratio constant incorrect: {phi_value}"
    
    # Optimal k should be 0.3
    k_value = constants['k_star']['value']
    assert abs(k_value - 0.3) < 0.001, f"Optimal k constant incorrect: {k_value}"
    
    print("✓ System constants validation passed")

def test_universal_invariant_formulation():
    """Test universal Z form Z = A(B/c) validation."""
    print("Testing universal invariant formulation...")
    
    system_instruction = get_system_instruction()
    
    # Test with linear transformation A(x) = 2x
    A_linear = lambda x: 2.0 * x
    B = 1.5e8  # Rate quantity
    c = 299792458.0  # Speed of light
    
    validation = system_instruction.validate_universal_form(A_linear, B, c)
    
    assert validation['universal_form_compliant'], f"Universal form validation failed: {validation['errors']}"
    assert validation['c_is_invariant'], "Speed of light invariant check failed"
    assert validation['precision_met'], "Precision requirement not met"
    
    # Check that result follows Z = A(B/c) = 2 * (1.5e8 / 299792458)
    expected_ratio = B / c
    expected_result = 2.0 * expected_ratio
    actual_result = validation['z_result']
    
    assert abs(actual_result - expected_result) < 1e-10, f"Z computation incorrect: expected {expected_result}, got {actual_result}"
    
    print("✓ Universal invariant formulation test passed")

def test_physical_domain_validation():
    """Test physical domain Z = T(v/c) validation."""
    print("Testing physical domain validation...")
    
    system_instruction = get_system_instruction()
    
    # Test time dilation transformation
    def time_dilation_func(x):
        """T(v/c) = τ₀/√(1-(v/c)²) where x = v/c"""
        return 1.0 / mp.sqrt(1 - x**2)
    
    v = 0.6 * 299792458.0  # 60% speed of light
    c = 299792458.0
    
    validation = system_instruction.validate_physical_domain(time_dilation_func, v, c)
    
    assert validation['physical_domain_compliant'], f"Physical domain validation failed: {validation['errors']}"
    assert validation['causality_satisfied'], "Causality constraint violation"
    assert validation['relativistic_effects_present'], "Relativistic effects should be present at 60% c"
    assert validation['empirical_basis'] == 'special_relativity', "Empirical basis should be special relativity"
    
    # Check velocity ratio
    expected_ratio = v / c
    actual_ratio = validation['velocity_ratio']
    assert abs(actual_ratio - expected_ratio) < 1e-10, f"Velocity ratio incorrect: expected {expected_ratio}, got {actual_ratio}"
    
    print("✓ Physical domain validation test passed")

def test_discrete_domain_validation():
    """Test discrete domain Z = n(Δ_n/Δ_max) validation."""
    print("Testing discrete domain validation...")
    
    system_instruction = get_system_instruction()
    
    # Test with specific integer
    n = 12
    
    # Calculate expected frame shift using curvature formula
    from sympy import divisors
    from src.core.axioms import curvature
    
    d_n = len(list(divisors(n)))
    expected_delta_n = curvature(n, d_n)
    delta_max = float(mp.exp(2))  # e²
    
    validation = system_instruction.validate_discrete_domain(n, expected_delta_n, delta_max)
    
    assert validation['discrete_domain_compliant'], f"Discrete domain validation failed: {validation['errors']}"
    assert validation['e_squared_normalization'], "e² normalization check failed"
    assert validation['curvature_formula_correct'], "Curvature formula validation failed"
    assert validation['variance_minimized'], "Variance minimization check failed"
    
    # Check ratio calculation
    expected_ratio = expected_delta_n / delta_max
    actual_ratio = validation['ratio_delta_n_over_delta_max']
    assert abs(actual_ratio - expected_ratio) < 1e-10, f"Delta ratio incorrect: expected {expected_ratio}, got {actual_ratio}"
    
    print("✓ Discrete domain validation test passed")

def test_geometric_resolution_validation():
    """Test geometric resolution via curvature-based geodesics."""
    print("Testing geometric resolution validation...")
    
    system_instruction = get_system_instruction()
    
    # Test with specific parameters
    n = 17  # Prime number
    k = 0.3  # Optimal curvature parameter
    
    validation = system_instruction.validate_geometric_resolution(n, k)
    
    assert validation['geometric_resolution_compliant'], f"Geometric resolution validation failed: {validation['errors']}"
    assert validation['geodesic_transformation_used'], "Geodesic transformation not detected"
    assert validation['optimal_k_used'], "Optimal k parameter not used"
    assert validation['golden_ratio_modular'], "Golden ratio modular arithmetic failed"
    
    # Check that result is in expected range [0, φ)
    theta_result = validation['theta_prime_result']
    phi = float(mp.sqrt(5) + 1) / 2
    assert 0 <= theta_result < phi, f"θ'(n,k) result {theta_result} not in range [0, φ)"
    
    print("✓ Geometric resolution validation test passed")

def test_empirical_claim_validation():
    """Test empirical claim validation with quantitative evidence."""
    print("Testing empirical claim validation...")
    
    system_instruction = get_system_instruction()
    
    # Test validated claim with proper evidence
    claim = "conditional prime density improvement under canonical benchmark methodology at k* ≈ 0.3"
    evidence = {
        'statistical_measure': 'enhancement_percentage',
        'confidence_interval': [14.6, 15.4],
        'p_value': 1e-6,
        'sample_size': 1000,
        'reproducible_code': 'src/number-theory/prime-curve/proof.py'
    }
    
    validation = system_instruction.validate_empirical_claim(claim, evidence, confidence_level=0.95)
    
    assert validation['empirically_substantiated'], "Valid empirical claim should be substantiated"
    assert validation['confidence_level_met'], "Confidence level should be met (p < 0.05)"
    assert validation['reproducible_evidence'], "Reproducible evidence should be detected"
    assert validation['hypothesis_vs_validated'] == 'validated', "Should be classified as validated"
    
    # Test hypothesis claim without sufficient evidence
    hypothesis_claim = "Primes follow quantum entanglement patterns"
    weak_evidence = {
        'statistical_measure': 'correlation',
        'p_value': 0.2,  # Not significant
        'sample_size': 10   # Too small
    }
    
    weak_validation = system_instruction.validate_empirical_claim(hypothesis_claim, weak_evidence)
    
    assert not weak_validation['empirically_substantiated'], "Weak claim should not be substantiated"
    assert not weak_validation['confidence_level_met'], "Weak confidence level should not be met"
    assert weak_validation['hypothesis_vs_validated'] == 'hypothesis', "Should remain classified as hypothesis"
    
    print("✓ Empirical claim validation test passed")

def test_scientific_communication_validation():
    """Test scientific communication standards validation."""
    print("Testing scientific communication validation...")
    
    system_instruction = get_system_instruction()
    
    # Test proper scientific communication
    good_text = """
    The Z Framework demonstrates empirically validated results with k* ≈ 0.3 
    yielding conditional prime density improvement under canonical benchmark methodology (CI [14.6%, 15.4%], p < 10^{-6}).
    This hypothesis requires further validation through extended analysis.
    """
    
    good_validation = system_instruction.validate_scientific_communication(good_text)
    
    assert good_validation['scientific_tone'], "Scientific tone should be maintained"
    assert good_validation['evidence_citations'], "Evidence citations should be present"
    
    # Test problematic communication with validation claims but no evidence
    bad_text = """
    The Z Framework definitely proves that primes always follow golden ratio patterns.
    This empirically validated result certainly demonstrates quantum consciousness in number theory.
    Mathematics is definitely connected to universal consciousness.
    """
    
    bad_validation = system_instruction.validate_scientific_communication(bad_text)
    
    assert len(bad_validation['unsupported_assertions']) > 0, "Should detect unsupported assertions"
    assert not bad_validation['evidence_citations'], "Should flag missing evidence citations"
    
    print("✓ Scientific communication validation test passed")

def test_full_compliance_verification():
    """Test complete system instruction compliance verification."""
    print("Testing full compliance verification...")
    
    system_instruction = get_system_instruction()
    
    # Test compliant operation
    compliant_data = {
        'A': lambda x: x,  # Linear transformation
        'B': 1.0e8,
        'c': 299792458.0,
        'domain': 'physical',
        'v': 0.5 * 299792458.0,
        'n': 13,
        'k': 0.3,
        'empirical_claims': {
            'test_claim': {
                'statistical_measure': 'enhancement',
                'confidence_interval': [14.0, 16.0],
                'p_value': 0.01,
                'sample_size': 100,
                'reproducible_code': 'test.py'
            }
        },
        'communication_text': 'Results show empirically validated enhancement (CI [14%, 16%], p < 0.05).'
    }
    
    compliance = system_instruction.verify_full_compliance(compliant_data)
    
    assert compliance['overall_compliant'], f"Should be compliant: score={compliance['compliance_score']}"
    assert compliance['compliance_score'] >= 0.8, f"Compliance score too low: {compliance['compliance_score']}"
    assert len(compliance['critical_violations']) == 0, f"Should have no critical violations: {compliance['critical_violations']}"
    
    # Test non-compliant operation
    non_compliant_data = {
        'A': lambda x: x,
        'B': 1.0e8,
        'c': 100.0,  # Wrong speed of light
        'domain': 'unknown',  # Invalid domain
        'empirical_claims': {
            'weak_claim': {
                'p_value': 0.9,  # Not significant
                'sample_size': 5   # Too small
            }
        }
    }
    
    non_compliance = system_instruction.verify_full_compliance(non_compliant_data)
    
    assert not non_compliance['overall_compliant'], "Should not be compliant"
    assert non_compliance['compliance_score'] < 0.8, "Compliance score should be low"
    assert len(non_compliance['critical_violations']) > 0, "Should have critical violations"
    
    print("✓ Full compliance verification test passed")

@enforce_system_instruction
def test_decorated_function(v, c):
    """Test function with system instruction enforcement decorator."""
    return v / c

def test_enforcement_decorator():
    """Test the system instruction enforcement decorator."""
    print("Testing enforcement decorator...")
    
    # This should work without warnings for compliant parameters
    result = test_decorated_function(v=0.5 * 299792458.0, c=299792458.0)
    expected = 0.5
    assert abs(result - expected) < 1e-10, f"Decorated function result incorrect: {result}"
    
    print("✓ Enforcement decorator test passed")

def run_all_tests():
    """Run all system instruction tests."""
    print("=" * 60)
    print("Z Framework System Instruction Test Suite")
    print("=" * 60)
    
    tests = [
        test_system_constants_validation,
        test_universal_invariant_formulation, 
        test_physical_domain_validation,
        test_discrete_domain_validation,
        test_geometric_resolution_validation,
        test_empirical_claim_validation,
        test_scientific_communication_validation,
        test_full_compliance_verification,
        test_enforcement_decorator
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All Z Framework system instruction tests passed!")
        return True
    else:
        print(f"❌ {failed} tests failed. System instruction implementation needs review.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)