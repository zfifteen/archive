#!/usr/bin/env python3
"""
PURE RESONANCE interval clustering + integer snap (deterministic)
- mpmath-only math (no float casts)
- Build fuzzy log-space intervals per (k,m)
- Cluster overlaps across ≥K distinct k values
- Snap only at cluster centers with small wheel-sieved window and test divisibility
- Log TSV/JSONL rows to results/<date>.{tsv,jsonl}
"""
import os, sys, json, time, argparse
from mpmath import mp

DEFAULT_DPS = 256

def ln_p(logN, m, k):
    return mp.mpf('0.5')*logN - (mp.pi/k)*m

def build_intervals(N, ks, m_min, m_max, dm):
    logN = mp.log(N)
    intervals = []  # (k, m, l_center, l_lo, l_hi)
    dm = mp.mpf(dm)
    for k in ks:
        kmp = mp.mpf(k)
        # iterate m inclusively
        m = mp.mpf(m_min)
        while m <= m_max + mp.mpf('1e-30'):
            l = ln_p(logN, m, kmp)
            dl = (mp.pi/kmp)*dm
            intervals.append((kmp, m, l, l - dl, l + dl))
            m += dm
    return intervals

def cluster_intervals(intervals, min_distinct_k=3):
    # Sort by center l
    intervals.sort(key=lambda x: x[2])
    clusters = []
    cur = []
    for it in intervals:
        if not cur:
            cur = [it]
            continue
        # overlap if current start <= previous end
        if it[3] <= cur[-1][4]:
            cur.append(it)
        else:
            clusters.append(cur)
            cur = [it]
    if cur:
        clusters.append(cur)

    centers = []
    for cl in clusters:
        ks_in = {str(it[0]) for it in cl}
        if len(ks_in) >= min_distinct_k:
            # mean of l centers
            # arithmetic mean of centers (avoid mp.nsum over indices)
            l_sum = mp.mpf('0')
            for it in cl:
                l_sum += it[2]
            l_mean = l_sum / len(cl)
            centers.append(l_mean)
    return centers

# simple 2*3*5*7*11 wheel residues modulo 2310
WHEEL = 2*3*5*7*11
RESIDUES = [r for r in range(WHEEL) if all(r % p != 0 for p in (2,3,5,7,11))]

def wheel_candidates(center, R):
    lo = max(2, int(center - R))
    hi = int(center + R)
    # align to next residue class
    start = lo
    while start % WHEEL not in RESIDUES:
        start += 1
    for x in range(start, hi+1):
        if x % WHEEL in RESIDUES:
            yield x

def log_append(tsv_path, jsonl_path, row_dict):
    # TSV header constraints
    tsv_header = 'timestamp\tmechanism\trel_distance\tabs_distance\tparams\tjson_notes\truntime_s\n'
    if not os.path.exists(tsv_path):
        with open(tsv_path, 'w') as f:
            f.write(f"# commit NA\n# python NA\n# mpmath {mp.dps}\n")
            f.write(tsv_header)
    if not os.path.exists(jsonl_path):
        with open(jsonl_path, 'w') as f:
            f.write(json.dumps({"_comment": f"mpmath_dps={mp.mp.dps}"})+"\n")
    # Append
    ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    mech = 'interval_snap'
    rel = row_dict.get('rel_distance', '')
    absd = row_dict.get('abs_distance', '')
    params = json.dumps(row_dict.get('params', {}), sort_keys=True)
    notes = json.dumps(row_dict.get('notes', {}), sort_keys=True)
    rt = f"{row_dict.get('runtime_s', 0):.3f}"
    with open(tsv_path, 'a') as f:
        f.write(f"{ts}\t{mech}\t{rel}\t{absd}\t{params}\t{notes}\t{rt}\n")
    with open(jsonl_path, 'a') as f:
        f.write(json.dumps({"timestamp": ts, "mechanism": mech, **row_dict}, sort_keys=True)+"\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=str, required=True)
    ap.add_argument('--dps', type=int, default=DEFAULT_DPS)
    ap.add_argument('--k-min', type=str, default='0.27')
    ap.add_argument('--k-max', type=str, default='0.33')
    ap.add_argument('--k-step', type=str, default='0.001')
    ap.add_argument('--m-range', type=str, default='10.0')
    ap.add_argument('--dm', type=str, default='0.0005')
    ap.add_argument('--min-k-cluster', type=int, default=3)
    ap.add_argument('--snap-radius', type=int, default=10**6)
    ap.add_argument('--date', type=str, default=time.strftime('%Y-%m-%d'))
    args = ap.parse_args()

    mp.dps = int(args.dps)
    N = mp.mpf(args.n)
    k_min = mp.mpf(args.k_min)
    k_max = mp.mpf(args.k_max)
    k_step = mp.mpf(args.k_step)
    m_range = mp.mpf(args.m_range)
    dm = mp.mpf(args.dm)

    ks = []
    k = k_min
    while k <= k_max + mp.mpf('1e-30'):
        ks.append(k)
        k += k_step

    t0 = time.time()
    intervals = build_intervals(N, ks, -m_range, m_range, dm)
    centers = cluster_intervals(intervals, min_distinct_k=args.min_k_cluster)

    # integer snap around centers
    found = None
    checked = 0
    for lc in centers:
        p_star = int(mp.nint(mp.e**lc))
        for cand in wheel_candidates(p_star, args.snap_radius):
            checked += 1
            # divisibility in Python int (convert once)
            c = int(cand)
            n_int = int(args.n)
            if c > 1 and c < n_int and n_int % c == 0:
                found = (c, n_int // c)
                break
        if found:
            break

    runtime = time.time() - t0
    # Log
    date = args.date
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    results_dir = os.path.abspath(results_dir)
    os.makedirs(results_dir, exist_ok=True)
    tsv_path = os.path.join(results_dir, f"{date}.tsv")
    jsonl_path = os.path.join(results_dir, f"{date}.jsonl")

    row = {
        'rel_distance': 0 if found else '',
        'abs_distance': 0 if found else '',
        'params': {
            'dps': int(args.dps), 'k_min': str(args.k_min), 'k_max': str(args.k_max), 'k_step': str(args.k_step),
            'm_range': str(args.m_range), 'dm': str(args.dm), 'min_k_cluster': args.min_k_cluster,
            'snap_radius': args.snap_radius, 'centers': len(centers), 'intervals': len(intervals)
        },
        'notes': {
            'found': bool(found), 'checked': checked,
            'factor': found[0] if found else None, 'cofactor': found[1] if found else None
        },
        'runtime_s': runtime
    }
    log_append(tsv_path, jsonl_path, row)

    # Also write centers file
    centers_path = os.path.join(results_dir, f"interval_centers_{date}.tsv")
    with open(centers_path, 'w') as f:
        f.write('idx\tl_center\tp_star\n')
        for i, lc in enumerate(centers):
            p_star = int(mp.nint(mp.e**lc))
            f.write(f"{i}\t{mp.nstr(lc, 30)}\t{p_star}\n")

if __name__ == '__main__':
    main()
