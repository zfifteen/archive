import csv
import numpy as np
import mpmath as mp

mp.dps = 50

zeros = []
with open('zeta_zeros.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    for row in reader:
        n = int(row[0])
        real = float(row[1])
        imag = float(row[2])
        zeros.append((n, real, imag))

t_vals = [imag for n, real, imag in zeros]
gaps = np.diff(t_vals)

# Z = n * gap / (10 * pi^2)
pi_val = float(mp.pi)
c = 10 * (pi_val ** 2)
Z_vals = [(n+1) * gap / c for n, gap in enumerate(gaps)]

print("Average Z:", np.mean(Z_vals))
print("Std Z:", np.std(Z_vals))
print("Min Z:", np.min(Z_vals))
print("Max Z:", np.max(Z_vals))