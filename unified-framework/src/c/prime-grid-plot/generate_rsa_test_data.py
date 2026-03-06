#!/usr/bin/env python3
"""
Generate small RSA moduli for prime factor visualization testing
"""
import random
from math import isqrt

def is_prime(n):
    """Simple primality test for small numbers"""
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

def generate_prime(min_val, max_val):
    """Generate a random prime in range"""
    while True:
        candidate = random.randint(min_val, max_val)
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            return candidate

def generate_rsa_moduli(count=20, bit_size=50):
    """Generate RSA moduli N=p*q with specified bit size"""
    moduli = []

    # Range for primes (roughly half the bit size each)
    prime_min = 2**(bit_size//2 - 2)
    prime_max = 2**(bit_size//2 + 2)

    print(f"Generating {count} RSA moduli (~{bit_size*2} bits each)")
    print(f"Prime range: [{prime_min}, {prime_max}]")
    print()

    for i in range(count):
        p = generate_prime(prime_min, prime_max)
        q = generate_prime(prime_min, prime_max)

        # Ensure p != q
        while q == p:
            q = generate_prime(prime_min, prime_max)

        n = p * q
        moduli.append((n, p, q))
        print(f"RSA {i+1:2d}: N = {n:15d} = {p:8d} × {q:8d}")

    return moduli

if __name__ == "__main__":
    # Generate test data
    rsa_data = generate_rsa_moduli(count=20, bit_size=50)

    # Save to file
    with open("rsa_test_data.txt", "w") as f:
        f.write("# RSA test data: N,p,q\n")
        for n, p, q in rsa_data:
            f.write(f"{n},{p},{q}\n")

    print(f"\nSaved {len(rsa_data)} RSA moduli to rsa_test_data.txt")

    # Extract all prime factors for grid plotting
    all_primes = []
    for n, p, q in rsa_data:
        all_primes.extend([p, q])

    with open("prime_factors.txt", "w") as f:
        f.write("# All prime factors from RSA keys\n")
        for prime in sorted(set(all_primes)):
            f.write(f"{prime}\n")

    print(f"Extracted {len(set(all_primes))} unique prime factors to prime_factors.txt")
    print(f"Prime range: [{min(all_primes)}, {max(all_primes)}]")