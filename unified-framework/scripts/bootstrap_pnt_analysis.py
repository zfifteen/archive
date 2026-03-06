import numpy as np
from math import log

# Data from high-precision results (k, known value, refined Z5D prediction, Z5D Error %, PNT Error %)
# These values are derived from Z5D predictions in high-precision mode with FFT-zeta enhancement
data = [
    {'k': 1e15, 'known': 37124508045065437, 'refined': 37125133196465557, 'z5d_err': 0.0017, 'pnt_err': 0.0053},
    {'k': 1e16, 'known': 394906913903735329, 'refined': 394911514682028139, 'z5d_err': 0.0012, 'pnt_err': 0.0045},
    {'k': 1e18, 'known': 44211790234832169331, 'refined': 44211933152759775281, 'z5d_err': 0.00032, 'pnt_err': 0.0034},
    {'k': 1e19, 'known': 465675465116607065549, 'refined': 465675315732479475703, 'z5d_err': 0.000032, 'pnt_err': 0.0030}
]

# Calculate improvement factors (PNT Error / Z5D Error)
improvements = []
for d in data:
    k = d['k']
    improvement = d['pnt_err'] / d['z5d_err']
    improvements.append(improvement)

# Bootstrap analysis (1,000 resamples) to estimate mean and CI for improvement factor
def bootstrap_mean_ci(data, n_resamples=1000, ci_level=0.95):
    means = []
    np.random.seed(42)  # For reproducibility
    for _ in range(n_resamples):
        sample = np.random.choice(data, size=len(data), replace=True)
        means.append(np.mean(sample))
    mean = np.mean(means)
    ci_low = np.percentile(means, (1 - ci_level) / 2 * 100)
    ci_high = np.percentile(means, (1 + ci_level) / 2 * 100)
    return mean, (ci_low, ci_high)

mean_improvement, ci = bootstrap_mean_ci(improvements)
print(f"Mean Improvement Factor: {mean_improvement:.1f}x")
print(f"95% Confidence Interval: [{ci[0]:.1f}, {ci[1]:.1f}]x")

# Function to calculate PNT approximation for reference (extended form)
def pnt_approx(k):
    ln_k = log(k)
    ln_ln_k = log(ln_k)
    term1 = ln_k + ln_ln_k - 1
    term2 = (ln_ln_k - 2) / ln_k
    term3 = (ln_ln_k**2 - 6 * ln_ln_k + 11) / (2 * ln_k**2)
    return k * (term1 + term2 + term3)

# Display PNT approximations and compare with known values for reference
print("\nPNT Approximations for Reference:")
for d in data:
    k = d['k']
    known = d['known']
    z5d_err = d['z5d_err']
    approx = pnt_approx(k)
    pnt_err = abs(approx - known) / known * 100
    print(f"k={k}: PNT Approx ~ {approx:.2e}, Known Value = {known}, Z5D Error = {z5d_err:.6f}%, PNT Error = {pnt_err:.4f}%")
