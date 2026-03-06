import sympy
from light_primes import light_primes_in_range

def demo(N=1000):
    generated = light_primes_in_range(500000,600000)
    print(f"Generated numbers up to {N}: {generated}")
    print(f"Total generated: {len(generated)}")

    true_primes = [num for num in generated if sympy.isprime(num)]
    accuracy = (len(true_primes) / len(generated)) * 100 if generated else 0
    print(f"True primes: {true_primes}")
    print(f"Number of true primes: {len(true_primes)}")
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    demo()