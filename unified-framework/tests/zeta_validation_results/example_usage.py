#!/usr/bin/env python3
"""
Usage example for Riemann Zeta Zeros Validation

This script demonstrates how to use the ZetaZerosValidator class
for computing and analyzing Riemann zeta zeros.

Example usage:
    python3 example_usage.py
"""

import sys
import os

# Add repository root to path
repo_root = '/home/runner/work/unified-framework/unified-framework'
sys.path.append(repo_root)
os.chdir(repo_root)

# Import the validator
import importlib.util
spec = importlib.util.spec_from_file_location(
    "zeta_validation", 
    "test-finding/scripts/zeta_zeros_validation.py"
)
zeta_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zeta_module)
ZetaZerosValidator = zeta_module.ZetaZerosValidator

def quick_validation_example():
    """
    Run a quick validation with just 100 zeros for demonstration.
    """
    print("=== Quick Zeta Zeros Validation Example ===")
    print()
    
    # Create validator for 100 zeros
    validator = ZetaZerosValidator(num_zeros=100, output_dir="example_output")
    
    try:
        # Run individual steps with progress reporting
        print("Step 1: Computing zeta zeros...")
        zeros = validator.compute_zeta_zeros()
        print(f"✓ Computed {len(zeros)} zeros")
        
        print("\nStep 2: Applying unfolding transformation...")
        unfolded = validator.apply_unfolding_transformation()
        print(f"✓ Generated {len(unfolded)} unfolded zeros")
        
        print("\nStep 3: Computing spacings...")
        spacings = validator.compute_spacings()
        print(f"✓ Computed {len(spacings)} spacings")
        
        print("\nStep 4: Analyzing statistics...")
        normalized_spacings = validator.analyze_gue_statistics()
        print(f"✓ GUE relative error: {validator.results['std_relative_error']:.4f}")
        
        print("\nStep 5: Generating visualizations...")
        validator.generate_visualizations()
        print("✓ Visualization saved")
        
        print("\nStep 6: Saving results...")
        validator.save_results()
        print("✓ Results saved")
        
        print(f"\n=== Summary ===")
        print(f"Zeros computed: {validator.results['total_zeros_computed']}")
        print(f"Valid for analysis: {validator.results['valid_zeros_for_analysis']}")
        print(f"Excluded: {validator.results['excluded_zeros']}")
        print(f"Spacings analyzed: {validator.results['total_spacings']}")
        print(f"GUE relative error: {validator.results['std_relative_error']:.4f}")
        print(f"Results directory: {validator.output_dir}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def full_validation_example():
    """
    Run the complete validation pipeline.
    """
    print("=== Full Zeta Zeros Validation (1000 zeros) ===")
    print("Note: This will take ~6-7 minutes to complete")
    print()
    
    # Create validator for 1000 zeros (as in the issue)
    validator = ZetaZerosValidator(num_zeros=1000, output_dir="full_validation_output")
    
    # Run complete pipeline
    success = validator.run_full_validation()
    
    if success:
        print("\n=== Full Validation Complete ===")
        print("All results saved in: full_validation_output/")
        print("Key files:")
        print("- riemann_zeta_zeros_1000.csv: Raw computed zeros")
        print("- unfolded_zeta_zeros.csv: Transformed zeros")
        print("- spacing_statistics.csv: Nearest neighbor spacings")
        print("- validation_results.json: Numerical results")
        print("- zeta_zeros_analysis.png: Visualization")
        print("- methodology_and_results.txt: Detailed report")
        print("- SUMMARY_REPORT.md: Executive summary")
    
    return success

if __name__ == "__main__":
    # Quick example (recommended for testing)
    print("Running quick validation example...")
    success = quick_validation_example()
    
    if success:
        print("\n" + "="*50)
        print("Quick example completed successfully!")
        print("To run full 1000-zero validation, uncomment the lines below:")
        print("# full_validation_example()")
    else:
        print("Quick example failed.")
    
    # Uncomment the following line to run full validation
    # full_validation_example()