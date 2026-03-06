import numpy as np
import matplotlib.pyplot as plt
import math
import zlib
from sympy import isprime, primerange

PHI = (1 + 5 ** 0.5) / 2

def prime_curvature_transform(n, k=3.33):
    frac = math.modf(n / PHI)[0]
    if frac == 0: frac = 1e-10
    return (frac ** k) * math.log(n + 1)

def forecast_next_primes(primes, num_forecast=100, k=3.33, window=100):
    """Forecast next primes based on curvature minima relative to recent history."""
    transformed = [prime_curvature_transform(p, k) for p in primes]
    next_primes = []
    all_curvatures = transformed.copy()
    forecast_range = []
    n = primes[-1] + 1

    while len(next_primes) < num_forecast:
        if isprime(n):
            z = prime_curvature_transform(n, k)
            local_window = all_curvatures[-window:]
            if z < min(local_window):  # Local curvature valley
                next_primes.append(n)
            all_curvatures.append(z)
            forecast_range.append(n)
        n += 1

    return next_primes, all_curvatures, forecast_range

def compression_ratio(data):
    raw = ','.join(map(str, data)).encode()
    compressed = zlib.compress(raw)
    return len(compressed) / len(raw)

def falsification_tests(true_primes, forecasted, k=3.33):
    print("\n🔬 Running Falsification Tests...")

    # 1. Forecast Accuracy Test
    matches = sum([1 for a, b in zip(true_primes, forecasted) if a == b])
    print(f"✅ Forecast Accuracy: {matches}/{len(true_primes)}")
    if matches < len(true_primes):
        print("❌ Falsified by Forecast Error")
        return False

    # 2. Compression Test
    comp_original = compression_ratio(true_primes)
    comp_forecast = compression_ratio(forecasted)
    print(f"📉 Compression Ratio (True): {comp_original:.3f}")
    print(f"📉 Compression Ratio (Forecast): {comp_forecast:.3f}")
    if comp_forecast >= comp_original:
        print("❌ Falsified by Compression Test")
        return False

    # 3. Randomization Test
    shuffled = forecasted.copy()
    np.random.shuffle(shuffled)
    shuffled_accuracy = sum([1 for a, b in zip(true_primes, shuffled) if a == b])
    print(f"🎲 Shuffled Forecast Accuracy: {shuffled_accuracy}/{len(true_primes)}")
    if shuffled_accuracy >= matches:
        print("❌ Falsified by Random Control Test")
        return False

    print("✅ All Tests Passed — Hypothesis Not Falsified")
    return True

def plot_curvature(all_primes, all_curvatures, forecasted):
    plt.figure(figsize=(12, 6))
    plt.plot(all_primes, all_curvatures, label='Transformed Curvature', color='black', linewidth=0.5)
    forecast_indices = [all_primes.index(p) for p in forecasted if p in all_primes]
    plt.scatter([all_primes[i] for i in forecast_indices],
                [all_curvatures[i] for i in forecast_indices],
                color='red', label='Forecasted Primes', s=15)
    plt.xlabel("Prime Number")
    plt.ylabel("Curvature")
    plt.title("Curvature Collapse: Prime Forecasting via Golden Ratio Transformation")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("🚀 Causal Prime Forecasting via Curvature Collapse\n")

    # 1. Historical primes and long-range forecast
    known = list(primerange(2, 10000))      # Training data
    true_future = list(primerange(10000, 10100))  # Ground truth for testing
    forecasted, all_curvatures, forecast_domain = forecast_next_primes(known, num_forecast=100, k=3.33)

    # 2. Merge full prime sequence for plotting
    all_primes = known + forecast_domain

    # 3. Print and Test
    print("🔮 Forecasted Primes:\n", forecasted)
    result = falsification_tests(true_future, forecasted)

    # 4. Plot curvature valleys
    plot_curvature(all_primes, all_curvatures, forecasted)

    # 5. Exit logic
    if not result:
        raise SystemExit("❌ Hypothesis Falsified — Exiting.")
    else:
        print("🎉 Prime Causality Hypothesis Survives Long-Range Test.")
