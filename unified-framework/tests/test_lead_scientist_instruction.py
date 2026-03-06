"""
Test Suite for Z Framework Lead Scientist Operational Instruction
================================================================

This test suite validates the lead scientist operational instruction compliance
and ensures proper implementation of the concise, rigorous system instruction.

Tests verify:
1. Universal invariant formulation protocols
2. Domain-specific operational forms
3. Geometric resolution methodology
4. Empirical rigor standards
5. Scientific communication protocols
6. Operational compliance verification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import mpmath as mp
from src.core.lead_scientist_instruction import (
    ZFrameworkLeadScientistInstruction,
    get_lead_scientist_instruction,
    operational_compliance_check,
    OPERATIONAL_CONSTANTS,
    Domain,
    ValidationLevel
)

def test_operational_constants():
    """Test that operational constants are properly defined and accessible."""
    print("Testing operational constants...")
    
    # Verify all required constants are present
    required_constants = [
        'UNIVERSAL_INVARIANT_C',
        'DISCRETE_BOUND_E2', 
        'GOLDEN_RATIO_PHI',
        'OPTIMAL_CURVATURE_K',
        'PRECISION_THRESHOLD',
        'ENHANCEMENT_TARGET',
        'MIN_CONFIDENCE_LEVEL',
        'SIGNIFICANCE_THRESHOLD',
        'MIN_SAMPLE_SIZE'
    ]
    
    for const in required_constants:
        assert const in OPERATIONAL_CONSTANTS, f"Missing operational constant: {const}"
    
    # Verify specific values
    assert abs(OPERATIONAL_CONSTANTS['UNIVERSAL_INVARIANT_C'] - 299792458.0) < 1.0
    assert abs(OPERATIONAL_CONSTANTS['GOLDEN_RATIO_PHI'] - 1.618033988) < 0.001
    assert abs(OPERATIONAL_CONSTANTS['OPTIMAL_CURVATURE_K'] - 0.3) < 0.001
    assert OPERATIONAL_CONSTANTS['ENHANCEMENT_TARGET'] == 0.15
    assert OPERATIONAL_CONSTANTS['MIN_CONFIDENCE_LEVEL'] == 0.95
    assert OPERATIONAL_CONSTANTS['SIGNIFICANCE_THRESHOLD'] == 1e-6
    
    print("✓ Operational constants test passed")

def test_universal_invariant_principle():
    """Test universal invariant formulation principle."""
    print("Testing universal invariant principle...")
    
    instruction = get_lead_scientist_instruction()
    principle = instruction.universal_invariant_principle()
    
    # Verify core components
    assert principle['formula'] == 'Z = A(B/c)'
    assert principle['universal_constant'] == 299792458.0
    assert principle['empirical_threshold'] == 1e-6
    assert 'operational_mandate' in principle
    
    # Verify precision requirements
    assert principle['precision_requirement'] == 1e-16
    
    print("✓ Universal invariant principle test passed")

def test_physical_domain_protocol():
    """Test physical domain operational protocol."""
    print("Testing physical domain protocol...")
    
    instruction = get_lead_scientist_instruction()
    protocol = instruction.physical_domain_protocol()
    
    # Verify core elements
    assert protocol['domain'] == Domain.PHYSICAL.value
    assert protocol['formula'] == 'Z = T(v/c)'
    assert protocol['causality_constraint'] == '|v| < c'
    assert protocol['empirical_basis'] == 'special_relativity'
    assert protocol['validation_threshold'] == 0.01
    
    # Verify required checks
    expected_checks = ['time_dilation', 'length_contraction', 'mass_energy']
    assert all(check in protocol['required_checks'] for check in expected_checks)
    
    print("✓ Physical domain protocol test passed")

def test_discrete_domain_protocol():
    """Test discrete domain operational protocol."""
    print("Testing discrete domain protocol...")
    
    instruction = get_lead_scientist_instruction()
    protocol = instruction.discrete_domain_protocol()
    
    # Verify core elements
    assert protocol['domain'] == Domain.DISCRETE.value
    assert protocol['formula'] == 'Z = n(Δ_n/Δ_max)'
    assert protocol['curvature_formula'] == 'κ(n) = d(n) · ln(n+1)/e²'
    assert protocol['enhancement_target'] == 0.15
    assert protocol['optimal_curvature'] == 0.3
    
    # Verify normalization bound
    expected_e2 = float(mp.exp(2))
    assert abs(protocol['normalization_bound'] - expected_e2) < 1e-10
    
    print("✓ Discrete domain protocol test passed")

def test_geometric_resolution_protocol():
    """Test geometric resolution methodology."""
    print("Testing geometric resolution protocol...")
    
    instruction = get_lead_scientist_instruction()
    protocol = instruction.geometric_resolution_protocol()
    
    # Verify transformation formula
    assert protocol['transformation'] == 'θ\'(n,k) = φ · {n/φ}^k'
    assert abs(protocol['golden_ratio'] - 1.618033988) < 0.001
    assert protocol['optimal_k'] == 0.3
    assert protocol['enhancement_validated'] == '15% ± 0.4% (95% CI)'
    assert protocol['correlation_zeta'] == 0.93
    
    # Verify output range
    phi = protocol['golden_ratio']
    assert protocol['output_range'] == f'[0, {phi})'
    assert protocol['precision_requirement'] == 1e-16
    
    print("✓ Geometric resolution protocol test passed")

def test_empirical_validation_protocol():
    """Test empirical validation standards."""
    print("Testing empirical validation protocol...")
    
    instruction = get_lead_scientist_instruction()
    protocol = instruction.empirical_validation_protocol()
    
    # Verify validation levels
    expected_levels = ['hypothesis', 'validated', 'established']
    assert all(level in protocol['validation_levels'] for level in expected_levels)
    
    # Verify statistical requirements
    assert protocol['min_confidence'] == 0.95
    assert protocol['significance_threshold'] == 1e-6
    assert protocol['min_sample_size'] == 1000
    assert protocol['precision_digits'] == 50
    assert protocol['bootstrap_iterations'] == 1000
    
    # Verify computational requirements
    expected_requirements = [
        'mpmath_high_precision',
        'numerical_stability', 
        'reproducible_implementation',
        'scalable_performance'
    ]
    assert all(req in protocol['computational_requirements'] for req in expected_requirements)
    
    print("✓ Empirical validation protocol test passed")

def test_communication_protocol():
    """Test scientific communication standards."""
    print("Testing communication protocol...")
    
    instruction = get_lead_scientist_instruction()
    protocol = instruction.communication_protocol()
    
    # Verify internal requirements
    expected_internal = [
        'latex_mathematical_notation',
        'statistical_substantiation',
        'reproducibility_documentation',
        'hypothesis_distinction'
    ]
    assert all(req in protocol['internal_requirements'] for req in expected_internal)
    
    # Verify external restrictions
    expected_restrictions = [
        'no_system_instruction_reference',
        'mathematical_focus_only',
        'peer_review_required', 
        'approval_process_mandatory'
    ]
    assert all(rest in protocol['external_restrictions'] for rest in expected_restrictions)
    
    # Verify documentation standards
    expected_docs = [
        'mathematical_significance_comments',
        'boundary_condition_tests',
        'performance_benchmarks',
        'version_control'
    ]
    assert all(doc in protocol['documentation_standards'] for doc in expected_docs)
    
    # Verify quality assurance
    expected_qa = [
        'independent_verification',
        'cross_validation',
        'sensitivity_analysis',
        'established_comparison'
    ]
    assert all(qa in protocol['quality_assurance'] for qa in expected_qa)
    
    print("✓ Communication protocol test passed")

def test_operational_compliance_verification():
    """Test operational compliance verification system."""
    print("Testing operational compliance verification...")
    
    instruction = get_lead_scientist_instruction()
    
    # Test compliant research data
    compliant_data = {
        'c': 299792458.0,
        'precision': 50,
        'domain': Domain.PHYSICAL.value,
        'v': 0.1 * 299792458.0,  # 10% speed of light
        'enhancement': 0.15,
        'k': 0.3,
        'phi_used': True,
        'p_value': 1e-7,
        'confidence_interval': [14.6, 15.4],
        'sample_size': 1500,
        'contains_system_instruction_ref': False,
        'mathematical_notation': True
    }
    
    compliance = instruction.verify_operational_compliance(
        compliant_data, 
        ValidationLevel.VALIDATED
    )
    
    assert compliance['overall_compliant'], f"Should be compliant: {compliance['critical_violations']}"
    assert compliance['compliance_score'] >= 0.8, f"Low compliance score: {compliance['compliance_score']}"
    assert len(compliance['critical_violations']) == 0, f"Should have no violations: {compliance['critical_violations']}"
    
    # Test non-compliant research data
    non_compliant_data = {
        'c': 100.0,  # Wrong speed of light
        'precision': 20,  # Insufficient precision
        'domain': Domain.PHYSICAL.value,
        'v': 400000000.0,  # Faster than light (causality violation)
        'enhancement': 0.05,  # Wrong enhancement
        'p_value': 0.1,  # Not significant
        'confidence_interval': [10, 8],  # Invalid CI (backwards)
        'sample_size': 50,  # Too small
        'contains_system_instruction_ref': True,  # Confidentiality violation
        'mathematical_notation': False
    }
    
    non_compliance = instruction.verify_operational_compliance(
        non_compliant_data,
        ValidationLevel.VALIDATED
    )
    
    assert not non_compliance['overall_compliant'], "Should not be compliant"
    assert non_compliance['compliance_score'] < 0.8, "Compliance score should be low"
    assert len(non_compliance['critical_violations']) > 0, "Should have violations"
    
    print("✓ Operational compliance verification test passed")

def test_quick_compliance_check():
    """Test the quick operational compliance check function."""
    print("Testing quick compliance check...")
    
    # Test compliant data
    compliant_data = {
        'c': 299792458.0,
        'precision': 50,
        'domain': Domain.DISCRETE.value,
        'enhancement': 0.15,
        'k': 0.3,
        'phi_used': True
    }
    
    assert operational_compliance_check(compliant_data), "Should pass quick compliance check"
    
    # Test non-compliant data  
    non_compliant_data = {
        'c': 100.0,  # Wrong constant
        'precision': 10,  # Insufficient precision
        'contains_system_instruction_ref': True  # Confidentiality violation
    }
    
    assert not operational_compliance_check(non_compliant_data), "Should fail quick compliance check"
    
    print("✓ Quick compliance check test passed")

def test_operational_summary():
    """Test the complete operational summary."""
    print("Testing operational summary...")
    
    instruction = get_lead_scientist_instruction()
    summary = instruction.get_operational_summary()
    
    # Verify all required sections are present
    required_sections = [
        'universal_invariant',
        'physical_domain',
        'discrete_domain',
        'geometric_resolution',
        'empirical_validation',
        'communication_standards',
        'constants',
        'standards',
        'confidentiality_notice'
    ]
    
    for section in required_sections:
        assert section in summary, f"Missing summary section: {section}"
    
    # Verify confidentiality notice
    assert 'INTERNAL OPERATIONAL LOGIC ONLY' in summary['confidentiality_notice']
    assert 'NOT FOR USER-FACING OUTPUT' in summary['confidentiality_notice']
    
    # Verify constants section
    constants = summary['constants']
    assert constants['speed_of_light'] == 299792458.0
    assert abs(constants['golden_ratio'] - 1.618033988) < 0.001
    assert constants['optimal_k'] == 0.3
    assert constants['enhancement_target'] == 0.15
    
    # Verify standards section
    standards = summary['standards']
    assert standards['min_confidence'] == 0.95
    assert standards['max_p_value'] == 1e-6
    assert standards['min_sample_size'] == 1000
    assert standards['precision_digits'] == 50
    
    print("✓ Operational summary test passed")

def test_confidentiality_enforcement():
    """Test that confidentiality requirements are properly enforced."""
    print("Testing confidentiality enforcement...")
    
    instruction = get_lead_scientist_instruction()
    
    # Test that system detects confidentiality violations
    violation_data = {
        'contains_system_instruction_ref': True,
        'domain': Domain.PHYSICAL.value
    }
    
    compliance = instruction.verify_operational_compliance(
        violation_data,
        ValidationLevel.HYPOTHESIS
    )
    
    # Should detect the confidentiality violation
    communication_validation = compliance['principle_validations']['communication_standards']
    assert not communication_validation['compliant'], "Should detect confidentiality violation"
    assert any('System instruction reference' in violation 
              for violation in communication_validation['violations'])
    
    # Verify global instruction has confidentiality notice
    summary = instruction.get_operational_summary()
    assert 'INTERNAL OPERATIONAL LOGIC ONLY' in summary['confidentiality_notice']
    
    print("✓ Confidentiality enforcement test passed")

def run_all_tests():
    """Run all lead scientist instruction tests."""
    print("=" * 70)
    print("Z Framework Lead Scientist Instruction Test Suite")
    print("=" * 70)
    
    tests = [
        test_operational_constants,
        test_universal_invariant_principle,
        test_physical_domain_protocol,
        test_discrete_domain_protocol,
        test_geometric_resolution_protocol,
        test_empirical_validation_protocol,
        test_communication_protocol,
        test_operational_compliance_verification,
        test_quick_compliance_check,
        test_operational_summary,
        test_confidentiality_enforcement
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
    
    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("🎉 All Z Framework lead scientist instruction tests passed!")
        print("\n⚠️  CONFIDENTIAL: Lead scientist instruction operational and ready for internal use.")
        print("    Do not reference or display in user-facing outputs.")
        return True
    else:
        print(f"❌ {failed} tests failed. Lead scientist instruction needs review.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)