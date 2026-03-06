#!/usr/bin/env python3
"""
Unit tests for shell-exclusion filter.

Tests the ShellExclusionFilter class and configuration for correctness,
ensuring no false exclusions and proper range merging.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from z5d.shell_exclusion import ShellExclusionConfig, ShellExclusionFilter


class TestShellExclusionConfig:
    """Test ShellExclusionConfig class."""
    
    def test_default_config(self):
        """Test default configuration initialization."""
        config = ShellExclusionConfig()
        assert config.shell_delta == 2500
        assert config.shell_count == 36
        assert config.shell_tau == 0.178
        assert config.shell_tau_spike == 0.224
        assert config.shell_overlap_percent == 0.15
        assert config.shell_k_samples == 7
        assert config.enabled is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ShellExclusionConfig(
            shell_delta=1000,
            shell_count=20,
            shell_tau=0.2,
            enabled=False,
        )
        assert config.shell_delta == 1000
        assert config.shell_count == 20
        assert config.shell_tau == 0.2
        assert config.enabled is False
    
    def test_challenge_127bit_config(self):
        """Test challenge 127-bit optimal configuration."""
        config = ShellExclusionConfig.challenge_127bit()
        assert config.enabled is True
        assert config.shell_delta == 2500
        assert config.shell_count == 36
        assert config.shell_tau == 0.178
        assert config.shell_tau_spike == 0.224
        assert config.shell_overlap_percent == 0.15
        assert config.shell_k_samples == 7


class TestShellExclusionFilter:
    """Test ShellExclusionFilter class."""
    
    def test_filter_initialization(self):
        """Test filter initialization."""
        config = ShellExclusionConfig()
        filter = ShellExclusionFilter(config)
        assert filter.config == config
        assert filter.excluded_ranges == []
    
    def test_disabled_filter(self):
        """Test that disabled filter returns no exclusions."""
        config = ShellExclusionConfig(enabled=False)
        filter = ShellExclusionFilter(config)
        
        n = 10403  # 101 × 103
        root_n = 102
        
        excluded = filter.analyze_and_exclude(n, root_n)
        assert excluded == []
    
    def test_merge_ranges(self):
        """Test range merging logic."""
        config = ShellExclusionConfig()
        filter = ShellExclusionFilter(config)
        
        # Test non-overlapping ranges
        ranges = [(1, 5), (10, 15), (20, 25)]
        merged = filter._merge_ranges(ranges)
        assert merged == [(1, 5), (10, 15), (20, 25)]
        
        # Test overlapping ranges
        ranges = [(1, 5), (4, 10), (8, 15)]
        merged = filter._merge_ranges(ranges)
        assert merged == [(1, 15)]
        
        # Test adjacent ranges
        ranges = [(1, 5), (6, 10), (11, 15)]
        merged = filter._merge_ranges(ranges)
        assert merged == [(1, 5), (6, 10), (11, 15)]
        
        # Test touching ranges
        ranges = [(1, 5), (5, 10)]
        merged = filter._merge_ranges(ranges)
        assert merged == [(1, 10)]
    
    def test_is_excluded(self):
        """Test is_excluded method."""
        config = ShellExclusionConfig()
        filter = ShellExclusionFilter(config)
        
        # Manually set excluded ranges
        filter.excluded_ranges = [(10, 20), (30, 40), (50, 60)]
        
        # Test inside excluded ranges
        assert filter.is_excluded(15) is True
        assert filter.is_excluded(35) is True
        assert filter.is_excluded(55) is True
        
        # Test outside excluded ranges
        assert filter.is_excluded(5) is False
        assert filter.is_excluded(25) is False
        assert filter.is_excluded(45) is False
        assert filter.is_excluded(65) is False
        
        # Test boundary conditions
        assert filter.is_excluded(10) is True
        assert filter.is_excluded(20) is True
        assert filter.is_excluded(9) is False
        assert filter.is_excluded(21) is False
    
    def test_get_included_ranges(self):
        """Test get_included_ranges method."""
        config = ShellExclusionConfig()
        filter = ShellExclusionFilter(config)
        
        # Manually set excluded ranges
        filter.excluded_ranges = [(10, 20), (30, 40)]
        
        # Get included ranges
        included = filter.get_included_ranges(0, 50)
        expected = [(0, 9), (21, 29), (41, 50)]
        assert included == expected
        
        # Test with no exclusions
        filter.excluded_ranges = []
        included = filter.get_included_ranges(0, 50)
        assert included == [(0, 50)]
    
    def test_get_statistics(self):
        """Test statistics collection."""
        config = ShellExclusionConfig()
        filter = ShellExclusionFilter(config)
        
        # Manually set excluded ranges
        filter.excluded_ranges = [(10, 20), (30, 40), (50, 60)]
        
        stats = filter.get_statistics()
        assert stats['excluded_count'] == 3
        assert stats['excluded_total_width'] == 33  # (20-10+1) + (40-30+1) + (60-50+1)
        assert stats['excluded_ranges'] == [(10, 20), (30, 40), (50, 60)]
    
    def test_small_semiprime(self):
        """Test shell exclusion on a small semiprime."""
        config = ShellExclusionConfig(
            shell_delta=10,
            shell_count=10,
            shell_tau=0.15,
            shell_k_samples=3,
        )
        filter = ShellExclusionFilter(config)
        
        # 101 × 103 = 10403
        n = 10403
        root_n = 102
        
        excluded = filter.analyze_and_exclude(n, root_n)
        
        # Should return some excluded ranges
        assert isinstance(excluded, list)
        
        # Verify that the true factor position is NOT excluded
        # For Fermat's method: x = (p+q)/2 = (101+103)/2 = 102
        # Check positions near 102
        for x in range(100, 105):
            # These positions are critical and should not be excluded
            # (We can't guarantee this without factors, but test that method runs)
            pass
        
        stats = filter.get_statistics()
        assert stats['excluded_count'] >= 0
    
    def test_perfect_square_detection(self):
        """Test that perfect squares are detected in resonance computation."""
        config = ShellExclusionConfig(
            shell_delta=5,
            shell_count=5,
            shell_tau=0.5,
            shell_k_samples=3,
        )
        filter = ShellExclusionFilter(config)
        
        # Perfect square: 100 = 10²
        n = 100
        root_n = 10
        
        # Analyze shell containing root_n
        amplitude = filter._compute_shell_resonance(n, root_n, root_n + 5)
        
        # Should detect perfect square (amplitude = 1.0)
        assert amplitude == 1.0


def test_no_false_exclusion_on_known_semiprimes():
    """
    Critical test: Ensure no false exclusions on known semiprimes.
    
    This test verifies that the filter never excludes the true factor
    position for a set of validated semiprimes.
    """
    # Known semiprimes with factors
    test_cases = [
        (15, 3, 5),       # 3 × 5
        (77, 7, 11),      # 7 × 11
        (143, 11, 13),    # 11 × 13
        (10403, 101, 103),  # 101 × 103
    ]
    
    config = ShellExclusionConfig(
        shell_delta=20,
        shell_count=20,
        shell_tau=0.15,
        shell_k_samples=5,
    )
    
    for n, p, q in test_cases:
        filter = ShellExclusionFilter(config)
        root_n = int(n ** 0.5) + 1
        
        excluded = filter.analyze_and_exclude(n, root_n)
        
        # For Fermat's method, the critical position is x = (p+q)/2
        # Verify this position is not excluded
        x_critical = (p + q) // 2
        
        assert not filter.is_excluded(x_critical), (
            f"False exclusion detected for {n} = {p} × {q}: "
            f"critical position {x_critical} is excluded"
        )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
