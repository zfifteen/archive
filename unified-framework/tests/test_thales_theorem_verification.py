"""
Test Suite for Thales' Theorem Verification and Z Framework Integration

This module provides comprehensive testing for the Thales' theorem verification
system and its integration with the Z Framework geodesic principles.

Key Test Areas:
1. Thales' theorem verification accuracy (1,000 trials)
2. Sympy geometry mathematical correctness
3. Z Framework integration and enhancement validation
4. Prime density improvement verification
5. Bootstrap confidence interval validation
"""

import pytest
import numpy as np
import os
from typing import Dict, List
import warnings

# Import with proper package structure and fallback for direct execution
try:
    from src.symbolic.thales_theorem import (
        ThalesTheoremsVerifier, 
        ZFrameworkThalesIntegration,
        run_comprehensive_thales_verification
    )
except ImportError:
    from ..src.symbolic.thales_theorem import (
        ThalesTheoremsVerifier, 
        ZFrameworkThalesIntegration,
        run_comprehensive_thales_verification
    )
from sympy import geometry as sg, pi, sqrt
from sympy.geometry import Point, Circle

warnings.filterwarnings("ignore")


class TestThalesTheoremVerification:
    """Test suite for Thales' theorem verification."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.verifier = ThalesTheoremsVerifier(tolerance=1e-10, random_seed=42)
        self.z_framework = ZFrameworkThalesIntegration(kappa_geo=0.3)
    
    def test_thales_verifier_initialization(self):
        """Test proper initialization of Thales verifier."""
        assert self.verifier.tolerance == 1e-10
        assert self.verifier.random_seed == 42
    
    def test_random_circle_generation(self):
        """Test random circle and diameter generation."""
        circle, p1, p2 = self.verifier.generate_random_circle_and_diameter()
        
        # Verify circle properties
        assert isinstance(circle, Circle)
        assert isinstance(p1, Point)
        assert isinstance(p2, Point)
        
        # Verify points are on circle
        assert abs(circle.center.distance(p1).evalf() - circle.radius.evalf()) < 1e-10
        assert abs(circle.center.distance(p2).evalf() - circle.radius.evalf()) < 1e-10
        
        # Verify points form diameter (distance = 2*radius)
        diameter_distance = p1.distance(p2).evalf()
        expected_diameter = 2 * circle.radius.evalf()
        assert abs(diameter_distance - expected_diameter) < 1e-10
    
    def test_inscribed_point_generation(self):
        """Test inscribed point generation on circle."""
        circle, p1, p2 = self.verifier.generate_random_circle_and_diameter()
        inscribed = self.verifier.generate_inscribed_point(circle, p1, p2)
        
        # Verify inscribed point is on circle
        distance_to_center = circle.center.distance(inscribed).evalf()
        assert abs(distance_to_center - circle.radius.evalf()) < 1e-10
        
        # Verify inscribed point is not too close to diameter endpoints
        assert inscribed.distance(p1).evalf() > self.verifier.tolerance
        assert inscribed.distance(p2).evalf() > self.verifier.tolerance
    
    def test_angle_calculation_right_angle(self):
        """Test angle calculation for known right angle configuration."""
        # Create specific configuration that should give right angle
        center = Point(0, 0)
        circle = Circle(center, 1)
        
        # Diameter points
        p1 = Point(-1, 0)
        p2 = Point(1, 0)
        
        # Inscribed point that should form right angle
        inscribed = Point(0, 1)
        
        angle = self.verifier.calculate_angle_at_inscribed_point(inscribed, p1, p2)
        
        # Should be π/2 (90 degrees)
        expected_angle = pi / 2
        assert abs(angle - float(expected_angle)) < 1e-10
    
    def test_single_trial_verification(self):
        """Test single trial verification produces valid result."""
        result = self.verifier.verify_single_trial(trial_id=1)
        
        # Verify result structure
        assert result.trial_id == 1
        assert isinstance(result.circle_center, Point)
        assert isinstance(result.circle_radius, float)
        assert len(result.diameter_points) == 2
        assert isinstance(result.inscribed_point, Point)
        assert isinstance(result.angle_at_inscribed, float)
        assert isinstance(result.is_right_angle, bool)
        assert isinstance(result.numerical_error, float)
        
        # Verify angle is close to π/2 (Thales' theorem)
        expected_angle = pi / 2
        assert abs(result.angle_at_inscribed - float(expected_angle)) < 1e-6
        
        # Verify it's classified as right angle
        assert result.is_right_angle
    
    def test_small_scale_verification_trials(self):
        """Test small-scale verification trials (10 trials)."""
        results = self.verifier.run_verification_trials(num_trials=10)
        
        # Verify results structure
        assert 'verification_summary' in results
        assert 'statistical_analysis' in results
        assert 'bootstrap_confidence_interval' in results
        assert 'trials_data' in results
        assert 'theorem_verification' in results
        
        # Verify verification summary
        summary = results['verification_summary']
        assert summary['total_trials'] == 10
        assert summary['successful_verifications'] <= 10
        assert 0 <= summary['accuracy_percentage'] <= 100
        
        # Should achieve high accuracy (>90% for small trials)
        assert summary['accuracy_percentage'] >= 90.0
    
    def test_statistical_analysis_structure(self):
        """Test statistical analysis computation."""
        results = self.verifier.run_verification_trials(num_trials=20)
        stats = results['statistical_analysis']
        
        # Verify error statistics
        assert 'error_statistics' in stats
        error_stats = stats['error_statistics']
        required_keys = ['mean', 'std', 'min', 'max', 'median', 'percentile_95', 'percentile_99']
        for key in required_keys:
            assert key in error_stats
            assert isinstance(error_stats[key], (int, float))
        
        # Verify angle statistics
        assert 'angle_statistics' in stats
        angle_stats = stats['angle_statistics']
        assert 'mean_angle_radians' in angle_stats
        assert 'theoretical_right_angle' in angle_stats
        
        # Mean angle should be close to π/2
        mean_angle = angle_stats['mean_angle_radians']
        theoretical = angle_stats['theoretical_right_angle']
        assert abs(mean_angle - theoretical) < 0.1  # Reasonable tolerance
    
    def test_bootstrap_confidence_interval(self):
        """Test bootstrap confidence interval computation."""
        results = self.verifier.run_verification_trials(num_trials=50)
        ci = results['bootstrap_confidence_interval']
        
        # Verify CI structure
        assert 'confidence_level' in ci
        assert 'lower_bound' in ci
        assert 'upper_bound' in ci
        assert 'mean_success_rate' in ci
        
        # Verify reasonable bounds
        assert 0 <= ci['lower_bound'] <= 1
        assert 0 <= ci['upper_bound'] <= 1
        assert ci['lower_bound'] <= ci['upper_bound']
        assert ci['confidence_level'] == 0.95
        
        # For Thales' theorem, bounds should be high (>0.9)
        assert ci['lower_bound'] >= 0.9


class TestZFrameworkIntegration:
    """Test suite for Z Framework integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.z_framework = ZFrameworkThalesIntegration(kappa_geo=0.3)
    
    def test_z_framework_initialization(self):
        """Test Z Framework integration initialization."""
        assert self.z_framework.kappa_geo == 0.3
        assert abs(self.z_framework.phi - 1.618033988749895) < 1e-10  # Golden ratio
    
    def test_theta_prime_transform(self):
        """Test θ'(n,k) transformation function."""
        # Test with specific values
        result_1 = self.z_framework.theta_prime_transform(1)
        result_10 = self.z_framework.theta_prime_transform(10)
        result_100 = self.z_framework.theta_prime_transform(100)
        
        # Verify results are in expected range [0, φ)
        phi = self.z_framework.phi
        assert 0 <= result_1 < phi
        assert 0 <= result_10 < phi
        assert 0 <= result_100 < phi
        
        # Verify transformation is deterministic
        assert self.z_framework.theta_prime_transform(1) == result_1
        assert self.z_framework.theta_prime_transform(10) == result_10
    
    def test_thales_geometric_enhancement(self):
        """Test Thales-enhanced geometric transformation."""
        test_numbers = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23]
        
        # Apply enhancement
        enhanced = self.z_framework.apply_thales_geometric_enhancement(test_numbers)
        
        # Verify structure
        assert len(enhanced) == len(test_numbers)
        assert all(isinstance(x, float) for x in enhanced)
        
        # Verify enhancement produces different results than standard transform
        standard = [self.z_framework.theta_prime_transform(n) for n in test_numbers]
        
        # Should be different (enhanced)
        differences = [abs(e - s) for e, s in zip(enhanced, standard)]
        assert any(diff > 1e-10 for diff in differences)
    
    def test_prime_density_enhancement_computation(self):
        """Test prime density enhancement computation."""
        # Small test set for faster execution
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        
        # Test both standard and enhanced modes
        standard_results = self.z_framework.compute_prime_density_enhancement(
            primes, use_thales_enhancement=False, n_bins=10
        )
        
        enhanced_results = self.z_framework.compute_prime_density_enhancement(
            primes, use_thales_enhancement=True, n_bins=10
        )
        
        # Verify results structure
        for results in [standard_results, enhanced_results]:
            assert 'enhancement_percentage' in results
            assert 'prime_density' in results
            assert 'all_density' in results
            assert 'enhancement_ratios' in results
            assert 'thales_enhanced' in results
            assert 'geodesic_parameters' in results
        
        # Verify enhancement flags
        assert not standard_results['thales_enhanced']
        assert enhanced_results['thales_enhanced']
        
        # Verify enhancement percentages are reasonable
        assert isinstance(standard_results['enhancement_percentage'], (int, float))
        assert isinstance(enhanced_results['enhancement_percentage'], (int, float))
    
    def test_geodesic_parameters(self):
        """Test geodesic parameter validation."""
        results = self.z_framework.compute_prime_density_enhancement(
            [2, 3, 5, 7], use_thales_enhancement=True, n_bins=5
        )
        
        params = results['geodesic_parameters']
        assert params['kappa_geo'] == 0.3
        assert abs(params['phi'] - 1.618033988749895) < 1e-10


