#!/usr/bin/env python3
"""
Geometric Resonance 127-bit Factorization
Fixed implementation based on successful method.py
"""

from mpmath import mp, mpf, mpc, log, exp, pi, nint, sqrt
import mpmath.libmp
import math

# Force pure Python backend (disable gmpy2)
mpmath.libmp.backend.BACKEND = 'python'

# Set precision
mp.dps = 200


def dirichlet_kernel(theta, J=6):
    """
    Dirichlet kernel for resonance detection.
    D_J(θ) = Σ_{j=-J}^{J} e^{ijθ}
    """
    s = mpc(0)
    for j in range(-J, J + 1):
        s += exp(1j * mpf(j) * theta)
    return s


def bias(k):
    """Phase bias correction term (zero for this run)."""
    return mpf('0.0')


def resonance_candidates(N, num_samples=801, k_lo=0.25, k_hi=0.45, m_span=180, J=6, progress=True):
    """
    Generate prime candidates via geometric resonance scanning.
    """
    LN = log(N)
    sqrtN = sqrt(N)
    cands = set()

    # Golden ratio conjugate
    phi_conjugate = (mpf(1) + sqrt(5)) / 2 - 1

    # Pre-compute threshold
    threshold = (2 * J + 1) * mpf('0.92')

    total_tested = 0

    for n in range(num_samples):
        if progress and n % 100 == 0:
            print(f"  QMC sample {n}/{num_samples}, candidates: {len(cands)}", flush=True)

        # Van der Corput sequence in golden ratio base
        u_n = math.modf(n * float(phi_conjugate))[0]

        # Map to k range
        k = mpf(k_lo) + mpf(u_n) * (mpf(k_hi) - mpf(k_lo))

        # Central mode from geometric formula
        m0 = nint((k * (LN - 2 * log(sqrtN))) / (2 * pi))

        b = bias(k)

        # Scan modes around m0
        for dm in range(-m_span, m_span + 1):
            m = m0 + dm
            total_tested += 1

            # Comb formula
            p_hat = exp((LN - (2 * pi * (m + b)) / k) / 2)

            # Resonance angle
            theta = (LN - 2 * log(p_hat)) * k / 2

            # Dirichlet kernel evaluation
            if abs(dirichlet_kernel(theta, J=J)) >= threshold:
                p_int = int(nint(p_hat))
                if p_int > 1:
                    cands.add(p_int)

    print(f"  Total positions tested: {total_tested}")
    print(f"  Candidates generated: {len(cands)}")
    print(f"  Keep-to-tested ratio: {len(cands)/total_tested:.6f}")

    return sorted(cands), total_tested


def main():
    """Main execution."""
    N_int = 137524771864208156028430259349934309717

    print(f"Factoring N = {N_int}")
    print(f"N bit length: {N_int.bit_length()} bits\n")

    N = mpf(N_int)

    print("Starting candidate generation...")
    cands, total_tested = resonance_candidates(
        N,
        num_samples=801,
        k_lo=0.25,
        k_hi=0.45,
        m_span=180,
        J=6,
        progress=True
    )

    print(f"\nCandidate generation complete")
    print()

    # DEBUG: Check if expected factors are in candidate list
    expected_p = 10508623501177419659
    expected_q = 13086849276577416863
    print(f"DEBUG: Checking for expected factors...")
    print(f"DEBUG:   p={expected_p} in candidates: {expected_p in cands}")
    print(f"DEBUG:   q={expected_q} in candidates: {expected_q in cands}")
    if expected_p in cands:
        print(f"DEBUG:   p is at position {cands.index(expected_p) + 1}")
    if expected_q in cands:
        print(f"DEBUG:   q is at position {cands.index(expected_q) + 1}")
    print()

    # Check divisibility
    print("Starting divisibility checks...")
    for i, p in enumerate(cands):
        if i % 1000 == 0 and i > 0:
            print(f"  Checked {i}/{len(cands)} candidates...", flush=True)

        if N_int % p == 0:
            q = N_int // p

            print()
            print("=" * 70)
            print("SUCCESS: FACTORS FOUND")
            print("=" * 70)
            print(f"p = {p}")
            print(f"q = {q}")
            print(f"Factor found at candidate #{i+1}")
            print()

            # Verification
            print("Verification:")
            print(f"  p × q == N: {p * q == N_int}")
            print(f"  N % p == 0: {N_int % p == 0}")
            print(f"  p primality: {mp.isprime(p)}")
            print(f"  q primality: {mp.isprime(q)}")

            return 0

    print()
    print("No factors found after checking all candidates")
    return 1


if __name__ == "__main__":
    exit(main())
