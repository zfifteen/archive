#!/usr/bin/env python3
"""
Run full zeta zero correlation analysis with specified parameters
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

from zeta_zero_correlation_analysis import main

if __name__ == "__main__":
    # Run with moderate parameters first (due to computational constraints)
    # M=200 zeta zeros, N=10000 primes should give us good results quickly
    print("Running zeta zero correlation analysis...")
    print("Using moderate parameters for computational efficiency...")
    
    results = main(M=200, N=10000)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)