"""Lognormal-guided Fermat factorization stage."""

import math
from typing import Optional
from .model import ModelStore, Band
from .config import SearchPolicyConfig
from .utils import clamp_gap, sample_lognormal, is_perfect_square, isqrt


def lognormal_fermat_stage(
    N: int, model_store: ModelStore, cfg: SearchPolicyConfig, seed: Optional[int] = None
) -> Optional[int]:
    """
    Try to factor N using a Fermat-style search guided by lognormal offsets.

    Returns a non-trivial factor of N on success, or None on failure.
    """
    if N % 2 == 0:
        return 2

    p0 = isqrt(N)
    band = model_store.get_band_for_p(p0)
    if band is None:
        band = model_store.get_closest_band(p0)

    cumulative_offset = 0.0
    direction = 1

    for step in range(1, cfg.max_steps + 1):
        g = sample_lognormal(band.shape, band.scale, cfg.rng)
        g = clamp_gap(g, band)
        cumulative_offset += g * cfg.radius_scale

        if cfg.direction_mode == "ALTERNATE":
            direction = -direction
        elif cfg.direction_mode == "RANDOM":
            direction = cfg.rng.choice([-1, 1])

        x_candidate = p0 + direction * round(cumulative_offset)
        if x_candidate <= 0:
            continue

        y2 = x_candidate * x_candidate - N
        if y2 < 0:
            continue

        if is_perfect_square(y2):
            y = isqrt(y2)
            a = x_candidate - y
            b = x_candidate + y
            if a > 1 and N % a == 0:
                return a
            if b > 1 and N % b == 0:
                return b

    return None
