"""Lognormal candidate pre-filter."""

from typing import List, Optional
from .model import ModelStore, Band
from .config import SearchPolicyConfig
from .utils import clamp_gap, sample_lognormal, pollard_rho, isqrt


def probably_prime(n: int, witnesses: List[int] = [2, 3, 5, 7, 11, 13, 23]) -> bool:
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^s * d
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    for a in witnesses:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_lognormal_offsets(
    p0: int, band: Band, cfg: SearchPolicyConfig, seed: Optional[int] = None
) -> List[int]:
    """Generate integer offsets around p0 based on lognormal model."""
    offsets = []
    cumulative_offset = 0.0
    direction = 1

    for _ in range(cfg.max_steps):
        g = sample_lognormal(band.shape, band.scale, cfg.rng)
        g = clamp_gap(g, band)
        cumulative_offset += g * cfg.radius_scale

        if cfg.direction_mode == "ALTERNATE":
            direction = -direction
        elif cfg.direction_mode == "RANDOM":
            direction = cfg.rng.choice([-1, 1])

        off = direction * round(cumulative_offset)
        offsets.append(off)

    return offsets


def factor_with_candidate_prefilter(
    N: int, model_store: ModelStore, cfg: SearchPolicyConfig, seed: Optional[int] = None
) -> Optional[int]:
    """
    Use lognormal model to generate candidate offsets, test as factors, then fallback.
    """
    if N % 2 == 0:
        return 2

    p0 = isqrt(N)
    band = model_store.get_band_for_p(p0)
    if band is None:
        band = model_store.get_closest_band(p0)

    offsets = generate_lognormal_offsets(p0, band, cfg, seed)

    for off in offsets:
        q_candidate = p0 + off
        if q_candidate <= 1:
            continue
        if probably_prime(q_candidate) and N % q_candidate == 0:
            return q_candidate

    # Fallback
    return pollard_rho(N)
