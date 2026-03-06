#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Stadlmann Distribution Level Integration
========================================================

Tests for the integration of Stadlmann's 2023 advancement on the level
of distribution of primes in smooth arithmetic progressions (θ ≈ 0.525)
into the Z Framework.

Reference: Issue #625
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import numpy as np
import mpmath as mp

from src.core.params import (
    DIST_LEVEL_STADLMANN,
    DIST_LEVEL_MIN,
    DIST_LEVEL_MAX,
    validate_dist_level
)
from src.core.conical_flow import (
    conical_evaporation_time,
    conical_height_at_time,
    conical_surface_area,
    conical_flux,
    conical_density_enhancement_factor,
    validate_conical_model
)
from src.core.z_5d_enhanced import (
    z5d_predictor,
    z5d_predictor_with_dist_level
)
from src.core.geodesic_mapping import GeodesicMapper


class TestDistLevelParameters:
    """Test distribution level parameters and validation"""
    
    def test_dist_level_stadlmann_value(self):
        """Test that Stadlmann level is correctly defined"""
        assert DIST_LEVEL_STADLMANN == 0.525
        assert DIST_LEVEL_MIN < DIST_LEVEL_STADLMANN <= DIST_LEVEL_MAX
    
    def test_dist_level_bounds(self):
        """Test distribution level bounds"""
        assert DIST_LEVEL_MIN == 0.5
        assert DIST_LEVEL_MAX == 1.0
        assert DIST_LEVEL_MIN < DIST_LEVEL_MAX
    
    def test_validate_dist_level_valid(self):
        """Test validation with valid distribution levels"""
        # Stadlmann level should validate
        assert validate_dist_level(DIST_LEVEL_STADLMANN) == DIST_LEVEL_STADLMANN
        
        # Values in valid range should validate
        assert validate_dist_level(0.51) == 0.51
        assert validate_dist_level(0.6) == 0.6
        assert validate_dist_level(0.9) == 0.9
    
    def test_validate_dist_level_invalid(self):
        """Test validation with invalid distribution levels"""
        # Below minimum (should raise)
        with pytest.raises(ValueError, match="Distribution level"):
            validate_dist_level(0.5)
        
        with pytest.raises(ValueError, match="Distribution level"):
            validate_dist_level(0.4)
        
        # Above maximum (should raise)
        with pytest.raises(ValueError, match="Distribution level"):
            validate_dist_level(1.1)
    
    def test_validate_dist_level_context(self):
        """Test validation with different contexts"""
        level = validate_dist_level(0.525, context="test_context")
        assert level == 0.525


class TestConicalFlowModel:
    """Test conical flow model from Issue #631"""
    
    def test_conical_evaporation_time_basic(self):
        """Test basic evaporation time calculation"""
        h0 = 100.0
        k = 0.01
        T = conical_evaporation_time(h0, k)
        assert T == 10000.0
        
        # Test different values
        assert conical_evaporation_time(50.0, 0.1) == 500.0
        assert conical_evaporation_time(1.0, 1.0) == 1.0
    
    def test_conical_evaporation_time_invalid(self):
        """Test evaporation time with invalid inputs"""
        # Negative k
        with pytest.raises(ValueError, match="must be positive"):
            conical_evaporation_time(100.0, -0.01)
        
        # Zero k
        with pytest.raises(ValueError, match="must be positive"):
            conical_evaporation_time(100.0, 0.0)
        
        # Negative h0
        with pytest.raises(ValueError, match="must be non-negative"):
            conical_evaporation_time(-10.0, 0.01)
    
    def test_conical_height_at_time(self):
        """Test height evolution over time"""
        h0 = 100.0
        k = 0.01
        
        # Initial height
        assert conical_height_at_time(h0, k, 0) == h0
        
        # Half time
        T = conical_evaporation_time(h0, k)
        assert abs(conical_height_at_time(h0, k, T/2) - h0/2) < 1e-10
        
        # Full evaporation
        assert conical_height_at_time(h0, k, T) == 0.0
        
        # Beyond full evaporation (should clamp to 0)
        assert conical_height_at_time(h0, k, T + 1000) == 0.0
    
    def test_conical_surface_area(self):
        """Test surface area calculation"""
        h = 10.0
        angle = 0.3
        
        area = conical_surface_area(h, angle)
        expected = np.pi * (h * np.tan(angle)) ** 2
        assert abs(area - expected) < 1e-10
        
        # Zero height
        assert conical_surface_area(0.0, angle) == 0.0
    
    def test_conical_flux(self):
        """Test flux calculation"""
        h = 10.0
        k = 0.01
        angle = 0.3
        
        flux = conical_flux(h, k, angle)
        area = conical_surface_area(h, angle)
        assert abs(flux - k * area) < 1e-10
    
    def test_conical_density_enhancement_factor(self):
        """Test density enhancement factor calculation"""
        # Test with various n values
        for n in [1000, 10000, 100000, 1000000]:
            enhancement = conical_density_enhancement_factor(n)
            
            # Should be a positive number close to 1
            assert enhancement > 0.0
            assert 0.9 < enhancement < 1.2  # Reasonable range
        
        # Test with custom dist_level
        enhancement_custom = conical_density_enhancement_factor(
            100000, 
            dist_level=0.53
        )
        assert enhancement_custom > 0.0
    
    def test_conical_density_enhancement_vectorized(self):
        """Test vectorized density enhancement"""
        n_array = np.array([1000, 10000, 100000])
        enhancements = conical_density_enhancement_factor(n_array)
        
        assert len(enhancements) == len(n_array)
        assert all(e > 0.0 for e in enhancements)
    
    def test_validate_conical_model(self):
        """Test conical model validation"""
        results = validate_conical_model(n_samples=100, tolerance=1e-6)
        
        # Check structure
        assert 'mean_error' in results
        assert 'pass_rate' in results
        assert 'n_samples' in results
        
        # Analytical solution should have perfect accuracy
        assert results['pass_rate'] >= 0.95
        assert results['mean_error'] < 1e-5


