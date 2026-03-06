import numpy as np
from scipy.stats import qmc
import math

def f(x, y):
    return np.cos(x + y)

# Exact integral
exact = -math.cos(2) + 2 * math.cos(1) - 1
print(f"Exact integral: {exact}")

# Test for different N
ns = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]

print("N\tMC Error\tQMC Error")
for n in ns:
    # Monte Carlo
    x_mc = np.random.random(n)
    y_mc = np.random.random(n)
    mc_integral = np.mean(f(x_mc, y_mc))
    mc_error = abs(mc_integral - exact)

    # Quasi-Monte Carlo with Sobol
    sampler = qmc.Sobol(d=2, scramble=True)
    samples = sampler.random(n)
    x_qmc = samples[:, 0]
    y_qmc = samples[:, 1]
    qmc_integral = np.mean(f(x_qmc, y_qmc))
    qmc_error = abs(qmc_integral - exact)

    print(f"{n}\t{mc_error:.5f}\t{qmc_error:.5f}")