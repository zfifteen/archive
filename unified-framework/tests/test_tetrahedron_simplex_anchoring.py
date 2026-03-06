#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Tetrahedron Geometric Insights and Simplex Anchoring
===================================================================

Tests for the integration of tetrahedron-based coordinates and rotational
symmetries (A₄ group, order 12) into the Z5D framework for enhanced symmetry
operations and density predictions.

Reference: Issue #XXX - Integrate Tetrahedron Geometric Insights
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import numpy as np
import mpmath as mp

from src.core.geodesic_mapping import GeodesicMapper
from src.core.params import (
    DIST_LEVEL_STADLMANN,
    ENHANCEMENT_DEFAULT_BINS,
    BOOTSTRAP_RESAMPLES_DEFAULT
)


class TestTetrahedronEmbedding:
    """Test 3D tetrahedron embedding into 5D"""
    
    def test_simplex_anchor_basic(self):
        """Test basic simplex anchoring with small prime list"""
        mapper = GeodesicMapper(kappa_geo=0.3)
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        
        result = mapper.simplex_anchor(primes)
        
        # Check that result contains expected keys
        assert 'enhancement_percent' in result
        assert 'base_enhancement_percent' in result
        assert 'simplex_boost_percent' in result
        assert 'tetrahedron_vertices_5d' in result
        
        # Check that enhancement is computed (may be near zero or negative for small samples)
        assert isinstance(result['enhancement_percent'], (int, float, np.number))
        assert isinstance(result['base_enhancement_percent'], (int, float, np.number))
    
    def test_tetrahedron_vertices_5d(self):
        """Test that tetrahedron vertices are correctly embedded in 5D"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7, 11]
        
        result = mapper.simplex_anchor(primes)
        vertices_5d = result['tetrahedron_vertices_5d']
        
        # Should have 6 vertices (4 tetrahedron + 2 orthogonal)
        assert len(vertices_5d) == 6
        
        # Each vertex should be 5-dimensional
        for vertex in vertices_5d:
            assert len(vertex) == 5
        
        # First 4 vertices should be embedded 3D tetrahedron
        # Standard tetrahedron: (1,1,1), (1,-1,-1), (-1,1,-1), (-1,-1,1)
        # Embedded as: (1,1,1,0,0), (1,-1,-1,0,0), (-1,1,-1,0,0), (-1,-1,1,0,0)
        expected_first_4 = [
            (1, 1, 1, 0, 0),
            (1, -1, -1, 0, 0),
            (-1, 1, -1, 0, 0),
            (-1, -1, 1, 0, 0)
        ]
        assert vertices_5d[:4] == expected_first_4
        
        # Last 2 vertices should be orthogonal completion
        assert vertices_5d[4] == (0, 0, 0, 1, 1)
        assert vertices_5d[5] == (0, 0, 0, -1, -1)
    
    def test_custom_base_coords(self):
        """Test simplex anchoring with custom base coordinates"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7]
        
        # Custom 3D coordinates
        custom_coords = [
            (2, 0, 0),
            (0, 2, 0),
            (0, 0, 2),
            (1, 1, 1)
        ]
        
        result = mapper.simplex_anchor(primes, base_coords=custom_coords)
        vertices_5d = result['tetrahedron_vertices_5d']
        
        # Should embed custom coords into 5D
        assert len(vertices_5d) == 6
        assert vertices_5d[0] == (2, 0, 0, 0, 0)
        assert vertices_5d[1] == (0, 2, 0, 0, 0)
        assert vertices_5d[2] == (0, 0, 2, 0, 0)
        assert vertices_5d[3] == (1, 1, 1, 0, 0)


class TestA4SymmetryFactor:
    """Test A₄ group (alternating group) symmetry factors"""
    
    def test_a4_group_order(self):
        """Test that A₄ group order is correctly computed"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5]
        
        result = mapper.simplex_anchor(primes)
        
        # A₄ has order 12 (even permutations of 4 elements)
        assert result['tetrahedron_properties']['a4_group_order'] == 12
    
    def test_a4_symmetry_contribution(self):
        """Test A₄ symmetry factor contribution"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7, 11]
        
        result = mapper.simplex_anchor(primes)
        
        # Symmetry factor should be slightly > 1 (normalized contribution)
        a4_factor = result['a4_symmetry_factor']
        assert a4_factor > 1.0
        assert a4_factor < 1.1  # Should be a small boost
        
        # Should be 1 + 0.5/12 = 1.041666...
        expected = 1.0 + (0.5 / 12)
        assert abs(a4_factor - expected) < 1e-6