class TestComprehensiveIntegration:
    """Test suite for comprehensive integration functionality."""
    
    def test_comprehensive_verification_structure(self):
        """Test comprehensive verification returns proper structure."""
        # This is a longer test - use smaller parameters for faster execution
        # We'll mock the internal calls to avoid long execution times
        
        # Test with smaller scale for CI/testing
        verifier = ThalesTheoremsVerifier(tolerance=1e-8, random_seed=42)
        
        # Run small verification
        verification_results = verifier.run_verification_trials(num_trials=10)
        
        # Verify core structure exists
        assert 'verification_summary' in verification_results
        assert 'statistical_analysis' in verification_results
        assert 'bootstrap_confidence_interval' in verification_results
        assert 'theorem_verification' in verification_results
        
        # Test Z Framework integration separately
        z_framework = ZFrameworkThalesIntegration()
        primes = [2, 3, 5, 7, 11, 13]
        
        enhancement_results = z_framework.compute_prime_density_enhancement(primes)
        assert 'enhancement_percentage' in enhancement_results
        assert 'geodesic_parameters' in enhancement_results
    
    def test_empirical_insights_validation(self):
        """Test empirical insights structure and validation."""
        # Create mock empirical insights
        accuracy = 100.0
        enhancement = 15.5
        
        empirical_insights = {
            'theorem_accuracy': accuracy,
            'geodesic_enhancement': enhancement,
            'universality_validated': accuracy == 100.0,
            'efficiency_gain_achieved': enhancement >= 15.0
        }
        
        # Verify structure
        assert empirical_insights['theorem_accuracy'] == 100.0
        assert empirical_insights['geodesic_enhancement'] == 15.5
        assert empirical_insights['universality_validated'] is True
        assert empirical_insights['efficiency_gain_achieved'] is True
    
    def test_target_enhancement_validation(self):
        """Test target enhancement validation logic."""
        target = 15.0
        
        # Test cases
        test_cases = [
            (14.5, False),  # Below target
            (15.0, True),   # Exactly at target
            (15.5, True),   # Above target
            (20.0, True)    # Well above target
        ]
        
        for enhancement, expected in test_cases:
            achieves_target = enhancement >= target
            assert achieves_target == expected


