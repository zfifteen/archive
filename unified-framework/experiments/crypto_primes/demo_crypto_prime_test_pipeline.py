#!/usr/bin/env python3
"""
Z5D Crypto-Friendly Primes Test Pipeline Demo
============================================

Demonstrates the complete test pipeline for Z5D-biased generation of crypto-friendly primes.
This script runs all test components as specified in Issue #677.

Usage:
    python demo_crypto_prime_test_pipeline.py --quick
    python demo_crypto_prime_test_pipeline.py --full
"""

import sys
import os
import subprocess
import argparse
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return True if successful"""
    logger.info(f"Running: {description}")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info(f"✅ {description} - PASSED")
            return True
        else:
            logger.warning(f"❌ {description} - FAILED")
            if result.stderr:
                logger.warning(f"Error output: {result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        logger.error(f"💥 {description} - ERROR: {e}")
        return False

def clean_previous_results():
    """Clean up previous test results"""
    logger.info("🧹 Cleaning previous test results...")
    
    # Remove existing results and metrics
    for directory in ['results', 'metrics']:
        if os.path.exists(directory):
            import shutil
            shutil.rmtree(directory)
            logger.info(f"Removed {directory}/")
    
    # Remove report files
    for file in ['REPORT.md']:
        if os.path.exists(file):
            os.remove(file)
            logger.info(f"Removed {file}")

def run_quick_demo() -> bool:
    """Run quick demonstration with small parameters"""
    logger.info("🚀 Starting QUICK demo of Z5D crypto-friendly primes test pipeline")
    
    commands = [
        # PNT inversion
        (['python', '-m', 'scripts.invert_pnt', '--m', '64'], 
         "PNT Inversion (64-bit)"),
        
        # Z5D accuracy test (small k values)
        (['python', '-m', 'scripts.test_z5d_accuracy', '--k-list', '10,20,50,100', '--max-feasible-k', '200'],
         "Z5D Accuracy Test (small k)"),
        
        # Form hit-rate benchmark (small window)
        (['python', '-m', 'scripts.bench_form_hitrate', '--m', '64', '--W', '1000', '--budget', '5000'],
         "Form Hit-Rate Benchmark (64-bit, small window)"),
        
        # Sqrt-friendly QC
        (['python', '-m', 'scripts.qc_sqrt_mod4', '--m', '64', '--generate-samples', '--sample-size', '50'],
         "Sqrt-Friendly QC (64-bit, 50 samples)"),
        
        # Montgomery multiplication benchmark
        (['python', '-m', 'scripts.bench_modmul_speed', '--m', '64', '--trials', '2', '--ops', '10000'],
         "Montgomery Multiplication Benchmark (64-bit, fast)"),
        
        # Generate final report
        (['python', '-m', 'scripts.summary_gate_report', '--metrics-dir', 'metrics'],
         "Summary Gate Report Generation")
    ]
    
    passed = 0
    total = len(commands)
    
    for cmd, description in commands:
        if run_command(cmd, description):
            passed += 1
    
    logger.info(f"📊 Quick Demo Results: {passed}/{total} tests completed successfully")
    return passed == total

def run_full_demo() -> bool:
    """Run full demonstration with realistic parameters"""
    logger.info("🚀 Starting FULL demo of Z5D crypto-friendly primes test pipeline")
    
    commands = [
        # PNT inversion for crypto bit lengths
        (['python', '-m', 'scripts.invert_pnt', '--m-list', '128,192,256'],
         "PNT Inversion (crypto bit lengths)"),
        
        # Z5D accuracy test (reasonable k range)
        (['python', '-m', 'scripts.test_z5d_accuracy', '--k-min', '1000', '--k-max', '100000', '--points', '50'],
         "Z5D Accuracy Test (k=1K-100K)"),
        
        # Form hit-rate benchmarks for multiple bit lengths
        (['python', '-m', 'scripts.bench_form_hitrate', '--m', '128', '--predicate', 'pseudo_mersenne', '--W', '16384', '--budget', '50000'],
         "Form Hit-Rate Benchmark (128-bit)"),
        
        (['python', '-m', 'scripts.bench_form_hitrate', '--m', '192', '--predicate', 'pseudo_mersenne', '--W', '16384', '--budget', '50000'],
         "Form Hit-Rate Benchmark (192-bit)"),
        
        # Sqrt-friendly QC for multiple bit lengths
        (['python', '-m', 'scripts.qc_sqrt_mod4', '--m-list', '128,192,256', '--generate-samples', '--sample-size', '500'],
         "Sqrt-Friendly QC (multiple bit lengths)"),
        
        # Montgomery multiplication benchmarks
        (['python', '-m', 'scripts.bench_modmul_speed', '--m', '128', '--trials', '3', '--ops', '100000'],
         "Montgomery Multiplication Benchmark (128-bit)"),
        
        (['python', '-m', 'scripts.bench_modmul_speed', '--m', '192', '--trials', '3', '--ops', '100000'],
         "Montgomery Multiplication Benchmark (192-bit)"),
        
        # Generate final report
        (['python', '-m', 'scripts.summary_gate_report', '--metrics-dir', 'metrics'],
         "Summary Gate Report Generation")
    ]
    
    passed = 0
    total = len(commands)
    
    for cmd, description in commands:
        if run_command(cmd, description):
            passed += 1
    
    logger.info(f"📊 Full Demo Results: {passed}/{total} tests completed successfully")
    return passed == total

def print_results_summary():
    """Print summary of generated results"""
    logger.info("📋 Generated Results Summary:")
    
    # Check for generated files
    result_files = []
    metric_files = []
    
    if os.path.exists('results'):
        result_files = [f for f in os.listdir('results') if f.endswith('.csv')]
    
    if os.path.exists('metrics'):
        metric_files = [f for f in os.listdir('metrics') if f.endswith('.json')]
    
    logger.info(f"  📄 Result CSV files: {len(result_files)}")
    for f in result_files:
        logger.info(f"    - results/{f}")
    
    logger.info(f"  📊 Metric JSON files: {len(metric_files)}")
    for f in metric_files:
        logger.info(f"    - metrics/{f}")
    
    if os.path.exists('REPORT.md'):
        logger.info(f"  📋 Final report: REPORT.md")
        
        # Show first few lines of report
        with open('REPORT.md', 'r') as f:
            lines = f.readlines()[:10]
        logger.info("  Report preview:")
        for line in lines:
            logger.info(f"    {line.rstrip()}")
    
def main():
    parser = argparse.ArgumentParser(
        description="Demo of Z5D crypto-friendly primes test pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Quick demo with small parameters (fast)
    python demo_crypto_prime_test_pipeline.py --quick
    
    # Full demo with realistic parameters (slower but more accurate)
    python demo_crypto_prime_test_pipeline.py --full
    
    # Clean previous results and run quick demo
    python demo_crypto_prime_test_pipeline.py --clean --quick
        """
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick demo with small parameters'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run full demo with realistic parameters'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean previous results before running'
    )
    
    args = parser.parse_args()
    
    if not args.quick and not args.full:
        print("Error: Must specify either --quick or --full")
        return 1
    
    if args.quick and args.full:
        print("Error: Cannot specify both --quick and --full")
        return 1
    
    try:
        # Clean previous results if requested
        if args.clean:
            clean_previous_results()
        
        # Run the appropriate demo
        if args.quick:
            success = run_quick_demo()
        else:
            success = run_full_demo()
        
        # Print results summary
        print_results_summary()
        
        # Final status
        if success:
            logger.info("🎉 Demo completed successfully!")
            logger.info("💡 Note: Test failures are expected with small sample sizes")
            logger.info("🔍 Check REPORT.md for detailed results")
        else:
            logger.warning("⚠️  Some tests failed during demo")
            logger.info("🔍 Check logs above for details")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"💥 Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())