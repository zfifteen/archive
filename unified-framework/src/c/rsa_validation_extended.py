import math
import concurrent.futures
import time
import random

def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def generate_semiprime(min_digits=3, max_digits=6):
    # Generate a semiprime with roughly min_digits to max_digits digits
    min_n = 10**(min_digits-1)
    max_n = 10**max_digits - 1
    while True:
        p = random.randint(int(math.sqrt(min_n)), int(math.sqrt(max_n)))
        q = random.randint(p+1, int(math.sqrt(max_n)))
        if is_prime(p) and is_prime(q):
            n = p * q
            if min_n <= n <= max_n:
                return n, p, q

def trial_division(n, start=2, end=None):
    if end is None: end = int(math.sqrt(n)) + 1
    for i in range(start, end):
        if n % i == 0: return i
    return None

def factorize_semiprime(n, workers=4):
    start_time = time.time()
    sqrt_n = int(math.sqrt(n)) + 1
    chunk_size = (sqrt_n - 2) // workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for i in range(workers):
            chunk_start = 2 + i * chunk_size
            chunk_end = chunk_start + chunk_size if i < workers - 1 else sqrt_n
            futures.append(executor.submit(trial_division, n, chunk_start, chunk_end))
        for future in concurrent.futures.as_completed(futures):
            factor = future.result()
            if factor:
                return factor, n // factor, time.time() - start_time
    return None, None, time.time() - start_time

# Test on original cases
original_test_cases = [15, 21, 35, 91, 143, 323, 899]
print("Original Test Cases:")
results = []
for n in original_test_cases:
    p, q, t = factorize_semiprime(n)
    results.append({'n': n, 'p': p, 'q': q, 'time': t, 'success': p and q and p * q == n})
    print(f"n={n}: factors={p},{q} time={t:.4f}s success={results[-1]['success']}")

# Generate and test larger semiprimes
print("\nExtended Test Cases (3-6 digits):")
extended_results = []
for _ in range(10):
    n, true_p, true_q = generate_semiprime(3, 6)
    p, q, t = factorize_semiprime(n)
    success = (p == true_p and q == true_q) or (p == true_q and q == true_p)
    extended_results.append({'n': n, 'p': p, 'q': q, 'time': t, 'success': success})
    print(f"n={n}: factors={p},{q} time={t:.4f}s success={success}")

# Summary
all_times = [r['time'] for r in results + extended_results]
mean_time = sum(all_times) / len(all_times)
sd_time = math.sqrt(sum((t - mean_time)**2 for t in all_times) / len(all_times))
print(f"\nOverall Mean Time: {mean_time:.4f}s (SD={sd_time:.4f}s)")
print(f"Success Rate: {(sum(1 for r in results + extended_results if r['success'])) / len(results + extended_results) * 100:.1f}%")