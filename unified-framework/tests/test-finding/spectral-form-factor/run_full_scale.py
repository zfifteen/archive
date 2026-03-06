#!/usr/bin/env python3
"""
Full-Scale Spectral Form Factor Analysis
========================================

Optimized implementation for full-scale analysis with M=1000 zeta zeros
as specified in Issue #121, designed to complete in reasonable time.
"""

import sys
import os
import time
sys.path.append('/home/runner/work/unified-framework/unified-framework/src')
sys.path.append('/home/runner/work/unified-framework/unified-framework/tests/test-finding/scripts')

from spectral_form_factor_analysis import SpectralFormFactorAnalysis
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.switch_backend('Agg')

def run_optimized_full_scale():
    """
    Run optimized full-scale analysis for Issue #121 requirements
    """
    print("🚀 FULL-SCALE SPECTRAL FORM FACTOR ANALYSIS")
    print("=" * 60)
    print("Optimized for Issue #121 requirements:")
    print("  • M=1000 zeta zeros")
    print("  • τ ∈ [0,10] with 100 steps")
    print("  • Bootstrap bands ≈0.05/N")
    print("  • Wave-CRISPR scores included")
    print("=" * 60)
    
    # Create output directory
    output_dir = "/home/runner/work/unified-framework/unified-framework/test-finding/spectral-form-factor/full_scale_results"
    os.makedirs(output_dir, exist_ok=True)
    
    start_time = time.time()
    
    # Initialize with full-scale parameters
    analysis = SpectralFormFactorAnalysis(
        M=1000,       # 1000 zeta zeros as specified
        N=1000000,    # N=10^6 as specified
        tau_max=10.0, # τ ∈ [0,10] as specified
        tau_steps=100 # 100 τ points as specified
    )
    
    # Stage 1: Zeta zeros
    print("\n📊 Stage 1/5: Computing 1000 zeta zeros...")
    stage_start = time.time()
    analysis.compute_zeta_zeros()
    print(f"   ✅ Completed in {time.time() - stage_start:.1f}s")
    
    # Stage 2: Unfolding
    print("\n🔄 Stage 2/5: Unfolding zeros...")
    stage_start = time.time()
    analysis.unfold_zeros()
    print(f"   ✅ Completed in {time.time() - stage_start:.1f}s")
    
    # Stage 3: Spectral form factor
    print("\n📈 Stage 3/5: Computing spectral form factor K(τ)/N...")
    stage_start = time.time()
    analysis.compute_spectral_form_factor()
    print(f"   ✅ Completed in {time.time() - stage_start:.1f}s")
    
    # Stage 4: Bootstrap bands (optimized with fewer samples for speed)
    print("\n🎯 Stage 4/5: Computing bootstrap confidence bands...")
    stage_start = time.time()
    analysis.compute_bootstrap_bands(n_bootstrap=500)  # Reduced for performance
    print(f"   ✅ Completed in {time.time() - stage_start:.1f}s")
    
    # Stage 5: CRISPR scores (optimized sample size)
    print("\n🧬 Stage 5/5: Computing Wave-CRISPR scores...")
    stage_start = time.time()
    analysis.compute_wave_crispr_scores(sample_size=20000)  # Optimized size
    print(f"   ✅ Completed in {time.time() - stage_start:.1f}s")
    
    # Validation
    print("\n✅ Validation: Hybrid GUE statistics...")
    ks_stat, p_value, is_hybrid = analysis.validate_hybrid_gue()
    
    # Save results in required format
    print("\n💾 Saving results...")
    
    # 1. Spectral form factor CSV: [τ, K_tau, band_low, band_high]
    spectral_df = pd.DataFrame({
        'tau': analysis.tau_values,
        'K_tau': analysis.spectral_form_factor,
        'band_low': analysis.bootstrap_bands['low'],
        'band_high': analysis.bootstrap_bands['high']
    })
    
    spectral_csv = os.path.join(output_dir, "spectral_form_factor_full_scale.csv")
    spectral_df.to_csv(spectral_csv, index=False, float_format='%.6f')
    print(f"   ✅ Spectral form factor: {spectral_csv}")
    
    # 2. CRISPR scores
    if analysis.crispr_scores:
        crispr_df = pd.DataFrame(analysis.crispr_scores)
        crispr_csv = os.path.join(output_dir, "wave_crispr_scores_full_scale.csv")
        crispr_df.to_csv(crispr_csv, index=False, float_format='%.6f')
        print(f"   ✅ CRISPR scores: {crispr_csv}")
    
    # 3. Zeta zeros
    zeros_df = pd.DataFrame({
        'zeta_zero': analysis.zeta_zeros,
        'unfolded': analysis.unfolded_zeros
    })
    zeros_csv = os.path.join(output_dir, "zeta_zeros_full_scale.csv")
    zeros_df.to_csv(zeros_csv, index=False, float_format='%.6f')
    print(f"   ✅ Zeta zeros: {zeros_csv}")
    
    # 4. Summary statistics
    summary_data = {
        'regime': 'full_scale',
        'M_zeta_zeros': len(analysis.zeta_zeros),
        'tau_max': analysis.tau_max,
        'tau_steps': len(analysis.tau_values),
        'N_sequences': analysis.N,
        'crispr_scores_computed': len(analysis.crispr_scores),
        'min_K_tau': np.min(analysis.spectral_form_factor),
        'max_K_tau': np.max(analysis.spectral_form_factor),
        'mean_K_tau': np.mean(analysis.spectral_form_factor),
        'bootstrap_band_width': np.mean(analysis.bootstrap_bands['high'] - analysis.bootstrap_bands['low']),
        'confidence_level': 0.90,
        'ks_statistic': ks_stat,
        'hybrid_gue_detected': is_hybrid
    }
    
    summary_csv = os.path.join(output_dir, "summary_statistics_full_scale.csv")
    pd.DataFrame([summary_data]).to_csv(summary_csv, index=False)
    print(f"   ✅ Summary statistics: {summary_csv}")
    
    # Generate plots
    print("\n📊 Generating plots...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Spectral Form Factor Analysis - FULL SCALE (M=1000)', fontsize=16)
    
    # 1. Spectral form factor with bootstrap bands
    ax1 = axes[0, 0]
    ax1.plot(analysis.tau_values, analysis.spectral_form_factor, 'b-', 
            label='K(τ)/N', linewidth=2, alpha=0.8)
    ax1.fill_between(analysis.tau_values, 
                    analysis.bootstrap_bands['low'], 
                    analysis.bootstrap_bands['high'], 
                    alpha=0.3, color='lightblue', label='Bootstrap bands (≈0.05/N)')
    ax1.set_xlabel('τ')
    ax1.set_ylabel('K(τ)/N')
    ax1.set_title(f'Spectral Form Factor (M={len(analysis.zeta_zeros)} zeros)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Zeta zeros
    ax2 = axes[0, 1]
    ax2.plot(range(len(analysis.zeta_zeros)), analysis.zeta_zeros, 
            'r.', alpha=0.7, markersize=2, label='Raw zeros')
    ax2.plot(range(len(analysis.unfolded_zeros)), analysis.unfolded_zeros, 
            'b.', alpha=0.7, markersize=2, label='Unfolded zeros')
    ax2.set_xlabel('Zero index')
    ax2.set_ylabel('Height')
    ax2.set_title('Riemann Zeta Zeros')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Bootstrap band width
    ax3 = axes[1, 0]
    band_widths = analysis.bootstrap_bands['high'] - analysis.bootstrap_bands['low']
    ax3.plot(analysis.tau_values, band_widths, 'g-', linewidth=2)
    ax3.set_xlabel('τ')
    ax3.set_ylabel('Band width')
    ax3.set_title('Bootstrap Confidence Band Width')
    ax3.grid(True, alpha=0.3)
    
    # 4. CRISPR score distribution
    ax4 = axes[1, 1]
    if analysis.crispr_scores:
        scores = [s['aggregate_score'] for s in analysis.crispr_scores]
        ax4.hist(scores, bins=50, alpha=0.7, density=True, color='orange')
        ax4.set_xlabel('Aggregate Score')
        ax4.set_ylabel('Density')
        ax4.set_title(f'Wave-CRISPR Score Distribution (N={len(scores)})')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    plot_file = os.path.join(output_dir, "spectral_analysis_full_scale.png")
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Plots: {plot_file}")
    
    total_runtime = time.time() - start_time
    
    print(f"\n🎉 FULL-SCALE ANALYSIS COMPLETED!")
    print(f"   Runtime: {total_runtime:.1f}s ({total_runtime/60:.2f} minutes)")
    print(f"   Zeta zeros: {len(analysis.zeta_zeros)}")
    print(f"   Spectral points: {len(analysis.spectral_form_factor)}")
    print(f"   CRISPR scores: {len(analysis.crispr_scores)}")
    print(f"   KS statistic: {ks_stat:.4f}")
    print(f"   Hybrid GUE: {is_hybrid}")
    print(f"   Output directory: {output_dir}")
    
    return {
        'runtime': total_runtime,
        'output_dir': output_dir,
        'zeta_zeros_count': len(analysis.zeta_zeros),
        'ks_statistic': ks_stat,
        'hybrid_gue': is_hybrid
    }

if __name__ == "__main__":
    result = run_optimized_full_scale()
    print(f"\n✅ Full-scale analysis completed in {result['runtime']/60:.2f} minutes")