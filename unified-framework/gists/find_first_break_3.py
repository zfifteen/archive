
from decimal import Decimal, getcontext
getcontext().prec = 80
PHI  = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
PHI2 = PHI * PHI
PHI3 = PHI2 * PHI

def _floor_dec(x: Decimal) -> int:
    return int(x.to_integral_value(rounding="ROUND_FLOOR"))

def geodesic_triplet(n: int) -> list[int]:
    """
    Three geodesic-chosen bases for this n: one from each φ-power family.
    Seeds are n-specific (no global k), then mapped to [2, n-2].
    """
    if n <= 4:
        return [2, 3, 5][:max(0, n-2)]
    M = n - 3
    seeds = []
    for alpha in (PHI, PHI2, PHI3):
        u = _floor_dec(alpha * Decimal(n))      # n-specific geodesic seed
        a = 2 + (u % M)                         # map to [2, n-2]
        # ensure distinct bases; simple de-dupe bump if needed
        while a in seeds:
            u += 1
            a = 2 + (u % M)
        seeds.append(a)
    return seeds

def mr_core(n: int, bases: list[int]) -> bool:
    if n < 2: return False
    if n in (2,3): return True
    if n % 2 == 0 or n % 3 == 0: return False
    d, r = n-1, 0
    while d % 2 == 0: d//=2; r+=1
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            continue
        for _ in range(r-1):
            x = (x*x) % n
            if x == n-1:
                break
        else:
            return False
    return True

def gbmr3(n: int) -> bool:
    return mr_core(n, geodesic_triplet(n))


def gbmr(n: int, m: int = 3) -> bool:
    return mr_core(n, beatty_witnesses(n, m))

CARMICHAEL_LE_1E6 = [
    561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341, 41041, 46657,
    52633, 62745, 63973, 75361, 101101, 115921, 126217, 162401, 172081, 188461,
    252601, 278545, 294409, 314821, 334153, 340561, 399001, 410041, 449065, 488881,
    512461, 530881, 552721, 656601, 658801, 670033, 748657, 825265, 838201, 852841,
    997633
]

def find_first_break(limit_scan: int = 1_000_000):
    for n in CARMICHAEL_LE_1E6:
        if gbmr(n, 3):
            return ("carmichael<=1e6", n, False, True, beatty_witnesses(n, 3))
    for n in range(3, limit_scan + 1, 2):
        t = sp.isprime(n)
        p = gbmr(n, 3)
        if t != p:
            return ("odd_scan", n, bool(t), bool(p), beatty_witnesses(n, 3))
    return None

if __name__ == "__main__":
    import sys
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    print(find_first_break(L))
