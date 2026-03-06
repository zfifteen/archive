#!/usr/bin/env python3
"""
Wave-Knob Prime Scanner Harness
==============================

Python harness for running z5d_mersenne experiments with batch R-sweep analysis.
Generates heatmaps, R-curves, and scaling analysis as described in the issue.

Usage:
    python3 wave_knob_harness.py --k 1e100 --r-sweep --output results.json
    python3 wave_knob_harness.py --k-range 1e6,1e9 --auto-tune --plot

Features:
- Batch R-sweep experiments (window/step grid scans) 
- Auto-tune convergence analysis
- Heatmap and curve generation
- Statistical analysis of R* scaling
- JSON telemetry aggregation
"""

import json
import subprocess
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import time
import sys
from typing import List, Dict, Tuple, Optional
import itertools

class WaveKnobHarness:
    """Harness for z5d_mersenne experiments."""
    
    def __init__(self, z5d_binary: str = None):
        """Initialize harness.
        
        Args:
            z5d_binary: Path to z5d_mersenne binary (auto-detected if None)
        """
        if z5d_binary is None:
            # Try to find z5d_mersenne binary
            for path in ['./z5d_mersenne', '../src/c/z5d_mersenne', './src/c/z5d_mersenne']:
                if Path(path).exists():
                    z5d_binary = path
                    break
            else:
                raise FileNotFoundError("z5d_mersenne binary not found. Please specify path.")
        
        self.z5d_binary = Path(z5d_binary).resolve()
        if not self.z5d_binary.exists():
            raise FileNotFoundError(f"z5d_mersenne binary not found: {self.z5d_binary}")
        
        print(f"Using z5d_mersenne binary: {self.z5d_binary}")
        
    def run_single_scan(self, k: str, window: int = None, step: int = None, 
                       auto_tune: bool = False, wheel: int = 210, 
                       precision: int = 4096, mr_rounds: int = 50) -> Dict:
        """Run a single scan and return parsed JSON result.
        
        Args:
            k: Target k value (string to support scientific notation)
            window: Search window size (None for auto-tune)
            step: Search step size (None for auto-tune) 
            auto_tune: Enable auto-tuning mode
            wheel: Wheel modulus (30 or 210)
            precision: MPFR precision in bits
            mr_rounds: Miller-Rabin test rounds
            
        Returns:
            Parsed JSON result dictionary
        """
        cmd = [str(self.z5d_binary), str(k), '--json', f'--wheel={wheel}', 
               f'--prec={precision}', f'--mr-rounds={mr_rounds}']
        
        if auto_tune:
            cmd.append('--auto-tune')
        else:
            cmd.extend(['--scan', f'--window={window}', f'--step={step}'])
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"Error running command: {' '.join(cmd)}")
                print(f"stderr: {result.stderr}")
                return None
                
            return json.loads(result.stdout)
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            print(f"Error in scan: {e}")
            return None
    
    def r_sweep_experiment(self, k: str, window_range: Tuple[int, int, int], 
                          step_range: Tuple[int, int, int], **kwargs) -> pd.DataFrame:
        """Run R-sweep experiment over window/step grid.
        
        Args:
            k: Target k value
            window_range: (start, stop, step) for window values
            step_range: (start, stop, step) for step values
            **kwargs: Additional arguments for run_single_scan
            
        Returns:
            DataFrame with columns: window, step, R, prime_count, mr_calls, elapsed_ms, locked, prime_found
        """
        results = []
        
        windows = range(*window_range)
        steps = range(*step_range)
        total_runs = len(windows) * len(steps)
        
        print(f"Running R-sweep for k={k}: {len(windows)} windows × {len(steps)} steps = {total_runs} total runs")
        
        start_time = time.time()
        for i, (window, step) in enumerate(itertools.product(windows, steps)):
            if step == 0:  # Avoid division by zero
                continue
                
            result = self.run_single_scan(k, window=window, step=step, auto_tune=False, **kwargs)
            if result:
                result['run_index'] = i
                results.append(result)
                
            # Progress update
            if (i + 1) % 10 == 0 or i == total_runs - 1:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                eta = (total_runs - i - 1) / rate if rate > 0 else 0
                print(f"  Progress: {i+1}/{total_runs} ({100*(i+1)/total_runs:.1f}%) "
                      f"Rate: {rate:.1f}/s ETA: {eta:.0f}s")
        
        df = pd.DataFrame(results)
        if not df.empty:
            # Convert numeric fields
            for col in ['window', 'step', 'R', 'prime_count', 'mr_calls', 'elapsed_ms']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
        print(f"R-sweep completed: {len(df)} successful runs out of {total_runs} attempted")
        return df
    
    def auto_tune_experiment(self, k_values: List[str], **kwargs) -> pd.DataFrame:
        """Run auto-tune experiments for multiple k values.
        
        Args:
            k_values: List of k values to test
            **kwargs: Additional arguments for run_single_scan
            
        Returns:
            DataFrame with auto-tune results
        """
        results = []
        
        print(f"Running auto-tune experiment for {len(k_values)} k values")
        
        for i, k in enumerate(k_values):
            print(f"  {i+1}/{len(k_values)}: k={k}")
            result = self.run_single_scan(k, auto_tune=True, **kwargs)
            if result:
                results.append(result)
        
        df = pd.DataFrame(results)
        if not df.empty:
            # Convert numeric fields
            for col in ['window', 'step', 'R', 'prime_count', 'iterations', 'mr_calls', 'elapsed_ms']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
        print(f"Auto-tune experiment completed: {len(df)} successful runs")
        return df
    
    def plot_r_sweep_heatmap(self, df: pd.DataFrame, output_file: str = None):
        """Generate R-sweep heatmap showing prime_count vs (window, step).
        
        Args:
            df: Results DataFrame from r_sweep_experiment
            output_file: Output file path (None for display)
        """
        if df.empty:
            print("No data to plot")
            return
            
        # Create pivot table for heatmap
        heatmap_data = df.pivot_table(values='prime_count', index='window', 
                                     columns='step', fill_value=0)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='viridis', 
                   cbar_kws={'label': 'Prime Count'})
        plt.title(f'Wave-Knob Heatmap: Prime Count vs (Window, Step)\nk = {df.iloc[0]["k"] if "k" in df.columns else "unknown"}')
        plt.xlabel('Step')
        plt.ylabel('Window') 
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Heatmap saved: {output_file}")
        else:
            plt.show()
    
    def plot_r_curve(self, df: pd.DataFrame, output_file: str = None):
        """Generate R-curve showing prime_count vs R ratio.
        
        Args:
            df: Results DataFrame from r_sweep_experiment  
            output_file: Output file path (None for display)
        """
        if df.empty:
            print("No data to plot")
            return
            
        plt.figure(figsize=(10, 6))
        
        # Plot prime count vs R
        plt.scatter(df['R'], df['prime_count'], alpha=0.6, s=30)
        
        # Highlight count=1 points (resonance valleys)
        valleys = df[df['prime_count'] == 1]
        if not valleys.empty:
            plt.scatter(valleys['R'], valleys['prime_count'], color='red', s=60, 
                       label=f'Resonance Valleys (count=1)', zorder=5)
            
            # Mark minimum R* with count=1
            r_star = valleys['R'].min()
            plt.axvline(r_star, color='red', linestyle='--', alpha=0.7,
                       label=f'R* = {r_star:.3f}')
        
        plt.xlabel('R = window/step')
        plt.ylabel('Prime Count')  
        plt.title(f'Wave-Knob R-Curve: Prime Count vs Ratio R\nk = {df.iloc[0]["k"] if "k" in df.columns else "unknown"}')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"R-curve saved: {output_file}")
        else:
            plt.show()
    
    def analyze_r_star_scaling(self, df: pd.DataFrame) -> Dict:
        """Analyze R* scaling across different k values.
        
        Args:
            df: Results DataFrame from auto_tune_experiment
            
        Returns:
            Analysis results dictionary
        """
        if df.empty or 'R' not in df.columns:
            return {}
            
        # Extract R* values (assuming these are from successful auto-tune runs)
        r_star_data = df[df['locked'] == True].copy() if 'locked' in df.columns else df.copy()
        
        if r_star_data.empty:
            return {'error': 'No successful auto-tune results'}
        
        # Convert k to numeric for analysis (handle scientific notation)
        r_star_data['k_numeric'] = pd.to_numeric(r_star_data['k'], errors='coerce')
        
        analysis = {
            'n_points': len(r_star_data),
            'k_range': [r_star_data['k_numeric'].min(), r_star_data['k_numeric'].max()],
            'r_star_range': [r_star_data['R'].min(), r_star_data['R'].max()],
            'mean_r_star': r_star_data['R'].mean(),
            'std_r_star': r_star_data['R'].std(),
            'mean_iterations': r_star_data['iterations'].mean() if 'iterations' in r_star_data.columns else None,
            'scaling_data': r_star_data[['k', 'k_numeric', 'R', 'iterations', 'mr_calls', 'elapsed_ms']].to_dict('records')
        }
        
        return analysis

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description='Wave-Knob Prime Scanner Harness')
    
    # Input options
    parser.add_argument('--k', type=str, help='Single k value to test')
    parser.add_argument('--k-range', type=str, help='k range: start,stop,count (log-spaced)')
    parser.add_argument('--binary', type=str, help='Path to z5d_mersenne binary')
    
    # Experiment modes
    parser.add_argument('--r-sweep', action='store_true', help='Run R-sweep experiment')
    parser.add_argument('--auto-tune', action='store_true', help='Run auto-tune experiment')
    parser.add_argument('--demo', action='store_true', help='Run quick demo')
    
    # R-sweep parameters
    parser.add_argument('--window-range', type=str, default='2,50,10', 
                       help='Window range: start,stop,step (default: 2,50,10)')
    parser.add_argument('--step-range', type=str, default='1,10,2',
                       help='Step range: start,stop,step (default: 1,10,2)')
    
    # Scanner parameters  
    parser.add_argument('--wheel', type=int, default=210, choices=[30, 210],
                       help='Wheel modulus (default: 210)')
    parser.add_argument('--precision', type=int, default=4096,
                       help='MPFR precision in bits (default: 4096)')
    parser.add_argument('--mr-rounds', type=int, default=50,
                       help='Miller-Rabin rounds (default: 50)')
    
    # Output options
    parser.add_argument('--output', type=str, help='Output JSON file')
    parser.add_argument('--plot', action='store_true', help='Generate plots')
    parser.add_argument('--plot-dir', type=str, default='plots', help='Plot output directory')
    
    args = parser.parse_args()
    
    # Create harness
    try:
        harness = WaveKnobHarness(args.binary)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    # Determine experiment type and parameters
    if args.demo:
        # Quick demo mode
        print("Running Wave-Knob demo...")
        k_values = ['1000', '10000']
        df_auto = harness.auto_tune_experiment(k_values, wheel=args.wheel, 
                                              precision=args.precision, mr_rounds=args.mr_rounds)
        print("\nAuto-tune results:")
        print(df_auto[['k', 'R', 'prime_count', 'iterations', 'locked']].to_string(index=False))
        
        # Quick R-sweep for k=1000
        df_sweep = harness.r_sweep_experiment('1000', (2, 20, 3), (1, 6, 1),
                                            wheel=args.wheel, precision=args.precision, mr_rounds=args.mr_rounds)
        print(f"\nR-sweep results for k=1000:")
        print(df_sweep[['window', 'step', 'R', 'prime_count']].to_string(index=False))
        return 0
    
    # Parse k values
    k_values = []
    if args.k:
        k_values = [args.k]
    elif args.k_range:
        try:
            start, stop, count = args.k_range.split(',')
            k_vals = np.logspace(np.log10(float(start)), np.log10(float(stop)), int(count))
            k_values = [f'{k:.0e}' for k in k_vals]
        except:
            print("Error: Invalid k-range format. Use: start,stop,count")
            return 1
    else:
        print("Error: Must specify --k, --k-range, or --demo")
        return 1
    
    # Run experiments
    results = {}
    
    if args.auto_tune:
        print("Running auto-tune experiment...")
        df_auto = harness.auto_tune_experiment(k_values, wheel=args.wheel,
                                              precision=args.precision, mr_rounds=args.mr_rounds)
        results['auto_tune'] = df_auto.to_dict('records')
        
        # Analyze R* scaling
        scaling_analysis = harness.analyze_r_star_scaling(df_auto)
        results['r_star_analysis'] = scaling_analysis
        
        print("\nR* Scaling Analysis:")
        if 'error' not in scaling_analysis:
            print(f"  Points: {scaling_analysis['n_points']}")
            print(f"  R* range: {scaling_analysis['r_star_range']}")
            print(f"  Mean R*: {scaling_analysis['mean_r_star']:.3f} ± {scaling_analysis['std_r_star']:.3f}")
    
    if args.r_sweep:
        if len(k_values) > 1:
            print("Warning: R-sweep only supports single k value. Using first k value.")
        k = k_values[0]
        
        # Parse ranges
        try:
            window_range = tuple(map(int, args.window_range.split(',')))
            step_range = tuple(map(int, args.step_range.split(',')))
        except:
            print("Error: Invalid range format. Use: start,stop,step")
            return 1
        
        print(f"Running R-sweep experiment for k={k}...")
        df_sweep = harness.r_sweep_experiment(k, window_range, step_range,
                                            wheel=args.wheel, precision=args.precision, mr_rounds=args.mr_rounds)
        results['r_sweep'] = df_sweep.to_dict('records')
        
        # Generate plots if requested
        if args.plot:
            plot_dir = Path(args.plot_dir)
            plot_dir.mkdir(exist_ok=True)
            
            harness.plot_r_sweep_heatmap(df_sweep, plot_dir / f'heatmap_k{k}.png')
            harness.plot_r_curve(df_sweep, plot_dir / f'rcurve_k{k}.png')
    
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved: {args.output}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())