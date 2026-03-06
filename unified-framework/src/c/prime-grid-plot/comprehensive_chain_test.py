#!/usr/bin/env python3
"""
Comprehensive chained grid filter analysis with 100% capture guarantee
Tests multiple scale combinations and threshold permutations
"""
import itertools
import statistics

def map_to_grid(number, scale):
    """Map number to grid coordinates at given scale"""
    base = 10 ** scale
    x = number // base
    y = number % base
    return x, y

def analyze_clustering_with_thresholds(numbers, scale, threshold_percentile=50):
    """Analyze clustering with configurable density threshold"""
    coords = [map_to_grid(n, scale) for n in numbers]
    x_coords = [coord[0] for coord in coords]

    # Count factors per x-coordinate
    x_counts = {}
    for x in x_coords:
        x_counts[x] = x_counts.get(x, 0) + 1

    # Calculate threshold based on percentile of densities
    densities = list(x_counts.values())
    if not densities:
        return {'high_density_x': [], 'threshold': 0, 'x_distribution': {}}

    # Use numpy percentile or manual calculation for compatibility
    import numpy as np
    threshold = np.percentile(densities, threshold_percentile)
    high_density_x = [x for x, count in x_counts.items() if count >= threshold]

    return {
        'x_distribution': x_counts,
        'high_density_x': high_density_x,
        'threshold': threshold,
        'total_unique_x': len(x_counts),
        'densities': densities
    }

def create_search_space(min_range, max_range):
    """Create full search space (use count for large ranges)"""
    return max_range - min_range + 1  # Just return the count, not the actual list

def calculate_filtered_space_size(search_space_size, search_min, search_max, high_density_x, scale):
    """Calculate filtered search space size without creating actual lists"""
    if not high_density_x:
        return 0

    base = 10 ** scale
    total_filtered = 0

    # For each high-density x-coordinate, calculate how many numbers fall in that region
    for x in high_density_x:
        x_min = x * base
        x_max = (x + 1) * base - 1

        # Find overlap with our search range
        overlap_min = max(search_min, x_min)
        overlap_max = min(search_max, x_max)

        if overlap_max >= overlap_min:
            total_filtered += overlap_max - overlap_min + 1

    return total_filtered

def test_chain_configuration(test_primes, full_search_space, chain_config):
    """Test a specific chain configuration"""
    current_search_space = full_search_space[:]
    current_primes = test_primes[:]
    filters_applied = []

    for i, (scale, threshold_percentile) in enumerate(chain_config):
        # Analyze clustering of remaining primes
        analysis = analyze_clustering_with_thresholds(current_primes, scale, threshold_percentile)

        # Apply filter
        filtered_space = apply_grid_filter(current_search_space, analysis['high_density_x'], scale)

        # Check which primes remain
        remaining_primes = [p for p in current_primes if p in filtered_space]

        filter_info = {
            'scale': scale,
            'threshold_percentile': threshold_percentile,
            'high_density_x': sorted(analysis['high_density_x']),
            'search_space_before': len(current_search_space),
            'search_space_after': len(filtered_space),
            'primes_before': len(current_primes),
            'primes_after': len(remaining_primes),
            'reduction_percent': (1 - len(filtered_space) / len(current_search_space)) * 100 if current_search_space else 0
        }

        filters_applied.append(filter_info)
        current_search_space = filtered_space
        current_primes = remaining_primes

    # Calculate overall results
    total_reduction = (1 - len(current_search_space) / len(full_search_space)) * 100 if full_search_space else 0
    capture_rate = (len(current_primes) / len(test_primes)) * 100 if test_primes else 0

    return {
        'chain_config': chain_config,
        'filters': filters_applied,
        'final_search_space': len(current_search_space),
        'final_primes_captured': len(current_primes),
        'total_reduction_percent': total_reduction,
        'capture_rate_percent': capture_rate,
        'search_multiplier': len(current_search_space) / len(full_search_space) if full_search_space else 0
    }

