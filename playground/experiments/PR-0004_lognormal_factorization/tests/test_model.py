"""Tests for model layer."""

import pytest
from src.model import ModelStore, Band


def test_get_band_for_p():
    model = ModelStore()
    assert model.get_band_for_p(500000).p_min == 100000
    assert model.get_band_for_p(5000000).p_min == 1000000
    assert model.get_band_for_p(50000000).p_min == 10000000
    assert model.get_band_for_p(500000000).p_min == 100000000
    assert model.get_band_for_p(50) is None  # Below range
    assert model.get_band_for_p(2000000000) is None  # Above range


def test_get_closest_band():
    model = ModelStore()
    assert model.get_closest_band(50).p_min == 100000  # Closest is first
    assert model.get_closest_band(2000000000).p_min == 100000000  # Closest is last
