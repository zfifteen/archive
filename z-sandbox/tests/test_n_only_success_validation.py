#!/usr/bin/env python3
"""
Automated validation test for N-only geometric resonance success case.

This test reproduces the validated successful factorization from 2025-11-06
and verifies all success criteria.

Test Target: N = 137524771864208156028430259349934309717 (127-bit)
Expected Factors: p = 10508623501177419659, q = 13086849276577416863
Expected Runtime: ~130 seconds (tolerance: 100-200 seconds)

Usage:
    python3 tests/test_n_only_success_validation.py
    pytest tests/test_n_only_success_validation.py -v
"""

import pytest
import subprocess
import sys
import os
import json
import time
from pathlib import Path

# Expected values from validated success run
EXPECTED_N = 137524771864208156028430259349934309717
EXPECTED_P = 10508623501177419659
EXPECTED_Q = 13086849276577416863

# Tolerance ranges
MIN_RUNTIME_SECONDS = 60
MAX_RUNTIME_SECONDS = 300
MIN_CANDIDATES = 70000
MAX_CANDIDATES = 76000
MIN_CHECKED = 500
MAX_CHECKED = 700


@pytest.fixture
def artifact_dir():
    """Return path to geometric resonance artifact directory."""
    repo_root = Path(__file__).parent.parent
    return repo_root / "results" / "geometric_resonance_127bit"


@pytest.fixture
def method_script(artifact_dir):
    """Return path to method.py script."""
    script = artifact_dir / "method.py"
    assert script.exists(), f"method.py not found at {script}"
    return script


def test_artifacts_exist(artifact_dir):
    """Verify all required artifact files exist."""
    required_files = [
        "method.py",
        "config.json",
        "README.md",
        "run.log",
        "metrics.json",
        "candidates.txt",
        "checksums.txt"
    ]

    for filename in required_files:
        filepath = artifact_dir / filename
        assert filepath.exists(), f"Required artifact missing: {filename}"
        assert filepath.stat().st_size > 0, f"Artifact is empty: {filename}"


def test_config_parameters(artifact_dir):
    """Verify configuration parameters match validated success case."""
    config_file = artifact_dir / "config.json"
    with open(config_file) as f:
        config = json.load(f)

    # Verify precision
    assert config["precision"]["mp_dps"] == 200, "Precision should be 200"

    # Verify QMC sampling
    qmc = config["qmc_sampling"]
    assert qmc["sampler"] == "golden_ratio_qmc", "Should use golden ratio QMC"
    assert qmc["num_samples"] == 801, "Should use 801 samples"

    # Verify k parameter range
    k_param = config["k_parameter"]
    assert k_param["k_lo"] == 0.25, "k_lo should be 0.25"
    assert k_param["k_hi"] == 0.45, "k_hi should be 0.45"

    # Verify mode scanning
    mode = config["mode_scanning"]
    assert mode["m_span"] == 180, "m_span should be 180"

    # Verify Dirichlet kernel
    dirichlet = config["dirichlet_kernel"]
    assert dirichlet["J"] == 6, "J should be 6"
    assert dirichlet["threshold_factor"] == 0.92, "Threshold should be 0.92"

    # Verify bias correction
    bias = config["bias_correction"]
    assert bias["bias_form"] == "zero", "Should use zero bias"


def test_method_imports_prohibited_libraries(method_script):
    """Verify method.py doesn't import prohibited factoring libraries."""
    with open(method_script) as f:
        content = f.read()

    prohibited = [
        "sympy.ntheory.factor",
        "gmpy2",
        "primefac",
        "factordb",
        "from sympy.ntheory import factorint",
        "from gmpy2 import",
    ]

    for lib in prohibited:
        assert lib not in content, f"Prohibited library found: {lib}"


def test_method_has_instrumentation(method_script):
    """Verify method.py contains verification instrumentation."""
    with open(method_script) as f:
        content = f.read()

    required_checks = [
        "_PROHIBITED_FACTORING",
        "VERIFICATION:",
        "Import check",
        "No prohibited",
    ]

    for check in required_checks:
        assert check in content, f"Missing instrumentation: {check}"


