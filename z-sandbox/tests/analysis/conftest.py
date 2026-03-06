"""
Pytest configuration and fixtures for zero-bias validation tests.
"""

import pytest
import json
import os
from pathlib import Path

@pytest.fixture
def zero_bias_target():
    """Fixture providing the 127-bit test target."""
    fixture_path = Path(__file__).parent / "fixtures" / "zero_bias" / "127bit_target.json"
    with open(fixture_path) as f:
        return json.load(f)

@pytest.fixture
def sample_config():
    """Fixture providing sample configuration data."""
    fixture_path = Path(__file__).parent / "fixtures" / "zero_bias" / "sample_config.json"
    with open(fixture_path) as f:
        return json.load(f)

def load_config_from_file(config_path):
    """Utility to load config.json from test output."""
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return None

def load_factors_from_file(factors_path):
    """Utility to load factors.txt from test output."""
    factors = {}
    if os.path.exists(factors_path):
        with open(factors_path) as f:
            for line in f:
                if line.strip():
                    key, value = line.split(" = ", 1)
                    factors[key.strip()] = value.strip()
    return factors

def validate_zero_bias_config(config):
    """Validate that config meets zero-bias requirements."""
    assert config["bias_present"] == False
    assert config["dirichlet_normalized"] == True
    assert config["snap_mode"] == "phase_corrected_nint"
    assert config["precision_digits"] >= 300
    assert config["seed"] == 42

@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture providing a temporary directory for test outputs."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir