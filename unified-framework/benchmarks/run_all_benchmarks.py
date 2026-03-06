#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run All Benchmarks - Comprehensive Validation Suite
===================================================

Executes all benchmark scripts and generates a summary report.

Usage:
    python benchmarks/run_all_benchmarks.py

Output:
    - Console output with all benchmark results
    - Summary statistics and validation status
"""

import sys
import os
import time
import json
import platform
import subprocess
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")


def print_separator():
    """Print a separator line"""
    print("\n" + "-" * 80 + "\n")


def run_benchmark(name, module_name):
    """
    Run a single benchmark and capture results

    Args:
        name: Display name of the benchmark
        module_name: Module name to import

    Returns:
        dict with execution results
    """
    print_header(f"Running: {name}")

    start_time = time.time()
    success = False
    error_msg = None

    try:
        # Import and run the benchmark
        module = __import__(f'benchmarks.{module_name}', fromlist=['main'])
        module.main()
        success = True
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error running {name}: {error_msg}")
        import traceback
        traceback.print_exc()

    end_time = time.time()
    duration = end_time - start_time

    return {
        'name': name,
        'success': success,
        'duration': duration,
        'error': error_msg
    }

def run_benchmark_with_args(name, module_name, args):
    """
    Run a single benchmark with command line arguments

    Args:
        name: Display name of the benchmark
        module_name: Module name to import
        args: List of command line arguments

    Returns:
        dict with execution results
    """
    print_header(f"Running: {name}")

    start_time = time.time()
    success = False
    error_msg = None

    try:
        # Import the benchmark module
        module = __import__(f'benchmarks.{module_name}', fromlist=['main'])
        # Run with arguments by temporarily replacing sys.argv
        original_argv = sys.argv
        sys.argv = [f'benchmarks/{module_name}.py'] + args
        try:
            module.main()
            success = True
        finally:
            sys.argv = original_argv
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error running {name}: {error_msg}")
        import traceback
        traceback.print_exc()

    end_time = time.time()
    duration = end_time - start_time

    return {
        'name': name,
        'success': success,
        'duration': duration,
        'error': error_msg
    }


def generate_summary_report(results, out_dir=None, jsonl_file=None, sys_info=None, start_time=None, seed=None):
    """
    Generate a summary report of all benchmark results

    Args:
        results: List of result dictionaries from run_benchmark
        out_dir: Output directory for results
        jsonl_file: JSONL output file path
        sys_info: System information dict
        start_time: Benchmark start time
        seed: Random seed used
    """
    end_time = datetime.now()

    # Default values
    if sys_info is None:
        sys_info = {'commit_sha': 'unknown', 'hostname': 'unknown', 'os': 'unknown',
                   'python_version': 'unknown', 'numpy_version': 'unknown'}
    if start_time is None:
        start_time = end_time
    if seed is None:
        seed = 42

    print_header("Benchmark Summary Report")

    # Overall statistics
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful
    total_time = sum(r['duration'] for r in results)

    print(f"Total benchmarks: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Success rate: {successful/total*100:.1f}%")

    # Individual results
    print_separator()
    print("Individual Benchmark Results:")
    print(f"\n{'Benchmark':<50} {'Status':<10} {'Time (s)':<12}")
    print("-" * 80)

    for result in results:
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"{result['name']:<50} {status:<10} {result['duration']:>10.2f}")
        if not result['success'] and result['error']:
            print(f"  Error: {result['error'][:60]}...")

    # Validation summary
    print_separator()
    print("Validation Summary:")
    print()

    if successful == total:
        print("✓ All benchmarks completed successfully!")
        print("  - Stadlmann integration validated")
        print("  - Geodesic density enhancement tested")
        print("  - Conical flow models benchmarked")
    else:
        print(f"⚠ {failed} benchmark(s) failed. Review output above for details.")

    # Determine output directory
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        base_dir = out_dir
    else:
        base_dir = os.path.dirname(__file__)

    # Save human-readable results
    report_file = os.path.join(base_dir, 'benchmark_results.txt')
    try:
        with open(report_file, 'w') as f:
            # Repro header
            f.write("unified-framework-benchmarks v1 | ")
            f.write(f"sha={sys_info['commit_sha']} | ")
            f.write(f"seed={seed} | ")
            f.write(f"py={sys_info['python_version']} | ")
            f.write(f"np={sys_info['numpy_version']} | ")
            f.write(f"os={sys_info['os']} | ")
            f.write(f"ts={start_time.strftime('%Y%m%d_%H%M%S')}\n\n")

            f.write("Z Framework Benchmark Results\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Date: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total benchmarks: {total}\n")
            f.write(f"Successful: {successful}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Total time: {total_time:.2f} seconds\n")
            f.write(f"Success rate: {successful/total*100:.1f}%\n\n")

            f.write("Individual Results:\n")
            f.write("-" * 80 + "\n")
            for result in results:
                status = "PASS" if result['success'] else "FAIL"
                f.write(f"{result['name']:<50} {status:<10} {result['duration']:>10.2f}s\n")
                if not result['success'] and result['error']:
                    f.write(f"  Error: {result['error']}\n")

        print(f"\nResults saved to: {report_file}")
    except Exception as e:
        print(f"\nWarning: Could not save results to file: {e}")

    # Save structured JSONL results
    if jsonl_file:
        try:
            jsonl_path = os.path.join(base_dir, jsonl_file) if not os.path.isabs(jsonl_file) else jsonl_file
            with open(jsonl_path, 'w') as f:
                for result in results:
                    record = {
                        'timestamp': end_time.isoformat(),
                        'benchmark': result['name'],
                        'success': result['success'],
                        'duration': result['duration'],
                        'error': result['error'],
                        'commit_sha': sys_info['commit_sha'],
                        'hostname': sys_info['hostname'],
                        'os': sys_info['os'],
                        'python_version': sys_info['python_version'],
                        'numpy_version': sys_info['numpy_version'],
                        'seed': seed,
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat()
                    }
                    f.write(json.dumps(record) + '\n')
            print(f"Structured results saved to: {jsonl_path}")
        except Exception as e:
            print(f"\nWarning: Could not save JSONL results: {e}")


def get_system_info():
    """Get system information for metadata"""
    try:
        commit_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    except:
        commit_sha = "unknown"

    return {
        'commit_sha': commit_sha,
        'hostname': platform.node(),
        'os': f"{platform.system()} {platform.release()}",
        'python_version': platform.python_version(),
        'numpy_version': np.__version__ if 'np' in globals() else "unknown"
    }

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Run All Benchmarks')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducible results')
    parser.add_argument('--max-n', type=int, default=1000000, help='Maximum N for prime generation')
    parser.add_argument('--k-min', type=int, default=10000, help='Minimum k value for testing')
    parser.add_argument('--k-max', type=int, default=1000000, help='Maximum k value for testing')
    parser.add_argument('--levels', type=str, default=None, help='Comma-separated levels for testing')
    parser.add_argument('--verify-claims', action='store_true', help='Verify specific numeric claims')
    parser.add_argument('--out', type=str, help='Output directory for results')
    parser.add_argument('--jsonl', type=str, help='JSONL output file for structured results')

    args = parser.parse_args()

    print_header("Z Framework Comprehensive Benchmark Suite")
    print("Starting benchmark execution...")
    start_time = datetime.now()
    print(f"Timestamp: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Random seed: {args.seed}")

    # Get system info
    sys_info = get_system_info()
    print(f"Commit SHA: {sys_info['commit_sha']}")
    print(f"Python: {sys_info['python_version']}")

    # Parse levels if provided
    levels_arg = None
    if args.levels:
        try:
            levels_arg = [float(x.strip()) for x in args.levels.split(',')]
        except:
            print("Warning: Could not parse levels argument")

    # Define benchmarks to run with arguments
    benchmark_configs = [
        {
            'name': "Stadlmann Extended Validation",
            'module': "stadlmann_extended_validation",
            'args': ['--seed', str(args.seed), '--max-n', str(args.max_n),
                    '--k-min', str(args.k_min), '--k-max', str(args.k_max)] +
                   (['--verify-claims'] if args.verify_claims else [])
        },
        {
            'name': "Geodesic Density Enhancement",
            'module': "geodesic_density_benchmark",
            'args': ['--seed', str(args.seed), '--max-n', str(args.max_n),
                    '--k-min', str(args.k_min), '--k-max', str(args.k_max)] +
                   (['--verify-claims'] if args.verify_claims else []) +
                   (['--levels'] + [str(l) for l in levels_arg] if levels_arg else [])
        },
        {
            'name': "Conical Flow Speedup",
            'module': "conical_flow_speedup_benchmark",
            'args': ['--seed', str(args.seed), '--max-n', str(args.max_n),
                    '--k-min', str(args.k_min), '--k-max', str(args.k_max)] +
                   (['--verify-claims'] if args.verify_claims else []) +
                   (['--levels'] + [str(l) for l in levels_arg] if levels_arg else [])
        },
    ]

    # Run all benchmarks
    results = []
    for config in benchmark_configs:
        result = run_benchmark_with_args(config['name'], config['module'], config['args'])
        results.append(result)

        if result['success']:
            print(f"\n✓ {config['name']} completed in {result['duration']:.2f}s")
        else:
            print(f"\n✗ {config['name']} failed after {result['duration']:.2f}s")

    # Generate summary
    generate_summary_report(results, args.out, args.jsonl, sys_info, start_time, args.seed)

    print_header("Benchmark Suite Complete")

    # Exit with non-zero code if any benchmark failed
    if any(not r['success'] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark suite interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error in benchmark suite: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
