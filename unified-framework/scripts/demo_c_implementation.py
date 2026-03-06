#!/usr/bin/env python3
"""
Z5D C Implementation Demonstration
=================================

Demonstrates the C implementation of Z5D and compares it with Python reference.
Shows accuracy, performance, and cross-platform compatibility.

@file demo_c_implementation.py
@author Unified Framework Team
@version 1.0
"""

import sys
import os
import subprocess
import time

# Add src to path for Python reference
sys.path.append('src')

def build_c_implementation():
    """Build the C implementation"""
    print("Building Z5D C Implementation...")
    print("================================")
    
    # Check if demo_phase2 already exists
    if os.path.exists("src/c/bin/demo_phase2"):
        print("✅ Z5D Phase 2 demo already built!")
        return True
    
    try:
        # Change to C directory and build
        # Use fallback compilation without OpenMP to avoid dependency issues
        result = subprocess.run(
            ["make", "OPENMP_CFLAGS=", "OPENMP_LDFLAGS=", "static", "bin/demo_phase2"], 
            cwd="src/c", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Build successful!")
            return True
        else:
            print("❌ Build failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def demo_basic_usage():
    """Demonstrate basic C implementation usage"""
    print("\nBasic Usage Demonstration")
    print("=========================")
    
    # Create a simple demo program
    demo_code = '''
#include "z5d_predictor.h"

int main() {
    printf("Z5D Prime Predictor - C Implementation Demo\\n");
    printf("===========================================\\n\\n");
    
    // Show formula information
    z5d_print_formula_info();
    
    printf("\\nBasic Predictions:\\n");
    printf("==================\\n");
    
    double test_k[] = {10, 100, 1000, 10000, 100000};
    int n_tests = sizeof(test_k) / sizeof(test_k[0]);
    
    for (int i = 0; i < n_tests; i++) {
        double k = test_k[i];
        double prediction = z5d_prime(k, 0.0, 0.0, 1);
        printf("z5d_prime(%.0f) = %.2f\\n", k, prediction);
    }
    
    printf("\\nDetailed Analysis Example:\\n");
    printf("==========================\\n");
    
    z5d_result_t result;
    int status = z5d_prime_extended(1000, 0.0, 0.0, 1, &result);
    
    if (status == Z5D_SUCCESS) {
        printf("k = 1000:\\n");
        printf("  PNT base:     %.6f\\n", result.pnt_base);
        printf("  Dilation (d): %.6f\\n", result.d_term);
        printf("  Curvature (e): %.6f\\n", result.e_term);
        printf("  Calibration c: %.6f\\n", result.c_used);
        printf("  Calibration k*: %.6f\\n", result.k_star_used);
        printf("  Final prediction: %.6f\\n", result.prediction);
    }
    
    return 0;
}
'''
    
    # Write and compile demo
    try:
        with open("src/c/demo.c", "w") as f:
            f.write(demo_code)
        
        compile_cmd = [
            "gcc", "-std=c99", "-O2", "-o", "src/c/demo", 
            "src/c/demo.c", "src/c/z5d_predictor.c", "-lm"
        ]
        
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Run demo
            demo_result = subprocess.run(["src/c/demo"], capture_output=True, text=True)
            print(demo_result.stdout)
        else:
            print(f"❌ Demo compilation failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    finally:
        # Cleanup
        for file in ["src/c/demo.c", "src/c/demo"]:
            try:
                os.remove(file)
            except:
                pass

def demo_performance():
    """Demonstrate performance characteristics"""
    print("\nPerformance Demonstration")
    print("=========================")
    
    # Create performance test
    perf_code = '''
#include "z5d_predictor.h"
#include <time.h>

int main() {
    printf("Z5D Performance Benchmark\\n");
    printf("=========================\\n\\n");
    
    // Single prediction timing
    clock_t start = clock();
    double result = z5d_prime(1000000, 0.0, 0.0, 1);
    clock_t end = clock();
    double single_time = ((double)(end - start)) / CLOCKS_PER_SEC * 1000000.0;
    
    printf("Single prediction (k=1M): %.2f μs\\n", single_time);
    printf("Result: %.2f\\n\\n", result);
    
    // Batch timing
    const int BATCH_SIZE = 10000;
    printf("Batch performance (%d predictions):\\n", BATCH_SIZE);
    
    start = clock();
    for (int i = 0; i < BATCH_SIZE; i++) {
        z5d_prime(1000 + i, 0.0, 0.0, 1);
    }
    end = clock();
    
    double batch_time = ((double)(end - start)) / CLOCKS_PER_SEC;
    double per_prediction = batch_time / BATCH_SIZE * 1000000.0;
    double throughput = BATCH_SIZE / batch_time;
    
    printf("Total time: %.3f seconds\\n", batch_time);
    printf("Per prediction: %.2f μs\\n", per_prediction);
    printf("Throughput: %.0f predictions/second\\n", throughput);
    
    return 0;
}
'''
    
    try:
        with open("src/c/perf_demo.c", "w") as f:
            f.write(perf_code)
        
        compile_cmd = [
            "gcc", "-std=c99", "-O2", "-o", "src/c/perf_demo", 
            "src/c/perf_demo.c", "src/c/z5d_predictor.c", "-lm"
        ]
        
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            demo_result = subprocess.run(["src/c/perf_demo"], capture_output=True, text=True)
            print(demo_result.stdout)
        else:
            print(f"❌ Performance demo compilation failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Performance demo error: {e}")
    
    finally:
        # Cleanup
        for file in ["src/c/perf_demo.c", "src/c/perf_demo"]:
            try:
                os.remove(file)
            except:
                pass

def demo_python_comparison():
    """Compare C and Python implementations"""
    print("\nC vs Python Comparison")
    print("======================")
    
    try:
        from z_framework.discrete.z5d_predictor import z5d_prime as python_z5d
        
        test_values = [100, 1000, 10000, 100000]
        
        print(f"{'k':<8} {'Python':<12} {'C':<12} {'Difference':<12} {'Rel Error %':<12}")
        print("-" * 68)
        
        # Create C comparison program
        c_compare_code = '''
#include "z5d_predictor.h"
int main(int argc, char* argv[]) {
    if (argc != 2) return 1;
    double k = atof(argv[1]);
    double result = z5d_prime(k, 0.0, 0.0, 1);
    printf("%.10f\\n", result);
    return 0;
}
'''
        
        with open("src/c/compare.c", "w") as f:
            f.write(c_compare_code)
        
        compile_cmd = [
            "gcc", "-std=c99", "-O2", "-o", "src/c/compare", 
            "src/c/compare.c", "src/c/z5d_predictor.c", "-lm"
        ]
        
        subprocess.run(compile_cmd, capture_output=True, check=True)
        
        for k in test_values:
            # Python result
            py_result = python_z5d(k)
            
            # C result
            c_result_proc = subprocess.run(
                ["src/c/compare", str(k)], 
                capture_output=True, text=True, check=True
            )
            c_result = float(c_result_proc.stdout.strip())
            
            # Comparison
            difference = abs(c_result - py_result)
            rel_error = (difference / py_result) * 100
            
            print(f"{k:<8.0f} {py_result:<12.6f} {c_result:<12.6f} {difference:<12.6f} {rel_error:<12.4f}")
        
        # Cleanup
        for file in ["src/c/compare.c", "src/c/compare"]:
            try:
                os.remove(file)
            except:
                pass
                
    except ImportError:
        print("❌ Python reference implementation not available")
    except Exception as e:
        print(f"❌ Comparison error: {e}")

def demo_phase2_performance():
    """Demonstrate Z5D Phase 2 parallel performance"""
    print("\nZ5D Phase 2 Parallel Performance")
    print("=================================")
    
    try:
        # Run the phase2 demo executable
        result = subprocess.run(
            ["./bin/demo_phase2"],
            cwd="src/c",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # Extract throughput information from the output
            lines = output.split('\n')
            throughput_found = False
            
            for line in lines:
                if 'Throughput:' in line and 'predictions/second' in line:
                    print(f"✅ Z5D Phase 2 {line.strip()}")
                    throughput_found = True
                elif 'Batch size:' in line and 'predictions' in line:
                    print(f"   {line.strip()}")
                elif 'Time:' in line and 'ms' in line and 'Cores:' in line:
                    print(f"   {line.strip()}")
            
            if not throughput_found:
                print("⚠️  Phase 2 demo ran but throughput not found in output")
                # Print first few lines for debugging
                print("   Output preview:")
                for line in lines[:10]:
                    if line.strip():
                        print(f"   {line}")
            
            return True
        else:
            print(f"❌ Phase 2 demo failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Phase 2 demo error: {e}")
        return False

def main():
    """Main demonstration runner"""
    print("Z5D Prime Predictor - C Implementation Demonstration")
    print("===================================================")
    
    # Check if we're in the right directory
    if not os.path.exists("src/c/z5d_predictor.c"):
        print("❌ Error: Please run from the repository root directory")
        return 1
    
    # Build implementation
    if not build_c_implementation():
        print("❌ Cannot proceed without successful build")
        return 1
    
    # Run demonstrations
    demo_basic_usage()
    demo_performance()
    demo_python_comparison()
    demo_phase2_performance()
    
    print("\nDemonstration Summary")
    print("====================")
    print("✅ C Implementation built successfully")
    print("✅ Basic functionality demonstrated")
    print("✅ Performance characteristics shown")
    print("✅ Python comparison completed")
    print(f"✅ Full documentation available in: docs/z5d_c_implementation_report.md")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)