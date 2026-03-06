def theta_prime_z5d(n: mpmath.mpf, k_star: mpmath.mpf = KAPPA_STAR) -> mpmath.mpf:
    """
    Compute θ'(n, k*) transformation for Z5D framework
    θ'(n,k) = φ · ((n mod φ)/φ)^k
    """
    n_mod_phi = mpmath.fmod(n, GOLDEN_PHI)
    ratio = n_mod_phi / GOLDEN_PHI
    return GOLDEN_PHI * mpmath.power(ratio, k_star)