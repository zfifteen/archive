#!/usr/bin/env python3
"""
Quick test of Progressive Validation Ladder
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'applications'))

from progressive_validation_ladder import ProgressiveValidationLadder

def quick_test():
    """Run a quick test with smaller parameters."""
    print("Running Quick Progressive Validation Ladder Test")
    print("=" * 60)
    
    # Create a test ladder with reduced parameters
    ladder = ProgressiveValidationLadder(enable_high_precision=True)
    
    # Override validation levels for quick testing
    ladder.validation_levels = [
        {
            'name': 'RSA-512-Test',
            'bits': 512,
            'known_factors': None,
            'description': 'Quick test with RSA-512 equivalent',
            'trials': 5,
            'max_iterations': 100,
            'tolerance': 1e-3
        },
        {
            'name': 'RSA-768-Test',
            'bits': 768, 
            'known_factors': ladder.RSA_768_FACTORS,  # Use known factors
            'description': 'Quick test with known RSA-768 factors',
            'trials': 3,
            'max_iterations': 50,
            'tolerance': 1e-3
        }
    ]
    
    # Run the validation
    results = ladder.run_progressive_validation()
    
    # Save and print results
    output_file = ladder.save_results(results, "quick_test_results.json")
    ladder.print_summary_report(results)
    
    return results.overall_success

if __name__ == '__main__':
    success = quick_test()
    print(f"\nQuick test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)