class TestZ5DWithDistLevel:
    """Test Z_5D predictor with distribution level"""
    
    def test_z5d_predictor_with_dist_level_basic(self):
        """Test basic Z_5D prediction with Stadlmann level"""
        k = 100000
        
        # Should return a positive prediction
        pred = z5d_predictor_with_dist_level(k)
        assert float(pred) > 0
        
        # Should be reasonable (within order of magnitude of k*ln(k))
        approx = k * np.log(k)
        assert 0.5 * approx < float(pred) < 2.0 * approx
    
    def test_z5d_predictor_comparison(self):
        """Compare standard and Stadlmann-enhanced predictions"""
        k = 100000
        
        pred_standard = z5d_predictor(k)
        pred_stadlmann = z5d_predictor_with_dist_level(k)
        
        # Both should be positive
        assert float(pred_standard) > 0
        assert float(pred_stadlmann) > 0
        
        # Should be close but not identical
        rel_diff = abs(float(pred_stadlmann) - float(pred_standard)) / float(pred_standard)
        assert rel_diff < 0.1  # Within 10% difference
    
    def test_z5d_predictor_with_custom_dist_level(self):
        """Test with custom distribution level"""
        k = 50000
        
        pred_default = z5d_predictor_with_dist_level(k)
        pred_custom = z5d_predictor_with_dist_level(k, dist_level=0.53)
        
        # Both should be positive
        assert float(pred_default) > 0
        assert float(pred_custom) > 0
        
        # Should be different
        assert float(pred_default) != float(pred_custom)
    
    def test_z5d_predictor_with_ap_mod(self):
        """Test AP-specific predictions"""
        k = 50000
        
        pred_standard = z5d_predictor_with_dist_level(k)
        pred_ap = z5d_predictor_with_dist_level(k, ap_mod=6, ap_res=1)
        
        # Both should be positive
        assert float(pred_standard) > 0
        assert float(pred_ap) > 0
        
        # AP prediction should account for density factor
        # Should be different from standard
        assert float(pred_standard) != float(pred_ap)
    
    def test_z5d_predictor_scale_range(self):
        """Test predictor across scale range"""
        test_k_values = [1000, 10000, 100000, 1000000]
        
        for k in test_k_values:
            pred = z5d_predictor_with_dist_level(k)
            
            # Should be positive and increasing with k
            assert float(pred) > 0
            
            # Should be within reasonable bounds
            approx = k * np.log(k)
            assert 0.5 * approx < float(pred) < 2.0 * approx


class TestGeodesicWithDistLevel:
    """Test geodesic mapping with distribution level"""
    
    def test_geodesic_mapper_init(self):
        """Test geodesic mapper initialization"""
        mapper = GeodesicMapper(kappa_geo=0.3)
        assert mapper is not None
    
    def test_compute_density_enhancement_with_dist_level(self):
        """Test density enhancement with dist_level parameter"""
        # Skip if SymPy not available
        try:
            from sympy import primerange
        except ImportError:
            pytest.skip("SymPy not available")
        
        # Generate small prime sample
        primes = list(primerange(2, 10000))[:1000]
        
        mapper = GeodesicMapper(kappa_geo=0.3)
        
        # Standard enhancement
        results_standard = mapper.compute_density_enhancement(
            primes,
            n_bootstrap=10  # Small for speed
        )
        
        # Enhancement with dist_level
        results_stadlmann = mapper.compute_density_enhancement_with_dist_level(
            primes,
            dist_level=DIST_LEVEL_STADLMANN,
            n_bootstrap=10  # Small for speed
        )
        
        # Check structure
        assert 'enhancement_percent' in results_stadlmann
        assert 'dist_level' in results_stadlmann
        assert 'stadlmann_boost_percent' in results_stadlmann
        
        # Check values
        assert results_stadlmann['dist_level'] == DIST_LEVEL_STADLMANN
        assert isinstance(results_stadlmann['enhancement_percent'], (int, float))


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_workflow_basic(self):
        """Test complete workflow with basic parameters"""
        k = 10000
        
        # Standard Z_5D
        pred1 = z5d_predictor(k)
        assert float(pred1) > 0
        
        # Z_5D with Stadlmann
        pred2 = z5d_predictor_with_dist_level(k)
        assert float(pred2) > 0
        
        # Conical enhancement
        enhancement = conical_density_enhancement_factor(k)
        assert enhancement > 0
    
    def test_parameter_consistency(self):
        """Test parameter consistency across modules"""
        from src.core.params import DIST_LEVEL_STADLMANN as param_level
        
        # Ensure consistent value used
        k = 50000
        pred = z5d_predictor_with_dist_level(k, dist_level=param_level)
        
        assert float(pred) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
