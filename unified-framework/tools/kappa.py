import mpmath as mp
import numpy as np

mp.mp.dps = 50

def kappa(n, epsilon=0.252):
    # Mock d(n) ~ log(log(n)) for large n (asymptotic)
    d_n = mp.log(mp.log(n)) + 1 # Placeholder
    return d_n * mp.log(n + 1) / mp.exp(2) + epsilon * mp.log(n)

# Grid search epsilon for minimal Δ_n (hypothetical optimization)
# Assuming Δ_n = kappa(n, epsilon), we minimize it
n_large = mp.mpf(10)**18 # Ultra-scale mock
n = n_large
epsilons = mp.linspace(0.2, 0.3, 5)  # epsilon values from 0.2 to 0.3
deltas = []
min_delta_n = mp.inf
best_eps = mp.mpf(0)
for eps in epsilons:
    delta_n = kappa(n_large, eps) - kappa(n_large - 1, eps) # Δ_n proxy
    assert float(delta_n) > 1e-16, "Causality guard violation"
    deltas.append(float(delta_n))
    print(f"eps: {eps}, delta_n: {delta_n}")
    if delta_n < min_delta_n:
        min_delta_n = delta_n
        best_eps = eps
print(f"Best epsilon: {best_eps}")
print(f"Minimal Δ_n: {min_delta_n}")
print(f"All deltas: {deltas}")
optimal_eps = epsilons[np.argmin(np.abs(deltas))]
print(f"Optimal eps (argmin abs): {optimal_eps}")
print(f"Optimal epsilon: {optimal_eps:.4f}, Min Δ_n: {min(deltas):.2e}")

# Bootstrap CI on deltas (1000 resamples)
# Assuming CI for the min of deltas
bootstrap_samples = 1000
bootstrap_mins = [np.min(np.random.choice(deltas, len(deltas), replace=True)) for _ in range(bootstrap_samples)]
bootstrap_mins = np.array(bootstrap_mins)
ci_lower, ci_upper = np.percentile(bootstrap_mins, [2.5, 97.5])
print(f"Bootstrap 95% CI for min Δ_n: ({ci_lower:.2e}, {ci_upper:.2e})")