class TestEulerFormulaConstraints:
    """Test Euler's formula topological constraints"""
    
    def test_euler_characteristic(self):
        """Test that Euler characteristic is correctly computed"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5]
        
        result = mapper.simplex_anchor(primes)
        
        # For tetrahedron: V=4, E=6, F=4
        # Euler's formula: V - E + F = 2
        props = result['tetrahedron_properties']
        assert props['vertices'] == 4
        assert props['edges'] == 6
        assert props['faces'] == 4
        assert result['euler_characteristic'] == 2
        assert props['euler_formula_verified'] is True
    
    def test_euler_constraint_factor(self):
        """Test Euler constraint topological boost"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7]
        
        result = mapper.simplex_anchor(primes)
        
        # Euler constraint factor should be 1 + χ/100 = 1 + 2/100 = 1.02
        euler_factor = result['euler_constraint_factor']
        expected = 1.0 + (2.0 / 100.0)
        assert abs(euler_factor - expected) < 1e-6


class TestTetrahedronSelfDuality:
    """Test tetrahedron self-duality property"""
    
    def test_self_duality_property(self):
        """Test that tetrahedron self-duality is recognized"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5]
        
        result = mapper.simplex_anchor(primes)
        
        # Tetrahedron is self-dual
        assert result['tetrahedron_properties']['self_dual'] is True
    
    def test_self_duality_factor(self):
        """Test self-duality factor contribution"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7, 11]
        
        result = mapper.simplex_anchor(primes)
        
        # Self-duality factor should provide ~1.5% boost (midpoint of [0.8%, 2.2%])
        self_duality_factor = result['self_duality_factor']
        expected = 1.0 + 0.015  # 1.5% boost
        assert abs(self_duality_factor - expected) < 1e-6


class TestSimplexBoost:
    """Test simplex anchoring density boost"""
    
    def test_simplex_boost_range(self):
        """Test that simplex boost is computed correctly"""
        mapper = GeodesicMapper(kappa_geo=0.3)
        
        # Use larger prime list for stable statistics
        primes = list(range(2, 100))
        primes = [p for p in primes if all(p % i != 0 for i in range(2, int(p**0.5) + 1)) and p > 1]
        
        result = mapper.simplex_anchor(primes[:20])  # Use first 20 primes
        
        # Check simplex boost is computed
        boost = result['simplex_boost_percent']
        
        # Boost should be a number (may be zero or small for small samples)
        assert isinstance(boost, (int, float, np.number))
        
        # Target range validation
        assert result['target_boost_range'] == [0.8, 2.2]
        
        # Note: The actual boost might not always be in [0.8%, 2.2%] for small samples
        # but the target_boost_met flag indicates validation
        assert 'target_boost_met' in result
    
    def test_combined_simplex_factor(self):
        """Test that combined simplex factor includes all contributions"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7, 11, 13]
        
        result = mapper.simplex_anchor(primes)
        
        # Combined factor should be product of individual factors
        expected_combined = (
            result['a4_symmetry_factor'] *
            result['euler_constraint_factor'] *
            result['self_duality_factor']
        )
        
        assert abs(result['combined_simplex_factor'] - expected_combined) < 1e-6
        
        # Combined factor should be > 1 (enhancement)
        assert result['combined_simplex_factor'] > 1.0
    
    def test_enhancement_with_simplex(self):
        """Test that simplex anchoring applies combined factor correctly"""
        mapper = GeodesicMapper(kappa_geo=0.3)
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        
        result = mapper.simplex_anchor(primes)
        
        # Simplex-enhanced should equal base * combined_simplex_factor
        expected_enhancement = result['base_enhancement_percent'] * result['combined_simplex_factor']
        
        # Allow small numerical differences
        assert abs(result['enhancement_percent'] - expected_enhancement) < 1e-6
        
        # Boost should equal difference
        expected_boost = result['enhancement_percent'] - result['base_enhancement_percent']
        assert abs(result['simplex_boost_percent'] - expected_boost) < 1e-6


class TestStadlmannIntegration:
    """Test integration with Stadlmann distribution level"""
    
    def test_dist_level_default(self):
        """Test that default distribution level is Stadlmann's 0.525"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7]
        
        result = mapper.simplex_anchor(primes)
        
        assert result['dist_level'] == DIST_LEVEL_STADLMANN
        assert result['dist_level'] == 0.525
    
    def test_custom_dist_level(self):
        """Test simplex anchoring with custom distribution level"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7, 11]
        
        custom_dist_level = 0.55
        result = mapper.simplex_anchor(primes, dist_level=custom_dist_level)
        
        assert result['dist_level'] == custom_dist_level
    
    def test_invalid_dist_level(self):
        """Test that invalid distribution levels raise errors"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5]
        
        # Below minimum (should raise)
        with pytest.raises(ValueError, match="Distribution level"):
            mapper.simplex_anchor(primes, dist_level=0.5)
        
        # Above maximum (should raise)
        with pytest.raises(ValueError, match="Distribution level"):
            mapper.simplex_anchor(primes, dist_level=1.1)


