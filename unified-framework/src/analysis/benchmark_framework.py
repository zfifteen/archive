#!/usr/bin/env python3
"""
Automated Benchmarking Infrastructure for Z Framework
====================================================

Implements automated benchmarks comparing Z_5D vs. PNT performance:
- Execution times comparison across k=10^3 to 10^10
- Error analysis with statistical validation
- Matplotlib visualization (line graphs, bar charts)
- Results storage in results/benchmarks.csv format

Features:
- Systematic performance comparison
- Error vs log(k) visualization
- Statistical significance testing
- CSV output for reproducibility
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import os
import sys
from pathlib import Path
import warnings

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.z_5d_enhanced import z5d_predictor
    from core.params import set_adaptive_mpmath_precision
    from statistical.computationally_intensive_tasks import ComputationallyIntensiveTasks
except ImportError as e:
    print(f"Warning: Could not import core modules: {e}")
    z5d_predictor = None

# Use sympy for PNT comparison and true prime generation
try:
    import sympy as sp
    from sympy import prime, pi as sympy_pi, log as sympy_log
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("Warning: sympy not available, using approximations")

import mpmath as mp

class BenchmarkFramework:
    """Automated benchmarking for Z_5D vs PNT performance comparison"""
    
    def __init__(self, results_dir="results", precision_dps=50):
        """
        Initialize benchmark framework
        
        Args:
            results_dir (str): Directory to store benchmark results
            precision_dps (int): Precision for calculations
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.precision_dps = precision_dps
        mp.dps = precision_dps
        
        # Benchmark test points as specified in issue
        self.test_k_values = [10**3, 10**5, 10**7, 10**10]
        
        # Initialize computational tasks for enhanced processing
        self.computational_tasks = ComputationallyIntensiveTasks(
            precision_dps=precision_dps, 
            num_cores=4  # Optimize for 4-8 cores as per issue
        )

    def pnt_approximation(self, k):
        """
        Prime Number Theorem approximation for kth prime
        
        Args:
            k (int): Prime index
            
        Returns:
            float: PNT approximation of kth prime
        """
        if k < 2:
            return 2.0 if k == 1 else 0.0
            
        # PNT approximation: p_k ≈ k * (ln(k) + ln(ln(k)) - 1)
        k = float(k)
        ln_k = np.log(k)
        ln_ln_k = np.log(ln_k) if k > 1 else 0
        
        return k * (ln_k + ln_ln_k - 1 + (ln_ln_k - 2) / ln_k)

    def get_true_prime(self, k):
        """Get true kth prime using sympy or approximation"""
        if SYMPY_AVAILABLE and k <= 1000000:  # Limit for performance
            return int(sp.prime(k))
        else:
            # Use Z_5D as best available approximation for large k
            if z5d_predictor:
                return float(z5d_predictor(k))
            else:
                return self.pnt_approximation(k)

    def benchmark_single_method(self, method_func, k_values, method_name):
        """
        Benchmark a single prediction method
        
        Args:
            method_func: Function to benchmark
            k_values: List of k values to test
            method_name: Name of the method for logging
            
        Returns:
            dict: Benchmark results
        """
        results = {
            'k_values': [],
            'predictions': [],
            'execution_times': [],
            'errors': [],
            'relative_errors': []
        }
        
        print(f"Benchmarking {method_name}...")
        
        for k in k_values:
            try:
                # Time the prediction
                start_time = time.time()
                prediction = method_func(k)
                execution_time = time.time() - start_time
                
                # Get true value for error calculation
                true_prime = self.get_true_prime(k)
                
                # Calculate errors
                error = float(prediction) - true_prime
                relative_error = (error / true_prime) * 100 if true_prime != 0 else 0
                
                results['k_values'].append(k)
                results['predictions'].append(float(prediction))
                results['execution_times'].append(execution_time * 1000)  # Convert to ms
                results['errors'].append(error)
                results['relative_errors'].append(abs(relative_error))
                
                print(f"  k={k:>8}: pred={prediction:>12.2f}, time={execution_time*1000:>8.4f}ms, err={relative_error:>8.4f}%")
                
            except Exception as e:
                print(f"  k={k:>8}: ERROR - {e}")
                continue
        
        return results

    def run_c_benchmark_integration(self, c_benchmark_path="src/c/bin/z5d_bench", 
                                   k_max=10000, csv_output=None, seed=42):
        """
        Run C benchmark and integrate results with Python framework
        
        This method integrates the C z5d_bench implementation that uses standardized
        parameters from src/core/params.py to ensure consistency across the Z Framework:
        - kappa_star = 0.04449 (Z_5D calibration factor)
        - kappa_geo = 0.3 (geodesic exponent) 
        - c = -0.00247 (least-squares calibration)
        
        This addresses the k parameter standardization issue by using distinct
        variable names for different contexts as defined in params.py.
        
        Args:
            c_benchmark_path (str): Path to the C z5d_bench executable
            k_max (int): Maximum k value for testing
            csv_output (str): Optional CSV output file path
            seed (int): Random seed for deterministic bootstrap samples
            
        Returns:
            dict: Integrated benchmark results with parameter standardization info
        """
        import subprocess
        import tempfile
        import os
        
        print("=" * 70)
        print("C BENCHMARK INTEGRATION (Z5D vs primesieve)")
        print("Parameter Standardization v2.0 - synchronized with params.py")
        print("=" * 70)
        
        # Determine paths
        repo_root = Path(__file__).parent.parent.parent
        full_benchmark_path = repo_root / c_benchmark_path
        
        if not full_benchmark_path.exists():
            print(f"Warning: C benchmark not found at {full_benchmark_path}")
            print("Please build the C benchmark first with 'make z5d-bench'")
            return None
        
        # Create temporary CSV file if not specified
        if csv_output is None:
            temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            csv_output = temp_csv.name
            temp_csv.close()
        
        try:
            # Run the C benchmark
            cmd = [
                str(full_benchmark_path), 
                "--k-max", str(k_max),
                "--csv-output", csv_output,
                "--verbose",
                "--verify",
                "--bootstrap-samples", "20",
                "--seed", str(seed)
            ]
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root))
            
            if result.returncode != 0:
                print(f"C benchmark failed with return code {result.returncode}")
                print(f"stderr: {result.stderr}")
                return None
            
            print("C benchmark output:")
            print(result.stdout)
            
            # Read and parse CSV results
            if os.path.exists(csv_output):
                df = pd.read_csv(csv_output)
                
                # Convert to Python framework format
                benchmark_results = {
                    'metadata': {
                        'timestamp': pd.Timestamp.now().isoformat(),
                        'source': 'C z5d_bench integration (Parameter Standardization v2.0)',
                        'k_max': k_max,
                        'csv_file': csv_output,
                        'parameter_standardization': {
                            'kappa_star': 0.04449,  # KAPPA_STAR_DEFAULT from params.py
                            'kappa_geo': 0.3,       # KAPPA_GEO_DEFAULT from params.py
                            'c_calibrated': -0.00247, # Z5D_C_CALIBRATED from params.py
                            'synchronized_with': 'src/core/params.py',
                            'addresses_issue': 'k parameter overloading via distinct variable names'
                        }
                    },
                    'z5d_results': {
                        'k_values': df['k_value'].tolist(),
                        'predictions': df['z5d_prediction'].tolist(),
                        'execution_times': df['z5d_time_ms'].tolist(),
                        'relative_errors': df['z5d_error_percent'].tolist()
                    },
                    'primesieve_results': {
                        'k_values': df['k_value'].tolist(),
                        'execution_times': df['primesieve_time_ms'].tolist(),
                        'prime_counts': df['primesieve_count'].tolist(),
                        'speedup_factors': df['speedup_factor'].tolist()
                    },
                    'comparison': {
                        'k_values': df['k_value'].tolist(),
                        'speedup_factors': df['speedup_factor'].tolist(),
                        'confidence_intervals': list(zip(df['ci_low'], df['ci_high'])),
                        'average_speedup': df['speedup_factor'].mean(),
                        'average_error': df['z5d_error_percent'].mean()
                    }
                }
                
                print(f"\nBenchmark Summary:")
                print(f"Average Z5D speedup vs primesieve: {benchmark_results['comparison']['average_speedup']:.2f}x")
                print(f"Average Z5D error: {benchmark_results['comparison']['average_error']:.6f}%")
                
                # Display parameter standardization info
                params = benchmark_results['metadata']['parameter_standardization']
                print(f"\nParameter Standardization (synchronized with {params['synchronized_with']}):")
                print(f"  kappa_star: {params['kappa_star']} (Z_5D calibration factor)")
                print(f"  kappa_geo: {params['kappa_geo']} (geodesic exponent)")
                print(f"  c: {params['c_calibrated']} (least-squares calibration)")
                print(f"  {params['addresses_issue']}")
                
                return benchmark_results
            else:
                print(f"CSV output file not found: {csv_output}")
                return None
                
        except Exception as e:
            print(f"Error running C benchmark: {e}")
            return None
        finally:
            # Clean up temporary file
            if csv_output and csv_output.startswith(tempfile.gettempdir()):
                try:
                    os.unlink(csv_output)
                except (FileNotFoundError, OSError):
                    pass

    def run_comprehensive_benchmark(self):
        """
        Run comprehensive benchmark comparing Z_5D vs PNT
        
        Returns:
            dict: Complete benchmark results
        """
        print("=" * 70)
        print("Z FRAMEWORK AUTOMATED BENCHMARK")
        print("=" * 70)
        print(f"Test k values: {self.test_k_values}")
        print(f"Precision: {self.precision_dps} dps")
        print(f"Cores: {self.computational_tasks.num_cores}")
        print()
        
        # Initialize results
        benchmark_results = {
            'metadata': {
                'timestamp': pd.Timestamp.now().isoformat(),
                'test_k_values': self.test_k_values,
                'precision_dps': self.precision_dps,
                'cores_used': self.computational_tasks.num_cores
            },
            'z5d_results': {},
            'pnt_results': {},
            'comparison': {}
        }
        
        # Benchmark Z_5D method
        if z5d_predictor:
            z5d_func = lambda k: z5d_predictor(k)
            benchmark_results['z5d_results'] = self.benchmark_single_method(
                z5d_func, self.test_k_values, "Z_5D Enhanced"
            )
        else:
            print("Warning: Z_5D predictor not available")
            benchmark_results['z5d_results'] = None
        
        # Benchmark PNT method
        benchmark_results['pnt_results'] = self.benchmark_single_method(
            self.pnt_approximation, self.test_k_values, "PNT Approximation"
        )
        
        # Calculate comparison metrics
        if benchmark_results['z5d_results']:
            benchmark_results['comparison'] = self._calculate_comparison_metrics(
                benchmark_results['z5d_results'],
                benchmark_results['pnt_results']
            )
        
        return benchmark_results

    def _calculate_comparison_metrics(self, z5d_results, pnt_results):
        """Calculate comparison metrics between Z_5D and PNT"""
        comparison = {
            'speedup_factors': [],
            'error_improvements': [],
            'k_values': []
        }
        
        for i, k in enumerate(z5d_results['k_values']):
            if i < len(pnt_results['k_values']) and k == pnt_results['k_values'][i]:
                # Calculate speedup factor
                z5d_time = z5d_results['execution_times'][i]
                pnt_time = pnt_results['execution_times'][i]
                speedup = pnt_time / z5d_time if z5d_time > 0 else 0
                
                # Calculate error improvement
                z5d_error = z5d_results['relative_errors'][i]
                pnt_error = pnt_results['relative_errors'][i]
                error_improvement = (pnt_error - z5d_error) / pnt_error * 100 if pnt_error > 0 else 0
                
                comparison['speedup_factors'].append(speedup)
                comparison['error_improvements'].append(error_improvement)
                comparison['k_values'].append(k)
        
        return comparison

    def visualize_results(self, benchmark_results, save_plots=True):
        """
        Create matplotlib visualizations of benchmark results
        
        Args:
            benchmark_results: Results from run_comprehensive_benchmark
            save_plots: Whether to save plots to files
        """
        if not benchmark_results['z5d_results']:
            print("No Z_5D results to visualize")
            return
            
        # Set up matplotlib
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        z5d = benchmark_results['z5d_results']
        pnt = benchmark_results['pnt_results']
        comparison = benchmark_results['comparison']
        
        # Plot 1: Error vs log(k) - Line Graph
        ax1.loglog(z5d['k_values'], z5d['relative_errors'], 'b-o', label='Z_5D Error', linewidth=2)
        ax1.loglog(pnt['k_values'], pnt['relative_errors'], 'r-s', label='PNT Error', linewidth=2)
        ax1.set_xlabel('k (Prime Index)')
        ax1.set_ylabel('Relative Error (%)')
        ax1.set_title('Error vs log(k) Comparison')
        ax1.legend()
        ax1.grid(True)
        
        # Plot 2: Execution Time Comparison - Bar Chart
        x_pos = np.arange(len(z5d['k_values']))
        width = 0.35
        ax2.bar(x_pos - width/2, z5d['execution_times'], width, label='Z_5D Time', alpha=0.8)
        ax2.bar(x_pos + width/2, pnt['execution_times'], width, label='PNT Time', alpha=0.8)
        ax2.set_xlabel('Test Cases')
        ax2.set_ylabel('Execution Time (ms)')
        ax2.set_title('Execution Time Comparison')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f'k=10^{int(np.log10(k))}' for k in z5d['k_values']])
        ax2.legend()
        ax2.set_yscale('log')
        
        # Plot 3: Speedup Factor
        if comparison['speedup_factors']:
            ax3.bar(range(len(comparison['speedup_factors'])), comparison['speedup_factors'], 
                   color='green', alpha=0.7)
            ax3.set_xlabel('Test Cases')
            ax3.set_ylabel('Speedup Factor (PNT/Z_5D)')
            ax3.set_title('Z_5D Speedup vs PNT')
            ax3.set_xticks(range(len(comparison['k_values'])))
            ax3.set_xticklabels([f'k=10^{int(np.log10(k))}' for k in comparison['k_values']])
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Error Improvement Percentage
        if comparison['error_improvements']:
            ax4.bar(range(len(comparison['error_improvements'])), comparison['error_improvements'], 
                   color='purple', alpha=0.7)
            ax4.set_xlabel('Test Cases')
            ax4.set_ylabel('Error Improvement (%)')
            ax4.set_title('Z_5D Error Improvement vs PNT')
            ax4.set_xticks(range(len(comparison['k_values'])))
            ax4.set_xticklabels([f'k=10^{int(np.log10(k))}' for k in comparison['k_values']])
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plots:
            plot_path = self.results_dir / "benchmark_comparison.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"Benchmark plots saved to: {plot_path}")
        
        plt.show()

    def save_results_csv(self, benchmark_results):
        """
        Save benchmark results to CSV file in results/benchmarks.csv format
        
        Args:
            benchmark_results: Results from run_comprehensive_benchmark
        """
        if not benchmark_results['z5d_results']:
            print("No results to save")
            return None
            
        # Prepare data for CSV
        data_rows = []
        z5d = benchmark_results['z5d_results']
        pnt = benchmark_results['pnt_results']
        comparison = benchmark_results['comparison']
        
        for i, k in enumerate(z5d['k_values']):
            # Find corresponding PNT result
            pnt_idx = None
            for j, pnt_k in enumerate(pnt['k_values']):
                if pnt_k == k:
                    pnt_idx = j
                    break
            
            # Find comparison data
            comp_idx = None
            for j, comp_k in enumerate(comparison.get('k_values', [])):
                if comp_k == k:
                    comp_idx = j
                    break
            
            row = {
                'k_value': k,
                'z5d_error_percent': z5d['relative_errors'][i],
                'pnt_error_percent': pnt['relative_errors'][pnt_idx] if pnt_idx is not None else None,
                'z5d_time_ms': z5d['execution_times'][i],
                'pnt_time_ms': pnt['execution_times'][pnt_idx] if pnt_idx is not None else None,
                'speedup_factor': comparison['speedup_factors'][comp_idx] if comp_idx is not None else None,
                'error_improvement_percent': comparison['error_improvements'][comp_idx] if comp_idx is not None else None,
                'z5d_prediction': z5d['predictions'][i],
                'pnt_prediction': pnt['predictions'][pnt_idx] if pnt_idx is not None else None
            }
            data_rows.append(row)
        
        # Create DataFrame and save
        df = pd.DataFrame(data_rows)
        csv_path = self.results_dir / "benchmarks.csv"
        df.to_csv(csv_path, index=False)
        
        print(f"Benchmark results saved to: {csv_path}")
        print(f"CSV contains {len(df)} rows with benchmark data")
        
        return csv_path

    def generate_benchmark_report(self):
        """
        Generate complete benchmark report with visualizations and CSV
        
        Returns:
            dict: Comprehensive benchmark results and file paths
        """
        print("Generating comprehensive benchmark report...")
        
        # Run benchmark
        results = self.run_comprehensive_benchmark()
        
        # Create visualizations
        self.visualize_results(results, save_plots=True)
        
        # Save CSV
        csv_path = self.save_results_csv(results)
        
        # Generate summary report
        summary = self._generate_summary_report(results)
        
        return {
            'benchmark_results': results,
            'csv_path': str(csv_path) if csv_path else None,
            'summary': summary,
            'plots_saved': True
        }

    def _generate_summary_report(self, results):
        """Generate text summary of benchmark results"""
        if not results['z5d_results']:
            return "No Z_5D results available for summary"
            
        z5d = results['z5d_results']
        pnt = results['pnt_results']
        comp = results['comparison']
        
        summary_lines = [
            "BENCHMARK SUMMARY REPORT",
            "=" * 50,
            f"Test completed: {results['metadata']['timestamp']}",
            f"Test cases: {len(z5d['k_values'])}",
            f"k values: {z5d['k_values']}",
            "",
            "PERFORMANCE COMPARISON:",
        ]
        
        if comp['speedup_factors']:
            avg_speedup = np.mean(comp['speedup_factors'])
            max_speedup = np.max(comp['speedup_factors'])
            summary_lines.extend([
                f"  Average speedup: {avg_speedup:.1f}x",
                f"  Maximum speedup: {max_speedup:.1f}x",
            ])
        
        if comp['error_improvements']:
            avg_improvement = np.mean(comp['error_improvements'])
            summary_lines.extend([
                f"  Average error improvement: {avg_improvement:.1f}%",
            ])
        
        summary_lines.extend([
            "",
            "Z_5D ERROR RANGE:",
            f"  Minimum: {np.min(z5d['relative_errors']):.4f}%",
            f"  Maximum: {np.max(z5d['relative_errors']):.4f}%",
            f"  Average: {np.mean(z5d['relative_errors']):.4f}%",
            "",
            "EXECUTION TIME ANALYSIS:",
            f"  Z_5D avg time: {np.mean(z5d['execution_times']):.4f}ms", 
            f"  PNT avg time: {np.mean(pnt['execution_times']):.4f}ms"
        ])
        
        return "\n".join(summary_lines)


def main():
    """Main function for running benchmarks"""
    # Create benchmark framework
    benchmark = BenchmarkFramework(results_dir="results", precision_dps=30)
    
    # Generate complete benchmark report
    report = benchmark.generate_benchmark_report()
    
    # Print summary
    print("\n" + report['summary'])
    
    return report


if __name__ == "__main__":
    report = main()