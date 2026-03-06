import time
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.filter import GeometricTradingFilter
from src.core.models import FilterConfig

def run_benchmark(n_signals=1000, batch_size=100):
    print(f"--- Phi-Filter Performance Benchmark ---")
    print(f"Signals: {n_signals}")
    print(f"Batch Size: {batch_size}")
    print("-" * 40)

    trading_filter = GeometricTradingFilter()
    
    # Generate synthetic data
    prices = np.random.uniform(100, 200, n_signals)
    supports = np.random.uniform(90, 110, n_signals)
    resistances = np.random.uniform(190, 210, n_signals)
    atrs = np.random.uniform(1, 5, n_signals)

    # 1. Single Processing (Iterative)
    start_time = time.perf_counter()
    results_single = []
    for i in range(n_signals):
        res = trading_filter.filter_signal(prices[i], supports[i], resistances[i], atrs[i])
        results_single.append(res)
    end_time = time.perf_counter()
    single_duration = end_time - start_time
    
    print(f"Single Processing (Iterative):")
    print(f"  Total Time: {single_duration:.4f}s")
    print(f"  Avg Time per Signal: {(single_duration/n_signals)*1e6:.2f}µs")
    print(f"  Throughput: {n_signals/single_duration:.2f} signals/sec")
    print()

    # Reset stats
    trading_filter = GeometricTradingFilter()

    # 2. Simulated Batch Processing (Looping - as currently in API)
    # We'll simulate what the API does
    start_time = time.perf_counter()
    results_batch = []
    for i in range(0, n_signals, batch_size):
        batch_slice = slice(i, min(i + batch_size, n_signals))
        # Simulate the loop inside API's filter_batch
        batch_results = []
        for j in range(batch_slice.start, batch_slice.stop):
            res = trading_filter.filter_signal(prices[j], supports[j], resistances[j], atrs[j])
            batch_results.append(res)
        results_batch.extend(batch_results)
    
    end_time = time.perf_counter()
    batch_duration = end_time - start_time

    print(f"Batch Processing (Simulated API Loop):")
    print(f"  Total Time: {batch_duration:.4f}s")
    print(f"  Avg Time per Signal: {(batch_duration/n_signals)*1e6:.2f}µs")
    print(f"  Throughput: {n_signals/batch_duration:.2f} signals/sec")
    print()

    # 3. Vectorized Batch Processing (New Core Implementation)
    start_time = time.perf_counter()
    results_vectorized = trading_filter.filter_batch(prices, supports, resistances, atrs)
    end_time = time.perf_counter()
    vectorized_duration = end_time - start_time

    print(f"Vectorized Batch Processing (New Core Method):")
    print(f"  Total Time: {vectorized_duration:.4f}s")
    print(f"  Avg Time per Signal: {(vectorized_duration/n_signals)*1e6:.2f}µs")
    print(f"  Throughput: {n_signals/vectorized_duration:.2f} signals/sec")
    print()
    
    speedup = single_duration / vectorized_duration
    print(f"Total Speedup (Single vs Vectorized): {speedup:.2f}x")
    print("-" * 40)
    
    # Conclusion
    print("\nObservation:")
    print("Vectorized batching provides a significant performance boost for local processing.")
    print("In production, the combination of reduced HTTP overhead and vectorized core logic")
    print("makes /filter/batch the optimal choice for high-frequency applications.")

if __name__ == "__main__":
    run_benchmark()