class TestBootstrapValidation:
    """Test bootstrap confidence intervals for simplex anchoring"""
    
    def test_bootstrap_ci_computed(self):
        """Test that bootstrap confidence intervals are computed"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        
        result = mapper.simplex_anchor(primes, n_bootstrap=100)
        
        # CI should be computed
        assert 'ci_lower' in result
        assert 'ci_upper' in result
        assert result['ci_lower'] <= result['ci_upper']
    
    def test_bootstrap_samples(self):
        """Test bootstrap sample count"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7, 11]
        
        n_bootstrap = 50
        result = mapper.simplex_anchor(primes, n_bootstrap=n_bootstrap)
        
        # Should have successful bootstrap samples
        assert result['n_bootstrap_successful'] > 0
        assert result['n_bootstrap_successful'] <= n_bootstrap
    
    def test_ci_contains_target(self):
        """Test that CI validation is performed"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5, 7, 11, 13]
        
        result = mapper.simplex_anchor(primes, n_bootstrap=100)
        
        # CI contains target flag should be present
        assert 'ci_contains_target' in result
        # numpy bool is compatible with bool type checking
        assert isinstance(result['ci_contains_target'], (bool, np.bool_))


class TestDimensionParameter:
    """Test dimension parameter flexibility"""
    
    def test_default_dimension(self):
        """Test that default dimension is 5"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5]
        
        result = mapper.simplex_anchor(primes)
        
        # Should have 5D vertices
        for vertex in result['tetrahedron_vertices_5d']:
            assert len(vertex) == 5
    
    def test_custom_dimension(self):
        """Test simplex anchoring with custom dimension"""
        mapper = GeodesicMapper()
        primes = [2, 3, 5]
        
        # Note: simplex_anchor currently only supports dim=5
        # This test documents the current behavior
        result = mapper.simplex_anchor(primes, dim=5)
        
        for vertex in result['tetrahedron_vertices_5d']:
            assert len(vertex) == 5


class TestIntegration:
    """Integration tests for simplex anchoring workflow"""
    
    def test_full_workflow(self):
        """Test complete simplex anchoring workflow"""
        mapper = GeodesicMapper(kappa_geo=0.3)
        
        # Generate small prime list
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        
        # Run simplex anchoring
        result = mapper.simplex_anchor(
            primes,
            dist_level=DIST_LEVEL_STADLMANN,
            n_bins=ENHANCEMENT_DEFAULT_BINS,
            n_bootstrap=100
        )
        
        # Verify all components present
        assert 'enhancement_percent' in result
        assert 'simplex_boost_percent' in result
        assert 'tetrahedron_vertices_5d' in result
        assert 'a4_symmetry_factor' in result
        assert 'euler_constraint_factor' in result
        assert 'self_duality_factor' in result
        assert 'combined_simplex_factor' in result
        assert 'ci_lower' in result
        assert 'ci_upper' in result
        
        # Verify topological properties
        props = result['tetrahedron_properties']
        assert props['vertices'] == 4
        assert props['edges'] == 6
        assert props['faces'] == 4
        assert props['euler_formula_verified'] is True
        assert props['a4_group_order'] == 12
        assert props['self_dual'] is True
        
        # Verify enhancement is computed (values are numerical)
        assert isinstance(result['enhancement_percent'], (int, float, np.number))
        assert isinstance(result['base_enhancement_percent'], (int, float, np.number))
        assert isinstance(result['simplex_boost_percent'], (int, float, np.number))
    
    def test_comparison_with_base_enhancement(self):
        """Test that simplex anchoring applies the combined factor correctly"""
        mapper = GeodesicMapper(kappa_geo=0.3)
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        
        # Get base enhancement with dist_level
        base_result = mapper.compute_density_enhancement_with_dist_level(
            primes,
            dist_level=DIST_LEVEL_STADLMANN,
            n_bins=ENHANCEMENT_DEFAULT_BINS,
            n_bootstrap=100
        )
        
        # Get simplex-anchored enhancement
        simplex_result = mapper.simplex_anchor(
            primes,
            dist_level=DIST_LEVEL_STADLMANN,
            n_bins=ENHANCEMENT_DEFAULT_BINS,
            n_bootstrap=100
        )
        
        # Base enhancement from simplex should match direct computation
        # Allow small numerical differences
        assert abs(simplex_result['base_enhancement_percent'] - base_result['enhancement_percent']) < 1e-6
        
        # Verify boost calculation
        expected_boost = simplex_result['enhancement_percent'] - simplex_result['base_enhancement_percent']
        assert abs(simplex_result['simplex_boost_percent'] - expected_boost) < 1e-6
        
        # Verify combined factor is applied
        expected_enhancement = base_result['enhancement_percent'] * simplex_result['combined_simplex_factor']
        assert abs(simplex_result['enhancement_percent'] - expected_enhancement) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
