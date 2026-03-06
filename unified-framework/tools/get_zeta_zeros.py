import mpmath as mp
import csv

mp.dps = 50

zeros = []
for n in range(1, 101):
    zero = mp.zetazero(n)
    zeros.append((n, float(zero.real), float(zero.imag)))

with open('zeta_zeros.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['n', 'real', 'imag'])
    writer.writerows(zeros)