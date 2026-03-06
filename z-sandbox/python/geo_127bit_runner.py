#!/usr/bin/env python3
import mpmath as mp
mp.mp.dps = 200
N = 137524771864208156028430259349934309717

k = mp.mpf(0.3)
m_min = -1000
m_max = 1000
m_step = 0.01

m_current = mp.mpf(m_min)
found = False
count = 0
while m_current <= mp.mpf(m_max):
    log_p = (mp.log(mp.mpf(N)) - (2 * mp.pi * m_current) / k) / 2
    p_hat = mp.exp(log_p)
    p_int = int(mp.nint(p_hat))
    if p_int > 1 and N % p_int == 0:
        q = N // p_int
        print(f"Found factor: p={p_int}, q={q}")
        found = True
        break
    m_current += mp.mpf(m_step)
    count += 1
    if count % 10000 == 0:
        print(f"Checked {count} m values")

if not found:
    print("No factor found in range")

print(f"Total checked: {count}")