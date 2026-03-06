#!/usr/bin/env python3
"""
Test module for Axis-wise Stabilization of Infinite Mod-3 Residue Series

Tests the scientific test suite for measuring stabilization rates of mod-3 residue axes
using Z-Framework observables with statistical rigor.

Author: Z Framework / Axis-wise Stabilization Testing
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import shutil
from pathlib import Path
import os
import sys

from applications.axis_wise_mod3_stabilization import AxiswiseMod3Stabilization
class TestAxiswiseMod3Stabilization:
    """Test suite for axis-wise mod-3 stabilization analysis."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return AxiswiseMod3Stabilization(max_n=1000, batch_size=100)
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        results_dir = Path(temp_dir) / "results"
        figs_dir = Path(temp_dir) / "figs"
        results_dir.mkdir()
        figs_dir.mkdir()
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        yield temp_dir, results_dir, figs_dir
        
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, analyzer):
        """Test proper initialization of the analyzer."""
        assert analyzer.max_n == 1000
        assert analyzer.batch_size == 100
        assert analyzer.resolution_ladder == [1000, 10000, 100000, 1000000]
        assert analyzer.k_primary == 0.3
        assert analyzer.n_bootstrap == 1000
        assert analyzer.confidence_level == 0.95
        assert len(analyzer.axis_data) == 3
    
    def test_partition_mod3_sequences(self, analyzer):
        """Test mod-3 sequence partitioning."""
        sequences = analyzer.partition_mod3_sequences(9)
        
        # Check correct partitioning
        assert sequences[0] == [3, 6, 9]  # S₀: multiples of 3
        assert sequences[1] == [1, 4, 7]  # S₁: remainder 1 mod 3
        assert sequences[2] == [2, 5, 8]  # S₂: remainder 2 mod 3
        
        # Test larger range
        sequences_large = analyzer.partition_mod3_sequences(30)
        
        # Verify all numbers are accounted for
        total_numbers = sum(len(seq) for seq in sequences_large.values())
        assert total_numbers == 30
        
        # Verify correct mod-3 assignment
        for axis_id, sequence in sequences_large.items():
            for n in sequence:
                assert n % 3 == axis_id
    
    def test_compute_prime_density(self, analyzer):
        """Test prime density computation."""
        # Test with known sequence containing primes 2, 3, 5
        sequence = [2, 3, 5, 4, 6]
        density = analyzer.compute_prime_density(sequence)
        assert density == 3/5  # 3 primes out of 5 numbers
        
        # Test empty sequence
        empty_density = analyzer.compute_prime_density([])
        assert empty_density == 0.0
        
        # Test sequence with no primes
        no_primes = [4, 6, 8, 9, 10]
        no_prime_density = analyzer.compute_prime_density(no_primes)
        assert no_prime_density == 0.0
        
        # Test sequence with only primes
        only_primes = [2, 3, 5, 7, 11]
        only_prime_density = analyzer.compute_prime_density(only_primes)
        assert only_prime_density == 1.0
    
    def test_compute_kappa(self, analyzer):
        """Test κ(n) curvature computation."""
        # Test with small values
        kappa_1 = analyzer.compute_kappa(1)
        assert kappa_1 > 0  # κ(1) should be positive
        
        kappa_2 = analyzer.compute_kappa(2)
        assert kappa_2 > 0  # κ(2) should be positive
        
        # Test that κ grows with n (generally)
        kappa_12 = analyzer.compute_kappa(12)  # 12 has many divisors
        kappa_13 = analyzer.compute_kappa(13)  # 13 is prime
        assert kappa_12 > kappa_13  # More divisors → higher κ
    
    def test_compute_theta_prime(self, analyzer):
        """Test θ′(n,k) mapping computation."""
        # Test basic computation
        theta_1 = analyzer.compute_theta_prime(1, 0.3)
        assert theta_1 > 0
        
        theta_2 = analyzer.compute_theta_prime(2, 0.3)
        assert theta_2 > 0
        
        # Test different k values
        theta_k1 = analyzer.compute_theta_prime(5, 0.1)
        theta_k3 = analyzer.compute_theta_prime(5, 0.3)
        assert theta_k1 != theta_k3  # Different k should give different results
        
        # Test k=0 should give φ for any n
        theta_k0 = analyzer.compute_theta_prime(100, 0.0)
        from src.applications.axis_wise_mod3_stabilization import PHI
        assert abs(theta_k0 - float(PHI)) < 1e-10
    
    def test_bootstrap_confidence_interval(self, analyzer):
        """Test bootstrap confidence interval computation."""
        # Test with known data
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        mean_est, ci_low, ci_high = analyzer.bootstrap_confidence_interval(data)
        
        assert mean_est == 3.0  # Mean of 1,2,3,4,5
        assert ci_low < mean_est < ci_high  # CI should contain mean
        assert ci_low < ci_high  # Lower bound < upper bound
        
        # Test with empty data
        empty_mean, empty_low, empty_high = analyzer.bootstrap_confidence_interval([])
        assert empty_mean == 0.0
        assert empty_low == 0.0
        assert empty_high == 0.0
        
        # Test with single value
        single_mean, single_low, single_high = analyzer.bootstrap_confidence_interval([5.0])
        assert single_mean == 5.0
        # CI for single value should be narrow
        assert abs(single_high - single_low) < 1e-10
    
    def test_compute_axis_metrics(self, analyzer):
        """Test comprehensive axis metrics computation."""
        # Create test sequence for axis 1 (remainder 1 mod 3)
        test_sequence = [1, 4, 7, 10, 13, 16, 19]  # Mix of primes and composites
        
        metrics = analyzer.compute_axis_metrics(test_sequence, axis_id=1)
        
        # Check all required keys are present
        required_keys = [
            'axis', 'N', 'prime_density_mean', 'prime_density_CI_lo', 'prime_density_CI_hi',
            'kappa_mean', 'kappa_CI_lo', 'kappa_CI_hi', 'kappa_variance',
            'theta_prime_mean', 'theta_prime_CI_lo', 'theta_prime_CI_hi', 'theta_prime_variance'
        ]
        
        for key in required_keys:
            assert key in metrics
        
        # Check basic properties
        assert metrics['axis'] == 'S1'
        assert metrics['N'] == len(test_sequence)
        assert 0 <= metrics['prime_density_mean'] <= 1
        assert metrics['kappa_mean'] > 0
        assert metrics['theta_prime_mean'] > 0
        assert metrics['kappa_variance'] >= 0
        assert metrics['theta_prime_variance'] >= 0
        
        # Check CI bounds
        assert metrics['prime_density_CI_lo'] <= metrics['prime_density_mean'] <= metrics['prime_density_CI_hi']
        assert metrics['kappa_CI_lo'] <= metrics['kappa_mean'] <= metrics['kappa_CI_hi']
        assert metrics['theta_prime_CI_lo'] <= metrics['theta_prime_mean'] <= metrics['theta_prime_CI_hi']
    
    def test_run_resolution_ladder_analysis_small(self, analyzer):
        """Test resolution ladder analysis with small data."""
        # Use small analyzer for faster testing
        small_analyzer = AxiswiseMod3Stabilization(max_n=100, batch_size=10)
        small_analyzer.resolution_ladder = [10, 30]  # Very small for testing
        
        results_df = small_analyzer.run_resolution_ladder_analysis()
        
        # Check DataFrame structure
        assert isinstance(results_df, pd.DataFrame)
        assert len(results_df) == 6  # 2 N values × 3 axes
        
        # Check required columns
        required_columns = [
            'axis', 'N', 'prime_density_mean', 'kappa_mean', 'theta_prime_mean'
        ]
        for col in required_columns:
            assert col in results_df.columns
        
        # Check axis representation
        axes_present = set(results_df['axis'].unique())
        assert axes_present == {'S0', 'S1', 'S2'}
        
        # Check N values
        n_values_present = set(results_df['N'].unique())
        assert n_values_present == {10, 30}
    
    def test_run_proportional_vs_independent_analysis_small(self, analyzer):
        """Test proportional vs independent analysis with small data."""
        small_analyzer = AxiswiseMod3Stabilization(max_n=100, batch_size=10)
        small_analyzer.resolution_ladder = [30, 60]  # Small for testing
        
        results_df = small_analyzer.run_proportional_vs_independent_analysis()
        
        # Check DataFrame structure
        assert isinstance(results_df, pd.DataFrame)
        assert len(results_df) == 2  # Proportional + Independent scenarios
        
        # Check scenarios
        scenarios = set(results_df['scenario'].unique())
        assert scenarios == {'proportional', 'independent'}
        
        # Check required columns
        required_columns = [
            'scenario', 'N0', 'N1', 'N2', 
            'composite_prime_density_mean', 'composite_kappa_mean', 'composite_theta_prime_mean'
        ]
        for col in required_columns:
            assert col in results_df.columns
    
    def test_compute_stabilization_index(self, analyzer):
        """Test stabilization index computation."""
        # Create mock ladder results
        mock_data = []
        for N in [100, 1000]:
            for axis_id in [0, 1, 2]:
                mock_data.append({
                    'axis': f'S{axis_id}',
                    'N': N,
                    'prime_density_mean': 0.1 + axis_id * 0.05,  # Different values per axis
                    'kappa_mean': 1.0 + axis_id * 0.2,
                    'theta_prime_mean': 0.5 + axis_id * 0.1
                })
        
        mock_df = pd.DataFrame(mock_data)
        stab_index = analyzer.compute_stabilization_index(mock_df)
        
        # Check structure
        assert isinstance(stab_index, pd.DataFrame)
        assert len(stab_index) == 3  # 3 metrics × 1 N value (only 100 has complete data)
        
        # Check required columns
        required_columns = ['metric', 'N', 'delta_star', 'delta_star_rel']
        for col in required_columns:
            assert col in stab_index.columns
        
        # Check metrics
        metrics_present = set(stab_index['metric'].unique())
        assert metrics_present == {'prime_density', 'kappa', 'theta_prime'}
        
        # Check that delta_star values are reasonable
        assert all(stab_index['delta_star'] >= 0)
        assert all(stab_index['delta_star_rel'] >= 0)
    
    def test_acceptance_checks(self, analyzer):
        """Test acceptance checks functionality."""
        # Create mock data with known properties
        mock_data = []
        
        # S0 with very low prime density (expected)
        for N in [100, 1000, 10000]:
            mock_data.append({
                'axis': 'S0',
                'N': N,
                'prime_density_mean': 1e-5,  # Very low to pass prime starvation check
                'prime_density_CI_hi': 5e-4,  # Below threshold
                'prime_density_CI_lo': 0.0,
                'kappa_mean': 1.0,
                'kappa_CI_hi': 1.2,
                'kappa_CI_lo': 0.8,
                'kappa_variance': 0.1,
                'theta_prime_mean': 0.5,
                'theta_prime_CI_hi': 0.6,
                'theta_prime_CI_lo': 0.4,
                'theta_prime_variance': 0.05
            })
        
        # S1 and S2 with higher prime densities
        for axis_id in [1, 2]:
            for N in [100, 1000, 10000]:
                mock_data.append({
                    'axis': f'S{axis_id}',
                    'N': N,
                    'prime_density_mean': 0.1,
                    'prime_density_CI_hi': 0.15,
                    'prime_density_CI_lo': 0.05,
                    'kappa_mean': 1.0 + axis_id * 0.2,
                    'kappa_CI_hi': 1.5,
                    'kappa_CI_lo': 0.5,
                    'kappa_variance': 0.2,
                    'theta_prime_mean': 0.5 + axis_id * 0.1,
                    'theta_prime_CI_hi': 0.8,
                    'theta_prime_CI_lo': 0.2,
                    'theta_prime_variance': 0.1
                })
        
        mock_df = pd.DataFrame(mock_data)
        checks = analyzer.run_acceptance_checks(mock_df)
        
        # Check that all expected checks are present
        expected_checks = [
            'prime_starvation_s0', 'ci_monotonicity', 
            'proportional_stability', 'independent_bias_detectability'
        ]
        
        for check in expected_checks:
            assert check in checks
            assert isinstance(checks[check], (bool, np.bool8))  # Accept both Python and numpy booleans
        
        # Prime starvation check should pass with our mock data
        assert checks['prime_starvation_s0'] == True
    
    def test_file_output_generation(self, analyzer, temp_dirs):
        """Test that output files are generated correctly."""
        temp_dir, results_dir, figs_dir = temp_dirs
        
        # Use very small analyzer for quick testing
        small_analyzer = AxiswiseMod3Stabilization(max_n=30, batch_size=10)
        small_analyzer.resolution_ladder = [10, 20]
        
        # Run minimal analysis
        results = small_analyzer.run_full_analysis()
        
        # Check that CSV files were created
        csv_files = [
            'axis_ladder_summary.csv',
            'proportional_vs_independent.csv', 
            'stabilization_index.csv',
            'ci_widths.csv',
            'theta_prime_ks.csv'
        ]
        
        for csv_file in csv_files:
            csv_path = results_dir / csv_file
            assert csv_path.exists(), f"Missing CSV file: {csv_file}"
            
            # Check that files are not empty
            df = pd.read_csv(csv_path)
            assert len(df) > 0, f"Empty CSV file: {csv_file}"
        
        # Check that summary report was created
        summary_path = results_dir / 'axis_stabilization_summary.md'
        assert summary_path.exists(), "Missing summary report"
        
        # Check summary content
        with open(summary_path, 'r') as f:
            content = f.read()
            assert 'Axis-wise Stabilization' in content
            assert 'S₀' in content
            assert 'Bootstrap' in content
    
    def test_prime_starvation_hypothesis(self, analyzer):
        """Test that S₀ shows expected prime starvation behavior."""
        # Partition a reasonable range
        sequences = analyzer.partition_mod3_sequences(100)
        
        # Compute prime densities
        s0_density = analyzer.compute_prime_density(sequences[0])  # Multiples of 3
        s1_density = analyzer.compute_prime_density(sequences[1])  # n ≡ 1 (mod 3)
        s2_density = analyzer.compute_prime_density(sequences[2])  # n ≡ 2 (mod 3)
        
        # S₀ should have lower prime density (only 3 is prime in multiples of 3)
        # This is the core hypothesis being tested
        assert s0_density < s1_density, "S₀ should have lower prime density than S₁"
        assert s0_density < s2_density, "S₀ should have lower prime density than S₂"
        
        # For multiples of 3 up to 100, only 3 should be prime
        s0_primes = [n for n in sequences[0] if analyzer.compute_prime_density([n]) == 1.0]
        assert 3 in s0_primes, "3 should be identified as prime in S₀"
        
        # Prime density of S₀ should be very small
        assert s0_density < 0.1, "S₀ prime density should be very low"
    
    def test_numerical_precision(self, analyzer):
        """Test numerical precision requirements."""
        # Test that computations maintain high precision
        
        # κ(n) should be computed with high precision
        kappa_100 = analyzer.compute_kappa(100)
        kappa_100_again = analyzer.compute_kappa(100)
        
        # Should be exactly reproducible
        assert abs(kappa_100 - kappa_100_again) < 1e-16
        
        # θ′(n,k) should also be high precision
        theta_50 = analyzer.compute_theta_prime(50, 0.3)
        theta_50_again = analyzer.compute_theta_prime(50, 0.3)
        
        assert abs(theta_50 - theta_50_again) < 1e-16
        
        # Bootstrap CIs should be reproducible with same seed
        test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        ci1 = analyzer.bootstrap_confidence_interval(test_data)
        ci2 = analyzer.bootstrap_confidence_interval(test_data)
        
        # Should be identical due to fixed seed
        assert abs(ci1[0] - ci2[0]) < 1e-16  # Mean
        assert abs(ci1[1] - ci2[1]) < 1e-16  # CI low
        assert abs(ci1[2] - ci2[2]) < 1e-16  # CI high
    
    def test_k_parameter_sensitivity(self, analyzer):
        """Test sensitivity to k parameter in θ′ mapping."""
        n = 50
        
        # Test different k values
        theta_k_low = analyzer.compute_theta_prime(n, 0.1)
        theta_k_mid = analyzer.compute_theta_prime(n, 0.3)
        theta_k_high = analyzer.compute_theta_prime(n, 0.5)
        
        # Should show variation with k
        assert theta_k_low != theta_k_mid != theta_k_high
        
        # Test that k=0.3 (primary k) gives reasonable values
        assert theta_k_mid > 0
        assert theta_k_mid < 10  # Should be reasonable magnitude
    
    def test_edge_cases(self, analyzer):
        """Test edge cases and error handling."""
        # Test with n=1 (smallest positive integer)
        kappa_1 = analyzer.compute_kappa(1)
        theta_1 = analyzer.compute_theta_prime(1, 0.3)
        
        assert kappa_1 > 0
        assert theta_1 > 0
        
        # Test with larger n
        kappa_large = analyzer.compute_kappa(10000)
        theta_large = analyzer.compute_theta_prime(10000, 0.3)
        
        assert kappa_large > 0
        assert theta_large > 0
        
        # Test empty sequence handling
        empty_density = analyzer.compute_prime_density([])
        assert empty_density == 0.0
        
        # Test single element sequence
        single_density = analyzer.compute_prime_density([2])
        assert single_density == 1.0  # 2 is prime
    
    def test_integration_with_existing_framework(self, analyzer):
        """Test integration with existing Z-framework components."""
        # Test that our module uses proper mathematical constants
        from src.applications.axis_wise_mod3_stabilization import PHI, E, E_SQUARED
        
        # Golden ratio should be approximately 1.618
        assert abs(float(PHI) - 1.618033988749) < 1e-10
        
        # e should be approximately 2.718
        assert abs(float(E) - 2.718281828459) < 1e-10
        
        # e² should be e squared
        assert abs(float(E_SQUARED) - float(E)**2) < 1e-15
        
        # Test that we use sympy correctly for prime testing
        assert analyzer.compute_prime_density([2, 3, 5]) == 1.0
        assert analyzer.compute_prime_density([4, 6, 8]) == 0.0


