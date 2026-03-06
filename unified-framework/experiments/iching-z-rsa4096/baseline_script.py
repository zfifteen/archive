import subprocess
import re

results = []
for i in range(10):
    proc = subprocess.run(['python3', 'rsa4096_test_harness.py'], capture_output=True, text=True)
    output = proc.stdout
    # Extract success rates
    scaling_match = re.search(r'Overall success rate: (\d+\.\d+)%', output)
    z5d_match = re.search(r'Z5D success rate: (\d+\.\d+)%', output)
    if scaling_match and z5d_match:
        scaling_rate = float(scaling_match.group(1))
        z5d_rate = float(z5d_match.group(1))
        results.append((scaling_rate, z5d_rate))
    else:
        print(f"Run {i+1}: Failed to parse output")

if results:
    avg_scaling = sum(r[0] for r in results) / len(results)
    avg_z5d = sum(r[1] for r in results) / len(results)
    print(f"Baseline (10 runs):")
    print(f"Average Geometric Scaling Success Rate: {avg_scaling:.1f}%")
    print(f"Average Z5D Success Rate: {avg_z5d:.1f}%")
    print(f"Raw results: {results}")
else:
    print("No valid results parsed.")