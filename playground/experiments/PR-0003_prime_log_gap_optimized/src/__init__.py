"""
PR-0003: Optimized Prime Log-Gap Analysis with 100 Bins

This package implements a comprehensive statistical analysis of prime number gaps
in logarithmic space, with the following improvements over PR-0002:
- 100 equal-width bins on log-prime axis (vs 50 bins on index)
- Support for primes up to 10^9 (vs 10^8)
- Disk caching for primes and computed gaps
- Segmented sieve for memory efficiency
- 12 2D plots and 5 3D plots for comprehensive visualization
"""

__version__ = "1.0.0"
__author__ = "GitHub Copilot"
