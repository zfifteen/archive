#!/usr/bin/env python3
"""
Main Test Runner for Scale-Invariant Geometric Resonance Experiment
Executes all tests and generates comprehensive report
"""

import sys
import json
import time
from datetime import datetime

from validate_z5d_hypothesis import comprehensive_validation
from adversarial_test_adaptive import test_rsa_challenges, test_unbalanced_semiprimes


def run_all_tests():
    """
    Execute complete test suite for the hypothesis.
    
    Returns:
        Complete results dictionary
    """
    print("=" * 70)
    print("SCALE-INVARIANT GEOMETRIC RESONANCE EXPERIMENT")
    print("Testing Hypothesis: Emergent scale-invariance in geometric resonance")
    print("=" * 70)
    print()
    
    start_time = time.time()
    
    results = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'hypothesis': 'Scale-Invariant Geometric Resonance in Extreme-Scale Semiprime Analysis',
        },
        'tests': {}
    }
    
    # Test Suite 1: Core Hypothesis Validation
    print("\n" + "=" * 70)
    print("TEST SUITE 1: Core Hypothesis Validation")
    print("=" * 70)
    
    try:
        validation_results = comprehensive_validation()
        results['tests']['hypothesis_validation'] = validation_results
    except Exception as e:
        print(f"Error in hypothesis validation: {e}")
        results['tests']['hypothesis_validation'] = {'error': str(e)}
    
    # Test Suite 2: RSA Challenge Tests
    print("\n" + "=" * 70)
    print("TEST SUITE 2: RSA Challenge Tests")
    print("=" * 70)
    
    try:
        rsa_results = test_rsa_challenges()
        results['tests']['rsa_challenges'] = {
            'count': len(rsa_results),
            'factors_found': sum(1 for r in rsa_results if r.get('factors_found')),
            'results': rsa_results
        }
    except Exception as e:
        print(f"Error in RSA challenge tests: {e}")
        results['tests']['rsa_challenges'] = {'error': str(e)}
    
    # Test Suite 3: Unbalanced Semiprimes
    print("\n" + "=" * 70)
    print("TEST SUITE 3: Unbalanced Semiprime Analysis")
    print("=" * 70)
    
    try:
        unbalanced_results = test_unbalanced_semiprimes()
        results['tests']['unbalanced_semiprimes'] = unbalanced_results
    except Exception as e:
        print(f"Error in unbalanced semiprime tests: {e}")
        results['tests']['unbalanced_semiprimes'] = {'error': str(e)}
    
    elapsed_time = time.time() - start_time
    results['metadata']['elapsed_time_seconds'] = elapsed_time
    
    # Summary
    print("\n" + "=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")
    
    # Determine overall conclusion
    hypothesis_validated = results['tests'].get('hypothesis_validation', {}).get('all_tests_passed', False)
    
    print(f"\nHypothesis Status: {'✓ VALIDATED' if hypothesis_validated else '✗ NOT VALIDATED'}")
    
    results['conclusion'] = {
        'hypothesis_validated': hypothesis_validated,
        'timestamp': datetime.now().isoformat()
    }
    
    return results


def save_results(results, filename='results/experiment_results.json'):
    """Save results to JSON file."""
    import os
    os.makedirs('results', exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✓ Results saved to {filename}")


if __name__ == "__main__":
    results = run_all_tests()
    save_results(results)
    
    # Exit with appropriate code
    hypothesis_validated = results.get('conclusion', {}).get('hypothesis_validated', False)
    sys.exit(0 if hypothesis_validated else 1)
