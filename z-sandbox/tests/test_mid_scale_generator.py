#!/usr/bin/env python3
"""
Tests for Mid-Scale Semiprime Generator

Validates:
- Cryptographically secure prime generation
- Balanced semiprime properties
- Special form exclusion
- Target validation
"""

import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

import pytest
import sympy
from mid_scale_semiprime_generator import (
    generate_random_prime,
    is_special_form,
    generate_balanced_semiprime,
    generate_mid_scale_suite,
    validate_target
)


class TestPrimeGeneration:
    """Test cryptographically secure prime generation."""
    
    def test_generate_random_prime_128bit(self):
        """Test generating 128-bit primes."""
        p = generate_random_prime(128)
        assert sympy.isprime(p)
        assert p.bit_length() == 128
    
    def test_generate_random_prime_256bit(self):
        """Test generating 256-bit primes."""
        p = generate_random_prime(256)
        assert sympy.isprime(p)
        assert p.bit_length() == 256
    
    def test_generate_random_prime_512bit(self):
        """Test generating 512-bit primes."""
        p = generate_random_prime(512)
        assert sympy.isprime(p)
        assert p.bit_length() == 512
    
    def test_prime_uniqueness(self):
        """Test that generated primes are different (high probability)."""
        primes = [generate_random_prime(128) for _ in range(10)]
        # All should be unique (probability of collision is negligible)
        assert len(set(primes)) == 10


class TestSpecialFormDetection:
    """Test detection of special prime forms."""
    
    def test_mersenne_prime_7(self):
        """Test Mersenne prime detection: 2^3 - 1 = 7."""
        assert is_special_form(7)
    
    def test_mersenne_prime_31(self):
        """Test Mersenne prime detection: 2^5 - 1 = 31."""
        assert is_special_form(31)
    
    def test_mersenne_prime_127(self):
        """Test Mersenne prime detection: 2^7 - 1 = 127."""
        assert is_special_form(127)
    
    def test_safe_prime_7(self):
        """Test safe prime detection: 7 where (7-1)/2 = 3 is prime."""
        assert is_special_form(7)
    
    def test_safe_prime_11(self):
        """Test safe prime detection: 11 where (11-1)/2 = 5 is prime."""
        assert is_special_form(11)
    
    def test_sophie_germain_2(self):
        """Test Sophie Germain prime: 2 where 2*2+1 = 5 is prime."""
        assert is_special_form(2)
    
    def test_sophie_germain_3(self):
        """Test Sophie Germain prime: 3 where 2*3+1 = 7 is prime."""
        assert is_special_form(3)
    
    def test_fermat_prime_17(self):
        """Test Fermat prime: 17 = 2^4 + 1."""
        # 17 is a Fermat prime (2^(2^2) + 1)
        assert is_special_form(17)
    
    def test_regular_prime_19(self):
        """Test regular prime: 19 is not special form."""
        assert not is_special_form(19)
    
    def test_regular_prime_97(self):
        """Test regular prime: 97 is not special form."""
        assert not is_special_form(97)


class TestBalancedSemiprimeGeneration:
    """Test balanced semiprime generation."""
    
    def test_generate_512bit_semiprime(self):
        """Test generating 512-bit balanced semiprime."""
        N, p, q, metadata = generate_balanced_semiprime(512)
        
        # Verify factorization
        assert p * q == N
        
        # Verify primality
        assert sympy.isprime(p)
        assert sympy.isprime(q)
        
        # Verify bit length
        assert N.bit_length() == 512
        
        # Verify balance
        bit_diff = abs(p.bit_length() - q.bit_length())
        assert bit_diff <= 2
        
        # Verify no special forms
        assert not is_special_form(p)
        assert not is_special_form(q)
        
        # Verify metadata
        assert metadata['target_bits'] == 512
        assert metadata['N_bits'] == 512
        assert metadata['balance_diff'] <= 2
    
    def test_generate_640bit_semiprime(self):
        """Test generating 640-bit balanced semiprime."""
        N, p, q, metadata = generate_balanced_semiprime(640)
        
        assert p * q == N
        assert sympy.isprime(p)
        assert sympy.isprime(q)
        assert N.bit_length() == 640
        assert abs(p.bit_length() - q.bit_length()) <= 2
    
    def test_generate_768bit_semiprime(self):
        """Test generating 768-bit balanced semiprime."""
        N, p, q, metadata = generate_balanced_semiprime(768)
        
        assert p * q == N
        assert sympy.isprime(p)
        assert sympy.isprime(q)
        assert N.bit_length() == 768
        assert abs(p.bit_length() - q.bit_length()) <= 2
    
    def test_factors_ordered(self):
        """Test that p ≤ q is maintained."""
        N, p, q, metadata = generate_balanced_semiprime(512)
        assert p <= q


class TestMidScaleSuite:
    """Test suite generation functionality."""
    
    def test_generate_small_suite(self):
        """Test generating a small suite of 3 targets."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            targets = generate_mid_scale_suite(
                num_targets=3,
                bit_range=(512, 576),
                output_file=output_file
            )
            
            # Verify count
            assert len(targets) == 3
            
            # Verify each target
            for target in targets:
                N = int(target['N'])
                p = int(target['p'])
                q = int(target['q'])
                
                # Basic validation
                assert p * q == N
                assert sympy.isprime(p)
                assert sympy.isprime(q)
                assert 512 <= N.bit_length() <= 576
            
            # Verify file was created
            assert Path(output_file).exists()
            
            # Verify file contents
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            assert data['num_targets'] == 3
            assert len(data['targets']) == 3
            assert data['bit_range'] == [512, 576]
            
        finally:
            # Cleanup
            if Path(output_file).exists():
                Path(output_file).unlink()
    
    def test_suite_bit_distribution(self):
        """Test that targets are distributed across bit range."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            targets = generate_mid_scale_suite(
                num_targets=5,
                bit_range=(512, 640),
                output_file=output_file
            )
            
            # Extract bit lengths
            bit_lengths = [int(t['metadata']['N_bits']) for t in targets]
            
            # Should span the range
            assert min(bit_lengths) >= 512
            assert max(bit_lengths) <= 640
            
            # Should be reasonably distributed (not all the same)
            assert len(set(bit_lengths)) > 1
            
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()


class TestTargetValidation:
    """Test target validation functionality."""
    
    def test_validate_correct_target(self):
        """Test validation of correct target."""
        # Generate a valid target
        N, p, q, metadata = generate_balanced_semiprime(512)
        
        target = {
            "id": "TEST-512b-01",
            "N": str(N),
            "p": str(p),
            "q": str(q),
            "metadata": metadata
        }
        
        assert validate_target(target)
    
    def test_validate_incorrect_factorization(self):
        """Test validation catches incorrect factorization."""
        N, p, q, metadata = generate_balanced_semiprime(512)
        
        # Create invalid target (wrong q)
        target = {
            "id": "TEST-512b-INVALID",
            "N": str(N),
            "p": str(p),
            "q": str(q + 2),  # Wrong factor
            "metadata": metadata
        }
        
        assert not validate_target(target)
    
    def test_validate_composite_factor(self):
        """Test validation catches composite factors."""
        # Use primes without special forms
        # 101 and 103 are not special forms
        target = {
            "id": "TEST-COMPOSITE",
            "N": str(101 * 103),  # 10403
            "p": "101",
            "q": "103",
            "metadata": {}
        }
        
        # This should pass (both prime, no special forms)
        assert validate_target(target)
        
        # Make p composite
        target['p'] = "102"
        target['N'] = str(102 * 103)
        assert not validate_target(target)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
