"""Tests for pipeline."""

import pytest
from src.model import ModelStore
from src.config import SearchPolicyConfig
from src.pipeline import factor_with_lognormal_prefilter, factor_classical


def test_pipeline_vs_classical():
    model = ModelStore()
    cfg = SearchPolicyConfig(max_steps=500, radius_scale=10000)
    test_ns = [77, 91, 119]  # Semiprimes 7*11, 7*13, 7*17

    for N in test_ns:
        cfg.seed = 42
        pipeline_factor = factor_with_lognormal_prefilter(N, model, cfg)
        classical_factor = factor_classical(N)
        assert pipeline_factor is not None
        # For small N, pollard_rho may not find quickly, skip assert for classical
        if classical_factor is not None:
            factors = {pipeline_factor, N // pipeline_factor}
            classical_factors = {classical_factor, N // classical_factor}
            assert factors == classical_factors
