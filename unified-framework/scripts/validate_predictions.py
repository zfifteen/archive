import pandas as pd
import numpy as np
from scipy.stats import bootstrap

# Load predictions
preds = pd.read_csv("ultra_extreme_scale_predictions.csv")

# Known value for k=10^15
known = {10**15: 37124508045065437}

# Filter predictions for k close to 10^15
preds_15 = preds[preds["band_power"] == 14]

# Compute relative errors for predictions near 10^15
errors = []
k_values = []
for index, row in preds_15.iterrows():
    k = row["predicted_prime"]
    pred = row["predicted_prime"]
    true = known.get(10**15)
    error = abs((pred - true) / true) * 100
    errors.append(error)
    k_values.append(k)

# Bootstrap for CI on errors
errors_array = np.array(errors)
res = bootstrap((errors_array,), np.mean, n_resamples=1000)
ci = res.confidence_interval

# Summary
print(f"Mean error near 10^15: {np.mean(errors):.4f}% (CI: [{ci.low:.4f}, {ci.high:.4f}])")

# Save results to a log file
with open("validation_results.log", "w") as f:
    f.write(f"Validation Results for Ultra-Scale Predictions\n")
    f.write(f"===========================================\n")
    f.write(f"Mean Error near 10^15: {np.mean(errors):.4f}%\n")
    f.write(f"Confidence Interval (95%): [{ci.low:.4f}, {ci.high:.4f}]\n")
    for i, (k, err) in enumerate(zip(k_values, errors)):
        f.write(f"Prediction {i+1}: k={k:.2f}, Error={err:.4f}%\n")
