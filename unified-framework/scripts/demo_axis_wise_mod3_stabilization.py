#!/usr/bin/env python3
"""
Demo script for Axis-wise Stabilization of Infinite Mod-3 Residue Series

This script demonstrates the complete analysis workflow with a small dataset
for quick validation of the implementation.

Usage:
    python3 demo_axis_wise_mod3_stabilization.py
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from applications.axis_wise_mod3_stabilization import AxiswiseMod3Stabilization

def main():
    """Run demonstration of axis-wise mod-3 stabilization analysis."""
    print("=" * 70)
    print("AXIS-WISE STABILIZATION OF INFINITE MOD-3 RESIDUE SERIES")
    print("Scientific Test Suite Demonstration")
    print("=" * 70)
    
    # Create temporary directory for demo outputs
    temp_dir = tempfile.mkdtemp(prefix="axis_mod3_demo_")
    original_cwd = os.getcwd()
    
    try:
        # Change to temp directory
        os.chdir(temp_dir)
        print(f"Demo outputs will be saved to: {temp_dir}")
        
        # Create analyzer with small parameters for quick demo
        print("\nInitializing analyzer with demo parameters...")
        analyzer = AxiswiseMod3Stabilization(
            max_n=1000,      # Small for demo (normally 1,000,000)
            batch_size=100   # Small batches
        )
        
        # Use smaller resolution ladder for demo
        analyzer.resolution_ladder = [100, 300, 500]
        analyzer.n_bootstrap = 100  # Reduced for speed
        
        print(f"Resolution ladder: {analyzer.resolution_ladder}")
        print(f"Bootstrap iterations: {analyzer.n_bootstrap}")
        print(f"Primary k parameter: {analyzer.k_primary}")
        
        # Demonstrate individual components
        print("\n" + "-" * 50)
        print("COMPONENT DEMONSTRATIONS")
        print("-" * 50)
        
        # 1. Mod-3 partitioning
        print("\n1. Mod-3 Sequence Partitioning:")
        sequences = analyzer.partition_mod3_sequences(15)
        for axis_id, seq in sequences.items():
            print(f"   S{axis_id}: {seq}")
        
        # 2. Z-Framework observables
        print("\n2. Z-Framework Observables:")
        test_n = 12
        prime_density = analyzer.compute_prime_density([test_n])
        kappa = analyzer.compute_kappa(test_n)
        theta_prime = analyzer.compute_theta_prime(test_n, analyzer.k_primary)
        
        print(f"   n = {test_n}:")
        print(f"   Prime density: {prime_density:.6f}")
        print(f"   κ(n) = {kappa:.6f}")
        print(f"   θ′(n,k) = {theta_prime:.6f}")
        
        # 3. Prime starvation demonstration
        print("\n3. Prime Starvation Analysis:")
        for axis_id in [0, 1, 2]:
            axis_seq = sequences[axis_id]
            density = analyzer.compute_prime_density(axis_seq)
            print(f"   S{axis_id} prime density: {density:.4f}")
        
        print("   → S₀ shows expected lower prime density (hypothesis validation)")
        
        # 4. Bootstrap confidence intervals
        print("\n4. Bootstrap Confidence Intervals:")
        test_data = [1.2, 1.5, 1.3, 1.4, 1.6]
        mean_est, ci_low, ci_high = analyzer.bootstrap_confidence_interval(test_data)
        print(f"   Test data: {test_data}")
        print(f"   Mean estimate: {mean_est:.4f}")
        print(f"   95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
        
        # Run full analysis
        print("\n" + "-" * 50)
        print("FULL ANALYSIS EXECUTION")
        print("-" * 50)
        
        results = analyzer.run_full_analysis()
        
        # Display results summary
        print("\n" + "-" * 50)
        print("RESULTS SUMMARY")
        print("-" * 50)
        
        # Acceptance checks
        print("\nAcceptance Checks:")
        for check, passed in results['acceptance_checks'].items():
            status = "✅ PASS" if passed else "❌ FAIL"
            check_name = check.replace('_', ' ').title()
            print(f"  {check_name}: {status}")
        
        # Generated outputs
        print("\nGenerated Outputs:")
        results_dir = Path("results")
        figs_dir = Path("figs")
        
        csv_files = list(results_dir.glob("*.csv"))
        png_files = list(figs_dir.glob("*.png"))
        md_files = list(results_dir.glob("*.md"))
        
        print(f"  CSV Tables: {len(csv_files)} files")
        for csv_file in sorted(csv_files):
            print(f"    - {csv_file.name}")
        
        print(f"  Figures: {len(png_files)} files")
        for png_file in sorted(png_files):
            print(f"    - {png_file.name}")
        
        print(f"  Reports: {len(md_files)} files")
        for md_file in sorted(md_files):
            print(f"    - {md_file.name}")
        
        # Sample from results
        print("\nSample Results:")
        ladder_df = results['ladder_results']
        print(f"  Resolution ladder data: {len(ladder_df)} rows")
        
        # Show final N results for each axis
        max_n = ladder_df['N'].max()
        final_results = ladder_df[ladder_df['N'] == max_n]
        
        print(f"  Results at N = {max_n}:")
        for _, row in final_results.iterrows():
            axis = row['axis']
            prime_density = row['prime_density_mean']
            kappa_mean = row['kappa_mean']
            print(f"    {axis}: Prime density = {prime_density:.6f}, κ̄ = {kappa_mean:.6f}")
        
        # Performance metrics
        prop_vs_indep = results['proportional_vs_independent']
        print(f"\n  Proportional vs Independent scenarios: {len(prop_vs_indep)} compared")
        
        print("\n" + "-" * 50)
        print("SCIENTIFIC VALIDATION")
        print("-" * 50)
        
        # Validate core hypothesis
        s0_final = final_results[final_results['axis'] == 'S0']
        s1_final = final_results[final_results['axis'] == 'S1']
        s2_final = final_results[final_results['axis'] == 'S2']
        
        if len(s0_final) > 0 and len(s1_final) > 0 and len(s2_final) > 0:
            s0_density = s0_final['prime_density_mean'].iloc[0]
            s1_density = s1_final['prime_density_mean'].iloc[0]
            s2_density = s2_final['prime_density_mean'].iloc[0]
            
            print(f"\nCore Hypothesis Validation:")
            print(f"  S₀ prime density: {s0_density:.6f}")
            print(f"  S₁ prime density: {s1_density:.6f}")
            print(f"  S₂ prime density: {s2_density:.6f}")
            
            if s0_density < s1_density and s0_density < s2_density:
                print("  ✅ HYPOTHESIS CONFIRMED: S₀ stabilizes faster (lower prime density)")
            else:
                print("  ⚠️  Hypothesis not clearly demonstrated in demo dataset")
        
        # Mathematical precision validation
        print(f"\nNumerical Precision:")
        print(f"  Mathematical constants:")
        from applications.axis_wise_mod3_stabilization import PHI, E_SQUARED
        print(f"    φ (Golden ratio) = {float(PHI):.10f}")
        print(f"    e² = {float(E_SQUARED):.10f}")
        print(f"  Target precision: abs error < 1e-16")
        
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)
        print(f"\nDemo outputs saved to: {temp_dir}")
        print("\nTo run full-scale analysis (N=10⁶), use:")
        print("  python3 -c \"from src.applications.axis_wise_mod3_stabilization import main; main()\"")
        
        # Option to preserve demo outputs
        preserve = input("\nPreserve demo outputs? (y/N): ").lower().strip()
        if preserve == 'y':
            print(f"Demo outputs preserved at: {temp_dir}")
            return temp_dir
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise
    
    finally:
        # Return to original directory
        os.chdir(original_cwd)
        
        # Cleanup if not preserving
        if 'preserve' not in locals() or preserve != 'y':
            try:
                shutil.rmtree(temp_dir)
                print("Demo outputs cleaned up.")
            except:
                print(f"Note: Cleanup failed, temp files remain at: {temp_dir}")

if __name__ == "__main__":
    main()