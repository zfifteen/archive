#!/usr/bin/env python3
"""
Small-scale test for spectral form factor computation
====================================================

This script tests the spectral form factor functionality with smaller parameters
to validate the implementation before running full-scale analysis.
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework/src')
sys.path.append('/home/runner/work/unified-framework/unified-framework/tests/test-finding/scripts')

from spectral_form_factor_analysis import SpectralFormFactorAnalysis
import matplotlib
matplotlib.use('Agg')  # Headless mode

def test_small_scale():
    """
    Test with small parameters to validate functionality
    """
    print("Testing small-scale spectral form factor analysis...")
    
    # Small parameters for quick testing
    analysis = SpectralFormFactorAnalysis(
        M=50,         # Just 50 zeta zeros
        N=1000,       # Small sequence length
        tau_max=5.0,  # Smaller τ range
        tau_steps=20  # Fewer steps
    )
    
    try:
        # Run the analysis
        results = analysis.run_complete_analysis(
            save_results=True,
            plot_results=True
        )
        
        print(f"✅ Small-scale test completed successfully!")
        print(f"   Runtime: {results['runtime']:.2f} seconds")
        print(f"   Zeta zeros: {len(analysis.zeta_zeros)}")
        print(f"   Spectral points: {len(analysis.spectral_form_factor)}")
        print(f"   CRISPR scores: {len(analysis.crispr_scores)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_small_scale()
    if success:
        print("Small-scale test passed - ready for full implementation")
    else:
        print("Small-scale test failed - need to fix issues")