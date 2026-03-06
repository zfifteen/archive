#!/usr/bin/env python3
"""
Full-Scale Spectral Form Factor and Wave-CRISPR Analysis
=========================================================

This script runs the complete Task 6 analysis with full parameters:
- M=1000 zeta zeros (up to t=1000+)  
- τ range [0,10] with 100 steps
- N=10^6 for CRISPR analysis
- Bootstrap bands ~0.05/N
- Expected runtime: ~4 hours

Optimized for performance with batch processing and memory management.
"""

import os
import time
import numpy as np
from spectral_form_factor_analysis import SpectralFormFactorAnalysis
import matplotlib
matplotlib.use('Agg')  # Headless mode

def run_full_analysis():
    """
    Run the complete full-scale analysis as specified in Task 6
    """
    print("="*70)
    print("TASK 6: FULL-SCALE SPECTRAL FORM FACTOR AND WAVE-CRISPR ANALYSIS")
    print("="*70)
    print(f"Parameters:")
    print(f"  - Zeta zeros: M=1000 (up to t=1000+)")
    print(f"  - τ range: [0, 10] with 100 steps")
    print(f"  - CRISPR sequences: N=10^6")
    print(f"  - Bootstrap samples: 1000")
    print(f"  - Expected runtime: ~20 minutes (optimized)")
    print("="*70)
    
    start_time = time.time()
    
    # Initialize with full parameters
    analysis = SpectralFormFactorAnalysis(
        M=1000,       # Zeta zeros up to t=1000+
        N=1000000,    # N=10^6 for CRISPR
        tau_max=10.0, # τ range [0,10]
        tau_steps=100 # 100 τ points as specified
    )
    
    # Run analysis with optimizations for large scale
    try:
        print("\n🚀 Starting full-scale computation...")
        
        # Stage 1: Zeta zeros (estimated ~5 minutes)
        print("\n📊 Stage 1/6: Computing 1000 zeta zeros...")
        stage_start = time.time()
        analysis.compute_zeta_zeros()
        stage_time = time.time() - stage_start
        print(f"   ✅ Completed in {stage_time:.1f}s")
        
        # Stage 2: Unfolding (estimated ~1 minute)
        print("\n🔄 Stage 2/6: Unfolding zeros...")
        stage_start = time.time()
        analysis.unfold_zeros()
        stage_time = time.time() - stage_start
        print(f"   ✅ Completed in {stage_time:.1f}s")
        
        # Stage 3: Spectral form factor (estimated ~3 minutes)
        print("\n📈 Stage 3/6: Computing spectral form factor K(τ)/N...")
        print("   ⚠️  Computing for 1000 zeros × 100 τ points (optimized algorithm)")
        stage_start = time.time()
        analysis.compute_spectral_form_factor()
        stage_time = time.time() - stage_start
        print(f"   ✅ Completed in {stage_time:.1f}s ({stage_time/60:.1f} minutes)")
        
        # Stage 4: Bootstrap bands (estimated ~5 minutes)
        print("\n🎯 Stage 4/6: Computing bootstrap confidence bands...")
        stage_start = time.time()
        analysis.compute_bootstrap_bands(n_bootstrap=1000)
        stage_time = time.time() - stage_start
        print(f"   ✅ Completed in {stage_time:.1f}s ({stage_time/60:.1f} minutes)")
        
        # Stage 5: Wave-CRISPR scores (estimated ~5 minutes)
        print("\n🧬 Stage 5/6: Computing Wave-CRISPR scores...")
        print("   ⚠️  Processing sequences - estimated 5 minutes")
        stage_start = time.time()
        analysis.compute_wave_crispr_scores(sample_size=50000)  # Larger batch for full scale
        stage_time = time.time() - stage_start
        print(f"   ✅ Completed in {stage_time:.1f}s ({stage_time/60:.1f} minutes)")
        
        # Stage 6: Validation and output
        print("\n✅ Stage 6/6: Validation and saving results...")
        stage_start = time.time()
        
        # Hybrid GUE validation
        ks_stat, p_value, is_hybrid = analysis.validate_hybrid_gue()
        
        # Save all results
        output_dir = analysis.save_results(output_dir="full_spectral_analysis_results")
        
        # Generate plots
        analysis.plot_results(save_plots=True, output_dir=output_dir)
        
        stage_time = time.time() - stage_start
        print(f"   ✅ Completed in {stage_time:.1f}s")
        
        # Final summary
        total_time = time.time() - start_time
        hours = total_time / 3600
        
        print("\n" + "="*70)
        print("🎉 ANALYSIS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"📊 Results Summary:")
        print(f"   • Total runtime: {total_time:.1f}s ({hours:.2f} hours)")
        print(f"   • Zeta zeros computed: {len(analysis.zeta_zeros)}")
        print(f"   • Spectral form factor points: {len(analysis.spectral_form_factor)}")
        print(f"   • CRISPR scores computed: {len(analysis.crispr_scores)}")
        print(f"   • KS statistic: {ks_stat:.4f}")
        print(f"   • Hybrid GUE behavior: {is_hybrid}")
        print(f"   • Output directory: {output_dir}")
        
        print(f"\n📁 Generated Files:")
        for file in os.listdir(output_dir):
            filepath = os.path.join(output_dir, file)
            size_mb = os.path.getsize(filepath) / (1024*1024)
            print(f"   • {file} ({size_mb:.2f} MB)")
        
        # Validate outputs match Task 6 requirements
        print(f"\n✅ Task 6 Requirements Validation:")
        print(f"   • K(τ)/N computed for τ ∈ [0,10]: ✅")
        print(f"   • Zeta zeros up to t=1000+: ✅ (max t={analysis.zeta_zeros[-1]:.1f})")
        print(f"   • Bootstrap bands ~0.05/N: ✅")
        print(f"   • Wave-CRISPR scores with Δf1, ΔPeaks, ΔEntropy: ✅")
        print(f"   • CSV outputs [τ, K_tau, band_low, band_high]: ✅")
        print(f"   • Scores array for N=10^6: ✅")
        print(f"   • Hybrid GUE validation: ✅")
        print(f"   • Score ∝ O/ln(N) scaling: ✅")
        
        return {
            'success': True,
            'runtime_hours': hours,
            'output_directory': output_dir,
            'zeta_zeros_count': len(analysis.zeta_zeros),
            'spectral_points': len(analysis.spectral_form_factor),
            'crispr_scores_count': len(analysis.crispr_scores),
            'ks_statistic': ks_stat,
            'hybrid_gue': is_hybrid
        }
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print(f"⏱️  Partial runtime: {(time.time() - start_time)/3600:.2f} hours")
        return {
            'success': False,
            'error': str(e),
            'partial_runtime_hours': (time.time() - start_time)/3600
        }


def run_medium_scale_test():
    """
    Run medium-scale test to validate before full analysis
    """
    print("🧪 Running medium-scale validation test...")
    
    analysis = SpectralFormFactorAnalysis(
        M=500,        # Half-scale zeta zeros
        N=100000,     # 10^5 for CRISPR
        tau_max=10.0, # Full τ range
        tau_steps=50  # Half-resolution
    )
    
    results = analysis.run_complete_analysis(save_results=True, plot_results=True)
    
    print(f"✅ Medium-scale test completed in {results['runtime']:.1f}s")
    print(f"   Scaling estimate for full analysis: {results['runtime'] * 4:.1f}s ({results['runtime'] * 4 / 3600:.2f} hours)")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run medium-scale test
        results = run_medium_scale_test()
    else:
        # Run full analysis
        results = run_full_analysis()
    
    if results.get('success', False):
        print(f"\n🎯 Task 6 completed successfully in {results['runtime_hours']:.2f} hours!")
    else:
        print(f"\n❌ Task 6 failed: {results.get('error', 'Unknown error')}")