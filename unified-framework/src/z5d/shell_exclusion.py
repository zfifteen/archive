"""
Shell Exclusion Filter for Semiprime Factorization

Implements aggressive pruning of search space by analyzing resonance patterns
in "shells" (narrow bands around √n). Based on calibrated noise thresholds,
excludes regions unlikely to contain factors, achieving up to 4x speedup.

This is an adaptation of the geofac PR #125 ShellExclusionFilter for the
unified-framework Python codebase.

Key parameters (calibrated Nov 2025 for 127-bit semiprimes):
- shell_delta: 2500 (thicker shells = fewer shells = faster)
- shell_count: 36 (covers ±90,000 around √N)
- shell_tau: 0.178 (96.8th percentile noise floor)
- shell_tau_spike: 0.224 (transient spike detection)
- shell_overlap_percent: 0.15 (15% overlap for safety)
- shell_k_samples: 7 (7x7 sparse grid = 49 evals/shell)
"""

import math
from typing import List, Tuple, Optional
import numpy as np


class ShellExclusionConfig:
    """Configuration for shell-exclusion pruning."""
    
    def __init__(
        self,
        shell_delta: int = 2500,
        shell_count: int = 36,
        shell_tau: float = 0.178,
        shell_tau_spike: float = 0.224,
        shell_overlap_percent: float = 0.15,
        shell_k_samples: int = 7,
        enabled: bool = True,
    ):
        """
        Initialize shell exclusion configuration.
        
        Args:
            shell_delta: Width of each shell (thicker = faster scan)
            shell_count: Number of shells to scan around √n
            shell_tau: Noise floor threshold (96.8th percentile)
            shell_tau_spike: Spike detection threshold
            shell_overlap_percent: Overlap between shells for safety (0.0-1.0)
            shell_k_samples: Sparse grid dimension (k×k samples per shell)
            enabled: Whether shell exclusion is active
        """
        self.shell_delta = shell_delta
        self.shell_count = shell_count
        self.shell_tau = shell_tau
        self.shell_tau_spike = shell_tau_spike
        self.shell_overlap_percent = shell_overlap_percent
        self.shell_k_samples = shell_k_samples
        self.enabled = enabled
        
    @classmethod
    def challenge_127bit(cls) -> 'ShellExclusionConfig':
        """
        Return optimal configuration for 127-bit challenge.
        
        Calibrated parameters provide maximum safe speedup for large semiprimes.
        """
        return cls(
            shell_delta=2500,
            shell_count=36,
            shell_tau=0.178,
            shell_tau_spike=0.224,
            shell_overlap_percent=0.15,
            shell_k_samples=7,
            enabled=True,
        )


