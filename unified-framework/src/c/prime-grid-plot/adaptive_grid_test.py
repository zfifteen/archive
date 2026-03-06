#!/usr/bin/env python3
"""
Adaptive grid test using decimal-based sizing: grid_size = decimal_places / 2
"""
import numpy as np
import random
from math import isqrt
import time

def is_prime(n):
    """Fast primality test"""
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
    """Generate random primes in range"""
    if seed:
        random.seed(seed)

    primes = []
    attempts = 0
    max_attempts = count * 50

    while len(primes) < count and attempts < max_attempts:
        candidate = random.randint(min_val, max_val)
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            primes.append(candidate)
        attempts += 1

    return sorted(set(primes))

def get_adaptive_grid_size(number):
    """Calculate adaptive grid size based on decimal places"""
    decimal_places = len(str(number))
    grid_size = decimal_places // 2
    return max(2, grid_size)  # Minimum grid size of 2

def map_to_adaptive_grid(number):
    """Map number to adaptive grid coordinates"""
    decimal_places = len(str(number))
    grid_size = decimal_places // 2

    # Split number into two halves
    num_str = str(number)
    mid_point = len(num_str) // 2

    left_half = int(num_str[:mid_point]) if num_str[:mid_point] else 0
    right_half = int(num_str[mid_point:]) if num_str[mid_point:] else 0

    # Map to grid coordinates (modulo grid_size to ensure bounds)
    x = left_half % (10 ** grid_size) if grid_size > 0 else 0
    y = right_half % (10 ** grid_size) if grid_size > 0 else 0

    # Normalize to grid size
    max_val = 10 ** grid_size - 1
    x_coord = int((x / max_val) * grid_size) if max_val > 0 else 0
    y_coord = int((y / max_val) * grid_size) if max_val > 0 else 0

    return x_coord, y_coord, grid_size

def analyze_adaptive_clustering(numbers, threshold_percentile=50):
    """Analyze clustering using adaptive grid sizing"""
    if not numbers:
        return {'grid_coords': [], 'high_density_coords': [], 'grid_size': 0}

    # All numbers should have similar grid sizes, use first number
    sample_grid_size = get_adaptive_grid_size(numbers[0])

    coords = []
    coord_counts = {}

    for number in numbers:
        x, y, grid_size = map_to_adaptive_grid(number)
        coords.append((x, y))
        coord_key = (x, y)
        coord_counts[coord_key] = coord_counts.get(coord_key, 0) + 1

    # Calculate threshold for high-density regions
    densities = list(coord_counts.values())
    if densities:
        threshold = np.percentile(densities, threshold_percentile)
        high_density_coords = [coord for coord, count in coord_counts.items() if count >= threshold]
    else:
        high_density_coords = []

    return {
        'grid_coords': coords,
        'coord_counts': coord_counts,
        'high_density_coords': high_density_coords,
        'grid_size': sample_grid_size,
        'threshold': threshold if densities else 0,
        'total_unique_coords': len(coord_counts)
    }

def calculate_adaptive_space_reduction(primes, search_min, search_max, high_density_coords, grid_size):
    """Calculate search space reduction using adaptive grid"""
    if not high_density_coords:
        return 0

    original_space = search_max - search_min + 1

    # Count numbers in high-density grid cells
    reduced_count = 0

    # Sample approach: estimate based on grid cell density
    total_grid_cells = grid_size * grid_size
    high_density_cells = len(high_density_coords)

    # Estimate reduction based on grid cell coverage
    if total_grid_cells > 0:
        coverage_ratio = high_density_cells / total_grid_cells
        reduced_space = int(original_space * coverage_ratio)
    else:
        reduced_space = original_space

    return reduced_space

