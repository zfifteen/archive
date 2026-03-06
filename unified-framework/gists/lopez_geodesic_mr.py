#!/usr/bin/env python3
# compare_lopez_vs_standard_mr.py
# Zero-arg defaults: compare geodesic-only vs standard S64 on [3, 1_000_000], m=4

import time, argparse, hashlib

# --- Proven 64-bit deterministic base set (oracle + "standard MR") ---
S64 = [2,3,5,7,11,13,17,19,23,29,31,37]

# --- GCD ---
def egcd(a,b):
    while b: a,b = b, a%b
    return a

# --- Geodesic witnesses (integer-only Weyl step ~ 2^64/φ: 0x9E3779B97F4A7C15) ---
STEP64 = 0x9E3779B97F4A7C15  # low-discrepancy "golden" increment (Weyl sequence)
def geodesic_witnesses(n:int, m:int)->list[int]:
    if n <= 4: return [2][:max(0,m)]
    out, seen = [], set()
    frac = 0
    span = n - 3
    mask = (1<<64) - 1
    for _ in range(m):
        frac = (frac + STEP64) & mask
        a = 2 + ((frac * span) >> 64)  # maps to [2, n-1]
        if 2 <= a < n and a not in seen and egcd(a,n)==1:
            seen.add(a); out.append(a)
    return out

# --- Miller–Rabin core (shared). Tracks bases used and squarings for comparison. ---
def _decompose(nm1:int):
    r=0; d=nm1
    while (d & 1)==0: r+=1; d//=2
    return r,d

def mr_with_bases(n:int, bases:list[int]):
    """Return (is_probable_prime, bases_used, squarings)."""
    if n < 2: return (False, 0, 0)
    # small-prime screen (same for both variants)
    for p in S64:
        if n == p: return (True, 0, 0)
        if n % p == 0 and n != p: return (False, 0, 0)
    r, d = _decompose(n-1)
    squarings = 0
    used = 0
    for a in bases:
        if a <= 1 or a >= n: continue
        used += 1
        x = pow(a, d, n)
        if x == 1 or x == n-1: continue
        for _ in range(r-1):
            x = (x*x) % n
            squarings += 1
            if x == n-1:
                break
        else:
            return (False, used, squarings)
    return (True, used, squarings)

def oracle_is_prime_u64(n:int)->bool:
    return mr_with_bases(n, S64)[0]

# --- Runner: compare geodesic-only vs standard (S64) ---
def compare(n_from=3, n_to=1_000_000, m=4, list_first_fail=3, log=None):
    t0=time.perf_counter()
    geo_ok=geo_fp=geo_fn=0
    std_ok=0  # std==oracle for n<2^64 by theorem
    geo_bases=geo_squar=0
    std_bases=std_squar=0
    fails=[]
    for n in range(n_from|1, n_to+1, 2):
        truth = oracle_is_prime_u64(n)          # ground truth (proved for n<2^64)
        geo_res, gb, gsq = mr_with_bases(n, geodesic_witnesses(n, m))
        std_res, sb, ssq = mr_with_bases(n, S64)
        geo_bases += gb; geo_squar += gsq
        std_bases += sb; std_squar += ssq
        if std_res == truth: std_ok += 1
        # classify geodesic outcome
        if geo_res == truth:
            geo_ok += 1
        else:
            if truth: geo_fn += 1   # prime mislabeled composite
            else:     geo_fp += 1   # composite mislabeled prime
            if len(fails) < list_first_fail:
                fails.append((n, truth, geo_res, geodesic_witnesses(n, m)))
    t1=time.perf_counter()

    total = (n_to - (n_from|1))//2 + 1
    out = {
        "range":[n_from, n_to],
        "m": m,
        "tested": total,
        "geo_ok": geo_ok,
        "geo_fp": geo_fp,
        "geo_fn": geo_fn,
        "geo_acc": geo_ok/total if total else 0.0,
        "std_ok": std_ok,
        "std_acc": std_ok/total if total else 0.0,
        "geo_bases_avg": geo_bases/total if total else 0.0,
        "std_bases_avg": std_bases/total if total else 0.0,
        "geo_squar_avg": geo_squar/total if total else 0.0,
        "std_squar_avg": std_squar/total if total else 0.0,
        "elapsed_sec": t1-t0,
        "first_fail_examples": fails,
    }
    if log:
        h = hashlib.sha256(str(out).encode()).hexdigest()
        with open(log, "w") as f:
            f.write(str(out)+"\nSHA256:"+h+"\n")
        out["log_sha256"]=h
    return out

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--from", dest="n_from", type=int, default=3)
    ap.add_argument("--to", dest="n_to", type=int, default=1_000_000)
    ap.add_argument("--m", dest="m", type=int, default=4)
    ap.add_argument("--log", dest="log", type=str, default=None)
    args = ap.parse_args()

    res = compare(args.n_from, args.n_to, args.m, log=args.log)
    # Pretty print (compact)
    print(f"Range [{res['range'][0]}, {res['range'][1]}], m={res['m']}, tested={res['tested']}")
    print(f"Geodesic-only: acc={res['geo_acc']:.6f}, FP={res['geo_fp']}, FN={res['geo_fn']}, "
          f"avg_bases={res['geo_bases_avg']:.2f}, avg_squarings={res['geo_squar_avg']:.2f}")
    print(f"Standard S64:  acc={res['std_acc']:.6f}, (provably correct <2^64), "
          f"avg_bases={res['std_bases_avg']:.2f}, avg_squarings={res['std_squar_avg']:.2f}")
    if res["first_fail_examples"]:
        print("First failures (n, truth_is_prime, geo_result, witnesses):")
        for tup in res["first_fail_examples"]:
            print("  ", tup)
    print(f"Elapsed: {res['elapsed_sec']:.3f}s")
    if 'log_sha256' in res:
        print(f"Log SHA256: {res['log_sha256']}")

if __name__ == "__main__":
    main()