class ShellExclusionFilter:
    """
    Shell-exclusion pruning filter for factorization search space.
    
    Analyzes resonance patterns in concentric shells around √n to identify
    and exclude regions unlikely to contain prime factors.
    """
    
    def __init__(self, config: ShellExclusionConfig):
        """
        Initialize shell exclusion filter.
        
        Args:
            config: Shell exclusion configuration
        """
        self.config = config
        self.excluded_ranges: List[Tuple[int, int]] = []
        
    def analyze_and_exclude(self, n: int, root_n: int) -> List[Tuple[int, int]]:
        """
        Analyze shells around √n and return ranges to exclude.
        
        Args:
            n: The semiprime to factor
            root_n: Integer square root of n (search starting point)
            
        Returns:
            List of (start, end) tuples representing excluded ranges
        """
        if not self.config.enabled:
            return []
        
        delta = self.config.shell_delta
        overlap = int(delta * self.config.shell_overlap_percent)
        
        # First pass: compute amplitude for each shell
        shell_data = []
        for i in range(self.config.shell_count):
            # Calculate shell boundaries with overlap
            offset = i * delta - (self.config.shell_count // 2) * delta
            shell_start = root_n + offset - overlap
            shell_end = shell_start + delta + 2 * overlap
            
            # Ensure shell boundaries are valid
            if shell_start < 2:
                shell_start = 2
            
            # Compute resonance amplitude for this shell
            amplitude = self._compute_shell_resonance(n, shell_start, shell_end)
            shell_data.append((shell_start, shell_end, amplitude))
        
        # Second pass: exclude only if ALL overlapping shells have low amplitude
        # Use interval-based approach to avoid creating millions of dictionary entries
        # Build list of (position, amplitude, shell_id, is_start) events
        events = []
        for shell_id, (shell_start, shell_end, amplitude) in enumerate(shell_data):
            events.append((shell_start, amplitude, shell_id, True))   # Start of shell
            events.append((shell_end + 1, amplitude, shell_id, False))  # End of shell (exclusive)
        
        events.sort()
        
        # Track active shells and their amplitudes
        self.excluded_ranges = []
        active_shells = {}  # shell_id -> amplitude
        in_excluded = False
        current_start = None
        last_pos = None
        
        for pos, amplitude, shell_id, is_start in events:
            # Update active shells
            if is_start:
                active_shells[shell_id] = amplitude
            else:
                active_shells.pop(shell_id, None)
            
            # Compute max amplitude of active shells
            max_amplitude = max(active_shells.values()) if active_shells else 0.0
            
            # Determine if this position should be excluded
            should_exclude = max_amplitude < self.config.shell_tau
            
            # Handle transitions
            if last_pos is not None and pos > last_pos + 1:
                # Gap in coverage - close any open exclusion
                if in_excluded:
                    self.excluded_ranges.append((current_start, last_pos))
                    in_excluded = False
            
            if should_exclude:
                if not in_excluded:
                    current_start = pos
                    in_excluded = True
            else:
                if in_excluded:
                    self.excluded_ranges.append((current_start, pos - 1))
                    in_excluded = False
            
            last_pos = pos
        
        # Close final excluded range if needed
        if in_excluded and last_pos is not None:
            self.excluded_ranges.append((current_start, last_pos))
        
        return self.excluded_ranges
    
    def _compute_shell_resonance(self, n: int, start: int, end: int) -> float:
        """
        Compute resonance amplitude for a shell using sparse grid sampling.
        
        Args:
            n: The semiprime
            start: Shell start position
            end: Shell end position
            
        Returns:
            Maximum resonance amplitude in the shell
        """
        k = self.config.shell_k_samples
        samples = []
        shell_width = end - start
        
        # Sparse k×k grid sampling
        grid_size = k * k
        for grid_idx in range(grid_size):
            # Map grid index to position in shell
            # Use grid_idx / grid_size to get normalized position [0, 1]
            normalized_pos = grid_idx / grid_size
            x = start + int(shell_width * normalized_pos)
            
            # Compute resonance metric: how close x² - n is to being a perfect square
            diff = x * x - n
            if diff < 0:
                continue
                
            # Resonance is inversely related to distance from perfect square
            sqrt_diff = math.isqrt(diff)
            residual = diff - sqrt_diff * sqrt_diff
            
            # Normalize: perfect square has residual 0, maximum resonance
            # Non-perfect squares have residual > 0, lower resonance
            if residual == 0:
                # Found a factor! Maximum resonance
                return 1.0
            else:
                # Resonance decreases with residual
                # Use inverse decay with clamping to avoid underflow
                # For small residuals, use approximation to avoid exp() overhead
                if residual < 10 and sqrt_diff > 0:
                    # Linear approximation for small residuals
                    resonance = 1.0 / (1.0 + residual / (sqrt_diff + 1))
                else:
                    # Exponential decay for larger residuals
                    decay_factor = residual / (sqrt_diff + 1)
                    resonance = math.exp(-min(decay_factor, 50))  # Clamp to avoid underflow
                samples.append(resonance)
        
        if not samples:
            return 0.0
        
        # Return max amplitude (peak resonance in shell)
        max_amplitude = max(samples)
        
        # Check for spike (transient above noise floor)
        if max_amplitude >= self.config.shell_tau_spike:
            return max_amplitude
        
        # Return average amplitude for non-spike regions
        return sum(samples) / len(samples)
    
    def _merge_ranges(self, ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Merge overlapping excluded ranges.
        
        Args:
            ranges: List of (start, end) tuples
            
        Returns:
            Merged list of non-overlapping ranges
        """
        if not ranges:
            return []
        
        # Sort by start position
        sorted_ranges = sorted(ranges, key=lambda x: x[0])
        merged = [sorted_ranges[0]]
        
        for current in sorted_ranges[1:]:
            last = merged[-1]
            # Check for overlap
            if current[0] <= last[1]:
                # Merge by extending the end
                merged[-1] = (last[0], max(last[1], current[1]))
            else:
                # No overlap, add as new range
                merged.append(current)
        
        return merged
    
    def is_excluded(self, x: int) -> bool:
        """
        Check if a search position is in an excluded range.
        
        Args:
            x: Position to check
            
        Returns:
            True if position should be skipped
        """
        for start, end in self.excluded_ranges:
            if start <= x <= end:
                return True
        return False
    
    def get_included_ranges(self, search_start: int, search_end: int) -> List[Tuple[int, int]]:
        """
        Get list of ranges to include in search (inverse of excluded).
        
        Args:
            search_start: Overall search start
            search_end: Overall search end
            
        Returns:
            List of (start, end) tuples for included ranges
        """
        if not self.excluded_ranges:
            return [(search_start, search_end)]
        
        included = []
        current_start = search_start
        
        for excl_start, excl_end in sorted(self.excluded_ranges):
            if excl_start > current_start:
                # Add range before this exclusion
                included.append((current_start, excl_start - 1))
            current_start = max(current_start, excl_end + 1)
        
        # Add final range after last exclusion
        if current_start < search_end:
            included.append((current_start, search_end))
        
        return included
    
    def get_statistics(self) -> dict:
        """
        Get statistics about excluded ranges.
        
        Returns:
            Dictionary with exclusion statistics
        """
        if not self.excluded_ranges:
            return {
                'excluded_count': 0,
                'excluded_total_width': 0,
                'excluded_ranges': []
            }
        
        total_width = sum(end - start + 1 for start, end in self.excluded_ranges)
        
        return {
            'excluded_count': len(self.excluded_ranges),
            'excluded_total_width': total_width,
            'excluded_ranges': self.excluded_ranges,
        }
