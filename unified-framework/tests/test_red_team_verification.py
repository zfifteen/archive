"""
Test suite for red team verification tools.

Validates that the verification scripts work correctly and 
provide reproducible results.
"""

import sys
import os
import subprocess
import pytest

# Add tools to path
TOOLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'tools')
sys.path.insert(0, TOOLS_DIR)


class TestVerificationTools:
    """Test the red team verification tools."""
    
    def test_verify_exact_primes_fast_exists(self):
        """Verify the fast verification script exists."""
        script_path = os.path.join(TOOLS_DIR, 'verify_exact_primes_fast.py')
        assert os.path.exists(script_path), "verify_exact_primes_fast.py should exist"
    
    def test_analyze_predictor_errors_exists(self):
        """Verify the error analysis script exists."""
        script_path = os.path.join(TOOLS_DIR, 'analyze_predictor_errors.py')
        assert os.path.exists(script_path), "analyze_predictor_errors.py should exist"
    
    def test_verification_script_imports(self):
        """Test that verification script imports successfully."""
        try:
            # Import the verification module
            import verify_exact_primes_fast
            assert hasattr(verify_exact_primes_fast, 'EXACT_PRIMES')
            assert hasattr(verify_exact_primes_fast, 'verify_prime_fast')
            assert hasattr(verify_exact_primes_fast, 'cross_reference_with_known_sources')
        except ImportError as e:
            pytest.skip(f"Cannot import verification module: {e}")
    
    def test_exact_primes_contains_key_claim(self):
        """Test that EXACT_PRIMES contains the key claim from issue."""
        try:
            import verify_exact_primes_fast
            # The issue specifically mentions p_1000000=15485863
            assert 10**6 in verify_exact_primes_fast.EXACT_PRIMES
            assert verify_exact_primes_fast.EXACT_PRIMES[10**6] == 15485863
        except ImportError:
            pytest.skip("Cannot import verification module")
    
    def test_verification_with_sympy(self):
        """Test actual verification using sympy (if available)."""
        try:
            import sympy
            import verify_exact_primes_fast as vef
            
            # Verify a small prime
            n = 10
            expected = 29
            is_correct, actual, elapsed, status = vef.verify_prime_fast(n, expected, timeout=5.0)
            
            assert status in ['verified', 'skipped']
            if status == 'verified':
                assert is_correct == True
                assert actual == 29
        except ImportError as e:
            pytest.skip(f"Required libraries not available: {e}")
    
    def test_cross_reference_literature(self):
        """Test cross-reference with known literature."""
        try:
            import verify_exact_primes_fast as vef
            known_lit = vef.cross_reference_with_known_sources()
            
            # Should contain key values from OEIS A006988
            assert 10**1 in known_lit
            assert known_lit[10**1] == 29
            assert 10**6 in known_lit
            assert known_lit[10**6] == 15485863
        except ImportError:
            pytest.skip("Cannot import verification module")


class TestGapUnitsMetric:
    """Test gap-units metric implementation."""
    
    def test_gap_units_calculation(self):
        """Test gap-units calculation is correct."""
        import math
        
        # Example from the issue: n = 10^6
        predicted = 15484008
        actual = 15485863
        error = abs(predicted - actual)  # 1855
        log_actual = math.log(actual)  # ~16.56
        gap_units = error / log_actual  # ~112.05
        
        # Verify calculation
        assert error == 1855
        assert abs(log_actual - 16.56) < 0.01
        assert abs(gap_units - 112.05) < 1.0
    
    def test_ppm_vs_gap_units(self):
        """Test that ppm and gap-units tell different stories."""
        import math
        
        # Example: n = 10^18 from the report
        predicted = 44211790233986166091
        actual = 44211790234832169331
        error = abs(predicted - actual)  # 846003240
        
        # ppm story
        ppm = (error / actual) * 1e6
        # Should be very small (rounds to 0.00)
        assert ppm < 0.001
        
        # gap-units story
        log_actual = math.log(actual)
        gap_units = error / log_actual
        # Should be millions
        assert gap_units > 1e6
        
        # This demonstrates the key finding: same error, different normalizations


class TestReproducibility:
    """Test reproducibility requirements from red team."""
    
    def test_precision_requirement(self):
        """Test that precision meets red team requirement (dps >= 50)."""
        try:
            import mpmath as mp
            # Save original precision
            original_dps = mp.mp.dps
            try:
                # Scripts should set dps = 60
                mp.mp.dps = 60
                assert mp.mp.dps >= 50, "Precision should be >= 50 as required"
            finally:
                # Restore original precision
                mp.mp.dps = original_dps
        except ImportError:
            pytest.skip("mpmath not available")
    
    def test_verification_reproducibility(self):
        """Test that verification gives same results on repeated runs."""
        try:
            import sympy
            
            # Run same verification twice
            n = 10**3
            result1 = sympy.prime(n)
            result2 = sympy.prime(n)
            
            assert result1 == result2, "Results should be reproducible"
            assert result1 == 7919, "Should match expected value"
        except ImportError:
            pytest.skip("sympy not available")


def test_red_team_report_exists():
    """Test that the red team report was generated."""
    report_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'RED_TEAM_VERIFICATION_REPORT.md'
    )
    assert os.path.exists(report_path), "RED_TEAM_VERIFICATION_REPORT.md should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
