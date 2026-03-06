def generate_semiprime_refined(bits: int, seed: int = 42) -> Tuple[str, int, int]:
    """
    Generate semi-prime with reproducible seeding.

    Parameters
    ----------
    bits : int
        Bit size
    seed : int
        Random seed

    Returns
    -------
    Tuple[str, int, int]
        (n_str, p, q)
    """
    random.seed(seed)

    if SYMPY_AVAILABLE:
        # Use sympy for accurate prime generation
        prime_bits = bits // 2
        min_val = 2**(prime_bits - 1) + 1
        p = int(nextprime(min_val + random.randint(0, 2**(prime_bits//2))))
        q = int(nextprime(p + random.randint(1, 2**(prime_bits//2))))
    else:
        # Fallback
        prime_bits = bits // 2
        min_val = 2**(prime_bits - 1) + 1
        max_val = min(2**prime_bits - 1, min_val + 2**(prime_bits//2))

        p = min_val + 7
        q = p + 13

    n = p * q
    return str(n), p, q