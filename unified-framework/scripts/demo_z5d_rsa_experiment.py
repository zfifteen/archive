#!/usr/bin/env python3
"""
Z5D-RSA Experiment Demo

A demonstration script showing the key features and capabilities of the Z5D-RSA
cryptographic scale experiment framework.

This demo showcases:
1. RSA benchmark suite initialization
2. Z5D predictor execution for different scales  
3. Enhanced Miller-Rabin validation (Lopez Test)
4. Performance metrics collection
5. Results analysis and reporting

Author: Z Framework Implementation Team
"""

import sys
import os
import time
from pathlib import Path

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from experiments.z5d_rsa_experiment import (
    RSACryptographicBenchmarkSuite,
    Z5DPredictorExecution,
    LopezTestMR,
    Z5DRSAExperiment
)


def demo_benchmark_suite():
    """Demonstrate RSA benchmark suite functionality."""
    print("🔐 RSA Cryptographic Benchmark Suite Demo")
    print("=" * 60)
    
    suite = RSACryptographicBenchmarkSuite()
    
    print("Available RSA Security Levels:")
    for level in suite.levels:
        print(f"  {level.name}:")
        print(f"    Bit size: {level.bit_size}")
        print(f"    Target k: ~10^{len(level.target_k)-1}")
        print(f"    Security: {level.security_level}")
        print(f"    Description: {level.description}")
        print()
    
    print("K-value calculations from bit sizes:")
    for bits in [256, 512, 1024, 2048]:
        k_val = suite.calculate_k_from_bits(bits)
        print(f"  {bits}-bit RSA: k ≈ {k_val[:20]}...")
    
    print()


def demo_z5d_predictor():
    """Demonstrate Z5D predictor execution."""
    print("🧮 Z5D Predictor Execution Demo")
    print("=" * 60)
    
    executor = Z5DPredictorExecution(adaptive_precision=True)
    
    # Test different scales
    test_cases = [
        ("Small scale", "100"),
        ("Medium scale", "10000"),
        ("Large scale", "1000000"),
    ]
    
    for description, k_str in test_cases:
        print(f"\n{description} (k = {k_str}):")
        
        try:
            start_time = time.time()
            predicted_prime, exec_time, metrics = executor.execute_prediction(k_str, description)
            
            print(f"  Predicted prime: {predicted_prime[:15]}...{predicted_prime[-15:]}")
            print(f"  Execution time: {exec_time:.4f}s")
            print(f"  Prime length: {len(predicted_prime)} digits")
            print(f"  Precision used: {metrics['precision_used']} decimal places")
            print(f"  Algorithm: {metrics['algorithm']}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print()


def demo_lopez_test():
    """Demonstrate Lopez Test Miller-Rabin validation."""
    print("🔍 Lopez Test Miller-Rabin Demo")
    print("=" * 60)
    
    lopez_test = LopezTestMR(enable_z5d_witnesses=True)
    
    # Test known primes and composites
    test_numbers = [
        ("Known primes", ["2", "3", "5", "7", "11", "17", "19", "23"]),
        ("Known composites", ["4", "6", "8", "9", "15", "21", "25", "27"]),
        ("Larger primes", ["101", "103", "107", "109", "113"])
    ]
    
    for category, numbers in test_numbers:
        print(f"\n{category}:")
        
        for num_str in numbers:
            is_prime, metrics = lopez_test.validate_prime(num_str)
            status = "PRIME" if is_prime else "COMPOSITE"
            rounds = metrics.get("rounds", 0)
            method = metrics.get("method", "unknown")
            
            print(f"  {num_str:>3}: {status:>9} ({method}, {rounds} rounds)")
    
    # Performance statistics
    stats = lopez_test.performance_stats
    print(f"\nPerformance Statistics:")
    print(f"  Total tests: {stats['total_tests']}")
    print(f"  Total rounds: {stats['total_rounds']}")
    print(f"  Z5D witnesses used: {stats['z5d_witnesses_used']}")
    
    print()


def demo_quick_experiment():
    """Demonstrate a quick experimental run."""
    print("🚀 Quick Z5D-RSA Experiment Demo")
    print("=" * 60)
    
    # Create experiment with temporary directory
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        experiment = Z5DRSAExperiment(output_dir=temp_dir, enable_detailed_logging=False)
        
        print("Running quick experiment (this may take a moment)...")
        
        try:
            # Override benchmark suite to use smaller values for demo
            from experiments.z5d_rsa_experiment import RSABenchmarkLevel
            experiment.benchmark_suite.levels = [
                RSABenchmarkLevel(
                    name="DEMO-QUICK",
                    bit_size=128,  # Small for demo
                    target_k="1000",  # Manageable k value
                    description="Quick demo level",
                    security_level="Demo"
                )
            ]
            
            results = experiment.run_full_experiment(target_levels=["DEMO-QUICK"])
            
            print("\nExperiment Results:")
            print(f"  Total time: {results['experiment_metadata']['total_time']:.3f}s")
            print(f"  Successful tests: {results['experiment_metadata']['successful_tests']}")
            print(f"  Mean execution time: {results['performance_metrics']['mean_execution_time']:.3f}s")
            print(f"  Verification success: {results['performance_metrics']['verification_success_rate']:.1%}")
            
            # Show detailed results
            for result in results['detailed_results']:
                print(f"\n  {result['level']} Results:")
                print(f"    Status: {'SUCCESS' if result['success'] else 'FAILED'}")
                print(f"    Execution time: {result['execution_time']:.3f}s")
                print(f"    Verification: {'PASSED' if result['verification_result'] else 'FAILED'}")
                print(f"    Prime length: {result['predicted_prime_length']} digits")
                print(f"    Memory usage: {result['memory_usage']} bytes")
                
        except Exception as e:
            print(f"Demo experiment failed: {e}")
    
    print()


def demo_performance_comparison():
    """Demonstrate performance comparison capabilities."""
    print("📊 Performance Comparison Demo")
    print("=" * 60)
    
    executor = Z5DPredictorExecution()
    
    # Benchmark different k values
    k_values = ["10", "100", "1000", "10000"]
    
    print("Benchmarking Z5D prediction performance:")
    print("K Value | Execution Time | Prime Length | Status")
    print("-" * 50)
    
    for k_str in k_values:
        try:
            predicted_prime, exec_time, metrics = executor.execute_prediction(k_str, "benchmark")
            prime_length = len(predicted_prime)
            status = "✅ Success"
        except Exception as e:
            exec_time = 0.0
            prime_length = 0
            status = f"❌ Failed: {str(e)[:20]}..."
        
        print(f"{k_str:>7} | {exec_time:>13.4f}s | {prime_length:>11} | {status}")
    
    print()


def main():
    """Run the complete demo."""
    print("🔐 Z5D-RSA Experiment Framework Demo")
    print("=" * 80)
    print("Demonstrating cryptographic-scale prime prediction capabilities")
    print()
    
    # Run all demo sections
    demo_benchmark_suite()
    demo_z5d_predictor()
    demo_lopez_test()
    demo_performance_comparison()
    demo_quick_experiment()
    
    print("🎉 Demo Complete!")
    print()
    print("Next steps:")
    print("1. Run full experiment: python bin/z5d_rsa_experiment.py")
    print("2. Quick test: python bin/z5d_rsa_experiment.py --quick")
    print("3. Validation: python bin/z5d_rsa_experiment.py --validate-only")
    print("4. Run tests: python -m pytest tests/test_z5d_rsa_experiment.py")


if __name__ == "__main__":
    main()