def run_comprehensive_chain_analysis():
    """Run comprehensive analysis of chained grid filters"""

    print("COMPREHENSIVE CHAINED GRID FILTER ANALYSIS")
    print("=" * 50)

    # Smaller test dataset for faster execution
    test_primes = [9469267, 9960101, 10455701, 12364889, 18854651, 22986787, 24318631, 37909987,
                   11436077, 14952629, 15004697, 15427547]  # 12 primes total

    # Define search range
    search_min = min(test_primes)
    search_max = max(test_primes)
    full_search_space = create_search_space(search_min, search_max)

    print(f"Test primes: {len(test_primes)} factors")
    print(f"Search range: [{search_min:,}, {search_max:,}]")
    print(f"Full search space: {len(full_search_space):,} numbers")
    print()

    # Define test configurations
    scales_to_test = [8, 7, 6, 5, 4]
    thresholds_to_test = [25, 40, 50, 60, 75]  # Percentiles

    # Test single filters first
    print("SINGLE FILTER ANALYSIS")
    print("-" * 30)

    single_filter_results = []
    for scale in scales_to_test:
        for threshold in thresholds_to_test:
            config = [(scale, threshold)]
            result = test_chain_configuration(test_primes, full_search_space, config)
            single_filter_results.append(result)

            if result['capture_rate_percent'] == 100:
                print(f"Scale 10^{scale}, {threshold}%ile: {result['total_reduction_percent']:.1f}% reduction, 100% capture")

    # Find best single filter configurations (100% capture)
    perfect_single_filters = [r for r in single_filter_results if r['capture_rate_percent'] == 100]
    perfect_single_filters.sort(key=lambda x: x['total_reduction_percent'], reverse=True)

    if perfect_single_filters:
        best_single = perfect_single_filters[0]
        print(f"\nBest single filter: Scale 10^{best_single['chain_config'][0][0]}, {best_single['chain_config'][0][1]}%ile")
        print(f"  Reduction: {best_single['total_reduction_percent']:.1f}%, Capture: 100%")

    print()

    # Test two-filter chains
    print("TWO-FILTER CHAIN ANALYSIS")
    print("-" * 35)

    chain_results = []

    # Test promising two-filter combinations
    promising_configs = [
        [(8, 25), (6, 25)],  # Coarse to fine, low threshold
        [(8, 40), (5, 40)],  # Coarse to very fine, moderate threshold
        [(7, 25), (5, 25)],  # Moderate to fine, low threshold
        [(7, 40), (4, 40)],  # Moderate to ultra-fine, moderate threshold
        [(8, 50), (6, 50)],  # Coarse to fine, median threshold
        [(8, 25), (7, 25)],  # Small step, low threshold
        [(8, 60), (5, 40)],  # Mixed thresholds
        [(7, 75), (5, 25)],  # High to low threshold progression
    ]

    for config in promising_configs:
        result = test_chain_configuration(test_primes, full_search_space, config)
        chain_results.append(result)

        if result['capture_rate_percent'] == 100:
            print(f"Chain {config}: {result['total_reduction_percent']:.1f}% reduction, 100% capture")

    # Test three-filter chains
    print("\nTHREE-FILTER CHAIN ANALYSIS")
    print("-" * 35)

    three_filter_configs = [
        [(8, 25), (6, 25), (4, 25)],  # Progressive scale reduction, low threshold
        [(8, 40), (6, 40), (4, 40)],  # Progressive scale reduction, moderate threshold
        [(8, 25), (7, 25), (5, 25)],  # Fine-grained progression, low threshold
        [(8, 60), (6, 40), (4, 25)],  # Descending threshold progression
    ]

    for config in three_filter_configs:
        result = test_chain_configuration(test_primes, full_search_space, config)
        chain_results.append(result)

        if result['capture_rate_percent'] == 100:
            print(f"Chain {config}: {result['total_reduction_percent']:.1f}% reduction, 100% capture")

    # Find optimal configurations
    perfect_chains = [r for r in chain_results if r['capture_rate_percent'] == 100]
    perfect_chains.sort(key=lambda x: x['total_reduction_percent'], reverse=True)

    print("\n" + "=" * 60)
    print("OPTIMAL CONFIGURATIONS (100% CAPTURE)")
    print("=" * 60)

    for i, result in enumerate(perfect_chains[:5]):  # Top 5
        config = result['chain_config']
        print(f"\n#{i+1} Configuration: {config}")
        print(f"  Total Reduction: {result['total_reduction_percent']:.2f}%")
        print(f"  Search Multiplier: {result['search_multiplier']:.6f}x")
        print(f"  Final Search Space: {result['final_search_space']:,} numbers")

        print("  Filter Details:")
        for j, filter_info in enumerate(result['filters']):
            print(f"    Filter {j+1}: Scale 10^{filter_info['scale']}, {filter_info['threshold_percentile']}%ile")
            print(f"      Reduction: {filter_info['reduction_percent']:.1f}%, "
                  f"Space: {filter_info['search_space_after']:,}")

    # Analyze patterns in successful configurations
    print("\n" + "=" * 60)
    print("PATTERN ANALYSIS")
    print("=" * 60)

    if perfect_chains:
        # Analyze scale patterns
        scale_patterns = {}
        for result in perfect_chains:
            scales = tuple(f[0] for f in result['chain_config'])
            if scales not in scale_patterns:
                scale_patterns[scales] = []
            scale_patterns[scales].append(result['total_reduction_percent'])

        print("\nSuccessful Scale Patterns:")
        for pattern, reductions in scale_patterns.items():
            avg_reduction = statistics.mean(reductions)
            print(f"  {pattern}: Average {avg_reduction:.1f}% reduction ({len(reductions)} configs)")

        # Analyze threshold patterns
        threshold_patterns = {}
        for result in perfect_chains:
            thresholds = tuple(f[1] for f in result['chain_config'])
            if thresholds not in threshold_patterns:
                threshold_patterns[thresholds] = []
            threshold_patterns[thresholds].append(result['total_reduction_percent'])

        print("\nSuccessful Threshold Patterns:")
        for pattern, reductions in threshold_patterns.items():
            avg_reduction = statistics.mean(reductions)
            print(f"  {pattern}%ile: Average {avg_reduction:.1f}% reduction ({len(reductions)} configs)")

    return {
        'single_filters': perfect_single_filters,
        'chain_filters': perfect_chains,
        'test_primes_count': len(test_primes),
        'search_space_size': len(full_search_space)
    }

if __name__ == "__main__":
    results = run_comprehensive_chain_analysis()