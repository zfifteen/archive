"""
Profiling module for analyzing performance of prime log-gap experiment.

Provides utilities for timing individual components and analyzing scaling behavior.
"""

import time
import functools
from typing import Callable, Dict, Any
import json
from pathlib import Path


class PerformanceProfiler:
    """
    Context manager and decorator for profiling code execution.
    
    Example usage:
        profiler = PerformanceProfiler()
        
        with profiler.time("prime_generation"):
            primes = generate_primes(10**6)
        
        print(profiler.get_results())
    """
    
    def __init__(self):
        self.timings = {}
        self.active_timers = {}
    
    def time(self, name: str):
        """
        Context manager for timing a code block.
        
        Args:
            name: Identifier for this timing measurement
        """
        return TimingContext(self, name)
    
    def start_timer(self, name: str):
        """Start a named timer."""
        self.active_timers[name] = time.time()
    
    def stop_timer(self, name: str):
        """Stop a named timer and record the duration."""
        if name in self.active_timers:
            duration = time.time() - self.active_timers[name]
            if name not in self.timings:
                self.timings[name] = []
            self.timings[name].append(duration)
            del self.active_timers[name]
            return duration
        return None
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get profiling results with statistics.
        
        Returns:
            Dictionary mapping names to timing statistics
        """
        results = {}
        for name, durations in self.timings.items():
            if len(durations) > 0:
                results[name] = {
                    'count': len(durations),
                    'total': sum(durations),
                    'mean': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'last': durations[-1]
                }
        return results
    
    def save_results(self, filepath: str):
        """Save profiling results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.get_results(), f, indent=2)
    
    def print_summary(self):
        """Print a human-readable summary of profiling results."""
        results = self.get_results()
        print("\n" + "=" * 70)
        print("PERFORMANCE PROFILING SUMMARY")
        print("=" * 70)
        
        if not results:
            print("No timing data collected.")
            return
        
        # Sort by total time
        sorted_results = sorted(results.items(), 
                               key=lambda x: x[1]['total'], 
                               reverse=True)
        
        total_time = sum(r['total'] for r in results.values())
        
        print(f"{'Component':<30} {'Time (s)':<12} {'% Total':<10} {'Calls':<8}")
        print("-" * 70)
        
        for name, stats in sorted_results:
            pct = (stats['total'] / total_time * 100) if total_time > 0 else 0
            print(f"{name:<30} {stats['total']:>10.3f}s {pct:>8.1f}% {stats['count']:>6d}")
        
        print("-" * 70)
        print(f"{'TOTAL':<30} {total_time:>10.3f}s {100.0:>8.1f}%")
        print("=" * 70)


class TimingContext:
    """Context manager for timing code blocks."""
    
    def __init__(self, profiler: PerformanceProfiler, name: str):
        self.profiler = profiler
        self.name = name
    
    def __enter__(self):
        self.profiler.start_timer(self.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.stop_timer(self.name)


def profile_function(name: str = None):
    """
    Decorator for profiling function execution time.
    
    Args:
        name: Optional custom name for the timing (defaults to function name)
    
    Example:
        @profile_function("my_computation")
        def compute_something(x):
            return x * 2
    """
    def decorator(func: Callable):
        timing_name = name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                print(f"[PROFILE] {timing_name}: {duration:.3f}s")
        
        return wrapper
    return decorator
