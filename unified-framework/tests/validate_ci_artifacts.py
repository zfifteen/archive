#!/usr/bin/env python3
"""
CI Artifact Validation Script for Spinor Geodesic Framework

This script validates test artifacts against defined thresholds for CI regression testing.
It can be used to fail CI jobs if performance metrics drop below acceptable levels.

Usage:
    python validate_ci_artifacts.py [artifact_path]
    
Exit codes:
    0: All thresholds passed
    1: One or more thresholds failed
    2: Artifact file not found or invalid
"""

import sys
import json
import os
from typing import Dict, Any

# Define performance thresholds for CI validation
CI_THRESHOLDS = {
    'min_fidelity': 0.95,           # F > 0.95 target
    'max_variance': 1e-4,           # σ < 10^-4 target  
    'min_improvement': 20.0,        # 20% improvement claim
    'min_pass_rate': 0.95,          # 95% pass rate for F > 0.95
    'max_mean_improvement': 50.0,   # Sanity check: not too high
    'min_test_count': 100          # Minimum tests for statistical validity
}

def load_artifact(filepath: str) -> Dict[str, Any]:
    """Load test artifact from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ Artifact file not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in artifact file: {e}")
        return None

def validate_improvement_artifact(artifact_data: Dict[str, Any]) -> Dict[str, bool]:
    """Validate improvement demonstration artifact."""
    results = artifact_data.get('results', {})
    validation = {}
    
    # Check maximum improvement claim
    max_improvement = results.get('max_improvement_percent', 0)
    validation['improvement_claim'] = max_improvement >= CI_THRESHOLDS['min_improvement']
    
    # Check mean improvement is reasonable
    mean_improvement = results.get('mean_improvement_percent', 0)
    validation['reasonable_improvement'] = (
        0 <= mean_improvement <= CI_THRESHOLDS['max_mean_improvement']
    )
    
    # Check all tests pass F > 0.95
    pass_rate = results.get('fraction_above_95_percent', 0)
    validation['pass_rate'] = pass_rate >= CI_THRESHOLDS['min_pass_rate']
    
    # Check test count
    test_count = results.get('total_tests', 0)
    validation['sufficient_tests'] = test_count >= 6  # Known configuration count
    
    return validation

def validate_framework_artifact(artifact_data: Dict[str, Any]) -> Dict[str, bool]:
    """Validate framework validation artifact."""
    results = artifact_data.get('results', {})
    stats = results.get('statistical_results', {})
    config = results.get('test_configuration', {})
    validation = {}
    
    # Check fidelity threshold
    mean_fidelity = stats.get('mean_fidelity', 0)
    validation['fidelity_threshold'] = mean_fidelity >= CI_THRESHOLDS['min_fidelity']
    
    # Check variance threshold
    std_fidelity = stats.get('std_fidelity', float('inf'))
    validation['variance_threshold'] = std_fidelity < CI_THRESHOLDS['max_variance']
    
    # Check pass rate
    pass_rate = stats.get('pass_rate_f095', 0)
    validation['pass_rate_threshold'] = pass_rate >= CI_THRESHOLDS['min_pass_rate']
    
    # Check test count
    total_tests = config.get('total_tests', 0)
    validation['test_count_threshold'] = total_tests >= CI_THRESHOLDS['min_test_count']
    
    return validation

def print_validation_results(validation: Dict[str, bool], artifact_type: str):
    """Print validation results in a CI-friendly format."""
    passed = sum(validation.values())
    total = len(validation)
    
    print(f"\n📊 {artifact_type.upper()} VALIDATION RESULTS:")
    for check, result in validation.items():
        status = '✅' if result else '❌'
        print(f"   {check}: {status}")
    
    print(f"\n🏆 SUMMARY: {passed}/{total} checks passed")
    
    if passed == total:
        print(f"   STATUS: ✅ ALL THRESHOLDS MET")
        return True
    else:
        print(f"   STATUS: ❌ {total - passed} THRESHOLD(S) FAILED")
        return False

def main():
    """Main validation function."""
    print("=" * 60)
    print("CI Artifact Validation for Spinor Geodesic Framework")
    print("=" * 60)
    
    # Determine artifact paths
    if len(sys.argv) > 1:
        # Use provided path
        artifact_paths = [sys.argv[1]]
    else:
        # Auto-discover artifacts in standard location
        artifacts_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
        if not os.path.exists(artifacts_dir):
            print(f"❌ Artifacts directory not found: {artifacts_dir}")
            print("   Run tests to generate artifacts first")
            return 2
        
        artifact_paths = []
        for filename in os.listdir(artifacts_dir):
            if filename.endswith('.json'):
                artifact_paths.append(os.path.join(artifacts_dir, filename))
    
    if not artifact_paths:
        print("❌ No artifact files found")
        return 2
    
    overall_success = True
    
    for artifact_path in artifact_paths:
        print(f"\n🔍 Validating: {os.path.basename(artifact_path)}")
        
        # Load artifact
        artifact_data = load_artifact(artifact_path)
        if artifact_data is None:
            overall_success = False
            continue
        
        # Determine artifact type and validate accordingly
        results = artifact_data.get('results', {})
        
        if 'max_improvement_percent' in results:
            # Improvement demonstration artifact
            validation = validate_improvement_artifact(artifact_data)
            success = print_validation_results(validation, "improvement demonstration")
        elif 'statistical_results' in results:
            # Framework validation artifact
            validation = validate_framework_artifact(artifact_data)
            success = print_validation_results(validation, "framework validation")
        else:
            print(f"⚠️  Unknown artifact type, skipping validation")
            continue
        
        if not success:
            overall_success = False
    
    print("\n" + "=" * 60)
    if overall_success:
        print("✅ ALL ARTIFACTS PASSED VALIDATION")
        print("   Framework performance meets CI thresholds")
        return 0
    else:
        print("❌ ARTIFACT VALIDATION FAILED")
        print("   Framework performance below CI thresholds")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)