class TestAxiswiseMod3StabilizationIntegration:
    """Integration tests for the complete workflow."""
    
    def test_full_analysis_workflow_minimal(self, tmp_path):
        """Test complete analysis workflow with minimal data."""
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Create results and figs directories
            Path("results").mkdir(exist_ok=True)
            Path("figs").mkdir(exist_ok=True)
            
            # Create minimal analyzer
            analyzer = AxiswiseMod3Stabilization(max_n=50, batch_size=10)
            analyzer.resolution_ladder = [20, 30]  # Very small for fast testing
            analyzer.n_bootstrap = 100  # Reduced for speed
            
            # Run full analysis
            results = analyzer.run_full_analysis()
            
            # Check that analysis completed
            assert results['status'] == 'completed'
            assert 'ladder_results' in results
            assert 'proportional_vs_independent' in results
            assert 'acceptance_checks' in results
            
            # Check that required files exist
            assert Path("results/axis_ladder_summary.csv").exists()
            assert Path("results/axis_stabilization_summary.md").exists()
            
            # Basic validation of results
            ladder_df = results['ladder_results']
            assert len(ladder_df) == 6  # 2 N values × 3 axes
            
            prop_vs_indep_df = results['proportional_vs_independent']
            assert len(prop_vs_indep_df) == 2  # 2 scenarios
            
            acceptance_checks = results['acceptance_checks']
            assert len(acceptance_checks) == 4  # 4 acceptance checks
            
        finally:
            os.chdir(original_cwd)
    
    def test_reproducibility(self):
        """Test that results are reproducible across runs."""
        analyzer1 = AxiswiseMod3Stabilization(max_n=100, batch_size=10)
        analyzer2 = AxiswiseMod3Stabilization(max_n=100, batch_size=10)
        
        # Both should use same random seed for bootstrap
        test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        ci1 = analyzer1.bootstrap_confidence_interval(test_data)
        ci2 = analyzer2.bootstrap_confidence_interval(test_data)
        
        # Should be identical
        assert ci1 == ci2
        
        # κ and θ′ computations should be identical
        assert analyzer1.compute_kappa(50) == analyzer2.compute_kappa(50)
        assert analyzer1.compute_theta_prime(50, 0.3) == analyzer2.compute_theta_prime(50, 0.3)


def test_standalone_execution():
    """Test that the module can be executed standalone."""
    # This test ensures the main() function doesn't crash
    # We'll mock it to avoid actual heavy computation
    
    import sys
    from unittest.mock import patch, MagicMock
    
    # Mock the analyzer to avoid heavy computation
    mock_analyzer = MagicMock()
    mock_analyzer.run_full_analysis.return_value = {
        'status': 'completed',
        'acceptance_checks': {
            'prime_starvation_s0': True,
            'ci_monotonicity': True,
            'proportional_stability': True,
            'independent_bias_detectability': True
        }
    }
    
    with patch('src.applications.axis_wise_mod3_stabilization.AxiswiseMod3Stabilization') as mock_class:
        mock_class.return_value = mock_analyzer
        
        # Import and run main
        from src.applications.axis_wise_mod3_stabilization import main
        
        # Should not raise any exceptions
        main()
        
        # Verify that the analyzer was created and run
        mock_class.assert_called_once_with(max_n=1000000)
        mock_analyzer.run_full_analysis.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])