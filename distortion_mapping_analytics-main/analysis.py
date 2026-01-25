import argparse
import csv
import math
from distortion_model import kappa

def is_prime(n):
    """Check if n is prime."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Analyze distortion mapping for primes vs composites.")
    parser.add_argument('--max-n', type=int, default=1000, help='Maximum n to analyze (default: 1000)')
    parser.add_argument('--rate', type=float, default=1.0, help='Traversal rate v (default: 1.0)')
    parser.add_argument('--output', type=str, default='results.csv', help='Output CSV file (default: results.csv)')
    args = parser.parse_args()

    max_n = args.max_n
    v = args.rate
    output_file = args.output

    # Compute threshold from n=2 to 49 as in demo
    primes_small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    composites_small = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30, 32, 33, 34, 35, 36, 38, 39, 40, 42, 44, 45, 46, 48, 49]

    prime_kappas = [kappa(p) for p in primes_small]
    comp_kappas = [kappa(c) for c in composites_small]
    avg_prime = sum(prime_kappas) / len(primes_small)
    avg_comp = sum(comp_kappas) / len(composites_small)
    threshold = (avg_prime + avg_comp) / 2

    # Analyze up to max_n
    results = []
    correct = 0
    total = 0

    for n in range(2, max_n + 1):
        k = kappa(n)
        actual_prime = is_prime(n)
        predicted_prime = k < threshold
        is_correct = (predicted_prime == actual_prime)
        if is_correct:
            correct += 1
        total += 1

        results.append({
            'n': n,
            'kappa': k,
            'is_prime': actual_prime,
            'predicted_prime': predicted_prime,
            'correct': is_correct
        })

    accuracy = correct / total * 100

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['n', 'kappa', 'is_prime', 'predicted_prime', 'correct']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Analysis complete for n=2 to {max_n}")
    print(f"Threshold: {threshold:.3f}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Results saved to {output_file}")

if __name__ == '__main__':
    main()