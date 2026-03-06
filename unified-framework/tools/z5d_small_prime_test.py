#!/usr/bin/env python3
"""
Test Z5D Prime Prediction for Small Primes
==========================================

Verify if Z5D predicts small primes with 100% accuracy.
"""

import sys
import os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.z_5d_enhanced import Z5DEnhancedPredictor

def generate_primes_up_to(n):
    primes = []
    for num in range(2, n+1):
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

def test_z5d_small_primes(max_prime=100):
    z5d = Z5DEnhancedPredictor()
    primes = generate_primes_up_to(max_prime)
    print(f"Testing Z5D prediction for first {len(primes)} primes (up to {max_prime})")
    
    successes = 0
    for idx, prime in enumerate(primes, start=1):
        try:
            predicted = z5d.z_5d_prediction(idx)
            predicted_int = int(float(predicted))
            if predicted_int == prime:
                successes += 1
            else:
                print(f"Prime {idx}: {prime}, predicted: {predicted_int}")
        except Exception as e:
            print(f"Error for prime {idx}: {e}")
    
    success_rate = successes / len(primes) if primes else 0
    print(f"Success rate: {success_rate:.3f} ({successes}/{len(primes)})")
    
    return success_rate == 1.0

if __name__ == "__main__":
    is_100_percent = test_z5d_small_primes(100)
    print(f"100% success: {is_100_percent}")