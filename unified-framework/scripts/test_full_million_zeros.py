#!/usr/bin/env python3
"""
Full Million Zeros Test

Test the complete 10^6 zeta zeros dataset with comprehensive validation
and performance benchmarking.
"""

import os
import sys
import time
import numpy as np

# Add src to path for imports  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_million_zeros():
    """Test the full million zeros dataset."""
    print("Testing Full Million Zeta Zeros Dataset")
    print("=" * 50)
    
    # Load the full dataset
    zeros_file = os.path.join('..', 'src', 'data', 'zeta_zeros.npy')
    print(f"Loading: {zeros_file}")
    
    start_time = time.time()
    zeros = np.load(zeros_file)
    load_time = time.time() - start_time
    
    print(f"✓ Loaded {len(zeros):,} zeros in {load_time:.3f}s")
    print(f"  File size: {os.path.getsize(zeros_file):,} bytes")
    print(f"  Memory usage: {zeros.nbytes:,} bytes")
    print(f"  Data type: {zeros.dtype}")
    
    # Quick validation
    print("\nValidation:")
    print(f"  Real parts range: {np.min(zeros.real):.10f} to {np.max(zeros.real):.10f}")
    print(f"  Imaginary parts range: {np.min(zeros.imag):.3f} to {np.max(zeros.imag):.3f}")
    print(f"  Monotonic ordering: {np.all(np.diff(zeros.imag) > 0)}")
    
    # Performance test - vectorized operations
    print("\nVectorized Operations Performance:")
    
    # Test 1: Spacing computation
    start_time = time.time()
    spacings = np.diff(zeros.imag)
    spacing_time = time.time() - start_time
    print(f"  Spacing computation: {spacing_time:.3f}s ({len(zeros)/spacing_time:,.0f} zeros/s)")
    
    # Test 2: Statistical analysis
    start_time = time.time()
    mean_spacing = np.mean(spacings)
    std_spacing = np.std(spacings)
    stats_time = time.time() - start_time
    print(f"  Statistical analysis: {stats_time:.3f}s")
    print(f"    Mean spacing: {mean_spacing:.6f}")
    print(f"    Std spacing: {std_spacing:.6f}")
    
    # Test 3: FFT computation
    start_time = time.time()
    fft_result = np.fft.fft(zeros.imag[:100000])  # Sample for memory efficiency
    fft_time = time.time() - start_time
    print(f"  FFT computation (100k sample): {fft_time:.3f}s")
    
    # Test 4: Weyl formula validation (sample)
    print("\nWeyl Formula Validation (sample):")
    sample_size = 10000
    sample_zeros = zeros[:sample_size]
    
    start_time = time.time()
    T_max = np.max(sample_zeros.imag)
    actual_count = len(sample_zeros)
    predicted_count = T_max / (2 * np.pi) * np.log(T_max / (2 * np.pi * np.e))
    relative_error = abs(actual_count - predicted_count) / predicted_count
    weyl_time = time.time() - start_time
    
    print(f"  Sample size: {sample_size:,}")
    print(f"  Actual count: {actual_count:,}")
    print(f"  Predicted count: {predicted_count:.0f}")
    print(f"  Relative error: {relative_error:.6f}")
    print(f"  Computation time: {weyl_time:.3f}s")
    
    # Overall performance summary
    total_operations_time = spacing_time + stats_time + fft_time + weyl_time
    overall_throughput = len(zeros) / total_operations_time
    
    print(f"\nOverall Performance:")
    print(f"  Total operations time: {total_operations_time:.3f}s")
    print(f"  Overall throughput: {overall_throughput:,.0f} zeros/s")
    print(f"  Memory efficiency: {zeros.nbytes / (1024**2):.1f} MB for {len(zeros):,} zeros")
    
    # Data quality assessment
    print("\nData Quality Assessment:")
    
    # Check for any anomalies
    real_variance = np.var(zeros.real)
    large_gaps = np.sum(spacings > 3 * std_spacing)
    
    print(f"  Real part variance: {real_variance:.2e} (should be ~0)")
    print(f"  Large gaps (>3σ): {large_gaps} ({100*large_gaps/len(spacings):.2f}%)")
    print(f"  Min spacing: {np.min(spacings):.6f}")
    print(f"  Max spacing: {np.max(spacings):.6f}")
    
    # Success criteria
    success = (
        len(zeros) >= 900000 and  # At least 900k zeros
        np.all(np.diff(zeros.imag) > 0) and  # Monotonic ordering
        real_variance < 1e-20 and  # All real parts should be 0.5
        relative_error < 0.1 and  # Weyl formula accuracy
        overall_throughput > 10000  # Performance threshold
    )
    
    print(f"\n{'='*50}")
    if success:
        print("✅ ALL TESTS PASSED - Dataset ready for production use")
        print(f"   {len(zeros):,} high-quality zeta zeros available")
        print(f"   Vectorized operations: {overall_throughput:,.0f} zeros/s")
        print(f"   Memory footprint: {zeros.nbytes/(1024**2):.1f} MB")
    else:
        print("❌ SOME TESTS FAILED - Review dataset quality")
    
    print("="*50)
    return success

def main():
    """Main test execution."""
    try:
        success = test_million_zeros()
        return success
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)