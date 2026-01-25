from distortion_model import kappa

# Classify n=2 to 49
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30, 32, 33, 34, 35, 36, 38, 39, 40, 42, 44, 45, 46, 48, 49]

prime_kappas = [kappa(p) for p in primes]
comp_kappas = [kappa(c) for c in composites]

avg_prime = sum(prime_kappas) / len(primes)
avg_comp = sum(comp_kappas) / len(composites)
threshold = (avg_prime + avg_comp) / 2

# Accuracy: classify if kappa < threshold -> prime
correct = sum(1 for p in primes if kappa(p) < threshold) + sum(1 for c in composites if kappa(c) >= threshold)
accuracy = correct / (len(primes) + len(composites)) * 100

print(f"Avg prime κ: {avg_prime:.3f}")
print(f"Avg composite κ: {avg_comp:.3f}")
print(f"Accuracy: {accuracy:.0f}%")