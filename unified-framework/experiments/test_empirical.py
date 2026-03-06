import math

PHI = (1 + math.sqrt(5)) / 2

def geometric_resolution(n, k=0.3):
    mod_phi = n % PHI
    return PHI * (mod_phi / PHI) ** k

def sieve_of_eratosthenes(n):
    if n < 2:
        return 0
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.sqrt(n)) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return sum(is_prime)

def test_prime_density(n_values):
    print("Empirical validation of geometric resolution θ'(n,k) for prime density approximation.")
    print("Comparing θ'(n, 0.3) to actual π(n) (prime count <= n).")
    print()
    for n in n_values:
        pi_n = sieve_of_eratosthenes(n)
        theta_prime = geometric_resolution(n)
        ratio = theta_prime / pi_n if pi_n != 0 else float('inf')
        print(f"n={n:6d}: π(n)={pi_n:4d}, θ'={theta_prime:8.4f}, ratio={ratio:6.4f}")

if __name__ == "__main__":
    n_values = [10, 100, 1000, 10000, 100000]
    test_prime_density(n_values)