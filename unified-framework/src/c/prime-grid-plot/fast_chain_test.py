#!/usr/bin/env python3
"""
Fast comprehensive chained grid filter analysis
"""
import numpy as np

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
        'threshold': threshold
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
    current_space = original_space

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
            'space_before': current_space,
            'space_after': filtered_space,
            'primes_before': len(current_primes),
            'primes_after': len(passing_primes),
            'reduction': (1 - filtered_space/current_space) * 100 if current_space > 0 else 0
        })

        current_space = filtered_space
        current_primes = passing_primes

    total_reduction = (1 - current_space/original_space) * 100 if original_space > 0 else 0
    capture_rate = (len(current_primes) / len(test_primes)) * 100 if test_primes else 0

    return {
        'config': chain_config,
        'steps': results,
        'final_space': current_space,
        'final_primes': len(current_primes),
        'total_reduction': total_reduction,
        'capture_rate': capture_rate
    }

def run_fast_analysis():
    """Run fast comprehensive analysis"""

    print("FAST COMPREHENSIVE CHAIN ANALYSIS")
    print("=" * 40)

    # Test primes
    test_primes = [9469267, 9960101, 10455701, 12364889, 18854651, 22986787,
                   24318631, 37909987, 11436077, 14952629, 15004697, 15427547]

    search_min = min(test_primes)
    search_max = max(test_primes)

    print(f"Test primes: {len(test_primes)}")
    print(f"Search range: [{search_min:,}, {search_max:,}]")
    print(f"Search space: {search_max - search_min + 1:,} numbers")
    print()

    # Test configurations
    test_configs = [
        # Single filters
        [(8, 25)], [(7, 25)], [(6, 25)], [(8, 50)], [(7, 50)],

        # Two-stage chains
        [(8, 25), (6, 25)], [(8, 40), (5, 40)], [(7, 25), (5, 25)],
        [(8, 50), (6, 50)], [(8, 25), (7, 50)], [(7, 40), (5, 25)],

        # Three-stage chains
        [(8, 25), (6, 25), (4, 25)], [(8, 40), (6, 30), (4, 20)],
        [(8, 50), (6, 40), (4, 30)], [(7, 30), (5, 30), (4, 30)]
    ]

    perfect_configs = []

    print("TESTING CONFIGURATIONS")
    print("-" * 30)

    for config in test_configs:
        result = test_chain_config(test_primes, search_min, search_max, config)

        if result['capture_rate'] == 100:
            perfect_configs.append(result)
            print(f"✓ {config}: {result['total_reduction']:.1f}% reduction, 100% capture")
        elif result['capture_rate'] >= 90:
            print(f"~ {config}: {result['total_reduction']:.1f}% reduction, {result['capture_rate']:.0f}% capture")

    # Sort by reduction percentage
    perfect_configs.sort(key=lambda x: x['total_reduction'], reverse=True)

    print("\n" + "=" * 50)
    print("TOP PERFORMING CONFIGURATIONS (100% CAPTURE)")
    print("=" * 50)

    for i, result in enumerate(perfect_configs[:5]):
        print(f"\n#{i+1}: {result['config']}")
        print(f"  Total Reduction: {result['total_reduction']:.2f}%")
        print(f"  Final Space: {result['final_space']:,} numbers")
        print(f"  Multiplier: {result['final_space']/(search_max-search_min+1):.6f}x")

        print("  Step Details:")
        for j, step in enumerate(result['steps']):
            print(f"    Step {j+1}: Scale 10^{step['scale']}, {step['threshold']}%ile")
            print(f"      X-coords: {step['high_density_x']}")
            print(f"      Reduction: {step['reduction']:.1f}% → {step['space_after']:,} numbers")

    return perfect_configs

if __name__ == "__main__":
    results = run_fast_analysis()