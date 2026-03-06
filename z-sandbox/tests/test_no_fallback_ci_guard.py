#!/usr/bin/env python3
"""
CI Guard: Ensure no fallback curvature warnings in production paths.

This test fails if the fallback curvature warning is triggered,
indicating that z5d_axioms is not properly imported. This serves
as a continuous integration safeguard against precision degradation.

Related to Issue #221 and @zfifteen's action item.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import logging
from io import StringIO


def test_no_fallback_warning_in_production():
    """
    CI Guard: Fail if fallback curvature warning is emitted.
    
    This test ensures that z5d_axioms imports correctly and high-precision
    curvature is used. Any fallback to float64 precision causes test failure.
    """
    # Capture logging output
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.WARNING)
    
    # Get the root logger and add our handler
    logger = logging.getLogger()
    old_level = logger.level
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)
    
    try:
        # Import and test compute_curvature
        try:
            from python.greens_function_factorization import (
                compute_curvature,
                Z5D_AVAILABLE
            )
        except ImportError:
            from greens_function_factorization import (
                compute_curvature,
                Z5D_AVAILABLE
            )
        
        # First check: Z5D should be available
        assert Z5D_AVAILABLE, (
            "❌ CI GUARD FAILED: z5d_axioms not available. "
            "This will cause 3.92% precision degradation. "
            "Fix import paths before merging."
        )
        
        # Second check: Call compute_curvature and ensure no warning
        test_value = 10**100
        kappa = compute_curvature(test_value)
        
        # Check captured logs for fallback warning
        log_output = log_capture.getvalue()
        
        if "PRECISION DEGRADATION" in log_output or "fallback curvature" in log_output:
            pytest.fail(
                "❌ CI GUARD FAILED: Fallback curvature warning detected!\n"
                f"Log output:\n{log_output}\n"
                "This indicates z5d_axioms failed to import properly, "
                "causing float64 fallback and 3.92% error floor."
            )
        
        # Third check: Verify reasonable curvature value
        assert kappa > 0, "Curvature should be positive"
        assert isinstance(kappa, float), "Curvature should be float"
        
        # Success - no fallback warning detected
        print("✅ CI GUARD PASSED: High-precision z5d_axioms active, no fallback warnings")
        
    finally:
        # Clean up logging
        logger.removeHandler(handler)
        logger.setLevel(old_level)


def test_z5d_import_mandatory():
    """
    CI Guard: Z5D_AVAILABLE must be True in production.
    
    This is a hard requirement for maintaining breakthrough precision.
    """
    try:
        from python.greens_function_factorization import Z5D_AVAILABLE
    except ImportError:
        from greens_function_factorization import Z5D_AVAILABLE
    
    assert Z5D_AVAILABLE is True, (
        "❌ CI GUARD FAILED: Z5D_AVAILABLE is False.\n"
        "Production code MUST have z5d_axioms available for high-precision work.\n"
        "Import path issues detected - fix before merging."
    )


if __name__ == "__main__":
    # Run as standalone
    pytest.main([__file__, "-v"])
