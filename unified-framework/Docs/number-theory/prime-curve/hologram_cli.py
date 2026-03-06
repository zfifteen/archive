#!/usr/bin/env python3
"""
Command-line interface for Advanced Hologram Visualizations.

This script provides easy access to the enhanced hologram visualization
capabilities through command-line arguments.

Usage:
    python3 hologram_cli.py --help
    python3 hologram_cli.py --all --points 1000 --output ./results
    python3 hologram_cli.py --spiral --torus --points 500
    python3 hologram_cli.py --5d --type helical --dims 0,1,2
"""

import argparse
import os
import sys
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from hologram import AdvancedHologramVisualizer
except ImportError as e:
    print(f"Error: Could not import hologram module: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Advanced Hologram Visualizations for Z Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate all visualizations with 1000 points:
    python3 hologram_cli.py --all --points 1000 --output ./results

  Generate specific visualizations:
    python3 hologram_cli.py --3d --spiral --torus --points 500

  Generate 5D projections with custom parameters:
    python3 hologram_cli.py --5d --projection-type helical --dimensions 0,1,2

  Interactive exploration with statistics:
    python3 hologram_cli.py --interactive --stats --points 2000
        """
    )
    
    # Data parameters
    data_group = parser.add_argument_group('Data Parameters')
    data_group.add_argument('--points', '-n', type=int, default=2000,
                           help='Number of data points to generate (default: 2000)')
    data_group.add_argument('--helix-freq', type=float, default=0.1003033,
                           help='Helical frequency parameter (default: 0.1003033)')
    data_group.add_argument('--log-scale', action='store_true',
                           help='Use logarithmic scaling for y-axis')
    
    # Visualization selection
    viz_group = parser.add_argument_group('Visualization Selection')
    viz_group.add_argument('--all', action='store_true',
                          help='Generate all visualizations')
    viz_group.add_argument('--3d', action='store_true',
                          help='Generate 3D prime geometry')
    viz_group.add_argument('--spiral', action='store_true',
                          help='Generate logarithmic spirals')
    viz_group.add_argument('--gaussian', action='store_true',
                          help='Generate Gaussian prime spirals')
    viz_group.add_argument('--torus', action='store_true',
                          help='Generate modular tori')
    viz_group.add_argument('--5d', action='store_true',
                          help='Generate 5D projections')
    viz_group.add_argument('--zeta', action='store_true',
                          help='Generate Riemann zeta landscape')
    viz_group.add_argument('--interactive', action='store_true',
                          help='Run interactive exploration')
    
    # Specific parameters
    param_group = parser.add_argument_group('Specific Parameters')
    param_group.add_argument('--spiral-rate', type=float, default=0.1,
                            help='Spiral rate for logarithmic spirals (default: 0.1)')
    param_group.add_argument('--height-scale', choices=['sqrt', 'log', 'linear'], default='sqrt',
                            help='Height scaling method for spirals (default: sqrt)')
    param_group.add_argument('--angle-increment', choices=['golden', 'pi', 'custom'], default='golden',
                            help='Angle increment for Gaussian spirals (default: golden)')
    param_group.add_argument('--mod1', type=int, default=17,
                            help='First modular base for torus (default: 17)')
    param_group.add_argument('--mod2', type=int, default=23,
                            help='Second modular base for torus (default: 23)')
    param_group.add_argument('--torus-ratio', type=float, default=3.0,
                            help='Torus ratio (major/minor radius) (default: 3.0)')
    param_group.add_argument('--projection-type', choices=['helical', 'orthogonal', 'perspective'], 
                            default='helical', help='5D projection type (default: helical)')
    param_group.add_argument('--dimensions', type=str, default='0,1,2',
                            help='Dimensions for 5D projection as comma-separated (default: 0,1,2)')
    
    # Output parameters
    output_group = parser.add_argument_group('Output Parameters')
    output_group.add_argument('--output', '-o', type=str, default='./hologram_output',
                             help='Output directory for saved plots (default: ./hologram_output)')
    output_group.add_argument('--save', action='store_true', default=True,
                             help='Save plots to files (default: True)')
    output_group.add_argument('--no-save', action='store_false', dest='save',
                             help='Do not save plots to files')
    output_group.add_argument('--stats', action='store_true',
                             help='Display detailed statistics')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.all, args.interactive, args.spiral, args.gaussian, args.torus, args.zeta, args.spiral, args.gaussian]):
        if not args.all:
            args.all = True  # Default to all if nothing specified
    
    # Parse dimensions for 5D projection
    try:
        dimensions = tuple(map(int, args.dimensions.split(',')))
        if len(dimensions) != 3:
            raise ValueError("Dimensions must be exactly 3 values")
        if any(d < 0 or d > 4 for d in dimensions):
            raise ValueError("Dimension indices must be between 0 and 4")
    except ValueError as e:
        print(f"Error parsing dimensions '{args.dimensions}': {e}")
        sys.exit(1)
    
    print("Z Framework Advanced Hologram Visualizations")
    print("=" * 50)
    print(f"Initializing with {args.points} data points...")
    
    # Create visualizer
    start_time = time.time()
    visualizer = AdvancedHologramVisualizer(
        n_points=args.points,
        helix_freq=args.helix_freq,
        use_log_scale=args.log_scale
    )
    
    init_time = time.time() - start_time
    print(f"Initialization completed in {init_time:.2f} seconds")
    
    # Display statistics if requested
    if args.stats:
        print("\nDataset Statistics:")
        print("-" * 30)
        stats = visualizer.get_statistics()
        print(f"Total points: {stats['n_points']}")
        print(f"Prime count: {stats['prime_count']}")
        print(f"Prime density: {stats['prime_density']:.4f}")
        print(f"Helix frequency: {stats['helix_frequency']}")
        print(f"Log scale: {stats['use_log_scale']}")
        
        if stats['embedding_statistics']:
            print("\n5D Embedding Statistics:")
            print(f"Mean coordinates: {[f'{x:.3f}' for x in stats['embedding_statistics']['mean']]}")
            print(f"Std deviations: {[f'{x:.3f}' for x in stats['embedding_statistics']['std']]}")
    
    # Create output directory if saving
    if args.save:
        os.makedirs(args.output, exist_ok=True)
        print(f"\nSaving plots to: {args.output}")
    
    print(f"\nGenerating visualizations...")
    generation_start = time.time()
    
    # Generate visualizations based on arguments
    if args.all or args.interactive:
        print("Running interactive exploration...")
        visualizer.interactive_exploration(save_plots=args.save, output_dir=args.output)
    else:
        # Generate specific visualizations
        if args.spiral or args.spiral:
            print("Generating 3D prime geometry...")
            fig = visualizer.prime_geometry_3d(
                save_path=os.path.join(args.output, "prime_geometry_3d.png") if args.save else None
            )
        
        if args.spiral:
            print("Generating logarithmic spiral...")
            fig = visualizer.logarithmic_spiral(
                spiral_rate=args.spiral_rate,
                height_scale=args.height_scale,
                save_path=os.path.join(args.output, "logarithmic_spiral.png") if args.save else None
            )
        
        if args.gaussian:
            print("Generating Gaussian prime spiral...")
            fig = visualizer.gaussian_prime_spiral(
                angle_increment=args.angle_increment,
                save_path=os.path.join(args.output, "gaussian_spiral.png") if args.save else None
            )
        
        if args.torus:
            print("Generating modular torus...")
            fig = visualizer.modular_torus(
                mod1=args.mod1,
                mod2=args.mod2,
                torus_ratio=args.torus_ratio,
                save_path=os.path.join(args.output, "modular_torus.png") if args.save else None
            )
        
        if args.spiral:
            print("Generating 5D projection...")
            try:
                fig = visualizer.projection_5d(
                    projection_type=args.projection_type,
                    dimensions=dimensions,
                    save_path=os.path.join(args.output, "projection_5d.png") if args.save else None
                )
            except Exception as e:
                print(f"Warning: 5D projection failed: {e}")
        
        if args.zeta:
            print("Generating Riemann zeta landscape...")
            try:
                fig = visualizer.riemann_zeta_landscape(
                    save_path=os.path.join(args.output, "zeta_landscape.png") if args.save else None
                )
            except Exception as e:
                print(f"Warning: Zeta landscape generation failed: {e}")
    
    generation_time = time.time() - generation_start
    total_time = time.time() - start_time
    
    print(f"\nGeneration completed in {generation_time:.2f} seconds")
    print(f"Total runtime: {total_time:.2f} seconds")
    
    if args.save:
        print(f"Results saved to: {os.path.abspath(args.output)}")
        
        # List generated files
        try:
            files = os.listdir(args.output)
            if files:
                print(f"Generated {len(files)} visualization files:")
                for file in sorted(files):
                    file_path = os.path.join(args.output, file)
                    size = os.path.getsize(file_path)
                    print(f"  - {file} ({size//1024} KB)")
        except OSError:
            pass
    
    print("\nVisualization generation completed successfully!")


if __name__ == "__main__":
    main()