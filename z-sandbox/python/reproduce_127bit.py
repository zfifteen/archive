import mpmath
from mpmath import mpf, sqrt, exp, ln, pi, sin, cos, fabs, nint
import sys
import os
import json
import time

# Set precision
mpmath.mp.dps = 200

def D_J(theta, J):
    """Dirichlet kernel D_J(θ)."""
    if sin(theta / 2) == 0:
        return mpf(2 * J + 1)
    return sin((J + mpf(0.5)) * theta) / sin(theta / 2)

def run_factorization(N_str, num_samples, k_lo, k_hi, m_span, J, threshold_factor, emit_artifacts=False):
    N = mpf(N_str)
    log_N = ln(N)
    phi_conjugate = (mpf(1) + sqrt(5)) / 2 - 1
    dirichlet_threshold = threshold_factor * (2 * J + 1)
    candidates = set()
    candidate_count = 0
    accepted_count = 0
    start_time = time.time()

    print(f"Factoring N = {N_str}")
    print(f"Parameters: samples={num_samples}, k=[{k_lo}, {k_hi}], m_span={m_span}, J={J}, threshold={threshold_factor}")

    for n in range(num_samples):
        fractional_part = (n * phi_conjugate) % 1
        k = mpf(k_lo) + fractional_part * (mpf(k_hi) - mpf(k_lo))
        m0 = 0  # as per calculation

        for m in range(m0 - m_span, m0 + m_span + 1):
            if m == 0:
                continue

            p_hat = exp((log_N - 2 * pi * m / k) / 2)
            if not mpmath.isfinite(p_hat) or p_hat > sqrt(N) or p_hat < 2:
                continue

            p_int = int(nint(p_hat))
            theta = (log_N - 2 * ln(mpf(p_int))) * k / 2

            if fabs(D_J(theta, J)) >= dirichlet_threshold:
                candidates.add(p_int)
                accepted_count += 1
                print(f"Accepted: p_int={p_int}, theta={theta}, D_J={D_J(theta, J)}")

            candidate_count += 1

    elapsed = time.time() - start_time
    print(f"Search complete. {candidate_count} combinations scanned, {accepted_count} accepted, {len(candidates)} unique candidates. Time: {elapsed:.2f}s")

    # Check for factors
    found_factors = []
    for p in candidates:
        if p > 1 and int(N) % p == 0:
            q = int(N) // p
            found_factors.append((p, q))
            print(f"FOUND: p={p}, q={q}")

    if emit_artifacts:
        os.makedirs("artifacts_127bit", exist_ok=True)
        config = {
            "N": N_str,
            "num_samples": num_samples,
            "k_lo": k_lo,
            "k_hi": k_hi,
            "m_span": m_span,
            "J": J,
            "threshold_factor": threshold_factor,
            "mp_dps": mpmath.mp.dps
        }
        with open("artifacts_127bit/config.json", "w") as f:
            json.dump(config, f, indent=2)

        metrics = {
            "scanned_combinations": candidate_count,
            "accepted": accepted_count,
            "unique_candidates": len(candidates),
            "elapsed_seconds": elapsed,
            "found_factors": found_factors
        }
        with open("artifacts_127bit/metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

        with open("artifacts_127bit/candidates.txt", "w") as f:
            for c in sorted(candidates):
                f.write(f"{c}\n")

        # run.log is the stdout, but since we print, perhaps redirect when running.

    return found_factors

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-artifacts", action="store_true")
    parser.add_argument("--k-lo", type=float, default=0.25)
    parser.add_argument("--k-hi", type=float, default=0.45)
    parser.add_argument("--J", type=int, default=6)
    parser.add_argument("--threshold", type=float, default=0.92)
    parser.add_argument("--m-span", type=int, default=180)
    parser.add_argument("--samples", type=int, default=801)
    args = parser.parse_args()

    N_str = "137524771864208156028430259349934309717"
    found = run_factorization(
        N_str=N_str,
        num_samples=args.samples,
        k_lo=args.k_lo,
        k_hi=args.k_hi,
        m_span=args.m_span,
        J=args.J,
        threshold_factor=args.threshold,
        emit_artifacts=args.emit_artifacts
    )

    if found:
        print("SUCCESS: Factors found.")
    else:
        print("NOT FOUND: No factors found.")