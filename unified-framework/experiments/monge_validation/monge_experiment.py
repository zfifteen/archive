import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

def external_similitude_center(c1, r1, c2, r2):
    """Compute external center of similitude for two circles."""
    if abs(r1 - r2) < 1e-10:
        # Parallel case: midpoint or handle limit
        return (c1 + c2) / 2
    denom = r2 - r1
    return (r2 * c1 - r1 * c2) / denom

def collinearity_check(p1, p2, p3, tol=1e-10):
    """Check if P1, P2, P3 collinear via cross product."""
    v1 = p2 - p1
    v2 = p3 - p2
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    return abs(cross) < tol, abs(cross)

# Setup circles (non-overlapping)
circles = [
    (np.array([0.0, 0.0]), 1.0),   # A1
    (np.array([6.0, 0.0]), 2.0),   # A2
    (np.array([2.0, 4.0]), 3.0)    # A3
]

# Baseline computation
p12 = external_similitude_center(circles[0][0], circles[0][1], circles[1][0], circles[1][1])
p13 = external_similitude_center(circles[0][0], circles[0][1], circles[2][0], circles[2][1])
p23 = external_similitude_center(circles[1][0], circles[1][1], circles[2][0], circles[2][1])

is_collinear, error = collinearity_check(p12, p13, p23)
print(f"Baseline: Collinear? {is_collinear}, Error: {error:.2e}")

# Noise loop
noise_levels = np.arange(0, 1.01, 0.01)
results = {"baseline": {"p12": p12.tolist(), "p13": p13.tolist(), "p23": p23.tolist(), "error": float(error)},
           "noise": []}
errors = []
failure_threshold = None
mc_runs = 10
tol_failure = 1e-6

for sigma in noise_levels:
    level_errors = []
    failures = 0
    for _ in range(mc_runs):
        # Warp: Add Gaussian noise to centers
        noisy_circles = [(c + np.random.normal(0, sigma, 2), r) for (c, r) in circles]
        np12 = external_similitude_center(noisy_circles[0][0], noisy_circles[0][1], noisy_circles[1][0], noisy_circles[1][1])
        np13 = external_similitude_center(noisy_circles[0][0], noisy_circles[0][1], noisy_circles[2][0], noisy_circles[2][1])
        np23 = external_similitude_center(noisy_circles[1][0], noisy_circles[1][1], noisy_circles[2][0], noisy_circles[2][1])
        _, err = collinearity_check(np12, np13, np23)
        level_errors.append(err)
        if err > tol_failure:
            failures += 1
    mean_err = np.mean(level_errors)
    errors.append(mean_err)
    frac_failure = failures / mc_runs
    results["noise"].append({"sigma": float(sigma), "mean_error": float(mean_err), "frac_failure": float(frac_failure)})
    if failure_threshold is None and frac_failure > 0.5:  # "Snap" when >50% fail
        failure_threshold = sigma
    print(f"Sigma {sigma:.2f}: Mean Error {mean_err:.2e}, Failure Rate {frac_failure:.1%}")

# Save results
with open("monge_results.json", "w") as f:
    json.dump(results, f, indent=2)

# Plot
plt.figure(figsize=(8, 5))
plt.plot(noise_levels, errors, 'b-', label='Mean Collinearity Error')
if failure_threshold is not None:
    plt.axvline(x=failure_threshold, color='r', linestyle='--', label=f'Failure Threshold (σ={failure_threshold:.3f})')
plt.xlabel('Noise σ (Quantum Tilt)')
plt.ylabel('Cross Product Error')
plt.title("Monge's Theorem Robustness to Plane Warping")
plt.legend()
plt.savefig("collinearity_error_plot.png")
plt.close()

if failure_threshold is not None:
    print(f"Failure Point: Theorem 'snaps' at σ ≈ {failure_threshold:.3f} (50% failure rate).")
else:
    print("No failure point reached up to max σ=1.0 (Theorem holds robustly under tested perturbations).")
