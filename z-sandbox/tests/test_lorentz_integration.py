#!/usr/bin/env python3
"""
Unit tests for Lorentz dilation integration in Z5D predictor.
"""

import sys
import math
sys.path.insert(0, 'python')

from z5d_predictor import z5d_predict, lorentz_gamma_from_L, z5d_predict_logL

def test_lorentz_gamma():
    """Test Lorentz gamma computation."""
    L = math.log(1e6)
    gamma = lorentz_gamma_from_L(L)
    assert 1.0 < gamma < 1.01, f"Gamma {gamma} not in expected range"
    print("✓ Lorentz gamma test passed")

def test_predict_small_k():
    """Test predictor for small k."""
    assert z5d_predict(1) == 2
    assert z5d_predict(2) == 3
    assert z5d_predict(3) == 5
    print("✓ Small k prediction test passed")

def test_predict_with_lorentz():
    """Test predictor with Lorentz correction."""
    p_base = z5d_predict(10000, eta=0)
    p_corr = z5d_predict(10000, eta=1.0, beta=30.34)
    assert p_corr != p_base, "Lorentz should change prediction"
    print("✓ Lorentz correction test passed")

def test_log_space_consistency():
    """Test log-space prediction consistency."""
    k = 1000
    L_log = z5d_predict_logL(k, eta=1.0)
    p_exp = math.exp(L_log)
    p_direct = z5d_predict(k, eta=1.0)
    assert abs(p_exp - p_direct) < 1, f"Inconsistency: {p_exp} vs {p_direct}"
    print("✓ Log-space consistency test passed")

if __name__ == "__main__":
    test_lorentz_gamma()
    test_predict_small_k()
    test_predict_with_lorentz()
    test_log_space_consistency()
    print("All tests passed!")