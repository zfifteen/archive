import mpmath as mp
import numpy as np
from sympy import primerange
mp.mp.dps = 50

phi = (1 + mp.sqrt(5)) / 2
kappa_geo = mp.mpf('0.3')

def pnt_density(n):
    return n / mp.log(n)  # Approx π(n)

N = 1000000
interval_size = N / 50  # 50 intervals for density
pnt_expected = [float(pnt_density(i * interval_size)) for i in range(1, 51)]

# Geodesic intervals: θ'(i * interval_size, k) defines bin starts
geo_primes_count = np.zeros(50)
primes = list(primerange(2, N))
for p in primes:
    # Map p to θ' bin
    n_mp = mp.mpf(p)
    mod_phi = n_mp % phi
    frac = mod_phi / phi
    if float(frac) < 1e-50: continue
    powered = mp.power(frac, kappa_geo)
    theta = float(phi * powered) % 1.0 * N  # Scale to [0,N) for binning
    bin_idx = int(theta / interval_size)
    if 0 <= bin_idx < 50:
        geo_primes_count[bin_idx] += 1

max_geo = np.max(geo_primes_count)
pnt_avg = np.mean(pnt_expected)
enhancement = ((max_geo / pnt_avg) - 1) * 100  # Relative to PNT

print(f'PNT avg per interval: {pnt_avg:.2f}')
print(f'Max geo primes in interval: {max_geo}')
print(f'Relative enhancement: {enhancement:.2f}%')

# Bootstrap (simplified on counts)
np.random.seed(42)
boot_data = []
for _ in range(1000):
    res_counts = np.random.multinomial(int(np.sum(geo_primes_count)), np.ones(50)/50)
    res_max = np.max(res_counts)
    res_enh = ((res_max / pnt_avg) - 1) * 100
    boot_data.append(res_enh)
ci_low, ci_high = np.percentile(boot_data, [2.5, 97.5])
print(f'95% CI: [{ci_low:.1f}%, {ci_high:.1f}%]')
