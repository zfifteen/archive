import time
import random
import mpmath as mp
from sympy import nextprime
from z5d_predictor import z5d_predictor

mp.dps = 50  # High precision

def generate_semiprimes(num=10, min_bits=10, max_bits=10):
    """Generate random semiprimes for testing."""
    semiprimes = []
    for _ in range(num):
        bits = random.randint(min_bits, max_bits)
        p = nextprime(random.randint(2**(bits//2-1), 2**(bits//2)))
        q = nextprime(random.randint(2**(bits//2-1), 2**(bits//2)))
        while p == q:  # Ensure distinct for RSA-style
            q = nextprime(random.randint(2**(bits//2-1), 2**(bits//2)))
        n = p * q
        semiprimes.append((n, p, q))
    return semiprimes

def poc_test_z5d(semiprimes, eps=0.5):
    """POC: Use Z5D to predict and factorize semiprimes."""
    results = []
    total_time = 0
    correct = 0
    
    for n, true_p, true_q in semiprimes:
        start = time.time()
        
        # Use Z5D predictor
        pred = z5d_predictor(n, eps=eps)
        best_k = pred['best_k']
        candidates = pred['candidates']
        
        # Check if any candidate matches (exact for p*q)
        match = False
        for p, q in candidates:
            if {p, q} == {true_p, true_q}:
                match = True
                break
        
        elapsed = time.time() - start
        total_time += elapsed
        
        results.append({
            'n': n,
            'true_p': true_p,
            'true_q': true_q,
            'pred_k': best_k,
            'candidates': candidates,
            'match': match,
            'time': elapsed
        })
        
        if match:
            correct += 1
    
    return results, correct, total_time

if __name__ == "__main__":
    random.seed(42)  # Reproducibility
    
    semiprimes = generate_semiprimes(1000)  # Expanded to 1000 RSA-style 10-bit semiprimes
    results, correct, total_time = poc_test_z5d(semiprimes, eps=0.5)
    
    print("POC Results for Z5D Integration (ε=0.5) on 10-bit Semiprimes:")
    print(f"Total semiprimes: {len(results)}")
    print(f"Correct factorizations: {correct} ({100*correct/len(results):.1f}%)")
    print(f"Total time: {total_time:.2f}s (avg: {total_time/len(results):.2f}s per n)")
    print("\nDetails (first 10 for brevity):")
    for r in results[:10]:
        print(f"n={r['n']}: Match={r['match']}, Time={r['time']:.2f}s, Candidates={r['candidates']}")