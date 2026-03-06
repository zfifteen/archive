"""Tests for utilities."""

import random
import pytest
from src.model import Band
from src.utils import sample_lognormal, clamp_gap, is_perfect_square, pollard_rho


def test_sample_lognormal():
    band = Band(100000, 1000000, 1.3, 1e-4)
    rng = random.Random(42)
    samples = [sample_lognormal(band.shape, band.scale, rng) for _ in range(100)]
    assert all(s > 0 for s in samples)


def test_clamp_gap():
    band = Band(100000, 1000000, 1.3, 1e-4)
    assert clamp_gap(0.5, band) == 0.01  # Clamped down to generic max (100*scale=0.01)
    assert clamp_gap(0.001, band) == 0.001  # Within
    assert clamp_gap(0.000005, band) == 0.000005  # Above min (scale/100=1e-6)


def test_is_perfect_square():
    assert is_perfect_square(4)
    assert is_perfect_square(9)
    assert not is_perfect_square(8)
    assert is_perfect_square(1)


def test_pollard_rho():
    assert pollard_rho(15) == 3 or pollard_rho(15) == 5
    assert pollard_rho(9) == 3
    assert pollard_rho(2) == 2
    assert pollard_rho(1) is None
