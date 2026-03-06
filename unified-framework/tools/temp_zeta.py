import mpmath as mp
import numpy as np
mp.dps = 50

with open('zeta.txt', 'r') as f:
    t_vals = [mp.mpf(line.strip()) for line in f if line.strip()]

gaps = [t_vals[i+1] - t_vals[i] for i in range(len(t_vals)-1)]

pi = mp.pi

Z_vals = [float((i+1) * gap / pi) for i, gap in enumerate(gaps)]

print("Average Z:", np.mean(Z_vals))
print("Std Z:", np.std(Z_vals))
print("Min Z:", np.min(Z_vals))
print("Max Z:", np.max(Z_vals))