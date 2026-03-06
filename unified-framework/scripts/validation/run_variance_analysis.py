#!/usr/bin/env python3
"""
Variance Analysis Runner: Compute var(O) ~ log log N on embedding artifacts

This script provides a convenient entry point to generate embedding data and 
perform variance analysis for the Z framework. It handles the complete workflow
from data generation to analysis and visualization.

Usage:
    python3 run_variance_analysis.py [--generate-data] [--max-n MAX_N] [--analysis-only]

Examples:
    # Generate new data and run analysis
    python3 run_variance_analysis.py --generate-data --max-n 1000

    # Run analysis on existing data only
    python3 run_variance_analysis.py --analysis-only

    # Generate large dataset and analyze
    python3 run_variance_analysis.py --generate-data --max-n 10000
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Set up the Python path for imports."""
    repo_root = Path(__file__).parent.absolute()
    src_path = repo_root / 'src'
    
    # Add src to Python path
    if str(src_path) not in os.environ.get('PYTHONPATH', ''):
        os.environ['PYTHONPATH'] = f"{src_path}:{os.environ.get('PYTHONPATH', '')}"
    
    return repo_root, src_path

def generate_embedding_data(max_n, csv_name):
    """Generate embedding data using z_embeddings_csv.py."""
    print(f"Generating embedding data for N=1 to {max_n}...")
    print(f"Output file: {csv_name}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            'python3', 'src/applications/z_embeddings_csv.py',
            '1', str(max_n), '--csv_name', csv_name
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print(f"Error generating embedding data:")
            print(result.stderr)
            return False
        
        elapsed = time.time() - start_time
        print(f"Embedding data generated successfully in {elapsed:.2f} seconds")
        return True
        
    except subprocess.TimeoutExpired:
        print("Error: Data generation timed out (>10 minutes)")
        return False
    except Exception as e:
        print(f"Error generating embedding data: {e}")
        return False

def run_analysis():
    """Run the enhanced variance analysis."""
    print("Running enhanced variance analysis...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            'python3', 'src/analysis/enhanced_variance_analysis.py'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"Error running variance analysis:")
            print(result.stderr)
            return False
        
        # Print the analysis output
        print(result.stdout)
        
        elapsed = time.time() - start_time
        print(f"\\nAnalysis completed in {elapsed:.2f} seconds")
        return True
        
    except subprocess.TimeoutExpired:
        print("Error: Analysis timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"Error running analysis: {e}")
        return False

def check_existing_data():
    """Check for existing embedding files and return the best one."""
    embedding_files = []
    
    # Look for embedding files in order of preference (largest first)
    candidates = [
        'z_embeddings_10k_1.csv',
        'z_embeddings_5k_1.csv', 
        'z_embeddings_1k_1.csv',
        'z_embeddings_100_1.csv'
    ]
    
    for file in candidates:
        if os.path.exists(file):
            size = os.path.getsize(file)
            embedding_files.append((file, size))
    
    if embedding_files:
        # Return the largest file
        largest_file = max(embedding_files, key=lambda x: x[1])
        return largest_file[0], largest_file[1]
    
    return None, 0

def print_summary():
    """Print a summary of available results."""
    print("\n" + "="*80)
    print("VARIANCE ANALYSIS SUMMARY")
    print("="*80)
    
    # Check for results directories
    result_dirs = [
        'enhanced_variance_analysis_results',
        'variance_analysis_results'
    ]
    
    for result_dir in result_dirs:
        if os.path.exists(result_dir):
            print(f"\nResults directory: {result_dir}/")
            
            files = [
                ('enhanced_variance_analysis.png', 'Comprehensive visualization'),
                ('variance_analysis.png', 'Basic visualization'),
                ('comprehensive_variance_report.md', 'Detailed analysis report'),
                ('variance_analysis_report.md', 'Basic analysis report'),
                ('variance_analysis_results.json', 'Machine-readable results')
            ]
            
            for filename, description in files:
                filepath = os.path.join(result_dir, filename)
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    print(f"  - {filename}: {description} ({size:,} bytes)")
    
    # Check for embedding data
    existing_file, size = check_existing_data()
    if existing_file:
        print(f"\nEmbedding data: {existing_file} ({size:,} bytes)")
    
    print("\n" + "="*80)

def main():
    """Main function to handle command line arguments and orchestrate the analysis."""
    parser = argparse.ArgumentParser(
        description='Run variance analysis: var(O) ~ log log N on Z framework embeddings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--generate-data', action='store_true',
                       help='Generate new embedding data before analysis')
    parser.add_argument('--max-n', type=int, default=5000,
                       help='Maximum N value for embedding generation (default: 5000)')
    parser.add_argument('--analysis-only', action='store_true',
                       help='Only run analysis on existing data')
    parser.add_argument('--summary', action='store_true',
                       help='Show summary of existing results and exit')
    
    args = parser.parse_args()
    
    # Setup environment
    repo_root, src_path = setup_environment()
    os.chdir(repo_root)
    
    # Handle summary request
    if args.summary:
        print_summary()
        return
    
    print("Z Framework Variance Analysis")
    print("=" * 40)
    print(f"Repository root: {repo_root}")
    print(f"Python path: {os.environ.get('PYTHONPATH', 'Not set')}")
    print("")
    
    # Check for existing data
    existing_file, size = check_existing_data()
    if existing_file:
        print(f"Found existing embedding data: {existing_file} ({size:,} bytes)")
    
    # Data generation phase
    if args.generate_data and not args.analysis_only:
        csv_name = f"z_embeddings_{args.max_n//1000}k.csv"
        if args.max_n < 1000:
            csv_name = f"z_embeddings_{args.max_n}.csv"
        
        success = generate_embedding_data(args.max_n, csv_name)
        if not success:
            print("Failed to generate embedding data. Exiting.")
            return 1
    
    elif args.analysis_only:
        if not existing_file:
            print("No existing embedding data found. Use --generate-data to create some first.")
            print("Example: python3 run_variance_analysis.py --generate-data --max-n 1000")
            return 1
        print("Using existing embedding data for analysis...")
    
    elif not existing_file:
        print("No embedding data found and --generate-data not specified.")
        print("Generating default dataset (N=1000)...")
        success = generate_embedding_data(1000, "z_embeddings_1k.csv")
        if not success:
            print("Failed to generate default embedding data. Exiting.")
            return 1
    
    # Analysis phase
    print("\\nStarting variance analysis...")
    success = run_analysis()
    
    if success:
        print("\\nAnalysis completed successfully!")
        print_summary()
        
        print("\\nNext steps:")
        print("- View enhanced_variance_analysis_results/enhanced_variance_analysis.png")
        print("- Read enhanced_variance_analysis_results/comprehensive_variance_report.md")
        print("- Check variance_analysis_results.json for machine-readable results")
        
        return 0
    else:
        print("Analysis failed. Check error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)