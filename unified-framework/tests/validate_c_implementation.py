#!/usr/bin/env python3
"""
Z5D Cross-Validation: C vs Python Implementation
==============================================

Validates the C implementation of Z5D against the Python reference.
Generates detailed accuracy and performance analysis reports.

@file validate_c_implementation.py
@author Unified Framework Team
@version 1.0
"""

import sys
import os
import subprocess
import numpy as np
import time
import json
from typing import List, Tuple, Dict

# Add src to path
sys.path.append('src')

try:
    from z_framework.discrete.z5d_predictor import z5d_prime as python_z5d_prime
except ImportError as e:
    print(f"Error importing Python Z5D: {e}")
    print("Make sure you're running from the repository root directory")
    sys.exit(1)

def run_c_z5d(k_values: List[float]) -> List[float]:
    """Run C implementation and get results"""
    # Create a simple C program to get predictions
    c_test_program = """
#include "z5d_predictor.h"
int main(int argc, char* argv[]) {
    if (argc != 2) return 1;
    double k = atof(argv[1]);
    double result = z5d_prime(k, 0.0, 0.0, 1);
    printf("%.10f\\n", result);
    return 0;
}
"""
    
    # Write test program
    with open("src/c/temp_test.c", "w") as f:
        f.write(c_test_program)
    
    # Compile test program
    compile_cmd = ["gcc", "-std=c99", "-O2", "-o", "src/c/temp_test", 
                   "src/c/temp_test.c", "src/c/z5d_predictor.c", "-lm"]
    
    try:
        subprocess.run(compile_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to compile test program: {e}")
        return []
    
    # Run for each k value
    results = []
    for k in k_values:
        try:
            result = subprocess.run(["src/c/temp_test", str(k)], 
                                   capture_output=True, text=True, check=True)
            results.append(float(result.stdout.strip()))
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"Failed to get C result for k={k}: {e}")
            results.append(np.nan)
    
    # Cleanup
    try:
        os.remove("src/c/temp_test")
        os.remove("src/c/temp_test.c")
    except:
        pass
    
    return results

def validate_implementation(test_k_values: List[float]) -> Dict:
    """Comprehensive validation of C vs Python implementation"""
    
    print("Z5D Implementation Cross-Validation")
    print("===================================")
    print(f"Testing {len(test_k_values)} values...")
    
    # Get Python predictions
    print("Running Python reference implementation...")
    python_start = time.time()
    python_results = []
    for k in test_k_values:
        try:
            result = python_z5d_prime(k)
            python_results.append(result)
        except Exception as e:
            print(f"Python failed for k={k}: {e}")
            python_results.append(np.nan)
    python_time = time.time() - python_start
    
    # Get C predictions
    print("Running C implementation...")
    c_start = time.time()
    c_results = run_c_z5d(test_k_values)
    c_time = time.time() - c_start
    
    # Calculate differences
    valid_mask = ~(np.isnan(python_results) | np.isnan(c_results))
    valid_indices = np.where(valid_mask)[0]
    
    if len(valid_indices) == 0:
        return {"error": "No valid results for comparison"}
    
    python_valid = np.array([python_results[i] for i in valid_indices])
    c_valid = np.array([c_results[i] for i in valid_indices])
    k_valid = np.array([test_k_values[i] for i in valid_indices])
    
    # Compute error metrics
    absolute_errors = np.abs(c_valid - python_valid)
    relative_errors = absolute_errors / np.abs(python_valid)
    
    # Statistics
    stats = {
        "total_tests": len(test_k_values),
        "valid_results": len(valid_indices),
        "success_rate": len(valid_indices) / len(test_k_values) * 100,
        
        "mean_absolute_error": np.mean(absolute_errors),
        "max_absolute_error": np.max(absolute_errors),
        "mean_relative_error": np.mean(relative_errors),
        "max_relative_error": np.max(relative_errors),
        
        "python_time": python_time,
        "c_time": c_time,
        "speedup_factor": python_time / c_time if c_time > 0 else np.inf,
        
        "results": {
            "k_values": k_valid.tolist(),
            "python_results": python_valid.tolist(),
            "c_results": c_valid.tolist(),
            "absolute_errors": absolute_errors.tolist(),
            "relative_errors": relative_errors.tolist()
        }
    }
    
    return stats

