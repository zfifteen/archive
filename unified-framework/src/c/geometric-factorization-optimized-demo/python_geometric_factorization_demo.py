import math
import random

# Golden ratio
PHI = (1 + math.sqrt(5)) / 2

def fractional_part(x):
    return x - math.floor(x)

def geometric_coordinate(n, k):
    frac1 = fractional_part(n / PHI)
    powered = math.pow(frac1, k)
    frac2 = fractional_part(powered)
    return fractional_part(PHI * frac2)

def circular_distance(a, b):
    d = abs(a - b) % 1
    return min(d, 1 - d)

def is_prime(num):
    if num <= 1:
        return False
    if num <= 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    i = 5
    while i * i <= num:
        if num % i == 0 or num % (i + 2) == 0:
            return False
        i += 6
    return True

def next_prime(start):
    candidate = start if start % 2 != 0 else start + 1
    while not is_prime(candidate):
        candidate += 2
    return candidate

def generate_semiprime(bit_size):
    half_bits = bit_size // 2
    p = random.getrandbits(half_bits)
    p = next_prime(p)
    q = random.getrandbits(half_bits)
    q = next_prime(q)
    return p * q, p, q

def geometric_factorize_optimized(N, k_values=[0.2, 0.45, 0.8], eps_values=[0.02, 0.05, 0.1]):
    sqrt_N = int(math.sqrt(N)) + 1
    
    # Step 1: Generate all prime candidates in the search space
    all_primes_in_range = []
    p = 2
    while p <= sqrt_N:
        if is_prime(p):
            all_primes_in_range.append(p)
        p = next_prime(p + 1)

    # Step 2: Use geometric method to FILTER the list
    for k in k_values:
        theta_N = geometric_coordinate(N, k)
        
        # Create a much smaller list of high-probability candidates
        filtered_candidates = []
        for p_candidate in all_primes_in_range:
            theta_p = geometric_coordinate(p_candidate, k)
            for eps in eps_values:
                if circular_distance(theta_p, theta_N) <= eps:
                    filtered_candidates.append(p_candidate)
                    break  # Avoid adding the same prime multiple times for different epsilons
        
        # Step 3: Perform trial division ONLY on the short list
        print(f"Generated {len(all_primes_in_range)} total primes. Filtering down to {len(filtered_candidates)} candidates for k={k}.")
        for p in filtered_candidates:
            if N % p == 0:
                q = N // p
                if is_prime(q):
                    return p, q, True
                    
    return None, None, False

# Demo with Iteration Until Success
bit_size = 20
max_attempts = 100
attempt = 0
success = False

while not success and attempt < max_attempts:
    attempt += 1
    N, actual_p, actual_q = generate_semiprime(bit_size)
    print(f"\nAttempt {attempt}: Generated {bit_size}-bit semiprime: N = {N}")
    print(f"Actual factors: {actual_p} x {actual_q}")
    
    p, q, success = geometric_factorize_optimized(N)
    if success:
        print(f"Successfully factorized: {p} x {q}")
    else:
        print("Factorization failed for this semiprime.")

if not success:
    print(f"No success after {max_attempts} attempts.")

# Note: This is a simplified demo. For larger bit sizes, use big integer libraries like sympy or gmpy2 for better performance and accuracy.