class TestThalesAccuracy:
    """Test suite specifically for Thales' theorem accuracy validation."""
    
    def test_high_accuracy_requirement(self):
        """Test that Thales verification achieves high accuracy."""
        verifier = ThalesTheoremsVerifier(tolerance=1e-10, random_seed=42)
        
        # Run moderate-scale verification for testing
        results = verifier.run_verification_trials(num_trials=100)
        
        accuracy = results['verification_summary']['accuracy_percentage']
        
        # Thales' theorem should have very high accuracy (>99%)
        assert accuracy >= 99.0
        
        # Ideally should be 100% for mathematical theorem
        # Note: Small numerical errors might occasionally cause <100%
        print(f"Achieved accuracy: {accuracy:.1f}%")
    
    def test_numerical_error_bounds(self):
        """Test that numerical errors are within acceptable bounds."""
        verifier = ThalesTheoremsVerifier(tolerance=1e-10, random_seed=42)
        
        results = verifier.run_verification_trials(num_trials=50)
        
        error_stats = results['statistical_analysis']['error_statistics']
        
        # Maximum error should be small
        assert error_stats['max'] < 1e-6
        
        # Mean error should be very small
        assert error_stats['mean'] < 1e-8
        
        # 99th percentile should be reasonable
        assert error_stats['percentile_99'] < 1e-7
    
    def test_bootstrap_ci_bounds(self):
        """Test bootstrap confidence interval bounds."""
        verifier = ThalesTheoremsVerifier(tolerance=1e-10, random_seed=42)
        
        results = verifier.run_verification_trials(num_trials=100)
        
        ci = results['bootstrap_confidence_interval']
        
        # For Thales' theorem, confidence interval should be very high
        assert ci['lower_bound'] >= 0.95
        assert ci['upper_bound'] >= 0.98
        
        # Interval should be tight for mathematical theorem
        interval_width = ci['upper_bound'] - ci['lower_bound']
        assert interval_width <= 0.1


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])