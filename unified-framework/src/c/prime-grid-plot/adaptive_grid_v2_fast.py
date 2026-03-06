#!/usr/bin/env python3
"""
Fast adaptive grid test v2: Minimum 8x8 grid, scale up when decimal_places/2 > 8
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
    max_attempts = count * 20  # Reduced for speed

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

def test_adaptive_grid_v2_fast():
    """Fast test of adaptive grid sizing v2"""
    print("ADAPTIVE GRID TEST V2 - MINIMUM 8x8, SCALE UP (FAST)")
    print("=" * 55)
    print("Rule: grid_size = max(8, decimal_places // 2)")
    print()

    # Smaller test scenarios for speed
    test_scenarios = [
        {'name': 'Small RSA (512-bit)', 'min': 2**25, 'max': 2**26-1, 'count': 50},
        {'name': 'Medium RSA (1024-bit)', 'min': 2**31, 'max': 2**32-1, 'count': 50},
        {'name': 'Large Range', 'min': 10**7, 'max': 10**10, 'count': 30},
        {'name': 'Very Large', 'min': 10**15, 'max': 10**16, 'count': 20}
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
        calculated_size = decimal_places // 2
        grid_size = get_adaptive_grid_size_v2(sample_prime)

        print(f"Prime example: {sample_prime:,}")
        print(f"Decimal places: {decimal_places}")
        print(f"Calculated size: {calculated_size}")
        print(f"Actual grid: {grid_size}×{grid_size}", end="")
        if grid_size > calculated_size:
            print(" (8×8 minimum applied)")
        else:
            print(" (natural scaling)")

        # Fast clustering analysis
        coords = []
        coord_counts = {}

        for number in test_primes:
            x, y, _ = map_to_adaptive_grid_v2(number)
            coords.append((x, y))
            coord_key = (x, y)
            coord_counts[coord_key] = coord_counts.get(coord_key, 0) + 1

        densities = list(coord_counts.values())
        total_unique_coords = len(coord_counts)
        max_density = max(densities) if densities else 0
        avg_density = np.mean(densities) if densities else 0

        # Test 50th percentile threshold
        threshold = np.percentile(densities, 50) if densities else 0
        high_density_coords = [coord for coord, count in coord_counts.items() if count >= threshold]

        # Calculate metrics
        total_grid_cells = grid_size * grid_size
        reduction_percent = (1 - len(high_density_coords) / total_grid_cells) * 100 if total_grid_cells > 0 else 0
        grid_utilization = (total_unique_coords / total_grid_cells) * 100 if total_grid_cells > 0 else 0

        # Check capture rate
        captured_primes = sum(1 for prime in test_primes
                             if map_to_adaptive_grid_v2(prime)[:2] in high_density_coords)
        capture_rate = (captured_primes / len(test_primes)) * 100 if test_primes else 0

        print(f"Grid utilization: {grid_utilization:.1f}% ({total_unique_coords}/{total_grid_cells} cells)")
        print(f"Density stats: avg={avg_density:.1f}, max={max_density}")
        print(f"50%ile threshold: {threshold:.1f}")
        print(f"High-density cells: {len(high_density_coords)}")
        print(f"Reduction: {reduction_percent:.1f}%")
        print(f"Capture rate: {capture_rate:.1f}%", end="")

        if capture_rate == 100:
            print(" ✓")
            status = "✓ Perfect"
        else:
            print(f" ~{capture_rate:.0f}%")
            status = f"~ {capture_rate:.0f}%"

        all_results[scenario['name']] = {
            'grid_size': grid_size,
            'decimal_places': decimal_places,
            'calculated_size': calculated_size,
            'prime_count': len(test_primes),
            'reduction_percent': reduction_percent,
            'capture_rate': capture_rate,
            'grid_utilization': grid_utilization,
            'status': status
        }

    # Summary analysis
    print(f"\n{'='*80}")
    print("ADAPTIVE GRID V2 PERFORMANCE SUMMARY")
    print(f"{'='*80}")

    print(f"{'Scenario':<22} {'DPs':<4} {'Calc':<4} {'Grid':<6} {'Primes':<6} {'Reduction':<9} {'Capture':<7} {'Status'}")
    print("-" * 80)

    perfect_count = 0
    total_count = 0

    for name, result in all_results.items():
        total_count += 1
        if result['capture_rate'] == 100:
            perfect_count += 1

        grid_desc = f"{result['grid_size']}×{result['grid_size']}"
        print(f"{name:<22} {result['decimal_places']:<4} {result['calculated_size']:<4} {grid_desc:<6} "
              f"{result['prime_count']:<6} {result['reduction_percent']:<8.1f}% {result['capture_rate']:<6.1f}% {result['status']}")

    perfect_results = [r for r in all_results.values() if r['capture_rate'] == 100]

    print(f"\nOVERALL PERFORMANCE:")
    print(f"  Perfect configurations: {perfect_count}/{total_count}")

    if perfect_results:
        reductions = [r['reduction_percent'] for r in perfect_results]
        print(f"  Reduction range: {min(reductions):.1f}% - {max(reductions):.1f}%")
        print(f"  Average reduction: {np.mean(reductions):.1f}%")
        print(f"  Search multiplier: {np.mean([1-r/100 for r in reductions]):.4f}x")

        reduction_std = np.std(reductions)
        if reduction_std < 10:
            print(f"  ✓ CONSISTENT performance (std: {reduction_std:.1f})")
        else:
            print(f"  ~ Variable performance (std: {reduction_std:.1f})")
    else:
        print(f"  ✗ No perfect configurations")

    print(f"\nGRID SCALING ANALYSIS:")
    for name, result in all_results.items():
        if result['grid_size'] > result['calculated_size']:
            print(f"  {name}: {result['calculated_size']} → {result['grid_size']} (minimum applied)")
        else:
            print(f"  {name}: {result['calculated_size']} → {result['grid_size']} (natural)")

    return all_results

if __name__ == "__main__":
    results = test_adaptive_grid_v2_fast()