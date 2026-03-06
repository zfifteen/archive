def z5d_prime_estimate(k: float) -> float:
    """
    Z5D prime estimation (from rsa_probe_validation).
    """
    mp_k = mp.mpf(k)
    ln_k = mp.log(mp_k)
    ln_ln_k = mp.log(ln_k)

    # Enhanced PNT
    pnt = mp_k * (ln_k + ln_ln_k - 1 + (ln_ln_k - 2)/ln_k)

    # Geodesic modulation
    geo_mod = 0.3 * mp.log(mp_k + 1) / mp.exp(2)

    # Z5D corrections
    dk = 2 * pnt * mp.mpf(-0.00247)
    ek = pnt * mp.mpf(0.04449) * geo_mod

    result = pnt + dk + ek
    return float(result.real) if hasattr(result, 'real') else float(result)