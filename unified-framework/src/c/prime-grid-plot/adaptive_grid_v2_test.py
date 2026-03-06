#!/usr/bin/env python3
"""
Adaptive grid test v2: Minimum 8x8 grid, scale up when decimal_places/2 > 8
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

def get_adaptive_grid_size_v2(number):
    """Calculate adaptive grid size: minimum 8x8, scale up when dps/2 > 8"""
    decimal_places = len(str(number))
    calculated_size = decimal_places // 2
    grid_size = max(8, calculated_size)  # Minimum 8x8 grid
    return grid_size

def map_to_adaptive_grid_v2(number):
    """Map number to adaptive grid coordinates v2"""
    grid_size = get_adaptive_grid_size_v2(number)

    # Convert number to string and split into halves
    num_str = str(number)
    mid_point = len(num_str) // 2

    left_half = num_str[:mid_point] if mid_point > 0 else "0"
    right_half = num_str[mid_point:] if mid_point < len(num_str) else "0"

    # Convert to integers
    left_val = int(left_half) if left_half else 0
    right_val = int(right_half) if right_half else 0

    # Map to grid coordinates using modulo
    x_coord = left_val % grid_size
    y_coord = right_val % grid_size

    return x_coord, y_coord, grid_size

def analyze_adaptive_clustering_v2(numbers, threshold_percentile=50):
    """Analyze clustering using adaptive grid sizing v2"""
    if not numbers:
        return {'grid_coords': [], 'high_density_coords': [], 'grid_size': 0}

    # All numbers should have similar grid sizes, use first number
    sample_grid_size = get_adaptive_grid_size_v2(numbers[0])

    coords = []
    coord_counts = {}

    for number in numbers:
        x, y, grid_size = map_to_adaptive_grid_v2(number)
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
        'total_unique_coords': len(coord_counts),
        'densities': densities
    }

def calculate_adaptive_space_reduction_v2(primes, high_density_coords, grid_size):
    """Calculate search space reduction using adaptive grid v2"""
    if not high_density_coords or grid_size == 0:
        return 0, 100  # No reduction, 100% of space

    total_grid_cells = grid_size * grid_size
    high_density_cells = len(high_density_coords)

    # Calculate reduction percentage
    if total_grid_cells > 0:
        reduction_percent = (1 - high_density_cells / total_grid_cells) * 100
    else:
        reduction_percent = 0

    return reduction_percent, high_density_cells / total_grid_cells

def test_adaptive_grid_v2():
    """Test adaptive grid sizing v2 across multiple RSA ranges"""
    print("ADAPTIVE GRID TEST V2 - MINIMUM 8x8, SCALE UP")
    print("=" * 55)
    print("Rule: grid_size = max(8, decimal_places // 2)")
    print()

    # Test scenarios with different number ranges
    test_scenarios = [
        {'name': 'Small RSA (512-bit)', 'min': 2**25, 'max': 2**26-1, 'count': 100},
        {'name': 'Medium RSA (1024-bit)', 'min': 2**31, 'max': 2**32-1, 'count': 100},
        {'name': 'Large Range', 'min': 10**7, 'max': 10**10, 'count': 100},
        {'name': 'Very Large', 'min': 10**15, 'max': 10**16, 'count': 50},
        {'name': 'Ultra Large', 'min': 10**30, 'max': 10**31, 'count': 25}
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
        grid_size = get_adaptive_grid_size_v2(sample_prime)

        print(f"Prime example: {sample_prime:,}")
        print(f"Decimal places: {decimal_places}")
        print(f"Calculated grid size: {decimal_places // 2}")
        print(f"Actual grid size: {grid_size}×{grid_size} (min 8×8 applied)")

        # Test different threshold percentiles
        threshold_tests = [25, 40, 50, 60, 75]
        results = []

        print(f"\nTesting threshold percentiles:")
        for threshold in threshold_tests:
            analysis = analyze_adaptive_clustering_v2(test_primes, threshold)

            reduction_percent, coverage_ratio = calculate_adaptive_space_reduction_v2(
                test_primes, analysis['high_density_coords'], analysis['grid_size']
            )

            # Check capture rate (all primes should be in high-density coords)
            captured_primes = 0
            for prime in test_primes:
                x, y, _ = map_to_adaptive_grid_v2(prime)
                if (x, y) in analysis['high_density_coords']:
                    captured_primes += 1

            capture_rate = (captured_primes / len(test_primes)) * 100 if test_primes else 0

            result = {
                'threshold': threshold,
                'reduction_percent': reduction_percent,
                'capture_rate': capture_rate,
                'high_density_coords': len(analysis['high_density_coords']),
                'total_coords': analysis['total_unique_coords'],
                'grid_utilization': (analysis['total_unique_coords'] / (grid_size * grid_size)) * 100 if grid_size > 0 else 0,
                'coverage_ratio': coverage_ratio
            }
            results.append(result)

            status = "✓" if capture_rate == 100 else f"~{capture_rate:.0f}%"
            print(f"  {threshold:2d}%ile: {reduction_percent:5.1f}% reduction, {capture_rate:3.0f}% capture, "
                  f"{len(analysis['high_density_coords']):2d}/{analysis['total_unique_coords']} coords "
                  f"({result['grid_utilization']:.1f}% util) {status}")

        # Find best configuration (100% capture, max reduction)
        perfect_results = [r for r in results if r['capture_rate'] == 100]
        if perfect_results:
            best_result = max(perfect_results, key=lambda x: x['reduction_percent'])
            print(f"\n✓ Best config: {best_result['threshold']}%ile threshold")
            print(f"  Reduction: {best_result['reduction_percent']:.1f}%")
            print(f"  Search space multiplier: {1-best_result['reduction_percent']/100:.4f}x")
            print(f"  Grid utilization: {best_result['grid_utilization']:.1f}%")
        else:
            best_non_perfect = max(results, key=lambda x: x['capture_rate']) if results else None
            print(f"\n⚠️  No configuration achieved 100% capture!")
            if best_non_perfect:
                print(f"  Best capture: {best_non_perfect['capture_rate']:.1f}% at {best_non_perfect['threshold']}%ile")

        all_results[scenario['name']] = {
            'grid_size': grid_size,
            'decimal_places': decimal_places,
            'prime_count': len(test_primes),
            'results': results,
            'best_result': perfect_results[0] if perfect_results else best_non_perfect
        }

    # Cross-scenario analysis
    print(f"\n{'='*80}")
    print("ADAPTIVE GRID V2 PERFORMANCE SUMMARY")
    print(f"{'='*80}")

    print(f"{'Scenario':<22} {'Decimals':<8} {'Grid':<8} {'Primes':<7} {'Best Reduction':<15} {'Capture':<8} {'Status'}")
    print("-" * 80)

    successful_configs = 0
    total_configs = 0

    for name, result in all_results.items():
        total_configs += 1
        grid_desc = f"{result['grid_size']}×{result['grid_size']}"

        if result['best_result']:
            reduction = f"{result['best_result']['reduction_percent']:.1f}%"
            capture = f"{result['best_result']['capture_rate']:.0f}%"

            if result['best_result']['capture_rate'] == 100:
                status = "✓ Perfect"
                successful_configs += 1
            else:
                status = f"~ Partial"
        else:
            reduction = "N/A"
            capture = "N/A"
            status = "✗ Failed"

        print(f"{name:<22} {result['decimal_places']:<8} {grid_desc:<8} {result['prime_count']:<7} {reduction:<15} {capture:<8} {status}")

    # Analysis summary
    perfect_tests = [r for r in all_results.values() if r['best_result'] and r['best_result']['capture_rate'] == 100]

    print(f"\nADAPTIVE GRID V2 EFFECTIVENESS:")
    print(f"  Perfect configurations: {successful_configs}/{total_configs}")

    if perfect_tests:
        reductions = [r['best_result']['reduction_percent'] for r in perfect_tests]
        print(f"  Reduction range: {min(reductions):.1f}% - {max(reductions):.1f}%")
        print(f"  Average reduction: {np.mean(reductions):.1f}%")
        print(f"  Average search multiplier: {np.mean([1-r/100 for r in reductions]):.4f}x")

        # Check for consistency
        reduction_variance = np.var(reductions)
        if reduction_variance < 100:  # Low variance
            print(f"  ✓ CONSISTENT PERFORMANCE across ranges (var: {reduction_variance:.1f})")
        else:
            print(f"  ~ Variable performance across ranges (var: {reduction_variance:.1f})")
    else:
        print(f"  ✗ NO PERFECT CONFIGURATIONS ACHIEVED")

    # Grid size analysis
    print(f"\nGRID SIZING ANALYSIS:")
    for name, result in all_results.items():
        calc_size = result['decimal_places'] // 2
        actual_size = result['grid_size']
        if actual_size > calc_size:
            print(f"  {name}: {calc_size} → {actual_size} (minimum 8×8 applied)")
        else:
            print(f"  {name}: {calc_size} → {actual_size} (natural scaling)")

    return all_results

if __name__ == "__main__":
    results = test_adaptive_grid_v2()