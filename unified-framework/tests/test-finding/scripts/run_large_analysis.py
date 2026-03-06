#!/usr/bin/env python3
"""
Run zeta zero correlation analysis with larger parameters
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

from zeta_zero_correlation_analysis import main

if __name__ == "__main__":
    print("Running zeta zero correlation analysis with larger parameters...")
    
    # Try with M=500 zeta zeros, N=50000 primes
    print("Parameters: M=500 zeta zeros, N=50000 prime limit")
    
    results = main(M=500, N=50000)
    
    print("\n" + "="*60)
    print("LARGE-SCALE ANALYSIS COMPLETE")
    print("="*60)