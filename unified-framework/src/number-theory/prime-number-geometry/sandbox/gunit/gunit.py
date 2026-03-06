from mpmath import mp, mpf, gamma, pi, zeta, quad, cos, log
import matplotlib.pyplot as plt
import numpy as np
from numpy import trapezoid  # Added import for trapezoid

mp.dps = 10

def xi(s):
    return (s * (s - 1)) / 2 * pi**(-s / 2) * gamma(s / 2) * zeta(s)

def f(t):
    xi_half = xi(mpf('0.5'))
    integrand = lambda x: cos(t * x) / xi(mpf('0.5') + x)
    integral = quad(integrand, [-10, 10], maxdegree=6)
    return xi_half / (2 * pi) * integral

ts = [mpf(t) for t in [-0.8, 0, 0.8]]
fs = [f(t) for t in ts]

print("f(t) values (should be positive):")
for t, val in zip(ts, fs):
    print(f"f({t}) = {val}")
    if val <= 0:
        print("Warning: Non-positive value detected.")

integral_f = quad(f, [-1, 1], maxdegree=6)
print(f"Integral of f(t) over [-1,1]: {integral_f} (expected ~1)")

log_fs = [log(val) for val in fs]
h = mpf('0.2')
second_diffs = []
for i in range(1, len(log_fs)-1):
    diff = (log_fs[i-1] - 2 * log_fs[i] + log_fs[i+1]) / (h**2)
    second_diffs.append(diff)
print("Second differences of log f (should be negative for logconcavity):", second_diffs)

# Generate plots
t_values = np.linspace(-1, 1, 100)
f_values = [float(f(mpf(t))) for t in t_values]
log_f_values = [float(log(f(mpf(t)))) for t in t_values if f(mpf(t)) > 0]

plt.figure(figsize=(10, 6))
plt.plot(t_values, f_values, label='f(t)', color='blue')
plt.twinx()
plt.plot(t_values[:len(log_f_values)], log_f_values, label='log(f(t))', color='red')
plt.xlabel('t')
plt.ylabel('f(t)', color='blue')
plt.ylabel('log(f(t))', color='red')
plt.title('f(t) and log(f(t))')
plt.legend(loc='upper left')
plt.grid(True)
plt.show()

cumulative_integral = [trapezoid(f_values[:i+1], t_values[:i+1]) for i in range(len(t_values))]
plt.figure(figsize=(8, 6))
plt.plot(t_values, cumulative_integral, label='Cumulative Integral', color='green')
plt.axhline(y=1, color='k', linestyle='--', label='Target = 1')
plt.xlabel('t')
plt.ylabel('Cumulative Integral')
plt.title('Cumulative Integral of f(t)')
plt.legend()
plt.grid(True)
plt.show()

ts_dense = np.linspace(-0.8, 0.8, 15)
log_fs_dense = [float(log(f(mpf(t)))) for t in ts_dense]
h = (ts_dense[1] - ts_dense[0])  # Dynamic step size
second_diffs_dense = [(log_fs_dense[i-1] - 2 * log_fs_dense[i] + log_fs_dense[i+1]) / (h**2)
                      for i in range(1, len(log_fs_dense)-1)]
plt.figure(figsize=(8, 6))
plt.plot(ts_dense[1:-1], second_diffs_dense, label='Second Difference', color='purple')
plt.axhline(y=0, color='k', linestyle='--', label='Zero Line')
plt.xlabel('t')
plt.ylabel('Second Difference of log(f(t))')
plt.title('Second Difference of log(f(t))')
plt.legend()
plt.grid(True)
plt.show()