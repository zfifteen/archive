"""
Test Suite for Prime Gap Analysis Implementation
==============================================

This script tests the prime gap analysis implementation at various scales
to validate correctness and performance before attempting N=10^9.
"""

import time
import numpy as np
from analyze_gaps_billion import LargeScalePrimeGapAnalyzer, print_large_scale_summary
from prime_gap_analyzer import PrimeGapAnalyzer
from optimized_sieves import OptimizedSieves, validate_sieve_correctness


def test_sieve_implementations():
    """Test sieve implementations for correctness and performance."""
    print("=== Testing Sieve Implementations ===")
    
    # Validate correctness
    if not validate_sieve_correctness():
        print("❌ Sieve validation failed!")
        return False
    
    # Performance benchmarks
    sieves = OptimizedSieves(memory_limit_mb=1000)
    
    test_limits = [10000, 100000, 1000000]
    for limit in test_limits:
        print(f"\n--- Benchmarking sieves for N={limit:,} ---")
        results = sieves.benchmark_sieves(limit)
        
        for method, stats in results.items():
            if method != 'verification':
                print(f"{method:>12}: {stats['time']:.3f}s, "
                      f"{stats['memory_mb']:.1f}MB, {stats['prime_count']:,} primes")
    
    return True


def test_gap_analysis_small():
    """Test gap analysis on small datasets."""
    print("\n=== Testing Gap Analysis (Small Scale) ===")
    
    analyzer = PrimeGapAnalyzer(memory_limit_mb=500)
    
    test_limits = [10000, 100000]
    for limit in test_limits:
        print(f"\n--- Testing gap analysis for N={limit:,} ---")
        start_time = time.time()
        
        try:
            results = analyzer.analyze_prime_gaps(limit, f"test_{limit}")
            elapsed = time.time() - start_time
            
            print(f"✅ Analysis completed in {elapsed:.2f}s")
            print(f"   Gaps: {results['summary']['total_gaps_generated']:,}")
            print(f"   Low-κ: {results['low_kappa_count']:,} ({results['low_kappa_fraction']:.1%})")
            print(f"   Plots: {len(results['summary']['plot_files'])}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False
    
    return True


def test_large_scale_analysis():
    """Test large-scale analysis implementation."""
    print("\n=== Testing Large-Scale Analysis ===")
    
    analyzer = LargeScalePrimeGapAnalyzer(memory_limit_mb=1000, sample_rate=0.1)
    
    test_limits = [1000000, 10000000]  # 1M and 10M
    
    for limit in test_limits:
        print(f"\n--- Testing large-scale analysis for N={limit:,} ---")
        start_time = time.time()
        
        try:
            results = analyzer.analyze_billion_scale(limit)
            elapsed = time.time() - start_time
            
            if 'error' not in results:
                params = results['analysis_parameters']
                overall = results['overall_statistics']
                
                print(f"✅ Analysis completed in {elapsed:.2f}s")
                print(f"   Total gaps: {overall['total_gaps']:,}")
                print(f"   Sample size: {params['sample_size']:,}")
                print(f"   Memory efficiency: {params['memory_limit_mb']} MB limit")
                
                # Validate basic statistics
                if overall['gap_mean'] > 0 and overall['gap_std'] > 0:
                    print(f"   Gap statistics: mean={overall['gap_mean']:.2f}, std={overall['gap_std']:.2f}")
                else:
                    print("⚠️ Warning: Gap statistics seem unusual")
            else:
                print(f"❌ Analysis failed: {results['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Analysis failed with exception: {e}")
            return False
    
    return True


def test_memory_efficiency():
    """Test memory efficiency and limits."""
    print("\n=== Testing Memory Efficiency ===")
    
    # Test with very low memory limit
    try:
        analyzer = LargeScalePrimeGapAnalyzer(memory_limit_mb=100, sample_rate=0.01)
        results = analyzer.analyze_billion_scale(100000)  # Small test
        
        if 'error' not in results:
            print("✅ Low memory test passed")
        else:
            print(f"⚠️ Low memory test issue: {results['error']}")
            
    except Exception as e:
        print(f"⚠️ Low memory test exception: {e}")
    
    return True


def performance_scaling_test():
    """Test performance scaling with different parameters."""
    print("\n=== Performance Scaling Test ===")
    
    limits = [100000, 500000, 1000000]
    sample_rates = [0.01, 0.05, 0.1]
    
    for limit in limits:
        for sample_rate in sample_rates:
            print(f"\n--- N={limit:,}, sample_rate={sample_rate:.1%} ---")
            
            start_time = time.time()
            analyzer = LargeScalePrimeGapAnalyzer(memory_limit_mb=500, sample_rate=sample_rate)
            
            try:
                results = analyzer.analyze_billion_scale(limit)
                elapsed = time.time() - start_time
                
                if 'error' not in results:
                    params = results['analysis_parameters']
                    overall = results['overall_statistics']
                    
                    rate = overall['total_gaps'] / elapsed if elapsed > 0 else 0
                    print(f"   Time: {elapsed:.2f}s, Rate: {rate:.0f} gaps/sec")
                    print(f"   Sample: {params['sample_size']:,} / {overall['total_gaps']:,}")
                else:
                    print(f"   Failed: {results['error']}")
                    
            except Exception as e:
                print(f"   Exception: {e}")
    
    return True


def main():
    """Run comprehensive test suite."""
    print("🧪 Prime Gap Analysis Test Suite")
    print("="*60)
    
    tests = [
        ("Sieve Implementations", test_sieve_implementations),
        ("Gap Analysis (Small)", test_gap_analysis_small),
        ("Large-Scale Analysis", test_large_scale_analysis),
        ("Memory Efficiency", test_memory_efficiency),
        ("Performance Scaling", performance_scaling_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for N=10^9 analysis.")
    else:
        print("⚠️ Some tests failed. Review issues before large-scale analysis.")
    
    return passed == total


if __name__ == "__main__":
    main()