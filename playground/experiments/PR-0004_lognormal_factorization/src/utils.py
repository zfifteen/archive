"""Utilities for sampling and factorization helpers."""

import math
import random
from typing import Optional
from .model import Band


def sample_lognormal(shape: float, scale: float, rng: random.Random) -> float:
    """Sample from lognormal distribution (loc=0)."""
    # Using Box-Muller transform for normal
    u1 = rng.random()
    u2 = rng.random()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return scale * math.exp(shape * z)


def clamp_gap(gap: float, band: Band) -> float:
    """Clamp gap to band limits or generic range."""
    if band.min_gap is not None and band.max_gap is not None:
        return max(band.min_gap, min(gap, band.max_gap))
    else:
        # Generic clamp: [scale/100, 100 * scale]
        return max(band.scale / 100, min(gap, 100 * band.scale))


def is_perfect_square(n: int) -> bool:
    """Check if n is a perfect square."""
    if n < 0:
        return False
    root = math.isqrt(n)
    return root * root == n


def isqrt(n: int) -> int:
    """Integer square root."""
    return math.isqrt(n)


def gcd(a: int, b: int) -> int:
    """Greatest common divisor."""
    while b:
        a, b = b, a % b
    return a


def pollard_rho(N: int, max_c: int = 5) -> Optional[int]:
    """Simple Pollard Rho factorization with multiple c tries."""
    if N % 2 == 0:
        return 2
    if N < 2:
        return None

    for c in range(1, max_c + 1):
        x = 3
        y = 3
        d = 1
        iterations = 0
        max_iterations = 10000  # Prevent infinite loop per c

        while d == 1 and iterations < max_iterations:
            x = (x * x + c) % N
            y = (y * y + c) % N
            y = (y * y + c) % N
            d = gcd(abs(x - y), N)
            iterations += 1

        if d != 1 and d != N:
            return d

    return None  # Not factored
