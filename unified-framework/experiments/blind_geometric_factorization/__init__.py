"""
Blind Geometric Factorization Experiment

This module implements a blind geometric search for semiprime factorization,
using the PR-123/969 scaling infrastructure without prior knowledge of factors.

The key distinction from PR-971's validation mode:
- Validation mode: Uses known factors to verify parameter infrastructure
- Blind mode: Attempts discovery without any prior knowledge of factors

Current status:
- Works for small semiprimes (up to ~64-bit) where trial division is tractable
- Gate-127 (127-bit) requires ~10^15 operations, demonstrating the challenge
- Further algorithmic breakthroughs needed for larger blind factorization
"""

__version__ = "0.1.0"
