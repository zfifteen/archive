#!/usr/bin/env python3
"""
Tests for Mission Charter Compliance Validator

Tests the validate_charter.py tool to ensure it correctly identifies
compliant and non-compliant deliverables.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from validate_charter import (
    parse_deliverable,
    validate_charter_compliance,
    generate_manifest,
    calculate_completeness,
    CHARTER_ELEMENTS
)


def test_parse_deliverable_all_elements():
    """Test parsing a deliverable with all charter elements."""
    content = """
# Test Deliverable

## First Principles
Some axioms here.

## Ground Truth & Provenance
Sources and timestamps.

## Reproducibility
Commands and seeds.

## Failure Knowledge
Known issues.

## Constraints
Legal and ethical.

## Context
Who, what, when, where, why.

## Models & Limits
Assumptions and ranges.

## Interfaces
Commands and paths.

## Calibration
Parameters and tuning.

## Purpose
Goals and metrics.
"""
    
    elements = parse_deliverable(content)
    
    # All elements should be found
    for element in CHARTER_ELEMENTS.keys():
        assert len(elements[element]) > 0, f"Element '{element}' not found"
        line_num, heading = elements[element][0]
        assert line_num > 0, f"Element '{element}' has invalid line number"
    
    print("✓ test_parse_deliverable_all_elements PASSED")


def test_parse_deliverable_missing_elements():
    """Test parsing a deliverable missing some elements."""
    content = """
# Test Deliverable

## First Principles
Some axioms here.

## Purpose
Some goals here.
"""
    
    elements = parse_deliverable(content)
    
    # Only first_principles and purpose should be found
    assert len(elements['first_principles']) > 0, "first_principles should be found"
    assert len(elements['purpose']) > 0, "purpose should be found"
    
    # Other elements should be missing
    assert len(elements['ground_truth']) == 0, "ground_truth should be missing"
    assert len(elements['reproducibility']) == 0, "reproducibility should be missing"
    
    print("✓ test_parse_deliverable_missing_elements PASSED")


def test_calculate_completeness():
    """Test completeness calculation."""
    # Section with all required keywords
    full_content = """
This section includes axioms, definitions, and units.
All required elements are present.
"""
    score = calculate_completeness('first_principles', full_content)
    assert score == 1.0, f"Expected 1.0, got {score}"
    
    # Section with partial keywords
    partial_content = """
This section includes axioms only.
"""
    score = calculate_completeness('first_principles', partial_content)
    assert score < 1.0, f"Expected < 1.0, got {score}"
    assert score > 0.0, f"Expected > 0.0, got {score}"
    
    # Section with no keywords
    empty_content = """
This section has nothing relevant.
"""
    score = calculate_completeness('first_principles', empty_content)
    assert score == 0.0, f"Expected 0.0, got {score}"
    
    print("✓ test_calculate_completeness PASSED")


def test_validate_compliant_deliverable():
    """Test validation of a compliant deliverable."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""
# Compliant Test Deliverable

## First Principles
Axioms, definitions, and units are specified here.

## Ground Truth & Provenance
Sources with author, timestamp, and method.

## Reproducibility
Commands, version, seed, and environment details.

## Failure Knowledge
Failure modes, diagnostics, and mitigations.

## Constraints
Legal, ethical, and safety considerations.

## Context
Who, what, when, where, and why this matters.

## Models & Limits
Assumptions, validity range, and break points.

## Interfaces & Keys
Command-line interface, environment variables, paths.

## Calibration
Parameter values, rationale, and validation methods.

## Purpose
Goals, metrics, and success criteria.
""")
        temp_path = Path(f.name)
    
    try:
        compliance, missing, warnings = validate_charter_compliance(temp_path)
        
        # Should have no missing elements
        assert len(missing) == 0, f"Expected no missing elements, got: {missing}"
        
        # All elements should be present
        for element in CHARTER_ELEMENTS.keys():
            assert compliance[element]['present'], f"Element '{element}' not marked as present"
        
        manifest = generate_manifest(temp_path, compliance, missing, warnings)
        assert manifest['validation_result']['is_compliant'], "Should be compliant"
        
        print("✓ test_validate_compliant_deliverable PASSED")
    finally:
        temp_path.unlink()


def test_validate_non_compliant_deliverable():
    """Test validation of a non-compliant deliverable (missing elements)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""
# Non-Compliant Test Deliverable

## First Principles
Some axioms.

## Purpose
Some goals.

This deliverable is missing most charter elements.
""")
        temp_path = Path(f.name)
    
    try:
        compliance, missing, warnings = validate_charter_compliance(temp_path)
        
        # Should have missing elements
        assert len(missing) > 0, "Expected missing elements"
        
        # first_principles and purpose should be present
        assert compliance['first_principles']['present'], "first_principles should be present"
        assert compliance['purpose']['present'], "purpose should be present"
        
        # Other elements should be missing
        assert not compliance['ground_truth']['present'], "ground_truth should be missing"
        assert not compliance['reproducibility']['present'], "reproducibility should be missing"
        
        manifest = generate_manifest(temp_path, compliance, missing, warnings)
        assert not manifest['validation_result']['is_compliant'], "Should NOT be compliant"
        assert len(manifest['validation_result']['missing_elements']) > 0, "Should have missing elements"
        
        print("✓ test_validate_non_compliant_deliverable PASSED")
    finally:
        temp_path.unlink()


def test_manifest_schema():
    """Test that generated manifest conforms to expected schema."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""
# Test Deliverable

## First Principles
Axioms and definitions.

## Ground Truth & Provenance
Sources.

## Reproducibility
Commands.

## Failure Knowledge
Failures.

## Constraints
Legal.

## Context
Context.

## Models & Limits
Limits.

## Interfaces
Interfaces.

## Calibration
Calibration.

## Purpose
Purpose.
""")
        temp_path = Path(f.name)
    
    try:
        compliance, missing, warnings = validate_charter_compliance(temp_path)
        manifest = generate_manifest(
            temp_path,
            compliance,
            missing,
            warnings,
            deliverable_type="test",
            author="test_suite"
        )
        
        # Check required top-level fields
        assert 'manifest_version' in manifest
        assert manifest['manifest_version'] == '1.0.0'
        assert 'deliverable_id' in manifest
        assert 'deliverable_type' in manifest
        assert manifest['deliverable_type'] == 'test'
        assert 'timestamp' in manifest
        assert 'author' in manifest
        assert manifest['author'] == 'test_suite'
        assert 'charter_compliance' in manifest
        assert 'validation_result' in manifest
        
        # Check charter_compliance structure
        charter = manifest['charter_compliance']
        for element in CHARTER_ELEMENTS.keys():
            assert element in charter, f"Element '{element}' missing from manifest"
            assert 'present' in charter[element]
            assert 'location' in charter[element]
            assert 'completeness' in charter[element]
        
        # Check validation_result structure
        result = manifest['validation_result']
        assert 'is_compliant' in result
        assert 'missing_elements' in result
        assert 'warnings' in result
        
        print("✓ test_manifest_schema PASSED")
    finally:
        temp_path.unlink()


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("MISSION CHARTER VALIDATOR TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        test_parse_deliverable_all_elements,
        test_parse_deliverable_missing_elements,
        test_calculate_completeness,
        test_validate_compliant_deliverable,
        test_validate_non_compliant_deliverable,
        test_manifest_schema,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()
    
    if failed == 0:
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
