#!/usr/bin/env python3
"""
Interactive 3D Helical Quantum Nonlocality Demonstration

This script demonstrates the capabilities of the Interactive3DHelixVisualizer,
showcasing helical patterns with quantum nonlocality analogs within the Z framework.

Features demonstrated:
- Interactive 3D helical visualizations with prime highlighting
- Quantum nonlocality pattern detection
- Bell inequality violation analysis
- Parameter control and sensitivity analysis
- Integration with core Z framework components

Usage:
    python3 interactive_3d_demo.py [--n_points N] [--k K] [--freq F]
    
Example:
    python3 interactive_3d_demo.py --n_points 3000 --k 0.200 --freq 0.1
"""

import sys
import os
import argparse
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visualization.interactive_3d_helix import Interactive3DHelixVisualizer
import plotly.offline as pyo

def main():
    """Main demonstration function."""
    parser = argparse.ArgumentParser(description='Interactive 3D Helical Quantum Nonlocality Demo')
    parser.add_argument('--n_points', type=int, default=2000, 
                       help='Number of points to generate (default: 2000)')
    parser.add_argument('--k', type=float, default=0.200,
                       help='Curvature parameter (default: 0.200, optimal k*)')
    parser.add_argument('--freq', type=float, default=0.1003033,
                       help='Helical frequency parameter (default: 0.1003033)')
    parser.add_argument('--no_primes', action='store_true',
                       help='Disable prime highlighting')
    parser.add_argument('--no_quantum', action='store_true',
                       help='Disable quantum correlation visualization')
    parser.add_argument('--no_bell', action='store_true',
                       help='Disable Bell violation indicators')
    parser.add_argument('--animation', action='store_true',
                       help='Create parameter sweep animation')
    parser.add_argument('--output_dir', type=str, default='.',
                       help='Output directory for HTML files (default: current directory)')
    
    args = parser.parse_args()
    
    print("🌀 Interactive 3D Helical Quantum Nonlocality Visualizer")
    print("=" * 60)
    print(f"🎯 Configuration:")
    print(f"   Points: {args.n_points}")
    print(f"   Curvature k: {args.k}")
    print(f"   Frequency: {args.freq}")
    print(f"   Prime highlighting: {'✗' if args.no_primes else '✓'}")
    print(f"   Quantum correlations: {'✗' if args.no_quantum else '✓'}")
    print(f"   Bell violations: {'✗' if args.no_bell else '✓'}")
    print(f"   Animation: {'✓' if args.animation else '✗'}")
    print(f"   Output directory: {args.output_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize visualizer
    print("\n🔧 Initializing visualizer...")
    visualizer = Interactive3DHelixVisualizer(
        n_points=args.n_points,
        default_k=args.k,
        helix_freq=args.freq
    )
    
    print(f"✓ Generated {len(visualizer.primes)} primes up to {np.max(visualizer.n)}")
    
    # Generate comprehensive report
    print("\n📊 Generating analysis report...")
    report = visualizer.generate_summary_report(args.k)
    
    print("📈 Analysis Results:")
    print(f"   Prime density: {report['statistics']['prime_density']:.4f}")
    print(f"   Maximum prime: {report['statistics']['max_prime']}")
    print(f"   Mean prime gap: {report['statistics']['mean_prime_gap']:.2f}")
    
    if 'quantum_analysis' in report and 'num_correlations' in report['quantum_analysis']:
        qa = report['quantum_analysis']
        if qa['num_correlations'] > 0:
            print(f"   Quantum correlations computed: {qa['num_correlations']}")
            print(f"   Mean correlation: {qa['mean_correlation']:.6f}")
            print(f"   Bell violation detected: {'✓' if qa['bell_violation_detected'] else '✗'}")
            if qa['bell_violation_detected']:
                print(f"   Correlation coefficient: {qa['correlation_coefficient']:.6f}")
                print("   ⚡ Quantum nonlocality analog detected!")
        else:
            print(f"   Note: {qa.get('note', 'No correlations computed')}")
    
    # Create main interactive visualization
    print("\n🎨 Creating main interactive 3D helical visualization...")
    fig_main = visualizer.create_interactive_helix_plot(
        k=args.k,
        freq=args.freq,
        show_primes=not args.no_primes,
        show_quantum_correlations=not args.no_quantum,
        show_bell_violations=not args.no_bell,
        title="Interactive 3D Helical Quantum Nonlocality Patterns"
    )
    
    main_file = os.path.join(args.output_dir, 'interactive_helix_main.html')
    pyo.plot(fig_main, filename=main_file, auto_open=False)
    print(f"✓ Saved main visualization: {main_file}")
    
    # Create quantum correlation analysis
    print("\n🔬 Creating quantum correlation analysis...")
    fig_correlations = visualizer.create_quantum_correlation_analysis(args.k)
    
    corr_file = os.path.join(args.output_dir, 'quantum_correlations.html')
    pyo.plot(fig_correlations, filename=corr_file, auto_open=False)
    print(f"✓ Saved correlation analysis: {corr_file}")
    
    # Create parameter sweep animation if requested
    if args.animation:
        print("\n🎬 Creating parameter sweep animation...")
        k_center = args.k
        k_range = (max(0.05, k_center - 0.1), k_center + 0.1)
        
        fig_animation = visualizer.create_parameter_sweep_animation(
            k_range=k_range,
            k_steps=15,
            save_html=False
        )
        
        anim_file = os.path.join(args.output_dir, 'helix_parameter_sweep.html')
        pyo.plot(fig_animation, filename=anim_file, auto_open=False)
        print(f"✓ Saved parameter sweep animation: {anim_file}")
    
    # Parameter sensitivity analysis
    print("\n🔍 Parameter sensitivity analysis:")
    k_values = [0.1, 0.15, 0.2, 0.25, 0.3]
    
    for k_test in k_values:
        test_report = visualizer.generate_summary_report(k_test)
        qa = test_report.get('quantum_analysis', {})
        
        if qa.get('num_correlations', 0) > 0:
            bell_status = "🔴" if qa.get('bell_violation_detected', False) else "🟢"
            correlation_coeff = qa.get('correlation_coefficient', 0.0)
            print(f"   k={k_test:.2f}: {bell_status} ρ={correlation_coeff:.4f}")
        else:
            print(f"   k={k_test:.2f}: ⚪ insufficient data")
    
    # Summary
    print("\n✨ Demonstration completed successfully!")
    print(f"\n📁 Generated files in {args.output_dir}:")
    print(f"   - interactive_helix_main.html (main 3D visualization)")
    print(f"   - quantum_correlations.html (correlation analysis)")
    if args.animation:
        print(f"   - helix_parameter_sweep.html (parameter animation)")
    
    print("\n🎯 Key Features Demonstrated:")
    print("   ✓ Interactive 3D helical patterns with plotly")
    print("   ✓ Prime number highlighting in curved space")
    print("   ✓ Quantum nonlocality correlation detection")
    print("   ✓ Bell inequality violation analysis")
    print("   ✓ Z framework integration (Z = A(B/c))")
    print("   ✓ Golden ratio φ curvature transforms")
    print("   ✓ Parameter sensitivity analysis")
    
    print("\n🌐 To view the visualizations:")
    print(f"   Open {main_file} in your web browser")
    print("   Interact with the 3D plot using mouse controls")
    print("   Hover over points to see detailed information")
    print("   Look for quantum correlation lines (orange)")
    print("   Check for Bell violation indicators (gold stars)")
    
    return report


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)