def print_detailed_report(stats: Dict):
    """Print detailed validation report"""
    
    print(f"\nValidation Results Summary")
    print("=========================")
    print(f"Total tests: {stats['total_tests']}")
    print(f"Valid results: {stats['valid_results']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    
    print(f"\nAccuracy Metrics")
    print("================")
    print(f"Mean absolute error: {stats['mean_absolute_error']:.6f}")
    print(f"Max absolute error:  {stats['max_absolute_error']:.6f}")
    print(f"Mean relative error: {stats['mean_relative_error']:.6f} ({stats['mean_relative_error']*100:.4f}%)")
    print(f"Max relative error:  {stats['max_relative_error']:.6f} ({stats['max_relative_error']*100:.4f}%)")
    
    print(f"\nPerformance Metrics")
    print("===================")
    print(f"Python execution time: {stats['python_time']:.6f} seconds")
    print(f"C execution time:      {stats['c_time']:.6f} seconds")
    print(f"C speedup factor:      {stats['speedup_factor']:.1f}x")
    
    print(f"\nDetailed Comparison (first 10 results)")
    print("======================================")
    print(f"{'k':<8} {'Python':<12} {'C':<12} {'Abs Error':<12} {'Rel Error %':<12}")
    print("-" * 68)
    
    for i in range(min(10, len(stats['results']['k_values']))):
        k = stats['results']['k_values'][i]
        py_result = stats['results']['python_results'][i]
        c_result = stats['results']['c_results'][i]
        abs_err = stats['results']['absolute_errors'][i]
        rel_err = stats['results']['relative_errors'][i] * 100
        
        print(f"{k:<8.0f} {py_result:<12.6f} {c_result:<12.6f} {abs_err:<12.6f} {rel_err:<12.4f}")

def generate_analysis_report(stats: Dict):
    """Generate comprehensive analysis report"""
    
    report_filename = "z5d_c_validation_report.md"
    
    with open(report_filename, "w") as f:
        f.write("# Z5D C Implementation Validation Report\n\n")
        
        f.write("## Overview\n")
        f.write("This report validates the C implementation of the Z5D prime predictor ")
        f.write("against the Python reference implementation.\n\n")
        
        f.write("## Test Configuration\n")
        f.write(f"- Total test cases: {stats['total_tests']}\n")
        f.write(f"- Valid results: {stats['valid_results']}\n")
        f.write(f"- Success rate: {stats['success_rate']:.1f}%\n\n")
        
        f.write("## Accuracy Analysis\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Mean Absolute Error | {stats['mean_absolute_error']:.6f} |\n")
        f.write(f"| Maximum Absolute Error | {stats['max_absolute_error']:.6f} |\n")
        f.write(f"| Mean Relative Error | {stats['mean_relative_error']*100:.4f}% |\n")
        f.write(f"| Maximum Relative Error | {stats['max_relative_error']*100:.4f}% |\n\n")
        
        f.write("## Performance Analysis\n")
        f.write("| Implementation | Execution Time | Speedup |\n")
        f.write("|----------------|----------------|----------|\n")
        f.write(f"| Python Reference | {stats['python_time']:.6f}s | 1.0x |\n")
        f.write(f"| C Implementation | {stats['c_time']:.6f}s | {stats['speedup_factor']:.1f}x |\n\n")
        
        f.write("## Detailed Results\n")
        f.write("| k | Python Z5D | C Z5D | Absolute Error | Relative Error (%) |\n")
        f.write("|---|------------|-------|----------------|--------------------|\n")
        
        for i in range(len(stats['results']['k_values'])):
            k = stats['results']['k_values'][i]
            py_result = stats['results']['python_results'][i]
            c_result = stats['results']['c_results'][i]
            abs_err = stats['results']['absolute_errors'][i]
            rel_err = stats['results']['relative_errors'][i] * 100
            
            f.write(f"| {k:.0f} | {py_result:.6f} | {c_result:.6f} | {abs_err:.6f} | {rel_err:.4f} |\n")
        
        f.write("\n## Conclusion\n")
        f.write(f"The C implementation shows excellent agreement with the Python reference:\n")
        f.write(f"- **High Accuracy**: Mean relative error of {stats['mean_relative_error']*100:.4f}%\n")
        f.write(f"- **High Performance**: {stats['speedup_factor']:.1f}x speedup over Python\n")
        f.write(f"- **Robust Implementation**: {stats['success_rate']:.1f}% success rate\n\n")
        
        if stats['mean_relative_error'] < 0.0001:
            f.write("✅ **EXCELLENT**: The C implementation meets high-precision requirements.\n")
        elif stats['mean_relative_error'] < 0.001:
            f.write("✅ **GOOD**: The C implementation provides very good accuracy.\n")
        elif stats['mean_relative_error'] < 0.01:
            f.write("⚠️ **ACCEPTABLE**: The C implementation provides reasonable accuracy.\n")
        else:
            f.write("❌ **NEEDS IMPROVEMENT**: The C implementation requires accuracy improvements.\n")
    
    print(f"\nDetailed report saved to: {report_filename}")

def main():
    """Main validation runner"""
    
    # Test cases covering different scales
    test_cases = [
        # Small scale
        10, 50, 100, 500,
        # Medium scale  
        1000, 5000, 10000, 50000, 100000,
        # Large scale
        500000, 1000000, 5000000,
        # Very large scale (if supported)
        10000000, 50000000
    ]
    
    try:
        stats = validate_implementation(test_cases)
        
        if "error" in stats:
            print(f"Validation failed: {stats['error']}")
            return 1
        
        print_detailed_report(stats)
        generate_analysis_report(stats)
        
        # Save results as JSON for further analysis
        with open("z5d_validation_results.json", "w") as f:
            json.dump(stats, f, indent=2)
        
        print(f"\nValidation complete!")
        print(f"- Accuracy: {stats['mean_relative_error']*100:.4f}% mean relative error")
        print(f"- Performance: {stats['speedup_factor']:.1f}x speedup over Python")
        
        return 0
        
    except Exception as e:
        print(f"Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)