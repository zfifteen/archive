import time
import mpmath
import sympy

class ComparisonResult:
    def __init__(self, method_name, N):
        self.method_name = method_name
        self.N = N
        self.success = False
        self.found_factor = None
        self.steps_taken = 0
        self.time_seconds = 0.0

def theta_prime_z5d(n, k):
    phi = mpmath.phi
    mod_phi = mpmath.fmod(n, phi)
    return phi * (mod_phi / phi)**k

def z5d_factorization_shortcut(N, max_steps=200, epsilon=0.3, k_param=0.3):
    result = ComparisonResult("Z5D θ' Shortcut", N)
    start_time = time.time()
    
    theta_N = theta_prime_z5d(mpmath.mpf(N), k_param)
    
    sqrt_N = int(mpmath.sqrt(N))
    # Start from smaller primes
    candidate = 2
    
    for _ in range(max_steps):
        candidate = sympy.nextprime(candidate)
        if candidate > sqrt_N:
            break
            
        result.steps_taken += 1
        
        theta_p = theta_prime_z5d(mpmath.mpf(candidate), k_param)
        
        dist = min(abs(theta_p - theta_N), 1 - abs(theta_p - theta_N))
        
        if dist < epsilon:
            if N % candidate == 0:
                result.found_factor = candidate
                result.success = True
                break
    
    result.time_seconds = time.time() - start_time
    return result

def print_results(results):
    for result in results:
        print(f"{result.method_name}: N={result.N}, success={result.success}, factor={result.found_factor}, steps={result.steps_taken}, time={result.time_seconds:.3f}s")

if __name__ == "__main__":
    N = 77
    results = []
    results.append(z5d_factorization_shortcut(N))
    print_results(results)