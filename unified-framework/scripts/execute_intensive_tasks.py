#!/usr/bin/env python3
"""
Execute Computationally Intensive Research Tasks
==============================================

Main execution script for the 4 computationally intensive research tasks:
1. Zeta Zero Expansion (1000+ Zeros)
2. Asymptotic Extrapolation to 10^12
3. Lorentz Analogy Frame Shift Analysis
4. Error Oscillation CSV Generation (1000 Bands)

Usage:
    python3 execute_intensive_tasks.py [--task=1,2,3,4] [--precision=50] [--cores=auto]

Examples:
    python3 execute_intensive_tasks.py --task=3 --precision=25  # Run only Task 3
    python3 execute_intensive_tasks.py                          # Run all tasks
"""

import sys
import os
import argparse
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from statistical.computationally_intensive_tasks import ComputationallyIntensiveTasks


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Execute computationally intensive research tasks for Z Framework"
    )
    
    parser.add_argument(
        '--task', 
        type=str, 
        default='1,2,3,4',
        help='Comma-separated list of tasks to run (1,2,3,4). Default: all tasks'
    )
    
    parser.add_argument(
        '--precision', 
        type=int, 
        default=50,
        help='Decimal precision for mpmath (default: 50)'
    )
    
    parser.add_argument(
        '--cores', 
        type=str, 
        default='auto',
        help='Number of CPU cores to use (default: auto)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Output directory for results (default: current directory)'
    )
    
    parser.add_argument(
        '--quick-test',
        action='store_true',
        help='Run with reduced parameters for testing'
    )
    
    return parser.parse_args()


def run_task1(processor, quick_test=False):
    """Run Task 1: Zeta Zero Expansion."""
    import numpy as np
    
    print("Starting Task 1: Zeta Zero Expansion (1000+ Zeros)")
    print("=" * 50)
    
    if quick_test:
        x_range = np.logspace(7, 10, 100)
        print("Quick test mode: using 100 points from 10^7 to 10^10")
    else:
        x_range = np.logspace(7, 13, 1000)
        print("Production mode: using 1000 points from 10^7 to 10^13")
    
    start_time = time.time()
    results = processor.task1_zeta_expansion(x_range=x_range)
    elapsed = time.time() - start_time
    
    print(f"\nTask 1 completed in {elapsed:.2f} seconds")
    return results


def run_task2(processor, quick_test=False):
    """Run Task 2: Asymptotic Extrapolation."""
    import numpy as np
    
    print("Starting Task 2: Asymptotic Extrapolation to 10^12")
    print("=" * 50)
    
    if quick_test:
        k_range = np.logspace(7, 10, 100)
        print("Quick test mode: using 100 points from 10^7 to 10^10")
    else:
        k_range = np.logspace(7, 12, 1000)
        print("Production mode: using 1000 points from 10^7 to 10^12")
    
    start_time = time.time()
    results = processor.task2_asymptotic_extrapolation(k_range=k_range)
    elapsed = time.time() - start_time
    
    print(f"\nTask 2 completed in {elapsed:.2f} seconds")
    return results


def run_task3(processor, quick_test=False):
    """Run Task 3: Lorentz Analogy Frame Shift Analysis."""
    import numpy as np
    
    print("Starting Task 3: Lorentz Analogy Frame Shift Analysis")
    print("=" * 50)
    
    if quick_test:
        n_range = np.logspace(5, 6, 200)
        print("Quick test mode: using 200 points from 10^5 to 10^6")
    else:
        n_range = np.logspace(5, 7, 1000)
        print("Production mode: using 1000 points from 10^5 to 10^7")
    
    start_time = time.time()
    results = processor.task3_lorentz_analogy(n_range=n_range)
    elapsed = time.time() - start_time
    
    print(f"\nTask 3 completed in {elapsed:.2f} seconds")
    return results


def run_task4(processor, output_dir, quick_test=False):
    """Run Task 4: Error Oscillation CSV Generation."""
    print("Starting Task 4: Error Oscillation CSV Generation")
    print("=" * 50)
    
    if quick_test:
        num_bands = 100
        output_file = os.path.join(output_dir, 'error_oscillations_test.csv')
        print("Quick test mode: generating 100 bands")
    else:
        num_bands = 1000
        output_file = os.path.join(output_dir, 'error_oscillations.csv')
        print("Production mode: generating 1000 bands")
    
    start_time = time.time()
    results = processor.task4_error_oscillation_csv(
        output_file=os.path.basename(output_file),
        num_bands=num_bands
    )
    elapsed = time.time() - start_time
    
    print(f"\nTask 4 completed in {elapsed:.2f} seconds")
    return results


