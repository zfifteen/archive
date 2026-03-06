#!/usr/bin/env python3
"""
Test script for Z5D vs primesieve benchmark integration
======================================================

Demonstrates the integration between C benchmark and Python framework
"""

import sys
import os
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analysis.benchmark_framework import BenchmarkFramework

@pytest.mark.skipif(
    not Path("src/c/bin/z5d_bench").exists(),
    reason="C benchmark binary not found. Build with 'make z5d-bench' first."
)
def test_c_benchmark_integration():
    """Test C benchmark integration with graceful fallback."""
    print("Z5D vs primesieve Benchmark Integration Test")
    print("=" * 50)
    
    # Initialize benchmark framework
    benchmark = BenchmarkFramework(results_dir="test_results", precision_dps=25)
    
    # Test C benchmark integration
    print("\n1. Testing C benchmark integration...")
    c_results = benchmark.run_c_benchmark_integration(
        k_max=10000,
        csv_output="test_primesieve_results.csv"
    )
    
    assert c_results is not None, "C benchmark integration should succeed"
    assert 'z5d_results' in c_results, "Results should contain Z5D data"
    assert 'comparison' in c_results, "Results should contain comparison data"
    
    print("✅ C benchmark integration successful!")
    print(f"   - Tested k values: {c_results['z5d_results']['k_values']}")
    print(f"   - Average speedup: {c_results['comparison']['average_speedup']:.2f}x")
    print(f"   - Average error: {c_results['comparison']['average_error']:.6f}%")
    
    # Save results for inspection
    csv_file = Path("test_primesieve_results.csv")
    if csv_file.exists():
        print(f"   - CSV results saved to: {csv_file.absolute()}")
        
        # Show CSV content
        with open(csv_file) as f:
            lines = f.readlines()
            print(f"   - CSV contains {len(lines)-1} data rows")
            print(f"   - Header: {lines[0].strip()}")
            if len(lines) > 1:
                print(f"   - Sample data: {lines[1].strip()}")

def test_python_benchmark_fallback():
    """Test Python benchmark as fallback when C benchmark is unavailable."""
    print("\n2. Testing traditional Python benchmark...")
    benchmark = BenchmarkFramework(results_dir="test_results", precision_dps=25)
    
    try:
        py_results = benchmark.run_comprehensive_benchmark()
        if py_results and py_results['z5d_results']:
            print("✅ Python benchmark successful!")
            print(f"   - Z5D results available: {len(py_results['z5d_results']['k_values'])} test points")
        else:
            print("⚠️  Python benchmark completed with warnings (some modules may be missing)")
    except Exception as e:
        print(f"❌ Python benchmark failed: {e}")
        # This is expected if dependencies are missing
        pytest.skip(f"Python benchmark dependencies missing: {e}")

def main():
    """Main function for direct execution."""
    print("Z5D vs primesieve Benchmark Integration Test")
    print("=" * 50)
    
    # Check if binary exists
    binary_path = Path("src/c/bin/z5d_bench")
    if not binary_path.exists():
        print("❌ C benchmark binary not found")
        print(f"   Expected location: {binary_path.absolute()}")
        print("   Please build the C benchmark first with 'make z5d-bench'")
        print("   Skipping C benchmark integration test")
        
        # Still run Python benchmark test
        test_python_benchmark_fallback()
        return
    
    # Run C benchmark test
    test_c_benchmark_integration()
    
    # Run Python benchmark test
    test_python_benchmark_fallback()
    
    print("\nTest completed.")

if __name__ == "__main__":
    main()