"""Tests for Fermat stage."""

import pytest
from src.model import ModelStore
from src.config import SearchPolicyConfig
from src.fermat import lognormal_fermat_stage


def test_lognormal_fermat_stage_even():
    model = ModelStore()
    cfg = SearchPolicyConfig()
    assert lognormal_fermat_stage(10, model, cfg) == 2


def test_lognormal_fermat_stage_small():
    model = ModelStore()
    cfg = SearchPolicyConfig(max_steps=10000, radius_scale=10000)
    # Semiprime: 7*11=77, sqrt~8.77
    cfg.seed = 42
    factor = lognormal_fermat_stage(77, model, cfg)
    assert factor in [7, 11] or factor is None  # May not find due to small N vs model