def save_results(results, output_dir):
    """Save results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(output_dir, f'intensive_tasks_results_{timestamp}.json')
    
    # Convert numpy arrays to lists for JSON serialization
    def convert_for_json(obj):
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        elif hasattr(obj, 'item'):
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_for_json(item) for item in obj]
        else:
            return obj
    
    results_clean = convert_for_json(results)
    
    with open(results_file, 'w') as f:
        json.dump(results_clean, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    return results_file


def main():
    """Main execution function."""
    import numpy as np
    
    args = parse_args()
    
    print("Computationally Intensive Research Tasks for Z Framework")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print(f"Tasks to run: {args.task}")
    print(f"Precision: {args.precision} decimal places")
    print(f"CPU cores: {args.cores}")
    print(f"Output directory: {args.output_dir}")
    print(f"Quick test mode: {args.quick_test}")
    print()
    
    # Parse tasks
    tasks_to_run = [int(t.strip()) for t in args.task.split(',')]
    
    # Parse cores
    if args.cores == 'auto':
        num_cores = None
    else:
        num_cores = int(args.cores)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize processor
    print("Initializing computational processor...")
    start_init = time.time()
    processor = ComputationallyIntensiveTasks(
        precision_dps=args.precision,
        num_cores=num_cores
    )
    init_time = time.time() - start_init
    print(f"Processor initialized in {init_time:.2f} seconds")
    print(f"Using {processor.num_cores} CPU cores")
    print(f"Loaded {len(processor.extended_zeros)} zeta zeros")
    print()
    
    # Run tasks
    all_results = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'precision_dps': args.precision,
            'num_cores': processor.num_cores,
            'zeta_zeros_count': len(processor.extended_zeros),
            'quick_test': args.quick_test,
            'tasks_requested': tasks_to_run
        }
    }
    
    total_start_time = time.time()
    
    # Task 1: Zeta Zero Expansion
    if 1 in tasks_to_run:
        try:
            all_results['task1_zeta_expansion'] = run_task1(processor, args.quick_test)
            print("✓ Task 1 completed successfully\n")
        except Exception as e:
            print(f"❌ Task 1 failed: {e}\n")
            all_results['task1_zeta_expansion'] = {'error': str(e)}
    
    # Task 2: Asymptotic Extrapolation
    if 2 in tasks_to_run:
        try:
            all_results['task2_asymptotic_extrapolation'] = run_task2(processor, args.quick_test)
            print("✓ Task 2 completed successfully\n")
        except Exception as e:
            print(f"❌ Task 2 failed: {e}\n")
            all_results['task2_asymptotic_extrapolation'] = {'error': str(e)}
    
    # Task 3: Lorentz Analogy Frame Shift Analysis
    if 3 in tasks_to_run:
        try:
            all_results['task3_lorentz_analogy'] = run_task3(processor, args.quick_test)
            print("✓ Task 3 completed successfully\n")
        except Exception as e:
            print(f"❌ Task 3 failed: {e}\n")
            all_results['task3_lorentz_analogy'] = {'error': str(e)}
    
    # Task 4: Error Oscillation CSV Generation
    if 4 in tasks_to_run:
        try:
            all_results['task4_error_csv'] = run_task4(processor, args.output_dir, args.quick_test)
            print("✓ Task 4 completed successfully\n")
        except Exception as e:
            print(f"❌ Task 4 failed: {e}\n")
            all_results['task4_error_csv'] = {'error': str(e)}
    
    total_elapsed = time.time() - total_start_time
    
    # Summary
    all_results['summary'] = {
        'total_execution_time': total_elapsed,
        'successful_tasks': [
            task for task in tasks_to_run 
            if f'task{task}' in str(all_results) and 'error' not in str(all_results.get(f'task{task}', {}))
        ],
        'failed_tasks': [
            task for task in tasks_to_run 
            if 'error' in str(all_results.get(f'task{task}', {}))
        ]
    }
    
    print("=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total execution time: {total_elapsed:.2f} seconds")
    print(f"Successful tasks: {all_results['summary']['successful_tasks']}")
    print(f"Failed tasks: {all_results['summary']['failed_tasks']}")
    print(f"End time: {datetime.now()}")
    
    # Save results
    results_file = save_results(all_results, args.output_dir)
    
    # Performance log
    performance_log = os.path.join(args.output_dir, 'performance_log.txt')
    with open(performance_log, 'w') as f:
        f.write(f"Computationally Intensive Tasks Performance Log\n")
        f.write(f"==============================================\n\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Precision: {args.precision} decimal places\n")
        f.write(f"CPU cores: {processor.num_cores}\n")
        f.write(f"Zeta zeros: {len(processor.extended_zeros)}\n")
        f.write(f"Quick test mode: {args.quick_test}\n\n")
        
        for task_num in tasks_to_run:
            task_key = f'task{task_num}'
            if task_key in all_results:
                task_result = all_results[task_key]
                if 'error' in task_result:
                    f.write(f"Task {task_num}: FAILED - {task_result['error']}\n")
                else:
                    perf = task_result.get('performance', {})
                    exec_time = perf.get('execution_time', 'N/A')
                    f.write(f"Task {task_num}: SUCCESS - {exec_time:.2f}s\n")
        
        f.write(f"\nTotal execution time: {total_elapsed:.2f} seconds\n")
    
    print(f"Performance log saved to: {performance_log}")
    
    # Exit code based on success
    success = len(all_results['summary']['failed_tasks']) == 0
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())