# bench/bench_arctan_half_angle.py
import time
import random
import mpmath as mp

mp.mp.dps = 50

def raw(x):
    return mp.atan((mp.sqrt(1 + x*x) - 1)/x)

def halfangle(x):
    return 0.5 * mp.atan(x)

def bench(fn, xs, iters=5):
    best = 1e9
    for _ in range(iters):
        t0 = time.perf_counter()
        s = sum(fn(x) for x in xs)  # direct evaluation, more efficient
        best = min(best, time.perf_counter() - t0)
    return best

if __name__ == "__main__":
    random.seed(1337)  # for reproducibility
    xs = [mp.mpf(str(10**random.uniform(-3, 3))) for _ in range(10000)]
    t_raw = bench(raw, xs)
    t_half = bench(halfangle, xs)
    print(f"raw arg time:  {t_raw:.6f}s")
    print(f"half-angle:    {t_half:.6f}s")