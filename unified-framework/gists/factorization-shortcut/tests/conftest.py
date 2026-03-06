"""
Pytest configuration and fixtures for Z5D Factorization Shortcut tests.
"""

import os
import pytest
from pathlib import Path


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


@pytest.fixture(scope="session")
def project_root():
    """Return path to project root."""
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture(scope="session")
def gist_dir():
    """Return path to factorization-shortcut gist directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session", autouse=True)
def check_z5d_binary():
    """Check Z5D binary exists before running tests."""
    z5d_path = os.environ.get(
        'Z5D_PRIME_GEN',
        str(Path(__file__).parent.parent.parent.parent / 'src/c/bin/z5d_prime_gen')
    )

    if not Path(z5d_path).exists():
        pytest.exit(
            f"Z5D binary not found at {z5d_path}.\n"
            f"Build it with: cd src/c && make z5d_prime_gen\n"
            f"Or set Z5D_PRIME_GEN environment variable.",
            returncode=1
        )

    print(f"\n✓ Using Z5D binary: {z5d_path}")


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary directory for test outputs."""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir
