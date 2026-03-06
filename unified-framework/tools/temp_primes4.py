import sympy
import numpy as np
import mpmath as mp
mp.dps = 50

primes = list(sympy.primerange(2, 10000))
gaps = np.diff(primes)

phi_val = float(mp.phi)

Z_vals = [(i+1) * gap / phi_val for i, gap in enumerate(gaps)]

print("Average Z:", np.mean(Z_vals))
print("Std Z:", np.std(Z_vals))
print("Min Z:", np.min(Z_vals))
print("Max Z:", np.max(Z_vals))