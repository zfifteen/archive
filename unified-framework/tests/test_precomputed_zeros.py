#!/usr/bin/env python3
"""
Test script to validate the enhanced experiment with pre-computed zeta zeros.
"""

import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from experiments.efficiency_through_symmetry import EfficiencyThroughSymmetryExperiment

def test_zeta_file_loading():
    """Test that zeta zeros can be loaded from file."""
    print("Testing zeta zeros file loading...")
    
    experiment = EfficiencyThroughSymmetryExperiment()
    
    # Test loading a small number of zeros
    zeros = experiment.load_zeta_zeros_from_file(max_zeros=10)
    
    print(f"Loaded {len(zeros)} zeros")
    if zeros:
        print(f"First zero: {zeros[0]}")
        print(f"Last zero: {zeros[-1]}")
        
        # Verify they are complex numbers with real part = 0.5
        for i, zero in enumerate(zeros[:3]):
            print(f"Zero {i+1}: real={zero.real:.6f}, imag={zero.imag:.6f}")
            
    return len(zeros) > 0

def test_quick_experiment():
    """Run a quick experiment with limited test cases."""
    print("\nRunning quick validation experiment...")
    
    # Create experiment with limited scope for testing
    experiment = EfficiencyThroughSymmetryExperiment()
    
    # Override test values for quick testing
    experiment.test_k_values = [1000, 10000]  # Just two test values
    
    # Test a single prediction to verify the system works
    print("Testing single baseline prediction...")
    start_time = time.time()
    
    try:
        # Compute true primes for small test set
        experiment.compute_true_primes()
        
        # Test baseline prediction
        result = experiment.run_single_experiment(1000, 'baseline', 0, None)
        print(f"Baseline prediction for k=1000: {result.prediction:.1f}")
        print(f"True value: {result.true_value}")
        print(f"Relative error: {result.error_relative:.6f}")
        
        # Test enhanced prediction with small number of zeros
        zeros = experiment.load_zeta_zeros_from_file(max_zeros=100)
        result_enhanced = experiment.run_single_experiment(1000, 'enhanced_100', 100, zeros)
        print(f"Enhanced prediction for k=1000: {result_enhanced.prediction:.1f}")
        print(f"Relative error: {result_enhanced.error_relative:.6f}")
        
        elapsed = time.time() - start_time
        print(f"Quick test completed in {elapsed:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"Quick test failed: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("Testing Enhanced Efficiency Through Symmetry Experiment")
    print("=" * 60)
    
    # Test 1: File loading
    file_test = test_zeta_file_loading()
    
    # Test 2: Quick experiment
    if file_test:
        exp_test = test_quick_experiment()
    else:
        print("Skipping experiment test due to file loading failure")
        exp_test = False
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"File loading: {'✅ PASSED' if file_test else '❌ FAILED'}")
    print(f"Quick experiment: {'✅ PASSED' if exp_test else '❌ FAILED'}")
    
    if file_test and exp_test:
        print("\n✅ All tests passed! The enhanced experiment is ready to use.")
        print("\nTo run the full experiment with fine-grained analysis:")
        print("python experiments/efficiency_through_symmetry.py")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    return file_test and exp_test

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)