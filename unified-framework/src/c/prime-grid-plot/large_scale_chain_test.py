#!/usr/bin/env python3
"""
Large-scale chained grid filter analysis with cryptographically significant sample sizes
"""
import numpy as np
import random
from math import isqrt
import time

def is_prime(n):
    """Fast primality test for moderate numbers"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True

def generate_prime_range(min_val, max_val, count, seed=None):
    """Generate specified count of random primes in range"""
    if seed:
        random.seed(seed)

    primes = []
    attempts = 0
    max_attempts = count * 50  # Prevent infinite loops

    while len(primes) < count and attempts < max_attempts:
        candidate = random.randint(min_val, max_val)
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            primes.append(candidate)
        attempts += 1

    return sorted(set(primes))  # Remove duplicates and sort

def map_to_grid(number, scale):
    """Map number to grid coordinates at given scale"""
    base = 10 ** scale
    x = number // base
    y = number % base
    return x, y

def analyze_clustering(numbers, scale, threshold_percentile=50):
    """Analyze clustering with configurable density threshold"""
    coords = [map_to_grid(n, scale) for n in numbers]
    x_coords = [coord[0] for coord in coords]

    # Count factors per x-coordinate
    x_counts = {}
    for x in x_coords:
        x_counts[x] = x_counts.get(x, 0) + 1

    # Calculate threshold
    densities = list(x_counts.values())
    if not densities:
        return {'high_density_x': [], 'x_distribution': {}}

    threshold = np.percentile(densities, threshold_percentile)
    high_density_x = [x for x, count in x_counts.items() if count >= threshold]

    return {
        'x_distribution': x_counts,
        'high_density_x': high_density_x,
        'threshold': threshold,
        'total_unique_x': len(x_counts)
    }

def calculate_space_reduction(search_min, search_max, high_density_x, scale):
    """Calculate search space size for given x-coordinates"""
    if not high_density_x:
        return 0

    base = 10 ** scale
    total_filtered = 0

    for x in high_density_x:
        x_min = x * base
        x_max = (x + 1) * base - 1

        overlap_min = max(search_min, x_min)
        overlap_max = min(search_max, x_max)

        if overlap_max >= overlap_min:
            total_filtered += overlap_max - overlap_min + 1

    return total_filtered

def test_chain_config(test_primes, search_min, search_max, chain_config):
    """Test specific chain configuration"""
    original_space = search_max - search_min + 1
    current_primes = test_primes[:]

    results = []
    current_space_estimate = original_space

    for scale, threshold in chain_config:
        analysis = analyze_clustering(current_primes, scale, threshold)
        filtered_space = calculate_space_reduction(search_min, search_max, analysis['high_density_x'], scale)

        # Check which primes would pass this filter
        passing_primes = []
        for prime in current_primes:
            x, y = map_to_grid(prime, scale)
            if x in analysis['high_density_x']:
                passing_primes.append(prime)

        results.append({
            'scale': scale,
            'threshold': threshold,
            'high_density_x': sorted(analysis['high_density_x']),
            'unique_x_coords': len(analysis['high_density_x']),
            'total_x_coords': analysis['total_unique_x'],
            'space_after': filtered_space,
            'primes_before': len(current_primes),
            'primes_after': len(passing_primes),
            'x_distribution': analysis['x_distribution']
        })

        current_space_estimate = filtered_space
        current_primes = passing_primes

    total_reduction = (1 - current_space_estimate/original_space) * 100 if original_space > 0 else 0
    capture_rate = (len(current_primes) / len(test_primes)) * 100 if test_primes else 0

    return {
        'config': chain_config,
        'steps': results,
        'final_space': current_space_estimate,
        'final_primes': len(current_primes),
        'total_reduction': total_reduction,
        'capture_rate': capture_rate,
        'search_multiplier': current_space_estimate / original_space if original_space > 0 else 0
    }

def run_large_scale_analysis():
    """Run large-scale comprehensive analysis"""

    print("LARGE-SCALE CRYPTOGRAPHIC CHAIN ANALYSIS")
    print("=" * 50)

    # Generate different sample sizes for comparison
    test_scenarios = [
        {'name': '512-bit RSA range', 'min': 2**25, 'max': 2**26-1, 'count': 100},
        {'name': '1024-bit RSA range', 'min': 2**31, 'max': 2**32-1, 'count': 200},
        {'name': 'Extended range', 'min': 10**7, 'max': 10**9, 'count': 500}
    ]

    all_results = {}

    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"Range: [{scenario['min']:,}, {scenario['max']:,}]")
        print(f"Generating {scenario['count']} random primes...")
        print(f"{'='*60}")

        start_time = time.time()
        test_primes = generate_prime_range(scenario['min'], scenario['max'], scenario['count'], seed=42)
        gen_time = time.time() - start_time

        if len(test_primes) < scenario['count'] * 0.8:  # Less than 80% success
            print(f"⚠️  Only generated {len(test_primes)} primes (target: {scenario['count']})")

        print(f"Generated {len(test_primes)} primes in {gen_time:.1f}s")
        print(f"Prime range: [{min(test_primes):,}, {max(test_primes):,}]")

        search_min = min(test_primes)
        search_max = max(test_primes)
        search_space = search_max - search_min + 1

        print(f"Search space: {search_space:,} numbers")
        print()

        # Test optimal configurations from previous analysis
        optimal_configs = [
            [(8, 25), (6, 25), (4, 25)],  # Best 3-stage from small test
            [(8, 40), (6, 30), (4, 20)],  # Alternative 3-stage
            [(8, 25), (5, 25)],           # 2-stage high reduction
            [(7, 25), (5, 25)],           # 2-stage moderate
            [(6, 25)],                     # Single stage baseline
            [(8, 50), (6, 40), (4, 30)],  # Conservative 3-stage
        ]

        scenario_results = []

        print("TESTING CONFIGURATIONS:")
        print("-" * 35)

        for config in optimal_configs:
            start_time = time.time()
            result = test_chain_config(test_primes, search_min, search_max, config)
            test_time = time.time() - start_time

            scenario_results.append(result)

            status = "✓" if result['capture_rate'] == 100 else f"~{result['capture_rate']:.0f}%"
            print(f"{status} {config}: {result['total_reduction']:.2f}% reduction, "
                  f"{result['capture_rate']:.0f}% capture ({test_time:.2f}s)")

        # Find best performing configurations
        perfect_configs = [r for r in scenario_results if r['capture_rate'] == 100]
        perfect_configs.sort(key=lambda x: x['total_reduction'], reverse=True)

        print(f"\nTOP PERFORMERS ({len(perfect_configs)} perfect configurations):")
        print("-" * 55)

        for i, result in enumerate(perfect_configs[:3]):
            print(f"#{i+1}: {result['config']}")
            print(f"  Reduction: {result['total_reduction']:.3f}%")
            print(f"  Multiplier: {result['search_multiplier']:.6f}x")
            print(f"  Final space: {result['final_space']:,}")

            # Show clustering details for most effective filter
            if result['steps']:
                most_effective = max(result['steps'], key=lambda x: len(x['high_density_x']) if x['high_density_x'] else 0)
                print(f"  Most effective stage: Scale 10^{most_effective['scale']}")
                print(f"    {len(most_effective['high_density_x'])} high-density regions")
                print(f"    Coverage: {len(most_effective['high_density_x'])}/{most_effective['total_x_coords']} x-coordinates")

        all_results[scenario['name']] = {
            'primes_generated': len(test_primes),
            'search_space': search_space,
            'perfect_configs': perfect_configs,
            'best_reduction': perfect_configs[0]['total_reduction'] if perfect_configs else 0,
            'best_multiplier': perfect_configs[0]['search_multiplier'] if perfect_configs else 1
        }

    # Cross-scenario analysis
    print(f"\n{'='*70}")
    print("CROSS-SCENARIO ANALYSIS")
    print(f"{'='*70}")

    print(f"{'Scenario':<20} {'Primes':<8} {'Search Space':<15} {'Best Reduction':<15} {'Multiplier':<12}")
    print("-" * 70)

    for name, results in all_results.items():
        print(f"{name:<20} {results['primes_generated']:<8} {results['search_space']:<15,} "
              f"{results['best_reduction']:<15.2f}% {results['best_multiplier']:<12.6f}x")

    # Scaling analysis
    print(f"\nSCALING CHARACTERISTICS:")
    print("-" * 30)

    reductions = [results['best_reduction'] for results in all_results.values()]
    multipliers = [results['best_multiplier'] for results in all_results.values()]

    if reductions:
        print(f"Reduction range: {min(reductions):.2f}% - {max(reductions):.2f}%")
        print(f"Average reduction: {np.mean(reductions):.2f}%")
        print(f"Multiplier range: {min(multipliers):.6f}x - {max(multipliers):.6f}x")
        print(f"Average search compression: {1/np.mean(multipliers):.1f}:1")

    return all_results

if __name__ == "__main__":
    results = run_large_scale_analysis()