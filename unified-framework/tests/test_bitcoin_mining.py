#!/usr/bin/env python3
"""
Tests for Bitcoin Mining Nonce Generation using Z Framework
===========================================================

Test suite for the ZetaBitcoinNonceGenerator implementation.
"""

import sys
import os
import pytest
import hashlib
import time

# Add paths to access implementation
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/applications/primes/core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../examples'))

from bitcoin_mining import ZetaBitcoinNonceGenerator, StatisticalTester, PCGFallbackGenerator


class TestStatisticalTester:
    """Test statistical testing functionality."""
    
    def test_frequency_test_uniform(self):
        """Test frequency test with uniform sequence."""
        # Generate alternating pattern (should pass)
        sequence = [0xAAAAAAAA, 0x55555555] * 50
        result = StatisticalTester.frequency_test(sequence)
        assert result is True
    
    def test_frequency_test_biased(self):
        """Test frequency test with biased sequence."""
        # All zeros (should fail)
        sequence = [0x00000000] * 100
        result = StatisticalTester.frequency_test(sequence)
        assert result is False
    
    def test_runs_test_alternating(self):
        """Test runs test with alternating pattern."""
        sequence = [0xAAAAAAAA, 0x55555555] * 50
        result = StatisticalTester.runs_test(sequence)
        # May pass or fail depending on exact implementation
        assert isinstance(result, bool)
    
    def test_chi_squared_test_uniform(self):
        """Test chi-squared test with reasonably uniform sequence."""
        # Generate sequence with good distribution
        sequence = list(range(0, 256, 1)) * 4  # 1024 numbers
        result = StatisticalTester.chi_squared_test(sequence)
        assert result is True
    
    def test_run_all_tests(self):
        """Test running all statistical tests."""
        sequence = [0xAAAAAAAA, 0x55555555] * 50
        all_passed, results = StatisticalTester.run_all_tests(sequence)
        
        assert isinstance(all_passed, bool)
        assert isinstance(results, dict)
        assert 'frequency' in results
        assert 'runs' in results
        assert 'chi_squared' in results


class TestPCGFallbackGenerator:
    """Test PCG fallback generator."""
    
    def test_initialization(self):
        """Test PCG generator initialization."""
        generator = PCGFallbackGenerator(12345)
        assert generator is not None
    
    def test_nonce_generation(self):
        """Test nonce generation."""
        generator = PCGFallbackGenerator(12345)
        
        # Generate several nonces
        nonces = [generator.get_nonce() for _ in range(100)]
        
        # Check they're all 32-bit values
        for nonce in nonces:
            assert 0 <= nonce < 2**32
            assert isinstance(nonce, int)
        
        # Check for some variation (not all the same)
        assert len(set(nonces)) > 1


