#!/usr/bin/env python3
"""
Test chained grid filters for search space reduction
"""

def map_to_grid(number, scale):
    """Map number to grid coordinates at given scale"""
    base = 10 ** scale
    x = number // base
    y = number % base
    return x, y

def analyze_clustering(numbers, scale):
    """Analyze clustering at given scale"""
    coords = [map_to_grid(n, scale) for n in numbers]
    x_coords = [coord[0] for coord in coords]

    # Count factors per x-coordinate
    x_counts = {}
    for x in x_coords:
        x_counts[x] = x_counts.get(x, 0) + 1

    # Identify high-density regions (above average)
    avg_density = len(numbers) / len(x_counts) if x_counts else 0
    high_density_x = [x for x, count in x_counts.items() if count >= avg_density]

    return {
        'x_distribution': x_counts,
        'high_density_x': high_density_x,
        'avg_density': avg_density,
        'total_unique_x': len(x_counts)
    }

def create_search_space(min_range, max_range):
    """Create full search space"""
    return list(range(min_range, max_range + 1))

def apply_grid_filter(search_space, high_density_x, scale):
    """Filter search space to only include numbers in high-density grid regions"""
    base = 10 ** scale
    filtered = []

    for num in search_space:
        x, y = map_to_grid(num, scale)
        if x in high_density_x:
            filtered.append(num)

    return filtered

def test_chained_filters():
    """Test search space reduction using chained grid filters"""

    print("CHAINED GRID FILTER SEARCH SPACE REDUCTION TEST")
    print("=" * 55)

    # Use our known prime factors from bias test
    test_primes = [
        9469267, 9960101, 10455701, 12364889, 18854651, 22986787, 24318631, 37909987,
        39239999, 43213109, 45689617, 52466047, 57699023, 58418131, 59426233, 61649207,
        65718431, 68517101, 71276207, 72545303, 75369337, 75471271, 78697343, 86615713,
        90089033, 90945263, 97120057, 101447639, 108492469, 109393001, 112210453,
        112915661, 115645429, 118841419, 118881667, 119503919, 119619547, 123296527,
        124895567, 129525391
    ]

    # Define search range
    search_min = min(test_primes)
    search_max = max(test_primes)
    full_search_space = create_search_space(search_min, search_max)

    print(f"Test primes: {len(test_primes)} factors")
    print(f"Search range: [{search_min:,}, {search_max:,}]")
    print(f"Full search space: {len(full_search_space):,} numbers")
    print()

    # Step 1: Analyze clustering at scale 10^7
    print("FILTER 1: Grid scale 10^7")
    print("-" * 30)

    scale1_analysis = analyze_clustering(test_primes, 7)
    print(f"High-density x-coordinates: {sorted(scale1_analysis['high_density_x'])}")
    print(f"Average density: {scale1_analysis['avg_density']:.2f}")
    print(f"X-distribution: {scale1_analysis['x_distribution']}")

    # Apply first filter
    filtered_space_1 = apply_grid_filter(full_search_space, scale1_analysis['high_density_x'], 7)
    reduction_1 = (1 - len(filtered_space_1) / len(full_search_space)) * 100

    print(f"After Filter 1: {len(filtered_space_1):,} numbers ({reduction_1:.1f}% reduction)")
    print()

    # Step 2: Analyze clustering at scale 10^5 within filtered space
    print("FILTER 2: Grid scale 10^5 (applied to Filter 1 results)")
    print("-" * 55)

    # Get primes that would pass filter 1
    primes_in_filtered_1 = [p for p in test_primes if p in filtered_space_1]
    scale2_analysis = analyze_clustering(primes_in_filtered_1, 5)

    print(f"Primes passing Filter 1: {len(primes_in_filtered_1)}")
    print(f"High-density x-coordinates at 10^5: {sorted(scale2_analysis['high_density_x'])}")
    print(f"Average density: {scale2_analysis['avg_density']:.2f}")
    print(f"X-distribution: {scale2_analysis['x_distribution']}")

    # Apply second filter to already filtered space
    filtered_space_2 = apply_grid_filter(filtered_space_1, scale2_analysis['high_density_x'], 5)
    reduction_2 = (1 - len(filtered_space_2) / len(full_search_space)) * 100
    chained_improvement = reduction_2 - reduction_1

    print(f"After Filter 2: {len(filtered_space_2):,} numbers ({reduction_2:.1f}% total reduction)")
    print(f"Chained improvement: {chained_improvement:.1f}% additional reduction")
    print()

    # Step 3: Verify all test primes are still in final filtered space
    print("VALIDATION: Checking if all test primes remain in filtered space")
    print("-" * 60)

    missing_primes = [p for p in test_primes if p not in filtered_space_2]

    if missing_primes:
        print(f"⚠️  LOST PRIMES: {len(missing_primes)} primes filtered out!")
        print(f"Lost primes: {missing_primes}")
    else:
        print("✓ SUCCESS: All test primes retained in filtered search space")

    print()

    # Summary
    print("SUMMARY")
    print("=" * 20)
    print(f"Original search space: {len(full_search_space):,} numbers")
    print(f"Filter 1 (10^7) result: {len(filtered_space_1):,} numbers ({reduction_1:.1f}% reduction)")
    print(f"Filter 2 (10^5) result: {len(filtered_space_2):,} numbers ({reduction_2:.1f}% reduction)")
    print(f"Chained filter advantage: {chained_improvement:.1f}% additional reduction")
    print(f"Search space multiplier: {len(filtered_space_2) / len(full_search_space):.4f}x")

    if chained_improvement > 0:
        print("✓ HYPOTHESIS CONFIRMED: Chained filters reduce search space further")
    else:
        print("✗ HYPOTHESIS REJECTED: Chained filters provide no additional benefit")

    return {
        'original_space': len(full_search_space),
        'filter1_space': len(filtered_space_1),
        'filter2_space': len(filtered_space_2),
        'reduction1': reduction_1,
        'reduction2': reduction_2,
        'chained_improvement': chained_improvement,
        'primes_retained': len(test_primes) - len(missing_primes)
    }

if __name__ == "__main__":
    results = test_chained_filters()