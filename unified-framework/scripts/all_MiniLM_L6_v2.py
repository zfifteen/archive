import numpy as np
from mpmath import mp, phi
from scipy.stats import ks_2samp
import json
import re

# Set high precision
mp.dps = 50
phi_val = float(phi)

# Read embeddings from file, handling single or multiple embeddings
def parse_embeddings_file(file_path):
    with open(file_path, "r") as f:
        content = f.read().strip()
    
    # Split by document markers
    segments = re.split(r'\[Document: [^\]]+\]', content)[1:]  # Skip first empty segment
    embeddings = []
    
    for segment in segments:
        # Clean and split the segment into values
        cleaned_segment = segment.strip().replace('\n', '')
        if cleaned_segment.startswith("Embedding: "):
            cleaned_segment = cleaned_segment[len("Embedding: "):]
        try:
            values = [float(x) for x in cleaned_segment.split(',') if x.strip()]
            if len(values) == 384:  # Accept 384-dimensional embeddings
                embeddings.append(values)
            else:
                print(f"Skipping segment with {len(values)} values (expected 384)")
        except ValueError as e:
            print(f"Skipping invalid segment due to: {e}")
            continue
    
    embeddings = np.array(embeddings)
    return embeddings if embeddings.size > 0 else None

# Load embeddings
file_path = "KBEMBEDDINGS.txt"  # Ensure this matches your file
embeddings = parse_embeddings_file(file_path)

if embeddings is None or embeddings.size == 0:
    raise ValueError("No valid embeddings parsed from file")

# Determine if single or multiple embeddings and compute inputs
if embeddings.ndim == 1:
    # Single embedding: use absolute values of components
    norms = np.abs(embeddings)
    N = len(norms)  # 384
else:
    # Multiple embeddings: compute norms
    norms = np.linalg.norm(embeddings, axis=1)
    N = len(norms)

# Generate control data
np.random.seed(42)
control = np.random.uniform(0, 0.1 if embeddings.ndim == 1 else 10, N)

# Z transform
k_star = 0.3
theta_prime = np.array([phi_val * ((n % phi_val) / phi_val) ** k_star for n in norms])
theta_prime_control = np.array([phi_val * ((n % phi_val) / phi_val) ** k_star for n in control])

# Binning
B = 20
bins = np.linspace(0, phi_val, B + 1)
counts, _ = np.histogram(theta_prime, bins=bins)
counts_control, _ = np.histogram(theta_prime_control, bins=bins)
density = counts / N
density_control = counts_control / N
uniform_density = 1 / B
enhancement = (density - uniform_density) / uniform_density * 100
enhancement_control = (density_control - uniform_density) / uniform_density * 100

# Bootstrap CI for max enhancement
n_boot = 1000
boot_max = []
for _ in range(n_boot):
    idx = np.random.choice(N, N, replace=True)
    boot_theta = theta_prime[idx]
    boot_counts, _ = np.histogram(boot_theta, bins=bins)
    boot_density = boot_counts / N
    boot_enhancement = (boot_density - uniform_density) / uniform_density * 100
    boot_max.append(np.max(boot_enhancement))
ci_lower, ci_upper = np.percentile(boot_max, [2.5, 97.5])

# KS test
ks_stat, p_value = ks_2samp(theta_prime, np.random.uniform(0, phi_val, N))

# Results
results = {
    "max_enhancement_embeddings": float(np.max(enhancement)),
    "ci_lower": float(ci_lower),
    "ci_upper": float(ci_upper),
    "max_enhancement_control": float(np.max(enhancement_control)),
    "ks_p_value": float(p_value),
    "num_embeddings": N
}
print(f"Number of inputs processed: {N}")
print(f"Max enhancement (embeddings): {results['max_enhancement_embeddings']:.2f}% "
      f"(CI [{results['ci_lower']:.2f}, {results['ci_upper']:.2f}])")
print(f"Max enhancement (control): {results['max_enhancement_control']:.2f}%")
print(f"KS test p-value: {results['ks_p_value']:.2e}")

# Chart data
chart_data = {
    "type": "bar",
    "data": {
        "labels": [f"Bin {i+1}" for i in range(B)],
        "datasets": [
            {
                "label": "Embeddings Enhancement (%)",
                "data": enhancement.tolist(),
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1
            },
            {
                "label": "Control Enhancement (%)",
                "data": enhancement_control.tolist(),
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 1
            }
        ]
    },
    "options": {
        "scales": {
            "y": {
                "title": {"display": True, "text": "Density Enhancement (%)"},
                "beginAtZero": True
            },
            "x": {
                "title": {"display": True, "text": "Bin"}
            }
        },
        "plugins": {
            "title": {"display": True, "text": "Z Transform Density Enhancement"},
            "legend": {"position": "top"}
        }
    }
}

# Save chart data
with open("enhancement_chart.json", "w") as f:
    json.dump(chart_data, f)

# Save results
with open("simulation_results.json", "w") as f:
    json.dump(results, f)