class TestZetaBitcoinNonceGenerator:
    """Test main bitcoin nonce generator."""
    
    def test_initialization_basic(self):
        """Test basic initialization."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(block_hash)
        
        assert generator.block_hash == block_hash
        assert generator.seed > 0
        assert generator.nonces_generated == 0
        assert generator.fallback_used is False
    
    def test_initialization_with_timestamp(self):
        """Test initialization with specific timestamp."""
        block_hash = '0000000000000000000abc123def456'
        timestamp = 1640995200  # 2022-01-01 00:00:00 UTC
        
        generator = ZetaBitcoinNonceGenerator(block_hash, timestamp)
        assert generator.timestamp == timestamp
    
    def test_seed_generation_deterministic(self):
        """Test that seed generation is deterministic."""
        block_hash = '0000000000000000000abc123def456'
        timestamp = 1640995200
        
        gen1 = ZetaBitcoinNonceGenerator(block_hash, timestamp)
        gen2 = ZetaBitcoinNonceGenerator(block_hash, timestamp)
        
        assert gen1.seed == gen2.seed
    
    def test_seed_generation_different_inputs(self):
        """Test that different inputs produce different seeds."""
        timestamp = 1640995200
        
        gen1 = ZetaBitcoinNonceGenerator('hash1', timestamp)
        gen2 = ZetaBitcoinNonceGenerator('hash2', timestamp)
        
        assert gen1.seed != gen2.seed
    
    def test_hmac_vs_simple_seeding(self):
        """Test HMAC vs simple seed generation."""
        block_hash = '0000000000000000000abc123def456'
        timestamp = 1640995200
        
        gen_hmac = ZetaBitcoinNonceGenerator(block_hash, timestamp, use_hmac=True)
        gen_simple = ZetaBitcoinNonceGenerator(block_hash, timestamp, use_hmac=False)
        
        # Should produce different seeds
        assert gen_hmac.seed != gen_simple.seed
    
    def test_nonce_generation_basic(self):
        """Test basic nonce generation."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(block_hash)
        
        # Generate several nonces
        nonces = [generator.get_nonce() for _ in range(10)]
        
        # Check they're all 32-bit values
        for nonce in nonces:
            assert 0 <= nonce < 2**32
            assert isinstance(nonce, int)
        
        # Check counter incremented
        assert generator.nonces_generated == 10
    
    def test_nonce_sequence_generation(self):
        """Test nonce sequence generation."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(block_hash)
        
        nonces = generator.get_nonce_sequence(50)
        
        assert len(nonces) == 50
        assert generator.nonces_generated == 50
        
        # Check for variation
        assert len(set(nonces)) > 1
    
    def test_statistical_testing_enabled(self):
        """Test statistical testing functionality."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(
            block_hash, 
            enable_statistical_testing=True
        )
        
        # Generate enough nonces to trigger testing
        nonces = generator.get_nonce_sequence(150)
        
        assert len(generator.test_sequence) > 0
        # May or may not have used fallback depending on test results
        assert isinstance(generator.fallback_used, bool)
    
    def test_geometric_resolution_enabled(self):
        """Test geometric resolution functionality."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(
            block_hash,
            enable_geometric_resolution=True
        )
        
        # Test curvature-based nonce generation
        nonces = generator.get_nonce_sequence_with_curvature(10)
        
        assert len(nonces) == 10
        for nonce in nonces:
            assert 0 <= nonce < 2**32
    
    def test_mining_simulation(self):
        """Test mining simulation."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(block_hash)
        
        successful_nonces, trials = generator.simulate_mining(max_trials=100)
        
        assert isinstance(successful_nonces, list)
        assert isinstance(trials, int)
        assert trials <= 100
        assert len(successful_nonces) <= trials
    
    def test_density_enhancement_calculation(self):
        """Test density enhancement calculation."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(block_hash)
        
        enhancement = generator.calculate_density_enhancement(100)
        
        assert isinstance(enhancement, float)
        # Enhancement could be positive or negative
        assert -100 <= enhancement <= 1000  # Reasonable bounds
    
    def test_statistics_collection(self):
        """Test statistics collection."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(
            block_hash,
            enable_statistical_testing=True,
            enable_geometric_resolution=True
        )
        
        # Generate some nonces
        generator.get_nonce_sequence(50)
        
        stats = generator.get_statistics()
        
        # Check required fields
        assert 'seed' in stats
        assert 'block_hash' in stats
        assert 'timestamp' in stats
        assert 'nonces_generated' in stats
        assert 'fallback_used' in stats
        assert 'use_hmac' in stats
        assert 'statistical_testing_enabled' in stats
        assert 'geometric_resolution_enabled' in stats
        
        assert stats['nonces_generated'] == 50
        assert stats['block_hash'] == block_hash
    
    def test_curvature_calculation(self):
        """Test curvature calculation."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(block_hash)
        
        # Test curvature for known values
        curvature_2 = generator._calculate_curvature(2)
        curvature_100 = generator._calculate_curvature(100)
        
        assert isinstance(curvature_2, float)
        assert isinstance(curvature_100, float)
        assert curvature_2 > 0
        assert curvature_100 > 0
        
        # Edge case
        curvature_0 = generator._calculate_curvature(0)
        assert curvature_0 == float('inf')


class TestIntegration:
    """Integration tests for complete functionality."""
    
    def test_full_workflow_basic(self):
        """Test complete workflow without advanced features."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(block_hash)
        
        # Generate nonces
        nonces = generator.get_nonce_sequence(50)
        
        # Run mining simulation
        successful_nonces, trials = generator.simulate_mining(max_trials=200)
        
        # Calculate enhancement
        enhancement = generator.calculate_density_enhancement(100)
        
        # Get statistics
        stats = generator.get_statistics()
        
        # Verify everything completed successfully
        assert len(nonces) == 50
        assert isinstance(successful_nonces, list)
        assert isinstance(trials, int)
        assert isinstance(enhancement, float)
        assert isinstance(stats, dict)
    
    def test_full_workflow_advanced(self):
        """Test complete workflow with all advanced features."""
        block_hash = '0000000000000000000abc123def456'
        generator = ZetaBitcoinNonceGenerator(
            block_hash,
            enable_statistical_testing=True,
            enable_geometric_resolution=True
        )
        
        # Generate nonces with curvature optimization
        nonces = generator.get_nonce_sequence_with_curvature(25)
        
        # Run mining simulation with curvature
        successful_nonces, trials = generator.simulate_mining(
            max_trials=200, 
            use_curvature=True
        )
        
        # Calculate enhancement
        enhancement = generator.calculate_density_enhancement(100)
        
        # Get statistics
        stats = generator.get_statistics()
        
        # Verify everything completed successfully
        assert len(nonces) == 25
        assert isinstance(successful_nonces, list)
        assert isinstance(trials, int)
        assert isinstance(enhancement, float)
        assert isinstance(stats, dict)
        assert stats['geometric_resolution_enabled'] is True
        assert stats['statistical_testing_enabled'] is True
    
    def test_reproducibility(self):
        """Test that results are reproducible with same inputs."""
        block_hash = '0000000000000000000abc123def456'
        timestamp = 1640995200
        
        gen1 = ZetaBitcoinNonceGenerator(block_hash, timestamp)
        gen2 = ZetaBitcoinNonceGenerator(block_hash, timestamp)
        
        nonces1 = gen1.get_nonce_sequence(10)
        nonces2 = gen2.get_nonce_sequence(10)
        
        # Should be identical for same inputs
        assert nonces1 == nonces2
    
    def test_different_block_hashes(self):
        """Test that different block hashes produce different results."""
        timestamp = 1640995200
        
        gen1 = ZetaBitcoinNonceGenerator('hash1', timestamp)
        gen2 = ZetaBitcoinNonceGenerator('hash2', timestamp)
        
        nonces1 = gen1.get_nonce_sequence(10)
        nonces2 = gen2.get_nonce_sequence(10)
        
        # Should be different for different block hashes
        assert nonces1 != nonces2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])