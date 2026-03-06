#!/usr/bin/env python3
"""
Test Z5D factorization with larger trials.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'applications', 'primes', 'core'))

from rsa_probe_validation import probe_semiprime_with_timeout

# Test with 16-bit n that works
n = 19043
print(f"Testing n={n} with trials=1000")

factor = probe_semiprime_with_timeout(str(n), trials=1000, timeout_seconds=60, enable_error_compensation=True)
print(f"Factor found: {factor}")

if factor and n % factor == 0:
    print("Success!")
else:
    print("Failed")