@pytest.mark.slow
def test_reproduce_success_case(method_script, artifact_dir, tmp_path):
    """
    Reproduce the successful factorization.

    This is the primary validation test that actually runs method.py
    and verifies it produces the correct factors.

    WARNING: This test takes ~2 minutes to run.
    """
    # Change to artifact directory (method.py writes to CWD)
    original_cwd = os.getcwd()
    os.chdir(artifact_dir)

    try:
        # Run method.py and capture output
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "method.py"],
            capture_output=True,
            text=True,
            timeout=MAX_RUNTIME_SECONDS
        )
        runtime = time.time() - start_time

        # Verify execution succeeded
        assert result.returncode == 0, f"method.py failed with code {result.returncode}\nSTDERR:\n{result.stderr}"

        # Verify runtime within tolerance
        assert MIN_RUNTIME_SECONDS <= runtime <= MAX_RUNTIME_SECONDS, \
            f"Runtime {runtime:.1f}s outside expected range [{MIN_RUNTIME_SECONDS}, {MAX_RUNTIME_SECONDS}]"

        # Verify output contains success message
        assert "SUCCESS: FACTORS FOUND" in result.stdout, "Success message not found in output"

        # Extract factors from output
        lines = result.stdout.strip().split('\n')

        # Find the final output section
        final_output_idx = None
        for i, line in enumerate(lines):
            if "FINAL OUTPUT" in line:
                final_output_idx = i
                break

        assert final_output_idx is not None, "FINAL OUTPUT section not found"

        # Extract p and q (should be last two non-empty lines)
        output_lines = [l for l in lines[final_output_idx:] if l.strip() and not l.startswith('=')]
        assert len(output_lines) >= 2, f"Could not find p and q in output: {output_lines}"

        p_str = output_lines[-2].strip()
        q_str = output_lines[-1].strip()

        p = int(p_str)
        q = int(q_str)

        # Ensure p < q
        if p > q:
            p, q = q, p

        # Verify factors match expected values
        assert p == EXPECTED_P, f"p mismatch: got {p}, expected {EXPECTED_P}"
        assert q == EXPECTED_Q, f"q mismatch: got {q}, expected {EXPECTED_Q}"

        # Verify p × q = N
        assert p * q == EXPECTED_N, f"p × q != N: {p * q} != {EXPECTED_N}"

        # Verify metrics file was created
        metrics_file = Path("run_metrics.json")
        assert metrics_file.exists(), "run_metrics.json not created"

        # Verify metrics
        with open(metrics_file) as f:
            metrics = json.load(f)

        assert metrics["success"] is True, "Metrics show failure"

        candidates_generated = metrics["candidates_generated"]
        assert MIN_CANDIDATES <= candidates_generated <= MAX_CANDIDATES, \
            f"Candidates {candidates_generated} outside expected range [{MIN_CANDIDATES}, {MAX_CANDIDATES}]"

        candidates_checked = metrics["candidates_checked"]
        assert MIN_CHECKED <= candidates_checked <= MAX_CHECKED, \
            f"Checked {candidates_checked} outside expected range [{MIN_CHECKED}, {MAX_CHECKED}]"

        # Verify keep-to-tested ratio is reasonable
        ratio = metrics["kept_to_tested_ratio"]
        assert 0.20 <= ratio <= 0.30, f"Keep ratio {ratio} outside expected range [0.20, 0.30]"

        print(f"\n✓ SUCCESS: Reproduced factorization in {runtime:.1f}s")
        print(f"  Factors: p={p}, q={q}")
        print(f"  Candidates: {candidates_generated} generated, {candidates_checked} checked")
        print(f"  Ratio: {ratio:.4f}")

    finally:
        os.chdir(original_cwd)


def test_verify_primality():
    """Verify expected factors are actually prime."""
    try:
        from sympy import isprime
    except ImportError:
        pytest.skip("sympy not installed, skipping primality test")

    assert isprime(EXPECTED_P), f"p={EXPECTED_P} is not prime"
    assert isprime(EXPECTED_Q), f"q={EXPECTED_Q} is not prime"


def test_verify_factorization():
    """Verify p × q = N."""
    assert EXPECTED_P * EXPECTED_Q == EXPECTED_N, "p × q != N"


def test_verify_bit_lengths():
    """Verify factor bit lengths."""
    p_bits = EXPECTED_P.bit_length()
    q_bits = EXPECTED_Q.bit_length()
    n_bits = EXPECTED_N.bit_length()

    assert p_bits == 64, f"p should be 64-bit, got {p_bits}"
    assert q_bits == 64, f"q should be 64-bit, got {q_bits}"
    assert n_bits == 127, f"N should be 127-bit, got {n_bits}"


def test_verify_balance():
    """Verify factors straddle sqrt(N)."""
    import math
    sqrt_n = math.sqrt(EXPECTED_N)

    # One factor should be below sqrt(N), one above
    assert EXPECTED_P < sqrt_n < EXPECTED_Q, \
        f"Factors don't straddle sqrt(N): p={EXPECTED_P}, sqrt(N)={sqrt_n:.2e}, q={EXPECTED_Q}"


def test_method_integrity_verification(artifact_dir):
    """Verify method integrity checks from metrics."""
    metrics_file = artifact_dir / "metrics.json"
    with open(metrics_file) as f:
        metrics = json.load(f)

    integrity = metrics.get("method_integrity", {})

    # Verify no classical methods used
    assert integrity.get("pure_geometric") is True, "Should be pure geometric"
    assert integrity.get("no_ecm") is True, "Should not use ECM"
    assert integrity.get("no_nfs") is True, "Should not use NFS"
    assert integrity.get("no_pollard") is True, "Should not use Pollard"
    assert integrity.get("no_gcd_cycles") is True, "Should not use GCD cycles"
    assert integrity.get("no_library_factoring") is True, "Should not use library factoring"

    # Verify geometric methods used
    assert integrity.get("qmc_sampling") == "golden_ratio", "Should use golden ratio QMC"
    assert integrity.get("resonance_detection") == "dirichlet_kernel", "Should use Dirichlet kernel"
    assert integrity.get("divisibility_check") == "final_stage_only", "Should only check divisibility at final stage"


if __name__ == "__main__":
    # Allow running directly for quick validation
    print("N-Only Success Validation Test")
    print("=" * 70)
    print(f"Target: N = {EXPECTED_N}")
    print(f"Expected: p = {EXPECTED_P}, q = {EXPECTED_Q}")
    print()

    # Run pytest with verbose output
    sys.exit(pytest.main([__file__, "-v", "-s"]))
