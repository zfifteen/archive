#!/usr/bin/env python3
"""
Z-Invariant CRISPR Guide Designer CLI

Command-line interface for the Z-Invariant CRISPR Guide Designer platform.
Provides easy access to guide design, optimization, and visualization capabilities.

USAGE:
    python crispr_cli.py sequence "ATGC..." --output results/
    python crispr_cli.py file input.fasta --max-guides 5 --visualize
    python crispr_cli.py demo --save-plots

FEATURES:
- Sequence input from command line or FASTA files
- Comprehensive analysis with modular-geodesic embeddings
- Interactive visualization generation
- Statistical validation reporting
- Export capabilities for further analysis
"""

import argparse
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add source path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from applications.crispr_guide_designer import CRISPRGuideDesigner, demo_crispr_guide_design
from applications.crispr_visualization import CRISPRVisualization

class CRISPRGuideDesignerCLI:
    """
    Command-line interface for Z-Invariant CRISPR Guide Designer.
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.designer = None
        self.visualizer = None
    
    def parse_arguments(self):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description="Z-Invariant CRISPR Guide Designer - Enhanced precision through modular-geodesic embeddings",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s sequence "ATGCTGCGGAGACCTGGAGAGAAAG..." --output results/
  %(prog)s file target_sequence.fasta --max-guides 5 --visualize
  %(prog)s demo --save-plots
  %(prog)s batch sequences/ --format json
            """
        )
        
        # Version
        parser.add_argument('--version', action='version', version=f'%(prog)s {self.version}')
        
        # Input methods
        subparsers = parser.add_subparsers(dest='command', help='Analysis mode')
        
        # Direct sequence input
        seq_parser = subparsers.add_parser('sequence', help='Analyze sequence directly')
        seq_parser.add_argument('sequence', help='Target DNA sequence (A, T, G, C)')
        
        # File input
        file_parser = subparsers.add_parser('file', help='Analyze sequence from file')
        file_parser.add_argument('file_path', help='Path to FASTA file')
        
        # Demo mode
        demo_parser = subparsers.add_parser('demo', help='Run demonstration')
        
        # Batch processing
        batch_parser = subparsers.add_parser('batch', help='Process multiple files')
        batch_parser.add_argument('directory', help='Directory containing sequence files')
        
        # Common parameters for all modes
        for subparser in [seq_parser, file_parser, demo_parser, batch_parser]:
            subparser.add_argument('--max-guides', type=int, default=5,
                                 help='Maximum number of guides to design (default: 5)')
            subparser.add_argument('--k-parameter', type=float, default=0.3,
                                 help='θ′(n, k) transformation parameter (default: 0.3)')
            subparser.add_argument('--precision', type=int, default=30,
                                 help='Arithmetic precision (default: 30)')
            subparser.add_argument('--output', '-o', default='crispr_results',
                                 help='Output directory (default: crispr_results)')
            subparser.add_argument('--visualize', action='store_true',
                                 help='Generate interactive visualizations')
            subparser.add_argument('--save-plots', action='store_true',
                                 help='Save plots to files')
            subparser.add_argument('--format', choices=['json', 'csv', 'txt'], default='json',
                                 help='Output format (default: json)')
            subparser.add_argument('--quiet', '-q', action='store_true',
                                 help='Minimize output messages')
        
        return parser.parse_args()
    
    def read_fasta_file(self, file_path):
        """Read sequence from FASTA file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
            
            # Simple FASTA parsing (assumes single sequence)
            lines = content.split('\n')
            sequence = ''
            for line in lines:
                if not line.startswith('>'):
                    sequence += line.strip().upper()
            
            if not sequence:
                raise ValueError("No sequence found in file")
            
            return sequence
        except Exception as e:
            raise ValueError(f"Error reading FASTA file: {e}")
    
    def initialize_components(self, args):
        """Initialize designer and visualizer components."""
        self.designer = CRISPRGuideDesigner(
            precision=args.precision,
            k_parameter=args.k_parameter
        )
        
        if args.visualize or args.save_plots:
            self.visualizer = CRISPRVisualization()
    
    def analyze_sequence(self, sequence, args):
        """Perform complete sequence analysis."""
        if not args.quiet:
            print(f"Analyzing sequence of length {len(sequence)} bp...")
        
        # Run analysis
        results = self.designer.analyze_target_sequence(sequence, max_guides=args.max_guides)
        
        # Add metadata
        results['analysis_metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'max_guides': args.max_guides,
                'k_parameter': args.k_parameter,
                'precision': args.precision
            },
            'version': self.version
        }
        
        return results
    
    def generate_visualizations(self, results, args):
        """Generate and save visualizations."""
        if not self.visualizer:
            return {}
        
        output_dir = Path(args.output)
        viz_dir = output_dir / 'visualizations'
        viz_dir.mkdir(parents=True, exist_ok=True)
        
        if not args.quiet:
            print("Generating visualizations...")
        
        figures = self.visualizer.create_analysis_dashboard(
            results, 
            save_directory=str(viz_dir) if args.save_plots else None
        )
        
        # Generate comprehensive report
        if args.save_plots:
            report_path = viz_dir / 'analysis_report.html'
            self.visualizer.save_analysis_report(results, figures, str(report_path))
        
        return figures
    
    def save_results(self, results, args, output_filename='analysis_results'):
        """Save analysis results in specified format."""
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if args.format == 'json':
            output_path = output_dir / f'{output_filename}.json'
            with open(output_path, 'w') as f:
                # Convert numpy arrays to lists for JSON serialization
                json_results = self._prepare_for_json(results)
                json.dump(json_results, f, indent=2)
        
        elif args.format == 'csv':
            output_path = output_dir / f'{output_filename}.csv'
            self._save_as_csv(results, output_path)
        
        elif args.format == 'txt':
            output_path = output_dir / f'{output_filename}.txt'
            with open(output_path, 'w') as f:
                f.write(results.get('analysis_summary', ''))
        
        if not args.quiet:
            print(f"Results saved to: {output_path}")
        
        return output_path
    
    def _prepare_for_json(self, obj):
        """Prepare object for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._prepare_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(item) for item in obj]
        elif hasattr(obj, 'tolist'):  # numpy array
            return obj.tolist()
        elif hasattr(obj, '__dict__'):  # complex object
            return str(obj)
        else:
            return obj
    
    def _save_as_csv(self, results, output_path):
        """Save results as CSV file."""
        import pandas as pd
        
        # Extract guide data for CSV
        optimized_guides = results.get('optimized_guides', [])
        if not optimized_guides:
            return
        
        # Prepare data for DataFrame
        csv_data = []
        for guide in optimized_guides:
            csv_data.append({
                'sequence': guide['sequence'],
                'position': guide['position'],
                'pam_sequence': guide['pam_sequence'],
                'composite_score': guide.get('composite_score', 0),
                'z_framework_score': guide.get('z_framework_score', 0),
                'density_enhancement': guide.get('density_enhancement', 0),
                'off_target_risk': guide.get('off_target_risk', 0),
                'geodesic_complexity': guide.get('geodesic_complexity', 0)
            })
        
        df = pd.DataFrame(csv_data)
        df.to_csv(output_path, index=False)
    
    def run_sequence_analysis(self, args):
        """Run analysis for direct sequence input."""
        sequence = args.sequence.upper().replace(' ', '').replace('\\n', '')
        
        # Validate sequence
        if not all(base in 'ATGC' for base in sequence):
            raise ValueError("Sequence must contain only A, T, G, C nucleotides")
        
        results = self.analyze_sequence(sequence, args)
        
        # Generate visualizations if requested
        if args.visualize or args.save_plots:
            figures = self.generate_visualizations(results, args)
        
        # Save results
        self.save_results(results, args)
        
        # Display summary
        if not args.quiet:
            print("\\n" + results.get('analysis_summary', ''))
        
        return results
    
    def run_file_analysis(self, args):
        """Run analysis for file input."""
        sequence = self.read_fasta_file(args.file_path)
        
        if not args.quiet:
            print(f"Loaded sequence from: {args.file_path}")
        
        # Use filename for output
        base_name = Path(args.file_path).stem
        
        results = self.analyze_sequence(sequence, args)
        
        # Generate visualizations if requested
        if args.visualize or args.save_plots:
            figures = self.generate_visualizations(results, args)
        
        # Save results
        self.save_results(results, args, f'{base_name}_analysis')
        
        # Display summary
        if not args.quiet:
            print("\\n" + results.get('analysis_summary', ''))
        
        return results
    
    def run_demo(self, args):
        """Run demonstration analysis."""
        if not args.quiet:
            print("Running Z-Invariant CRISPR Guide Designer demonstration...")
        
        results = demo_crispr_guide_design()
        
        # Generate visualizations if requested
        if args.visualize or args.save_plots:
            self.initialize_components(args)
            figures = self.generate_visualizations(results, args)
        
        # Save results
        self.save_results(results, args, 'demo_analysis')
        
        return results
    
    def run_batch_analysis(self, args):
        """Run batch analysis on multiple files."""
        directory = Path(args.directory)
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Directory not found: {directory}")
        
        # Find FASTA files
        fasta_files = list(directory.glob('*.fasta')) + list(directory.glob('*.fa'))
        
        if not fasta_files:
            raise ValueError(f"No FASTA files found in: {directory}")
        
        if not args.quiet:
            print(f"Processing {len(fasta_files)} files from: {directory}")
        
        batch_results = []
        
        for file_path in fasta_files:
            try:
                if not args.quiet:
                    print(f"\\nProcessing: {file_path.name}")
                
                # Create file-specific args
                file_args = argparse.Namespace(**vars(args))
                file_args.file_path = str(file_path)
                file_args.output = str(Path(args.output) / file_path.stem)
                
                results = self.run_file_analysis(file_args)
                batch_results.append({
                    'file': str(file_path),
                    'results': results
                })
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                continue
        
        # Save batch summary
        batch_summary = {
            'processed_files': len(batch_results),
            'timestamp': datetime.now().isoformat(),
            'results': batch_results
        }
        
        summary_path = Path(args.output) / 'batch_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(self._prepare_for_json(batch_summary), f, indent=2)
        
        if not args.quiet:
            print(f"\\nBatch processing complete. Summary saved to: {summary_path}")
        
        return batch_results
    
    def run(self):
        """Main CLI execution."""
        try:
            args = self.parse_arguments()
            
            if not args.command:
                print("Error: Please specify a command (sequence, file, demo, or batch)")
                print("Use --help for usage information")
                return 1
            
            # Initialize components
            self.initialize_components(args)
            
            # Execute requested command
            if args.command == 'sequence':
                self.run_sequence_analysis(args)
            elif args.command == 'file':
                self.run_file_analysis(args)
            elif args.command == 'demo':
                self.run_demo(args)
            elif args.command == 'batch':
                self.run_batch_analysis(args)
            
            if not args.quiet:
                print(f"\\nAnalysis complete! Results saved to: {args.output}")
            
            return 0
            
        except Exception as e:
            print(f"Error: {e}")
            return 1

def main():
    """Entry point for CLI."""
    cli = CRISPRGuideDesignerCLI()
    return cli.run()

if __name__ == "__main__":
    sys.exit(main())