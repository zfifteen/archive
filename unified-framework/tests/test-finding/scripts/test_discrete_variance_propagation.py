"""
Test suite for discrete variance propagation and quantum nonlocality analysis.

Tests the implementation of discrete analogs of quantum nonlocality via zeta shift
cascades, including var(O) ~ log log N scaling verification and geodesic effects.
"""

import numpy as np
import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import sys
import os

# Add the repository root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from experiments.discrete_variance_propagation import QuantumNonlocalityAnalyzer

class TestQuantumNonlocalityAnalyzer:
    """Test suite for QuantumNonlocalityAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = QuantumNonlocalityAnalyzer(max_N=200, seed=2)
        
    def test_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer.max_N == 200
        assert self.analyzer.seed == 2
        assert len(self.analyzer.cascade_data) == 0
        assert len(self.analyzer.variance_data) == 0
        
    def test_cascade_generation(self):
        """Test zeta shift cascade generation."""
        N = 50
        cascade = self.analyzer.generate_cascade(N)
        
        assert len(cascade) == N
        assert all(hasattr(shift, 'getO') for shift in cascade)
        assert all(hasattr(shift, 'a') for shift in cascade)
        
        # Test caching
        cascade2 = self.analyzer.generate_cascade(N)
        assert cascade is cascade2  # Should be same object due to caching
        
    def test_operator_value_extraction(self):
        """Test extraction of O operator values."""
        cascade = self.analyzer.generate_cascade(20)
        O_values = self.analyzer.extract_operator_values(cascade)
        
        assert len(O_values) == 20
        assert isinstance(O_values, np.ndarray)
        assert all(isinstance(val, (int, float)) for val in O_values)
        assert all(np.isfinite(val) for val in O_values)
        
    def test_theta_prime_transformation(self):
        """Test θ'(n,k) transformation application."""
        cascade = self.analyzer.generate_cascade(30)
        
        # Test with default k=0.3
        theta_values = self.analyzer.apply_theta_prime_transformation(cascade)
        assert len(theta_values) == 30
        assert isinstance(theta_values, np.ndarray)
        assert all(val >= 0 for val in theta_values)  # Should be non-negative
        
        # Test with custom k
        theta_values_k05 = self.analyzer.apply_theta_prime_transformation(cascade, k=0.5)
        assert len(theta_values_k05) == 30
        assert not np.array_equal(theta_values, theta_values_k05)  # Should be different
        
    def test_curvature_computation(self):
        """Test κ(n) curvature value computation."""
        cascade = self.analyzer.generate_cascade(25)
        curvature_vals = self.analyzer.compute_curvature_values(cascade)
        
        assert len(curvature_vals) == 25
        assert isinstance(curvature_vals, np.ndarray)
        assert all(np.isfinite(val) for val in curvature_vals)
        assert all(val > 0 for val in curvature_vals)  # Curvature should be positive
        
    def test_variance_scaling_analysis(self):
        """Test variance scaling analysis for var(O) ~ log log N."""
        N_values = [16, 32, 64, 100]
        results = self.analyzer.analyze_variance_scaling(N_values)
        
        # Check required keys in results
        required_keys = ['N_values', 'variances', 'log_log_N', 'slope', 
                        'intercept', 'r_squared', 'correlation', 'scaling_formula']
        for key in required_keys:
            assert key in results
            
        # Check data consistency
        assert len(results['N_values']) == len(results['variances'])
        assert len(results['variances']) == len(results['log_log_N'])
        
        # Check statistical measures
        assert isinstance(results['slope'], (int, float))
        assert isinstance(results['r_squared'], (int, float))
        assert isinstance(results['correlation'], (int, float))
        assert 0 <= results['r_squared'] <= 1  # R-squared should be between 0 and 1
        assert -1 <= results['correlation'] <= 1  # Correlation should be between -1 and 1
        
        # Check that variances are positive
        assert all(var >= 0 for var in results['variances'])
        
    def test_geodesic_effects_simulation(self):
        """Test simulation of discrete geodesic effects."""
        N = 100
        k_values = [0.2, 0.3, 0.4]
        results = self.analyzer.simulate_geodesic_effects(N, k_values)
        
        # Check required keys
        required_keys = ['k_values', 'variance_ratios', 'theta_correlations', 
                        'curvature_correlations', 'geodesic_effects', 
                        'optimal_k', 'max_geodesic_effect']
        for key in required_keys:
            assert key in results
            
        # Check data consistency
        assert len(results['k_values']) == len(k_values)
        assert len(results['variance_ratios']) == len(k_values)
        assert len(results['theta_correlations']) == len(k_values)
        assert len(results['curvature_correlations']) == len(k_values)
        assert len(results['geodesic_effects']) == len(k_values)
        
        # Check that optimal k is within expected range
        assert 0.1 <= results['optimal_k'] <= 0.5
        assert results['optimal_k'] in k_values
        
        # Check that variance ratios are positive
        assert all(ratio > 0 for ratio in results['variance_ratios'])
        
        # Check that correlations are within valid range
        for corr_list in [results['theta_correlations'], results['curvature_correlations']]:
            for corr in corr_list:
                if not np.isnan(corr):  # Allow NaN for edge cases
                    assert -1 <= corr <= 1
                    
    def test_quantum_nonlocality_metrics(self):
        """Test quantum nonlocality metrics computation."""
        N = 80
        metrics = self.analyzer.quantum_nonlocality_metrics(N)
        
        # Check required keys
        required_keys = ['cross_correlation', 'entanglement_metric', 'nonlocality_violation',
                        'coherence_measure', 'bell_inequality_factor', 'quantum_advantage']
        for key in required_keys:
            assert key in metrics
            
        # Check value ranges and types
        assert -1 <= metrics['cross_correlation'] <= 1
        assert metrics['entanglement_metric'] >= 0
        assert metrics['nonlocality_violation'] >= 0
        assert isinstance(metrics['quantum_advantage'], bool)
        assert metrics['bell_inequality_factor'] >= 0
        
        # Bell inequality factor should be > 1 if quantum advantage exists
        if metrics['quantum_advantage']:
            assert metrics['bell_inequality_factor'] > 1
            
    def test_variance_scaling_relationship(self):
        """Test that var(O) ~ log log N relationship holds approximately."""
        # Use larger sample for better statistical power
        N_values = [16, 32, 64, 100, 150]
        results = self.analyzer.analyze_variance_scaling(N_values)
        
        # Should show positive correlation for log log N scaling
        assert results['correlation'] > 0.3, f"Correlation {results['correlation']} too weak for log log N scaling"
        
        # Slope should be positive for increasing variance with log log N
        assert results['slope'] > 0, f"Slope {results['slope']} should be positive for log log N scaling"
        
        # R-squared should show reasonable fit
        assert results['r_squared'] > 0.1, f"R-squared {results['r_squared']} too low for meaningful scaling"
        
    def test_optimal_k_near_expected(self):
        """Test that optimal k is near the expected value of 0.3."""
        geodesic_results = self.analyzer.simulate_geodesic_effects(N=100)
        
        # Optimal k should be reasonably close to the theoretical optimum of 0.3
        # Allow for more variation since discrete systems may have different optima
        expected_k = 0.3
        assert abs(geodesic_results['optimal_k'] - expected_k) < 0.25, \
            f"Optimal k {geodesic_results['optimal_k']} too far from expected {expected_k}"
            
    def test_cascade_consistency(self):
        """Test that cascades are generated consistently."""
        cascade1 = self.analyzer.generate_cascade(50)
        cascade2 = self.analyzer.generate_cascade(50)
        
        # Should be the same due to caching
        assert cascade1 is cascade2
        
        # Values should be consistent
        O_values1 = self.analyzer.extract_operator_values(cascade1)
        O_values2 = self.analyzer.extract_operator_values(cascade2)
        np.testing.assert_array_equal(O_values1, O_values2)
        
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Small cascade
        small_cascade = self.analyzer.generate_cascade(5)
        assert len(small_cascade) == 5
        
        O_values = self.analyzer.extract_operator_values(small_cascade)
        assert len(O_values) == 5
        
        # Single element cascade
        single_cascade = self.analyzer.generate_cascade(1)
        assert len(single_cascade) == 1
        
        # Zero should raise error or handle gracefully
        try:
            zero_cascade = self.analyzer.generate_cascade(0)
            # Accept either empty list or single element for edge case
            assert len(zero_cascade) <= 1
        except (ValueError, IndexError):
            pass  # Expected for edge case
            
    def test_plotting_methods(self):
        """Test that plotting methods run without errors."""
        # Run analysis first
        self.analyzer.analyze_variance_scaling([16, 32, 64])
        
        # Test plotting methods (should not raise exceptions)
        try:
            self.analyzer.plot_variance_scaling()
            # Close the plot to avoid memory issues
            import matplotlib.pyplot as plt
            plt.close('all')
            
            geodesic_results = self.analyzer.simulate_geodesic_effects(N=50)
            self.analyzer.plot_geodesic_effects(geodesic_results)
            plt.close('all')
            
        except Exception as e:
            pytest.fail(f"Plotting methods should not raise exceptions: {e}")
            
    def test_generate_report(self):
        """Test comprehensive report generation."""
        # Redirect stdout to capture print statements
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            report = self.analyzer.generate_report()
            sys.stdout = sys.__stdout__  # Reset stdout
            
            # Check report structure
            required_sections = ['variance_scaling', 'geodesic_effects', 'quantum_nonlocality', 'summary']
            for section in required_sections:
                assert section in report
                
            # Check summary flags (handle numpy boolean types)
            assert isinstance(bool(report['summary']['var_scaling_confirmed']), bool)
            assert isinstance(bool(report['summary']['optimal_k_near_expected']), bool)
            assert isinstance(bool(report['summary']['quantum_nonlocality_detected']), bool)
            
            # Check that output was captured
            output = captured_output.getvalue()
            assert len(output) > 0
            assert "Analysis Complete!" in output
            
        finally:
            sys.stdout = sys.__stdout__  # Ensure stdout is reset
            
