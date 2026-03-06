#!/usr/bin/env python3
"""
SHAs Matching Requirements Verification

This script demonstrates that the implementation meets all requirements from
the problem statement regarding "SHAs matching" and Z_5D error validation.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports using pathlib and check existence
src_path = Path(__file__).parent / 'src'
if not src_path.exists():
    print(f"Error: src directory not found at {src_path}")
    sys.exit(1)
sys.path.insert(0, str(src_path))

from tests.test_z5d_zeta_validation import Z5DZetaValidator
from tests.test_sha_matching_validation import SHAMatchingValidator


def verify_requirements():
    """
    Verify that all requirements from the problem statement are met.
    """
    print("="*60)
    print("VERIFICATION: SHAs MATCHING REQUIREMENTS")
    print("="*60)
    
    print("\n1. TESTING Z_5D ERROR <0.01% FOR k≥10^5...")
    sha_validator = SHAMatchingValidator()
    z5d_results = sha_validator.validate_z5d_error_threshold()
    
    summary = z5d_results['summary']
    print(f"   Pass rate: {summary['pass_rate']*100:.1f}% ({summary['passing_count']}/{summary['total_count']})")
    print(f"   Requirement met: {'✓' if summary['requirement_met'] else '✗'}")
    
    print("\n2. TESTING SHA MATCHING VALIDATION...")
    sha_consistency = sha_validator.validate_sha_matching_consistency()
    print(f"   SHA matching validated: {'✓' if sha_consistency['sha_matching_validated'] else '✗'}")
    print(f"   Overall consistency: {sha_consistency['overall_consistency']:.4f}")
    
    print("\n3. TESTING METRICS LOCKING...")
    metrics_locking = sha_validator.validate_metrics_locking()
    print(f"   Metrics locked: {'✓' if metrics_locking['metrics_locked'] else '✗'}")
    print(f"   SHA matching score: {metrics_locking['sha_matching_score']:.4f}")
    
    print("\n4. TESTING INTEGRATED Z5D-ZETA-SHA VALIDATION...")
    z5d_validator = Z5DZetaValidator(target_k=1000000, num_zeros=50)
    integrated_results = z5d_validator.run_complete_validation()
    
    # Check key validation components
    z5d_prediction = integrated_results.get('z5d_prediction', {})
    sha_validation = integrated_results.get('sha_matching_validation', {})
    
    print(f"   Z5D prediction: {float(z5d_prediction.get('z5d_prediction', 0)):,.2f}")
    print(f"   SHA validation: {'✓' if 'error' not in sha_validation else '✗'}")
    print(f"   Metrics locked: {'✓' if sha_validation.get('metrics_locked', False) else '✗'}")
    
    print("\n" + "="*60)
    print("REQUIREMENTS VERIFICATION SUMMARY")
    print("="*60)
    
    requirements_met = [
        summary['requirement_met'],
        sha_consistency['sha_matching_validated'],
        metrics_locking['metrics_locked'],
        'error' not in sha_validation
    ]
    
    req_names = [
        "Z_5D error <0.01% for k≥10^5",
        "SHA matching consistency",
        "Metrics locking functionality", 
        "Integrated validation"
    ]
    
    for req_name, met in zip(req_names, requirements_met):
        print(f"   {req_name}: {'✓' if met else '✗'}")
    
    overall_success = all(requirements_met)
    print(f"\n   OVERALL SUCCESS: {'✓' if overall_success else '✗'}")
    
    if overall_success:
        print("\n✓ ALL REQUIREMENTS FROM PROBLEM STATEMENT ARE MET!")
        print("  - SHAs matching functionality implemented")
        print("  - Z Framework metrics locked when criteria met")
        print("  - Z_5D error validated to be <0.01% for k≥10^5")
        print("  - Cryptographic hash analysis integrated with Z Framework")
    else:
        print("\n⚠ SOME REQUIREMENTS NOT FULLY MET")
        
    print("="*60)
    
    return overall_success


if __name__ == "__main__":
    verify_requirements()