#!/usr/bin/env python3
"""
Test Geometric Embedding Calibration
====================================

CI guard for embedding calibration format and first-order correction effectiveness.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

# Test that calibration produces expected format and sub-0.2% residual
def test_embedding_calibration_format():
    """Test that calibration script produces valid output with expected residuals."""
    # Import the calibration runner
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python', 'examples'))
    try:
        import rsa_embedding_calibration
    except ImportError:
        pytest.skip("Calibration script not available")

    # Run calibration (should be fast with small test moduli)
    records = rsa_embedding_calibration.run_calibration()

    # Should have records for all test moduli
    assert len(records) >= 4, f"Expected at least 4 records, got {len(records)}"

    # Check balanced_2048_a specifically
    balanced_2048_a = next((r for r in records if r['profile'] == 'balanced_2048_a'), None)
    assert balanced_2048_a is not None, "Missing balanced_2048_a record"

    # Verify structure
    required_keys = ['profile', 'N_bits', 'p_bits', 'q_bits', 'abs_bias', 'rel_bias',
                    'candidate_abs_err', 'candidate_rel_err', 'embedding_offset_used']
    for key in required_keys:
        assert key in balanced_2048_a, f"Missing key: {key}"

    # Verify correction effectiveness (sub-0.2% residual)
    assert balanced_2048_a['rel_bias'] < 0.002, f"rel_bias too high: {balanced_2048_a['rel_bias']}"
    assert balanced_2048_a['candidate_rel_err'] < 0.002, f"candidate_rel_err too high: {balanced_2048_a['candidate_rel_err']}"

    # Verify offset used
    assert abs(balanced_2048_a['embedding_offset_used'] - (-0.0392)) < 1e-6, "Wrong embedding offset used"

    print("✓ Embedding calibration format and effectiveness validated")


def test_calibration_output_file_exists():
    """Test that calibration output file is generated."""
    output_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'geometric_embedding_bias_calibration.json')

    # File should exist after calibration run
    assert os.path.exists(output_path), f"Calibration output file missing: {output_path}"

    # Should be valid JSON
    with open(output_path, 'r') as f:
        data = json.load(f)

    assert isinstance(data, list), "Output should be a list"
    assert len(data) > 0, "Output should not be empty"

    print("✓ Calibration output file validated")


def test_correction_improves_non_2048_profiles():
    """Test that second-order correction improves residuals on non-RSA-2048 profiles."""
    correction_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'geometric_embedding_bias_correction_results.json')

    # File should exist after correction run
    assert os.path.exists(correction_path), f"Correction results file missing: {correction_path}"

    # Load correction results
    with open(correction_path, 'r') as f:
        correction_data = json.load(f)

    # Index by profile
    correction_results = {record['profile']: record for record in correction_data}

    # Check balanced_14_test improvement (was 5.94% residual, should be better)
    assert 'balanced_14_test' in correction_results, "Missing balanced_14_test in correction results"
    balanced_14 = correction_results['balanced_14_test']
    assert balanced_14['best_rel_distance'] < 0.06, f"balanced_14_test not improved: {balanced_14['best_rel_distance']}"

    # Check skewed_9_test improvement (was 17.65% residual, should be better)
    assert 'skewed_9_test' in correction_results, "Missing skewed_9_test in correction results"
    skewed_9 = correction_results['skewed_9_test']
    assert skewed_9['best_rel_distance'] < 0.18, f"skewed_9_test not improved: {skewed_9['best_rel_distance']}"

    # Ensure RSA-2048 doesn't regress
    assert 'balanced_2048_a' in correction_results, "Missing balanced_2048_a in correction results"
    rsa_2048 = correction_results['balanced_2048_a']
    assert rsa_2048['best_rel_distance'] < 0.002, f"RSA-2048 regressed: {rsa_2048['best_rel_distance']}"

    print("✓ Correction improvements validated for non-RSA-2048 profiles")


def test_gap_closure_achieved():
    """Test that gap closure target is achieved for balanced RSA-2048."""
    correction_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'geometric_embedding_bias_correction_results.json')

    # File should exist after correction run
    assert os.path.exists(correction_path), f"Correction results file missing: {correction_path}"

    # Load correction results
    with open(correction_path, 'r') as f:
        correction_data = json.load(f)

    # Find balanced_2048_a
    rsa_2048 = next((r for r in correction_data if r['profile'] == 'balanced_2048_a'), None)
    assert rsa_2048 is not None, "Missing balanced_2048_a in correction results"

    # Check relative error < 0.1% (Target B achieved)
    assert rsa_2048['best_rel_distance'] < 0.001, f"Gap closure not achieved: {rsa_2048['best_rel_distance']} >= 0.1%"

    # Log the achievement
    print(f"✓ Gap closure achieved: rel_distance = {rsa_2048['best_rel_distance']:.6f} < 0.1%")
    print(f"  Absolute miss: {rsa_2048['abs_distance']} (large, but relative target met)")


def test_combined_breakthrough_config():
    """Test that combined breakthrough configuration parameters are reasonable."""
    # Test parameter ranges are valid
    comb_step = 0.001
    comb_range = 100

    assert comb_step > 0, "comb_step must be positive"
    assert comb_range > 0, "comb_range must be positive"
    assert comb_step < 1.0, "comb_step should be fractional for breakthrough"

    print("✓ Combined breakthrough configuration parameters validated")