def test_adaptive_grid():
    """Test adaptive grid sizing across multiple RSA ranges"""
    print("ADAPTIVE GRID TEST - DECIMAL-BASED SIZING")
    print("=" * 50)

    # Test scenarios with different number ranges
    test_scenarios = [
        {'name': 'Small RSA (512-bit)', 'min': 2**25, 'max': 2**26-1, 'count': 100},
        {'name': 'Medium RSA (1024-bit)', 'min': 2**31, 'max': 2**32-1, 'count': 100},
        {'name': 'Large Range', 'min': 10**7, 'max': 10**10, 'count': 100},
        {'name': 'Very Large', 'min': 10**15, 'max': 10**16, 'count': 50}
    ]

    all_results = {}

    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"Range: [{scenario['min']:,}, {scenario['max']:,}]")
        print(f"{'='*60}")

        # Generate test primes
        start_time = time.time()
        test_primes = generate_prime_range(scenario['min'], scenario['max'], scenario['count'], seed=42)
        gen_time = time.time() - start_time

        if not test_primes:
            print("⚠️  No primes generated!")
            continue

        print(f"Generated {len(test_primes)} primes in {gen_time:.1f}s")

        # Analyze grid characteristics
        sample_prime = test_primes[0]
        decimal_places = len(str(sample_prime))
        grid_size = get_adaptive_grid_size(sample_prime)

        print(f"Prime example: {sample_prime:,}")
        print(f"Decimal places: {decimal_places}")
        print(f"Adaptive grid size: {grid_size}×{grid_size}")

        # Test different threshold percentiles
        threshold_tests = [25, 40, 50, 60, 75]
        results = []

        print(f"\nTesting threshold percentiles:")
        for threshold in threshold_tests:
            analysis = analyze_adaptive_clustering(test_primes, threshold)

            search_min = min(test_primes)
            search_max = max(test_primes)
            reduced_space = calculate_adaptive_space_reduction(
                test_primes, search_min, search_max,
                analysis['high_density_coords'], analysis['grid_size']
            )

            original_space = search_max - search_min + 1
            reduction_percent = (1 - reduced_space / original_space) * 100 if original_space > 0 else 0

            # Check capture rate (all primes should be in their own grid cells)
            captured_primes = 0
            for prime in test_primes:
                x, y, _ = map_to_adaptive_grid(prime)
                if (x, y) in analysis['high_density_coords']:
                    captured_primes += 1

            capture_rate = (captured_primes / len(test_primes)) * 100 if test_primes else 0

            result = {
                'threshold': threshold,
                'reduction_percent': reduction_percent,
                'capture_rate': capture_rate,
                'high_density_coords': len(analysis['high_density_coords']),
                'total_coords': analysis['total_unique_coords'],
                'grid_utilization': (analysis['total_unique_coords'] / (grid_size * grid_size)) * 100 if grid_size > 0 else 0
            }
            results.append(result)

            status = "✓" if capture_rate == 100 else f"~{capture_rate:.0f}%"
            print(f"  {threshold:2d}%ile: {reduction_percent:5.1f}% reduction, {capture_rate:3.0f}% capture, "
                  f"{len(analysis['high_density_coords']):2d}/{analysis['total_unique_coords']} coords {status}")

        # Find best configuration (100% capture, max reduction)
        perfect_results = [r for r in results if r['capture_rate'] == 100]
        if perfect_results:
            best_result = max(perfect_results, key=lambda x: x['reduction_percent'])
            print(f"\n✓ Best config: {best_result['threshold']}%ile threshold")
            print(f"  Reduction: {best_result['reduction_percent']:.1f}%")
            print(f"  Grid utilization: {best_result['grid_utilization']:.1f}%")
        else:
            print(f"\n⚠️  No configuration achieved 100% capture!")

        all_results[scenario['name']] = {
            'grid_size': grid_size,
            'decimal_places': decimal_places,
            'prime_count': len(test_primes),
            'results': results,
            'best_result': perfect_results[0] if perfect_results else None
        }

    # Cross-scenario analysis
    print(f"\n{'='*70}")
    print("ADAPTIVE GRID PERFORMANCE SUMMARY")
    print(f"{'='*70}")

    print(f"{'Scenario':<20} {'Decimals':<8} {'Grid':<8} {'Primes':<7} {'Best Reduction':<15} {'Status'}")
    print("-" * 70)

    for name, result in all_results.items():
        grid_desc = f"{result['grid_size']}×{result['grid_size']}"
        if result['best_result']:
            reduction = f"{result['best_result']['reduction_percent']:.1f}%"
            status = "✓ Perfect"
        else:
            reduction = "N/A"
            status = "✗ Failed"

        print(f"{name:<20} {result['decimal_places']:<8} {grid_desc:<8} {result['prime_count']:<7} {reduction:<15} {status}")

    # Analysis summary
    successful_tests = [r for r in all_results.values() if r['best_result']]
    if successful_tests:
        reductions = [r['best_result']['reduction_percent'] for r in successful_tests]
        print(f"\nADAPTIVE GRID EFFECTIVENESS:")
        print(f"  Successful configurations: {len(successful_tests)}/{len(all_results)}")
        print(f"  Reduction range: {min(reductions):.1f}% - {max(reductions):.1f}%")
        print(f"  Average reduction: {np.mean(reductions):.1f}%")

        if len(set(reductions)) == 1:
            print(f"  ✓ CONSISTENT PERFORMANCE across all ranges!")
        else:
            print(f"  ~ Variable performance across ranges")
    else:
        print(f"\n✗ NO SUCCESSFUL CONFIGURATIONS")

    return all_results

if __name__ == "__main__":
    results = test_adaptive_grid()