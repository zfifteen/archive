#!/usr/bin/env python3
"""
Convert prime factors to grid coordinates for visualization
"""

def map_prime_to_grid(prime, scale_m=7):
    """
    Map prime to grid coordinates using N = x * 10^m + y
    Find x,y such that prime = x * 10^scale_m + y
    """
    base = 10 ** scale_m
    x = prime // base
    y = prime % base
    return x, y

def create_grid_csv(prime_file, output_csv, scale_m=7):
    """Create CSV file with prime factors mapped to grid coordinates"""

    print(f"Mapping primes to grid with scale 10^{scale_m}")

    with open(prime_file, 'r') as f:
        primes = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                primes.append(int(line))

    with open(output_csv, 'w') as f:
        f.write("x,y,N,is_prime\n")

        for prime in primes:
            x, y = map_prime_to_grid(prime, scale_m)
            f.write(f"{x},{y},{prime},1\n")

    print(f"Created {output_csv} with {len(primes)} prime factors")
    print(f"Grid coordinates range:")
    print(f"  x: [{min(p // (10**scale_m) for p in primes)}, {max(p // (10**scale_m) for p in primes)}]")
    print(f"  y: [{min(p % (10**scale_m) for p in primes)}, {max(p % (10**scale_m) for p in primes)}]")

if __name__ == "__main__":
    create_grid_csv("prime_factors.txt", "rsa_prime_grid.csv", scale_m=7)