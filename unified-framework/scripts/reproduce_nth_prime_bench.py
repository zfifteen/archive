# scripts/reproduce_nth_prime_bench.py
import numpy as np, matplotlib.pyplot as plt, csv, argparse

def load_csv(path):
    with open(path) as f:
        r = csv.DictReader(f)
        return [{k: float(v) for k, v in row.items()} for row in r]

def pctile(arr, q): return float(np.percentile(np.asarray(arr, float), q))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="results/comparators_nth_prime.csv")
    args = ap.parse_args()
    rows = load_csv(args.csv)

    k   = np.array([r["k"] for r in rows])
    ez  = np.array([r["err_z5d"] for r in rows])
    ezs = np.array([r["signed_err_z5d"] for r in rows])
    eli = np.array([r["err_li"] for r in rows])
    ea  = np.array([r["err_asymp4"] for r in rows])
    ed  = np.array([r["err_dusart_ub"] for r in rows])

    def summarize(name, e):
        print(f"{name}: median={pctile(e,50):.6f}%  p95={pctile(e,95):.6f}%")

    for name, e in [("Z5D", ez), ("li^{-1}", eli), ("asymp4", ea), ("Dusart_UB", ed)]:
        summarize(name, e)

    # Abs error vs log10(k)
    plt.figure()
    for name, e in [("Z5D", ez), ("li^{-1}", eli), ("asymp4", ea), ("Dusart_UB", ed)]:
        plt.plot(np.log10(k), e, marker="o", label=name)
    plt.xlabel("log10(k)"); plt.ylabel("Abs rel error (%)")
    plt.legend(); plt.tight_layout(); plt.savefig("error_vs_k.png")

    # Signed error (bias) for Z5D and Dusart
    plt.figure()
    plt.plot(k, ezs, marker="o", label="Z5D (signed)")
    plt.plot(k, np.sign(ed) * ed, marker="o", label="Dusart UB (signed, >0 expected)")
    plt.xscale("log")
    plt.axvspan(1e10, k.max() * 1.01, alpha=0.15, label="Extrapolation")
    plt.xlabel("k"); plt.ylabel("Signed rel error (%)")
    plt.legend(); plt.tight_layout(); plt.savefig("signed_error_vs_k.png")

if __name__ == "__main__":
    main()