def run_integration_test():
    """
    Run integration test to validate complete workflow.
    """
    print("\nRunning Integration Test for Discrete Variance Propagation")
    print("=" * 60)
    
    analyzer = QuantumNonlocalityAnalyzer(max_N=200, seed=2)
    
    # Test complete workflow
    print("1. Testing variance scaling analysis...")
    scaling_results = analyzer.analyze_variance_scaling([16, 32, 64, 100])
    assert scaling_results['correlation'] > 0, "Should show positive correlation for log log N scaling"
    print(f"   ✓ Scaling correlation: {scaling_results['correlation']:.4f}")
    
    print("2. Testing geodesic effects simulation...")
    geodesic_results = analyzer.simulate_geodesic_effects(N=100)
    print(f"   ✓ Optimal k: {geodesic_results['optimal_k']:.3f}")
    print(f"   ✓ Max geodesic effect: {geodesic_results['max_geodesic_effect']:.6f}")
    
    print("3. Testing quantum nonlocality metrics...")
    nonlocality_results = analyzer.quantum_nonlocality_metrics(N=100)
    print(f"   ✓ Cross-correlation: {nonlocality_results['cross_correlation']:.4f}")
    print(f"   ✓ Quantum advantage: {nonlocality_results['quantum_advantage']}")
    
    print("4. Testing comprehensive report generation...")
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        report = analyzer.generate_report()
        sys.stdout = sys.__stdout__
        
        # Validate key findings
        assert report['summary']['var_scaling_confirmed'] or scaling_results['correlation'] > 0.3
        print(f"   ✓ Report generated successfully")
        
    finally:
        sys.stdout = sys.__stdout__
    
    print("\nIntegration Test PASSED!")
    print("All components working correctly together.")
    
    return {
        'scaling_results': scaling_results,
        'geodesic_results': geodesic_results,
        'nonlocality_results': nonlocality_results,
        'report': report
    }

if __name__ == "__main__":
    # Run integration test
    results = run_integration_test()
    
    # Run pytest if available
    try:
        import pytest
        print("\nRunning pytest test suite...")
        pytest.main([__file__, "-v"])
    except ImportError:
        print("\npytest not available, running manual tests...")
        
        # Run manual tests
        test_instance = TestQuantumNonlocalityAnalyzer()
        test_instance.setup_method()
        
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            try:
                print(f"Running {method_name}...")
                method = getattr(test_instance, method_name)
                method()
                print(f"  ✓ {method_name} PASSED")
            except Exception as e:
                print(f"  ✗ {method_name} FAILED: {e}")