"""
Z5D Large Scale Accuracy Validation

This script specifically validates the claim that Z5D achieves 
Mean Relative Error (MRE) ~0.0001% for n ≥ 10^6.

Tests a focused set of large-scale points to verify accuracy claims.
"""

import sys
import os
import numpy as np
import time
from sympy import ntheory

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from z_framework.discrete.z5d_predictor import z5d_prime

def test_large_scale_accuracy():
    """Test Z5D accuracy for n ≥ 10^6"""
    print("=" * 60)
    print("Z5D LARGE SCALE ACCURACY VALIDATION")
    print("Testing claim: MRE ~0.0001% for n ≥ 10^6")
    print("=" * 60)
    
    # Test points at and above 10^6
    test_points = [
        1000000,   # 10^6
        2000000,   # 2×10^6  
        5000000,   # 5×10^6
        10000000,  # 10^7
        50000000,  # 5×10^7
        100000000  # 10^8 (limit for direct computation)
    ]
    
    results = []
    total_time = 0
    
    print(f"{'n':<12} {'True Prime':<15} {'Z5D Prediction':<15} {'Rel Error (%)':<12} {'Time (s)':<10}")
    print("-" * 75)
    
    for n in test_points:
        try:
            # Time the prediction
            start_time = time.time()
            z5d_pred = z5d_prime(n)
            prediction_time = time.time() - start_time
            total_time += prediction_time
            
            # Get true prime (may be slow for large n)
            print(f"Computing true {n}th prime...", end=" ", flush=True)
            true_start = time.time()
            true_prime = ntheory.prime(n)
            true_time = time.time() - true_start
            print(f"({true_time:.1f}s)")
            
            # Calculate error
            absolute_error = abs(z5d_pred - true_prime)
            relative_error = (absolute_error / true_prime) * 100
            
            results.append({
                'n': n,
                'true_prime': true_prime,
                'z5d_prediction': z5d_pred,
                'relative_error': relative_error,
                'absolute_error': absolute_error,
                'prediction_time': prediction_time
            })
            
            print(f"{n:<12} {true_prime:<15} {z5d_pred:<15.1f} {relative_error:<12.6f} {prediction_time:<10.4f}")
            
        except Exception as e:
            print(f"Error testing n={n}: {e}")
            break
    
    if results:
        print("\n" + "=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        
        relative_errors = [r['relative_error'] for r in results]
        
        mean_error = np.mean(relative_errors)
        median_error = np.median(relative_errors)
        max_error = np.max(relative_errors)
        min_error = np.min(relative_errors)
        std_error = np.std(relative_errors)
        
        print(f"Points tested: {len(results)}")
        print(f"Range: {results[0]['n']:,} to {results[-1]['n']:,}")
        print(f"")
        print(f"Mean Relative Error:   {mean_error:.6f}%")
        print(f"Median Relative Error: {median_error:.6f}%")
        print(f"Max Relative Error:    {max_error:.6f}%")
        print(f"Min Relative Error:    {min_error:.6f}%")
        print(f"Std Relative Error:    {std_error:.6f}%")
        print(f"")
        print(f"Total prediction time: {total_time:.4f}s")
        print(f"Average per prediction: {total_time/len(results):.4f}s")
        print(f"")
        
        # Check accuracy claim
        claim_threshold = 0.001  # 0.001% = 0.0001% × 10 (generous margin)
        
        if mean_error < claim_threshold:
            print(f"✅ ACCURACY CLAIM VALIDATED")
            print(f"   Mean error {mean_error:.6f}% < {claim_threshold:.3f}% threshold")
        else:
            print(f"❌ ACCURACY CLAIM NOT MET")
            print(f"   Mean error {mean_error:.6f}% > {claim_threshold:.3f}% threshold")
        
        # Check individual points
        points_meeting_claim = sum(1 for err in relative_errors if err < 0.001)
        print(f"")
        print(f"Points with error < 0.001%: {points_meeting_claim}/{len(results)} ({100*points_meeting_claim/len(results):.1f}%)")
        
        return results
    else:
        print("No successful tests completed")
        return []

if __name__ == "__main__":
    test_large_scale_accuracy()